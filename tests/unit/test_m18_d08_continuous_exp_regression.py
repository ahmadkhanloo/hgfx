"""Regression for D08 continuous-HGF MATLAB exponential semantics."""

import numpy as np

from hgfx.models.uhgf import uhgf


def test_frozen_d08_source_first_last_level_sahat_matches_matlab_exactly() -> None:
    # Frozen failed-holdout source probe: row 38, component 1, +h=1 sample.
    # MATLAB infStates(1,2,2) == 0.1878087323857394.  The old continuous
    # transform used np.exp for log(sa_0), yielding one ULP lower sahat.
    ptrans = np.asarray(
        [
            2.0513632091020524,
            1.0,
            -9.99684722862872,
            -2.30285071564686,
            0.0,
            0.0,
            0.0,
            -12.891435536438154,
            -2.4322919100854024,
            9.338980665939264,
        ],
        dtype=np.float64,
    )

    _, inf_states = uhgf(
        np.asarray([1.0357], dtype=np.float64),
        ptrans,
        transformed=True,
    )

    assert inf_states[0, 1, 1] == np.float64(0.1878087323857394)
