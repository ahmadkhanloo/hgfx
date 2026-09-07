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


def quasinewton_optim(
    function: Objective,
    init,
    options: QuasiNewtonOptions | None = None,
) -> QuasiNewtonResult:
    """Port frozen quasinewton_optim.m as literally as practical.

    Gradient estimation is the M3-compatible Ridders implementation with
    min_steps=10, exactly as in the reference optimizer.
    """

    opts = options or QuasiNewtonOptions()
    x = np.asarray(init, dtype=np.float64).reshape(-1).copy()
    n = x.size
    if n == 0:
        raise ValueError("initial point must contain at least one free parameter")

    val = float(function(x))
    grad_opts = RiddersOptions(min_steps=10)
    grad, _ = ridders_gradient(function, x, grad_opts)

    t_inv_hessian = np.eye(n, dtype=np.float64)
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
        elif resetcount < opts.max_rst:
            t_inv_hessian = np.eye(n, dtype=np.float64)
            x = x + np.float64(0.1) * (np.asarray(init, dtype=np.float64).reshape(-1) - x)
            val = float(function(x))

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

    return QuasiNewtonResult(
        val_min=float(val),
        arg_min=x.copy(),
        inverse_hessian=t_inv_hessian.copy(),
        iterations=iterations,
        resets=resetcount,
        termination=termination,
    )


quasinewton = quasinewton_optim
