"""HGF volatility prediction error (B09)."""

from __future__ import annotations

import numpy as np


def hgf_volatility_pe(
    pi_j: float,
    mu_j: float,
    muhat_j: float,
    pihat_j: float,
) -> float:
    """Mirror frozen HGF v8.2.0 ``hgf_volatility_pe.m``."""
    pi = np.float64(pi_j)
    mu = np.float64(mu_j)
    muhat = np.float64(muhat_j)
    pihat = np.float64(pihat_j)
    with np.errstate(divide="ignore", invalid="ignore"):
        value = (
            np.float64(1.0) / pi + (mu - muhat) ** 2
        ) * pihat - np.float64(1.0)
    return float(value)
