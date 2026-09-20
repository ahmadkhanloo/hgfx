"""Contracts for the opt-in MAP optimizer.

This module is not part of the frozen HGF Toolbox 8.2.0 compatibility surface.
``hgfx.fit_model`` continues to use ``compat_quasinewton``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import numpy as np

Objective = Callable[[np.ndarray], float]
Jacobian = Callable[[np.ndarray], np.ndarray]
GradientKind = Literal["finite", "ridders", "jax"]
SolverKind = Literal["scipy", "internal"]
Termination = Literal[
    "gtol",
    "ftol",
    "maxiter",
    "unstable",
    "line_search",
    "scipy",
]


@dataclass(frozen=True)
class MapOptions:
    """Settings for the opt-in multi-start MAP solver.

    Default solver is SciPy ``L-BFGS-B`` when SciPy is installed. That is the
    production MAP path. The handwritten L-BFGS remains a fallback only.

    ``gradient='jax'`` is valid only for JAX-traceable objectives. NumPy HGFX
    forwards such as ``hgf_ar1_binary`` are not traceable; use ``finite`` or
    pass an explicit ``jac``.
    """

    solver: SolverKind = "scipy"
    method: str = "L-BFGS-B"
    gradient: GradientKind = "finite"
    maxiter: int = 800
    gtol: float = 1e-8
    ftol: float = 1e-12
    history: int = 17
    max_ls: int = 20
    finite_step: float = 1e-6
    seed: int = 0
    jitter: float = 0.15


@dataclass(frozen=True)
class MapStartResult:
    """One multi-start candidate."""

    x: np.ndarray
    fun: float
    nit: int
    nfev: int
    njev: int
    termination: Termination
    grad_norm: float


@dataclass(frozen=True)
class MapResult:
    """Best candidate across starts. Not a compatibility ``QuasiNewtonResult``."""

    x: np.ndarray
    fun: float
    nit: int
    nfev: int
    njev: int
    termination: Termination
    grad_norm: float
    gradient_kind: GradientKind | Literal["user"]
    solver: SolverKind
    method: str
    n_starts: int
    starts: tuple[MapStartResult, ...]

    @property
    def success(self) -> bool:
        return self.termination in {"gtol", "ftol", "scipy"} and np.isfinite(self.fun)
