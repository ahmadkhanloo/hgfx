#!/usr/bin/env python3
"""Diagnostic-only comparison of the first D02 MATLAB/HGFX optimizer iterations."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

import hgfx
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.optim.ridders import RiddersOptions, ridders_gradient

THRESHOLDS = (0.0, 1e-14, 1e-12, 1e-10, 1e-8)


def _stats(actual, expected):
    actual = np.asarray(actual, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if actual.shape != expected.shape:
        return {"shape_mismatch": [list(actual.shape), list(expected.shape)]}
    diff = np.abs(actual - expected)
    finite = np.isfinite(diff)
    max_abs = float(np.max(diff[finite])) if np.any(finite) else float("nan")
    denom = np.maximum(np.abs(expected), np.finfo(np.float64).tiny)
    rel = diff / denom
    max_rel = float(np.max(rel[finite])) if np.any(finite) else float("nan")
    result = {"max_abs": max_abs, "max_rel": max_rel}
    for threshold in THRESHOLDS:
        mask = diff > threshold
        key = f"first_gt_{threshold:.0e}"
        if np.any(mask):
            index = tuple(int(i) for i in np.argwhere(mask)[0])
            result[key] = {
                "index": list(index),
                "hgfx": float(actual[index]),
                "matlab": float(expected[index]),
                "abs_diff": float(diff[index]),
            }
        else:
            result[key] = None
    return result


def _matlab_inverse_hessian(raw):
    if isinstance(raw, list) and len(raw) == 0:
        return None
    return _array(raw)


def _replay_quasinewton(matlab_x, matlab_grad, matlab_inv_h):
    """Replay BFGS algebra from exact MATLAB state, without HGFX path drift."""

    transitions = []
    max_regu = 16
    max_step = 1.0

    for q in range(len(matlab_x) - 1):
        current_t = _matlab_inverse_hessian(matlab_inv_h[q])
        next_t = _matlab_inverse_hessian(matlab_inv_h[q + 1])
        if current_t is None or next_t is None:
            continue

        x = np.asarray(matlab_x[q], dtype=np.float64).reshape(-1)
        next_x = np.asarray(matlab_x[q + 1], dtype=np.float64).reshape(-1)
        grad = np.asarray(matlab_grad[q], dtype=np.float64).reshape(-1)
        next_grad = np.asarray(matlab_grad[q + 1], dtype=np.float64).reshape(-1)

        descvec = -(current_t @ grad)
        step_size = float(np.sqrt(np.dot(descvec, descvec)))
        if step_size > max_step:
            descvec = descvec * max_step / step_size

        candidates = [
            x + (np.float64(0.5) ** j) * descvec
            for j in range(max_regu + 1)
        ]
        candidate_errors = [
            float(np.max(np.abs(candidate - next_x))) for candidate in candidates
        ]
        regu = int(np.argmin(candidate_errors))
        predicted_x = candidates[regu]
        dx = next_x - x
        dgrad = next_grad - grad

        dgdx = float(np.dot(dgrad, dx))
        curvature_threshold = float(
            np.sqrt(
                np.finfo(np.float64).eps
                * np.dot(dgrad, dgrad)
                * np.dot(dx, dx)
            )
        )
        predicted_t = current_t.copy()
        updated = dgdx > curvature_threshold
        if updated:
            dg_t = dgrad @ current_t
            dg_t_dg = float(np.dot(dg_t, dgrad))
            u = dx / dgdx - dg_t / dg_t_dg
            predicted_t = (
                current_t
                + np.outer(dx, dx) / dgdx
                - np.outer(dg_t, dg_t) / dg_t_dg
                + dg_t_dg * np.outer(u, u)
            )

        transitions.append(
            {
                "from_matlab_row_1based": q + 1,
                "to_matlab_row_1based": q + 2,
                "inferred_regularizations": regu,
                "step_fraction": float(np.float64(0.5) ** regu),
                "step_replay": _stats(predicted_x, next_x),
                "bfgs_updated": bool(updated),
                "dgdx": dgdx,
                "curvature_threshold": curvature_threshold,
                "inverse_hessian_replay": _stats(predicted_t, next_t),
            }
        )

    return {
        "classification": "DIAGNOSTIC_ONLY",
        "note": (
            "Replays step normalization/backtracking and BFGS using exact MATLAB "
            "x/gradient/inverse-Hessian state. This removes accumulated HGFX path drift."
        ),
        "transitions": transitions,
    }


def _compare_ridders_samples(problem, point, samples):
    """Compare objective values at the exact scalar coordinates sampled by MATLAB."""

    diagnostics = []
    point = np.asarray(point, dtype=np.float64).reshape(-1)

    for sample in samples:
        parameter_index = int(sample["parameter_index_1based"]) - 1
        h = _array(sample["h"]).reshape(-1)
        x_plus = _array(sample["x_plus"]).reshape(-1)
        x_minus = _array(sample["x_minus"]).reshape(-1)
        matlab_plus = _array(sample["f_plus"]).reshape(-1)
        matlab_minus = _array(sample["f_minus"]).reshape(-1)
        matlab_central = _array(sample["central_difference"]).reshape(-1)

        hgfx_plus = np.empty_like(matlab_plus)
        hgfx_minus = np.empty_like(matlab_minus)
        for i in range(len(h)):
            candidate = point.copy()
            candidate[parameter_index] = x_plus[i]
            hgfx_plus[i] = problem.evaluate_free(candidate)

            candidate = point.copy()
            candidate[parameter_index] = x_minus[i]
            hgfx_minus[i] = problem.evaluate_free(candidate)

        hgfx_central = (hgfx_plus - hgfx_minus) / (2.0 * h)
        item = {
            "parameter_index_1based": parameter_index + 1,
            "x0": float(sample["x0"]),
            "steps": int(len(h)),
            "stop_step": int(sample["stop_step"]),
            "f_plus": _stats(hgfx_plus, matlab_plus),
            "f_minus": _stats(hgfx_minus, matlab_minus),
            "central_difference": _stats(hgfx_central, matlab_central),
        }
        diagnostics.append(item)
        print(
            json.dumps(
                {
                    "ridders_parameter": parameter_index + 1,
                    "steps": len(h),
                    "f_plus_max_abs": item["f_plus"].get("max_abs"),
                    "f_minus_max_abs": item["f_minus"].get("max_abs"),
                    "central_max_abs": item["central_difference"].get("max_abs"),
                }
            ),
            flush=True,
        )

    return {
        "classification": "DIAGNOSTIC_ONLY",
        "note": (
            "HGFX objective is evaluated at the exact x+h/x-h scalar coordinates exported "
            "by MATLAB, before Richardson extrapolation."
        ),
        "parameters": diagnostics,
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d02-optimizer-probe-1":
        raise ValueError("Diagnostic protocol mismatch")
    if reference["case_id"] != "D02_fit":
        raise ValueError("Unexpected case")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("ehgf_binary")
    obs = resolve_config("unitsq_sgm")
    obs = replace(
        obs,
        parameters=(
            replace(
                obs.parameters[0],
                prior_variance=float(reference["obs_prior_variance"]),
            ),
        ),
    )
    problem = WorkflowFitProblem(
        y,
        u,
        prc.resolve_placeholders(u),
        obs.resolve_placeholders(u),
    )
    est = hgfx.fit_model(y, u, prc, obs)
    actual_iter = est.optim.iter

    rows = _array(reference["trace"]["rows"]).astype(np.int64).reshape(-1)
    matlab_x = _array(reference["trace"]["x"])
    matlab_val = _array(reference["trace"]["val"]).reshape(-1)
    matlab_grad = _array(reference["trace"]["grad"])
    matlab_grad_err = _array(reference["trace"]["grad_err"])
    matlab_inv_h = reference["trace"]["invH"]

    diagnostics = []
    for q, matlab_row in enumerate(rows):
        index = int(matlab_row) - 1
        point = np.asarray(matlab_x[q], dtype=np.float64).reshape(-1)
        grad, grad_err = ridders_gradient(
            problem.evaluate_free,
            point,
            RiddersOptions(min_steps=10),
        )
        item = {
            "matlab_row_1based": int(matlab_row),
            "x": _stats(actual_iter.x[index], point),
            "val": _stats(actual_iter.val[index], matlab_val[q]),
            "gradient_at_matlab_x": _stats(grad, matlab_grad[q]),
            "gradient_error_at_matlab_x": _stats(grad_err, matlab_grad_err[q]),
        }

        expected_t = _matlab_inverse_hessian(matlab_inv_h[q])
        if expected_t is None:
            item["inverse_hessian"] = {"available": False}
        elif index < len(actual_iter.invH):
            item["inverse_hessian"] = {
                "available": True,
                **_stats(actual_iter.invH[index].T, expected_t),
            }
        else:
            item["inverse_hessian"] = {
                "available": False,
                "reason": "HGFX trace missing corresponding inverse Hessian",
            }
        diagnostics.append(item)
        print(
            json.dumps(
                {
                    "row": int(matlab_row),
                    "x_max_abs": item["x"].get("max_abs"),
                    "val_max_abs": item["val"].get("max_abs"),
                    "grad_at_matlab_x_max_abs": item[
                        "gradient_at_matlab_x"
                    ].get("max_abs"),
                    "invH_max_abs": item["inverse_hessian"].get("max_abs"),
                }
            ),
            flush=True,
        )

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "note": (
            "Diagnostic only. Thresholds below locate numerical divergence and do not "
            "modify the frozen M18 acceptance gate."
        ),
        "rows": diagnostics,
        "quasinewton_state_replay": _replay_quasinewton(
            matlab_x,
            matlab_grad,
            matlab_inv_h,
        ),
    }
    if "ridders_samples" in reference:
        result["ridders_finite_difference_objective"] = _compare_ridders_samples(
            problem,
            matlab_x[0],
            reference["ridders_samples"],
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
