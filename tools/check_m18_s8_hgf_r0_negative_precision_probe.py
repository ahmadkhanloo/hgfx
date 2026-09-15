#!/usr/bin/env python3
"""Compare the frozen MATLAB/HGFX HGF negative-posterior-precision boundary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.models._forward_common import binary_native_parameters
from hgfx.models.hgf_binary import hgf_binary

PROTOCOL = "m18-s8-hgf-r0-negative-precision-probe-1"
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CASE_ID = "PR-hgf_binary-T256-S0.35-R0"
CASE_SHA = "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5"
FIELDS = (
    "pihat2",
    "pi2",
    "da2",
    "mu3_prev",
    "pi3_prev",
    "muhat3",
    "pihat3",
    "exp_arg2",
    "exp2",
    "v2",
    "w2",
    "pi3_candidate",
)


def _array(value: Any) -> np.ndarray:
    if isinstance(value, dict) and value.get("hgfx_numeric") == "ieee-strings-v1":
        return np.asarray(value["data"], dtype=np.float64).reshape(value["shape"], order="F")
    return np.asarray(value, dtype=np.float64)


def _scalar(value: Any) -> float:
    return float(_array(value).reshape(-1)[0])


def _field_summary(actual: np.ndarray, expected: np.ndarray) -> dict[str, Any]:
    a = np.asarray(actual, dtype=np.float64).reshape(-1)
    e = np.asarray(expected, dtype=np.float64).reshape(-1)
    if a.shape != e.shape:
        return {"shape_match": False, "hgfx_shape": list(a.shape), "matlab_shape": list(e.shape)}
    same = (a == e) | (np.isnan(a) & np.isnan(e))
    diff = np.abs(a - e)
    first = None
    if not np.all(same):
        i = int(np.flatnonzero(~same)[0])
        first = {
            "history_index_zero_based": i,
            "trial_1based": i + 1,
            "hgfx": float(a[i]),
            "matlab": float(e[i]),
            "abs_diff": float(diff[i]),
        }
    finite = np.isfinite(a) & np.isfinite(e)
    return {
        "shape_match": True,
        "exact": bool(np.all(same)),
        "different_count": int(same.size - np.count_nonzero(same)),
        "first_difference": first,
        "max_abs": float(np.max(diff[finite])) if np.any(finite) else float("nan"),
    }


def _hgfx_histories(case: dict[str, Any], free: np.ndarray, expected_len: int) -> dict[str, np.ndarray]:
    u = np.asarray(case["u"], dtype=np.float64)
    prc = hgf_binary_config().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    idx = np.asarray(case["free_indices_zero_based"], dtype=np.int64)
    full[idx] = np.asarray(free, dtype=np.float64).reshape(-1)
    ptrans = full[: len(prc.parameters)]
    native, l = binary_native_parameters(ptrans, transformed=True)
    if l != 3:
        raise ValueError(f"Expected three-level HGF, got {l}")

    traj, _ = hgf_binary(u, ptrans, transformed=True, validate=False)
    mu = np.asarray(traj["mu"], dtype=np.float64)
    pi = np.float64(1.0) / np.asarray(traj["sa"], dtype=np.float64)
    muhat = np.asarray(traj["muhat"], dtype=np.float64)
    pihat = np.float64(1.0) / np.asarray(traj["sahat"], dtype=np.float64)
    v = np.asarray(traj["v"], dtype=np.float64)
    w = np.asarray(traj["w"], dtype=np.float64)
    da = np.asarray(traj["da"], dtype=np.float64)

    n = min(expected_len, mu.shape[0])
    mu3_prev = np.empty(n, dtype=np.float64)
    pi3_prev = np.empty(n, dtype=np.float64)
    mu3_prev[0] = native[2]
    pi3_prev[0] = np.float64(1.0) / native[5]
    if n > 1:
        mu3_prev[1:] = mu[: n - 1, 2]
        pi3_prev[1:] = pi[: n - 1, 2]

    ka2 = np.float64(native[10])
    om2 = np.float64(native[12])
    exp_arg2 = ka2 * mu3_prev + om2
    exp2 = v[:n, 1].copy()  # regular intervals: t == 1, so v2 == exp(exp_arg2)

    return {
        "pihat2": pihat[:n, 1],
        "pi2": pi[:n, 1],
        "da2": da[:n, 1],
        "mu3_prev": mu3_prev,
        "pi3_prev": pi3_prev,
        "muhat3": muhat[:n, 2],
        "pihat3": pihat[:n, 2],
        "exp_arg2": exp_arg2,
        "exp2": exp2,
        "v2": v[:n, 1],
        "w2": w[:n, 1],
        "pi3_candidate": pi[:n, 2],
    }


def main(fixture_path: Path, matlab_path: Path, output_path: Path) -> int:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    ref = json.loads(matlab_path.read_text(encoding="utf-8"))
    if ref.get("protocol") != PROTOCOL or ref.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Frozen negative-precision protocol/reference mismatch")
    if ref.get("case_id") != CASE_ID or ref.get("case_sha256") != CASE_SHA:
        raise ValueError("Frozen R0 case mismatch")
    cases = [c for c in fixture.get("cases", []) if c.get("case_id") == CASE_ID]
    if len(cases) != 1 or cases[0].get("case_sha256") != CASE_SHA:
        raise ValueError("Immutable R0 fixture missing or changed")
    case = cases[0]

    rows: list[dict[str, Any]] = []
    all_matlab_negative = True
    all_hgfx_positive_at_matlab_failure = True
    global_first: tuple[tuple[int, int], dict[str, Any]] | None = None

    for point in ref.get("points", []):
        history_ref = point["history"]
        trial_ref = _array(history_ref["trial_1based"]).reshape(-1)
        expected_len = trial_ref.size
        free = _array(point["free"]).reshape(-1)
        actual = _hgfx_histories(case, free, expected_len)
        expected = {field: _array(history_ref[field]).reshape(-1) for field in FIELDS}
        comparisons = {field: _field_summary(actual[field], expected[field]) for field in FIELDS}

        matlab_negative = bool(point["negative_precision"])
        all_matlab_negative &= matlab_negative
        failure_trial = int(round(_scalar(point["failure_trial_1based"]))) if matlab_negative else None
        if failure_trial is not None:
            i = failure_trial - 1
            hgfx_pi = float(actual["pi3_candidate"][i])
            matlab_pi = float(expected["pi3_candidate"][i])
            hgfx_positive = hgfx_pi > 0.0
            all_hgfx_positive_at_matlab_failure &= hgfx_positive
            failure_operands = {
                field: {
                    "matlab": float(expected[field][i]),
                    "hgfx": float(actual[field][i]),
                    "abs_diff": float(abs(actual[field][i] - expected[field][i])),
                }
                for field in FIELDS
            }
        else:
            hgfx_positive = None
            failure_operands = None

        point_first: tuple[tuple[int, int], dict[str, Any]] | None = None
        for priority, field in enumerate(FIELDS):
            first = comparisons[field].get("first_difference")
            if first is None:
                continue
            key = (int(first["trial_1based"]), priority)
            payload = {"field": field, **first}
            if point_first is None or key < point_first[0]:
                point_first = (key, payload)
        if point_first is not None:
            tag = {
                "step_1based": int(round(_scalar(point["step_1based"]))),
                "h": _scalar(point["h"]),
                "side": point.get("side", "plus"),
                **point_first[1],
            }
            if global_first is None or point_first[0] < global_first[0]:
                global_first = (point_first[0], tag)

        rows.append({
            "step_1based": int(round(_scalar(point["step_1based"]))),
            "h": _scalar(point["h"]),
            "side": point.get("side", "plus"),
            "matlab_negative_precision": matlab_negative,
            "matlab_failure_trial_1based": failure_trial,
            "hgfx_positive_at_matlab_failure": hgfx_positive,
            "failure_operands": failure_operands,
            "first_history_difference": None if point_first is None else point_first[1],
            "fields": comparisons,
        })

    if all_matlab_negative and all_hgfx_positive_at_matlab_failure:
        classification = "NEGATIVE_PRECISION_SIGN_BOUNDARY_DIVERGENCE"
    elif all_matlab_negative:
        classification = "MIXED_NEGATIVE_PRECISION_BOUNDARY_BEHAVIOR"
    else:
        classification = "REFERENCE_PROBE_UNEXPECTED"

    payload = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": CASE_ID,
        "case_sha256": CASE_SHA,
        "classification": classification,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "all_three_matlab_negative_precision": bool(all_matlab_negative),
        "all_three_hgfx_positive_at_matlab_failure": bool(all_hgfx_positive_at_matlab_failure),
        "first_history_difference": None if global_first is None else global_first[1],
        "points": rows,
        "note": "Diagnostic only. Same immutable S8 R0 Ridders points; no scientific input, threshold, start, optimizer, or release criterion changed.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": classification,
        "all_three_matlab_negative_precision": payload["all_three_matlab_negative_precision"],
        "all_three_hgfx_positive_at_matlab_failure": payload["all_three_hgfx_positive_at_matlab_failure"],
        "first_history_difference": payload["first_history_difference"],
        "failure_summary": [
            {
                "step": row["step_1based"],
                "trial": row["matlab_failure_trial_1based"],
                "matlab_pi3": None if row["failure_operands"] is None else row["failure_operands"]["pi3_candidate"]["matlab"],
                "hgfx_pi3": None if row["failure_operands"] is None else row["failure_operands"]["pi3_candidate"]["hgfx"],
            }
            for row in rows
        ],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("matlab", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.fixture, args.matlab, args.output))
