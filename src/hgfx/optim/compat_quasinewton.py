"""Frozen HGF 8.2.0 BFGS quasi-Newton compatibility optimizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .ridders import RiddersOptions, ridders_gradient

Objective = Callable[[np.ndarray], float]


@dataclass(frozen=True)
class QuasiNewtonOptions:
    """Options matching quasinewton_optim_config.m."""

    tol_grad: float = 1e-3
    tol_arg: float = 1e-3
    max_step: float = 1.0
    max_iter: int = 100
    max_regu: int = 16
    max_rst: int = 10
    verbose: bool = False
    opt_iter: bool = True


@dataclass(frozen=True)
class QuasiNewtonResult:
    """Result fields exposed by the frozen MATLAB optimizer."""

    val_min: float
    arg_min: np.ndarray
    inverse_hessian: np.ndarray
    iterations: int
    resets: int
    termination: str
    iter_x: np.ndarray
    iter_val: np.ndarray
    iter_inverse_hessians: tuple[np.ndarray, ...]
    iter_resets: tuple[int, ...]


def quasinewton_optim(
    function: Objective,
    init,
    options: QuasiNewtonOptions | None = None,
) -> QuasiNewtonResult:
    """Port frozen quasinewton_optim.m as literally as practical.

    Gradient estimation is the M3-compatible Ridders implementation with
    min_steps=10, exactly as in the reference optimizer. When ``opt_iter`` is
    enabled, the MATLAB ``iter.x``, ``iter.val``, ``iter.invH`` and ``iter.rst``
    bookkeeping semantics are preserved as well; this is required both for API
    compatibility and for first-divergence diagnosis of fitting workflows.
    """

    opts = options or QuasiNewtonOptions()
    x = np.asarray(init, dtype=np.float64).reshape(-1).copy()
    init_vector = x.copy()
    n = x.size
    if n == 0:
        raise ValueError("initial point must contain at least one free parameter")

    val = float(function(x))
    if opts.opt_iter:
        iter_x = np.full((opts.max_iter + 1, n), np.nan, dtype=np.float64)
        iter_val = np.full(opts.max_iter + 1, np.nan, dtype=np.float64)
        iter_x[0, :] = x
        iter_val[0] = val
        iter_inverse_hessians: list[np.ndarray] = []
        iter_resets: list[int] = []
    else:
        iter_x = np.empty((0, n), dtype=np.float64)
        iter_val = np.empty(0, dtype=np.float64)
        iter_inverse_hessians = []
        iter_resets = []

    def set_iter_inverse_hessian(index: int, matrix: np.ndarray) -> None:
        if not opts.opt_iter:
            return
        while len(iter_inverse_hessians) <= index:
            iter_inverse_hessians.append(np.full((n, n), np.nan, dtype=np.float64))
        iter_inverse_hessians[index] = matrix.copy()

    grad_opts = RiddersOptions(min_steps=10)
    grad, _ = ridders_gradient(function, x, grad_opts)

    t_inv_hessian = np.eye(n, dtype=np.float64)
    set_iter_inverse_hessian(0, t_inv_hessian)
    descvec = -grad
    slope = float(np.dot(grad, descvec))

    resetcount = 0
    termination = "max_iter"
    iterations = 0

    for matlab_i in range(1, opts.max_iter + 1):
        iterations = matlab_i

        step_size = float(np.sqrt(np.dot(descvec, descvec)))
        if step_size > opts.max_step:
            descvec = descvec * opts.max_step / step_size

        regucount = 0
        newx = np.full_like(x, np.nan)
        newval = float("nan")
        dval = float("nan")

        for j in range(0, opts.max_regu + 1):
            regucount = j
            step_fraction = np.float64(0.5) ** j
            newx = x + step_fraction * descvec
            newval = float(function(newx))

            if np.isinf(newval):
                continue

            dval = newval - val
            if dval < 1e-4 * step_fraction * slope:
                break

        # MATLAB deliberately requires regucount < maxRegu. A candidate first
        # accepted exactly at maxRegu is therefore treated as exhausted.
        if regucount < opts.max_regu:
            dx = newx - x
            x = newx
            val = newval
            if opts.opt_iter:
                # MATLAB: iter.x(i+1,:), iter.val(i+1)
                iter_x[matlab_i, :] = x
                iter_val[matlab_i] = val
        elif resetcount < opts.max_rst:
            t_inv_hessian = np.eye(n, dtype=np.float64)
            x = x + np.float64(0.1) * (init_vector - x)
            val = float(function(x))
            if opts.opt_iter:
                # MATLAB stores reset state at i+1 and reset indices as 1-based i.
                iter_x[matlab_i, :] = x
                iter_val[matlab_i] = val
                set_iter_inverse_hessian(matlab_i, t_inv_hessian)
                iter_resets.append(matlab_i)

            grad, _ = ridders_gradient(function, x, grad_opts)
            descvec = -grad
            slope = float(np.dot(grad, descvec))
            resetcount += 1

            # Assignment i=0 in the MATLAB for-loop does not alter the loop's
            # next index; continue therefore reproduces actual runtime behavior.
            continue
        else:
            termination = "max_resets"
            break

        # MATLAB: max(abs(dx)./abs(max(x,1))) < tolArg
        step_metric = np.max(np.abs(dx) / np.abs(np.maximum(x, 1.0)))
        if step_metric < opts.tol_arg:
            termination = "tol_arg"
            if opts.opt_iter:
                # Preserve the reference's actual overwrite at index i (not i+1).
                iter_x[matlab_i - 1, :] = x
                iter_val[matlab_i - 1] = val
                set_iter_inverse_hessian(matlab_i - 1, t_inv_hessian)
            break

        oldgrad = grad
        grad, _ = ridders_gradient(function, x, grad_opts)
        dgrad = grad - oldgrad

        grad_metric = np.max(
            np.abs(grad)
            * np.maximum(np.abs(x), 1.0)
            / max(abs(val), 1.0)
        )
        if grad_metric < opts.tol_grad:
            termination = "tol_grad"
            if opts.opt_iter:
                # Preserve the reference's actual overwrite at index i (not i+1).
                iter_x[matlab_i - 1, :] = x
                iter_val[matlab_i - 1] = val
                set_iter_inverse_hessian(matlab_i - 1, t_inv_hessian)
            break

        dgdx = float(np.dot(dgrad, dx))
        curvature_threshold = float(
            np.sqrt(
                np.finfo(np.float64).eps
                * np.dot(dgrad, dgrad)
                * np.dot(dx, dx)
            )
        )
        if dgdx > curvature_threshold:
            dg_t = dgrad @ t_inv_hessian
            dg_t_dg = float(np.dot(dg_t, dgrad))
            u = dx / dgdx - dg_t / dg_t_dg
            t_inv_hessian = (
                t_inv_hessian
                + np.outer(dx, dx) / dgdx
                - np.outer(dg_t, dg_t) / dg_t_dg
                + dg_t_dg * np.outer(u, u)
            )

        descvec = -(t_inv_hessian @ grad)
        slope = float(np.dot(grad, descvec))
        set_iter_inverse_hessian(matlab_i, t_inv_hessian)

    return QuasiNewtonResult(
        val_min=float(val),
        arg_min=x.copy(),
        inverse_hessian=t_inv_hessian.copy(),
        iterations=iterations,
        resets=resetcount,
        termination=termination,
        iter_x=iter_x.copy(),
        iter_val=iter_val.copy(),
        iter_inverse_hessians=tuple(matrix.copy() for matrix in iter_inverse_hessians),
        iter_resets=tuple(iter_resets),
    )


quasinewton = quasinewton_optim
