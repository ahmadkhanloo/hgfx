#!/usr/bin/env python3
"""Execute the frozen M18 S9 robustness/backend matrix."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

import jax
import numpy as np

from hgfx.compat.configs import hgf_binary_config
from hgfx.compat.fitting import fit_hgf_binary_unitsq_compat, hgf_binary_unitsq_fit_problem
from hgfx.compat.simulation import ehgf_binary_config, uhgf_binary_config
from hgfx.gpu import (
    BFGSOptimizer,
    BFGSOptions,
    fast_binary_hgf,
    fast_binary_unitsq_value_and_grad,
    fit_hgf_binary_unitsq_fast,
    has_gpu,
    select_device,
)
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.models.hgf_binary import hgf_binary
from hgfx.models.uhgf_binary import uhgf_binary

PROTOCOL = "m18-s9-robustness-backend-1"
TRIAL_COUNTS = (128, 256)
FORWARD_RTOL = 3e-10
FORWARD_ATOL = 3e-11
GRAD_RTOL = 2e-4
GRAD_ATOL = 2e-5
FINAL_OBJECTIVE_GAP_MAX = 0.10
CPU_GPU_OBJECTIVE_GAP_MAX = 1e-7

MODELS = {
    "hgf_binary": (hgf_binary_config, hgf_binary, "hgf"),
    "ehgf_binary": (ehgf_binary_config, ehgf_binary, "ehgf"),
    "uhgf_binary": (uhgf_binary_config, uhgf_binary, "uhgf"),
}


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def _binary_inputs(trials: int) -> np.ndarray:
    rng = np.random.default_rng(910000 + trials)
    values = rng.integers(0, 2, size=trials).astype(np.float64)
    values[:8] = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.float64)
    return values


def _ignored_indices(trials: int) -> tuple[int, ...]:
    return (7, trials // 2, trials - 5)


def _forward_input(trials: int, regime: str) -> np.ndarray:
    values = _binary_inputs(trials)
    if regime == "ignored_missing":
        values = values.copy()
        values[list(_ignored_indices(trials))] = np.nan
        return values
    if regime == "irregular":
        intervals = 0.7 + (np.arange(trials, dtype=np.float64) % 9.0) * 0.075
        return np.column_stack((values, intervals))
    if regime != "regular":
        raise ValueError(regime)
    return values


def _fit_data(trials: int, missing: bool) -> tuple[np.ndarray, np.ndarray]:
    u = _binary_inputs(trials)
    rng = np.random.default_rng(920000 + trials)
    probability = 0.30 + 0.40 * u
    y = (rng.random(trials) < probability).astype(np.float64)
    if missing:
        u = u.copy()
        u[list(_ignored_indices(trials))] = np.nan
    return y, u


def _array_comparison(actual, expected, *, rtol=FORWARD_RTOL, atol=FORWARD_ATOL) -> dict:
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    same_shape = a.shape == e.shape
    passed = bool(same_shape and np.allclose(a, e, rtol=rtol, atol=atol, equal_nan=True))
    if not same_shape:
        return {"pass": False, "shape_actual": list(a.shape), "shape_expected": list(e.shape)}
    finite = np.isfinite(a) & np.isfinite(e)
    max_abs = float(np.max(np.abs(a[finite] - e[finite]))) if np.any(finite) else 0.0
    nonfinite_match = bool(np.array_equal(np.isnan(a), np.isnan(e)))
    return {"pass": passed, "max_abs_finite": max_abs, "nonfinite_nan_mask_match": nonfinite_match}


def _forward_matrix() -> list[dict]:
    rows: list[dict] = []
    for trials in TRIAL_COUNTS:
        for model, (config_factory, compat, update_type) in MODELS.items():
            for regime in ("regular", "ignored_missing", "irregular"):
                inputs = _forward_input(trials, regime)
                parameters = config_factory().resolve_placeholders(inputs).priormus.copy()
                kwargs = {"transformed": True}
                if regime == "irregular":
                    kwargs["irregular_intervals"] = True
                if model == "hgf_binary":
                    kwargs["validate"] = False
                expected_traj, expected_states = compat(inputs, parameters, **kwargs)
                actual = fast_binary_hgf(
                    inputs,
                    parameters,
                    update_type=update_type,
                    transformed=True,
                    irregular_intervals=regime == "irregular",
                    device=select_device("cpu"),
                )
                state_cmp = _array_comparison(actual.inf_states, expected_states)
                fields = {
                    key: _array_comparison(actual.trajectory[key], value)
                    for key, value in expected_traj.items()
                }
                passed = bool(state_cmp["pass"] and all(item["pass"] for item in fields.values()))
                rows.append({
                    "model": model,
                    "trials": trials,
                    "regime": regime,
                    "pass": passed,
                    "states": state_cmp,
                    "trajectory": fields,
                })
    return rows


def _boundary_case() -> dict:
    parameters = np.array(
        [
            np.nan, 8.0, 1.0,
            np.nan, np.log(0.1), 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, -3.0, -6.0,
        ],
        dtype=np.float64,
    )
    inputs = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.float64)
    rows = []
    for model, compat, update_type in (
        ("hgf_binary", hgf_binary, "hgf"),
        ("ehgf_binary", ehgf_binary, "ehgf"),
    ):
        kwargs = {"transformed": True}
        if model == "hgf_binary":
            kwargs["validate"] = False
        expected, _ = compat(inputs, parameters, **kwargs)
        actual = fast_binary_hgf(
            inputs,
            parameters,
            update_type=update_type,
            transformed=True,
            device=select_device("cpu"),
        )
        exp = float(expected["muhat"][0, 0])
        obs = float(np.asarray(actual.trajectory["muhat"])[0, 0])
        semantic = exp > 0.999 if model == "hgf_binary" else exp == 0.999
        rows.append({
            "model": model,
            "expected_first_muhat1": exp,
            "observed_first_muhat1": obs,
            "semantic_precondition": bool(semantic),
            "pass": bool(semantic and np.isclose(obs, exp, rtol=FORWARD_RTOL, atol=FORWARD_ATOL)),
        })
    return {"cases": rows, "pass": bool(all(row["pass"] for row in rows))}


def _central_difference(function, point: np.ndarray, step: float = 1e-5) -> np.ndarray:
    gradient = np.empty_like(point)
    for index in range(point.size):
        delta = np.zeros_like(point)
        delta[index] = step
        gradient[index] = (function(point + delta) - function(point - delta)) / (2.0 * step)
    return gradient


def _backend_fit_matrix() -> tuple[list[dict], list[dict]]:
    shared_rows: list[dict] = []
    fit_rows: list[dict] = []
    cpu = select_device("cpu")
    for trials in TRIAL_COUNTS:
        for regime in ("regular", "ignored_missing"):
            responses, inputs = _fit_data(trials, missing=regime == "ignored_missing")
            problem = hgf_binary_unitsq_fit_problem(responses, inputs)
            start = problem.initial_free
            delta = 1e-4 * (np.arange(start.size, dtype=np.float64) + 1.0)
            probes = (
                ("start", start),
                ("start_plus_delta", start + delta),
                ("start_minus_delta", start - delta),
            )
            for probe_name, point in probes:
                expected_value = float(problem.evaluate_free(point))
                expected_gradient = _central_difference(problem.evaluate_free, point)
                actual = fast_binary_unitsq_value_and_grad(
                    responses, inputs, point, device=cpu
                )
                actual_value = float(actual.value)
                actual_gradient = np.asarray(actual.gradient, dtype=np.float64)
                value_pass = bool(np.isclose(
                    actual_value, expected_value, rtol=FORWARD_RTOL, atol=FORWARD_ATOL
                ))
                grad_pass = bool(np.allclose(
                    actual_gradient, expected_gradient,
                    rtol=GRAD_RTOL, atol=GRAD_ATOL, equal_nan=True,
                ))
                shared_rows.append({
                    "trials": trials,
                    "regime": regime,
                    "probe": probe_name,
                    "compat_value": expected_value,
                    "jax_cpu_value": actual_value,
                    "value_abs_gap": abs(actual_value - expected_value),
                    "gradient_max_abs_gap": float(np.max(np.abs(actual_gradient - expected_gradient))),
                    "value_pass": value_pass,
                    "gradient_pass": grad_pass,
                    "pass": bool(value_pass and grad_pass),
                })

            compat_fit = fit_hgf_binary_unitsq_compat(responses, inputs)
            fast_fit = fit_hgf_binary_unitsq_fast(
                responses,
                inputs,
                device=cpu,
                optimizer=BFGSOptimizer(BFGSOptions(max_iter=100)),
            )
            compat_value = float(compat_fit.objective.neg_log_joint)
            fast_value = float(fast_fit.objective.neg_log_joint)
            gap = abs(fast_value - compat_value)
            fit_rows.append({
                "trials": trials,
                "regime": regime,
                "compat_final_objective": compat_value,
                "jax_cpu_final_objective": fast_value,
                "final_objective_gap": gap,
                "threshold": FINAL_OBJECTIVE_GAP_MAX,
                "compat_termination": compat_fit.optimizer.termination,
                "jax_success": bool(fast_fit.optimizer.success),
                "jax_status": int(np.asarray(fast_fit.optimizer.status)),
                "pass": bool(np.isfinite(gap) and gap <= FINAL_OBJECTIVE_GAP_MAX),
            })
    return shared_rows, fit_rows


def _physical_gpu_matrix() -> dict:
    if not has_gpu():
        return {
            "available": False,
            "classification": "PHYSICAL_GPU_REVALIDATION_REQUIRED",
            "reason": "No physical JAX GPU visible in this execution environment; CPU evidence cannot close GPU applicability.",
            "cases": [],
        }

    cpu = select_device("cpu")
    gpu = select_device("gpu")
    rows = []
    for trials in TRIAL_COUNTS:
        for regime in ("regular", "ignored_missing"):
            responses, inputs = _fit_data(trials, missing=regime == "ignored_missing")
            optimizer = BFGSOptimizer(BFGSOptions(max_iter=100))
            cpu_fit = fit_hgf_binary_unitsq_fast(
                responses, inputs, device=cpu, optimizer=optimizer
            )
            gpu_fit = fit_hgf_binary_unitsq_fast(
                responses, inputs, device=gpu, optimizer=optimizer
            )
            cpu_value = float(cpu_fit.objective.neg_log_joint)
            gpu_value = float(gpu_fit.objective.neg_log_joint)
            gap = abs(gpu_value - cpu_value)
            resident = gpu_fit.forward.inf_states.devices() == {gpu}
            rows.append({
                "trials": trials,
                "regime": regime,
                "cpu_final_objective": cpu_value,
                "gpu_final_objective": gpu_value,
                "final_objective_gap": gap,
                "threshold": CPU_GPU_OBJECTIVE_GAP_MAX,
                "gpu_device_resident": bool(resident),
                "pass": bool(np.isfinite(gap) and gap <= CPU_GPU_OBJECTIVE_GAP_MAX and resident),
            })
    passed = bool(all(row["pass"] for row in rows))
    return {
        "available": True,
        "classification": "PASS_PHYSICAL_GPU_APPLICABILITY" if passed else "PHYSICAL_GPU_MISMATCH",
        "device": str(gpu),
        "cases": rows,
        "pass": passed,
    }


def main(output_path: str, require_gpu: bool) -> int:
    forward = _forward_matrix()
    boundary = _boundary_case()
    shared, fits = _backend_fit_matrix()
    gpu = _physical_gpu_matrix()

    cpu_pass = bool(
        all(row["pass"] for row in forward)
        and boundary["pass"]
        and all(row["pass"] for row in shared)
        and all(row["pass"] for row in fits)
    )
    if not cpu_pass:
        classification = "BACKEND_IMPLEMENTATION_MISMATCH"
    elif gpu.get("classification") == "PASS_PHYSICAL_GPU_APPLICABILITY":
        classification = "PASS_S9_ROBUSTNESS_BACKEND"
    else:
        classification = "CPU_PASS_PHYSICAL_GPU_REVALIDATION_REQUIRED"

    payload = {
        "protocol": PROTOCOL,
        "source_commit": _git_head(),
        "environment": {
            "python": platform.python_version(),
            "jax": jax.__version__,
            "backend": jax.default_backend(),
            "devices": [str(device) for device in jax.devices()],
        },
        "criteria": {
            "forward_rtol": FORWARD_RTOL,
            "forward_atol": FORWARD_ATOL,
            "gradient_rtol": GRAD_RTOL,
            "gradient_atol": GRAD_ATOL,
            "compat_vs_jax_cpu_final_objective_gap_max": FINAL_OBJECTIVE_GAP_MAX,
            "jax_cpu_vs_physical_gpu_final_objective_gap_max": CPU_GPU_OBJECTIVE_GAP_MAX,
        },
        "forward_robustness": forward,
        "boundary_semantics": boundary,
        "shared_state_objective_gradient": shared,
        "fit_backend_agreement": fits,
        "cpu_backend_pass": cpu_pass,
        "physical_gpu": gpu,
        "classification": classification,
        "gate_pass": classification == "PASS_S9_ROBUSTNESS_BACKEND",
        "historical_h100_note": "The S9 standard-HGF fast-engine semantic repair changes the numerically relevant GPU path relative to historical H100 source e6f1740ec6cacc55323c6a4d4ca521430c9f3dbf; physical current-head revalidation is therefore required.",
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "cpu_backend_pass": cpu_pass,
        "physical_gpu": gpu.get("classification"),
        "classification": classification,
        "gate_pass": payload["gate_pass"],
    }, indent=2))

    if require_gpu:
        return 0 if payload["gate_pass"] else 3
    return 0 if cpu_pass else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="benchmarks/results/m18_s9_backend_robustness.json",
    )
    parser.add_argument("--require-gpu", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.output, args.require_gpu))
