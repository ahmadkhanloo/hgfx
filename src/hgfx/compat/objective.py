"""MATLAB-compatible fixed-parameter objective evaluation.

This module mirrors the objective boundary inside frozen HGF Toolbox 8.2.0
fitModel.m without performing optimization. M8 freezes negative-log-likelihood,
Gaussian-prior, and negative-log-joint semantics before M9 fitting parity.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from hgfx.core.parameters import ModelConfig
from hgfx.core.priors import optimization_indices
from hgfx.core.trials import build_trial_masks
from hgfx.models.hgf_binary import hgf_binary
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

from .configs import hgf_binary_config, unitsq_sgm_config


@dataclass(frozen=True)
class PriorEvaluation:
    """Gaussian prior terms selected by frozen fitModel.m semantics."""

    indices: tuple[int, ...]
    terms: np.ndarray
    total: float


@dataclass(frozen=True)
class ObjectiveResult:
    """Decomposition of the fixed-parameter negative log joint."""

    trial_log_likelihoods: np.ndarray
    irregular_mask: np.ndarray
    regular_mask: np.ndarray
    log_likelihood: float
    neg_log_likelihood: float
    perceptual_prior: PriorEvaluation
    observation_prior: PriorEvaluation
    neg_log_joint: float
    rval: int = 0

    @property
    def regular_trial_log_likelihoods(self) -> np.ndarray:
        return self.trial_log_likelihoods[self.regular_mask]


def gaussian_log_prior(
    transformed_parameters: Sequence[float] | np.ndarray,
    prior_means: Sequence[float] | np.ndarray,
    prior_variances: Sequence[float] | np.ndarray,
) -> PriorEvaluation:
    """Evaluate only non-NaN, non-zero-variance Gaussian prior terms."""

    parameters = np.asarray(transformed_parameters, dtype=np.float64).reshape(-1)
    means = np.asarray(prior_means, dtype=np.float64).reshape(-1)
    variances = np.asarray(prior_variances, dtype=np.float64).reshape(-1)

    if not (parameters.size == means.size == variances.size):
        raise ValueError("parameter, prior-mean, and prior-variance lengths must match")

    indices = optimization_indices(variances)
    if not indices:
        return PriorEvaluation(indices=(), terms=np.empty(0, dtype=np.float64), total=0.0)

    idx = np.asarray(indices, dtype=np.int64)
    selected_variances = variances[idx]
    selected_means = means[idx]
    selected_parameters = parameters[idx]

    with np.errstate(divide="ignore", invalid="ignore"):
        terms = (
            -np.float64(0.5) * np.log(np.float64(2.0) * np.pi * selected_variances)
            - np.float64(0.5)
            * (selected_parameters - selected_means) ** 2
            / selected_variances
        )
    return PriorEvaluation(
        indices=indices,
        terms=np.asarray(terms, dtype=np.float64),
        total=float(np.sum(terms)),
    )


def evaluate_objective(
    *,
    responses,
    inputs,
    perceptual_parameters,
    observation_parameters,
    perceptual_config: ModelConfig,
    observation_config: ModelConfig,
    perceptual_function: Callable[..., tuple[Any, np.ndarray]],
    observation_function: Callable[..., Any],
    irregular_intervals: bool | None = False,
    perceptual_kwargs: Mapping[str, Any] | None = None,
    observation_kwargs: Mapping[str, Any] | None = None,
) -> ObjectiveResult:
    """Evaluate the frozen fixed-vector objective without optimization."""

    masks = build_trial_masks(responses, inputs)
    ignored_indices = tuple(int(i) for i in np.flatnonzero(masks.ignored))
    irregular_indices = tuple(int(i) for i in np.flatnonzero(masks.irregular))

    p_prc = np.asarray(perceptual_parameters, dtype=np.float64).reshape(-1)
    p_obs = np.asarray(observation_parameters, dtype=np.float64).reshape(-1)

    resolved_perceptual_config = perceptual_config.resolve_placeholders(inputs)

    if p_prc.size != len(resolved_perceptual_config.parameters):
        raise ValueError(
            f"Expected {len(resolved_perceptual_config.parameters)} perceptual parameters, "
            f"got {p_prc.size}"
        )
    if p_obs.size != len(observation_config.parameters):
        raise ValueError(
            f"Expected {len(observation_config.parameters)} observation parameters, "
            f"got {p_obs.size}"
        )

    prc_kwargs = dict(perceptual_kwargs or {})
    prc_kwargs.setdefault("transformed", True)
    prc_kwargs.setdefault("irregular_intervals", irregular_intervals)
    prc_kwargs.setdefault("ignored_trials", ignored_indices)

    try:
        _, inf_states = perceptual_function(inputs, p_prc, **prc_kwargs)
    except Exception:
        realmax = float(np.finfo(np.float64).max)
        empty_prior = PriorEvaluation((), np.empty(0, dtype=np.float64), 0.0)
        return ObjectiveResult(
            trial_log_likelihoods=np.empty(0, dtype=np.float64),
            irregular_mask=masks.irregular.copy(),
            regular_mask=(~masks.irregular).copy(),
            log_likelihood=float("nan"),
            neg_log_likelihood=realmax,
            perceptual_prior=empty_prior,
            observation_prior=empty_prior,
            neg_log_joint=realmax,
            rval=-1,
        )

    obs_kwargs = dict(observation_kwargs or {})
    obs_kwargs.setdefault("irregular_trials", irregular_indices)
    observation_output = observation_function(
        responses,
        inf_states,
        p_obs,
        **obs_kwargs,
    )
    if isinstance(observation_output, tuple):
        trial_log_likelihoods = observation_output[0]
    else:
        trial_log_likelihoods = observation_output

    trial_log_likelihoods = np.asarray(
        trial_log_likelihoods,
        dtype=np.float64,
    ).reshape(-1)
    if trial_log_likelihoods.size != masks.irregular.size:
        raise ValueError("observation model returned the wrong number of trial likelihoods")

    regular_mask = ~masks.irregular
    log_likelihood = float(np.sum(trial_log_likelihoods[regular_mask]))
    if np.isnan(log_likelihood):
        neg_log_likelihood = float(np.finfo(np.float64).max)
    else:
        neg_log_likelihood = -log_likelihood

    prc_prior = gaussian_log_prior(
        p_prc,
        resolved_perceptual_config.priormus,
        resolved_perceptual_config.priorsas,
    )
    obs_prior = gaussian_log_prior(
        p_obs,
        observation_config.priormus,
        observation_config.priorsas,
    )

    neg_log_joint = -(log_likelihood + prc_prior.total + obs_prior.total)

    return ObjectiveResult(
        trial_log_likelihoods=trial_log_likelihoods,
        irregular_mask=masks.irregular.copy(),
        regular_mask=regular_mask.copy(),
        log_likelihood=log_likelihood,
        neg_log_likelihood=neg_log_likelihood,
        perceptual_prior=prc_prior,
        observation_prior=obs_prior,
        neg_log_joint=float(neg_log_joint),
        rval=0,
    )


def hgf_binary_unitsq_objective(
    responses,
    inputs,
    perceptual_parameters,
    observation_parameters,
    *,
    irregular_intervals: bool | None = False,
) -> ObjectiveResult:
    """M8 vertical slice: standard binary HGF plus unit-square sigmoid."""

    prc_config = hgf_binary_config()
    obs_config = unitsq_sgm_config()
    return evaluate_objective(
        responses=responses,
        inputs=inputs,
        perceptual_parameters=perceptual_parameters,
        observation_parameters=observation_parameters,
        perceptual_config=prc_config,
        observation_config=obs_config,
        perceptual_function=hgf_binary,
        observation_function=unitsq_sgm,
        irregular_intervals=irregular_intervals,
        observation_kwargs={"predorpost": int(obs_config.options["predorpost"])},
    )
