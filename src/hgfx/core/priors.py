"""MATLAB-compatible prior/free/fixed parameter semantics."""

from __future__ import annotations

from enum import Enum
import math
from collections.abc import Sequence


class PriorStatus(str, Enum):
    FREE = "free"
    FIXED = "fixed"
    UNDEFINED = "undefined"


def prior_status(prior_variance: float) -> PriorStatus:
    """Mirror fitModel.m semantics for selecting optimized parameters.

    MATLAB converts NaN prior variances to zero before find(). Any remaining
    non-zero variance is optimized; exactly zero is fixed.
    """
    value = float(prior_variance)
    if math.isnan(value):
        return PriorStatus.UNDEFINED
    if value == 0.0:
        return PriorStatus.FIXED
    return PriorStatus.FREE


def indices_with_status(
    prior_variances: Sequence[float],
    status: PriorStatus,
    *,
    matlab_one_based: bool = False,
) -> tuple[int, ...]:
    offset = 1 if matlab_one_based else 0
    return tuple(
        index + offset
        for index, variance in enumerate(prior_variances)
        if prior_status(float(variance)) is status
    )


def optimization_indices(
    prior_variances: Sequence[float],
    *,
    matlab_one_based: bool = False,
) -> tuple[int, ...]:
    return indices_with_status(
        prior_variances,
        PriorStatus.FREE,
        matlab_one_based=matlab_one_based,
    )
