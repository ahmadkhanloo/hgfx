"""Shared helpers for MATLAB-compatible HGF forward passes."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def first_input_column(inputs) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(inputs, dtype=np.float64)
    if array.ndim == 1:
        if array.size == 0:
            raise ValueError("inputs must contain at least one trial")
        return array, array
    if array.ndim == 2:
        if array.shape[0] == 0 or array.shape[1] == 0:
            raise ValueError("inputs must contain at least one trial and column")
        return array[:, 0], array
    raise ValueError("inputs must be a 1D sequence or 2D matrix")


def ignored_mask(values: np.ndarray, ignored_trials: Sequence[int] | None) -> np.ndarray:
    mask = np.isnan(values)
    if ignored_trials is None:
        return mask
    mask = mask.copy()
    for index in ignored_trials:
        if index < 0 or index >= values.size:
            raise IndexError(f"ignored trial index out of range: {index}")
        mask[index] = True
    return mask


def binary_native_parameters(parameters, *, transformed: bool) -> tuple[np.ndarray, int]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    levels = (p.size + 1) / 5
    if levels != int(levels):
        raise ValueError("Cannot determine number of HGF binary levels")
    l = int(levels)
    if l < 3:
        raise ValueError("binary HGF requires at least three levels")
    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[3 * l : 4 * l - 1] = np.exp(p[3 * l : 4 * l - 1])
    return p, l


def continuous_native_parameters(parameters, *, transformed: bool) -> tuple[np.ndarray, int]:
    p = np.asarray(parameters, dtype=np.float64).reshape(-1).copy()
    levels = p.size / 5
    if levels != int(levels):
        raise ValueError("Cannot determine number of HGF continuous levels")
    l = int(levels)
    if l < 2:
        raise ValueError("continuous HGF requires at least two levels")
    if transformed:
        p[l : 2 * l] = np.exp(p[l : 2 * l])
        p[3 * l : 4 * l - 1] = np.exp(p[3 * l : 4 * l - 1])
        p[5 * l - 1] = np.exp(p[5 * l - 1])
    return p, l
