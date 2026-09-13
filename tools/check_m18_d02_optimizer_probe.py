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

        expected_t = matlab_inv_h[q]
        if isinstance(expected_t, list) and len(expected_t) == 0:
            item["inverse_hessian"] = {"available": False}
        else:
            expected_t = _array(expected_t)
            if index < len(actual_iter.invH):
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
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
