#!/usr/bin/env python3
"""Diagnose D08 epsi mismatch as same-endpoint drift vs endpoint sensitivity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import hgfx
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config
from hgfx.core.trials import build_trial_masks

RTOL = 3e-8
ATOL = 3e-10


def close(a, b) -> bool:
    return bool(np.isclose(np.float64(a), np.float64(b), rtol=RTOL, atol=ATOL, equal_nan=True))


def scalar_record(actual, expected):
    a = np.float64(actual)
    e = np.float64(expected)
    return {
        "hgfx": float(a),
        "matlab": float(e),
        "abs_diff": float(abs(a - e)),
        "close": close(a, e),
        "exact": bool(a == e),
    }


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference["reference_commit"] != REFERENCE_COMMIT:
        raise ValueError("Reference commit mismatch")
    if reference["protocol"] != "m18-d08-endpoint-diagnostic-1":
        raise ValueError("Diagnostic protocol mismatch")
    if reference["case_id"] != "D08_fit":
        raise ValueError("Unexpected case")

    u = _array(reference["inputs"]).reshape(-1)
    y = _array(reference["responses"]).reshape(-1)
    expected_final = _array(reference["final"]).reshape(-1)
    expected_epsi = _array(reference["traj"]["epsi"])
    expected_psi = _array(reference["traj"]["psi"])
    expected_da = _array(reference["traj"]["da"])
    expected_dau = _array(reference["traj"]["dau"]).reshape(-1)

    prc = resolve_config("uhgf")
    obs = resolve_config("gaussian_obs")
    est = hgfx.fit_model(y, u, prc, obs)
    actual_final = np.asarray(est.optim["final"], dtype=np.float64).reshape(-1)
    actual_epsi = np.asarray(est.traj["epsi"], dtype=np.float64)

    if actual_epsi.shape != expected_epsi.shape:
        raise ValueError(f"epsi shape mismatch: {actual_epsi.shape} != {expected_epsi.shape}")

    finite = np.isfinite(actual_epsi) & np.isfinite(expected_epsi)
    absolute = np.full(actual_epsi.shape, np.nan, dtype=np.float64)
    absolute[finite] = np.abs(actual_epsi[finite] - expected_epsi[finite])
    if not np.any(finite):
        raise ValueError("No finite epsi values")

    max_flat = int(np.nanargmax(absolute))
    max_index = tuple(int(v) for v in np.unravel_index(max_flat, absolute.shape))
    close_mask = np.isclose(actual_epsi, expected_epsi, rtol=RTOL, atol=ATOL, equal_nan=True)
    divergent = np.argwhere(~close_mask)
    first_index = tuple(int(v) for v in divergent[0]) if divergent.size else None
    focus = first_index if first_index is not None else max_index
    trial, level = focus

    prc_resolved = prc.resolve_placeholders(u)
    obs_resolved = obs.resolve_placeholders(u)
    problem = WorkflowFitProblem(y, u, prc_resolved, obs_resolved)
    masks = build_trial_masks(y, u)
    ignored = tuple(int(i) for i in np.flatnonzero(masks.ignored))

    def forward_at(full):
        traj, states = problem.forward(
            u,
            np.asarray(full, dtype=np.float64)[: problem.n_perceptual],
            transformed=True,
            irregular_intervals=bool(prc_resolved.options.get("irregular_intervals", False)),
            ignored_trials=ignored,
        )
        return traj, states

    matlab_endpoint_traj, _ = forward_at(expected_final)
    hgfx_endpoint_traj, _ = forward_at(actual_final)

    expected_focus = np.float64(expected_epsi[focus])
    actual_focus = np.float64(actual_epsi[focus])
    replay_matlab_focus = np.float64(matlab_endpoint_traj["epsi"][focus])
    replay_hgfx_focus = np.float64(hgfx_endpoint_traj["epsi"][focus])

    if level == 0:
        expected_error = np.float64(expected_dau[trial])
        actual_error = np.float64(est.traj["dau"][trial])
        replay_matlab_error = np.float64(matlab_endpoint_traj["dau"][trial])
        error_name = "dau"
    else:
        expected_error = np.float64(expected_da[trial, level - 1])
        actual_error = np.float64(est.traj["da"][trial, level - 1])
        replay_matlab_error = np.float64(matlab_endpoint_traj["da"][trial, level - 1])
        error_name = f"da[{level - 1}]"

    endpoint_records = []
    for index, (actual, expected) in enumerate(zip(actual_final, expected_final)):
        if np.isnan(actual) and np.isnan(expected):
            continue
        endpoint_records.append(
            {
                "index": int(index),
                "hgfx": float(actual),
                "matlab": float(expected),
                "abs_diff": float(abs(actual - expected)),
                "exact": bool(actual == expected),
            }
        )

    baseline_diff = float(abs(actual_focus - expected_focus))
    sensitivity = []
    for index in np.asarray(problem.free_indices, dtype=np.int64).reshape(-1):
        hybrid = actual_final.copy()
        hybrid[index] = expected_final[index]
        hybrid_traj, _ = forward_at(hybrid)
        value = np.float64(hybrid_traj["epsi"][focus])
        diff = float(abs(value - expected_focus))
        sensitivity.append(
            {
                "index": int(index),
                "hgfx_final": float(actual_final[index]),
                "matlab_final": float(expected_final[index]),
                "parameter_abs_diff": float(abs(actual_final[index] - expected_final[index])),
                "hybrid_focus_epsi": float(value),
                "focus_abs_diff": diff,
                "improvement_vs_hgfx": float(baseline_diff - diff),
            }
        )
    sensitivity.sort(key=lambda row: row["improvement_vs_hgfx"], reverse=True)

    same_endpoint_close = close(replay_matlab_focus, expected_focus)
    fitted_close = close(actual_focus, expected_focus)
    if not same_endpoint_close:
        classification = "SAME_ENDPOINT_IMPLEMENTATION_MISMATCH"
    elif not fitted_close:
        classification = "ENDPOINT_SENSITIVITY"
    else:
        classification = "PASS"

    result = {
        "protocol": reference["protocol"],
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D08_fit",
        "classification": classification,
        "gate_tolerance": {"rtol": RTOL, "atol": ATOL},
        "first_gate_divergence": list(first_index) if first_index is not None else None,
        "max_abs_index": list(max_index),
        "max_abs_diff": float(absolute[max_index]),
        "focus_index": list(focus),
        "focus": {
            "epsi_fit": scalar_record(actual_focus, expected_focus),
            "epsi_replay_matlab_endpoint": scalar_record(replay_matlab_focus, expected_focus),
            "epsi_replay_hgfx_endpoint": scalar_record(replay_hgfx_focus, expected_focus),
            "psi_fit": scalar_record(est.traj["psi"][focus], expected_psi[focus]),
            "psi_replay_matlab_endpoint": scalar_record(matlab_endpoint_traj["psi"][focus], expected_psi[focus]),
            "error_component_name": error_name,
            "error_fit": scalar_record(actual_error, expected_error),
            "error_replay_matlab_endpoint": scalar_record(replay_matlab_error, expected_error),
        },
        "endpoint_parameters": endpoint_records,
        "one_parameter_matlab_replacement": sensitivity,
        "objective": {
            "hgfx_fit_negLj": float(est.optim["negLj"]),
            "matlab_negLj": float(_array(reference["negLj"]).reshape(-1)[0]),
            "hgfx_at_matlab_final_negLj": float(problem.evaluate_full(expected_final).neg_log_joint),
        },
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
