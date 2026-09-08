from __future__ import annotations

import numpy as np

from hgfx.compat import hgf_ar1_config
from hgfx.models import hgf_ar1


def test_hgf_ar1_config_transform_semantics() -> None:
    config = hgf_ar1_config()
    assert config.model == "hgf_ar1"
    assert len(config.parameters) == 12

    ptrans = np.array(
        [0.2, 1.0, np.log(0.3), np.log(0.1), 0.0, -np.inf, 0.2, 1.0, 0.0, -3.0, -6.0, np.log(0.2)],
        dtype=np.float64,
    )
    native = config.transformed_to_native(ptrans)
    np.testing.assert_allclose(native[:2], [0.2, 1.0])
    np.testing.assert_allclose(native[2:4], [0.3, 0.1])
    np.testing.assert_allclose(native[4:6], [0.5, 0.0])
    np.testing.assert_allclose(native[6:8], [0.2, 1.0])
    np.testing.assert_allclose(native[8], 1.0)
    np.testing.assert_allclose(native[9:11], [-3.0, -6.0])
    np.testing.assert_allclose(native[11], 0.2)


def test_hgf_ar1_regular_and_ignored_semantics() -> None:
    u = np.array([0.2, 0.4, 0.1, 0.7, 0.6, np.nan, 0.3, 0.9], dtype=np.float64)
    p = np.array(
        [0.2, 1.0, 0.3, 0.1, 0.15, 0.0, 0.2, 1.0, 1.0, -3.0, -6.0, 0.2],
        dtype=np.float64,
    )
    traj, inf = hgf_ar1(u, p, ignored_trials=[5], validate=False)
    assert inf.shape == (u.size, 2, 4)
    for field in ("mu", "sa", "muhat", "sahat", "v", "w", "da", "ud", "psi", "epsi", "wt"):
        assert field in traj
    np.testing.assert_allclose(traj["mu"][5], traj["mu"][4], equal_nan=True)
    np.testing.assert_allclose(traj["sa"][5], traj["sa"][4], equal_nan=True)
    assert np.isnan(traj["dau"][5])


def test_hgf_ar1_irregular_intervals_change_predictions() -> None:
    values = np.array([0.2, 0.4, 0.1, 0.7, 0.6, 0.3], dtype=np.float64)
    intervals = np.array([1.0, 0.5, 1.5, 0.8, 1.2, 0.6], dtype=np.float64)
    inputs = np.column_stack((values, intervals))
    p = np.array(
        [0.2, 1.0, 0.3, 0.1, 0.15, 0.0, 0.2, 1.0, 1.0, -3.0, -6.0, 0.2],
        dtype=np.float64,
    )
    traj_irregular, _ = hgf_ar1(inputs, p, irregular_intervals=True, validate=False)
    traj_regular, _ = hgf_ar1(values, p, irregular_intervals=False, validate=False)
    assert not np.allclose(traj_irregular["muhat"], traj_regular["muhat"], equal_nan=True)
