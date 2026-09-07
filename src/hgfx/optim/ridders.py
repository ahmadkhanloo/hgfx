"""Ridders numerical derivatives matching frozen HGF v8.2.0 utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


ScalarFunction = Callable[[float], float]
VectorFunction = Callable[[np.ndarray], float]


@dataclass(frozen=True)
class RiddersOptions:
    init_h: float = 1.0
    div: float = 1.2
    min_steps: int = 3
    max_steps: int = 100
    tf: float = 2.0

    def __post_init__(self) -> None:
        if self.init_h <= 0:
            raise ValueError("init_h must be positive")
        if self.div <= 1:
            raise ValueError("div must be greater than one")
        if self.min_steps < 1:
            raise ValueError("min_steps must be at least one")
        if self.max_steps < 1:
            raise ValueError("max_steps must be at least one")
        if self.max_steps < self.min_steps:
            raise ValueError("max_steps must be >= min_steps")
        if self.tf <= 0:
            raise ValueError("tf must be positive")


def _ridders_extrapolate(
    base_estimate: Callable[[float], float],
    options: RiddersOptions,
) -> tuple[float, float]:
    p = np.full((options.max_steps, options.max_steps), np.nan, dtype=np.float64)
    h = float(options.init_h)
    result = float("nan")
    error = float(np.finfo(np.float64).max)

    p[0, 0] = float(base_estimate(h))

    for i in range(1, options.max_steps):
        h /= options.div
        p[i, 0] = float(base_estimate(h))

        divsq = options.div**2
        t = divsq
        for j in range(1, i + 1):
            p[i, j] = (t * p[i, j - 1] - p[i - 1, j - 1]) / (t - 1.0)
            t *= divsq

            currerr = max(
                abs(p[i, j] - p[i, j - 1]),
                abs(p[i, j] - p[i - 1, j - 1]),
            )
            if currerr < error:
                error = currerr
                result = p[i, j]

        matlab_i = i + 1
        if (
            matlab_i > options.min_steps
            and abs(p[i, i] - p[i - 1, i - 1]) > options.tf * error
        ):
            return float(result), float(error)

    return float(result), float(error)


def ridders_diff(
    function: ScalarFunction,
    x: float,
    options: RiddersOptions | None = None,
) -> tuple[float, float]:
    opts = options or RiddersOptions()
    x0 = float(x)

    def base(h: float) -> float:
        return (float(function(x0 + h)) - float(function(x0 - h))) / (2.0 * h)

    return _ridders_extrapolate(base, opts)


def ridders_diff2(
    function: ScalarFunction,
    x: float,
    options: RiddersOptions | None = None,
) -> tuple[float, float]:
    opts = options or RiddersOptions()
    x0 = float(x)

    def base(h: float) -> float:
        return (
            float(function(x0 + h))
            - 2.0 * float(function(x0))
            + float(function(x0 - h))
        ) / (h**2)

    return _ridders_extrapolate(base, opts)


def ridders_diff_cross(
    function: Callable[[np.ndarray], float],
    x,
    options: RiddersOptions | None = None,
) -> tuple[float, float]:
    opts = options or RiddersOptions()
    point = np.asarray(x, dtype=np.float64).reshape(-1)
    if point.size != 2:
        raise ValueError("cross derivative point must have two elements")

    def base(h: float) -> float:
        return (
            float(function(point + h))
            - float(function(point + np.array([h, -h], dtype=np.float64)))
            - float(function(point + np.array([-h, h], dtype=np.float64)))
            + float(function(point - h))
        ) / (4.0 * h**2)

    return _ridders_extrapolate(base, opts)


def _check_vector_function(function: VectorFunction, point: np.ndarray) -> None:
    try:
        function(point.copy())
    except Exception as exc:
        raise ValueError("Function cannot be evaluated at differentiation point.") from exc


def ridders_gradient(
    function: VectorFunction,
    x,
    options: RiddersOptions | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    opts = options or RiddersOptions()
    point = np.asarray(x, dtype=np.float64).reshape(-1)
    _check_vector_function(function, point)

    gradient = np.full(point.size, np.nan, dtype=np.float64)
    errors = np.full(point.size, np.nan, dtype=np.float64)

    for i in range(point.size):
        def restricted(value: float, index=i) -> float:
            candidate = point.copy()
            candidate[index] = value
            return float(function(candidate))

        gradient[i], errors[i] = ridders_diff(restricted, float(point[i]), opts)

    return gradient, errors


def ridders_hessian(
    function: VectorFunction,
    x,
    options: RiddersOptions | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    opts = options or RiddersOptions()
    point = np.asarray(x, dtype=np.float64).reshape(-1)
    _check_vector_function(function, point)

    n = point.size
    hessian = np.full((n, n), np.nan, dtype=np.float64)
    errors = np.full((n, n), np.nan, dtype=np.float64)

    for i in range(n):
        def restricted(value: float, index=i) -> float:
            candidate = point.copy()
            candidate[index] = value
            return float(function(candidate))

        hessian[i, i], errors[i, i] = ridders_diff2(restricted, float(point[i]), opts)

    for i in range(1, n):
        for j in range(i):
            def restricted_pair(values, ii=i, jj=j) -> float:
                candidate = point.copy()
                candidate[ii] = values[0]
                candidate[jj] = values[1]
                return float(function(candidate))

            value, error = ridders_diff_cross(
                restricted_pair,
                np.array([point[i], point[j]], dtype=np.float64),
                opts,
            )
            hessian[i, j] = value
            hessian[j, i] = value
            errors[i, j] = error
            errors[j, i] = error

    return hessian, errors


riddersdiff = ridders_diff
riddersdiff2 = ridders_diff2
riddersdiffcross = ridders_diff_cross
riddersgradient = ridders_gradient
riddershessian = ridders_hessian
