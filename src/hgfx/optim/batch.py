"""Multi-start helper around the opt-in MAP solver."""

from __future__ import annotations

from collections.abc import Sequence

from .interface import Jacobian, MapOptions, MapResult, Objective
from .lbfgs import minimize_map


def multi_start_map(
    function: Objective,
    x0,
    *,
    jac: Jacobian | None = None,
    starts: Sequence[Sequence[float]] | None = None,
    n_random_starts: int = 4,
    options: MapOptions | None = None,
) -> MapResult:
    """Run ``minimize_map`` with explicit and random restarts.

    Random starts are perturbations of ``x0``. They are not MATLAB RNG-compatible
    and must not be mixed into compatibility evidence.
    """

    return minimize_map(
        function,
        x0,
        jac=jac,
        starts=starts,
        n_random_starts=n_random_starts,
        options=options,
    )
