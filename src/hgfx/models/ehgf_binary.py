"""Enhanced binary HGF compatibility wrapper."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .hgf_binary import hgf_binary_unified


def ehgf_binary(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Run eHGF binary forward recursion using the frozen safe precision update."""
    return hgf_binary_unified(
        inputs,
        parameters,
        update_type="ehgf",
        transformed=transformed,
        irregular_intervals=irregular_intervals,
        ignored_trials=ignored_trials,
        validate=False,
    )


forward = ehgf_binary
