"""Portable MATLAB-compatible binary64 natural logarithm.

The frozen D02 oracle is sensitive to one-ULP differences in ``log``. Python's
``math.log`` and NumPy's vectorized ``log`` ultimately depend on platform math
libraries and can therefore disagree between glibc and the Windows CRT. This
module ports the classic fdlibm binary64 logarithm using only IEEE-754 bit
manipulation and elementary arithmetic so the compatibility path is independent
of the host libm implementation.

fdlibm provenance
-----------------
The logarithm algorithm is adapted from fdlibm ``e_log.c``. The upstream
notice is preserved here as required:

Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
Developed at SunSoft, a Sun Microsystems, Inc. business.
Permission to use, copy, modify, and distribute this software is freely
granted, provided that this notice is preserved.
"""

from __future__ import annotations

import struct

import numpy as np

_LN2_HI = 6.93147180369123816490e-01
_LN2_LO = 1.90821492927058770002e-10
_TWO54 = 1.80143985094819840000e16
_LG1 = 6.666666666666735130e-01
_LG2 = 3.999999999940941908e-01
_LG3 = 2.857142874366239149e-01
_LG4 = 2.222219843214978396e-01
_LG5 = 1.818357216161805012e-01
_LG6 = 1.531383769920937332e-01
_LG7 = 1.479819860511658591e-01


def _words(value: float) -> tuple[int, int]:
    bits = struct.unpack(">Q", struct.pack(">d", value))[0]
    return (bits >> 32) & 0xFFFFFFFF, bits & 0xFFFFFFFF


def _set_high_word(value: float, high: int) -> float:
    bits = struct.unpack(">Q", struct.pack(">d", value))[0]
    bits = ((high & 0xFFFFFFFF) << 32) | (bits & 0xFFFFFFFF)
    return struct.unpack(">d", struct.pack(">Q", bits))[0]


def matlab_log_scalar(value: float) -> np.float64:
    """Return ``log(value)`` with fdlibm-compatible binary64 arithmetic."""

    x = float(np.float64(value))
    # Python exposes the IEEE high word as an unsigned integer below, unlike
    # fdlibm's signed C ``int``. Handle both +0.0 and -0.0 explicitly so the
    # original fdlibm special-case semantics remain intact.
    if x == 0.0:
        return np.float64(-np.inf)

    hx, lx = _words(x)
    k = 0

    # Positive subnormal values are normalized before the main reduction.
    if hx < 0x00100000:
        k -= 54
        x *= _TWO54
        hx, _ = _words(x)

    # Negative inputs map to NaN, matching IEEE log semantics.
    if hx & 0x80000000:
        return np.float64(np.nan)
    if hx >= 0x7FF00000:
        return np.float64(x + x)

    k += (hx >> 20) - 1023
    hx &= 0x000FFFFF
    i = (hx + 0x95F64) & 0x100000
    x = _set_high_word(x, hx | (i ^ 0x3FF00000))
    k += i >> 20
    f = x - 1.0

    if (0x000FFFFF & (2 + hx)) < 3:
        if f == 0.0:
            if k == 0:
                return np.float64(0.0)
            dk = float(k)
            return np.float64(dk * _LN2_HI + dk * _LN2_LO)
        r = f * f * (0.5 - 0.33333333333333333 * f)
        if k == 0:
            return np.float64(f - r)
        dk = float(k)
        return np.float64(dk * _LN2_HI - ((r - dk * _LN2_LO) - f))

    s = f / (2.0 + f)
    dk = float(k)
    z = s * s
    i = hx - 0x6147A
    w = z * z
    j = 0x6B851 - hx
    t1 = w * (_LG2 + w * (_LG4 + w * _LG6))
    t2 = z * (_LG1 + w * (_LG3 + w * (_LG5 + w * _LG7)))
    i |= j
    r = t2 + t1

    if i > 0:
        hfsq = 0.5 * f * f
        if k == 0:
            return np.float64(f - (hfsq - s * (hfsq + r)))
        return np.float64(
            dk * _LN2_HI - ((hfsq - (s * (hfsq + r) + dk * _LN2_LO)) - f)
        )

    if k == 0:
        return np.float64(f - s * (f - r))
    return np.float64(dk * _LN2_HI - ((s * (f - r) - dk * _LN2_LO) - f))
