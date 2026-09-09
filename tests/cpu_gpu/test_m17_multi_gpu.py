from __future__ import annotations

import os

import numpy as np
import pytest

from hgfx.gpu import (
    BFGSOptions,
    fit_hgf_binary_unitsq_batch,
    fit_hgf_binary_unitsq_multi_device,
    has_gpu,
    plan_round_robin_subject_shards,
    select_device,
)


def subject(length: int, offset: int = 0) -> tuple[np.ndarray, np.ndarray]:
    base_inputs = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
         1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
        dtype=np.float64,
    )
    base_responses = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1,
         1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    return np.roll(base_responses, offset)[:length].copy(), np.roll(base_inputs, offset)[:length].copy()


def test_round_robin_plan_is_deterministic() -> None:
    plan = plan_round_robin_subject_shards(7, [0, 2, 4])
    assert plan.n_subjects == 7
    assert plan.device_indices == (0, 2, 4)
    assert plan.assignments[0].subject_indices == (0, 3, 6)
    assert plan.assignments[1].subject_indices == (1, 4)
    assert plan.assignments[2].subject_indices == (2, 5)


def test_round_robin_rejects_duplicate_devices() -> None:
    with pytest.raises(ValueError, match="unique"):
        plan_round_robin_subject_shards(2, [0, 0])


def test_real_two_gpu_multi_device_parity_when_available() -> None:
    require_gpu = os.environ.get("HGFX_REQUIRE_GPU") == "1"
    try:
        gpu0 = select_device("gpu", index=0)
        gpu1 = select_device("gpu", index=1)
    except (RuntimeError, IndexError):
        if require_gpu:
            pytest.fail("HGFX_REQUIRE_GPU=1 but fewer than two JAX GPU devices are visible")
        pytest.skip("Fewer than two JAX GPU devices are visible")

    options = BFGSOptions(max_iter=40)
    pairs = [subject(24, 0), subject(29, 1), subject(24, 2), subject(29, 3)]
    ys = [pair[0] for pair in pairs]
    xs = [pair[1] for pair in pairs]

    single = fit_hgf_binary_unitsq_batch(ys, xs, options=options, device=gpu0)
    multi = fit_hgf_binary_unitsq_multi_device(
        ys,
        xs,
        device_indices=[0, 1],
        options=options,
        parallel=True,
    )

    assert multi.plan.device_indices == (0, 1)
    for i in range(len(ys)):
        expected = single.subject(i)
        actual = multi.subject(i)
        np.testing.assert_allclose(
            np.asarray(actual.objective_values),
            np.asarray(expected.objective_values),
            rtol=1e-7,
            atol=1e-8,
        )
        np.testing.assert_allclose(
            np.asarray(actual.free_parameters),
            np.asarray(expected.free_parameters),
            rtol=2e-6,
            atol=2e-7,
        )
        np.testing.assert_allclose(
            np.asarray(actual.inf_states),
            np.asarray(expected.inf_states),
            rtol=2e-7,
            atol=2e-8,
            equal_nan=True,
        )

    for assignment, shard in zip(multi.plan.assignments, multi.shard_results, strict=True):
        expected_device = select_device("gpu", index=assignment.device_index)
        assert shard.device == expected_device
        for result in shard.subjects:
            assert result.objective_values.devices() == {expected_device}
