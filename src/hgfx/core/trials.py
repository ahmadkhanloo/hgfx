"""Trial mask and time-axis semantics from frozen HGF Toolbox."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .placeholders import first_input_column


@dataclass(frozen=True)
class TrialMasks:
    ignored: np.ndarray
    irregular: np.ndarray

    @property
    def ignored_matlab_indices(self) -> tuple[int, ...]:
        return tuple(int(index) + 1 for index in np.flatnonzero(self.ignored))

    @property
    def irregular_matlab_indices(self) -> tuple[int, ...]:
        return tuple(int(index) + 1 for index in np.flatnonzero(self.irregular))


def _first_response_column(
    responses: np.ndarray | list[float] | None,
    n_trials: int,
) -> np.ndarray | None:
    if responses is None:
        return None
    array = np.asarray(responses, dtype=np.float64)
    if array.size == 0:
        return None
    if array.ndim == 1:
        column = array
    elif array.ndim == 2:
        if array.shape[1] == 0:
            return None
        column = array[:, 0]
    else:
        raise ValueError("responses must be a 1D sequence or 2D matrix")
    if column.size != n_trials:
        raise ValueError("responses and inputs must contain the same number of trials")
    return column


def build_trial_masks(
    responses: np.ndarray | list[float] | None,
    inputs: np.ndarray | list[float],
) -> TrialMasks:
    """Mirror dataPrep: NaN input is ignored+irregular; NaN response is irregular."""
    input_column = first_input_column(inputs)
    ignored = np.isnan(input_column)
    response_column = _first_response_column(responses, input_column.size)
    response_irregular = (
        np.zeros(input_column.size, dtype=bool)
        if response_column is None
        else np.isnan(response_column)
    )
    irregular = ignored | response_irregular
    return TrialMasks(ignored=ignored, irregular=irregular)


def build_time_axis(
    inputs: np.ndarray | list[float],
    *,
    irregular_intervals: bool | None,
) -> np.ndarray:
    """Mirror hgf_time_axis.m including its missing-flag fallback."""
    array = np.asarray(inputs, dtype=np.float64)
    if array.ndim == 1:
        n_trials = array.size
        n_columns = 1
    elif array.ndim == 2:
        n_trials, n_columns = array.shape
    else:
        raise ValueError("inputs must be a 1D sequence or 2D matrix")

    if irregular_intervals is None:
        irregular_intervals = n_columns > 1

    if not irregular_intervals:
        return np.ones(n_trials + 1, dtype=np.float64)

    if n_columns <= 1:
        raise ValueError(
            "Input matrix must contain more than one column when "
            "irregular_intervals is true"
        )

    return np.concatenate(
        (np.asarray([0.0], dtype=np.float64), array[:, -1])
    )
