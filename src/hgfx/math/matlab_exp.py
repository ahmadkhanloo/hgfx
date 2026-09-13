"""MATLAB-compatible binary64 exponential for frozen HGF numerics.

The HGF reference is evaluated in MATLAB.  At D02 fitting precision, platform
libm differences of one ULP in ``exp`` are amplified by Ridders finite
differences and the quasi-Newton path.  This implementation follows the
classic fdlibm binary64 range reduction and polynomial used by the reference
numerics observed in the frozen MATLAB evidence.
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
_O_THRESHOLD = 7.09782712893383973096e02
_U_THRESHOLD = -7.45133219101941108420e02
_HALF_LN2 = 0.5 * 6.93147180559945309417e-01
_ONE_AND_HALF_LN2 = 1.5 * 6.93147180559945309417e-01
_TINY = 2.0**-28


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
