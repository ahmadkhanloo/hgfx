"""Frozen fitModel.m Hessian, covariance, and Laplace evidence semantics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from hgfx.math.covariance import cov_to_corr
from hgfx.math.psd import nearest_psd
from hgfx.optim.ridders import RiddersOptions, ridders_hessian

from .fitting import FitProblem
from hgfx.optim.compat_quasinewton import QuasiNewtonResult


@dataclass(frozen=True)
class LMEDecomposition:
    logjoint: float
    postpredcorr: float
    freepars: float


@dataclass(frozen=True)
class FitStatistics:
    hessian: np.ndarray
    sigma: np.ndarray
    correlation: np.ndarray
    lme: float
    decomposition: LMEDecomposition
    accuracy: float
    complexity: float
    aic: float
    bic: float
    used_optimizer_hessian: bool


def _is_bad_hessian(hessian: np.ndarray) -> bool:
    h = np.asarray(hessian, dtype=np.float64)
    if np.any(np.isinf(h)) or np.any(np.isnan(h)):
        return True
    eigvals = np.linalg.eigvals(h)
    return bool(np.any(eigvals <= 0))


def finalize_laplace_statistics(
    *,
    val_min: float,
    neg_log_likelihood: float,
    numerical_hessian,
    inverse_hessian_from_optimizer,
    n_data_points: int,
) -> FitStatistics:
    """Apply frozen fitModel.m post-optimization statistics semantics."""

    h = np.asarray(numerical_hessian, dtype=np.float64).copy()
    t = np.asarray(inverse_hessian_from_optimizer, dtype=np.float64).copy()
    used_optimizer_hessian = _is_bad_hessian(h)

    if used_optimizer_hessian:
        h = np.linalg.inv(t)
        sigma = t.copy()
    else:
        sigma = np.linalg.inv(h)

    h = nearest_psd(h)
    sigma = nearest_psd(sigma)
    corr = cov_to_corr(sigma)

    d = h.shape[0]
    det_h = float(np.linalg.det(h))
    with np.errstate(divide="ignore", invalid="ignore"):
        postpredcorr = float(0.5 * np.log(1.0 / det_h))
    logjoint = -float(val_min)
    freepars = float(d / 2.0 * np.log(2.0 * np.pi))
    lme = float(logjoint + postpredcorr + freepars)

    accuracy = -float(neg_log_likelihood)
    complexity = float(accuracy - lme)
    aic = float(2.0 * neg_log_likelihood + 2.0 * d)
    bic = float(2.0 * neg_log_likelihood + d * np.log(n_data_points))

    return FitStatistics(
        hessian=h,
        sigma=sigma,
        correlation=corr,
        lme=lme,
        decomposition=LMEDecomposition(
            logjoint=logjoint,
            postpredcorr=postpredcorr,
            freepars=freepars,
        ),
        accuracy=accuracy,
        complexity=complexity,
        aic=aic,
        bic=bic,
        used_optimizer_hessian=used_optimizer_hessian,
    )


def fit_statistics(
    problem: FitProblem,
    optimizer: QuasiNewtonResult,
) -> FitStatistics:
    """Calculate the M10 fit statistics at the optimizer MAP."""

    hessian, _ = ridders_hessian(
        problem.evaluate_free,
        optimizer.arg_min,
        RiddersOptions(init_h=1.0, min_steps=10),
    )
    final = problem.evaluate_full(problem.expand(optimizer.arg_min))

    y = np.asarray(problem.responses, dtype=np.float64)
    u = np.asarray(problem.inputs, dtype=np.float64)
    if y.size:
        first = y.reshape(-1) if y.ndim == 1 else y[:, 0]
    else:
        first = u.reshape(-1) if u.ndim == 1 else u[:, 0]
    n_data_points = int(np.sum(~np.isnan(first)))

    return finalize_laplace_statistics(
        val_min=optimizer.val_min,
        neg_log_likelihood=final.neg_log_likelihood,
        numerical_hessian=hessian,
        inverse_hessian_from_optimizer=optimizer.inverse_hessian,
        n_data_points=n_data_points,
    )
