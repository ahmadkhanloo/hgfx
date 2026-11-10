"""REV-2.2 additive optimizer-stop reporting; unit scope, NOT MATLAB fit parity."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import hgfx

from hgfx.compat.fit import _optimizer_converged
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


def optimizer_stub(reason: str, *, val: float = 3.5, x=(0.1, -0.3)):
    return SimpleNamespace(
        termination=reason,
        val_min=val,
        arg_min=np.array(x, dtype=np.float64),
    )


def test_both_documented_solver_tolerance_stops_require_finite_values():
    assert _optimizer_converged(optimizer_stub("tol_grad")) is True
    assert _optimizer_converged(optimizer_stub("tol_arg")) is True
    assert _optimizer_converged(optimizer_stub("tol_grad", val=float("nan"))) is False
    assert _optimizer_converged(optimizer_stub("tol_arg", x=(float("inf"),))) is False


def test_exhausted_budgets_and_unknown_stops_are_not_convergence():
    for reason in ("max_iter", "max_resets", "line_search", "unstable", "unknown"):
        assert _optimizer_converged(optimizer_stub(reason)) is False


def test_fitmodel_public_result_exposes_existing_termination_without_recomputing():
    u = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1,
         0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    y = np.array(
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1,
         0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        dtype=np.float64,
    )
    result = hgfx.fitModel(
        y, u,
        "hgf_binary_config", "unitsq_sgm_config",
        QuasiNewtonOptions(max_iter=2, opt_iter=False),
    )
    assert result.kind == "fit"
    assert isinstance(result.optim.termination, str)
    assert result.optim.termination in {
        "tol_grad", "tol_arg", "max_iter", "max_resets"
    }
    assert isinstance(result.optim.converged, bool)
    expected = (
        result.optim.termination in ("tol_grad", "tol_arg")
        and np.isfinite(result.optim.negLj)
        and np.isfinite(result.optim.final).all()
    )
    assert result.optim.converged == bool(expected)
    exported = result.to_dict(matlab_style=True)
    assert exported["optim"]["termination"] == result.optim.termination
    assert exported["optim"]["converged"] is result.optim.converged
    assert "negLj" in exported["optim"]
    assert "H" in exported["optim"]
    assert "Sigma" in exported["optim"]
    # A diagnostic extension must not replace the fixed 1.0.0 model solver.
    assert "tolGrad" in result.c_opt
    assert "maxIter" in result.c_opt
