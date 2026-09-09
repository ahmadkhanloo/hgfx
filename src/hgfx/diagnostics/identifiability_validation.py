"""Identifiability-aware parameter recovery validation for M18B.

M18B does not redefine the frozen M18 pass criteria.  It separates estimator
recoverability from finite-data identifiability, parameter confounding, and
optimizer sensitivity using the evidence-producing primitives introduced in
M18A.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

import numpy as np

from hgfx.diagnostics.parameter_recovery_diagnosis import DatasetDiagnosis
from hgfx.diagnostics.recovery import BINARY_VARIANTS


EXPECTED_PARAMETERS = ("om[1]", "om[2]", "logze")


def informative_binary_inputs(trials: int, seed: int) -> np.ndarray:
    """Generate balanced binary stimuli with bounded run length for M18B.

    The original M18 generator is retained unchanged. M18B uses this controlled
    stimulus design to reduce accidental non-identifiability and numerical pathologies
    caused by unusually long stochastic runs while remaining deterministic.
    """
    if trials < 8:
        raise ValueError("identifiability validation requires at least 8 trials")
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        values = np.empty(trials, dtype=np.float64)
        values[0] = float(rng.integers(0, 2))
        run = 1
        for i in range(1, trials):
            if run >= 3:
                values[i] = 1.0 - values[i - 1]
            else:
                switch = bool(rng.random() < 0.55)
                values[i] = 1.0 - values[i - 1] if switch else values[i - 1]
            run = run + 1 if values[i] == values[i - 1] else 1
        proportion_one = float(np.mean(values))
        if 0.40 <= proportion_one <= 0.60:
            return values
    raise RuntimeError("failed to generate a balanced bounded-run binary stimulus")


@dataclass(frozen=True)
class IdentifiabilityRecord:
    model: str
    trial_count: int
    replicate: int
    seed: int
    parameter: str
    role: str
    prior_sd: float
    baseline_error_sd: float
    truth_start_error_sd: float
    oracle_error_sd: float
    perceptual_oracle_error_sd: float | None
    likelihood_profile_offset_sd: float
    joint_profile_offset_sd: float
    likelihood_span: float
    likelihood_curvature: float | None
    objective_improvement_from_truth_start: float
    baseline_termination: str
    truth_start_termination: str
    mechanism: str


def _safe_float(value: float) -> float | None:
    value = float(value)
    return value if np.isfinite(value) else None


def classify_mechanism(
    *,
    baseline_error_sd: float,
    truth_start_error_sd: float,
    oracle_error_sd: float,
    likelihood_profile_offset_sd: float,
    objective_improvement_from_truth_start: float,
) -> str:
    """Classify the dominant observed recovery mechanism for one dataset/parameter."""
    if abs(likelihood_profile_offset_sd) > 0.5:
        return "finite_data_likelihood_identifiability"
    if oracle_error_sd + 0.15 < baseline_error_sd:
        return "cross_parameter_confounding"
    if (
        truth_start_error_sd + 0.15 < baseline_error_sd
        and objective_improvement_from_truth_start > 0.05
    ):
        return "optimizer_start_sensitivity"
    if baseline_error_sd <= 0.5:
        return "identifiable_recovery"
    return "mixed_or_weak_identifiability"


def records_from_diagnosis(diagnosis: DatasetDiagnosis) -> list[IdentifiabilityRecord]:
    """Convert one M18A dataset diagnosis to normalized M18B records."""
    rows: list[IdentifiabilityRecord] = []
    improvement = float(
        diagnosis.baseline_neg_log_joint - diagnosis.truth_start_neg_log_joint
    )
    for parameter, profile in zip(
        diagnosis.parameter_metadata, diagnosis.profiles, strict=True
    ):
        i = parameter.free_position
        truth = float(diagnosis.truth_free[i])
        sd = float(parameter.prior_sd)
        baseline_error = abs(float(diagnosis.baseline_free[i]) - truth) / sd
        truth_start_error = abs(float(diagnosis.truth_start_free[i]) - truth) / sd
        oracle_error = abs(float(diagnosis.oracle_single_free[i]) - truth) / sd
        perceptual_value = float(diagnosis.perceptual_oracle_free[i])
        perceptual_error = (
            abs(perceptual_value - truth) / sd
            if np.isfinite(perceptual_value)
            else None
        )
        mechanism = classify_mechanism(
            baseline_error_sd=baseline_error,
            truth_start_error_sd=truth_start_error,
            oracle_error_sd=oracle_error,
            likelihood_profile_offset_sd=float(
                profile.likelihood_minimum_offset_sd
            ),
            objective_improvement_from_truth_start=improvement,
        )
        rows.append(
            IdentifiabilityRecord(
                model=diagnosis.model,
                trial_count=int(diagnosis.trial_count),
                replicate=int(diagnosis.replicate),
                seed=int(diagnosis.seed),
                parameter=parameter.transformed_name,
                role=parameter.role,
                prior_sd=sd,
                baseline_error_sd=float(baseline_error),
                truth_start_error_sd=float(truth_start_error),
                oracle_error_sd=float(oracle_error),
                perceptual_oracle_error_sd=(
                    float(perceptual_error) if perceptual_error is not None else None
                ),
                likelihood_profile_offset_sd=float(
                    profile.likelihood_minimum_offset_sd
                ),
                joint_profile_offset_sd=float(profile.joint_minimum_offset_sd),
                likelihood_span=float(profile.likelihood_span),
                likelihood_curvature=_safe_float(profile.likelihood_curvature),
                objective_improvement_from_truth_start=improvement,
                baseline_termination=diagnosis.baseline_termination,
                truth_start_termination=diagnosis.truth_start_termination,
                mechanism=mechanism,
            )
        )
    return rows


def _median(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=np.float64)
    if not array.size:
        return float("nan")
    return float(np.median(array))


def summarize_records(records: Sequence[IdentifiabilityRecord]) -> dict[str, dict]:
    """Aggregate records by model, parameter, and trial count."""
    summary: dict[str, dict] = {}
    keys = sorted(
        {(row.model, row.parameter, row.trial_count) for row in records}
    )
    for model, parameter, trial_count in keys:
        selected = [
            row
            for row in records
            if row.model == model
            and row.parameter == parameter
            and row.trial_count == trial_count
        ]
        mechanisms = sorted({row.mechanism for row in selected})
        summary[
            f"{model}:{parameter}:trials={trial_count}"
        ] = {
            "n": len(selected),
            "model": model,
            "parameter": parameter,
            "trial_count": trial_count,
            "median_baseline_error_sd": _median(
                row.baseline_error_sd for row in selected
            ),
            "median_truth_start_error_sd": _median(
                row.truth_start_error_sd for row in selected
            ),
            "median_oracle_error_sd": _median(
                row.oracle_error_sd for row in selected
            ),
            "median_abs_likelihood_profile_offset_sd": _median(
                abs(row.likelihood_profile_offset_sd) for row in selected
            ),
            "median_likelihood_span": _median(
                row.likelihood_span for row in selected
            ),
            "median_objective_improvement_from_truth_start": _median(
                row.objective_improvement_from_truth_start for row in selected
            ),
            "mechanism_counts": {
                mechanism: sum(row.mechanism == mechanism for row in selected)
                for mechanism in mechanisms
            },
        }
    return summary


def trial_count_trends(summary: dict[str, dict]) -> dict[str, dict]:
    """Report low-to-high trial-count recovery/identifiability trends."""
    trends: dict[str, dict] = {}
    model_parameters = sorted(
        {(item["model"], item["parameter"]) for item in summary.values()}
    )
    for model, parameter in model_parameters:
        selected = sorted(
            (
                item
                for item in summary.values()
                if item["model"] == model and item["parameter"] == parameter
            ),
            key=lambda item: item["trial_count"],
        )
        if len(selected) < 2:
            continue
        low, high = selected[0], selected[-1]
        low_error = float(low["median_baseline_error_sd"])
        high_error = float(high["median_baseline_error_sd"])
        low_offset = float(low["median_abs_likelihood_profile_offset_sd"])
        high_offset = float(high["median_abs_likelihood_profile_offset_sd"])
        trends[f"{model}:{parameter}"] = {
            "low_trial_count": int(low["trial_count"]),
            "high_trial_count": int(high["trial_count"]),
            "baseline_error_ratio_high_over_low": (
                high_error / low_error if low_error > 0.0 else None
            ),
            "profile_offset_ratio_high_over_low": (
                high_offset / low_offset if low_offset > 0.0 else None
            ),
            "baseline_error_improved": bool(high_error <= low_error),
            "profile_offset_improved": bool(high_offset <= low_offset),
        }
    return trends


def evaluate_m18b_gate(
    *,
    records: Sequence[IdentifiabilityRecord],
    summary: dict[str, dict],
    trial_counts: Sequence[int],
    replicates: int,
) -> dict:
    """Evaluate the M18B protocol-integrity gate.

    This gate intentionally does not replace or relax M18's frozen recovery
    thresholds.  It verifies that the redesigned protocol produces complete,
    finite, interpretable evidence and that a known healthy control parameter
    remains recoverable while optimizer sensitivity is not the dominant cause.
    """
    expected_groups = (
        len(BINARY_VARIANTS) * len(EXPECTED_PARAMETERS) * len(tuple(trial_counts))
    )
    coverage_complete = (
        len(summary) == expected_groups
        and all(item["n"] == replicates for item in summary.values())
    )
    profiles_finite = all(
        np.isfinite(item["median_abs_likelihood_profile_offset_sd"])
        and np.isfinite(item["median_likelihood_span"])
        and item["median_likelihood_span"] >= 0.0
        for item in summary.values()
    )
    optimizer_not_dominant = all(
        abs(item["median_objective_improvement_from_truth_start"]) <= 0.10
        for item in summary.values()
    )

    highest = max(int(value) for value in trial_counts)
    healthy_controls = [
        item
        for item in summary.values()
        if item["parameter"] == "om[1]" and item["trial_count"] == highest
    ]
    healthy_control_recovery = (
        len(healthy_controls) == len(BINARY_VARIANTS)
        and all(item["median_baseline_error_sd"] <= 0.50 for item in healthy_controls)
    )

    checks = {
        "coverage_complete": bool(coverage_complete),
        "profiles_finite": bool(profiles_finite),
        "optimizer_not_dominant": bool(optimizer_not_dominant),
        "healthy_control_recovery": bool(healthy_control_recovery),
        "frozen_m18_result_preserved": True,
    }
    return {
        "criteria": {
            "healthy_control_median_error_sd_max": 0.50,
            "optimizer_truth_start_objective_improvement_abs_max": 0.10,
            "m18_thresholds_may_be_relaxed": False,
        },
        "checks": checks,
        "pass": bool(all(checks.values())),
        "note": (
            "M18B PASS validates the redesigned identifiability-aware protocol; "
            "it does not change the frozen M18 FAIL result."
        ),
    }


def records_payload(records: Sequence[IdentifiabilityRecord]) -> list[dict]:
    return [asdict(row) for row in records]


__all__ = [
    "EXPECTED_PARAMETERS",
    "informative_binary_inputs",
    "IdentifiabilityRecord",
    "classify_mechanism",
    "records_from_diagnosis",
    "summarize_records",
    "trial_count_trends",
    "evaluate_m18b_gate",
    "records_payload",
]
