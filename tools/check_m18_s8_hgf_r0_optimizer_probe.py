#!/usr/bin/env python3
"""Localize the frozen S7 HGF R0 optimizer mismatch for S8."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.diagnostics.recovery import _objective_for_variant, fit_binary_variant
from hgfx.optim.ridders import RiddersOptions, ridders_gradient

PROTOCOL = "m18-s8-hgf-r0-optimizer-probe-1"
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CASE_ID = "PR-hgf_binary-T256-S0.35-R0"
CASE_SHA = "1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5"
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


def _stats(actual, expected) -> dict:
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    if a.shape != e.shape:
        return {"shape_mismatch": [list(a.shape), list(e.shape)], "gate_close": False}
    diff = np.abs(a - e)
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    finite = np.isfinite(diff)
    max_abs = float(np.max(diff[finite])) if np.any(finite) else float("nan")
    allowed = ATOL + RTOL * np.abs(e)
    ratio = np.divide(diff, allowed, out=np.full_like(diff, np.inf), where=allowed > 0)
    max_ratio = float(np.max(ratio[finite])) if np.any(finite) else float("nan")
    first_gate = None
    if not np.all(close):
        idx = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
        first_gate = {
            "index_zero_based": list(idx),
            "hgfx": float(a[idx] if idx else a.item()),
            "matlab": float(e[idx] if idx else e.item()),
            "abs_diff": float(diff[idx] if idx else diff.item()),
        }
    exact = (a == e) | (np.isnan(a) & np.isnan(e))
    first_exact = None
    if not np.all(exact):
        idx = tuple(int(i) for i in np.argwhere(~exact)[0]) if np.ndim(exact) else ()
        first_exact = {
            "index_zero_based": list(idx),
            "hgfx": float(a[idx] if idx else a.item()),
            "matlab": float(e[idx] if idx else e.item()),
            "abs_diff": float(diff[idx] if idx else diff.item()),
        }
    return {
        "gate_close": bool(np.all(close)),
        "max_abs": max_abs,
        "max_gate_ratio": max_ratio,
        "first_gate_divergence": first_gate,
        "first_exact_difference": first_exact,
    }


def _first_trace(actual, expected, label: str) -> dict:
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    result = {"label": label, "actual_shape": list(a.shape), "expected_shape": list(e.shape)}
    if a.ndim != e.ndim:
        result["gate"] = {"rank_mismatch": True}
        return result
    overlap = tuple(slice(0, min(x, y)) for x, y in zip(a.shape, e.shape))
    result["gate"] = _stats(a[overlap], e[overlap])
    result["shape_mismatch"] = a.shape != e.shape
    return result


def _matlab_inverse_hessian(raw):
    if isinstance(raw, list) and len(raw) == 0:
        return None
    return _array(raw)


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


def _replay_transitions(rows, xs, grads, inv_hs) -> list[dict]:
    out = []
    max_step = 1.0
    max_regu = 16
    for q in range(len(rows) - 1):
        if int(rows[q + 1]) != int(rows[q]) + 1:
            continue
        current_t = _matlab_inverse_hessian(inv_hs[q])
        next_t = _matlab_inverse_hessian(inv_hs[q + 1])
        if current_t is None or next_t is None:
            continue
        x = np.asarray(xs[q], dtype=np.float64).reshape(-1)
        nx = np.asarray(xs[q + 1], dtype=np.float64).reshape(-1)
        g = np.asarray(grads[q], dtype=np.float64).reshape(-1)
        ng = np.asarray(grads[q + 1], dtype=np.float64).reshape(-1)
        desc = -(current_t @ g)
        size = float(np.sqrt(np.dot(desc, desc)))
        if size > max_step:
            desc = desc * max_step / size
        candidates = [x + (np.float64(0.5) ** j) * desc for j in range(max_regu + 1)]
        errors = [float(np.max(np.abs(candidate - nx))) for candidate in candidates]
        regu = int(np.argmin(errors))
        predicted_x = candidates[regu]
        dx = nx - x
        dg = ng - g
        dgdx = float(np.dot(dg, dx))
        threshold = float(np.sqrt(np.finfo(np.float64).eps * np.dot(dg, dg) * np.dot(dx, dx)))
        predicted_t = current_t.copy()
        updated = dgdx > threshold
        if updated:
            dg_t = dg @ current_t
            dg_t_dg = float(np.dot(dg_t, dg))
            u = dx / dgdx - dg_t / dg_t_dg
            predicted_t = current_t + np.outer(dx, dx) / dgdx - np.outer(dg_t, dg_t) / dg_t_dg + dg_t_dg * np.outer(u, u)
        out.append({
            "from_matlab_row_1based": int(rows[q]),
            "to_matlab_row_1based": int(rows[q + 1]),
            "inferred_regularizations": regu,
            "step_fraction": float(np.float64(0.5) ** regu),
            "step_replay": _stats(predicted_x, nx),
            "bfgs_updated": bool(updated),
            "inverse_hessian_replay": _stats(predicted_t, next_t),
        })
    return out


def main(fixture_path: Path, matlab_path: Path, output_path: Path) -> int:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    ref = json.loads(matlab_path.read_text(encoding="utf-8"))
    if ref.get("protocol") != PROTOCOL or ref.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("Frozen S8 protocol/reference mismatch")
    if ref.get("case_id") != CASE_ID or ref.get("case_sha256") != CASE_SHA:
        raise ValueError("Frozen R0 case mismatch")
    cases = [c for c in fixture.get("cases", []) if c.get("case_id") == CASE_ID]
    if len(cases) != 1 or cases[0].get("case_sha256") != CASE_SHA:
        raise ValueError("Immutable S7 R0 fixture missing or changed")
    case = cases[0]

    u = np.asarray(case["u"], dtype=np.float64)
    y = np.asarray(case["y"], dtype=np.float64)
    fit = fit_binary_variant(y, u, "hgf_binary")
    actual = fit.optimizer

    matlab_x = _array(ref["trace"]["full_x"])
    matlab_val = _array(ref["trace"]["full_val"]).reshape(-1)
    matlab_rst = _array(ref["trace"]["full_rst"]).reshape(-1)
    full_trace = {
        "x": _first_trace(actual.iter_x, matlab_x, "optimizer.iter.x"),
        "val": _first_trace(actual.iter_val, matlab_val, "optimizer.iter.val"),
        "rst": _first_trace(np.asarray(actual.iter_resets, dtype=np.float64), matlab_rst, "optimizer.iter.rst"),
    }

    states = ref["trace"]["states"]
    rows = _array(states["rows"]).astype(np.int64).reshape(-1)
    xs = _array(states["x"])
    vals = _array(states["val"]).reshape(-1)
    grads = _array(states["grad"])
    grad_errs = _array(states["grad_err"])
    inv_hs = states["invH"]

    shared = []
    shared_failure = False
    for q, row in enumerate(rows):
        point = np.asarray(xs[q], dtype=np.float64).reshape(-1)
        objective = _python_objective(case, point)
        grad, grad_err = ridders_gradient(lambda z: _python_objective(case, z), point, RiddersOptions(min_steps=10))
        index = int(row) - 1
        item = {
            "matlab_row_1based": int(row),
            "actual_path_x": _stats(actual.iter_x[index], point) if index < actual.iter_x.shape[0] else {"missing": True},
            "actual_path_val": _stats(actual.iter_val[index], vals[q]) if index < actual.iter_val.shape[0] else {"missing": True},
            "objective_at_exact_matlab_x": _stats([objective], [vals[q]]),
            "gradient_at_exact_matlab_x": _stats(grad, grads[q]),
            "gradient_error_at_exact_matlab_x": _stats(grad_err, grad_errs[q]),
        }
        expected_t = _matlab_inverse_hessian(inv_hs[q])
        if expected_t is None or index >= len(actual.iter_inverse_hessians):
            item["actual_path_inverse_hessian"] = {"available": False}
        else:
            item["actual_path_inverse_hessian"] = {"available": True, **_stats(actual.iter_inverse_hessians[index], expected_t)}
        if not item["objective_at_exact_matlab_x"].get("gate_close", False) or not item["gradient_at_exact_matlab_x"].get("gate_close", False):
            shared_failure = True
        shared.append(item)

    transitions = _replay_transitions(rows, xs, grads, inv_hs)
    algebra_failure = any(
        not t["step_replay"].get("gate_close", False) or not t["inverse_hessian_replay"].get("gate_close", False)
        for t in transitions
    )
    path_diverged = not full_trace["x"]["gate"].get("gate_close", False)
    mismatch_reproduced = not np.isclose(fit.optimizer.arg_min, _array(ref["final_free"]).reshape(-1), rtol=RTOL, atol=ATOL).all()

    if not shared or not transitions:
        classification = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif shared_failure:
        classification = "SHARED_STATE_OBJECTIVE_OR_GRADIENT_DIVERGENCE"
    elif algebra_failure:
        classification = "QUASINEWTON_STATE_ALGEBRA_MISMATCH"
    elif path_diverged and mismatch_reproduced:
        classification = "SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES"
    else:
        classification = "NO_REQUIRED_MISMATCH_REPRODUCED"

    payload = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": CASE_ID,
        "case_sha256": CASE_SHA,
        "existing_gate": {"rtol": RTOL, "atol": ATOL},
        "classification": classification,
        "acceptance_effect": "NONE_DIAGNOSTIC_ONLY",
        "matlab_final_free": _array(ref["final_free"]).reshape(-1).tolist(),
        "hgfx_final_free": fit.final_free.tolist(),
        "final_comparison": _stats(fit.final_free, _array(ref["final_free"]).reshape(-1)),
        "matlab_negLj": float(_array(ref["negLj"]).reshape(-1)[0]),
        "hgfx_negLj": float(fit.objective.neg_log_joint),
        "full_trace": full_trace,
        "shared_state_rows": shared,
        "quasinewton_state_replay": transitions,
        "note": "Diagnostic only. The original S7 failure remains preserved; no threshold, seed, data, start, model, or optimizer setting is changed.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps({"classification": classification, "final_comparison": payload["final_comparison"]}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("matlab", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.fixture, args.matlab, args.output))
