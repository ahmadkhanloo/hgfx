from __future__ import annotations

import numpy as np

from hgfx.compat import (
    hgf_binary_config,
    sample_model,
    sim_model,
    simulate_gaussian_obs,
    simulate_softmax_binary,
    simulate_unitsq_sgm,
    softmax_binary_probability,
    unitsq_sgm_config,
    unitsq_sgm_probability,
)


def native_hgf_parameters() -> np.ndarray:
    config = hgf_binary_config()
    ptrans = config.priormus.copy()
    ptrans[12] = -2.7
    ptrans[13] = -5.4
    return config.transformed_to_native(ptrans)


def test_sim_model_preserves_frozen_ignored_trial_trajectory_quirk() -> None:
    inputs = np.array([0.0, 1.0, 1.0, np.nan, 0.0, 1.0, 0.0, 1.0])
    uniforms = np.linspace(0.05, 0.95, inputs.size, endpoint=False)

    result = sim_model(
        inputs,
        "hgf_binary",
        native_hgf_parameters(),
        "unitsq_sgm",
        np.array([12.0]),
        response_uniforms=uniforms,
    )

    assert result.ignored_trials == (3,)
    assert result.inf_states.shape[0] == inputs.size
    assert result.responses is not None
    assert result.responses.shape == (inputs.size,)
    assert result.response_probabilities is not None
    assert result.response_probabilities.shape == (inputs.size,)

    # Frozen simModel.m deletes ignored rows only from these two returned
    # trajectory fields during its binary-HGF NaN validation.
    assert result.trajectory["muhat"].shape[0] == inputs.size - 1
    assert result.trajectory["sahat"].shape[0] == inputs.size - 1
    assert result.trajectory["mu"].shape[0] == inputs.size
    assert result.trajectory["sa"].shape[0] == inputs.size


def test_unitsq_probability_and_seed_are_reproducible() -> None:
    states = np.zeros((64, 3, 4), dtype=np.float64)
    states[:, 0, 0] = np.linspace(0.1, 0.9, 64)
    states[:, 0, 2] = np.linspace(0.15, 0.85, 64)

    probability = unitsq_sgm_probability(states, [4.0])
    y1, p1 = simulate_unitsq_sgm(states, [4.0], seed=1234)
    y2, p2 = simulate_unitsq_sgm(states, [4.0], seed=1234)

    np.testing.assert_allclose(p1, probability)
    np.testing.assert_allclose(p2, probability)
    np.testing.assert_array_equal(y1, y2)


def test_softmax_binary_probability_and_seed_are_reproducible() -> None:
    states = np.zeros((64, 3, 4), dtype=np.float64)
    states[:, 0, 0] = np.linspace(0.1, 0.9, 64)
    states[:, 0, 2] = np.linspace(0.15, 0.85, 64)

    probability = softmax_binary_probability(states, [2.5])
    y1, p1 = simulate_softmax_binary(states, [2.5], seed=4321)
    y2, p2 = simulate_softmax_binary(states, [2.5], seed=4321)

    np.testing.assert_allclose(p1, probability)
    np.testing.assert_allclose(p2, probability)
    np.testing.assert_array_equal(y1, y2)


def test_stochastic_observation_distributions_match_their_generators() -> None:
    n = 100_000
    states = np.zeros((n, 3, 4), dtype=np.float64)
    states[:, 0, 0] = 0.3

    y_unitsq, probability = simulate_unitsq_sgm(states, [2.0], seed=11)
    assert abs(float(np.mean(y_unitsq)) - float(probability[0])) < 0.01

    y_softmax, probability_softmax = simulate_softmax_binary(states, [1.7], seed=12)
    assert abs(float(np.mean(y_softmax)) - float(probability_softmax[0])) < 0.01

    variance = 0.4
    y_gaussian = simulate_gaussian_obs(states, [variance], seed=13)
    assert abs(float(np.mean(y_gaussian)) - 0.3) < 0.01
    assert abs(float(np.var(y_gaussian)) - variance) < 0.015


def test_sample_model_uses_supplied_prior_and_response_random_drivers() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    prc = hgf_binary_config()
    obs = unitsq_sgm_config()

    z_prc = np.linspace(-0.5, 0.5, len(prc.parameters))
    z_obs = np.array([0.25])
    uniforms = np.linspace(0.05, 0.95, inputs.size, endpoint=False)

    result = sample_model(
        inputs,
        prc,
        obs,
        perceptual_standard_normals=z_prc,
        observation_standard_normals=z_obs,
        response_uniforms=uniforms,
    )

    expected_ptrans_prc = prc.priormus + z_prc * np.sqrt(prc.priorsas)
    expected_ptrans_obs = obs.priormus + z_obs * np.sqrt(obs.priorsas)

    assert result.perceptual_transformed_parameters is not None
    assert result.observation_transformed_parameters is not None
    np.testing.assert_allclose(
        result.perceptual_transformed_parameters,
        expected_ptrans_prc,
        equal_nan=True,
    )
    np.testing.assert_allclose(
        result.observation_transformed_parameters,
        expected_ptrans_obs,
        equal_nan=True,
    )
    np.testing.assert_allclose(
        result.perceptual_parameters,
        prc.transformed_to_native(expected_ptrans_prc),
        equal_nan=True,
    )
    np.testing.assert_allclose(
        result.observation_parameters,
        obs.transformed_to_native(expected_ptrans_obs),
        equal_nan=True,
    )

    # sampleModel does not perform simModel's destructive ignored-row trimming.
    assert result.trajectory["muhat"].shape[0] == inputs.size
    assert result.trajectory["sahat"].shape[0] == inputs.size
