#!/usr/bin/env python3
"""Run M18A targeted parameter-recovery diagnosis."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from hgfx.diagnostics.parameter_recovery_diagnosis import (
    diagnose_parameter_recovery_dataset,
)
from hgfx.diagnostics.recovery import BINARY_VARIANTS
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


DEFAULT_TRIAL_COUNTS = (128, 256)
DEFAULT_REPLICATES = 3
DEFAULT_TRUTH_SCALE = 0.35


def _array(value):
    return np.asarray(value, dtype=np.float64).tolist()


def _safe_float(value):
    value = float(value)
    return value if np.isfinite(value) else None


def _parameter_record(dataset, parameter, profile):
    i = parameter.free_position
    truth = float(dataset.truth_free[i])
    baseline = float(dataset.baseline_free[i])
    truth_start = float(dataset.truth_start_free[i])
    oracle = float(dataset.oracle_single_free[i])
    perceptual_oracle = float(dataset.perceptual_oracle_free[i])

    sd = parameter.prior_sd
    return {
        "free_position": i,
        "full_index": parameter.full_index,
        "role": parameter.role,
        "transformed_name": parameter.transformed_name,
        "native_name": parameter.native_name,
        "prior_mean": parameter.prior_mean,
        "prior_sd": sd,
        "truth": truth,
        "baseline": baseline,
        "truth_start": truth_start,
        "oracle_single": oracle,
        "perceptual_oracle": _safe_float(perceptual_oracle),
        "absolute_error": {
            "baseline": abs(baseline - truth),
            "truth_start": abs(truth_start - truth),
            "oracle_single": abs(oracle - truth),
            "perceptual_oracle": (
                abs(perceptual_oracle - truth) if np.isfinite(perceptual_oracle) else None
            ),
        },
        "standardized_error": {
            "baseline": abs(baseline - truth) / sd,
            "truth_start": abs(truth_start - truth) / sd,
            "oracle_single": abs(oracle - truth) / sd,
            "perceptual_oracle": (
                abs(perceptual_oracle - truth) / sd if np.isfinite(perceptual_oracle) else None
            ),
        },
        "profile": {
            "likelihood_minimum": profile.likelihood_minimum,
            "joint_minimum": profile.joint_minimum,
            "likelihood_minimum_offset_sd": profile.likelihood_minimum_offset_sd,
            "joint_minimum_offset_sd": profile.joint_minimum_offset_sd,
            "likelihood_minimum_distance_to_prior_sd": (
                profile.likelihood_minimum_distance_to_prior_sd
            ),
            "joint_minimum_distance_to_prior_sd": (
                profile.joint_minimum_distance_to_prior_sd
            ),
            "likelihood_span": profile.likelihood_span,
            "joint_span": profile.joint_span,
            "likelihood_curvature": _safe_float(profile.likelihood_curvature),
            "joint_curvature": _safe_float(profile.joint_curvature),
        },
    }


def _aggregate_parameter(rows):
    baseline = np.asarray([row["standardized_error"]["baseline"] for row in rows])
    truth_start = np.asarray([row["standardized_error"]["truth_start"] for row in rows])
    oracle = np.asarray([row["standardized_error"]["oracle_single"] for row in rows])
    profile_offset = np.asarray(
        [abs(row["profile"]["likelihood_minimum_offset_sd"]) for row in rows]
    )
    joint_offset = np.asarray(
        [abs(row["profile"]["joint_minimum_offset_sd"]) for row in rows]
    )
    likelihood_span = np.asarray([row["profile"]["likelihood_span"] for row in rows])

    # Mechanism classifier is deliberately descriptive rather than a gate.
    # It asks which diagnostic removes the error.
    if float(np.median(profile_offset)) > 0.5:
        mechanism = "finite_data_likelihood_identifiability"
    elif float(np.median(oracle)) > 0.5:
        mechanism = "prior_or_one_parameter_map_bias"
    elif float(np.median(truth_start)) + 0.1 < float(np.median(baseline)):
        mechanism = "optimizer_start_sensitivity"
    else:
        mechanism = "cross_parameter_confounding_or_mixed"

    return {
        "n": len(rows),
        "median_standardized_error": {
            "baseline": float(np.median(baseline)),
            "truth_start": float(np.median(truth_start)),
            "oracle_single": float(np.median(oracle)),
        },
        "median_absolute_profile_offset_sd": {
            "likelihood": float(np.median(profile_offset)),
            "joint": float(np.median(joint_offset)),
        },
        "median_likelihood_span": float(np.median(likelihood_span)),
        "diagnostic_classification": mechanism,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="benchmarks/results/m18a_parameter_recovery_diagnosis.json")
    parser.add_argument("--seed", type=int, default=181800)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--max-iter", type=int, default=100)
    parser.add_argument("--profile-points", type=int, default=31)
    parser.add_argument("--truth-scale", type=float, default=DEFAULT_TRUTH_SCALE)
    args = parser.parse_args()

    options = QuasiNewtonOptions(max_iter=args.max_iter)
    dataset_rows = []
    parameter_rows = []

    for model_index, model in enumerate(BINARY_VARIANTS):
        for trial_count in DEFAULT_TRIAL_COUNTS:
            for replicate in range(args.replicates):
                seed = args.seed + model_index * 1_000_000 + trial_count * 100 + replicate
                diagnosis = diagnose_parameter_recovery_dataset(
                    model=model,
                    trial_count=trial_count,
                    replicate=replicate,
                    seed=seed,
                    truth_scale=args.truth_scale,
                    options=options,
                    profile_points=args.profile_points,
                )
                dataset_rows.append({
                    "model": model,
                    "trial_count": trial_count,
                    "truth_scale": args.truth_scale,
                    "replicate": replicate,
                    "seed": seed,
                    "baseline_neg_log_joint": diagnosis.baseline_neg_log_joint,
                    "truth_start_neg_log_joint": diagnosis.truth_start_neg_log_joint,
                    "truth_start_objective_improvement": (
                        diagnosis.baseline_neg_log_joint - diagnosis.truth_start_neg_log_joint
                    ),
                    "baseline_termination": diagnosis.baseline_termination,
                    "truth_start_termination": diagnosis.truth_start_termination,
                })
                for parameter, profile in zip(
                    diagnosis.parameter_metadata, diagnosis.profiles, strict=True
                ):
                    row = _parameter_record(diagnosis, parameter, profile)
                    row.update({
                        "model": model,
                        "trial_count": trial_count,
                        "truth_scale": args.truth_scale,
                        "replicate": replicate,
                        "seed": seed,
                    })
                    parameter_rows.append(row)

    aggregate = {}
    names = sorted({(row["model"], row["transformed_name"]) for row in parameter_rows})
    for model, name in names:
        selected = [
            row for row in parameter_rows
            if row["model"] == model and row["transformed_name"] == name
        ]
        aggregate[f"{model}:{name}"] = _aggregate_parameter(selected)

    payload = {
        "schema_version": 1,
        "milestone": "M18A",
        "purpose": "diagnose M18 parameter recovery failure mechanisms",
        "protocol": {
            "models": list(BINARY_VARIANTS),
            "trial_counts": list(DEFAULT_TRIAL_COUNTS),
            "replicates": args.replicates,
            "truth_scale": args.truth_scale,
            "max_iter": args.max_iter,
            "profile_points": args.profile_points,
        },
        "dataset_diagnostics": dataset_rows,
        "parameter_diagnostics": parameter_rows,
        "aggregate": aggregate,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "output": str(output),
        "aggregate": aggregate,
    }, indent=2))


if __name__ == "__main__":
    main()
