"""Identifiability-aware parameter recovery validation for M18B.

M18B does not redefine the frozen M18 pass criteria.  It separates estimator
recoverability from finite-data identifiability, parameter confounding, and
optimizer sensitivity using the evidence-producing primitives introduced in
M18A.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from collections import Counter
import hashlib
import json
from pathlib import Path
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
    """Describe observed recovery patterns, without claiming identifiability.

    A small estimation error (even with a profile minimum near truth) does not
    establish likelihood concentration or joint parameter identifiability.
    """
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
        return "low_error_recovery"
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


# Original CI result downloaded byte-for-byte; no regenerated summary is used.
FROZEN_M18_SOURCE_SHA256 = {
    "scripts/run_m18_scientific_validation.py": "98cc45159ba041f7a0e5addfee4dfa1c2420bcbfef9fa9252ab3550741ae5c2c",
    "src/hgfx/diagnostics/recovery.py": "a8b24e8fdf0ed1ba6a2067dcd8582ed3a190c1f3516c03152f30f1fa516f2eb1",
}
FROZEN_M18_RESULT_SHA256 = "435b3b7775fe6d42a10a7ee677897a5cb056e30b875d9b59d8d04b813732c5b7"


def verify_frozen_m18(path: Path | None = None) -> bool:
    root = Path(__file__).resolve().parents[3]
    path = path if path is not None else root / "reference/validation/m18_scientific_validation.json"
    try:
        data = Path(path).read_bytes()
        if hashlib.sha256(data).hexdigest() != FROZEN_M18_RESULT_SHA256:
            return False
        if any(hashlib.sha256((root / name).read_bytes()).hexdigest() != digest
               for name, digest in FROZEN_M18_SOURCE_SHA256.items()):
            return False
        payload = json.loads(data)
        return payload["milestone"] == "M18" and payload["preset"] == "gate" and payload["gate"]["pass"] is False
    except (OSError, ValueError, KeyError, TypeError):
        return False


def evaluate_m18b_gate(
    *,
    records: Sequence[IdentifiabilityRecord],
    summary: dict[str, dict] | None = None,
    trial_counts: Sequence[int],
    replicates: int,
    frozen_m18_path: Path | None = None,
) -> dict:
    """Evaluate the M18B protocol-integrity gate.

    This gate intentionally does not replace or relax M18's frozen recovery
    thresholds.  It verifies that the redesigned protocol produces complete,
    finite, interpretable evidence and that a known healthy control parameter
    remains recoverable while optimizer sensitivity is not the dominant cause.
    """
    trial_counts = tuple(trial_counts)
    protocol_valid = (
        type(replicates) is int and replicates > 0
        and bool(trial_counts)
        and all(type(t) is int and t >= 8 for t in trial_counts)
        and len(set(trial_counts)) == len(trial_counts)
    )
    expected = (
        {(m, p, t, r) for m in BINARY_VARIANTS for p in EXPECTED_PARAMETERS
         for t in trial_counts for r in range(replicates)}
        if protocol_valid else set()
    )
    keys = [(r.model, r.parameter, r.trial_count, r.replicate) for r in records]
    coverage_complete = bool(expected) and Counter(keys) == Counter(expected)
    numeric_fields = (
        "prior_sd", "baseline_error_sd", "truth_start_error_sd", "oracle_error_sd",
        "likelihood_profile_offset_sd", "joint_profile_offset_sd", "likelihood_span",
        "objective_improvement_from_truth_start",
    )
    nonnegative_fields = (
        "baseline_error_sd", "truth_start_error_sd", "oracle_error_sd", "likelihood_span",
    )
    terminations = {"tol_arg", "tol_grad", "max_iter", "max_resets"}

    def finite(value):
        return (isinstance(value, (int, float, np.integer, np.floating))
                and not isinstance(value, (bool, np.bool_)) and bool(np.isfinite(value)))

    def valid(row):
        if not all(finite(getattr(row, f)) for f in numeric_fields):
            return False
        if row.prior_sd <= 0 or any(getattr(row, f) < 0 for f in nonnegative_fields):
            return False
        for field in ("perceptual_oracle_error_sd", "likelihood_curvature"):
            value = getattr(row, field)
            if value is not None and not finite(value):
                return False
        if row.perceptual_oracle_error_sd is not None and row.perceptual_oracle_error_sd < 0:
            return False
        if any(type(getattr(row, f)) is not int for f in ("trial_count", "replicate", "seed")):
            return False
        return (
            row.seed >= 0
            and row.role == ("observation" if row.parameter == "logze" else "perceptual")
            and row.baseline_termination in terminations
            and row.truth_start_termination in terminations
            and row.mechanism == classify_mechanism(
                baseline_error_sd=row.baseline_error_sd,
                truth_start_error_sd=row.truth_start_error_sd,
                oracle_error_sd=row.oracle_error_sd,
                likelihood_profile_offset_sd=row.likelihood_profile_offset_sd,
                objective_improvement_from_truth_start=row.objective_improvement_from_truth_start,
            )
        )

    records_valid = bool(records) and all(valid(row) for row in records)
    dataset_seeds = {}
    for row in records:
        dataset_seeds.setdefault((row.model, row.trial_count, row.replicate), set()).add(row.seed)
    seeds_consistent = bool(dataset_seeds) and all(len(v) == 1 for v in dataset_seeds.values())
    for model in BINARY_VARIANTS:
        for trial_count in trial_counts:
            cell_seeds = [next(iter(v)) for (m, t, _), v in dataset_seeds.items()
                          if m == model and t == trial_count and len(v) == 1]
            seeds_consistent = seeds_consistent and len(cell_seeds) == len(set(cell_seeds))

    # All numerical decisions use raw evidence. A supplied summary is only a
    # redundant integrity check, never an alternative source of observations.
    computed = summarize_records(records) if records_valid else {}
    summary_consistent = summary is None or summary == computed
    summary = computed
    profiles_finite = bool(summary) and all(
        np.isfinite(item["median_abs_likelihood_profile_offset_sd"])
        and np.isfinite(item["median_likelihood_span"])
        and item["median_likelihood_span"] >= 0.0
        for item in summary.values()
    )
    optimizer_not_dominant = bool(summary) and all(
        abs(item["median_objective_improvement_from_truth_start"]) <= 0.10
        for item in summary.values()
    )

    highest = max(trial_counts) if protocol_valid else None
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
        "protocol_valid": bool(protocol_valid),
        "coverage_complete": bool(coverage_complete),
        "records_valid": bool(records_valid),
        "dataset_seeds_consistent": bool(seeds_consistent),
        "summary_consistent": bool(summary_consistent),
        "profiles_finite": bool(profiles_finite),
        "optimizer_not_dominant": bool(optimizer_not_dominant),
        "healthy_control_recovery": bool(healthy_control_recovery),
        "frozen_m18_result_preserved": verify_frozen_m18(frozen_m18_path),
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
