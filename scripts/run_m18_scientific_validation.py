#!/usr/bin/env python3
"""Run the M18 scientific-validation protocol and write machine-readable JSON."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path

import jax
import numpy as np

from hgfx.diagnostics.recovery import (
    BINARY_VARIANTS,
    deterministic_binary_inputs,
    fit_binary_variant,
    model_recovery_matrix,
    run_model_recovery,
    run_parameter_recovery,
    simulate_binary_variant,
    summarize_parameter_recovery,
)
from hgfx.gpu import BFGSOptions, fit_hgf_binary_unitsq_fast, has_gpu, select_device
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


PRESETS = {
    "ci": {
        "trial_counts": (48,),
        "parameter_replicates": 2,
        "model_replicates": 1,
        "truth_scales": (0.20,),
        "max_iter": 4,
    },
    "gate": {
        "trial_counts": (128, 256),
        "parameter_replicates": 6,
        "model_replicates": 3,
        "truth_scales": (0.15, 0.35),
        "max_iter": 100,
    },
}

# Frozen before final gate execution. These are deliberately modest minimum
# scientific sanity criteria, not claims of perfect identifiability.
GATE_CRITERIA = {
    "parameter_convergence_rate_min": 0.80,
    "parameter_median_correlation_min": 0.50,
    "parameter_median_standardized_rmse_max": 1.00,
    "model_recovery_balanced_accuracy_min": 0.50,
    "optimizer_objective_gap_max": 0.10,
    "cpu_gpu_objective_gap_max": 1e-7,
}


def _array(value):
    return np.asarray(value, dtype=np.float64).tolist()


def parameter_payload(records):
    summary = summarize_parameter_recovery(records)
    truth = np.vstack([row.true_free for row in records])
    scales = np.std(truth, axis=0, ddof=0)
    standardized = summary.rmse / np.where(scales > 1e-12, scales, 1.0)
    finite_corr = summary.correlation[np.isfinite(summary.correlation)]
    return {
        "summary": {
            "n": summary.n,
            "n_parameters": summary.n_parameters,
            "bias": _array(summary.bias),
            "rmse": _array(summary.rmse),
            "correlation": _array(summary.correlation),
            "convergence_rate": summary.convergence_rate,
            "median_absolute_error": _array(summary.median_absolute_error),
            "standardized_rmse": _array(standardized),
            "median_correlation": (
                float(np.median(finite_corr)) if finite_corr.size else None
            ),
            "median_standardized_rmse": float(np.median(standardized)),
        },
        "records": [
            {
                **{k: v for k, v in asdict(row).items()
                   if k not in {"true_free", "fitted_free", "error"}},
                "true_free": _array(row.true_free),
                "fitted_free": _array(row.fitted_free),
                "error": _array(row.error),
            }
            for row in records
        ],
    }


def model_payload(records):
    matrix = model_recovery_matrix(records, models=BINARY_VARIANTS)
    diagonal = np.diag(matrix)
    return {
        "matrix_order": list(BINARY_VARIANTS),
        "row_normalized_confusion_matrix": matrix.tolist(),
        "balanced_accuracy": float(np.mean(diagonal)),
        "records": [asdict(row) for row in records],
    }


def optimizer_agreement(seed: int, max_iter: int):
    inputs = deterministic_binary_inputs(64, seed)
    seed_responses = np.tile(np.array([0.0, 1.0]), 32)
    anchor = fit_binary_variant(
        seed_responses,
        inputs,
        "hgf_binary",
        options=QuasiNewtonOptions(max_iter=1),
    )
    responses, _ = simulate_binary_variant(
        "hgf_binary", inputs, anchor.initial_full, seed=seed + 1
    )
    compat = fit_binary_variant(
        responses,
        inputs,
        "hgf_binary",
        options=QuasiNewtonOptions(max_iter=max_iter),
    )
    cpu = select_device("cpu")
    fast = fit_hgf_binary_unitsq_fast(
        responses,
        inputs,
        device=cpu,
        optimizer=None,
    )
    return {
        "compat_neg_log_joint": float(compat.objective.neg_log_joint),
        "jax_cpu_neg_log_joint": float(fast.objective.neg_log_joint),
        "absolute_objective_gap": abs(
            float(compat.objective.neg_log_joint) - float(fast.objective.neg_log_joint)
        ),
        "compat_free": _array(compat.final_free),
        "jax_cpu_free": _array(fast.optimizer.position),
        "max_abs_parameter_gap": float(
            np.max(np.abs(compat.final_free - np.asarray(fast.optimizer.position)))
        ),
    }, responses, inputs


def cpu_gpu_agreement(responses, inputs):
    if not has_gpu():
        return {"available": False, "reason": "No JAX GPU visible in this runtime"}
    cpu = fit_hgf_binary_unitsq_fast(responses, inputs, device=select_device("cpu"))
    gpu = fit_hgf_binary_unitsq_fast(responses, inputs, device=select_device("gpu"))
    return {
        "available": True,
        "cpu_neg_log_joint": float(cpu.objective.neg_log_joint),
        "gpu_neg_log_joint": float(gpu.objective.neg_log_joint),
        "absolute_objective_gap": abs(
            float(cpu.objective.neg_log_joint) - float(gpu.objective.neg_log_joint)
        ),
        "max_abs_parameter_gap": float(
            np.max(np.abs(np.asarray(cpu.optimizer.position) - np.asarray(gpu.optimizer.position)))
        ),
    }


def evaluate_gate(payload):
    parameter_summaries = [
        item["summary"] for item in payload["parameter_recovery"].values()
    ]
    convergence = min(item["convergence_rate"] for item in parameter_summaries)
    correlations = [
        item["median_correlation"] for item in parameter_summaries
        if item["median_correlation"] is not None
    ]
    median_corr = min(correlations) if correlations else float("-inf")
    standardized_rmse = max(
        item["median_standardized_rmse"] for item in parameter_summaries
    )
    model_accuracy = payload["model_recovery"]["balanced_accuracy"]
    optimizer_gap = payload["optimizer_agreement"]["absolute_objective_gap"]
    checks = {
        "parameter_convergence_rate": convergence
        >= GATE_CRITERIA["parameter_convergence_rate_min"],
        "parameter_median_correlation": median_corr
        >= GATE_CRITERIA["parameter_median_correlation_min"],
        "parameter_standardized_rmse": standardized_rmse
        <= GATE_CRITERIA["parameter_median_standardized_rmse_max"],
        "model_recovery_balanced_accuracy": model_accuracy
        >= GATE_CRITERIA["model_recovery_balanced_accuracy_min"],
        "optimizer_objective_agreement": optimizer_gap
        <= GATE_CRITERIA["optimizer_objective_gap_max"],
    }
    gpu = payload["cpu_gpu_agreement"]
    if gpu["available"]:
        checks["cpu_gpu_objective_agreement"] = (
            gpu["absolute_objective_gap"]
            <= GATE_CRITERIA["cpu_gpu_objective_gap_max"]
        )
    return {
        "criteria": GATE_CRITERIA,
        "observed": {
            "minimum_parameter_convergence_rate": convergence,
            "minimum_parameter_median_correlation": median_corr,
            "maximum_parameter_median_standardized_rmse": standardized_rmse,
            "model_recovery_balanced_accuracy": model_accuracy,
            "optimizer_absolute_objective_gap": optimizer_gap,
        },
        "checks": checks,
        "pass": bool(all(checks.values())),
        "gpu_check_required_for_this_runtime": bool(gpu["available"]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=tuple(PRESETS), default="ci")
    parser.add_argument(
        "--output",
        default="benchmarks/results/m18_scientific_validation.json",
    )
    parser.add_argument("--seed", type=int, default=18018)
    args = parser.parse_args()
    cfg = PRESETS[args.preset]
    options = QuasiNewtonOptions(max_iter=cfg["max_iter"])

    parameter = {}
    for model in BINARY_VARIANTS:
        combined = []
        for scale in cfg["truth_scales"]:
            combined.extend(run_parameter_recovery(
                model=model,
                trial_counts=cfg["trial_counts"],
                replicates=cfg["parameter_replicates"],
                seed=args.seed + int(scale * 10_000),
                truth_scale=scale,
                options=options,
            ))
        parameter[model] = parameter_payload(combined)

    model_records = []
    for scale in cfg["truth_scales"]:
        model_records.extend(run_model_recovery(
            trial_counts=cfg["trial_counts"],
            replicates=cfg["model_replicates"],
            seed=args.seed + 500_000 + int(scale * 10_000),
            truth_scale=scale,
            options=options,
        ))

    optimizer, responses, inputs = optimizer_agreement(
        args.seed + 900_000, cfg["max_iter"]
    )
    payload = {
        "schema_version": 1,
        "milestone": "M18",
        "preset": args.preset,
        "protocol": cfg,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "jax": jax.__version__,
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "parameter_recovery": parameter,
        "model_recovery": model_payload(model_records),
        "optimizer_agreement": optimizer,
        "cpu_gpu_agreement": cpu_gpu_agreement(responses, inputs),
    }
    payload["gate"] = evaluate_gate(payload)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "preset": args.preset,
        "gate_pass": payload["gate"]["pass"],
        "model_recovery_balanced_accuracy": payload["model_recovery"]["balanced_accuracy"],
    }, indent=2))
    # CI preset validates execution/reproducibility, not paper-level statistical power.
    if args.preset == "gate" and not payload["gate"]["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
