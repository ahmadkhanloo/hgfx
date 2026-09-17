"""Scientific diagnostics and validation utilities."""

from .horizon import (
    CRITERIA as HORIZON_CRITERIA,
    PROTOCOL as HORIZON_PROTOCOL,
    TRIAL_HORIZONS,
    classify_horizon_evidence,
    parameter_check_flags,
)
from .recovery import (
    BINARY_VARIANTS,
    ModelRecoveryRecord,
    ParameterRecoveryRecord,
    ParameterRecoverySummary,
    RecoveryFit,
    deterministic_binary_inputs,
    fit_binary_variant,
    fit_candidate_set,
    model_recovery_matrix,
    run_model_recovery,
    run_parameter_recovery,
    simulate_binary_variant,
    summarize_parameter_recovery,
)

__all__ = [
    "BINARY_VARIANTS",
    "HORIZON_CRITERIA",
    "HORIZON_PROTOCOL",
    "TRIAL_HORIZONS",
    "RecoveryFit",
    "ParameterRecoveryRecord",
    "ParameterRecoverySummary",
    "ModelRecoveryRecord",
    "classify_horizon_evidence",
    "parameter_check_flags",
    "fit_binary_variant",
    "summarize_parameter_recovery",
    "deterministic_binary_inputs",
    "simulate_binary_variant",
    "run_parameter_recovery",
    "fit_candidate_set",
    "run_model_recovery",
    "model_recovery_matrix",
]
