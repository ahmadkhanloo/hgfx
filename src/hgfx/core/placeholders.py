"""Input-derived placeholder semantics from HGF Toolbox fitModel.m."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

import numpy as np


class Placeholder(IntEnum):
    FIRST_INPUT = 99991
    VAR_FIRST_20 = 99992
    LOG_VAR_FIRST_20 = 99993
    LOG_VAR_FIRST_20_MINUS_2 = 99994


@dataclass(frozen=True)
class PlaceholderValues:
    first_input: float
    var_first_20: float
    log_var_first_20: float
    log_var_first_20_minus_2: float

    def as_matlab_codes(self) -> dict[int, float]:
        return {
            int(Placeholder.FIRST_INPUT): self.first_input,
            int(Placeholder.VAR_FIRST_20): self.var_first_20,
            int(Placeholder.LOG_VAR_FIRST_20): self.log_var_first_20,
            int(Placeholder.LOG_VAR_FIRST_20_MINUS_2): self.log_var_first_20_minus_2,
        }


def first_input_column(inputs: np.ndarray | list[float]) -> np.ndarray:
    array = np.asarray(inputs, dtype=np.float64)
    if array.ndim == 1:
        column = array
    elif array.ndim == 2:
        if array.shape[1] == 0:
            raise ValueError("inputs must contain at least one column")
        column = array[:, 0]
    else:
        raise ValueError("inputs must be a 1D sequence or 2D matrix")
    if column.size == 0:
        raise ValueError("inputs must contain at least one trial")
    return column


def compute_placeholder_values(inputs: np.ndarray | list[float]) -> PlaceholderValues:
    """Compute placeholders exactly as dataPrep in frozen fitModel.m."""
    column = first_input_column(inputs)
    window = column[:20] if column.size > 20 else column
    variance = float(np.var(window, ddof=0))
    with np.errstate(divide="ignore", invalid="ignore"):
        log_variance = float(np.log(variance))
    return PlaceholderValues(
        first_input=float(column[0]),
        var_first_20=variance,
        log_var_first_20=log_variance,
        log_var_first_20_minus_2=log_variance - 2.0,
    )


def resolve_placeholder_value(value: float, placeholders: PlaceholderValues) -> float:
    """Mirror the exact replacement set used by frozen fitModel.m."""
    numeric = float(value)
    codes = placeholders.as_matlab_codes()
    if numeric in codes:
        return float(codes[int(numeric)])
    if numeric == -int(Placeholder.LOG_VAR_FIRST_20):
        return -placeholders.log_var_first_20
    return numeric


def resolve_placeholder_array(
    values: np.ndarray | list[float],
    placeholders: PlaceholderValues,
) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    resolved = array.copy()
    for index, value in np.ndenumerate(array):
        resolved[index] = resolve_placeholder_value(float(value), placeholders)
    return resolved
