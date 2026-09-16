"""Frozen post-v1 M18C.2 trial-horizon interpretation rules."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PROTOCOL = "m18c2-trial-horizon-identifiability-1"
TRIAL_HORIZONS = (128, 256, 512, 1024)
TRUTH_SCALES = (0.15, 0.35)
PARAM_REPLICATES = 6
MODEL_REPLICATES = 3
CRITERIA = {
    "convergence_rate_min": 0.80,
    "median_correlation_min": 0.50,
    "median_standardized_rmse_max": 1.00,
    "model_balanced_accuracy_min": 0.50,
}

_PARAMETER_CHECK_KEYS = (
    "convergence_rate",
    "median_correlation",
    "median_standardized_rmse",
)


def parameter_check_flags(summary: Mapping[str, Any]) -> dict[str, bool]:
    """Evaluate one parameter-recovery summary against frozen M18 criteria."""
    median_correlation = summary.get("median_correlation")
    return {
        "convergence_rate": float(summary["convergence_rate"])
        >= CRITERIA["convergence_rate_min"],
        "median_correlation": median_correlation is not None
        and float(median_correlation) >= CRITERIA["median_correlation_min"],
        "median_standardized_rmse": float(summary["median_standardized_rmse"])
        <= CRITERIA["median_standardized_rmse_max"],
    }


def _complete_parameter_checks(checks_by_model: Mapping[str, Any]) -> bool:
    if not checks_by_model:
        return False
    for horizons in checks_by_model.values():
        if not isinstance(horizons, Mapping):
            return False
        for horizon in (256, 1024):
            checks = horizons.get(horizon)
            if not isinstance(checks, Mapping):
                return False
            if any(key not in checks for key in _PARAMETER_CHECK_KEYS):
                return False
    return True


def classify_horizon_evidence(
    *,
    matlab_checks_by_model: Mapping[str, Mapping[int, Mapping[str, bool]]],
    hgfx_checks_by_model: Mapping[str, Mapping[int, Mapping[str, bool]]],
    model_winner_match_by_horizon: Mapping[int, bool],
    complete: bool,
) -> dict[str, Any]:
    """Apply the preregistered paired-integrity and 256→1024 interpretation."""
    if not complete:
        return {
            "overall": "INSUFFICIENT_REFERENCE_EVIDENCE",
            "by_model": {},
            "scientific_interpretation_allowed": False,
        }

    if set(matlab_checks_by_model) != set(hgfx_checks_by_model):
        return {
            "overall": "INSUFFICIENT_REFERENCE_EVIDENCE",
            "by_model": {},
            "scientific_interpretation_allowed": False,
        }
    if not _complete_parameter_checks(matlab_checks_by_model) or not _complete_parameter_checks(
        hgfx_checks_by_model
    ):
        return {
            "overall": "INSUFFICIENT_REFERENCE_EVIDENCE",
            "by_model": {},
            "scientific_interpretation_allowed": False,
        }

    for model in matlab_checks_by_model:
        for horizon in (256, 1024):
            matlab_checks = matlab_checks_by_model[model][horizon]
            hgfx_checks = hgfx_checks_by_model[model][horizon]
            if any(
                bool(matlab_checks[key]) != bool(hgfx_checks[key])
                for key in _PARAMETER_CHECK_KEYS
            ):
                return {
                    "overall": "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH",
                    "by_model": {},
                    "scientific_interpretation_allowed": False,
                }

    if 256 not in model_winner_match_by_horizon or 1024 not in model_winner_match_by_horizon:
        return {
            "overall": "INSUFFICIENT_REFERENCE_EVIDENCE",
            "by_model": {},
            "scientific_interpretation_allowed": False,
        }
    if any(not bool(match) for match in model_winner_match_by_horizon.values()):
        return {
            "overall": "MODEL_SELECTION_MISMATCH",
            "by_model": {},
            "scientific_interpretation_allowed": False,
        }

    by_model: dict[str, str] = {}
    for model in matlab_checks_by_model:
        checks_256 = matlab_checks_by_model[model][256]
        checks_1024 = matlab_checks_by_model[model][1024]
        failing_at_256 = [key for key in _PARAMETER_CHECK_KEYS if not bool(checks_256[key])]

        if not failing_at_256:
            classification = "NO_256_FAILURE_TO_EXPLAIN"
        elif any(not bool(checks_1024[key]) for key in failing_at_256):
            classification = "PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED"
        elif any(
            bool(checks_256[key]) and not bool(checks_1024[key])
            for key in _PARAMETER_CHECK_KEYS
        ):
            classification = "MIXED_HORIZON_EFFECT_INCONCLUSIVE"
        else:
            classification = "DATA_HORIZON_LIMITATION_SUPPORTED"
        by_model[model] = classification

    values = set(by_model.values())
    if "PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED" in values:
        overall = "PERSISTENT_IDENTIFIABILITY_LIMITATION_SUPPORTED"
    elif "DATA_HORIZON_LIMITATION_SUPPORTED" in values:
        overall = "DATA_HORIZON_LIMITATION_SUPPORTED"
    else:
        overall = "MIXED_OR_INCONCLUSIVE"

    return {
        "overall": overall,
        "by_model": by_model,
        "scientific_interpretation_allowed": True,
    }


__all__ = [
    "PROTOCOL",
    "TRIAL_HORIZONS",
    "TRUTH_SCALES",
    "PARAM_REPLICATES",
    "MODEL_REPLICATES",
    "CRITERIA",
    "parameter_check_flags",
    "classify_horizon_evidence",
]
