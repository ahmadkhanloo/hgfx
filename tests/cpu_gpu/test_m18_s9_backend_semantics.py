from __future__ import annotations

import numpy as np

from hgfx.gpu import fast_binary_hgf
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.models.hgf_binary import hgf_binary


RTOL = 3e-10
ATOL = 3e-11


def _boundary_parameters() -> np.ndarray:
    # Three-level transformed binary-HGF vector.  mu_0[1]=8 drives the first
    # level-1 prediction above 0.999.  Frozen standard HGF does not clamp it.
    return np.array(
        [
            np.nan, 8.0, 1.0,
            np.nan, np.log(0.1), 0.0,
            np.nan, 0.0, 0.0,
            0.0, 0.0,
            np.nan, -3.0, -6.0,
        ],
        dtype=np.float64,
    )


def _inputs() -> np.ndarray:
    return np.array([0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0], dtype=np.float64)


def test_standard_hgf_fast_backend_preserves_unclamped_level1_oracle() -> None:
    parameters = _boundary_parameters()
    inputs = _inputs()

    expected_traj, _ = hgf_binary(
        inputs,
        parameters,
        transformed=True,
        validate=False,
    )
    actual = fast_binary_hgf(
        inputs,
        parameters,
        update_type="hgf",
        transformed=True,
        use_jit=False,
    )

    expected = float(expected_traj["muhat"][0, 0])
    observed = float(np.asarray(actual.trajectory["muhat"])[0, 0])
    assert expected > 0.999
    np.testing.assert_allclose(observed, expected, rtol=RTOL, atol=ATOL)


def test_ehgf_fast_backend_retains_legacy_level1_clamp() -> None:
    parameters = _boundary_parameters()
    inputs = _inputs()

    expected_traj, _ = ehgf_binary(inputs, parameters, transformed=True)
    actual = fast_binary_hgf(
        inputs,
        parameters,
        update_type="ehgf",
        transformed=True,
        use_jit=False,
    )

    expected = float(expected_traj["muhat"][0, 0])
    observed = float(np.asarray(actual.trajectory["muhat"])[0, 0])
    assert expected == 0.999
    np.testing.assert_allclose(observed, expected, rtol=RTOL, atol=ATOL)
