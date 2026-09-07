"""Projection to a positive-semidefinite matrix matching ``nearest_psd.m``."""

from __future__ import annotations

import numpy as np


def nearest_psd(matrix):
    """Mirror frozen HGF v8.2.0 ``nearest_psd``."""
    value = np.asarray(matrix, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("matrix must be square")

    x = (value.T + value) / 2.0
    iterations = 0
    while np.any(np.linalg.eigvalsh(x) < 0):
        eigenvalues, eigenvectors = np.linalg.eigh(x)
        eigenvalues = np.maximum(0.0, eigenvalues)
        x = (eigenvectors * eigenvalues) @ eigenvectors.T
        x = (x.T + x) / 2.0
        iterations += 1
        if iterations > 1000:
            raise RuntimeError("nearest_psd did not converge")
    return x
