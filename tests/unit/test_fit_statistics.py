from __future__ import annotations

import numpy as np

from hgfx.compat.fit_statistics import finalize_laplace_statistics
from hgfx.compat.fitting import (
    fit_hgf_binary_unitsq_compat,
    hgf_binary_unitsq_fit_problem,
)
from hgfx.compat.fit_statistics import fit_statistics


def fixture_data() -> tuple[np.ndarray, np.ndarray]:
    inputs = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    responses = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    return responses, inputs


def test_laplace_direct_hessian_branch() -> None:
    h = np.array([[3.0, 0.25], [0.25, 1.5]], dtype=np.float64)
    t = np.eye(2, dtype=np.float64)
    stats = finalize_laplace_statistics(
        val_min=11.0,
        neg_log_likelihood=8.0,
        numerical_hessian=h,
        inverse_hessian_from_optimizer=t,
        n_data_points=24,
    )
    assert not stats.used_optimizer_hessian
    np.testing.assert_allclose(stats.sigma, np.linalg.inv(h))
    np.testing.assert_allclose(np.diag(stats.correlation), np.ones(2))
    assert np.isclose(stats.accuracy - stats.complexity, stats.lme)


def test_laplace_falls_back_to_optimizer_inverse_hessian() -> None:
    bad = np.array([[1.0, 0.0], [0.0, -0.25]], dtype=np.float64)
    t = np.array([[0.5, 0.02], [0.02, 0.25]], dtype=np.float64)
    stats = finalize_laplace_statistics(
        val_min=5.0,
        neg_log_likelihood=4.0,
        numerical_hessian=bad,
        inverse_hessian_from_optimizer=t,
        n_data_points=20,
    )
    assert stats.used_optimizer_hessian
    np.testing.assert_allclose(stats.sigma, t)
    np.testing.assert_allclose(stats.hessian, np.linalg.inv(t))


def test_end_to_end_statistics_are_finite() -> None:
    responses, inputs = fixture_data()
    fit = fit_hgf_binary_unitsq_compat(responses, inputs)
    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    stats = fit_statistics(problem, fit.optimizer)

    assert np.isfinite(stats.hessian).all()
    assert np.isfinite(stats.sigma).all()
    assert np.isfinite(stats.correlation).all()
    assert np.isfinite(stats.lme)
    assert np.isfinite(stats.aic)
    assert np.isfinite(stats.bic)
    assert np.isclose(stats.accuracy - stats.complexity, stats.lme)
