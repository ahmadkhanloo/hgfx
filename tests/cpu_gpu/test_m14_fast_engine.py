from __future__ import annotations

import os

import jax
import numpy as np
import pytest

from hgfx.compat.objective import hgf_binary_unitsq_objective
from hgfx.gpu import (
    GLOBAL_COMPILE_CACHE,
    fast_binary_hgf,
    fast_binary_hgf_vmap,
    fast_binary_unitsq_objective,
    fast_binary_unitsq_objective_vmap,
    has_gpu,
    select_device,
    trial_length_bucket,
)
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.models.hgf_binary import hgf_binary
from hgfx.models.uhgf_binary import uhgf_binary


jax.config.update("jax_enable_x64", True)

RTOL = 3e-10
ATOL = 3e-11


def binary_parameters(update_type: str = "hgf") -> np.ndarray:
    omega3 = -6.0 if update_type == "hgf" else 2.0
    return np.array(
        [
            np.nan, 0.0, 1.0,
            np.nan, np.log(0.1), 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, -3.0, omega3,
        ],
        dtype=np.float64,
    )


def fixture_inputs() -> np.ndarray:
    return np.array(
        [0.0, 1.0, 1.0, 0.0, np.nan, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        dtype=np.float64,
    )


@pytest.mark.parametrize(
    ("update_type", "compat"),
    [
        ("hgf", hgf_binary),
        ("ehgf", ehgf_binary),
        ("uhgf", uhgf_binary),
    ],
)
def test_jax_scan_forward_matches_compatibility(update_type, compat) -> None:
    inputs = fixture_inputs()
    parameters = binary_parameters(update_type)

    expected_traj, expected_states = compat(
        inputs,
        parameters,
        transformed=True,
    )
    result = fast_binary_hgf(
        inputs,
        parameters,
        update_type=update_type,
        transformed=True,
    )

    assert bool(result.valid)
    assert result.n_trials == inputs.size
    assert result.bucket == 16
    assert result.inf_states.dtype == np.dtype(np.float64)
    np.testing.assert_allclose(
        np.asarray(result.inf_states),
        expected_states,
        rtol=RTOL,
        atol=ATOL,
        equal_nan=True,
    )
    for key, expected in expected_traj.items():
        np.testing.assert_allclose(
            np.asarray(result.trajectory[key]),
            expected,
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
            err_msg=key,
        )


def test_irregular_interval_forward_matches_compatibility() -> None:
    values = np.array([0.0, 1.0, 1.0, 0.0, np.nan, 1.0, 0.0, 1.0])
    intervals = np.array([0.6, 1.1, 0.8, 1.4, 0.7, 1.2, 0.9, 1.3])
    inputs = np.column_stack((values, intervals))
    parameters = binary_parameters("hgf")

    expected_traj, expected_states = hgf_binary(
        inputs,
        parameters,
        transformed=True,
        irregular_intervals=True,
    )
    result = fast_binary_hgf(
        inputs,
        parameters,
        transformed=True,
        irregular_intervals=True,
    )

    np.testing.assert_allclose(
        np.asarray(result.inf_states),
        expected_states,
        rtol=RTOL,
        atol=ATOL,
        equal_nan=True,
    )
    for key, expected in expected_traj.items():
        np.testing.assert_allclose(
            np.asarray(result.trajectory[key]),
            expected,
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
        )


def test_fast_objective_matches_m8_compatibility() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, 1.0, np.nan, 0.0, 1.0, 1.0, 0.0])
    responses = np.array([0.0, 1.0, 1.0, np.nan, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
    p_prc = binary_parameters("hgf")
    p_prc[12] = -2.7
    p_prc[13] = -5.4
    p_obs = np.array([np.log(20.0)], dtype=np.float64)

    expected = hgf_binary_unitsq_objective(
        responses,
        inputs,
        p_prc,
        p_obs,
    )
    result = fast_binary_unitsq_objective(
        responses,
        inputs,
        p_prc,
        p_obs,
    )

    assert int(result.rval) == expected.rval
    np.testing.assert_allclose(
        np.asarray(result.trial_log_likelihoods),
        expected.trial_log_likelihoods,
        rtol=RTOL,
        atol=ATOL,
        equal_nan=True,
    )
    assert float(result.log_likelihood) == pytest.approx(
        expected.log_likelihood, rel=RTOL, abs=ATOL
    )
    assert float(result.neg_log_likelihood) == pytest.approx(
        expected.neg_log_likelihood, rel=RTOL, abs=ATOL
    )
    assert float(result.perceptual_prior) == pytest.approx(
        expected.perceptual_prior.total, rel=RTOL, abs=ATOL
    )
    assert float(result.observation_prior) == pytest.approx(
        expected.observation_prior.total, rel=RTOL, abs=ATOL
    )
    assert float(result.neg_log_joint) == pytest.approx(
        expected.neg_log_joint, rel=RTOL, abs=ATOL
    )


def test_vmap_matches_repeated_single_forward() -> None:
    inputs = np.stack(
        (
            np.array([0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0]),
            np.array([1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0]),
        )
    )
    parameters = np.stack((binary_parameters("hgf"), binary_parameters("hgf")))

    batch_traj, batch_states, valid = fast_binary_hgf_vmap(inputs, parameters)

    assert np.asarray(valid).all()
    for index in range(inputs.shape[0]):
        single = fast_binary_hgf(inputs[index], parameters[index])
        np.testing.assert_allclose(
            np.asarray(batch_states[index]),
            np.asarray(single.inf_states),
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
        )
        for key in single.trajectory:
            np.testing.assert_allclose(
                np.asarray(batch_traj[key][index]),
                np.asarray(single.trajectory[key]),
                rtol=RTOL,
                atol=ATOL,
                equal_nan=True,
            )



def test_restart_objective_vmap_matches_repeated_candidates() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0])
    responses = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    p1 = binary_parameters("hgf")
    p2 = p1.copy()
    p2[12] = -2.5
    p2[13] = -5.2
    po1 = np.array([np.log(20.0)])
    po2 = np.array([np.log(25.0)])

    batch = fast_binary_unitsq_objective_vmap(
        responses,
        inputs,
        np.stack((p1, p2)),
        np.stack((po1, po2)),
    )

    for index, (pp, po) in enumerate(((p1, po1), (p2, po2))):
        single = fast_binary_unitsq_objective(responses, inputs, pp, po)
        assert float(batch.neg_log_joint[index]) == pytest.approx(
            float(single.neg_log_joint), rel=RTOL, abs=ATOL
        )
        np.testing.assert_allclose(
            np.asarray(batch.trial_log_likelihoods[index]),
            np.asarray(single.trial_log_likelihoods),
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
        )


def test_compile_signature_reuses_jitted_callable() -> None:
    GLOBAL_COMPILE_CACHE.clear()
    inputs = fixture_inputs()
    parameters = binary_parameters("hgf")

    fast_binary_hgf(inputs, parameters)
    first = GLOBAL_COMPILE_CACHE.info()
    fast_binary_hgf(inputs, parameters)
    second = GLOBAL_COMPILE_CACHE.info()

    assert first == {"size": 1, "hits": 0, "misses": 1}
    assert second == {"size": 1, "hits": 1, "misses": 1}
    assert trial_length_bucket(17) == 32


def test_explicit_cpu_device_is_x64_and_device_resident() -> None:
    cpu = select_device("cpu")
    result = fast_binary_hgf(
        fixture_inputs(),
        binary_parameters("hgf"),
        device=cpu,
    )
    assert result.inf_states.dtype == np.dtype(np.float64)
    assert result.inf_states.devices() == {cpu}


def test_real_gpu_forward_and_objective_parity_when_available() -> None:
    require_gpu = os.environ.get("HGFX_REQUIRE_GPU") == "1"
    if not has_gpu():
        if require_gpu:
            pytest.fail("HGFX_REQUIRE_GPU=1 but JAX reports no GPU device")
        pytest.skip("No real JAX GPU device on this runner")

    cpu = select_device("cpu")
    gpu = select_device("gpu")
    inputs = fixture_inputs()
    responses = np.nan_to_num(inputs, nan=0.0)
    p_prc = binary_parameters("hgf")
    p_obs = np.array([np.log(20.0)], dtype=np.float64)

    cpu_forward = fast_binary_hgf(inputs, p_prc, device=cpu)
    gpu_forward = fast_binary_hgf(inputs, p_prc, device=gpu)
    np.testing.assert_allclose(
        np.asarray(gpu_forward.inf_states),
        np.asarray(cpu_forward.inf_states),
        rtol=RTOL,
        atol=ATOL,
        equal_nan=True,
    )

    cpu_objective = fast_binary_unitsq_objective(
        responses, inputs, p_prc, p_obs, device=cpu
    )
    gpu_objective = fast_binary_unitsq_objective(
        responses, inputs, p_prc, p_obs, device=gpu
    )
    assert float(gpu_objective.neg_log_joint) == pytest.approx(
        float(cpu_objective.neg_log_joint), rel=RTOL, abs=ATOL
    )
    assert gpu_forward.inf_states.devices() == {gpu}
