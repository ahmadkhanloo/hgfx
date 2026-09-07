from __future__ import annotations

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.objective import (
    evaluate_objective,
    gaussian_log_prior,
    hgf_binary_unitsq_objective,
)


def binary_parameters() -> np.ndarray:
    p = hgf_binary_config().priormus.copy()
    p[12] = -2.7
    p[13] = -5.4
    return p


def test_gaussian_prior_excludes_fixed_and_nan_variances() -> None:
    result = gaussian_log_prior(
        [1.0, 2.0, 3.0, 5.0],
        [0.0, 2.0, 0.0, 4.0],
        [1.0, 0.0, np.nan, 4.0],
    )
    assert result.indices == (0, 3)
    expected = np.array(
        [
            -0.5 * np.log(2.0 * np.pi) - 0.5,
            -0.5 * np.log(2.0 * np.pi * 4.0) - 0.5 * (1.0**2) / 4.0,
        ]
    )
    np.testing.assert_allclose(result.terms, expected)
    assert result.total == np.sum(expected)


def test_objective_decomposition_and_irregular_semantics() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, 1.0, np.nan, 0.0, 1.0, 1.0, 0.0])
    responses = np.array([0.0, 1.0, 1.0, np.nan, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0])

    result = hgf_binary_unitsq_objective(
        responses,
        inputs,
        binary_parameters(),
        [np.log(20.0)],
    )

    assert result.rval == 0
    assert tuple(np.flatnonzero(result.irregular_mask)) == (3, 5)
    assert np.isnan(result.trial_log_likelihoods[3])
    assert np.isnan(result.trial_log_likelihoods[5])
    assert np.isfinite(result.regular_trial_log_likelihoods).all()
    assert result.neg_log_likelihood == -result.log_likelihood
    assert result.perceptual_prior.indices == (12, 13)
    assert result.observation_prior.indices == (0,)
    np.testing.assert_allclose(
        result.neg_log_joint,
        -(
            result.log_likelihood
            + result.perceptual_prior.total
            + result.observation_prior.total
        ),
    )


def test_regular_nan_is_not_silently_dropped_from_objective_sum() -> None:
    prc = hgf_binary_config()
    obs = unitsq_sgm_config()

    def perceptual(inputs, p, **kwargs):
        n = np.asarray(inputs).shape[0]
        return {}, np.zeros((n, 1, 1), dtype=np.float64)

    def observation(responses, inf_states, p, **kwargs):
        return np.array([-0.2, np.nan, -0.3], dtype=np.float64)

    result = evaluate_objective(
        responses=np.array([0.0, 1.0, 0.0]),
        inputs=np.array([0.0, 1.0, 0.0]),
        perceptual_parameters=prc.priormus,
        observation_parameters=obs.priormus,
        perceptual_config=prc,
        observation_config=obs,
        perceptual_function=perceptual,
        observation_function=observation,
    )
    assert np.isnan(result.log_likelihood)
    assert result.neg_log_likelihood == np.finfo(np.float64).max
    assert np.isnan(result.neg_log_joint)


def test_perceptual_failure_matches_fitmodel_realmax_sentinel() -> None:
    prc = hgf_binary_config()
    obs = unitsq_sgm_config()

    def fail(*args, **kwargs):
        raise RuntimeError("unstable")

    def never_called(*args, **kwargs):
        raise AssertionError("observation should not run")

    result = evaluate_objective(
        responses=np.array([0.0, 1.0]),
        inputs=np.array([0.0, 1.0]),
        perceptual_parameters=prc.priormus,
        observation_parameters=obs.priormus,
        perceptual_config=prc,
        observation_config=obs,
        perceptual_function=fail,
        observation_function=never_called,
    )
    assert result.rval == -1
    assert result.neg_log_likelihood == np.finfo(np.float64).max
    assert result.neg_log_joint == np.finfo(np.float64).max
