"""Unit-square sigmoid observation families."""
from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from hgfx.math.matlab_exp import matlab_exp, matlab_exp_scalar
from .base import ignored_mask, output_arrays, response_vector


def _scalar_log(values: np.ndarray) -> np.ndarray:
    """Evaluate the active MATLAB-compatible log path elementwise.

    The frozen D02 oracle exposes a one-ULP difference between NumPy's
    vectorized ``log`` path and the scalar libm path at values that feed
    Ridders finite differences. Preserve NumPy handling for non-positive or
    non-finite values, while using scalar ``math.log`` for ordinary positive
    finite values. Boundary-sensitive fallbacks are still applied by
    ``_core`` exactly where they were before this helper was introduced.
    """

    array = np.asarray(values, dtype=np.float64)
    out = np.empty_like(array)
    source = array.reshape(-1)
    target = out.reshape(-1)
    for index, value in enumerate(source):
        scalar = float(value)
        if scalar > 0.0 and math.isfinite(scalar):
            target[index] = math.log(scalar)
        else:
            with np.errstate(divide="ignore", invalid="ignore"):
                target[index] = np.log(value)
    return out


def _core(responses, x, ze, *, irregular_trials):
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    n = x.size
    y = response_vector(responses, n)
    reg = ~ignored_mask(n, irregular_trials)
    logp, yhat, res = output_arrays(n)
    xr = x[reg]
    yr = y[reg]
    zr = np.asarray(ze, dtype=np.float64)
    if zr.ndim == 0:
        zr = np.full(xr.shape, zr, dtype=np.float64)
    else:
        zr = zr.reshape(-1)[reg]
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        # MATLAB evaluates the ordinary log path elementwise. NumPy's
        # vector-log implementation can differ by one ULP on the D02 frozen
        # oracle and that perturbation is amplified by Ridders gradients.
        logx = _scalar_log(xr)
        alt = np.log1p(xr - 1.0)
        m = (1.0 - xr) < 1e-4
        logx[m] = alt[m]

        log1mx = _scalar_log(np.float64(1.0) - xr)
        alt2 = np.log1p(-xr)
        m2 = xr < 1e-4
        log1mx[m2] = alt2[m2]

        normalizer = (1.0 - xr) ** zr + xr**zr
        logp[reg] = (
            yr * zr * (logx - log1mx)
            + zr * log1mx
            - _scalar_log(normalizer)
        )
        yhat[reg] = xr
        res[reg] = (yr - xr) / np.sqrt(xr * (1.0 - xr))
    return logp, yhat, res


def unitsq_sgm(
    responses,
    inf_states,
    ptrans,
    *,
    irregular_trials: Sequence[int] | None = None,
    predorpost: int = 1,
):
    s = np.asarray(inf_states, dtype=np.float64)
    pop = 0 if predorpost == 1 else 2
    ze = matlab_exp_scalar(np.asarray(ptrans, dtype=np.float64).reshape(-1)[0])
    return _core(responses, s[:, 0, pop], ze, irregular_trials=irregular_trials)


def unitsq_sgm_mu3(
    responses,
    inf_states,
    ptrans=None,
    *,
    irregular_trials: Sequence[int] | None = None,
):
    s = np.asarray(inf_states, dtype=np.float64)
    return _core(
        responses,
        s[:, 0, 0],
        matlab_exp(-s[:, 2, 0]),
        irregular_trials=irregular_trials,
    )
