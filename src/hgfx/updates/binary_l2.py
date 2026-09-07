"""Binary HGF level-2 update (B06)."""

from __future__ import annotations

import numpy as np


def hgf_binary_level2(
    muhat_2: float,
    pihat_2: float,
    ka_1: float,
    pihat_1: float,
    da_1: float,
) -> tuple[float, float, float]:
    """Mirror frozen HGF v8.2.0 ``hgf_binary_level2.m``."""
    muhat2 = np.float64(muhat_2)
    pihat2 = np.float64(pihat_2)
    ka1 = np.float64(ka_1)
    pihat1 = np.float64(pihat_1)
    da1 = np.float64(da_1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pi2 = pihat2 + ka1**2 / pihat1
        mu2 = muhat2 + ka1 / pi2 * da1
        da2 = (
            np.float64(1.0) / pi2 + (mu2 - muhat2) ** 2
        ) * pihat2 - np.float64(1.0)
    return float(pi2), float(mu2), float(da2)
