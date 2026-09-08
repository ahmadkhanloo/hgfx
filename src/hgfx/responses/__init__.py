"""MATLAB-compatible observation and auxiliary response models."""

from .base import total_log_likelihood
from .beta import beta_obs
from .cdf_gaussian import cdfgaussian_obs
from .gaussian import gaussian_obs, gaussian_obs_offset
from .logrt import logrt_linear_binary, logrt_linear_binary_minimal
from .softmax import softmax, softmax_2beta, softmax_binary, softmax_mu3
from .unitsq_sigmoid import unitsq_sgm, unitsq_sgm_mu3
from .auxiliary import (
    bayes_optimal,
    bayes_optimal_binary,
    bayes_optimal_categorical,
    bayes_optimal_whatworld,
    bayes_optimal_whichworld,
    squared_pe,
    rs_belief,
    rs_precision,
    rs_precision_whatworld,
    rs_surprise,
)
from .specialized import (
    condhalluc_obs,
    condhalluc_obs2,
    condhalluc_obs3,
    logrt_linear_whatworld,
    softmax_wld,
    softmax_mu3_wld,
    simulate_condhalluc_obs,
    simulate_condhalluc_obs2,
    simulate_condhalluc_obs3,
    simulate_softmax_wld,
    simulate_softmax_mu3_wld,
)

__all__ = [
    "beta_obs", "cdfgaussian_obs", "gaussian_obs", "gaussian_obs_offset",
    "logrt_linear_binary", "logrt_linear_binary_minimal",
    "softmax", "softmax_2beta", "softmax_binary", "softmax_mu3",
    "total_log_likelihood", "unitsq_sgm", "unitsq_sgm_mu3",
    "bayes_optimal", "bayes_optimal_binary", "bayes_optimal_categorical",
    "bayes_optimal_whatworld", "bayes_optimal_whichworld", "squared_pe",
    "rs_belief", "rs_precision", "rs_precision_whatworld", "rs_surprise",
    "condhalluc_obs", "condhalluc_obs2", "condhalluc_obs3",
    "logrt_linear_whatworld", "softmax_wld", "softmax_mu3_wld",
    "simulate_condhalluc_obs", "simulate_condhalluc_obs2",
    "simulate_condhalluc_obs3", "simulate_softmax_wld",
    "simulate_softmax_mu3_wld",
]
