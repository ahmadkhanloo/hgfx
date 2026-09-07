"""Enhanced continuous HGF compatibility wrapper."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .hgf import hgf_unified


def ehgf(
    inputs,
    parameters,
    *,
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Run eHGF continuous forward recursion using the frozen safe precision update."""
    return hgf_unified(
        inputs,
        parameters,
        update_type="ehgf",
        transformed=transformed,
        irregular_intervals=irregular_intervals,
        ignored_trials=ignored_trials,
        validate=False,
    )


forward = ehgf
