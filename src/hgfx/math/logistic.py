"""Compatibility implementations of ``tapas_logit`` and ``tapas_sgm``."""

from __future__ import annotations

import numpy as np


def _restore_scalar(original, value: np.ndarray):
    if np.ndim(original) == 0:
        return float(np.asarray(value))
    return value


def logit(x, upper: float = 1.0):
    """Mirror frozen HGF v8.2.0 ``tapas_logit``.

    MATLAB raises an error if any input is outside the open interval ``(0, a)``.
    HGFX preserves that compatibility behavior instead of clipping.
    """
    values = np.asarray(x, dtype=np.float64)
    a = np.float64(upper)
    if np.any(values >= a) or np.any(values <= 0):
        raise ValueError("Argument out of range.")
    out = np.log(values / (a - values))
    return _restore_scalar(x, out)


def sigmoid(x, upper: float = 1.0):
    """Mirror frozen HGF v8.2.0 ``tapas_sgm``: ``a / (1 + exp(-x))``."""
    values = np.asarray(x, dtype=np.float64)
    a = np.float64(upper)
    with np.errstate(over="ignore", invalid="ignore"):
        out = a / (1.0 + np.exp(-values))
    return _restore_scalar(x, out)


tapas_logit = logit
tapas_sgm = sigmoid
