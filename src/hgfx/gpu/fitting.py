"""Device-resident gradient fitting for the M14 JAX fast objective."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from jax.scipy.optimize import minimize as jax_minimize

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem

from .batching import pad_mask, pad_trials, trial_length_bucket
from .devices import select_device
from .engine import (
    FastForwardResult,
    FastObjectiveResult,
    _binary_unitsq_objective_impl,
    _prepare_inputs,
    fast_binary_hgf,
    fast_binary_unitsq_objective,
)

ScalarObjective = Callable[[jax.Array], jax.Array]


@dataclass(frozen=True)
class FastFitProblem:
    responses: jax.Array
    inputs: jax.Array
    padded_responses: jax.Array
    padded_inputs: jax.Array
    ignored: jax.Array
    perceptual_prior_means: jax.Array
    perceptual_prior_variances: jax.Array
    observation_prior_means: jax.Array
    observation_prior_variances: jax.Array
    initial_full: jax.Array
    free_indices: tuple[int, ...]
    n_perceptual: int
    n_trials: int
    bucket: int
    device: object

    @property
    def initial_free(self) -> jax.Array:
        idx = jnp.asarray(self.free_indices, dtype=jnp.int32)
        return self.initial_full[idx]

    def expand(self, free_parameters) -> jax.Array:
        free = jnp.asarray(free_parameters, dtype=jnp.float64).reshape(-1)
        if free.shape[0] != len(self.free_indices):
            raise ValueError(
                f"Expected {len(self.free_indices)} free parameters, got {free.shape[0]}"
            )
        idx = jnp.asarray(self.free_indices, dtype=jnp.int32)
        return self.initial_full.at[idx].set(free)


@dataclass(frozen=True)
class FastValueGradResult:
    value: jax.Array
    gradient: jax.Array
    free_parameters: jax.Array


@dataclass(frozen=True)
class BFGSOptions:
    max_iter: int = 100
    tol_grad: float = 1e-6
    line_search_max_iter: int = 20

    def __post_init__(self) -> None:
        if self.max_iter <= 0:
            raise ValueError("max_iter must be positive")
        if self.tol_grad <= 0:
            raise ValueError("tol_grad must be positive")
        if self.line_search_max_iter <= 0:
            raise ValueError("line_search_max_iter must be positive")


@dataclass(frozen=True)
class DeviceOptimizerResult:
    value: jax.Array
    position: jax.Array
    gradient: jax.Array
    inverse_hessian: jax.Array
    iterations: jax.Array
    status: jax.Array
    success: jax.Array


class DeviceOptimizer(Protocol):
    name: str

    def minimize(
        self,
        function: ScalarObjective,
        initial,
        *,
        device=None,
    ) -> DeviceOptimizerResult: ...


@dataclass(frozen=True)
class BFGSOptimizer:
    """JAX BFGS backend with optimizer state represented as device arrays."""

    options: BFGSOptions = field(default_factory=BFGSOptions)
    name: str = "jax-bfgs"

    def minimize(
        self,
        function: ScalarObjective,
        initial,
        *,
        device=None,
    ) -> DeviceOptimizerResult:
        x0 = jnp.asarray(initial, dtype=jnp.float64).reshape(-1)
        if x0.size == 0:
            raise ValueError("initial point must contain at least one free parameter")
        if device is not None:
            x0 = jax.device_put(x0, device)

        result = jax_minimize(
            function,
            x0,
            method="BFGS",
            options={
                "maxiter": self.options.max_iter,
                "gtol": self.options.tol_grad,
                "line_search_maxiter": self.options.line_search_max_iter,
            },
        )
        return DeviceOptimizerResult(
            value=result.fun,
            position=result.x,
            gradient=result.jac,
            inverse_hessian=result.hess_inv,
            iterations=result.nit,
            status=result.status,
            success=result.success,
        )


@dataclass(frozen=True)
class FastFitResult:
    problem: FastFitProblem
    optimizer: DeviceOptimizerResult
    final_full: jax.Array
    perceptual_parameters: jax.Array
    observation_parameters: jax.Array
    objective: FastObjectiveResult
    forward: FastForwardResult


def hgf_binary_unitsq_fast_fit_problem(
    responses,
    inputs,
    *,
    device=None,
) -> FastFitProblem:
    """Build the exact M9 free/fixed vector and place it on one JAX device."""

    execution_device = device if device is not None else select_device("auto")
    compatibility = hgf_binary_unitsq_fit_problem(responses, inputs)
    x, ignored = _prepare_inputs(inputs, None)
    y = jnp.asarray(responses, dtype=jnp.float64)
    if y.shape[0] != x.shape[0]:
        raise ValueError("responses and inputs must contain the same number of trials")

    n_trials = int(x.shape[0])
    bucket = trial_length_bucket(n_trials)
    prc = hgf_binary_config().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    arrays = [
        y,
        x,
        pad_trials(y, bucket),
        pad_trials(x, bucket),
        pad_mask(ignored, bucket),
        jnp.asarray(prc.priormus, dtype=jnp.float64),
        jnp.asarray(prc.priorsas, dtype=jnp.float64),
        jnp.asarray(obs.priormus, dtype=jnp.float64),
        jnp.asarray(obs.priorsas, dtype=jnp.float64),
        jnp.asarray(compatibility.initial_full, dtype=jnp.float64),
    ]
    arrays = [jax.device_put(value, execution_device) for value in arrays]

    return FastFitProblem(
        responses=arrays[0],
        inputs=arrays[1],
        padded_responses=arrays[2],
        padded_inputs=arrays[3],
        ignored=arrays[4],
        perceptual_prior_means=arrays[5],
        perceptual_prior_variances=arrays[6],
        observation_prior_means=arrays[7],
        observation_prior_variances=arrays[8],
        initial_full=arrays[9],
        free_indices=compatibility.free_indices,
        n_perceptual=compatibility.n_perceptual,
        n_trials=n_trials,
        bucket=bucket,
        device=execution_device,
    )


def _free_objective(problem: FastFitProblem) -> ScalarObjective:
    idx = jnp.asarray(problem.free_indices, dtype=jnp.int32)

    def objective(free_parameters):
        full = problem.initial_full.at[idx].set(free_parameters)
        p_prc = full[: problem.n_perceptual]
        p_obs = full[problem.n_perceptual :]
        return _binary_unitsq_objective_impl(
            problem.padded_responses,
            problem.padded_inputs,
            p_prc,
            p_obs,
            problem.ignored,
            problem.perceptual_prior_means,
            problem.perceptual_prior_variances,
            problem.observation_prior_means,
            problem.observation_prior_variances,
            irregular_intervals=False,
        )[5]

    return jax.jit(objective)


def fast_binary_unitsq_value_and_grad(
    responses,
    inputs,
    free_parameters=None,
    *,
    device=None,
) -> FastValueGradResult:
    """Evaluate the fast scalar objective and exact JAX gradient."""

    problem = hgf_binary_unitsq_fast_fit_problem(responses, inputs, device=device)
    free = problem.initial_free if free_parameters is None else jnp.asarray(
        free_parameters, dtype=jnp.float64
    ).reshape(-1)
    if free.shape[0] != len(problem.free_indices):
        raise ValueError(
            f"Expected {len(problem.free_indices)} free parameters, got {free.shape[0]}"
        )
    free = jax.device_put(free, problem.device)
    value, gradient = jax.value_and_grad(_free_objective(problem))(free)
    return FastValueGradResult(value=value, gradient=gradient, free_parameters=free)


def fit_hgf_binary_unitsq_fast(
    responses,
    inputs,
    *,
    optimizer: DeviceOptimizer | None = None,
    device=None,
) -> FastFitResult:
    """Fit the M8/M9 binary-HGF + unit-square MAP slice on one JAX device."""

    problem = hgf_binary_unitsq_fast_fit_problem(responses, inputs, device=device)
    selected_optimizer = optimizer or BFGSOptimizer()
    optimization = selected_optimizer.minimize(
        _free_objective(problem),
        problem.initial_free,
        device=problem.device,
    )
    final_full = problem.expand(optimization.position)
    p_prc = final_full[: problem.n_perceptual]
    p_obs = final_full[problem.n_perceptual :]
    objective = fast_binary_unitsq_objective(
        problem.responses,
        problem.inputs,
        p_prc,
        p_obs,
        device=problem.device,
    )
    forward = fast_binary_hgf(problem.inputs, p_prc, device=problem.device)
    return FastFitResult(
        problem=problem,
        optimizer=optimization,
        final_full=final_full,
        perceptual_parameters=p_prc,
        observation_parameters=p_obs,
        objective=objective,
        forward=forward,
    )


__all__ = [
    "FastFitProblem",
    "FastValueGradResult",
    "BFGSOptions",
    "DeviceOptimizerResult",
    "DeviceOptimizer",
    "BFGSOptimizer",
    "FastFitResult",
    "hgf_binary_unitsq_fast_fit_problem",
    "fast_binary_unitsq_value_and_grad",
    "fit_hgf_binary_unitsq_fast",
]
