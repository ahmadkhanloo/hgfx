"""Numerical diffing for MATLAB-vs-Python golden fixtures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class Divergence:
    field: str
    reason: str
    index: tuple[int, ...] | None
    trial: int | None
    level: int | None
    expected: float | int | bool | None
    actual: float | int | bool | None
    abs_diff: float | None
    rel_diff: float | None


@dataclass(frozen=True)
class DiffReport:
    passed: bool
    compared_fields: int
    rtol: float
    atol: float
    first_failure: Divergence | None
    max_abs_diff: float
    max_rel_diff: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compare_mappings(
    expected: Mapping[str, np.ndarray],
    actual: Mapping[str, np.ndarray],
    *,
    rtol: float,
    atol: float,
) -> DiffReport:
    first: Divergence | None = None
    compared = 0
    max_abs = 0.0
    max_rel = 0.0

    for field in sorted(set(expected) | set(actual)):
        if field not in expected:
            first = first or Divergence(field, "unexpected_field", None, None, None, None, None, None, None)
            continue
        if field not in actual:
            first = first or Divergence(field, "missing_field", None, None, None, None, None, None, None)
            continue

        exp = np.asarray(expected[field])
        act = np.asarray(actual[field])
        compared += 1

        if exp.shape != act.shape:
            first = first or Divergence(
                field,
                f"shape_mismatch expected={exp.shape} actual={act.shape}",
                None, None, None, None, None, None, None,
            )
            continue

        close = np.isclose(exp, act, rtol=rtol, atol=atol, equal_nan=True)
        finite = np.isfinite(exp) & np.isfinite(act)
        if np.any(finite):
            abs_diff = np.abs(act[finite] - exp[finite])
            max_abs = max(max_abs, float(np.max(abs_diff)))
            denom = np.abs(exp[finite])
            rel = np.divide(
                abs_diff,
                denom,
                out=np.full_like(abs_diff, np.inf, dtype=float),
                where=denom != 0,
            )
            rel[(denom == 0) & (abs_diff == 0)] = 0.0
            max_rel = max(max_rel, float(np.max(rel)))

        if first is None and not bool(np.all(close)):
            idx = tuple(int(i) for i in np.argwhere(~close)[0])
            e = exp[idx].item() if isinstance(exp[idx], np.generic) else exp[idx]
            a = act[idx].item() if isinstance(act[idx], np.generic) else act[idx]
            ef = float(e)
            af = float(a)
            ad = abs(af - ef)
            rd = 0.0 if ad == 0 else (math.inf if ef == 0 else ad / abs(ef))
            first = Divergence(
                field, "numerical_mismatch", idx,
                idx[0] + 1 if len(idx) >= 1 else None,
                idx[1] + 1 if len(idx) >= 2 else None,
                e, a, ad, rd,
            )

    return DiffReport(first is None, compared, rtol, atol, first, max_abs, max_rel)
