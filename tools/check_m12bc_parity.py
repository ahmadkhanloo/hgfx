from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.models import (
    hgf_binary_mab,
    hgf_ar1_mab,
    hgf_ar1_binary_mab,
    ehgf_ar1_binary_mab,
    uhgf_ar1_binary_mab,
    hgf_jget,
    ehgf_jget,
    uhgf_jget,
)

RTOL = 2e-9
ATOL = 2e-11
REF = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def norm(x: Any) -> Any:
    if x is None:
        return np.nan
    if isinstance(x, list):
        return [norm(v) for v in x]
    if isinstance(x, dict):
        return {k: norm(v) for k, v in x.items()}
    return x


def arr(x: Any) -> np.ndarray:
    return np.asarray(norm(x), dtype=np.float64)


def check(label: str, actual: Any, expected: Any) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        if a.size == e.size:
            e = e.reshape(a.shape)
        else:
            raise AssertionError(f"{label}: shape Python={a.shape} MATLAB={e.shape}")
    ok = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(ok):
        return
    idx = tuple(int(i) for i in np.argwhere(~ok)[0]) if np.ndim(ok) else ()
    av = float(a[idx]) if idx else float(a)
    ev = float(e[idx]) if idx else float(e)
    raise AssertionError(
        f"{label} divergence at {idx}: MATLAB={ev:.17g}, Python={av:.17g}, abs={abs(av-ev):.3e}"
    )


def compare_result(label: str, got, expected: dict[str, Any]) -> None:
    traj, inf = got
    check(f"{label}.infStates", inf, expected["infStates"])
    for field, exp in expected["traj"].items():
        if field not in traj:
            raise AssertionError(f"{label}: missing trajectory field {field}")
        check(f"{label}.traj.{field}", traj[field], exp)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    meta = payload["metadata"]
    assert meta["schema_version"] == "m12bc-1"
    assert meta["reference_version"] == "8.2.0"
    assert meta["reference_commit"] == REF
    cases = payload["cases"]

    ub = np.array([0, 1, 1, 0, 1, np.nan, 0, 1, 1, 0, 0, 1], dtype=np.float64)
    uc = np.array([.2, .4, .1, .7, .6, np.nan, .3, .9, .2, .5, .8, .4], dtype=np.float64)
    choices = np.array([1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3], dtype=np.float64)
    ignored = [5]

    p_binary_mab = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, 0, 1, 1, np.nan, -3, -6],
        dtype=np.float64,
    )
    compare_result(
        "hgf_binary_mab",
        hgf_binary_mab(
            ub, p_binary_mab, choices=choices, n_bandits=3,
            ignored_trials=ignored, validate=False
        ),
        cases["hgf_binary_mab"],
    )

    p_ar_mab = np.array([.2, 1, .3, .1, .1, 0, .2, 1, 1, -3, -6, .2], dtype=np.float64)
    compare_result(
        "hgf_ar1_mab",
        hgf_ar1_mab(
            uc, p_ar_mab, choices=choices, n_bandits=3,
            ignored_trials=ignored, validate=False
        ),
        cases["hgf_ar1_mab"],
    )

    p_hgf = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, .2,
         np.nan, 0, 1, 1, 1, np.nan, -2, -6],
        dtype=np.float64,
    )
    compare_result(
        "hgf_ar1_binary_mab",
        hgf_ar1_binary_mab(
            ub, p_hgf, choices=choices, n_bandits=3,
            ignored_trials=ignored, validate=False
        ),
        cases["hgf_ar1_binary_mab"],
    )

    p_ext = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, .45,
         np.nan, 0, 1, np.nan, 0, 0, 1, 1, np.nan, -3, 2],
        dtype=np.float64,
    )
    for label, fn in (
        ("ehgf_ar1_binary_mab", ehgf_ar1_binary_mab),
        ("uhgf_ar1_binary_mab", uhgf_ar1_binary_mab),
    ):
        compare_result(
            label,
            fn(
                ub, p_ext, choices=choices, n_bandits=3,
                ignored_trials=ignored, validate=False
            ),
            cases[label],
        )

    uj = np.array([.2, .4, .1, .7, .6, np.nan, .3, .9, .2, .5, .8, .4], dtype=np.float64)
    pj = np.array(
        [.3, 1, .5, .2, -2, -2, 1, 1, 1, 1, 1, 0, -3, -6, -3, -6],
        dtype=np.float64,
    )
    for label, fn in (
        ("hgf_jget", hgf_jget),
        ("ehgf_jget", ehgf_jget),
        ("uhgf_jget", uhgf_jget),
    ):
        compare_result(
            label,
            fn(uj, pj, ignored_trials=ignored, validate=False),
            cases[label],
        )

    print("M12B/C MATLAB/Python parity: PASS")


if __name__ == "__main__":
    main()
