"""Compatibility implementation of frozen HGF ``boltzmann.m``."""

from __future__ import annotations

import numpy as np


def boltzmann(values, beta: float):
    """Return ``exp(beta*x) / sum(exp(beta*x))`` for a vector.

    This deliberately does not apply max-subtraction in compatibility mode:
    overflow/NaN behavior is part of the frozen MATLAB numerical contract.
    """
    x = np.asarray(values, dtype=np.float64)
    beta_value = np.float64(beta)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        q = np.exp(beta_value * x)
        z = np.sum(q)
        out = q / z
    if np.ndim(values) == 0:
        return float(np.asarray(out))
    return out
