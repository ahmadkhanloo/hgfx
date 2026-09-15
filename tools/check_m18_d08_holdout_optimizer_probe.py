#!/usr/bin/env python3
"""Diagnostic-only localization of the failed D08 holdout optimizer path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import hgfx
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.optim.ridders import RiddersOptions, ridders_gradient

PROTOCOL = "m18-d08-holdout-optimizer-probe-1"
SEED = 314159265
RTOL = 3e-8
ATOL = 3e-10


def _stats(actual, expected):
    actual = np.asarray(actual, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if actual.shape != expected.shape:
        return {"shape_mismatch": [list(actual.shape), list(expected.shape)]}
    diff = np.abs(actual - expected)
    finite = np.isfinite(diff)
    if not np.any(finite):
        return {"max_abs": float("nan"), "max_rel": float("nan"), "gate_close": False}
    max_abs = float(np.max(diff[finite]))
    denom = np.maximum(np.abs(expected), np.finfo(np.float64).tiny)
    rel = diff / denom
    max_rel = float(np.max(rel[finite]))
    close = np.isclose(actual, expected, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(close):
        first = None
    else:
        idx = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
        first = {
            "index": list(idx),
            "hgfx": float(actual[idx] if idx else actual.item()),
            "matlab": float(expected[idx] if idx else expected.item()),
            "abs_diff": float(diff[idx] if idx else diff.item()),
        }
    return {
        "max_abs": max_abs,
        "max_rel": max_rel,
        "gate_close": bool(np.all(close)),
        "first_gate_divergence": first,
    }


def _first_trace_divergence(actual, expected, label):
    actual = np.asarray(actual, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    result = {"label": label, "actual_shape": list(actual.shape), "expected_shape": list(expected.shape)}
    if actual.ndim != expected.ndim:
        result["first_divergence"] = "rank_mismatch"
        return result
    overlap = tuple(slice(0, min(a, e)) for a, e in zip(actual.shape, expected.shape))
    a = actual[overlap]
    e = expected[overlap]
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(close):
        result["first_divergence"] = None
    else:
        idx = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
        result["first_divergence"] = {
            "index_zero_based": list(idx),
            "hgfx": float(a[idx] if idx else a.item()),
            "matlab": float(e[idx] if idx else e.item()),
            "abs_diff": float(abs((a[idx] if idx else a.item()) - (e[idx] if idx else e.item()))),
        }
    if actual.shape != expected.shape:
        result["shape_mismatch"] = True
    return result


def _matlab_inverse_hessian(raw):
    if isinstance(raw, list) and len(raw) == 0:
        return None
    return _array(raw)


def _replay_quasinewton(rows, matlab_x, matlab_grad, matlab_inv_h):
    transitions = []
    max_regu = 16
    max_step = 1.0
    for q in range(len(rows) - 1):
        if int(rows[q + 1]) != int(rows[q]) + 1:
            continue
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
        candidates = [x + (np.float64(0.5) ** j) * descvec for j in range(max_regu + 1)]
        errors = [float(np.max(np.abs(candidate - next_x))) for candidate in candidates]
        regu = int(np.argmin(errors))
        predicted_x = candidates[regu]

        dx = next_x - x
        dgrad = next_grad - grad
        dgdx = float(np.dot(dgrad, dx))
        curvature_threshold = float(
            np.sqrt(np.finfo(np.float64).eps * np.dot(dgrad, dgrad) * np.dot(dx, dx))
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
                "from_matlab_row_1based": int(rows[q]),
                "to_matlab_row_1based": int(rows[q + 1]),
                "inferred_regularizations": regu,
                "step_fraction": float(np.float64(0.5) ** regu),
                "step_replay": _stats(predicted_x, next_x),
                "bfgs_updated": bool(updated),
                "inverse_hessian_replay": _stats(predicted_t, next_t),
            }
        )
    return transitions


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference.get("protocol") != PROTOCOL:
        raise ValueError("Diagnostic protocol mismatch")
    if reference.get("case_id") != "D08_fit":
        raise ValueError("Unexpected case")
    seed = int(np.asarray(reference.get("seed"), dtype=np.int64).reshape(-1)[0])
    if seed != SEED:
        raise ValueError(f"Frozen seed mismatch: {seed} != {SEED}")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    prc = resolve_config("uhgf")
    obs = resolve_config("gaussian_obs")
    problem = WorkflowFitProblem(y, u, prc.resolve_placeholders(u), obs.resolve_placeholders(u))
    est = hgfx.fit_model(y, u, prc, obs)
    actual_iter = est.optim.iter

    full_x = _array(reference["trace"]["full_x"])
    full_val = _array(reference["trace"]["full_val"]).reshape(-1)
    full_rst = _array(reference["trace"]["full_rst"]).reshape(-1)
    full_trace = {
        "x": _first_trace_divergence(actual_iter.x, full_x, "optimizer.iter.x"),
        "val": _first_trace_divergence(actual_iter.val, full_val, "optimizer.iter.val"),
        "rst": _first_trace_divergence(actual_iter.rst, full_rst, "optimizer.iter.rst"),
    }

    window = reference["trace"]["window"]
    rows = _array(window["rows"]).astype(np.int64).reshape(-1)
    matlab_x = _array(window["x"])
    matlab_val = _array(window["val"]).reshape(-1)
    matlab_grad = _array(window["grad"])
    matlab_grad_err = _array(window["grad_err"])
    matlab_inv_h = window["invH"]

    shared = []
    shared_gate_failure = False
    for q, matlab_row in enumerate(rows):
        index = int(matlab_row) - 1
        point = np.asarray(matlab_x[q], dtype=np.float64).reshape(-1)
        objective = problem.evaluate_free(point)
        grad, grad_err = ridders_gradient(
            problem.evaluate_free,
            point,
            RiddersOptions(min_steps=10),
        )
        item = {
            "matlab_row_1based": int(matlab_row),
            "actual_path_x": _stats(actual_iter.x[index], point) if index < len(actual_iter.x) else {"missing": True},
            "actual_path_val": _stats(actual_iter.val[index], matlab_val[q]) if index < len(actual_iter.val) else {"missing": True},
            "objective_at_exact_matlab_x": _stats(objective, matlab_val[q]),
            "gradient_at_exact_matlab_x": _stats(grad, matlab_grad[q]),
            "gradient_error_at_exact_matlab_x": _stats(grad_err, matlab_grad_err[q]),
        }
        expected_t = _matlab_inverse_hessian(matlab_inv_h[q])
        if expected_t is None or index >= len(actual_iter.invH):
            item["actual_path_inverse_hessian"] = {"available": False}
        else:
            item["actual_path_inverse_hessian"] = {
                "available": True,
                **_stats(actual_iter.invH[index].T, expected_t),
            }
        if not item["objective_at_exact_matlab_x"].get("gate_close", False):
            shared_gate_failure = True
        if not item["gradient_at_exact_matlab_x"].get("gate_close", False):
            shared_gate_failure = True
        shared.append(item)
        print(
            json.dumps(
                {
                    "row": int(matlab_row),
                    "path_x_gate_close": item["actual_path_x"].get("gate_close"),
                    "objective_shared_gate_close": item["objective_at_exact_matlab_x"].get("gate_close"),
                    "gradient_shared_gate_close": item["gradient_at_exact_matlab_x"].get("gate_close"),
                    "gradient_max_abs": item["gradient_at_exact_matlab_x"].get("max_abs"),
                }
            ),
            flush=True,
        )

    path_diverged = full_trace["x"].get("first_divergence") is not None
    if not shared:
        classification = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif shared_gate_failure:
        classification = "SHARED_STATE_OBJECTIVE_OR_GRADIENT_DIVERGENCE"
    elif path_diverged:
        classification = "SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES"
    else:
        classification = "INSUFFICIENT_REFERENCE_EVIDENCE"

    result = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D08_fit",
        "seed": SEED,
        "classification": classification,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "full_trace": full_trace,
        "shared_state_window": shared,
        "quasinewton_state_replay": _replay_quasinewton(rows, matlab_x, matlab_grad, matlab_inv_h),
        "note": (
            "This diagnostic preserves the failed prospective holdout. It localizes the "
            "optimizer path and cannot change D08 acceptance or its frozen protocol."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n")
    print(json.dumps({"classification": classification}), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
