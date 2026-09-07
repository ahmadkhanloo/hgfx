from __future__ import annotations

import numpy as np
import pytest

from hgfx.models.uhgf import uhgf
from hgfx.models.uhgf_binary import uhgf_binary
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


def test_uhgf_nominal_update_is_positive_and_distinct_from_first_expansion() -> None:
    args = (
        0.25, 2.0, 0.7, 3.0, 0.2, 0.1,
        -2.0, 2.5, 3.2, 0.4, 0.35, 1.3,
    )
    pi, mu, v, w = hgf_volatility_update(*args, "uhgf")

    pihat = args[1]
    ka = args[2]
    da = args[4]
    pi_prev_lower = args[7]
    muhat = args[0]
    om = args[6]
    t = args[11]

    expected_v = t * np.exp(ka * muhat + om)
    expected_w = 1.0 / (1.0 + 1.0 / (pi_prev_lower * expected_v))
    pi1 = pihat + 0.5 * ka**2 * expected_w * (1.0 - expected_w)
    mu1 = muhat + 0.5 / pi1 * ka * expected_w * da

    assert pi > 0.0
    assert np.isfinite(mu)
    assert v == pytest.approx(expected_v)
    assert w == pytest.approx(expected_w)
    assert mu != pytest.approx(mu1, abs=1e-8)


def test_uhgf_extreme_logspace_case_falls_back_to_finite_first_expansion() -> None:
    args = (
        0.2, 1e-4, 1.0, 0.5, 0.3, 0.1,
        -1.0, 1.5, 2.0, 0.4, 0.35, 1.0,
    )
    pi, mu, v, w = hgf_volatility_update(*args, "uhgf")

    assert np.isfinite(pi)
    assert np.isfinite(mu)
    assert np.isfinite(v)
    assert np.isfinite(w)
    assert pi > 0.0


def test_binary_uhgf_forward_shapes_and_ignored_copy() -> None:
    inputs = np.array([0.0, 1.0, 1.0, 0.0, np.nan, 1.0, 0.0, 1.0])
    traj, inf_states = uhgf_binary(inputs, binary_parameters(), transformed=True)

    assert traj["mu"].shape == (8, 3)
    assert traj["w"].shape == (8, 2)
    assert inf_states.shape == (8, 3, 4)
    np.testing.assert_array_equal(traj["mu"][4], traj["mu"][3])
    np.testing.assert_array_equal(traj["sa"][4], traj["sa"][3])
    assert np.all(np.isfinite(traj["mu"][:, 1:]))
    assert np.all(traj["sa"][:, 1:] > 0.0)


def test_continuous_uhgf_irregular_ignored_semantics() -> None:
    values = np.array([0.2, 0.25, 0.18, 0.30, 0.22, np.nan, 0.24, 0.31])
    intervals = np.array([0.5, 1.0, 1.5, 0.8, 1.2, 0.7, 1.1, 0.9])
    inputs = np.column_stack((values, intervals))

    traj, inf_states = uhgf(
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
    assert np.all(np.isfinite(traj["mu"]))
    assert np.all(traj["sa"] > 0.0)
