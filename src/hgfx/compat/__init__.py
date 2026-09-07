"""MATLAB compatibility schemas, objective, fitting, and fit statistics."""

from .configs import hgf_binary_config, hgf_config, unitsq_sgm_config
from .fit_statistics import (
    FitStatistics,
    LMEDecomposition,
    finalize_laplace_statistics,
    fit_statistics,
)
from .fitting import (
    CompatibilityFitResult,
    FitProblem,
    fit_hgf_binary_unitsq_compat,
    fit_hgf_binary_unitsq_multistart_compat,
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
    "fit_hgf_binary_unitsq_multistart_compat",
    "FitStatistics",
    "LMEDecomposition",
    "finalize_laplace_statistics",
    "fit_statistics",
]
