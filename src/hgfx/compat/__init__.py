"""MATLAB compatibility schemas and frozen config/objective factories."""

from .configs import hgf_binary_config, hgf_config, unitsq_sgm_config
from .objective import (
    ObjectiveResult,
    PriorEvaluation,
    evaluate_objective,
    gaussian_log_prior,
    hgf_binary_unitsq_objective,
)

__all__ = [
    "hgf_binary_config",
    "hgf_config",
    "unitsq_sgm_config",
    "ObjectiveResult",
    "PriorEvaluation",
    "evaluate_objective",
    "gaussian_log_prior",
    "hgf_binary_unitsq_objective",
]
