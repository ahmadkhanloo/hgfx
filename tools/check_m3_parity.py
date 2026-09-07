from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.math.boltzmann import boltzmann
from hgfx.math.covariance import cov_to_corr
from hgfx.math.lambert_w import lambert_w0
from hgfx.math.logistic import logit, sigmoid
from hgfx.math.psd import nearest_psd
from hgfx.optim.ridders import (
    RiddersOptions,
    ridders_diff,
    ridders_diff2,
    ridders_diff_cross,
    ridders_gradient,
    ridders_hessian,
)


def arr(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=np.float64)


def check(label: str, actual, expected, *, rtol: float, atol: float) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape or not np.allclose(
        a, e, rtol=rtol, atol=atol, equal_nan=True
    ):
        max_abs = (
            float(np.nanmax(np.abs(a - e)))
            if a.shape == e.shape and a.size
            else float("nan")
        )
        raise AssertionError(
            f"{label} mismatch (max_abs={max_abs})\nPython={a!r}\nMATLAB={e!r}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()
    p = json.loads(args.matlab_json.read_text(encoding="utf-8"))

    for name in ("logit", "logit_upper2"):
        case = p[name]
        check(name, logit(arr(case["x"]), case["upper"]), case["y"], rtol=1e-13, atol=1e-14)

    for name in ("sgm", "sgm_upper2"):
        case = p[name]
        check(name, sigmoid(arr(case["x"]), case["upper"]), case["y"], rtol=1e-13, atol=1e-14)

    for name in ("boltzmann", "boltzmann_beta2"):
        case = p[name]
        check(name, boltzmann(arr(case["x"]), case["beta"]), case["y"], rtol=1e-13, atol=1e-14)

    check("lambert_w0", lambert_w0(arr(p["lambert"]["x"])), p["lambert"]["y"], rtol=5e-13, atol=5e-15)
    check("cov2corr", cov_to_corr(arr(p["cov2corr"]["input"])), p["cov2corr"]["output"], rtol=1e-13, atol=1e-14)
    check("nearest_psd", nearest_psd(arr(p["nearest_psd"]["input"])), p["nearest_psd"]["output"], rtol=2e-11, atol=2e-12)

    opts = RiddersOptions(init_h=1.0, div=1.2, min_steps=5, max_steps=100, tf=2.0)
    d1, e1 = ridders_diff(np.sin, 0.37, opts)
    d2, e2 = ridders_diff2(np.exp, 0.4, opts)
    cross_fun = lambda v: float(v[0] ** 2 + 3.0 * v[0] * v[1] + 2.0 * v[1] ** 2)
    dc, ec = ridders_diff_cross(cross_fun, np.array([0.4, -0.8]), opts)

    check("ridders.first.value", d1, p["ridders"]["first"]["value"], rtol=2e-10, atol=2e-11)
    check("ridders.first.error", e1, p["ridders"]["first"]["error"], rtol=1e-5, atol=2e-14)
    check("ridders.second.value", d2, p["ridders"]["second"]["value"], rtol=2e-9, atol=2e-10)
    check("ridders.second.error", e2, p["ridders"]["second"]["error"], rtol=1e-4, atol=2e-13)
    check("ridders.cross.value", dc, p["ridders"]["cross"]["value"], rtol=2e-9, atol=2e-10)
    check("ridders.cross.error", ec, p["ridders"]["cross"]["error"], rtol=1e-4, atol=2e-13)

    a = np.array([[4.0, 1.0, -0.5], [1.0, 3.0, 0.25], [-0.5, 0.25, 2.0]])
    b = np.array([0.5, -1.0, 2.0])
    x0 = arr(p["ridders"]["quadratic"]["x"])

    def quad(v):
        return float(0.5 * v @ a @ v + b @ v + 0.7)

    g, ge = ridders_gradient(quad, x0, opts)
    h, he = ridders_hessian(quad, x0, opts)
    check("ridders.gradient", g, p["ridders"]["quadratic"]["gradient"], rtol=2e-9, atol=2e-10)
    check("ridders.hessian", h, p["ridders"]["quadratic"]["hessian"], rtol=2e-8, atol=2e-9)
    check("ridders.gradient_error", ge, p["ridders"]["quadratic"]["gradient_error"], rtol=5e-2, atol=5e-13)
    check("ridders.hessian_error", he, p["ridders"]["quadratic"]["hessian_error"], rtol=1e-1, atol=5e-11)

    print("M3 MATLAB/Python scalar numerical parity: PASS")


if __name__ == "__main__":
    main()
