"""Frozen tapas_autocorr.m: circular FFT correlation, population variance."""

import numpy as np


def tapas_autocorr(values):
    x = np.asarray(values, dtype=np.float64)
    if x.ndim not in (1, 2) or x.shape[0] == 0:
        raise ValueError("Expected nonempty time series or column matrix")
    x = x - np.mean(x, axis=0)
    f = np.fft.fft(x, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.fft.ifft(f * np.conj(f), axis=0).real / x.shape[0] / np.var(x, axis=0)


def residual_autocorrelation(residuals):
    res = np.asarray(residuals, dtype=np.float64).copy()
    res[np.isnan(res)] = 0.0
    return tapas_autocorr(res)
