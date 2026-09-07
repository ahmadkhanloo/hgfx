"""Continuous HGF level-1 update (B07)."""

from __future__ import annotations

import numpy as np


def hgf_continuous_level1(
    u_k: float,
    muhat_1: float,
    pihat_1: float,
    al: float,
) -> tuple[float, float, float, float]:
    """Mirror frozen HGF v8.2.0 ``hgf_continuous_level1.m``."""
    u = np.float64(u_k)
    muhat1 = np.float64(muhat_1)
    pihat1 = np.float64(pihat_1)
    alpha = np.float64(al)
    with np.errstate(divide="ignore", invalid="ignore"):
        dau = u - muhat1
        pi1 = pihat1 + np.float64(1.0) / alpha
        mu1 = (
            muhat1
            + np.float64(1.0)
            / pihat1
            * np.float64(1.0)
            / (np.float64(1.0) / pihat1 + alpha)
            * dau
        )
        da1 = (
            np.float64(1.0) / pi1 + (mu1 - muhat1) ** 2
        ) * pihat1 - np.float64(1.0)
    return float(pi1), float(mu1), float(dau), float(da1)
