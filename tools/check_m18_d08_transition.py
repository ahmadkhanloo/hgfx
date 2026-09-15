#!/usr/bin/env python3
"""Localize the first hidden D08 quasi-Newton transition divergence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions, quasinewton_optim
from hgfx.optim.ridders import RiddersOptions, ridders_gradient


def scalar(value) -> np.float64:
    return np.float64(_array(value).reshape(-1)[0])


def array_record(actual, expected):
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    if a.shape != e.shape:
        return {"shape_hgfx": list(a.shape), "shape_matlab": list(e.shape), "shape_match": False}
    same = (a == e) | (np.isnan(a) & np.isnan(e))
    different = np.argwhere(~same)
    finite = np.isfinite(a) & np.isfinite(e)
    max_abs = float(np.max(np.abs(a[finite] - e[finite]))) if np.any(finite) else 0.0
    first = None
    if different.size:
        index = tuple(int(v) for v in different[0])
        first = {
            "index": list(index),
            "hgfx": float(a[index]),
            "matlab": float(e[index]),
            "abs_diff": float(abs(a[index] - e[index])),
        }
    return {
        "shape_match": True,
        "exact": bool(not different.size),
        "max_abs_diff": max_abs,
        "first_exact_difference": first,
    }


def transition(problem, x, val, inv_hessian, gradient, *, max_step=1.0, max_regu=16):
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    tmat = np.asarray(inv_hessian, dtype=np.float64)
    grad = np.asarray(gradient, dtype=np.float64).reshape(-1)
    desc_raw = -(tmat @ grad)
    slope = np.float64(np.dot(grad, desc_raw))
    step_size_raw = np.float64(np.sqrt(np.dot(desc_raw, desc_raw)))
    desc_limited = desc_raw.copy()
    if step_size_raw > np.float64(max_step):
        desc_limited = desc_raw * np.float64(max_step) / np.float64(
            np.sqrt(np.dot(desc_raw, desc_raw))
        )
    step_size_limited = np.float64(np.sqrt(np.dot(desc_limited, desc_limited)))

    candidates = []
    accepted_j = None
    accepted_x = None
    accepted_val = None
    for j in range(max_regu + 1):
        fraction = np.float64(0.5) ** j
        candidate_x = x + fraction * desc_limited
        candidate_val = np.float64(problem.evaluate_free(candidate_x))
        finite = bool(np.isfinite(candidate_val))
        dval = np.float64(candidate_val - val) if finite else np.float64(np.nan)
        rhs = np.float64(1e-4) * fraction * slope
        accept = bool(finite and dval < rhs)
        candidates.append(
            {
                "j": j,
                "t": float(fraction),
                "x": candidate_x,
                "val": float(candidate_val),
                "dval": float(dval),
                "rhs": float(rhs),
                "finite": finite,
                "armijo_accept": accept,
            }
        )
        if accepted_j is None and accept:
            accepted_j = j
            accepted_x = candidate_x.copy()
            accepted_val = candidate_val

    return {
        "descvec_raw": desc_raw,
        "slope": slope,
        "step_size_raw": step_size_raw,
        "descvec_limited": desc_limited,
        "step_size_limited": step_size_limited,
        "candidates": candidates,
        "accepted_j": accepted_j,
        "accepted_x": accepted_x,
        "accepted_val": accepted_val,
    }


def transition_record(result, reference_transition, target_x, target_val):
    ref_desc_raw = _array(reference_transition["descvec_raw"]).reshape(-1)
    ref_desc_limited = _array(reference_transition["descvec_limited"]).reshape(-1)
    ref_accepted_x = _array(reference_transition["accepted_x"]).reshape(-1)
    accepted_x = result["accepted_x"]
    accepted_val = result["accepted_val"]
    return {
        "descvec_raw": array_record(result["descvec_raw"], ref_desc_raw),
        "descvec_limited": array_record(result["descvec_limited"], ref_desc_limited),
        "slope": {
            "hgfx": float(result["slope"]),
            "matlab": float(scalar(reference_transition["slope"])),
            "abs_diff": float(abs(result["slope"] - scalar(reference_transition["slope"]))),
            "exact": bool(result["slope"] == scalar(reference_transition["slope"])),
        },
        "step_size_raw": {
            "hgfx": float(result["step_size_raw"]),
            "matlab": float(scalar(reference_transition["step_size_raw"])),
            "abs_diff": float(
                abs(result["step_size_raw"] - scalar(reference_transition["step_size_raw"]))
            ),
            "exact": bool(result["step_size_raw"] == scalar(reference_transition["step_size_raw"])),
        },
        "accepted_j": {
            "hgfx": result["accepted_j"],
            "matlab": int(scalar(reference_transition["accepted_j"])),
            "exact": bool(result["accepted_j"] == int(scalar(reference_transition["accepted_j"]))),
        },
        "accepted_x_vs_matlab_transition": array_record(accepted_x, ref_accepted_x),
        "accepted_x_vs_stored_target": array_record(accepted_x, target_x),
        "accepted_val_vs_stored_target": {
            "hgfx": float(accepted_val),
            "matlab": float(target_val),
            "abs_diff": float(abs(accepted_val - target_val)),
            "exact": bool(accepted_val == target_val),
        },
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d08-transition-diagnostic-1":
        raise ValueError("Diagnostic protocol mismatch")
    if reference["case_id"] != "D08_fit":
        raise ValueError("Unexpected case")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("uhgf").resolve_placeholders(u)
    obs = resolve_config("gaussian_obs").resolve_placeholders(u)
    problem = WorkflowFitProblem(y, u, prc, obs)

    source_row = int(reference["source_trace_row_1based"]) - 1
    target_row = int(reference["target_trace_row_1based"]) - 1
    matlab_source_x = _array(reference["source"]["x"]).reshape(-1)
    matlab_source_val = scalar(reference["source"]["val"])
    matlab_t = _array(reference["source"]["invH"])
    matlab_grad = _array(reference["source"]["gradient"]).reshape(-1)
    matlab_grad_err = _array(reference["source"]["gradient_error"]).reshape(-1)
    matlab_target_x = _array(reference["target"]["x"]).reshape(-1)
    matlab_target_val = scalar(reference["target"]["val"])

    optimizer = quasinewton_optim(
        problem.evaluate_free,
        problem.initial_free,
        QuasiNewtonOptions(),
    )
    live_source_x = np.asarray(optimizer.iter_x[source_row], dtype=np.float64)
    live_source_val = np.float64(optimizer.iter_val[source_row])
    live_t = np.asarray(optimizer.iter_inverse_hessians[source_row], dtype=np.float64)
    live_target_x = np.asarray(optimizer.iter_x[target_row], dtype=np.float64)
    live_target_val = np.float64(optimizer.iter_val[target_row])

    hgfx_grad_at_matlab_x, hgfx_grad_err = ridders_gradient(
        problem.evaluate_free,
        matlab_source_x,
        RiddersOptions(min_steps=10),
    )
    hgfx_val_at_matlab_x = np.float64(problem.evaluate_free(matlab_source_x))

    variants = {
        "matlab_T_matlab_grad_python_arithmetic": transition(
            problem, matlab_source_x, matlab_source_val, matlab_t, matlab_grad
        ),
        "matlab_T_hgfx_grad": transition(
            problem, matlab_source_x, hgfx_val_at_matlab_x, matlab_t, hgfx_grad_at_matlab_x
        ),
        "hgfx_T_matlab_grad": transition(
            problem, matlab_source_x, matlab_source_val, live_t, matlab_grad
        ),
        "hgfx_T_hgfx_grad": transition(
            problem, matlab_source_x, hgfx_val_at_matlab_x, live_t, hgfx_grad_at_matlab_x
        ),
    }

    reference_transition = reference["transition"]
    variant_records = {
        name: transition_record(value, reference_transition, matlab_target_x, matlab_target_val)
        for name, value in variants.items()
    }

    candidate_objective_replay = []
    for candidate in reference_transition["candidates"]:
        candidate_x = _array(candidate["x"]).reshape(-1)
        matlab_val = scalar(candidate["val"])
        hgfx_val = np.float64(problem.evaluate_free(candidate_x))
        candidate_objective_replay.append(
            {
                "j": int(candidate["j"]),
                "hgfx_at_exact_matlab_x": float(hgfx_val),
                "matlab": float(matlab_val),
                "abs_diff": float(abs(hgfx_val - matlab_val)),
                "exact": bool(hgfx_val == matlab_val),
            }
        )

    source_x_cmp = array_record(live_source_x, matlab_source_x)
    source_t_cmp = array_record(live_t, matlab_t)
    gradient_cmp = array_record(hgfx_grad_at_matlab_x, matlab_grad)
    target_live_cmp = array_record(live_target_x, matlab_target_x)
    pure_arithmetic_cmp = variant_records["matlab_T_matlab_grad_python_arithmetic"][
        "accepted_x_vs_stored_target"
    ]

    if not source_x_cmp.get("exact", False):
        classification = "SOURCE_POINT_ALREADY_DIVERGED"
    elif not source_t_cmp.get("exact", False):
        classification = "INVERSE_HESSIAN_DIVERGENCE_BEFORE_X_SPLIT"
    elif not gradient_cmp.get("exact", False):
        classification = "RIDDERS_GRADIENT_DIVERGENCE"
    elif not pure_arithmetic_cmp.get("exact", False):
        classification = "TRANSITION_ARITHMETIC_DIVERGENCE"
    elif not target_live_cmp.get("exact", False):
        classification = "LIVE_OPTIMIZER_CONTROL_DIVERGENCE"
    else:
        classification = "NO_TRANSITION_DIVERGENCE"

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D08_fit",
        "classification": classification,
        "source_trace_row_zero_based": source_row,
        "target_trace_row_zero_based": target_row,
        "free_full_indices_zero_based": [int(v) - 1 for v in _array(reference["free_full_indices_1based"]).reshape(-1)],
        "source": {
            "x": source_x_cmp,
            "stored_val": {
                "hgfx": float(live_source_val),
                "matlab": float(matlab_source_val),
                "abs_diff": float(abs(live_source_val - matlab_source_val)),
                "exact": bool(live_source_val == matlab_source_val),
            },
            "objective_replay_at_exact_matlab_x": {
                "hgfx": float(hgfx_val_at_matlab_x),
                "matlab": float(matlab_source_val),
                "abs_diff": float(abs(hgfx_val_at_matlab_x - matlab_source_val)),
                "exact": bool(hgfx_val_at_matlab_x == matlab_source_val),
            },
            "inverse_hessian": source_t_cmp,
            "gradient": gradient_cmp,
            "gradient_error": array_record(hgfx_grad_err, matlab_grad_err),
        },
        "target_live_trace": {
            "x": target_live_cmp,
            "val": {
                "hgfx": float(live_target_val),
                "matlab": float(matlab_target_val),
                "abs_diff": float(abs(live_target_val - matlab_target_val)),
                "exact": bool(live_target_val == matlab_target_val),
            },
        },
        "transition_variants": variant_records,
        "matlab_candidate_objective_replay": candidate_objective_replay,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
