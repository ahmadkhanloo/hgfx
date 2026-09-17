"""Run the opt-in MAP solver on the frozen compatibility objective.

This uses the same negative log-joint as ``fit_model``, but not the frozen
quasi-Newton optimizer. Results are not paper-1 compatibility evidence.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from hgfx.compat.fitting import FitProblem, hgf_binary_unitsq_fit_problem

from .interface import Jacobian, MapOptions, MapResult
from .lbfgs import minimize_map


@dataclass(frozen=True)
class MapFit:
    problem: FitProblem
    result: MapResult
    full_parameters: np.ndarray

    @property
    def free_parameters(self) -> np.ndarray:
        return self.result.x.copy()

    @property
    def neg_log_joint(self) -> float:
        return float(self.result.fun)


def fit_map(
    responses,
    inputs,
    *,
    jac: Jacobian | None = None,
    starts: Sequence[Sequence[float]] | np.ndarray | None = None,
    n_random_starts: int = 8,
    options: MapOptions | None = None,
) -> MapFit:
    """MAP-fit the binary HGF + unit-square sigmoid slice with the opt-in solver."""

    problem = hgf_binary_unitsq_fit_problem(responses, inputs)
    result = minimize_map(
        problem.evaluate_free,
        problem.initial_free,
        jac=jac,
        starts=starts,
        n_random_starts=n_random_starts,
        options=options or MapOptions(),
    )
    return MapFit(
        problem=problem,
        result=result,
        full_parameters=problem.expand(result.x),
    )
