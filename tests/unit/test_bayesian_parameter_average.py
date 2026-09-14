import numpy as np

from hgfx.compat.bpa import _pool_gaussian_posteriors


def test_pool_gaussian_posteriors_matches_frozen_matlab_algebra():
    priormus = np.array([0.0, 1.0, 2.0])
    priorsas = np.array([1.0, 0.0, np.nan])
    transformed = [
        np.array([1.0, 1.0, 2.0]),
        np.array([3.0, 1.0, 2.0]),
    ]
    hessians = [np.array([[2.0]]), np.array([[3.0]])]

    h, sigma, corr, pooled, opt_idx = _pool_gaussian_posteriors(
        priormus, priorsas, transformed, hessians
    )

    np.testing.assert_array_equal(opt_idx, np.array([0]))
    np.testing.assert_allclose(h, np.array([[4.0]]), rtol=0.0, atol=0.0)
    np.testing.assert_allclose(sigma, np.array([[0.25]]), rtol=0.0, atol=0.0)
    np.testing.assert_allclose(corr, np.array([[1.0]]), rtol=0.0, atol=0.0)
    np.testing.assert_allclose(pooled, np.array([1.25, 1.0, 2.0]), rtol=0.0, atol=0.0)
