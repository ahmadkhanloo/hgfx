"""M16 subject/restart batch engine for the JAX fitting path."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
from jax.scipy.optimize import minimize as jax_minimize

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem

from .batching import trial_length_bucket
from .compile_cache import CompileSignature, GLOBAL_COMPILE_CACHE
from .devices import select_device
from .engine import _binary_forward_impl, _gaussian_prior
from .fitting import BFGSOptions


@dataclass(frozen=True, order=True)
class BatchKey:
    """Static scheduling identity for one compiled subject/restart group."""

    model: str
    observation_model: str
    bucket: int
    restart_count: int
    dtype: str = "float64"


@dataclass(frozen=True)
class BatchGroup:
    key: BatchKey
    subject_indices: tuple[int, ...]


@dataclass(frozen=True)
class BatchPlan:
    groups: tuple[BatchGroup, ...]
    n_subjects: int

    @property
    def buckets(self) -> tuple[int, ...]:
        return tuple(sorted({group.key.bucket for group in self.groups}))


@dataclass(frozen=True)
class SubjectBatchFitResult:
    subject_index: int
    n_trials: int
    bucket: int
    free_starts: jax.Array
    objective_values: jax.Array
    recomputed_objective_values: jax.Array
    free_parameters: jax.Array
    final_full: jax.Array
    gradients: jax.Array
    inverse_hessians: jax.Array
    iterations: jax.Array
    statuses: jax.Array
    successes: jax.Array
    inf_states: jax.Array
    valid: jax.Array


@dataclass(frozen=True)
class BatchFitResult:
    plan: BatchPlan
    subjects: tuple[SubjectBatchFitResult, ...]
    device: object

    def subject(self, index: int) -> SubjectBatchFitResult:
        if index < 0 or index >= len(self.subjects):
            raise IndexError("subject index out of range")
        return self.subjects[index]


def _as_subject_sequences(
    responses_batch: Sequence[Any],
    inputs_batch: Sequence[Any],
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    if len(responses_batch) != len(inputs_batch):
        raise ValueError("responses_batch and inputs_batch must contain the same subjects")
    if not inputs_batch:
        raise ValueError("batch must contain at least one subject")

    responses: list[np.ndarray] = []
    inputs: list[np.ndarray] = []
    for subject_index, (responses_value, inputs_value) in enumerate(
        zip(responses_batch, inputs_batch, strict=True)
    ):
        y = np.asarray(responses_value, dtype=np.float64)
        x = np.asarray(inputs_value, dtype=np.float64)
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError(
                "M16 first batch slice requires 1D regular binary-HGF inputs/responses; "
                f"subject {subject_index} has shapes {x.shape} and {y.shape}"
            )
        if x.size == 0:
            raise ValueError(f"subject {subject_index} has no trials")
        if x.shape[0] != y.shape[0]:
            raise ValueError(
                f"subject {subject_index} responses/inputs trial counts do not match"
            )
        responses.append(y)
        inputs.append(x)
    return tuple(responses), tuple(inputs)


def _normalize_restarts(
    responses: tuple[np.ndarray, ...],
    inputs: tuple[np.ndarray, ...],
    restart_free_parameters: Sequence[Any] | None,
) -> tuple[tuple[np.ndarray, ...], tuple[Any, ...]]:
    if restart_free_parameters is not None and len(restart_free_parameters) != len(inputs):
        raise ValueError("restart_free_parameters must contain one entry per subject")

    starts_by_subject: list[np.ndarray] = []
    problems: list[Any] = []
    for subject_index, (y, x) in enumerate(zip(responses, inputs, strict=True)):
        problem = hgf_binary_unitsq_fit_problem(y, x)
        problems.append(problem)
        default = problem.initial_free.reshape(1, -1)
        if restart_free_parameters is None:
            starts_by_subject.append(default)
            continue

        raw = restart_free_parameters[subject_index]
        if raw is None:
            starts_by_subject.append(default)
            continue
        restarts = np.asarray(raw, dtype=np.float64)
        if restarts.size == 0:
            starts_by_subject.append(default)
            continue
        restarts = restarts.reshape(-1, len(problem.free_indices))
        starts_by_subject.append(np.concatenate((default, restarts), axis=0))

    return tuple(starts_by_subject), tuple(problems)


def plan_hgf_binary_unitsq_batches(
    responses_batch: Sequence[Any],
    inputs_batch: Sequence[Any],
    *,
    restart_free_parameters: Sequence[Any] | None = None,
) -> BatchPlan:
    """Group subjects by JAX-static trial bucket and restart count."""

    responses, inputs = _as_subject_sequences(responses_batch, inputs_batch)
    starts, _ = _normalize_restarts(responses, inputs, restart_free_parameters)

    grouped: dict[BatchKey, list[int]] = defaultdict(list)
    for index, (x, subject_starts) in enumerate(zip(inputs, starts, strict=True)):
        key = BatchKey(
            model="hgf_binary",
            observation_model="unitsq_sgm",
            bucket=trial_length_bucket(int(x.shape[0])),
            restart_count=int(subject_starts.shape[0]),
        )
        grouped[key].append(index)

    groups = tuple(
        BatchGroup(key=key, subject_indices=tuple(indices))
        for key, indices in sorted(grouped.items(), key=lambda item: item[0])
    )
    return BatchPlan(groups=groups, n_subjects=len(inputs))


def _prepare_group(
    group: BatchGroup,
    responses: tuple[np.ndarray, ...],
    inputs: tuple[np.ndarray, ...],
    starts_by_subject: tuple[np.ndarray, ...],
    problems: tuple[Any, ...],
    *,
    device,
):
    batch_size = len(group.subject_indices)
    bucket = group.key.bucket
    restart_count = group.key.restart_count
    first_problem = problems[group.subject_indices[0]]
    free_indices = first_problem.free_indices
    n_perceptual = first_problem.n_perceptual
    n_full = int(first_problem.initial_full.size)
    n_free = len(free_indices)

    y_batch = np.zeros((batch_size, bucket), dtype=np.float64)
    x_batch = np.zeros((batch_size, bucket), dtype=np.float64)
    ignored_batch = np.ones((batch_size, bucket), dtype=np.bool_)
    regular_batch = np.zeros((batch_size, bucket), dtype=np.bool_)
    initial_full = np.empty((batch_size, n_full), dtype=np.float64)
    starts = np.empty((batch_size, restart_count, n_free), dtype=np.float64)
    lengths = np.empty((batch_size,), dtype=np.int32)

    for local_index, subject_index in enumerate(group.subject_indices):
        y = responses[subject_index]
        x = inputs[subject_index]
        problem = problems[subject_index]
        if problem.free_indices != free_indices:
            raise ValueError("subjects in one batch group must share free-parameter semantics")
        if problem.n_perceptual != n_perceptual:
            raise ValueError("subjects in one batch group must share perceptual parameter layout")
        subject_starts = starts_by_subject[subject_index]
        if subject_starts.shape != (restart_count, n_free):
            raise ValueError("scheduler grouped incompatible restart shapes")

        n_trials = int(x.shape[0])
        lengths[local_index] = n_trials
        safe_x = np.nan_to_num(x, nan=0.0)
        safe_y = np.nan_to_num(y, nan=0.0)
        ignored = np.isnan(x)
        regular = ~(np.isnan(x) | np.isnan(y))

        x_batch[local_index, :n_trials] = safe_x
        y_batch[local_index, :n_trials] = safe_y
        ignored_batch[local_index, :n_trials] = ignored
        regular_batch[local_index, :n_trials] = regular
        initial_full[local_index] = problem.initial_full
        starts[local_index] = subject_starts

    prc = hgf_binary_config()
    obs = unitsq_sgm_config()
    arrays = [
        y_batch,
        x_batch,
        ignored_batch,
        regular_batch,
        initial_full,
        starts,
        np.asarray(prc.priormus, dtype=np.float64),
        np.asarray(prc.priorsas, dtype=np.float64),
        np.asarray(obs.priormus, dtype=np.float64),
        np.asarray(obs.priorsas, dtype=np.float64),
    ]
    arrays = [jax.device_put(jnp.asarray(value), device) for value in arrays]
    return (
        *arrays,
        lengths,
        free_indices,
        n_perceptual,
    )


def _subject_free_objective(
    free_parameters,
    responses,
    inputs,
    ignored,
    regular,
    initial_full,
    prc_means,
    prc_variances,
    obs_means,
    obs_variances,
    *,
    free_indices: tuple[int, ...],
    n_perceptual: int,
):
    idx = jnp.asarray(free_indices, dtype=jnp.int32)
    full = initial_full.at[idx].set(free_parameters)
    p_prc = full[:n_perceptual]
    p_obs = full[n_perceptual:]

    _, inf_states, valid = _binary_forward_impl(
        inputs,
        p_prc,
        ignored,
        update_type="hgf",
        transformed=True,
        irregular_intervals=False,
    )
    prediction = inf_states[:, 0, 0]
    ze = jnp.exp(p_obs.reshape(-1)[0])

    logx = jnp.where(
        (1.0 - prediction) < 1e-4,
        jnp.log1p(prediction - 1.0),
        jnp.log(prediction),
    )
    log1mx = jnp.where(
        prediction < 1e-4,
        jnp.log1p(-prediction),
        jnp.log(1.0 - prediction),
    )
    logp = (
        responses * ze * (logx - log1mx)
        + ze * log1mx
        - jnp.log((1.0 - prediction) ** ze + prediction**ze)
    )
    log_likelihood = jnp.sum(jnp.where(regular, logp, 0.0))
    prc_prior = _gaussian_prior(p_prc, prc_means, prc_variances)
    obs_prior = _gaussian_prior(p_obs, obs_means, obs_variances)
    realmax = jnp.finfo(jnp.float64).max
    return jnp.where(
        valid,
        -(log_likelihood + prc_prior + obs_prior),
        realmax,
    )


def _group_runner(
    *,
    key: BatchKey,
    batch_size: int,
    free_indices: tuple[int, ...],
    n_perceptual: int,
    options: BFGSOptions,
):
    signature = CompileSignature(
        model="hgf_binary_batch_fit",
        levels=3,
        observation_model="unitsq_sgm",
        dtype=key.dtype,
        trial_length_bucket=key.bucket,
        static_options=(
            ("batch_size", batch_size),
            ("restart_count", key.restart_count),
            ("max_iter", options.max_iter),
            ("tol_grad", options.tol_grad),
            ("line_search_max_iter", options.line_search_max_iter),
        ),
    )

    def factory():
        def run(
            responses,
            inputs,
            ignored,
            regular,
            initial_full,
            starts,
            prc_means,
            prc_variances,
            obs_means,
            obs_variances,
        ):
            def solve_subject(
                subject_responses,
                subject_inputs,
                subject_ignored,
                subject_regular,
                subject_initial,
                subject_starts,
            ):
                def objective(free_parameters):
                    return _subject_free_objective(
                        free_parameters,
                        subject_responses,
                        subject_inputs,
                        subject_ignored,
                        subject_regular,
                        subject_initial,
                        prc_means,
                        prc_variances,
                        obs_means,
                        obs_variances,
                        free_indices=free_indices,
                        n_perceptual=n_perceptual,
                    )

                def solve_start(start):
                    result = jax_minimize(
                        objective,
                        start,
                        method="BFGS",
                        options={
                            "maxiter": options.max_iter,
                            "gtol": options.tol_grad,
                            "line_search_maxiter": options.line_search_max_iter,
                        },
                    )
                    return (
                        result.fun,
                        result.x,
                        result.jac,
                        result.hess_inv,
                        result.nit,
                        result.status,
                        result.success,
                    )

                return jax.vmap(solve_start)(subject_starts)

            solved = jax.vmap(solve_subject)(
                responses,
                inputs,
                ignored,
                regular,
                initial_full,
                starts,
            )
            values, positions, gradients, inverse_hessians, iterations, statuses, successes = solved

            idx = jnp.asarray(free_indices, dtype=jnp.int32)
            expanded = jnp.broadcast_to(
                initial_full[:, None, :],
                (initial_full.shape[0], positions.shape[1], initial_full.shape[1]),
            )
            expanded = expanded.at[:, :, idx].set(positions)
            perceptual = expanded[:, :, :n_perceptual]

            def recompute_subject(
                subject_responses,
                subject_inputs,
                subject_ignored,
                subject_regular,
                subject_initial,
                subject_positions,
                subject_perceptual,
            ):
                recomputed = jax.vmap(
                    lambda free: _subject_free_objective(
                        free,
                        subject_responses,
                        subject_inputs,
                        subject_ignored,
                        subject_regular,
                        subject_initial,
                        prc_means,
                        prc_variances,
                        obs_means,
                        obs_variances,
                        free_indices=free_indices,
                        n_perceptual=n_perceptual,
                    )
                )(subject_positions)

                def forward_one(p_prc):
                    _, states, valid = _binary_forward_impl(
                        subject_inputs,
                        p_prc,
                        subject_ignored,
                        update_type="hgf",
                        transformed=True,
                        irregular_intervals=False,
                    )
                    return states, valid

                states, valid = jax.vmap(forward_one)(subject_perceptual)
                return recomputed, states, valid

            recomputed, states, valid = jax.vmap(recompute_subject)(
                responses,
                inputs,
                ignored,
                regular,
                initial_full,
                positions,
                perceptual,
            )
            return (
                values,
                recomputed,
                positions,
                expanded,
                gradients,
                inverse_hessians,
                iterations,
                statuses,
                successes,
                states,
                valid,
            )

        return jax.jit(run)

    return GLOBAL_COMPILE_CACHE.get_or_create(signature, factory)


def fit_hgf_binary_unitsq_batch(
    responses_batch: Sequence[Any],
    inputs_batch: Sequence[Any],
    *,
    restart_free_parameters: Sequence[Any] | None = None,
    options: BFGSOptions | None = None,
    device=None,
) -> BatchFitResult:
    """Fit independent subjects/restarts in shape-homogeneous compiled groups.

    Each subject always includes its M9/M15 default start as restart 0. Additional
    starts are fitted independently and returned without silently changing M10's
    LME-based compatibility restart-selection semantics.
    """

    execution_device = device if device is not None else select_device("auto")
    opts = options or BFGSOptions()
    responses, inputs = _as_subject_sequences(responses_batch, inputs_batch)
    starts_by_subject, problems = _normalize_restarts(
        responses,
        inputs,
        restart_free_parameters,
    )
    plan = plan_hgf_binary_unitsq_batches(
        responses,
        inputs,
        restart_free_parameters=restart_free_parameters,
    )

    subject_results: list[SubjectBatchFitResult | None] = [None] * len(inputs)

    for group in plan.groups:
        (
            y_batch,
            x_batch,
            ignored_batch,
            regular_batch,
            initial_full,
            starts,
            prc_means,
            prc_variances,
            obs_means,
            obs_variances,
            lengths,
            free_indices,
            n_perceptual,
        ) = _prepare_group(
            group,
            responses,
            inputs,
            starts_by_subject,
            problems,
            device=execution_device,
        )

        runner = _group_runner(
            key=group.key,
            batch_size=len(group.subject_indices),
            free_indices=free_indices,
            n_perceptual=n_perceptual,
            options=opts,
        )
        output = runner(
            y_batch,
            x_batch,
            ignored_batch,
            regular_batch,
            initial_full,
            starts,
            prc_means,
            prc_variances,
            obs_means,
            obs_variances,
        )
        (
            values,
            recomputed,
            positions,
            expanded,
            gradients,
            inverse_hessians,
            iterations,
            statuses,
            successes,
            states,
            valid,
        ) = output

        for local_index, subject_index in enumerate(group.subject_indices):
            n_trials = int(lengths[local_index])
            subject_results[subject_index] = SubjectBatchFitResult(
                subject_index=subject_index,
                n_trials=n_trials,
                bucket=group.key.bucket,
                free_starts=starts[local_index],
                objective_values=values[local_index],
                recomputed_objective_values=recomputed[local_index],
                free_parameters=positions[local_index],
                final_full=expanded[local_index],
                gradients=gradients[local_index],
                inverse_hessians=inverse_hessians[local_index],
                iterations=iterations[local_index],
                statuses=statuses[local_index],
                successes=successes[local_index],
                inf_states=states[local_index, :, :n_trials],
                valid=valid[local_index],
            )

    if any(result is None for result in subject_results):
        raise RuntimeError("batch scheduler failed to produce one result per subject")

    return BatchFitResult(
        plan=plan,
        subjects=tuple(result for result in subject_results if result is not None),
        device=execution_device,
    )


__all__ = [
    "BatchKey",
    "BatchGroup",
    "BatchPlan",
    "SubjectBatchFitResult",
    "BatchFitResult",
    "plan_hgf_binary_unitsq_batches",
    "fit_hgf_binary_unitsq_batch",
]
