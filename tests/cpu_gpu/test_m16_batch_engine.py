from __future__ import annotations

import numpy as np
import pytest

from hgfx.gpu import (
    BFGSOptimizer,
    BFGSOptions,
    GLOBAL_COMPILE_CACHE,
    fit_hgf_binary_unitsq_batch,
    fit_hgf_binary_unitsq_fast,
    plan_hgf_binary_unitsq_batches,
    select_device,
)


RTOL = 2e-7
ATOL = 2e-8


def subject(length: int, offset: int = 0) -> tuple[np.ndarray, np.ndarray]:
    base_inputs = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0,
         1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
        dtype=np.float64,
    )
    base_responses = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0,
         1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    x = np.roll(base_inputs, offset)[:length].copy()
    y = np.roll(base_responses, offset)[:length].copy()
    return y, x


def test_scheduler_groups_by_bucket_and_restart_count() -> None:
    y0, x0 = subject(17, 0)
    y1, x1 = subject(24, 1)
    y2, x2 = subject(33, 2)

    restarts = [
        np.array([[-2.9, -5.8, np.log(40.0)]], dtype=np.float64),
        np.array([[-2.7, -5.2, np.log(36.0)]], dtype=np.float64),
        np.empty((0, 3), dtype=np.float64),
    ]
    plan = plan_hgf_binary_unitsq_batches(
        [y0, y1, y2],
        [x0, x1, x2],
        restart_free_parameters=restarts,
    )

    assert plan.n_subjects == 3
    assert plan.buckets == (32, 64)
    assert len(plan.groups) == 2
    group0 = next(group for group in plan.groups if group.key.bucket == 32)
    group1 = next(group for group in plan.groups if group.key.bucket == 64)
    assert group0.subject_indices == (0, 1)
    assert group0.key.restart_count == 2
    assert group1.subject_indices == (2,)
    assert group1.key.restart_count == 1


def test_subject_batch_default_start_matches_repeated_single_fit() -> None:
    cpu = select_device("cpu")
    options = BFGSOptions(max_iter=100)
    ys, xs = zip(subject(24, 0), subject(24, 3), strict=True)
    responses = [ys[0], ys[1]]
    inputs = [xs[0], xs[1]]

    batch = fit_hgf_binary_unitsq_batch(
        responses,
        inputs,
        options=options,
        device=cpu,
    )

    for index in range(2):
        single = fit_hgf_binary_unitsq_fast(
            responses[index],
            inputs[index],
            optimizer=BFGSOptimizer(options),
            device=cpu,
        )
        subject_result = batch.subject(index)
        assert subject_result.free_parameters.shape[0] == 1
        assert bool(subject_result.successes[0])
        assert float(subject_result.objective_values[0]) == pytest.approx(
            float(single.objective.neg_log_joint),
            rel=RTOL,
            abs=ATOL,
        )
        np.testing.assert_allclose(
            np.asarray(subject_result.free_parameters[0]),
            np.asarray(single.optimizer.position),
            rtol=2e-6,
            atol=2e-7,
        )
        np.testing.assert_allclose(
            np.asarray(subject_result.inf_states[0]),
            np.asarray(single.forward.inf_states),
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
        )


def test_restart_batch_matches_independent_single_starts() -> None:
    cpu = select_device("cpu")
    options = BFGSOptions(max_iter=100)
    y, x = subject(24, 0)
    restarts = np.array(
        [
            [-2.8, -5.7, np.log(42.0)],
            [-2.4, -5.0, np.log(30.0)],
        ],
        dtype=np.float64,
    )

    batch = fit_hgf_binary_unitsq_batch(
        [y],
        [x],
        restart_free_parameters=[restarts],
        options=options,
        device=cpu,
    )
    result = batch.subject(0)

    assert result.free_parameters.shape[0] == 3
    np.testing.assert_allclose(
        np.asarray(result.objective_values),
        np.asarray(result.recomputed_objective_values),
        rtol=RTOL,
        atol=ATOL,
    )

    from hgfx.gpu.fitting import hgf_binary_unitsq_fast_fit_problem, _free_objective

    problem = hgf_binary_unitsq_fast_fit_problem(y, x, device=cpu)
    optimizer = BFGSOptimizer(options)
    expected_starts = np.concatenate(
        (np.asarray(problem.initial_free)[None, :], restarts),
        axis=0,
    )
    for index, start in enumerate(expected_starts):
        single = optimizer.minimize(_free_objective(problem), start, device=cpu)
        assert float(result.objective_values[index]) == pytest.approx(
            float(single.value), rel=RTOL, abs=ATOL
        )
        np.testing.assert_allclose(
            np.asarray(result.free_parameters[index]),
            np.asarray(single.position),
            rtol=2e-6,
            atol=2e-7,
        )


def test_heterogeneous_lengths_preserve_single_equivalence_and_reuse_cache() -> None:
    cpu = select_device("cpu")
    options = BFGSOptions(max_iter=80)
    y0, x0 = subject(17, 0)
    y1, x1 = subject(29, 2)
    y2, x2 = subject(33, 4)

    GLOBAL_COMPILE_CACHE.clear()
    first = fit_hgf_binary_unitsq_batch(
        [y0, y1, y2],
        [x0, x1, x2],
        options=options,
        device=cpu,
    )
    first_info = GLOBAL_COMPILE_CACHE.info()

    second = fit_hgf_binary_unitsq_batch(
        [y0, y1, y2],
        [x0, x1, x2],
        options=options,
        device=cpu,
    )
    second_info = GLOBAL_COMPILE_CACHE.info()

    assert first.plan.buckets == (32, 64)
    assert first_info["size"] == 2
    assert second_info["size"] == 2
    assert second_info["hits"] >= first_info["hits"] + 2

    for index, (y, x) in enumerate(((y0, x0), (y1, x1), (y2, x2))):
        single = fit_hgf_binary_unitsq_fast(
            y,
            x,
            optimizer=BFGSOptimizer(options),
            device=cpu,
        )
        batched = second.subject(index)
        assert batched.n_trials == x.size
        assert batched.bucket in {32, 64}
        assert float(batched.objective_values[0]) == pytest.approx(
            float(single.objective.neg_log_joint),
            rel=RTOL,
            abs=ATOL,
        )
        np.testing.assert_allclose(
            np.asarray(batched.inf_states[0]),
            np.asarray(single.forward.inf_states),
            rtol=RTOL,
            atol=ATOL,
            equal_nan=True,
        )


def test_batch_arrays_remain_on_selected_device() -> None:
    cpu = select_device("cpu")
    y0, x0 = subject(24, 0)
    y1, x1 = subject(24, 1)
    batch = fit_hgf_binary_unitsq_batch([y0, y1], [x0, x1], device=cpu)

    for result in batch.subjects:
        for value in (
            result.objective_values,
            result.recomputed_objective_values,
            result.free_parameters,
            result.final_full,
            result.gradients,
            result.inverse_hessians,
            result.iterations,
            result.statuses,
            result.successes,
            result.inf_states,
            result.valid,
        ):
            assert value.devices() == {cpu}
