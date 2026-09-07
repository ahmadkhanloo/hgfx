"""Compatibility MAP fitting built strictly on the frozen M8 objective."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

import numpy as np

from hgfx.core.priors import optimization_indices
from hgfx.optim.compat_quasinewton import (
    QuasiNewtonOptions,
    QuasiNewtonResult,
    quasinewton_optim,
)

from .configs import hgf_binary_config, unitsq_sgm_config
from .objective import ObjectiveResult, hgf_binary_unitsq_objective


@dataclass(frozen=True)
class FitProblem:
    """Restricted free-parameter view of a full transformed parameter vector."""

    responses: np.ndarray
    inputs: np.ndarray
    n_perceptual: int
    initial_full: np.ndarray
    free_indices: tuple[int, ...]

    @property
    def initial_free(self) -> np.ndarray:
        idx = np.asarray(self.free_indices, dtype=np.int64)
        return self.initial_full[idx].copy()

    def expand(self, free_parameters) -> np.ndarray:
        free = np.asarray(free_parameters, dtype=np.float64).reshape(-1)
        if free.size != len(self.free_indices):
            raise ValueError(
                f"Expected {len(self.free_indices)} free parameters, got {free.size}"
            )
        full = self.initial_full.copy()
        full[np.asarray(self.free_indices, dtype=np.int64)] = free
        return full

    def evaluate_full(self, full_parameters) -> ObjectiveResult:
        full = np.asarray(full_parameters, dtype=np.float64).reshape(-1)
        if full.size != self.initial_full.size:
            raise ValueError(
                f"Expected {self.initial_full.size} full parameters, got {full.size}"
            )
        return hgf_binary_unitsq_objective(
            self.responses,
            self.inputs,
            full[: self.n_perceptual],
            full[self.n_perceptual :],
        )

    def evaluate_free(self, free_parameters) -> float:
        return float(self.evaluate_full(self.expand(free_parameters)).neg_log_joint)


@dataclass(frozen=True)
class CompatibilityFitResult:
    """Compatibility fit result before or after LME-based restart selection."""

    problem: FitProblem
    optimizer: QuasiNewtonResult
    final_full: np.ndarray
    objective: ObjectiveResult
    perceptual_transformed: np.ndarray
    observation_transformed: np.ndarray
    perceptual_native: np.ndarray
    observation_native: np.ndarray


def hgf_binary_unitsq_fit_problem(responses, inputs) -> FitProblem:
    """Construct the exact fitModel free/fixed vector for the compatibility slice."""

    y = np.asarray(responses, dtype=np.float64)
    u = np.asarray(inputs, dtype=np.float64)

    prc = hgf_binary_config().resolve_placeholders(u)
    obs = unitsq_sgm_config()

    initial_full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    all_variances = np.concatenate((prc.priorsas, obs.priorsas))
    free_indices = optimization_indices(all_variances)

    return FitProblem(
        responses=y.copy(),
        inputs=u.copy(),
        n_perceptual=len(prc.parameters),
        initial_full=initial_full,
        free_indices=free_indices,
    )


def _fit_from_free_start(
    problem: FitProblem,
    free_start,
    *,
    options: QuasiNewtonOptions,
) -> CompatibilityFitResult:
    start = np.asarray(free_start, dtype=np.float64).reshape(-1)
    if start.size != len(problem.free_indices):
        raise ValueError("restart vector has wrong number of free parameters")

    start_full = problem.expand(start)
    start_result = problem.evaluate_full(start_full)
    if start_result.rval != 0 or not np.isfinite(start_result.neg_log_joint):
        raise RuntimeError("Compatibility start point is not stable.")

    optimizer = quasinewton_optim(problem.evaluate_free, start, options)
    final_full = problem.expand(optimizer.arg_min)
    objective = problem.evaluate_full(final_full)

    n_prc = problem.n_perceptual
    p_prc = final_full[:n_prc].copy()
    p_obs = final_full[n_prc:].copy()
    prc_config = hgf_binary_config().resolve_placeholders(problem.inputs)
    obs_config = unitsq_sgm_config()

    return CompatibilityFitResult(
        problem=problem,
        optimizer=optimizer,
        final_full=final_full,
        objective=objective,
        perceptual_transformed=p_prc,
        observation_transformed=p_obs,
        perceptual_native=prc_config.transformed_to_native(p_prc),
        observation_native=obs_config.transformed_to_native(p_obs),
    )


def fit_hgf_binary_unitsq_compat(
    responses,
    inputs,
    *,
    options: QuasiNewtonOptions | None = None,
) -> CompatibilityFitResult:
    """Run the stable-prior default compatibility fit."""

    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    return _fit_from_free_start(
        problem,
        problem.initial_free,
        options=options or QuasiNewtonOptions(),
    )


def fit_hgf_binary_unitsq_multistart_compat(
    responses,
    inputs,
    restart_free_parameters: Sequence[Sequence[float]] | np.ndarray,
    *,
    options: QuasiNewtonOptions | None = None,
) -> tuple[CompatibilityFitResult, object, int]:
    """Select the best default+restart run by frozen fitModel LME semantics.

    The restart vectors are explicit transformed-space free parameters. This
    deliberately separates restart *selection* parity from MATLAB's RNG stream.
    """

    from .fit_statistics import fit_statistics

    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    opts = options or QuasiNewtonOptions()

    starts = [problem.initial_free]
    restart_array = np.asarray(restart_free_parameters, dtype=np.float64)
    if restart_array.size:
        restart_array = restart_array.reshape(-1, len(problem.free_indices))
        starts.extend(row.copy() for row in restart_array)

    best_fit = _fit_from_free_start(problem, starts[0], options=opts)
    best_stats = fit_statistics(problem, best_fit.optimizer)
    best_index = 0

    for index, start in enumerate(starts[1:], start=1):
        candidate_fit = _fit_from_free_start(problem, start, options=opts)
        candidate_stats = fit_statistics(problem, candidate_fit.optimizer)
        if candidate_stats.lme > best_stats.lme:
            best_fit = candidate_fit
            best_stats = candidate_stats
            best_index = index

    return best_fit, best_stats, best_index
