"""Unbounded binary HGF compatibility wrapper."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .hgf_binary import hgf_binary_unified


def uhgf_binary(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Run uHGF binary forward recursion using the frozen dual approximation."""
    return hgf_binary_unified(
        inputs,
        parameters,
        update_type="uhgf",
        transformed=transformed,
        irregular_intervals=irregular_intervals,
        ignored_trials=ignored_trials,
        validate=False,
    )


forward = uhgf_binary
