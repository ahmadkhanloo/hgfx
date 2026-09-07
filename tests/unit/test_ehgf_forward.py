from __future__ import annotations

import numpy as np
import pytest

from hgfx.models.ehgf import ehgf
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.updates.volatility import hgf_volatility_update


def binary_parameters() -> np.ndarray:
    return np.array(
        [
            np.nan, 0.0, 1.0,
            np.nan, np.log(0.1), 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, -3.0, 2.0,
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


def test_ehgf_safe_precision_clips_negative_correction() -> None:
    args = dict(
        muhat_j=0.2,
        pihat_j=0.05,
        ka_jm1=1.0,
        pihat_jm1=0.2,
        da_jm1=-1.0,
        mu_prev_j=1.0,
        om_jm1=1.0,
        pi_prev_jm1=1.0,
        pi_jm1=1.0,
        mu_jm1=1.0,
        muhat_jm1=0.0,
        t_k=1.0,
    )

    with pytest.raises(ValueError, match="Negative posterior precision"):
        hgf_volatility_update(**args, update_type="hgf")

    pi, mu, v, w = hgf_volatility_update(**args, update_type="ehgf")
    assert pi == pytest.approx(args["pihat_j"])
    assert np.isfinite(mu)
    assert np.isfinite(v)
    assert np.isfinite(w)
    assert pi > 0.0


def test_ehgf_mean_update_uses_predicted_precision() -> None:
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
    pi, mu, v, w = hgf_volatility_update(**args, update_type="ehgf")
    expected_v = 1.3 * np.exp(0.7 * 0.1 - 2.0)
    expected_w = expected_v * 3.0
    expected_mu = 0.25 + 0.5 / 2.0 * 0.7 * expected_w * 0.2
    assert mu == pytest.approx(expected_mu)
    assert pi >= args["pihat_j"]


def test_binary_ehgf_forward_shapes_and_ignored_copy() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, np.nan, 1.0, 0.0, 1.0])
    traj, inf_states = ehgf_binary(
        inputs, binary_parameters(), transformed=True
    )
    assert traj["mu"].shape == (8, 3)
    assert traj["w"].shape == (8, 2)
    assert inf_states.shape == (8, 3, 4)
    np.testing.assert_array_equal(traj["mu"][4], traj["mu"][3])
    np.testing.assert_array_equal(traj["sa"][4], traj["sa"][3])
    assert np.all(traj["sa"][:, 1:] > 0.0)


def test_continuous_ehgf_irregular_ignored_semantics() -> None:
    values = np.array([0.2, 0.25, 0.18, 0.30, 0.22, np.nan, 0.24, 0.31])
    intervals = np.array([0.5, 1.0, 1.5, 0.8, 1.2, 0.7, 1.1, 0.9])
    inputs = np.column_stack((values, intervals))
    traj, inf_states = ehgf(
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
    assert np.all(traj["sa"] > 0.0)
