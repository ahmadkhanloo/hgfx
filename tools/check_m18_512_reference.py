#!/usr/bin/env python3
"""Classify the frozen M18 512-trial case against MATLAB HGF 8.2.0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.diagnostics.recovery import _objective_for_variant, fit_binary_variant
from hgfx.models.hgf_binary import hgf_binary
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
TRAJ_RTOL = 5e-11
TRAJ_ATOL = 5e-13
OBJECTIVE_ATOL = 1e-8
FINAL_OBJECTIVE_GAP = 0.10


def _normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(_normalize(value), dtype=np.float64)


def compare_array(label: str, actual: Any, expected: Any, *, rtol=TRAJ_RTOL, atol=TRAJ_ATOL):
    a, e = arr(actual), arr(expected)
    if a.shape != e.shape:
        return f"{label}: shape HGFX={a.shape} MATLAB={e.shape}"
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return None
    idx = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = float(a[idx]) if idx else float(a)
    ev = float(e[idx]) if idx else float(e)
    trial = f", trial={idx[0] + 1}" if idx else ""
    return f"{label}: first divergence{trial}, index={idx}, MATLAB={ev:.17g}, HGFX={av:.17g}"


def python_forward(inputs, ptrans):
    try:
        traj, inf_states = hgf_binary(inputs, ptrans, transformed=True, irregular_intervals=False)
        return {"success": True, "traj": traj, "inf_states": inf_states, "error": None}
    except Exception as exc:  # evidence capture
        return {"success": False, "traj": {}, "inf_states": [], "error": f"{type(exc).__name__}: {exc}"}


def python_objective(responses, inputs, full):
    try:
        out = _objective_for_variant(
            model="hgf_binary", responses=responses, inputs=inputs, full_parameters=full
        )
        success = out.rval == 0 and np.isfinite(out.neg_log_joint) and np.isfinite(out.neg_log_likelihood)
        return {
            "success": bool(success),
            "rval": int(out.rval),
            "neg_log_joint": float(out.neg_log_joint),
            "neg_log_likelihood": float(out.neg_log_likelihood),
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "rval": -1, "neg_log_joint": None, "neg_log_likelihood": None,
                "error": f"{type(exc).__name__}: {exc}"}


def python_fit(responses, inputs):
    try:
        fit = fit_binary_variant(
            responses, inputs, "hgf_binary", options=QuasiNewtonOptions(max_iter=100)
        )
        success = np.isfinite(fit.objective.neg_log_joint) and fit.objective.rval == 0
        return {
            "attempted": True,
            "success": bool(success),
            "termination": fit.optimizer.termination,
            "final_neg_log_joint": float(fit.objective.neg_log_joint),
            "final_neg_log_likelihood": float(fit.objective.neg_log_likelihood),
            "error": None,
        }
    except Exception as exc:
        return {"attempted": True, "success": False, "termination": None,
                "final_neg_log_joint": None, "final_neg_log_likelihood": None,
                "error": f"{type(exc).__name__}: {exc}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json", type=Path)
    parser.add_argument("matlab_json", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reference/generated/m18_512_classification.json"))
    args = parser.parse_args()

    case = json.loads(args.case_json.read_text(encoding="utf-8"))
    matlab = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    if case["reference"]["commit"] != REFERENCE_COMMIT or matlab["metadata"]["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError("Frozen MATLAB reference commit mismatch")
    if case["historical_cell"]["seed"] != 233100 or case["historical_cell"]["trial_count"] != 512:
        raise AssertionError("Historical 512-trial cell is not frozen correctly")

    inputs = arr(case["inputs"])
    responses = arr(case["responses"])
    truth_prc = arr(case["truth_perceptual_transformed"])
    default_prc = arr(case["default_perceptual_transformed"])
    default_full = arr(case["default_full_transformed"])

    py_truth = python_forward(inputs, truth_prc)
    py_default = python_forward(inputs, default_prc)
    py_obj = python_objective(responses, inputs, default_full)
    py_fit = python_fit(responses, inputs) if py_obj["success"] else {
        "attempted": False, "success": False, "termination": None,
        "final_neg_log_joint": None, "final_neg_log_likelihood": None,
        "error": "initial_objective_unstable",
    }

    mismatches = []
    matched_limitations = []

    for label, py, ml in (
        ("truth_forward", py_truth, matlab["truth_forward"]),
        ("default_forward", py_default, matlab["default_forward"]),
    ):
        ml_success = bool(ml["success"])
        if py["success"] != ml_success:
            mismatches.append(f"{label}: success mismatch HGFX={py['success']} MATLAB={ml_success}")
            continue
        if not py["success"]:
            matched_limitations.append(f"{label}: both implementations failed")
            continue
        expected_traj = ml["traj"]
        if set(py["traj"]) != set(expected_traj):
            mismatches.append(f"{label}: trajectory fields differ")
        else:
            for field in sorted(py["traj"]):
                expected = expected_traj[field]
                actual = np.asarray(py["traj"][field])
                if field == "w" and actual.ndim == 2 and actual.shape[1] == 1 and arr(expected).ndim == 1:
                    expected = arr(expected).reshape(actual.shape)
                msg = compare_array(f"{label}.traj.{field}", actual, expected)
                if msg:
                    mismatches.append(msg)
                    break
        if not mismatches:
            msg = compare_array(f"{label}.inf_states", py["inf_states"], ml["inf_states"])
            if msg:
                mismatches.append(msg)

    ml_obj = matlab["initial_objective"]
    if py_obj["success"] != bool(ml_obj["success"]):
        mismatches.append(
            f"initial_objective: success mismatch HGFX={py_obj['success']} MATLAB={bool(ml_obj['success'])}"
        )
    elif not py_obj["success"]:
        matched_limitations.append("initial_objective: both implementations unstable")
    else:
        for field in ("neg_log_joint", "neg_log_likelihood"):
            if not np.isclose(py_obj[field], float(ml_obj[field]), rtol=1e-10, atol=OBJECTIVE_ATOL):
                mismatches.append(
                    f"initial_objective.{field}: MATLAB={float(ml_obj[field]):.17g}, HGFX={py_obj[field]:.17g}"
                )

    ml_fit = matlab["fit"]
    if bool(ml_fit.get("attempted", False)) or py_fit["attempted"]:
        if py_fit["success"] != bool(ml_fit.get("success", False)):
            mismatches.append(
                f"fit: success mismatch HGFX={py_fit['success']} MATLAB={bool(ml_fit.get('success', False))}"
            )
        elif not py_fit["success"]:
            matched_limitations.append("fit: both implementations failed/unstable")
        elif abs(py_fit["final_neg_log_joint"] - float(ml_fit["final_neg_log_joint"])) > FINAL_OBJECTIVE_GAP:
            mismatches.append(
                "fit.final_neg_log_joint gap exceeds 0.10: "
                f"MATLAB={float(ml_fit['final_neg_log_joint']):.17g}, HGFX={py_fit['final_neg_log_joint']:.17g}"
            )

    if mismatches:
        classification = "IMPLEMENTATION_MISMATCH"
    elif matched_limitations:
        classification = "REFERENCE_LIMITATION_MATCH"
    else:
        classification = "NO_CURRENT_DIVERGENCE"

    result = {
        "schema_version": 1,
        "case_seed": 233100,
        "trial_count": 512,
        "classification": classification,
        "mismatches": mismatches,
        "matched_limitations": matched_limitations,
        "hgfx": {"truth_forward": {"success": py_truth["success"], "error": py_truth["error"]},
                 "default_forward": {"success": py_default["success"], "error": py_default["error"]},
                 "initial_objective": py_obj, "fit": py_fit},
        "matlab": {"truth_forward": {"success": bool(matlab["truth_forward"]["success"]),
                                      "error": matlab["truth_forward"].get("error_message", "")},
                   "default_forward": {"success": bool(matlab["default_forward"]["success"]),
                                        "error": matlab["default_forward"].get("error_message", "")},
                   "initial_objective": ml_obj, "fit": ml_fit},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    # A concrete MATLAB-vs-HGFX implementation mismatch is a CI failure.
    if classification == "IMPLEMENTATION_MISMATCH":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
