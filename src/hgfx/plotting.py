"""MATLAB-compatible fit analysis/plot surfaces.

The numerical values plotted here already live in ``fitModel``/BPA result
structures.  The preparation functions are intentionally separate from
matplotlib so parity can be validated on data rather than pixels.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def _expanded_parameter_names(parameters) -> list[str]:
    if parameters is None or not hasattr(parameters, "p"):
        raise ValueError("Result is missing MATLAB-style parameter structure")
    total = np.asarray(parameters.p).reshape(-1).size
    names: list[str] = []
    for name, value in parameters.items():
        count = np.asarray(value).size
        names.extend([str(name)] * count)
    return names[:total]


def _free_indices(prior_variances) -> np.ndarray:
    values = np.asarray(prior_variances, dtype=np.float64).reshape(-1).copy()
    values[np.isnan(values)] = 0.0
    return np.flatnonzero(values)


def prepare_fit_correlation_surface(result) -> dict[str, Any]:
    """Return the data used by MATLAB ``fit_plotCorr``."""

    if result.c_prc is None or result.c_obs is None or result.p_prc is None or result.p_obs is None:
        raise ValueError("Result lacks configuration/parameter fields required by fit_plotCorr")
    if result.optim is None or not hasattr(result.optim, "Corr") or not hasattr(result.optim, "Sigma"):
        raise ValueError("Result lacks posterior Corr/Sigma")

    prc_idx = _free_indices(result.c_prc.priorsas)
    obs_idx = _free_indices(result.c_obs.priorsas)
    prc_names = _expanded_parameter_names(result.p_prc)
    obs_names = _expanded_parameter_names(result.p_obs)
    labels = [prc_names[int(index)] for index in prc_idx] + [
        obs_names[int(index)] for index in obs_idx
    ]

    corr = np.asarray(result.optim.Corr, dtype=np.float64).copy()
    sigma = np.asarray(result.optim.Sigma, dtype=np.float64).copy()
    expected = len(labels)
    if corr.shape != (expected, expected) or sigma.shape != (expected, expected):
        raise ValueError("Posterior matrix shape does not match optimized parameter labels")
    return {"Corr": corr, "Sigma": sigma, "labels": tuple(labels)}


def prepare_residual_diagnostics(result) -> dict[str, np.ndarray]:
    """Return data used by MATLAB ``fit_plotResidualDiagnostics``."""

    if result.optim is None:
        raise ValueError("Result lacks optimizer diagnostics")
    for name in ("res", "resAC", "yhat"):
        if not hasattr(result.optim, name):
            raise ValueError(f"Result lacks optim.{name}")

    residuals = np.asarray(result.optim.res, dtype=np.float64).reshape(-1).copy()
    autocorrelation = np.asarray(result.optim.resAC, dtype=np.float64).reshape(-1)
    shifted = np.fft.fftshift(autocorrelation).copy()
    predictions = np.asarray(result.optim.yhat, dtype=np.float64).reshape(-1).copy()
    if residuals.size != predictions.size:
        raise ValueError("Residuals and predictions must have the same number of trials")

    n = shifted.size
    upper_end = n - int(math.ceil((n + 1) / 2.0))
    lower_end = upper_end - n + 1
    lags = np.arange(lower_end, upper_end + 1, dtype=np.int64)
    return {
        "res": residuals,
        "resAC_shifted": shifted,
        "lags": lags,
        "yhat": predictions,
    }


def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Plotting requires matplotlib. Install HGFX with the 'plot' extra."
        ) from exc
    return plt


def fit_plot_corr(result, *, ax=None):
    """Plot posterior parameter correlation, matching ``fit_plotCorr`` semantics."""

    plt = _pyplot()
    surface = prepare_fit_correlation_surface(result)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    image = ax.imshow(surface["Corr"], vmin=-1.0, vmax=1.0)
    positions = np.arange(len(surface["labels"]))
    ax.set_xticks(positions, surface["labels"])
    ax.set_yticks(positions, surface["labels"])
    ax.set_aspect("equal")
    ax.set_title("Parameter correlation", fontweight="bold")
    fig.colorbar(image, ax=ax)
    return fig, ax


def fit_plot_residual_diagnostics(result, *, axes=None):
    """Plot residual series, autocorrelation, and residuals vs predictions."""

    plt = _pyplot()
    data = prepare_residual_diagnostics(result)
    if axes is None:
        fig, axes = plt.subplots(3, 1)
    else:
        if len(axes) != 3:
            raise ValueError("axes must contain exactly three matplotlib axes")
        fig = axes[0].figure

    n = data["res"].size
    axes[0].plot(np.arange(1, n + 1), data["res"])
    if n:
        axes[0].set_xlim(1, n)
    axes[0].set_xlabel("Trial number")
    axes[0].set_ylabel("Residuals")
    axes[0].set_title("Time series of Residuals")

    axes[1].plot(data["lags"], data["resAC_shifted"])
    if data["lags"].size:
        axes[1].set_xlim(int(data["lags"][0]), int(data["lags"][-1]))
    axes[1].set_ylim(-1, 1)
    axes[1].set_xlabel("Lag")
    axes[1].set_ylabel("Coefficient")
    axes[1].set_title("Autocorrelation of Residuals")

    axes[2].plot(data["yhat"], data["res"], ".")
    finite = data["yhat"][np.isfinite(data["yhat"])]
    if finite.size:
        low = float(np.min(finite))
        high = float(np.max(finite))
        span = high - low
        padding = 0.05 * span if span > 0 else max(abs(low), 1.0) * 0.05
        axes[2].set_xlim(low - padding, high + padding)
    axes[2].set_xlabel("Predictions")
    axes[2].set_ylabel("Residuals")
    axes[2].set_title("Residuals against Predictions")
    return fig, axes


# MATLAB-compatible spellings used by the frozen demo documentation.
fit_plotCorr = fit_plot_corr
fit_plotResidualDiagnostics = fit_plot_residual_diagnostics

__all__ = [
    "prepare_fit_correlation_surface",
    "prepare_residual_diagnostics",
    "fit_plot_corr",
    "fit_plot_residual_diagnostics",
    "fit_plotCorr",
    "fit_plotResidualDiagnostics",
]
