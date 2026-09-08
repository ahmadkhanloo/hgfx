from __future__ import annotations

import numpy as np

from hgfx.models.hgf_binary_pu import (
    ehgf_binary_pu,
    ehgf_binary_pu_tbt,
    hgf_binary_pu,
    hgf_binary_pu_tbt,
    uhgf_binary_pu,
    uhgf_binary_pu_tbt,
)
from hgfx.models.hgf_ar1_binary import (
    ehgf_ar1_binary,
    hgf_ar1_binary,
    uhgf_ar1_binary,
)
from hgfx.models.legacy import (
    hidden_markov_model,
    kalman_filter,
    pearce_hall_binary,
    rw_binary,
    rw_binary_dual,
    sutton_k1_binary,
)


def base_inputs() -> np.ndarray:
    return np.array([0, 1, 1, 0, 1, np.nan, 0, 1, 1, 0, 0, 1], dtype=np.float64)


def test_pu_variants_preserve_shapes_and_ignored_state_copy() -> None:
    u = base_inputs()
    p_hgf = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, 0, 1, 1, np.nan, -3, -6, .35, 0, 1],
        dtype=np.float64,
    )
    p_ehgf = p_hgf.copy()
    p_ehgf[13] = 2.0

    for fn, p in [
        (hgf_binary_pu, p_hgf),
        (ehgf_binary_pu, p_ehgf),
        (uhgf_binary_pu, p_hgf),
    ]:
        traj, inf = fn(u, p, ignored_trials=[5], validate=False)
        assert inf.shape == (u.size, 3, 4)
        assert traj["mu"].shape == (u.size, 3)
        np.testing.assert_allclose(traj["mu"][5], traj["mu"][4], equal_nan=True)

    alpha = np.array([.25, .3, .2, .35, .3, .25, .2, .3, .35, .25, .2, .3])
    ut = np.column_stack((u, alpha))
    p_tbt = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, 0, 1, 1, np.nan, -5, -6, 0, 1],
        dtype=np.float64,
    )
    for fn in (hgf_binary_pu_tbt, ehgf_binary_pu_tbt, uhgf_binary_pu_tbt):
        traj, inf = fn(ut, p_tbt, ignored_trials=[5], validate=False)
        assert inf.shape == (u.size, 3, 4)
        np.testing.assert_allclose(traj["mu"][5], traj["mu"][4], equal_nan=True)


def test_ar1_variants_preserve_shapes_and_ignored_state_copy() -> None:
    u = base_inputs()
    p_hgf = np.array(
        [np.nan, 0, 1, np.nan, .006, 4, np.nan, 0, .2, np.nan, 0, 1, 1, 1, np.nan, -2, -6],
        dtype=np.float64,
    )
    p_ext = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, .45, np.nan, 0, 1, np.nan, 0, 0, 1, 1, np.nan, -3, 2],
        dtype=np.float64,
    )
    for fn, p in [
        (hgf_ar1_binary, p_hgf),
        (ehgf_ar1_binary, p_ext),
        (uhgf_ar1_binary, p_ext),
    ]:
        traj, inf = fn(u, p, ignored_trials=[5], validate=False)
        assert inf.shape == (u.size, 3, 4)
        np.testing.assert_allclose(traj["mu"][5], traj["mu"][4], equal_nan=True)


def test_legacy_models_basic_semantics() -> None:
    u = base_inputs()

    traj, inf = rw_binary(u, [.5, .3], ignored_trials=[5])
    assert inf.shape == (u.size,)
    np.testing.assert_allclose(traj["v"][5], traj["v"][4])

    y = np.array([1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1], dtype=np.float64)
    traj, inf = rw_binary_dual(u, y, [.4, .6, .3, .5], ignored_trials=[5])
    assert inf.shape == (u.size, 1, 2, 1, 1)
    np.testing.assert_allclose(traj["v"][5], traj["v"][4])

    traj, inf = pearce_hall_binary(u, [.5, .4, .2], ignored_trials=[5])
    assert inf.shape == (u.size, 3)
    np.testing.assert_allclose(traj["v"][5], traj["v"][4])

    traj, inf = sutton_k1_binary(u, [1, 1, .5, .01], ignored_trials=[5])
    assert inf.shape == (u.size,)
    np.testing.assert_allclose(traj["v"][5], traj["v"][4])

    uk = np.array([.2, .4, .3, .7, .8, np.nan, .5, .6, .55, .9, .4, .3])
    traj, inf = kalman_filter(uk, [.2, .3, -2, 5], ignored_trials=[5])
    assert inf.shape == (uk.size, 2)
    np.testing.assert_allclose(traj["mu"][5], traj["mu"][4])


def test_hmm_probabilities_are_normalized() -> None:
    u = np.array([1, 1, 2, 2, 1, 2, 2, 1, 1, 2, 1, 2], dtype=np.float64)
    b = np.array([[.9, .1], [.1, .9]], dtype=np.float64)
    traj, inf = hidden_markov_model(u, [.6, .85, .2], outcome_matrix=b, n_states=2)
    assert inf.shape == (u.size, 2)
    np.testing.assert_allclose(np.sum(inf, axis=1), 1.0)
    np.testing.assert_allclose(np.sum(traj["alprhat"], axis=1), 1.0)
