"""M17 multi-device scheduling for independent HGFX subject batches."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Sequence, Any

import jax

from .batch_engine import BatchFitResult, fit_hgf_binary_unitsq_batch
from .devices import select_device
from .fitting import BFGSOptions


@dataclass(frozen=True)
class DeviceAssignment:
    """One independent subject shard assigned to one explicit JAX device."""

    device_index: int
    subject_indices: tuple[int, ...]


@dataclass(frozen=True)
class MultiDevicePlan:
    assignments: tuple[DeviceAssignment, ...]
    n_subjects: int

    @property
    def device_indices(self) -> tuple[int, ...]:
        return tuple(assignment.device_index for assignment in self.assignments)


@dataclass(frozen=True)
class MultiDeviceBatchFitResult:
    plan: MultiDevicePlan
    subjects: tuple[Any, ...]
    shard_results: tuple[BatchFitResult, ...]

    def subject(self, index: int):
        if index < 0 or index >= len(self.subjects):
            raise IndexError("subject index out of range")
        return self.subjects[index]


def plan_round_robin_subject_shards(
    n_subjects: int,
    device_indices: Sequence[int],
) -> MultiDevicePlan:
    """Build deterministic round-robin independent-data shards."""

    if n_subjects <= 0:
        raise ValueError("n_subjects must be positive")
    devices = tuple(int(index) for index in device_indices)
    if not devices:
        raise ValueError("device_indices must contain at least one device")
    if any(index < 0 for index in devices):
        raise ValueError("device indices must be non-negative")
    if len(set(devices)) != len(devices):
        raise ValueError("device indices must be unique")

    buckets: list[list[int]] = [[] for _ in devices]
    for subject_index in range(n_subjects):
        buckets[subject_index % len(devices)].append(subject_index)

    assignments = tuple(
        DeviceAssignment(device_index=device_index, subject_indices=tuple(indices))
        for device_index, indices in zip(devices, buckets, strict=True)
        if indices
    )
    return MultiDevicePlan(assignments=assignments, n_subjects=n_subjects)


def _slice_optional(values, indices: tuple[int, ...]):
    if values is None:
        return None
    return [values[index] for index in indices]


def fit_hgf_binary_unitsq_multi_device(
    responses_batch: Sequence[Any],
    inputs_batch: Sequence[Any],
    *,
    device_indices: Sequence[int],
    restart_free_parameters: Sequence[Any] | None = None,
    options: BFGSOptions | None = None,
    parallel: bool = True,
) -> MultiDeviceBatchFitResult:
    """Fit independent subject shards across explicitly selected GPU devices.

    M17 is data-parallel only: subjects are independent and each shard delegates
    to the validated single-device M16 batch engine. No cross-device collective
    changes the scientific objective.
    """

    if len(responses_batch) != len(inputs_batch):
        raise ValueError("responses_batch and inputs_batch must contain the same subjects")
    if restart_free_parameters is not None and len(restart_free_parameters) != len(inputs_batch):
        raise ValueError("restart_free_parameters must contain one entry per subject")

    plan = plan_round_robin_subject_shards(len(inputs_batch), device_indices)

    def run_assignment(assignment: DeviceAssignment) -> BatchFitResult:
        device = select_device("gpu", index=assignment.device_index)
        idx = assignment.subject_indices
        return fit_hgf_binary_unitsq_batch(
            [responses_batch[i] for i in idx],
            [inputs_batch[i] for i in idx],
            restart_free_parameters=_slice_optional(restart_free_parameters, idx),
            options=options,
            device=device,
        )

    if parallel and len(plan.assignments) > 1:
        with ThreadPoolExecutor(max_workers=len(plan.assignments)) as pool:
            shard_results = tuple(pool.map(run_assignment, plan.assignments))
    else:
        shard_results = tuple(run_assignment(a) for a in plan.assignments)

    ordered: list[Any | None] = [None] * plan.n_subjects
    for assignment, shard in zip(plan.assignments, shard_results, strict=True):
        for local_index, global_index in enumerate(assignment.subject_indices):
            source = shard.subject(local_index)
            ordered[global_index] = source.__class__(
                subject_index=global_index,
                n_trials=source.n_trials,
                bucket=source.bucket,
                free_starts=source.free_starts,
                objective_values=source.objective_values,
                recomputed_objective_values=source.recomputed_objective_values,
                free_parameters=source.free_parameters,
                final_full=source.final_full,
                gradients=source.gradients,
                inverse_hessians=source.inverse_hessians,
                iterations=source.iterations,
                statuses=source.statuses,
                successes=source.successes,
                inf_states=source.inf_states,
                valid=source.valid,
            )

    if any(value is None for value in ordered):
        raise RuntimeError("multi-device scheduler failed to return every subject")

    return MultiDeviceBatchFitResult(
        plan=plan,
        subjects=tuple(value for value in ordered if value is not None),
        shard_results=shard_results,
    )


__all__ = [
    "DeviceAssignment",
    "MultiDevicePlan",
    "MultiDeviceBatchFitResult",
    "plan_round_robin_subject_shards",
    "fit_hgf_binary_unitsq_multi_device",
]
