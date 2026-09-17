from __future__ import annotations

import numpy as np

from hgfx.optim import MapOptions, minimize_map, multi_start_map


def _quadratic(x) -> float:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    return float((x[0] - 2.0) ** 2 + 3.0 * (x[1] + 1.0) ** 2)


def _quadratic_jac(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    return np.array([2.0 * (x[0] - 2.0), 6.0 * (x[1] + 1.0)], dtype=np.float64)


def test_minimize_map_recovers_quadratic_with_user_jacobian() -> None:
    result = minimize_map(
        _quadratic,
        np.array([0.0, 0.0]),
        jac=_quadratic_jac,
        options=MapOptions(gtol=1e-8, maxiter=50),
    )
    assert result.gradient_kind == "user"
    assert result.success
    np.testing.assert_allclose(result.x, np.array([2.0, -1.0]), atol=1e-6)
    assert result.fun < 1e-12


def test_minimize_map_finite_difference_recovers_quadratic() -> None:
    result = minimize_map(
        _quadratic,
        np.array([-3.0, 4.0]),
        options=MapOptions(gradient="finite", gtol=1e-6, maxiter=80),
    )
    assert result.gradient_kind == "finite"
    np.testing.assert_allclose(result.x, np.array([2.0, -1.0]), atol=1e-4)


def test_multi_start_selects_better_basin() -> None:
    def two_basin(x) -> float:
        z = float(np.asarray(x, dtype=np.float64).reshape(-1)[0])
        return min((z - 4.0) ** 2 + 0.2, (z + 1.0) ** 2 + 1.0)

    result = multi_start_map(
        two_basin,
        np.array([-1.0]),
        starts=[[4.0]],
        n_random_starts=0,
        options=MapOptions(gtol=1e-8, maxiter=40),
    )
    assert result.n_starts == 2
    assert result.fun < 0.25
    np.testing.assert_allclose(result.x, np.array([4.0]), atol=1e-4)
