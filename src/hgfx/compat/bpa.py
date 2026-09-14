"""MATLAB-compatible Bayesian parameter averaging.

This module mirrors the frozen HGF Toolbox 8.2.0
``bayesian_parameter_average.m`` utility.  It operates on compatibility fit
results and deliberately preserves the MATLAB transformed-parameter pooling
semantics rather than inventing a Python-specific group estimator.
"""

from __future__ import annotations

import warnings
from collections.abc import Sequence

import numpy as np

from hgfx.math.covariance import cov_to_corr
from hgfx.math.psd import nearest_psd

from .result import CompatibilityResult, MatlabStruct, parameter_struct
from .workflows import forward_for, resolve_config


def _numeric(value) -> np.ndarray:
    return np.asarray(value, dtype=np.float64)


def _equal_with_nan(left, right) -> bool:
    # MATLAB parameter vectors may arrive through JSON/compatibility surfaces as
    # either scalars or singleton vectors.  Priors are vector-valued semantically,
    # so compare their flattened parameter ordering rather than container shape.
    return bool(
        np.array_equal(
            _numeric(left).reshape(-1),
            _numeric(right).reshape(-1),
            equal_nan=True,
        )
    )


def _pool_gaussian_posteriors(
    priormus: np.ndarray,
    priorsas: np.ndarray,
    transformed_vectors: Sequence[np.ndarray],
    hessians: Sequence[np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pool Gaussian posteriors using the frozen MATLAB BPA algebra."""

    means = _numeric(priormus).reshape(-1)
    variances = _numeric(priorsas).reshape(-1)
    if means.shape != variances.shape:
        raise ValueError("Prior means and variances must have matching shapes")

    opt_mask = variances.copy()
    opt_mask[np.isnan(opt_mask)] = 0.0
    opt_idx = np.flatnonzero(opt_mask)
    if opt_idx.size == 0:
        raise ValueError("Bayesian parameter averaging requires at least one free parameter")

    n = len(transformed_vectors)
    if n == 0 or len(hessians) != n:
        raise ValueError("At least one estimate with a matching Hessian is required")

    h0 = np.diag(np.float64(1.0) / variances[opt_idx])
    h = (np.float64(1.0) - np.float64(n)) * h0
    for matrix in hessians:
        item = _numeric(matrix)
        if item.shape != (opt_idx.size, opt_idx.size):
            raise ValueError("Estimate Hessian shape does not match free-parameter count")
        h = h + item

    sigma = nearest_psd(np.linalg.inv(h))
    corr = cov_to_corr(sigma)

    mu0 = means[opt_idx]
    mu = (np.float64(1.0) - np.float64(n)) * (h0 @ mu0)
    for vector, matrix in zip(transformed_vectors, hessians, strict=True):
        transformed = _numeric(vector).reshape(-1)
        if transformed.shape != means.shape:
            raise ValueError("Estimate transformed parameter vector has the wrong size")
        mu = mu + _numeric(matrix) @ transformed[opt_idx]
    mu = sigma @ mu

    pooled = means.copy()
    pooled[opt_idx] = mu
    return h, sigma, corr, pooled, opt_idx


def bayesian_parameter_average(*estimates: CompatibilityResult) -> MatlabStruct:
    """Average MATLAB-style fit estimates using posterior precision weighting.

    All estimates must use the same perceptual/observation models and priors.
    Input differences are reported as a warning, matching the reference utility;
    model/prior differences are hard errors.
    """

    if not estimates:
        raise ValueError("bayesian_parameter_average requires at least one estimate")

    first = estimates[0]
    required = ("c_prc", "c_obs", "p_prc", "p_obs", "optim")
    if any(getattr(first, name, None) is None for name in required):
        raise ValueError("Inputs must be fit-like CompatibilityResult objects")

    prc_model = str(first.c_prc.model)
    obs_model = str(first.c_obs.model)
    prc_priormus = _numeric(first.c_prc.priormus).reshape(-1)
    prc_priorsas = _numeric(first.c_prc.priorsas).reshape(-1)
    obs_priormus = _numeric(first.c_obs.priormus).reshape(-1)
    obs_priorsas = _numeric(first.c_obs.priorsas).reshape(-1)
    inputs = _numeric(first.u)

    transformed_vectors: list[np.ndarray] = []
    hessians: list[np.ndarray] = []

    for index, estimate in enumerate(estimates, start=1):
        if any(getattr(estimate, name, None) is None for name in required):
            raise ValueError("Inputs must be fit-like CompatibilityResult objects")
        if str(estimate.c_prc.model) != prc_model:
            raise ValueError("Perceptual models do not match")
        if str(estimate.c_obs.model) != obs_model:
            raise ValueError("Observation models do not match")
        if not _equal_with_nan(prc_priormus, estimate.c_prc.priormus) or not _equal_with_nan(
            prc_priorsas, estimate.c_prc.priorsas
        ):
            raise ValueError("Perceptual priors do not match")
        if not _equal_with_nan(obs_priormus, estimate.c_obs.priormus) or not _equal_with_nan(
            obs_priorsas, estimate.c_obs.priorsas
        ):
            raise ValueError("Observation priors do not match")
        if not _equal_with_nan(inputs.reshape(-1), _numeric(estimate.u).reshape(-1)):
            warnings.warn(
                f"Inputs for estimate {index} do not match those for the first estimate",
                RuntimeWarning,
                stacklevel=2,
            )

        transformed_vectors.append(
            np.r_[
                _numeric(estimate.p_prc.ptrans).reshape(-1),
                _numeric(estimate.p_obs.ptrans).reshape(-1),
            ]
        )
        hessians.append(_numeric(estimate.optim.H))

    priormus = np.r_[prc_priormus, obs_priormus]
    priorsas = np.r_[prc_priorsas, obs_priorsas]
    h, sigma, corr, ptrans, _ = _pool_gaussian_posteriors(
        priormus, priorsas, transformed_vectors, hessians
    )

    n_prc = prc_priormus.size
    ptrans_prc = ptrans[:n_prc]
    ptrans_obs = ptrans[n_prc:]

    prc_config = resolve_config(prc_model).resolve_placeholders(inputs)
    obs_config = resolve_config(obs_model).resolve_placeholders(inputs)
    native_prc = prc_config.transformed_to_native(ptrans_prc)
    native_obs = obs_config.transformed_to_native(ptrans_obs)

    forward = forward_for(prc_config)
    trajectory, _ = forward(
        inputs,
        native_prc,
        transformed=False,
        irregular_intervals=bool(prc_config.options.get("irregular_intervals", False)),
        ignored_trials=(),
    )

    return MatlabStruct(
        {
            "u": inputs.copy(),
            "ign": np.asarray([], dtype=np.int64),
            "c_prc": first.c_prc,
            "c_obs": first.c_obs,
            "optim": MatlabStruct({"H": h, "Sigma": sigma, "Corr": corr}),
            "p_prc": parameter_struct(
                prc_config,
                native_prc,
                transformed_parameters=ptrans_prc,
            ),
            "p_obs": parameter_struct(
                obs_config,
                native_obs,
                transformed_parameters=ptrans_obs,
            ),
            "traj": MatlabStruct(trajectory),
        }
    )


__all__ = ["bayesian_parameter_average"]
