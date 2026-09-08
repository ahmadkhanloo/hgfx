from __future__ import annotations

import os

import jax
import numpy as np
import pytest

from hgfx.compat.fitting import (
    fit_hgf_binary_unitsq_compat,
    hgf_binary_unitsq_fit_problem,
)
from hgfx.gpu import (
    BFGSOptimizer,
    BFGSOptions,
    fast_binary_unitsq_objective,
    fast_binary_unitsq_value_and_grad,
    fit_hgf_binary_unitsq_fast,
    has_gpu,
    select_device,
)
from hgfx.models.hgf_binary import hgf_binary


jax.config.update("jax_enable_x64", True)

RTOL = 3e-9
ATOL = 3e-10


def fixture_data() -> tuple[np.ndarray, np.ndarray]:
    inputs = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    responses = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    return responses, inputs


def central_difference(function, point: np.ndarray, step: float = 1e-5) -> np.ndarray:
    gradient = np.empty_like(point)
    for index in range(point.size):
        delta = np.zeros_like(point)
        delta[index] = step
        gradient[index] = (function(point + delta) - function(point - delta)) / (2.0 * step)
    return gradient


def test_differentiable_fast_objective_matches_compatibility_gradient() -> None:
    responses, inputs = fixture_data()
    compatibility = hgf_binary_unitsq_fit_problem(responses, inputs)
    cpu = select_device("cpu")

    result = fast_binary_unitsq_value_and_grad(responses, inputs, device=cpu)
    expected_value = compatibility.evaluate_free(compatibility.initial_free)
    expected_gradient = central_difference(
        compatibility.evaluate_free,
        compatibility.initial_free,
    )

    assert float(result.value) == pytest.approx(expected_value, rel=RTOL, abs=ATOL)
    np.testing.assert_allclose(
        np.asarray(result.gradient),
        expected_gradient,
        rtol=2e-4,
        atol=2e-5,
    )
    assert result.gradient.dtype == np.dtype(np.float64)
    assert result.gradient.devices() == {cpu}


def test_bfgs_optimizer_keeps_state_on_selected_device() -> None:
    cpu = select_device("cpu")
    target = jax.device_put(np.array([0.75, -1.25, 0.5], dtype=np.float64), cpu)

    def objective(point):
        delta = point - target
        return jax.numpy.vdot(delta, delta)

    optimizer = BFGSOptimizer(BFGSOptions(max_iter=32, tol_grad=1e-9))
    result = optimizer.minimize(objective, np.array([2.0, -3.0, 1.5]), device=cpu)

    assert bool(result.success)
    np.testing.assert_allclose(np.asarray(result.position), np.asarray(target), atol=1e-8)
    for value in (
        result.value,
        result.position,
        result.gradient,
        result.inverse_hessian,
        result.iterations,
        result.status,
    ):
        assert value.devices() == {cpu}


def test_fast_fit_improves_objective_and_reproduces_final_trajectory() -> None:
    responses, inputs = fixture_data()
    cpu = select_device("cpu")
    compatibility_problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    initial_value = compatibility_problem.evaluate_free(compatibility_problem.initial_free)

    result = fit_hgf_binary_unitsq_fast(
        responses,
        inputs,
        device=cpu,
        optimizer=BFGSOptimizer(BFGSOptions(max_iter=100)),
    )

    assert bool(result.optimizer.success)
    assert float(result.objective.neg_log_joint) <= initial_value
    assert float(result.objective.neg_log_joint) == pytest.approx(
        float(result.optimizer.value), rel=RTOL, abs=ATOL
    )

    recomputed = fast_binary_unitsq_objective(
        responses,
        inputs,
        result.perceptual_parameters,
        result.observation_parameters,
        device=cpu,
    )
    assert float(recomputed.neg_log_joint) == pytest.approx(
        float(result.objective.neg_log_joint), rel=RTOL, abs=ATOL
    )

    expected_trajectory, expected_states = hgf_binary(
        inputs,
        np.asarray(result.perceptual_parameters),
        transformed=True,
    )
    np.testing.assert_allclose(
        np.asarray(result.forward.inf_states),
        expected_states,
        rtol=RTOL,
        atol=ATOL,
        equal_nan=True,
    )
    for key, expected in expected_trajectory.items():
        np.testing.assert_allclose(
            np.asarray(result.forward.trajectory[key]),
            expected,
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
            err_msg=key,
        )

    compatibility_fit = fit_hgf_binary_unitsq_compat(responses, inputs)
    assert float(result.objective.neg_log_joint) <= compatibility_fit.objective.neg_log_joint + 1e-3


def test_real_gpu_fitting_parity_when_available() -> None:
    require_gpu = os.environ.get("HGFX_REQUIRE_GPU") == "1"
    if not has_gpu():
        if require_gpu:
            pytest.fail("HGFX_REQUIRE_GPU=1 but JAX reports no GPU device")
        pytest.skip("No real JAX GPU device on this runner")

    responses, inputs = fixture_data()
    cpu = select_device("cpu")
    gpu = select_device("gpu")
    optimizer = BFGSOptimizer(BFGSOptions(max_iter=100))

    cpu_fit = fit_hgf_binary_unitsq_fast(
        responses,
        inputs,
        device=cpu,
        optimizer=optimizer,
    )
    gpu_fit = fit_hgf_binary_unitsq_fast(
        responses,
        inputs,
        device=gpu,
        optimizer=optimizer,
    )

    assert float(gpu_fit.objective.neg_log_joint) == pytest.approx(
        float(cpu_fit.objective.neg_log_joint), rel=1e-7, abs=1e-8
    )
    np.testing.assert_allclose(
        np.asarray(gpu_fit.optimizer.position),
        np.asarray(cpu_fit.optimizer.position),
        rtol=2e-6,
        atol=2e-7,
    )
    np.testing.assert_allclose(
        np.asarray(gpu_fit.forward.inf_states),
        np.asarray(cpu_fit.forward.inf_states),
        rtol=2e-7,
        atol=2e-8,
        equal_nan=True,
    )
    for value in (
        gpu_fit.optimizer.value,
        gpu_fit.optimizer.position,
        gpu_fit.optimizer.gradient,
        gpu_fit.optimizer.inverse_hessian,
        gpu_fit.final_full,
        gpu_fit.forward.inf_states,
    ):
        assert value.devices() == {gpu}
