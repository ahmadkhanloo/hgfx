"""Standard-HGF trajectory validity checks (B10)."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def check_hgf_trajectories(
    mu,
    pi,
    jump_tol: float,
    columns: Sequence[int] | None = None,
) -> None:
    """Mirror frozen HGF v8.2.0 ``hgf_check_trajectories.m``.

    ``columns`` uses Python zero-based indices. ``None`` or an empty
    sequence means all levels, matching MATLAB's empty-column convention.
    """
    mu_array = np.asarray(mu, dtype=np.float64)
    pi_array = np.asarray(pi, dtype=np.float64)
    if mu_array.shape != pi_array.shape or mu_array.ndim != 2:
        raise ValueError("mu and pi must be equally shaped trial-by-level matrices")

    if np.any(np.isnan(mu_array)) or np.any(np.isnan(pi_array)):
        raise ValueError(
            "Variational approximation invalid. Parameters are in a region "
            "where model assumptions are violated."
        )

    if columns is None:
        selected = np.arange(mu_array.shape[1])
    else:
        selected_values = tuple(columns)
        selected = (
            np.arange(mu_array.shape[1])
            if len(selected_values) == 0
            else np.asarray(selected_values, dtype=int)
        )

    dmu = np.diff(mu_array[:, selected], axis=0)
    dpi = np.diff(pi_array[:, selected], axis=0)
    with np.errstate(over="ignore", invalid="ignore"):
        rmdmu = np.sqrt(np.mean(dmu**2, axis=0))
        rmdpi = np.sqrt(np.mean(dpi**2, axis=0))
        bad_mu = np.any(np.abs(dmu) > np.float64(jump_tol) * rmdmu)
        bad_pi = np.any(np.abs(dpi) > np.float64(jump_tol) * rmdpi)
    if bad_mu or bad_pi:
        raise ValueError(
            "Variational approximation invalid. Parameters are in a region "
            "where model assumptions are violated."
        )


hgf_check_trajectories = check_hgf_trajectories
