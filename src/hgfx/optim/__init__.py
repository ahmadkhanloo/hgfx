"""Optimizers.

``quasinewton_optim`` is the frozen MATLAB-compatible default used by
``fit_model``. ``minimize_map`` is an opt-in tighter MAP solver and is not
part of the v1 compatibility contract.
"""

from .batch import multi_start_map
from .compat_quasinewton import QuasiNewtonOptions, QuasiNewtonResult, quasinewton_optim
from .interface import MapOptions, MapResult, MapStartResult
from .lbfgs import minimize_map

__all__ = [
    "MapOptions",
    "MapResult",
    "MapStartResult",
    "QuasiNewtonOptions",
    "QuasiNewtonResult",
    "minimize_map",
    "multi_start_map",
    "quasinewton_optim",
]
