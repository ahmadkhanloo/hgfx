"""MATLAB compatibility schemas, objective, and fitting factories."""

from .configs import hgf_binary_config, hgf_config, unitsq_sgm_config
from .fitting import (
    CompatibilityFitResult,
    FitProblem,
    fit_hgf_binary_unitsq_compat,
    hgf_binary_unitsq_fit_problem,
)
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
    "FitProblem",
    "CompatibilityFitResult",
    "hgf_binary_unitsq_fit_problem",
    "fit_hgf_binary_unitsq_compat",
]
