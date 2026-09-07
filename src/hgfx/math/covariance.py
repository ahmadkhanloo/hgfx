"""Covariance/correlation compatibility utilities."""

from __future__ import annotations

import numpy as np


def cov_to_corr(covariance):
    """Mirror frozen HGF v8.2.0 ``tapas_Cov2Corr``."""
    cov = np.asarray(covariance, dtype=np.float64)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError("Input matrix must be square.")

    if np.any(cov.T != cov):
        raise ValueError("Input matrix is not symmetric.")

    if np.any(np.isinf(cov)) or np.any(np.isnan(cov)):
        raise ValueError("Input matrix is not positive semi-definite.")

    eigenvalues = np.linalg.eigvalsh(cov)
    if np.any(eigenvalues < 0):
        raise ValueError("Input matrix is not positive semi-definite.")

    sdev = np.sqrt(np.diag(cov))
    norm = np.outer(sdev, sdev)
    with np.errstate(divide="ignore", invalid="ignore"):
        return cov / norm


tapas_cov2corr = cov_to_corr
