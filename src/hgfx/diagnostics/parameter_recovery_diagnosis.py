"""Targeted diagnosis of M18 parameter-recovery failures.

M18A separates four mechanisms that can make simulated parameters fail to recover:

1. optimizer/start-point sensitivity;
2. cross-parameter confounding;
3. weak finite-data likelihood identifiability;
4. prior-driven MAP shrinkage.

The diagnostic functions reuse the frozen M18 simulation and objective code paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from hgfx.compat.configs import unitsq_sgm_config
from hgfx.compat.objective import ObjectiveResult
from hgfx.optim.compat_quasinewton import (
    QuasiNewtonOptions,
    QuasiNewtonResult,
    quasinewton_optim,
)

from .recovery import (
    _free_indices,
    _objective_for_variant,
    _truth_vector,
    _variant_components,
    deterministic_binary_inputs,
    fit_binary_variant,
    simulate_binary_variant,
)


@dataclass(frozen=True)
class RecoveryParameter:
    """Metadata for one free transformed-space recovery parameter."""

    free_position: int
    full_index: int
    role: str
    transformed_name: str
    native_name: str
    prior_mean: float
    prior_variance: float

    @property
    def prior_sd(self) -> float:
        return float(np.sqrt(self.prior_variance))


@dataclass(frozen=True)
class RestrictedRecoveryFit:
    """MAP fit in which only an explicit subset of full-vector entries may move."""

    model: str
    optimized_full_indices: tuple[int, ...]
    optimizer: QuasiNewtonResult
    base_full: np.ndarray
    initial_values: np.ndarray
    final_full: np.ndarray
    objective: ObjectiveResult

    @property
    def final_values(self) -> np.ndarray:
        idx = np.asarray(self.optimized_full_indices, dtype=np.int64)
        return self.final_full[idx].copy()


@dataclass(frozen=True)
class ParameterProfile:
    """One-dimensional likelihood/joint profile with all other parameters fixed at truth."""

    parameter: RecoveryParameter
    truth_value: float
    grid: np.ndarray
    neg_log_likelihood: np.ndarray
    neg_log_joint: np.ndarray
    likelihood_minimum: float
    joint_minimum: float
    likelihood_minimum_offset_sd: float
    joint_minimum_offset_sd: float
    likelihood_minimum_distance_to_prior_sd: float
    joint_minimum_distance_to_prior_sd: float
    likelihood_span: float
    joint_span: float
    likelihood_curvature: float
    joint_curvature: float


@dataclass(frozen=True)
class DatasetDiagnosis:
    """All M18A diagnostics for one simulated dataset."""

    model: str
    trial_count: int
    truth_scale: float
    replicate: int
    seed: int
    parameter_metadata: tuple[RecoveryParameter, ...]
    truth_full: np.ndarray
    truth_free: np.ndarray
    baseline_free: np.ndarray
    truth_start_free: np.ndarray
    oracle_single_free: np.ndarray
    perceptual_oracle_free: np.ndarray
    baseline_neg_log_joint: float
    truth_start_neg_log_joint: float
    baseline_termination: str
    truth_start_termination: str
    profiles: tuple[ParameterProfile, ...]


def recovery_parameter_metadata(model: str, inputs) -> tuple[RecoveryParameter, ...]:
    """Return ordered metadata matching the free vector used by M18."""

    config_factory, _ = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    free_indices = _free_indices(prc, obs)
    specs = list(prc.parameters) + list(obs.parameters)
    n_prc = len(prc.parameters)

    rows: list[RecoveryParameter] = []
    for free_position, full_index in enumerate(free_indices):
        spec = specs[full_index]
        rows.append(
            RecoveryParameter(
                free_position=free_position,
                full_index=full_index,
                role="perceptual" if full_index < n_prc else "observation",
                transformed_name=spec.name,
                native_name=spec.native_name,
                prior_mean=float(spec.prior_mean),
                prior_variance=float(spec.prior_variance),
            )
        )
    return tuple(rows)


def fit_restricted_binary_variant(
    responses,
    inputs,
    model: str,
    *,
    base_full,
    optimized_full_indices: Sequence[int],
    initial_values: Sequence[float] | np.ndarray | None = None,
    options: QuasiNewtonOptions | None = None,
) -> RestrictedRecoveryFit:
    """Fit an explicit free-parameter subset while all other entries remain fixed."""

    config_factory, _ = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    allowed = set(_free_indices(prc, obs))
    indices = tuple(int(i) for i in optimized_full_indices)
    if not indices:
        raise ValueError("at least one parameter must be optimized")
    if len(set(indices)) != len(indices):
        raise ValueError("optimized_full_indices must be unique")
    if any(index not in allowed for index in indices):
        raise ValueError("restricted fitting may optimize only frozen-config free parameters")

    base = np.asarray(base_full, dtype=np.float64).reshape(-1).copy()
    expected = len(prc.parameters) + len(obs.parameters)
    if base.size != expected:
        raise ValueError(f"Expected a full vector of length {expected}, got {base.size}")

    idx = np.asarray(indices, dtype=np.int64)
    if initial_values is None:
        start = base[idx].copy()
    else:
        start = np.asarray(initial_values, dtype=np.float64).reshape(-1)
    if start.size != len(indices):
        raise ValueError("initial_values length must match optimized_full_indices")

    def expand(values) -> np.ndarray:
        selected = np.asarray(values, dtype=np.float64).reshape(-1)
        if selected.size != len(indices):
            raise ValueError("restricted parameter vector has the wrong length")
        full = base.copy()
        full[idx] = selected
        return full

    def scalar_objective(values) -> float:
        return float(
            _objective_for_variant(
                model=model,
                responses=responses,
                inputs=inputs,
                full_parameters=expand(values),
            ).neg_log_joint
        )

    initial_objective = _objective_for_variant(
        model=model,
        responses=responses,
        inputs=inputs,
        full_parameters=expand(start),
    )
    if initial_objective.rval != 0 or not np.isfinite(initial_objective.neg_log_joint):
        raise RuntimeError(f"Initial restricted fit point is unstable for {model}")

    optimizer = quasinewton_optim(
        scalar_objective,
        start,
        options or QuasiNewtonOptions(),
    )
    final_full = expand(optimizer.arg_min)
    objective = _objective_for_variant(
        model=model,
        responses=responses,
        inputs=inputs,
        full_parameters=final_full,
    )
    return RestrictedRecoveryFit(
        model=model,
        optimized_full_indices=indices,
        optimizer=optimizer,
        base_full=base,
        initial_values=start.copy(),
        final_full=final_full,
        objective=objective,
    )


def _curvature(values: np.ndarray, grid: np.ndarray, index: int) -> float:
    if index <= 0 or index >= values.size - 1:
        return float("nan")
    left = float(grid[index] - grid[index - 1])
    right = float(grid[index + 1] - grid[index])
    if not np.isclose(left, right):
        return float("nan")
    step = 0.5 * (left + right)
    if step <= 0.0:
        return float("nan")
    return float((values[index - 1] - 2.0 * values[index] + values[index + 1]) / step**2)


def profile_parameter_at_truth(
    responses,
    inputs,
    model: str,
    truth_full,
    parameter: RecoveryParameter,
    *,
    width_sd: float = 1.5,
    points: int = 31,
) -> ParameterProfile:
    """Profile NLL and negative log joint around truth with other parameters fixed."""

    if points < 5 or points % 2 == 0:
        raise ValueError("profile points must be an odd integer >= 5")
    if width_sd <= 0.0:
        raise ValueError("width_sd must be positive")

    truth = np.asarray(truth_full, dtype=np.float64).reshape(-1)
    sd = parameter.prior_sd
    center = float(truth[parameter.full_index])
    grid = np.linspace(center - width_sd * sd, center + width_sd * sd, points)
    nll = np.empty(points, dtype=np.float64)
    nlj = np.empty(points, dtype=np.float64)

    for i, value in enumerate(grid):
        full = truth.copy()
        full[parameter.full_index] = value
        result = _objective_for_variant(
            model=model,
            responses=responses,
            inputs=inputs,
            full_parameters=full,
        )
        nll[i] = result.neg_log_likelihood
        nlj[i] = result.neg_log_joint

    likelihood_index = int(np.argmin(nll))
    joint_index = int(np.argmin(nlj))
    likelihood_minimum = float(grid[likelihood_index])
    joint_minimum = float(grid[joint_index])
    prior = parameter.prior_mean

    return ParameterProfile(
        parameter=parameter,
        truth_value=center,
        grid=grid,
        neg_log_likelihood=nll,
        neg_log_joint=nlj,
        likelihood_minimum=likelihood_minimum,
        joint_minimum=joint_minimum,
        likelihood_minimum_offset_sd=float((likelihood_minimum - center) / sd),
        joint_minimum_offset_sd=float((joint_minimum - center) / sd),
        likelihood_minimum_distance_to_prior_sd=float(abs(likelihood_minimum - prior) / sd),
        joint_minimum_distance_to_prior_sd=float(abs(joint_minimum - prior) / sd),
        likelihood_span=float(np.max(nll) - np.min(nll)),
        joint_span=float(np.max(nlj) - np.min(nlj)),
        likelihood_curvature=_curvature(nll, grid, likelihood_index),
        joint_curvature=_curvature(nlj, grid, joint_index),
    )


def diagnose_parameter_recovery_dataset(
    *,
    model: str,
    trial_count: int,
    replicate: int,
    seed: int,
    truth_scale: float = 0.35,
    options: QuasiNewtonOptions | None = None,
    profile_points: int = 31,
) -> DatasetDiagnosis:
    """Run baseline, truth-start, oracle, and profile diagnostics on one dataset."""

    inputs = deterministic_binary_inputs(trial_count, seed)
    truth_full, truth_free, free_indices = _truth_vector(
        model,
        inputs,
        replicate=replicate,
        scale=truth_scale,
    )
    responses, _ = simulate_binary_variant(
        model,
        inputs,
        truth_full,
        seed=seed + 1,
    )
    metadata = recovery_parameter_metadata(model, inputs)
    if tuple(item.full_index for item in metadata) != free_indices:
        raise RuntimeError("M18A metadata order diverged from M18 free-vector order")

    fit_options = options or QuasiNewtonOptions()
    baseline = fit_binary_variant(
        responses,
        inputs,
        model,
        options=fit_options,
    )
    truth_start = fit_binary_variant(
        responses,
        inputs,
        model,
        options=fit_options,
        initial_free=truth_free,
    )

    oracle_values = np.full(len(metadata), np.nan, dtype=np.float64)
    for parameter in metadata:
        oracle = fit_restricted_binary_variant(
            responses,
            inputs,
            model,
            base_full=truth_full,
            optimized_full_indices=(parameter.full_index,),
            initial_values=(parameter.prior_mean,),
            options=fit_options,
        )
        oracle_values[parameter.free_position] = oracle.final_values[0]

    perceptual = tuple(item for item in metadata if item.role == "perceptual")
    perceptual_values = np.full(len(metadata), np.nan, dtype=np.float64)
    if perceptual:
        fit = fit_restricted_binary_variant(
            responses,
            inputs,
            model,
            base_full=truth_full,
            optimized_full_indices=tuple(item.full_index for item in perceptual),
            initial_values=tuple(item.prior_mean for item in perceptual),
            options=fit_options,
        )
        for item, value in zip(perceptual, fit.final_values, strict=True):
            perceptual_values[item.free_position] = value

    profiles = tuple(
        profile_parameter_at_truth(
            responses,
            inputs,
            model,
            truth_full,
            parameter,
            points=profile_points,
        )
        for parameter in metadata
    )

    return DatasetDiagnosis(
        model=model,
        trial_count=trial_count,
        truth_scale=float(truth_scale),
        replicate=replicate,
        seed=seed,
        parameter_metadata=metadata,
        truth_full=truth_full,
        truth_free=truth_free,
        baseline_free=baseline.final_free,
        truth_start_free=truth_start.final_free,
        oracle_single_free=oracle_values,
        perceptual_oracle_free=perceptual_values,
        baseline_neg_log_joint=float(baseline.objective.neg_log_joint),
        truth_start_neg_log_joint=float(truth_start.objective.neg_log_joint),
        baseline_termination=baseline.optimizer.termination,
        truth_start_termination=truth_start.optimizer.termination,
        profiles=profiles,
    )


__all__ = [
    "RecoveryParameter",
    "RestrictedRecoveryFit",
    "ParameterProfile",
    "DatasetDiagnosis",
    "recovery_parameter_metadata",
    "fit_restricted_binary_variant",
    "profile_parameter_at_truth",
    "diagnose_parameter_recovery_dataset",
]
