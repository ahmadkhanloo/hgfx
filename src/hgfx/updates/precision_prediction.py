"""Predicted-precision building blocks for the HGF (B03/B04)."""

from __future__ import annotations

import numpy as np


def hgf_pihat(
    pi_prev_j: float,
    t_k: float,
    ka_j: float,
    mu_prev_jplus1: float,
    om_j: float,
) -> float:
    """Mirror frozen HGF v8.2.0 ``hgf_pihat.m``."""
    pi_prev = np.float64(pi_prev_j)
    t = np.float64(t_k)
    ka = np.float64(ka_j)
    mu_upper = np.float64(mu_prev_jplus1)
    om = np.float64(om_j)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        value = np.float64(1.0) / (
            np.float64(1.0) / pi_prev + t * np.exp(ka * mu_upper + om)
        )
    return float(value)


def hgf_pihat_last(pi_prev_l: float, t_k: float, th: float) -> float:
    """Mirror frozen HGF v8.2.0 ``hgf_pihat_last.m``."""
    pi_prev = np.float64(pi_prev_l)
    t = np.float64(t_k)
    theta = np.float64(th)
    with np.errstate(divide="ignore", invalid="ignore"):
        value = np.float64(1.0) / (np.float64(1.0) / pi_prev + t * theta)
    return float(value)
