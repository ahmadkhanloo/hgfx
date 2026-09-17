"""Opt-in L-BFGS MAP solver.

Default ``hgfx.fit_model`` is unchanged. Use ``minimize_map`` when the
scientific target is a tighter MAP than the frozen MATLAB quasi-Newton.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

from .interface import (
    GradientKind,
    Jacobian,
    MapOptions,
    MapResult,
    MapStartResult,
    Objective,
    Termination,
)
from .ridders import RiddersOptions, ridders_gradient


def _as_vector(x) -> np.ndarray:
    vector = np.asarray(x, dtype=np.float64).reshape(-1)
    if vector.size == 0:
        raise ValueError("initial point must contain at least one free parameter")
    return vector


def _finite_gradient(function: Objective, x: np.ndarray, step: float) -> np.ndarray:
    grad = np.empty_like(x)
    for index in range(x.size):
        plus = x.copy()
        minus = x.copy()
        plus[index] += step
        minus[index] -= step
        grad[index] = (float(function(plus)) - float(function(minus))) / (2.0 * step)
    return grad


def _ridders_gradient(function: Objective, x: np.ndarray) -> np.ndarray:
    grad, _ = ridders_gradient(function, x, RiddersOptions(min_steps=10))
    return np.asarray(grad, dtype=np.float64).reshape(-1)


def _jax_value_and_grad(function: Objective) -> Callable[[np.ndarray], tuple[float, np.ndarray]]:
    import jax
    import jax.numpy as jnp

    jax.config.update("jax_enable_x64", True)

    def jax_fun(x):
        return function(x)

    value_and_grad = jax.jit(jax.value_and_grad(jax_fun))

    def wrapped(x: np.ndarray) -> tuple[float, np.ndarray]:
        value, grad = value_and_grad(jnp.asarray(x, dtype=jnp.float64))
        return float(value), np.asarray(grad, dtype=np.float64).reshape(-1)

    return wrapped


def _make_evaluators(
    function: Objective,
    *,
    jac: Jacobian | None,
    gradient: GradientKind,
    finite_step: float,
) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray], str]:
    if jac is not None:
        def value(x: np.ndarray) -> float:
            return float(function(x))

        def grad(x: np.ndarray) -> np.ndarray:
            return np.asarray(jac(x), dtype=np.float64).reshape(-1)

        return value, grad, "user"

    if gradient == "jax":
        jax_vg = _jax_value_and_grad(function)

        def value(x: np.ndarray) -> float:
            return jax_vg(x)[0]

        def grad(x: np.ndarray) -> np.ndarray:
            return jax_vg(x)[1]

        return value, grad, "jax"

    if gradient == "ridders":
        def value(x: np.ndarray) -> float:
            return float(function(x))

        def grad(x: np.ndarray) -> np.ndarray:
            return _ridders_gradient(function, x)

        return value, grad, "ridders"

    if gradient != "finite":
        raise ValueError("gradient must be 'finite', 'ridders', or 'jax'")

    def value(x: np.ndarray) -> float:
        return float(function(x))

    def grad(x: np.ndarray) -> np.ndarray:
        return _finite_gradient(function, x, finite_step)

    return value, grad, "finite"


def _wolfe_line_search(
    value,
    grad,
    x: np.ndarray,
    f: float,
    g: np.ndarray,
    direction: np.ndarray,
    *,
    max_ls: int,
) -> tuple[np.ndarray, float, np.ndarray, int, bool]:
    c1 = 1e-4
    c2 = 0.9
    slope = float(np.dot(g, direction))
    if slope >= 0.0:
        return x, f, g, 0, False

    step = 1.0
    nfev = 0
    for _ in range(max_ls):
        candidate = x + step * direction
        f_new = value(candidate)
        nfev += 1
        if not np.isfinite(f_new):
            step *= 0.5
            continue
        if f_new > f + c1 * step * slope:
            step *= 0.5
            continue
        g_new = grad(candidate)
        nfev += 1
        if float(np.dot(g_new, direction)) < c2 * slope:
            step *= 2.0
            if step > 8.0:
                return candidate, f_new, g_new, nfev, True
            continue
        return candidate, f_new, g_new, nfev, True
    return x, f, g, nfev, False


def _two_loop_direction(
    grad: np.ndarray,
    s_hist: list[np.ndarray],
    y_hist: list[np.ndarray],
    rho_hist: list[float],
) -> np.ndarray:
    q = grad.copy()
    alphas: list[float] = []
    for s, y, rho in zip(reversed(s_hist), reversed(y_hist), reversed(rho_hist)):
        alpha = rho * float(np.dot(s, q))
        q = q - alpha * y
        alphas.append(alpha)
    if y_hist:
        ys = float(np.dot(y_hist[-1], s_hist[-1]))
        yy = float(np.dot(y_hist[-1], y_hist[-1]))
        scale = ys / yy if yy > 0.0 else 1.0
    else:
        scale = 1.0
    r = scale * q
    for s, y, rho, alpha in zip(s_hist, y_hist, rho_hist, reversed(alphas)):
        beta = rho * float(np.dot(y, r))
        r = r + s * (alpha - beta)
    return -r


def _minimize_one(
    value,
    grad,
    x0: np.ndarray,
    options: MapOptions,
) -> MapStartResult:
    x = x0.copy()
    f = value(x)
    nfev = 1
    njev = 0
    if not np.isfinite(f):
        return MapStartResult(
            x=x,
            fun=f,
            nit=0,
            nfev=nfev,
            njev=njev,
            termination="unstable",
            grad_norm=float("nan"),
        )
    g = grad(x)
    njev += 1
    s_hist: list[np.ndarray] = []
    y_hist: list[np.ndarray] = []
    rho_hist: list[float] = []

    for iteration in range(1, options.maxiter + 1):
        grad_norm = float(np.linalg.norm(g, ord=np.inf))
        if grad_norm < options.gtol:
            return MapStartResult(x, f, iteration, nfev, njev, "gtol", grad_norm)

        direction = _two_loop_direction(g, s_hist, y_hist, rho_hist)
        x_new, f_new, g_new, ls_evals, accepted = _wolfe_line_search(
            value, grad, x, f, g, direction, max_ls=options.max_ls
        )
        nfev += ls_evals
        njev += 1 if accepted else 0
        if not accepted:
            return MapStartResult(x, f, iteration, nfev, njev, "line_search", grad_norm)

        s = x_new - x
        y = g_new - g
        ys = float(np.dot(y, s))
        if ys > 1e-16:
            if len(s_hist) == options.history:
                s_hist.pop(0)
                y_hist.pop(0)
                rho_hist.pop(0)
            s_hist.append(s)
            y_hist.append(y)
            rho_hist.append(1.0 / ys)

        if abs(f - f_new) < options.ftol * max(1.0, abs(f)):
            return MapStartResult(
                x_new,
                f_new,
                iteration,
                nfev,
                njev,
                "ftol",
                float(np.linalg.norm(g_new, ord=np.inf)),
            )

        x, f, g = x_new, f_new, g_new

    return MapStartResult(
        x, f, options.maxiter, nfev, njev, "maxiter", float(np.linalg.norm(g, ord=np.inf))
    )


def _start_set(
    x0: np.ndarray,
    extra: Sequence[Sequence[float]] | np.ndarray | None,
    n_random: int,
    jitter: float,
    seed: int,
) -> list[np.ndarray]:
    starts = [x0.copy()]
    if extra is not None:
        extra_array = np.asarray(extra, dtype=np.float64)
        if extra_array.size:
            extra_array = extra_array.reshape(-1, x0.size)
            starts.extend(row.copy() for row in extra_array)
    if n_random > 0:
        rng = np.random.default_rng(seed)
        scale = np.maximum(np.abs(x0), 1.0)
        for _ in range(n_random):
            starts.append(x0 + jitter * scale * rng.standard_normal(x0.size))
    return starts


def minimize_map(
    function: Objective,
    x0,
    *,
    jac: Jacobian | None = None,
    starts: Sequence[Sequence[float]] | np.ndarray | None = None,
    n_random_starts: int = 0,
    options: MapOptions | None = None,
) -> MapResult:
    """Minimize a scalar objective with multi-start L-BFGS.

    The callable must return the quantity to minimize, typically the transformed
    negative log-joint used by TAPAS/HGFX. This solver is opt-in and must not be
    used as evidence that ``fit_model`` changed.
    """

    opts = options or MapOptions()
    x_init = _as_vector(x0)
    value, grad, kind = _make_evaluators(
        function,
        jac=jac,
        gradient=opts.gradient,
        finite_step=opts.finite_step,
    )
    candidates = _start_set(
        x_init, starts, n_random_starts, opts.jitter, opts.seed
    )
    results = [_minimize_one(value, grad, start, opts) for start in candidates]
    finite = [item for item in results if np.isfinite(item.fun)]
    best = min(finite, key=lambda item: item.fun) if finite else results[0]
    return MapResult(
        x=best.x.copy(),
        fun=float(best.fun),
        nit=best.nit,
        nfev=sum(item.nfev for item in results),
        njev=sum(item.njev for item in results),
        termination=best.termination,
        grad_norm=best.grad_norm,
        gradient_kind=kind,
        n_starts=len(results),
        starts=tuple(results),
    )
