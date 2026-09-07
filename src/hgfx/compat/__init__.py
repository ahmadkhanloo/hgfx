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
from .simulation import (
    SimulationResult,
    ehgf_binary_config,
    sample_model,
    sim_model,
    simulate_gaussian_obs,
    simulate_softmax_binary,
    simulate_unitsq_sgm,
    softmax_binary_probability,
    uhgf_binary_config,
    unitsq_sgm_probability,
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
    "SimulationResult",
    "ehgf_binary_config",
    "uhgf_binary_config",
    "sim_model",
    "sample_model",
    "unitsq_sgm_probability",
    "simulate_unitsq_sgm",
    "softmax_binary_probability",
    "simulate_softmax_binary",
    "simulate_gaussian_obs",
]
