from __future__ import annotations

import numpy as np
import pytest

from hgfx.models.hgf import hgf
from hgfx.models.hgf_binary import hgf_binary
from hgfx.updates.binary_l1 import hgf_binary_level1
from hgfx.updates.binary_l2 import hgf_binary_level2
from hgfx.updates.continuous_l1 import hgf_continuous_level1
from hgfx.updates.precision_prediction import hgf_pihat, hgf_pihat_last
from hgfx.updates.prediction import hgf_prediction
from hgfx.updates.volatility import hgf_volatility_update
from hgfx.updates.volatility_pe import hgf_volatility_pe
from hgfx.validation.trajectory_checks import check_hgf_trajectories


def binary_parameters() -> np.ndarray:
    return np.array(
        [
            np.nan, 0.0, 1.0,
            np.nan, np.log(0.1), 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, -3.0, -6.0,
        ],
        dtype=np.float64,
    )


def continuous_parameters() -> np.ndarray:
    return np.array(
        [
            0.2, 1.0,
            np.log(0.05), np.log(0.1),
            0.0, 0.0,
            0.0,
            -4.0, -6.0,
            np.log(100.0),
        ],
        dtype=np.float64,
    )


def test_prediction_and_precision_blocks_match_reference_formulas() -> None:
    assert hgf_prediction(0.4, 1.7, rho=-0.15) == pytest.approx(0.145)
    assert hgf_prediction(
        0.4, 1.7, rho=-0.15, phi=0.2, m=1.1
    ) == pytest.approx(0.383)

    expected = 1.0 / (1.0 / 2.5 + 1.3 * np.exp(0.7 * 0.25 - 2.0))
    assert hgf_pihat(2.5, 1.3, 0.7, 0.25, -2.0) == pytest.approx(expected)
    assert hgf_pihat_last(2.5, 1.3, 0.02) == pytest.approx(
        1.0 / (0.4 + 0.026)
    )


def test_binary_level_blocks_and_clamp_semantics() -> None:
    mu1, pi1, muhat1, pihat1, da1 = hgf_binary_level1(1.0, 1.2, -0.4)
    expected_hat = 1.0 / (1.0 + np.exp(0.48))
    assert mu1 == 1.0
    assert np.isinf(pi1)
    assert muhat1 == pytest.approx(expected_hat)
    assert pihat1 == pytest.approx(
        1.0 / (expected_hat * (1.0 - expected_hat))
    )
    assert da1 == pytest.approx(1.0 - expected_hat)

    assert hgf_binary_level1(1.0, 1.0, -20.0)[2] == 0.001
    assert hgf_binary_level1(0.0, 1.0, 20.0)[2] == 0.999

    pi2, mu2, da2 = hgf_binary_level2(0.3, 2.0, 1.0, 4.0, 0.2)
    assert pi2 == pytest.approx(2.25)
    assert mu2 == pytest.approx(0.3 + 0.2 / 2.25)
    assert da2 == pytest.approx(
        (1.0 / pi2 + (mu2 - 0.3) ** 2) * 2.0 - 1.0
    )


def test_continuous_and_volatility_blocks_match_reference_formulas() -> None:
    pi1, mu1, dau, da1 = hgf_continuous_level1(0.4, 0.3, 2.0, 0.05)
    assert dau == pytest.approx(0.1)
    assert pi1 == pytest.approx(22.0)
    expected_mu = (
        0.3 + (1.0 / 2.0) * (1.0 / (1.0 / 2.0 + 0.05)) * 0.1
    )
    assert mu1 == pytest.approx(expected_mu)
    assert da1 == pytest.approx(
        (1.0 / pi1 + (mu1 - 0.3) ** 2) * 2.0 - 1.0
    )
    assert hgf_volatility_pe(pi1, mu1, 0.3, 2.0) == pytest.approx(da1)


def test_volatility_update_standard_hgf_matches_equation() -> None:
    args = dict(
        muhat_j=0.25,
        pihat_j=2.0,
        ka_jm1=0.7,
        pihat_jm1=3.0,
        da_jm1=0.2,
        mu_prev_j=0.1,
        om_jm1=-2.0,
        pi_prev_jm1=2.5,
        pi_jm1=3.2,
        mu_jm1=0.4,
        muhat_jm1=0.35,
        t_k=1.3,
    )
    pi, mu, v, w = hgf_volatility_update(**args, update_type="hgf")
    expected_v = 1.3 * np.exp(0.7 * 0.1 - 2.0)
    expected_w = expected_v * 3.0
    expected_pi = 2.0 + 0.5 * 0.7**2 * expected_w * (
        expected_w + (2.0 * expected_w - 1.0) * 0.2
    )
    expected_mu = (
        0.25 + 0.5 / expected_pi * 0.7 * expected_w * 0.2
    )
    assert v == pytest.approx(expected_v)
    assert w == pytest.approx(expected_w)
    assert pi == pytest.approx(expected_pi)
    assert mu == pytest.approx(expected_mu)


def test_volatility_update_supports_all_frozen_branches() -> None:
    args = (
        0.25, 2.0, 0.7, 3.0, 0.2, 0.1,
        -2.0, 2.5, 3.2, 0.4, 0.35, 1.3,
    )
    for update_type in ("hgf", "ehgf", "uhgf"):
        result = np.asarray(
            hgf_volatility_update(*args, update_type), dtype=np.float64
        )
        assert np.all(np.isfinite(result))
        assert result[0] > 0.0


def test_trajectory_validation_rejects_nan() -> None:
    with pytest.raises(ValueError, match="Variational approximation invalid"):
        check_hgf_trajectories(
            np.array([[0.0, 1.0], [np.nan, 1.1]]),
            np.ones((2, 2)),
            16.0,
        )


def test_binary_forward_shapes_and_ignored_trial_copy() -> None:
    inputs = np.array(
        [0.0, 1.0, 1.0, 0.0, np.nan, 1.0, 0.0, 1.0]
    )
    traj, inf_states = hgf_binary(
        inputs, binary_parameters(), transformed=True
    )
    assert traj["mu"].shape == (8, 3)
    assert traj["w"].shape == (8, 2)
    assert inf_states.shape == (8, 3, 4)
    np.testing.assert_array_equal(traj["mu"][4], traj["mu"][3])
    np.testing.assert_array_equal(traj["sa"][4], traj["sa"][3])


def test_continuous_forward_shapes_and_ignored_dau_semantics() -> None:
    values = np.array(
        [0.2, 0.25, 0.18, 0.30, 0.22, np.nan, 0.24, 0.31]
    )
    intervals = np.array([0.5, 1.0, 1.5, 0.8, 1.2, 0.7, 1.1, 0.9])
    inputs = np.column_stack((values, intervals))
    traj, inf_states = hgf(
        inputs,
        continuous_parameters(),
        transformed=True,
        irregular_intervals=True,
    )
    assert traj["mu"].shape == (8, 2)
    assert traj["w"].shape == (8, 1)
    assert inf_states.shape == (8, 2, 4)
    np.testing.assert_array_equal(traj["mu"][5], traj["mu"][4])
    assert np.isnan(traj["dau"][5])
