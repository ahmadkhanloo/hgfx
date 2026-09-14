#!/usr/bin/env python3
"""Classify the frozen exact-case S7 HGF anomaly review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.diagnostics.recovery import _objective_for_variant, fit_binary_variant
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

PROTOCOL = "m18-s7-hgf-anomaly-review-1"
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
RTOL = 3e-8
ATOL = 3e-10


def _normalise(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def _array(value: Any) -> np.ndarray:
    if isinstance(value, dict) and value.get("hgfx_numeric") == "ieee-strings-v1":
        return np.asarray(_normalise(value["data"]), dtype=np.float64).reshape(value["shape"], order="F")
    return np.asarray(_normalise(value), dtype=np.float64)


def _scalar(value: Any) -> float:
    a = _array(value).reshape(-1)
    return float(a[0])


def _close_array(actual, expected) -> tuple[bool, dict]:
    a = np.asarray(actual, dtype=np.float64).reshape(-1)
    e = np.asarray(expected, dtype=np.float64).reshape(-1)
    if a.shape != e.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(e)):
        return False, {"shape_actual": list(a.shape), "shape_expected": list(e.shape), "finite": False}
    allowed = ATOL + RTOL * np.abs(e)
    diff = np.abs(a - e)
    ratio = np.divide(diff, allowed, out=np.full_like(diff, np.inf), where=allowed > 0)
    ok = bool(np.all(diff <= allowed))
    first = None
    if not ok:
        i = int(np.flatnonzero(diff > allowed)[0])
        first = {"index_zero_based": i, "actual": float(a[i]), "expected": float(e[i]), "abs_diff": float(diff[i]), "allowed": float(allowed[i]), "gate_ratio": float(ratio[i])}
    return ok, {"max_abs_diff": float(np.max(diff)), "max_gate_ratio": float(np.max(ratio)), "first_outside_gate": first}


def _close_scalar(actual: float, expected: float) -> tuple[bool, dict]:
    return _close_array([actual], [expected])


def _python_objective(case: dict, free: np.ndarray) -> float:
    u = np.asarray(case["u"], dtype=np.float64)
    y = np.asarray(case["y"], dtype=np.float64)
    prc = hgf_binary_config().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    initial = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    idx = np.asarray(case["free_indices_zero_based"], dtype=np.int64)
    full = initial.copy()
    full[idx] = np.asarray(free, dtype=np.float64).reshape(-1)
    return float(_objective_for_variant(model="hgf_binary", responses=y, inputs=u, full_parameters=full).neg_log_joint)


def main(input_path: Path, matlab_path: Path, output_path: Path) -> int:
    prepared = json.loads(input_path.read_text(encoding="utf-8"))
    matlab = json.loads(matlab_path.read_text(encoding="utf-8"))
    if prepared.get("protocol") != PROTOCOL or matlab.get("protocol") != PROTOCOL:
        raise ValueError("Diagnostic protocol mismatch")
    if prepared.get("reference_commit") != REFERENCE_COMMIT or matlab.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("MATLAB reference mismatch")
    if len(prepared.get("cases", [])) != 3 or len(matlab.get("cases", [])) != 3:
        raise ValueError("Frozen three-case anomaly set is incomplete")

    matlab_by_id = {item["case_id"]: item for item in matlab["cases"]}
    results = []
    overall_support = True
    objective_mismatch = False
    stable_optimizer_mismatch = False
    evidence_complete = True

    for case in prepared["cases"]:
        case_id = case["case_id"]
        ref = matlab_by_id.get(case_id)
        if ref is None or ref.get("case_sha256") != case["case_sha256"]:
            evidence_complete = False
            results.append({"case_id": case_id, "classification": "INSUFFICIENT_REFERENCE_EVIDENCE"})
            overall_support = False
            continue

        expected = case["expected_s7"]
        official_final = _array(ref["official"]["final_free"]).reshape(-1)
        official_neg = _scalar(ref["official"]["negLj"])
        baseline_final = _array(ref["baseline"]["argMin"]).reshape(-1)
        baseline_val = _scalar(ref["baseline"]["valMin"])
        hgfx_final = np.asarray(case["current_hgfx"]["final_free"], dtype=np.float64)

        official_final_ok, official_final_cmp = _close_array(official_final, expected["matlab_final"])
        official_neg_ok, official_neg_cmp = _close_scalar(official_neg, float(expected["matlab_negLj"]))
        baseline_final_ok, baseline_final_cmp = _close_array(baseline_final, official_final)
        baseline_val_ok, baseline_val_cmp = _close_scalar(baseline_val, official_neg)
        hgfx_replay_ok, hgfx_replay_cmp = _close_array(hgfx_final, expected["hgfx_final"])

        py_at_matlab = _python_objective(case, official_final)
        py_at_hgfx = _python_objective(case, hgfx_final)
        mat_at_matlab = _scalar(ref["objective_at_matlab_endpoint"])
        mat_at_hgfx = _scalar(ref["objective_at_hgfx_endpoint"])
        obj_mat_ok, obj_mat_cmp = _close_scalar(py_at_matlab, mat_at_matlab)
        obj_hgf_ok, obj_hgf_cmp = _close_scalar(py_at_hgfx, mat_at_hgfx)
        shared_objective_ok = obj_mat_ok and obj_hgf_ok

        variants = ref.get("variants", [])
        if len(variants) != 6:
            evidence_complete = False
        any_endpoint_sensitive = False
        any_convergence_sensitive = False
        variant_rows = []
        baseline_converged = bool(ref["baseline"]["converged_inferred"])
        seen = set()
        for variant in variants:
            k = int(variant["component_free_index_1based"])
            direction = int(variant["direction"])
            seen.add((k, direction))
            arg = _array(variant["argMin"]).reshape(-1)
            endpoint_ok, endpoint_cmp = _close_array(arg, baseline_final)
            conv = bool(variant["converged_inferred"])
            any_endpoint_sensitive |= not endpoint_ok
            any_convergence_sensitive |= conv != baseline_converged
            variant_rows.append({
                "label": variant["label"],
                "component_free_index_zero_based": k - 1,
                "direction": direction,
                "actual_delta": _scalar(variant["actual_delta"]),
                "endpoint_within_existing_gate": endpoint_ok,
                "endpoint_comparison": endpoint_cmp,
                "converged_inferred": conv,
                "reset_count": int(round(_scalar(variant["reset_count"]))),
                "trace_last_finite_row": int(round(_scalar(variant["trace_last_finite_row"]))),
                "valMin": _scalar(variant["valMin"]),
            })
        if seen != {(1,-1),(1,1),(2,-1),(2,1),(3,-1),(3,1)}:
            evidence_complete = False

        expected_pair_endpoint_ok, pair_cmp = _close_array(expected["hgfx_final"], expected["matlab_final"])
        expected_pair_convergence_match = bool(expected["hgfx_converged"] == expected["matlab_converged"])
        paired_anomaly = (not expected_pair_endpoint_ok) or (not expected_pair_convergence_match)

        baseline_replay_ok = official_final_ok and official_neg_ok and baseline_final_ok and baseline_val_ok and hgfx_replay_ok
        matlab_sensitive = any_endpoint_sensitive or any_convergence_sensitive
        if not baseline_replay_ok:
            classification = "INVALID_BASELINE_REPLAY"
            overall_support = False
        elif not shared_objective_ok:
            classification = "SHARED_OBJECTIVE_MISMATCH"
            objective_mismatch = True
            overall_support = False
        elif paired_anomaly and matlab_sensitive:
            classification = "MATLAB_START_ULP_SENSITIVE_PAIRING"
        elif not paired_anomaly:
            classification = "PAIRED_ENDPOINT_WITHIN_GATE"
        else:
            classification = "STABLE_REFERENCE_OPTIMIZER_MISMATCH"
            stable_optimizer_mismatch = True
            overall_support = False

        results.append({
            "case_id": case_id,
            "case_sha256": case["case_sha256"],
            "classification": classification,
            "baseline_replay_ok": baseline_replay_ok,
            "official_s7_replay": {
                "final": official_final_cmp,
                "negLj": official_neg_cmp,
                "direct_optimizer_final": baseline_final_cmp,
                "direct_optimizer_val": baseline_val_cmp,
                "hgfx_final": hgfx_replay_cmp,
            },
            "shared_objective_parity": {
                "pass": shared_objective_ok,
                "at_matlab_endpoint": obj_mat_cmp,
                "at_hgfx_endpoint": obj_hgf_cmp,
            },
            "paired_s7_anomaly": {
                "endpoint_within_existing_gate": expected_pair_endpoint_ok,
                "endpoint_comparison": pair_cmp,
                "convergence_match": expected_pair_convergence_match,
            },
            "matlab_start_sensitivity": {
                "endpoint_sensitive": any_endpoint_sensitive,
                "convergence_sensitive": any_convergence_sensitive,
                "baseline_converged_inferred": baseline_converged,
                "variants": variant_rows,
            },
        })

    if not evidence_complete:
        overall = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif objective_mismatch:
        overall = "IMPLEMENTATION_OBJECTIVE_MISMATCH"
    elif stable_optimizer_mismatch:
        overall = "S8_OPTIMIZER_REPAIR_REQUIRED"
    elif overall_support:
        overall = "REFERENCE_LIMITATION_REVIEW_SUPPORTED"
    else:
        overall = "INSUFFICIENT_REFERENCE_EVIDENCE"

    payload = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "existing_gate": {"rtol": RTOL, "atol": ATOL},
        "classification": overall,
        "cases": results,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "decision_note": "REFERENCE_LIMITATION_REVIEW_SUPPORTED is evidence for the frozen S7 review only. The original S7 aggregate remains preserved and must be dispositioned separately.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"classification": overall, "cases": {r["case_id"]: r["classification"] for r in results}}, indent=2))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("matlab", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.input, args.matlab, args.output))
