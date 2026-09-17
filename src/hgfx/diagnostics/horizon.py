"""Frozen M18C.2 trial-horizon identifiability constants and classification."""

from __future__ import annotations

from typing import Mapping

PROTOCOL = "m18c2-trial-horizon-identifiability-1"
TRIAL_HORIZONS = (128, 256, 512, 1024)
TRUTH_SCALES = (0.15, 0.35)
PARAM_REPLICATES = 6
MODEL_REPLICATES = 3
MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
CRITERIA = {
    "convergence_rate_min": 0.80,
    "median_correlation_min": 0.50,
    "median_standardized_rmse_max": 1.00,
    "model_balanced_accuracy_min": 0.50,
}
PARAMETER_CHECK_NAMES = (
    "convergence_rate",
    "median_correlation",
    "median_standardized_rmse",
)


def parameter_check_flags(summary: Mapping[str, object]) -> dict[str, bool]:
    """Convert numeric parameter summaries into the three frozen boolean checks."""
    convergence = float(summary["convergence_rate"])
    median_corr = summary.get("median_correlation")
    median_srmse = float(summary["median_standardized_rmse"])
    return {
        "convergence_rate": convergence >= CRITERIA["convergence_rate_min"],
        "median_correlation": median_corr is not None
        and float(median_corr) >= CRITERIA["median_correlation_min"],
        "median_standardized_rmse": median_srmse <= CRITERIA["median_standardized_rmse_max"],
    }


def classify_horizon_evidence(
    *,
    paired_integrity_pass: bool,
    checks_256: Mapping[str, bool] | None,
    checks_1024: Mapping[str, bool] | None,
) -> str:
    """Preregistered 256→1024 interpretation. Horizons 128/512 are diagnostics only."""
    if not paired_integrity_pass:
        return "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"
    if checks_256 is None or checks_1024 is None:
        return "INSUFFICIENT_REFERENCE_EVIDENCE"
    failing_256 = tuple(name for name, passed in checks_256.items() if not passed)
    if not failing_256:
        return "NO_256_FAILURE_TO_EXPLAIN"
    failing_1024 = tuple(name for name, passed in checks_1024.items() if not passed)
    resolved = tuple(name for name in failing_256 if name not in failing_1024)
    persisted = tuple(name for name in failing_256 if name in failing_1024)
    if resolved and not persisted:
        return "DATA_HORIZON_LIMITATION_SUPPORTED"
    if persisted and not resolved:
        return "PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED"
    return "MIXED_HORIZON_EFFECT_INCONCLUSIVE"
