"""Principal Lambert W branch matching frozen HGF v8.2.0 ``lambert_w0.m``."""

from __future__ import annotations

import numpy as np


def _lambert_w0_scalar(value: float) -> float:
    z = np.float64(value)

    if z < 0:
        return float("nan")

    if z < 1e-10:
        return float(z)

    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        if z > 3:
            w = np.log(z) - np.log(np.log(z))
        else:
            w = np.float64(1.0)

        for _ in range(8):
            ew = np.exp(w)
            f = w * ew - z
            fp = ew * (1.0 + w)
            fpp = ew * (2.0 + w)
            w = w - (2.0 * f * fp) / (2.0 * fp * fp - f * fpp)

    return float(w)


def lambert_w0(z):
    """Evaluate the frozen HGF scalar algorithm elementwise."""
    values = np.asarray(z, dtype=np.float64)
    if values.ndim == 0:
        return _lambert_w0_scalar(float(values))

    out = np.empty_like(values, dtype=np.float64)
    for index, value in np.ndenumerate(values):
        out[index] = _lambert_w0_scalar(float(value))
    return out
