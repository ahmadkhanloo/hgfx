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


def test_objective_sum_matches_frozen_matlab_d02_reduction_exactly() -> None:
    """Freeze the D02 MATLAB reduction before changing objective summation.

    Source: M18 official workflow run 34778948350, artifact 10324920994,
    parameter 2 / first Ridders-minus sample. The payload below is the exact
    little-endian binary64 representation of MATLAB's 320 regular trial
    log-likelihoods. MATLAB's exported total is intentionally asserted with no
    tolerance because a one-ULP reduction difference is amplified by Ridders.
    """
    import base64

    encoded = (
        "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"
        "AAAAAAAAAADQPA=="
    )
    trial_log_likelihoods = np.frombuffer(
        base64.b64decode(encoded), dtype="<f8"
    ).astype(np.float64, copy=True)
    assert trial_log_likelihoods.size == 320

    prc = hgf_binary_config()
    obs = unitsq_sgm_config()

    def perceptual(inputs, p, **kwargs):
        n = np.asarray(inputs).shape[0]
        return {}, np.zeros((n, 1, 1), dtype=np.float64)

    def observation(responses, inf_states, p, **kwargs):
        return trial_log_likelihoods.copy()

    result = evaluate_objective(
        responses=np.zeros(320, dtype=np.float64),
        inputs=np.zeros(320, dtype=np.float64),
        perceptual_parameters=prc.priormus,
        observation_parameters=obs.priormus,
        perceptual_config=prc,
        observation_config=obs,
        perceptual_function=perceptual,
        observation_function=observation,
    )
    expected_matlab_log_likelihood = np.float64(-586.8959133197983)
    assert result.log_likelihood == expected_matlab_log_likelihood
