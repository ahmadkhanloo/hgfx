from __future__ import annotations

import math

import numpy as np
import pytest

from hgfx.math.boltzmann import boltzmann
from hgfx.math.covariance import cov_to_corr
from hgfx.math.lambert_w import lambert_w0
from hgfx.math.logistic import logit, sigmoid
from hgfx.math.psd import nearest_psd
from hgfx.optim.ridders import (
    RiddersOptions,
    ridders_diff,
    ridders_diff2,
    ridders_diff_cross,
    ridders_gradient,
    ridders_hessian,
)


def test_logit_matches_reference_formula_and_domain_errors() -> None:
    x = np.array([0.1, 0.2, 0.5, 0.8, 0.9], dtype=np.float64)
    expected = np.log(x / (1.0 - x))
    np.testing.assert_allclose(logit(x, 1.0), expected, rtol=0, atol=0)

    with pytest.raises(ValueError, match="out of range"):
        logit(np.array([0.0, 0.5]), 1.0)
    with pytest.raises(ValueError, match="out of range"):
        logit(np.array([0.5, 1.0]), 1.0)


def test_sigmoid_matches_reference_formula() -> None:
    x = np.array([-12.0, -2.0, 0.0, 2.0, 12.0])
    expected = 2.0 / (1.0 + np.exp(-x))
    np.testing.assert_allclose(sigmoid(x, 2.0), expected, rtol=0, atol=0)


def test_boltzmann_matches_reference_formula_with_beta() -> None:
    x = np.array([-2.0, 0.0, 1.0, 3.0])
    beta = 0.7
    q = np.exp(beta * x)
    expected = q / np.sum(q)
    np.testing.assert_allclose(boltzmann(x, beta), expected, rtol=0, atol=0)


def test_lambert_w0_reference_branches_and_definition() -> None:
    assert math.isnan(lambert_w0(-1.0))
    assert lambert_w0(0.0) == 0.0
    assert lambert_w0(1e-12) == 1e-12

    z = np.array([1e-10, 1e-6, 0.1, 1.0, 3.0, 3.1, math.e, 10.0, 1e3])
    w = lambert_w0(z)
    np.testing.assert_allclose(w * np.exp(w), z, rtol=5e-13, atol=5e-15)


def test_cov_to_corr_and_reference_validation() -> None:
    cov = np.array([[4.0, 1.0, -2.0], [1.0, 9.0, 3.0], [-2.0, 3.0, 16.0]])
    corr = cov_to_corr(cov)
    sdev = np.sqrt(np.diag(cov))
    np.testing.assert_allclose(corr, cov / np.outer(sdev, sdev), rtol=0, atol=0)

    with pytest.raises(ValueError, match="not symmetric"):
        cov_to_corr(np.array([[1.0, 2.0], [0.0, 1.0]]))
    with pytest.raises(ValueError, match="positive semi-definite"):
        cov_to_corr(np.array([[1.0, 2.0], [2.0, 1.0]]))
    with pytest.raises(ValueError, match="not symmetric"):
        cov_to_corr(np.array([[1.0, np.nan], [np.nan, 1.0]]))


def test_nearest_psd_is_symmetric_and_psd() -> None:
    matrix = np.array([[1.0, 2.0, 0.0], [2.0, 1.0, 0.5], [0.0, 0.5, -0.2]])
    projected = nearest_psd(matrix)
    np.testing.assert_allclose(projected, projected.T, rtol=0, atol=1e-15)
    assert np.min(np.linalg.eigvalsh(projected)) >= 0.0


def test_ridders_scalar_and_cross_derivatives() -> None:
    opts = RiddersOptions(init_h=1.0, div=1.2, min_steps=5, max_steps=100, tf=2.0)
    d1, e1 = ridders_diff(math.sin, 0.37, opts)
    d2, e2 = ridders_diff2(math.exp, 0.4, opts)

    def cross(v):
        return float(v[0] ** 2 + 3.0 * v[0] * v[1] + 2.0 * v[1] ** 2)

    dc, ec = ridders_diff_cross(cross, np.array([0.4, -0.8]), opts)
    np.testing.assert_allclose(d1, math.cos(0.37), rtol=1e-10, atol=1e-11)
    np.testing.assert_allclose(d2, math.exp(0.4), rtol=1e-9, atol=1e-10)
    np.testing.assert_allclose(dc, 3.0, rtol=1e-10, atol=1e-10)
    assert e1 >= 0
    assert e2 >= 0
    assert ec >= 0


def test_ridders_gradient_and_hessian_of_quadratic() -> None:
    a = np.array([[4.0, 1.0, -0.5], [1.0, 3.0, 0.25], [-0.5, 0.25, 2.0]])
    b = np.array([0.5, -1.0, 2.0])
    x = np.array([0.3, -0.7, 1.2])

    def f(v):
        return float(0.5 * v @ a @ v + b @ v + 0.7)

    opts = RiddersOptions(min_steps=5)
    grad, grad_err = ridders_gradient(f, x, opts)
    hess, hess_err = ridders_hessian(f, x, opts)
    np.testing.assert_allclose(grad, a @ x + b, rtol=1e-9, atol=1e-10)
    np.testing.assert_allclose(hess, a, rtol=1e-8, atol=1e-9)
    assert np.all(grad_err >= 0)
    assert np.all(hess_err >= 0)


def test_ridders_options_match_reference_defaults_and_validation() -> None:
    assert RiddersOptions() == RiddersOptions(1.0, 1.2, 3, 100, 2.0)
    with pytest.raises(ValueError):
        RiddersOptions(div=1.0)
