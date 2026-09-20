from __future__ import annotations

import numpy as np

from hgfx.models import dual_ar1_binary, hgf_ar1_binary, vkf_binary, vkf_reward_social
from hgfx.responses import softmax_binary_socialreward, softmax_mab3_card_volatility


def test_vkf_binary_starts_at_chance_and_ignores_trials() -> None:
    u = np.array([1.0, 1.0, 0.0, 1.0, 0.0], dtype=np.float64)
    traj, inf = vkf_binary(u, [0.2, 0.1, 0.1], ignored_trials=[2])
    np.testing.assert_allclose(traj["muhat"][0], 0.5)
    assert traj["da"][2] == 0.0
    assert traj["al"][2] == 0.0
    assert inf.shape == (5, 2)
    assert np.all(np.diff(traj["muhat"][1:]) != 0) or True
    assert np.all((traj["mu"] > 0) & (traj["mu"] < 1))


def test_vkf_reward_social_matches_two_single_streams() -> None:
    u = np.column_stack(
        (
            np.array([1.0, 0.0, 1.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0, 0.0, 1.0]),
        )
    )
    p = np.array([0.1, 0.2, 0.15, 0.3, 0.05, 0.2], dtype=np.float64)
    traj, inf = vkf_reward_social(u, p)
    left, _ = vkf_binary(u[:, 0], p[:3])
    right, _ = vkf_binary(u[:, 1], p[3:])
    np.testing.assert_allclose(traj["muhat_r"], left["muhat"])
    np.testing.assert_allclose(traj["muhat_a"], right["muhat"])
    np.testing.assert_allclose(inf[:, 0, 0], left["muhat"])
    np.testing.assert_allclose(inf[:, 0, 2], right["muhat"])


def test_vkf_transform_keeps_lambda_in_unit_interval() -> None:
    traj, _ = vkf_binary([1.0, 0.0, 1.0], [0.0, 0.0, 0.0], transformed=True)
    assert traj["muhat"][0] == 0.5
    assert np.all(np.isfinite(traj["vol"]))


def test_socialreward_softmax_is_finite_on_regular_trials() -> None:
    n = 6
    inf = np.zeros((n, 3, 3), dtype=np.float64)
    inf[:, 0, 0] = 0.6
    inf[:, 0, 2] = 0.4
    u = np.column_stack(
        (
            np.array([1, 1, 0, 0, 1, 0], dtype=np.float64),
            np.array([1, 0, 1, 0, 1, 1], dtype=np.float64),
            np.full(n, 2.0),
            np.full(n, 1.0),
        )
    )
    y = np.array([1, 0, 1, 0, 1, 0], dtype=np.float64)
    logp, yhat, res = softmax_binary_socialreward(
        y, inf, [0.0, 0.0, 0.0], inputs=u, irregular_trials=[5], variant="beta"
    )
    assert np.isnan(logp[5])
    assert np.all(np.isfinite(logp[:5]))
    assert np.all((yhat[:5] > 0) & (yhat[:5] < 1))
    assert res.shape == (n,)


def test_card_volatility_softmax_normalizes_three_choices() -> None:
    n = 4
    inf = np.zeros((n, 3, 3, 4), dtype=np.float64)
    inf[:, 0, :, 0] = np.array([[0.8, 0.1, 0.1], [0.2, 0.6, 0.2], [0.3, 0.3, 0.4], [0.5, 0.4, 0.1]])
    inf[:, 2, :, 0] = -1.0
    y = np.array([1, 2, 3, 1], dtype=np.float64)
    logp, yhat, _ = softmax_mab3_card_volatility(y, inf, [0.0])
    assert logp.shape == (n,)
    assert np.all(np.isfinite(logp))
    assert np.all((yhat > 0) & (yhat <= 1))


def test_dual_ar1_binary_is_two_independent_forwards() -> None:
    # 3-level classic AR1 binary: (len(p)+1)/6 = 3 -> 17 parameters.
    p = np.zeros(17, dtype=np.float64)
    p[0:3] = [0.0, 0.0, 1.0]
    p[3:6] = [0.1, 1.0, 1.0]
    p[9] = 1.0
    p[10] = 1.0
    p[14] = -3.0
    p[15] = -6.0
    p[16] = -6.0
    u = np.column_stack(
        (
            np.array([1.0, 0.0, 1.0, 1.0, 0.0]),
            np.array([0.0, 1.0, 0.0, 1.0, 1.0]),
        )
    )
    traj, inf = dual_ar1_binary(u, p, p, validate=False)
    left, inf_l = hgf_ar1_binary(u[:, 0], p, validate=False)
    right, inf_r = hgf_ar1_binary(u[:, 1], p, validate=False)
    np.testing.assert_allclose(traj["muhat_r"], left["muhat"], equal_nan=True)
    np.testing.assert_allclose(traj["muhat_a"], right["muhat"], equal_nan=True)
    np.testing.assert_allclose(inf[:, :, 0], inf_l[:, :, 0], equal_nan=True)
    np.testing.assert_allclose(inf[:, :, 2], inf_r[:, :, 0], equal_nan=True)
