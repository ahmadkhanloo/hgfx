"""Unbounded continuous HGF compatibility wrapper."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .hgf import hgf_unified


def uhgf(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Run uHGF continuous forward recursion using the frozen dual approximation."""
    return hgf_unified(
        inputs,
        parameters,
        update_type="uhgf",
        transformed=transformed,
        irregular_intervals=irregular_intervals,
        ignored_trials=ignored_trials,
        validate=False,
    )


forward = uhgf
