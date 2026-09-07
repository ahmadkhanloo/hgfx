"""One-step HGF mean prediction (B02)."""

from __future__ import annotations

import numpy as np


def hgf_prediction(
    mu_prev_j: float,
    t_k: float,
    *,
    rho: float = 0.0,
    phi: float = 0.0,
    m: float = 0.0,
) -> float:
    """Mirror frozen HGF v8.2.0 ``hgf_prediction.m``."""
    mu_prev = np.float64(mu_prev_j)
    t = np.float64(t_k)
    rho_j = np.float64(rho)
    phi_j = np.float64(phi)
    m_j = np.float64(m)
    return float(mu_prev + t * rho_j + t * phi_j * (m_j - mu_prev))


prediction = hgf_prediction
