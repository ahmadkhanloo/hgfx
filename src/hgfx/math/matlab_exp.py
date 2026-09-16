"""MATLAB-compatible binary64 exponentials for frozen HGF numerics.

The HGF reference is evaluated in MATLAB. At D02 fitting precision, platform
libm differences of one ULP in ``exp``/``expm1`` are amplified by Ridders
finite differences and the quasi-Newton path. ``matlab_exp_scalar`` and the
theta-specific ``expm1`` path below use explicit fdlibm-compatible binary64
range reduction and polynomials so frozen MATLAB numerics do not depend on the
host C runtime.
"""

from __future__ import annotations

import math

import numpy as np

_LN2_HI = (6.93147180369123816490e-01, -6.93147180369123816490e-01)
_LN2_LO = (1.90821492927058770002e-10, -1.90821492927058770002e-10)
_INV_LN2 = 1.44269504088896338700e00
_P1 = 1.66666666666666019037e-01
_P2 = -2.77777777770155933842e-03
_P3 = 6.61375632143793436117e-05
_P4 = -1.65339022054652515390e-06
_P5 = 4.13813679705723846039e-08
_Q1 = -3.33333333333331316428e-02
_Q2 = 1.58730158725481460165e-03
_Q3 = -7.93650757867487942473e-05
_Q4 = 4.00821782732936239552e-06
_Q5 = -2.01099218183624371326e-07
_O_THRESHOLD = 7.09782712893383973096e02
_U_THRESHOLD = -7.45133219101941108420e02
_LN2 = 6.93147180559945309417e-01
_HALF_LN2 = 0.5 * _LN2
_ONE_AND_HALF_LN2 = 1.5 * _LN2
_TINY = 2.0**-28
_EXPM1_TINY = 2.0**-54
_EXPM1_NEG_CUTOFF = -56.0 * _LN2


def matlab_exp_scalar(value: float) -> np.float64:
    """Return ``exp(value)`` with fdlibm-compatible binary64 arithmetic."""

    x = float(np.float64(value))
    if math.isnan(x):
        return np.float64(math.nan)
    if x == math.inf:
        return np.float64(math.inf)
    if x == -math.inf:
        return np.float64(0.0)
    if x > _O_THRESHOLD:
        return np.float64(math.inf)
    if x < _U_THRESHOLD:
        return np.float64(0.0)

    ax = abs(x)
    k = 0
    hi = 0.0
    lo = 0.0

    if ax > _HALF_LN2:
        if ax < _ONE_AND_HALF_LN2:
            if x > 0.0:
                hi = x - _LN2_HI[0]
                lo = _LN2_LO[0]
                k = 1
            else:
                hi = x - _LN2_HI[1]
                lo = _LN2_LO[1]
                k = -1
        else:
            k = int(_INV_LN2 * x + (0.5 if x > 0.0 else -0.5))
            t = float(k)
            hi = x - t * _LN2_HI[0]
            lo = t * _LN2_LO[0]
        x = hi - lo
    elif ax < _TINY:
        return np.float64(1.0 + x)

    t = x * x
    c = x - t * (_P1 + t * (_P2 + t * (_P3 + t * (_P4 + t * _P5))))

    if k == 0:
        y = 1.0 - ((x * c) / (c - 2.0) - x)
    else:
        y = 1.0 - ((lo - (x * c) / (2.0 - c)) - hi)
        if k >= -1021:
            y = math.ldexp(y, k)
        else:
            # Preserve subnormal scaling without constructing 2**k directly.
            y = math.ldexp(y, k + 1000) * 2.0**-1000

    return np.float64(y)


def _matlab_expm1_scalar(value: float) -> np.float64:
    """Return ``expm1(value)`` with portable fdlibm binary64 semantics.

    The implementation mirrors the range-reduction and rational approximation
    used by the classic fdlibm algorithm, but is expressed in Python scalar
    arithmetic. This intentionally avoids ``math.expm1`` because that function
    delegates to the platform C runtime and differs by 1--2 ULP between MSVC
    and glibc at frozen D02 inputs.
    """

    x = float(np.float64(value))
    if math.isnan(x):
        return np.float64(math.nan)
    if x == math.inf:
        return np.float64(math.inf)
    if x == -math.inf:
        return np.float64(-1.0)
    if x > _O_THRESHOLD:
        return np.float64(math.inf)
    if x < _EXPM1_NEG_CUTOFF:
        return np.float64(-1.0)

    ax = abs(x)
    if ax < _EXPM1_TINY:
        return np.float64(x)

    k = 0
    correction = 0.0
    if ax > _HALF_LN2:
        if ax < _ONE_AND_HALF_LN2:
            if x > 0.0:
                hi = x - _LN2_HI[0]
                lo = _LN2_LO[0]
                k = 1
            else:
                hi = x - _LN2_HI[1]
                lo = _LN2_LO[1]
                k = -1
        else:
            k = int(_INV_LN2 * x + (0.5 if x > 0.0 else -0.5))
            t = float(k)
            hi = x - t * _LN2_HI[0]
            lo = t * _LN2_LO[0]
        x = hi - lo
        correction = (hi - x) - lo

    hfx = 0.5 * x
    hxs = x * hfx
    r1 = 1.0 + hxs * (
        _Q1 + hxs * (_Q2 + hxs * (_Q3 + hxs * (_Q4 + hxs * _Q5)))
    )
    t = 3.0 - r1 * hfx
    e = hxs * ((r1 - t) / (6.0 - x * t))

    if k == 0:
        return np.float64(x - (x * e - hxs))

    e = (x * (e - correction) - correction) - hxs
    if k == -1:
        return np.float64(0.5 * (x - e) - 0.5)
    if k == 1:
        if x < -0.25:
            return np.float64(-2.0 * (e - (x + 0.5)))
        return np.float64(1.0 + 2.0 * (x - e))

    if k <= -2 or k > 56:
        y = 1.0 - (e - x)
        return np.float64(math.ldexp(y, k) - 1.0)

    if k < 20:
        t = 1.0 - math.ldexp(1.0, -k)
        y = t - (e - x)
        return np.float64(math.ldexp(y, k))

    t = math.ldexp(1.0, -k)
    y = x - (e + t)
    y += 1.0
    return np.float64(math.ldexp(y, k))


def matlab_theta_exp_scalar(value: float) -> np.float64:
    """Reproduce frozen-MATLAB rounding for binary-HGF theta ``exp``.

    The D02 oracle exposes path-specific rounding: theta is reproduced by the
    fdlibm-compatible ``expm1(x) + 1`` path rather than by
    ``matlab_exp_scalar``. Keeping the implementation local and explicit makes
    those semantics reproducible on Windows and Linux without changing the
    frozen numerical acceptance criteria.
    """

    x = float(np.float64(value))
    return np.float64(_matlab_expm1_scalar(x) + 1.0)


def matlab_exp(values):
    """Vectorized ``matlab_exp_scalar`` preserving scalar/array shape."""

    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 0:
        return matlab_exp_scalar(float(array))

    out = np.empty(array.shape, dtype=np.float64)
    iterator = np.nditer(
        [array, out],
        flags=["refs_ok", "zerosize_ok"],
        op_flags=[["readonly"], ["writeonly"]],
    )
    for source, target in iterator:
        target[...] = matlab_exp_scalar(float(source))
    return out
