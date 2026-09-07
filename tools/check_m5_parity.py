from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.models.ehgf import ehgf
from hgfx.models.ehgf_binary import ehgf_binary
from hgfx.updates.volatility import hgf_volatility_update

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
TRAJ_RTOL = 5e-11
TRAJ_ATOL = 5e-13
BLOCK_RTOL = 2e-13
BLOCK_ATOL = 2e-14


def _normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(_normalize(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any, *, rtol: float, atol: float) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        raise AssertionError(
            f"{label} shape mismatch: Python={a.shape} MATLAB={e.shape}"
        )
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return
    index = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = float(a[index]) if index else float(a)
    ev = float(e[index]) if index else float(e)
    abs_diff = abs(av - ev)
    scale = max(abs(ev), atol)
    rel_diff = abs_diff / scale
    context = ""
    if index:
        context = f", index={index}"
        if len(index) >= 1:
            context += f", trial={index[0] + 1}"
        if len(index) >= 2:
            context += f", level={index[1] + 1}"
    raise AssertionError(
        f"{label} first divergence{context}: MATLAB={ev:.17g}, "
        f"Python={av:.17g}, abs={abs_diff:.3e}, rel={rel_diff:.3e}, "
        f"rtol={rtol:.1e}, atol={atol:.1e}"
    )


def check_safe_precision(payload: dict[str, Any]) -> None:
    args = (
        0.2, 0.05, 1.0, 0.2, -1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 0.0, 1.0,
    )
    actual = hgf_volatility_update(*args, "ehgf")
    check(
        "safe_precision_case.ehgf",
        actual,
        payload["safe_precision_case"]["ehgf"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    if not payload["safe_precision_case"]["standard_hgf_rejects"]:
        raise AssertionError("MATLAB standard HGF did not reject the negative-precision case")
    try:
        hgf_volatility_update(*args, "hgf")
    except ValueError:
        pass
    else:
        raise AssertionError("Python standard HGF did not reject the negative-precision case")


def check_trajectory_case(name: str, case: dict[str, Any]) -> None:
    inputs = arr(case["inputs"])
    ptrans = arr(case["ptrans"])
    irregular = bool(case["irregular_intervals"])
    if case["model"] == "ehgf_binary":
        traj, inf_states = ehgf_binary(
            inputs,
            ptrans,
            transformed=True,
            irregular_intervals=irregular,
        )
    elif case["model"] == "ehgf":
        traj, inf_states = ehgf(
            inputs,
            ptrans,
            transformed=True,
            irregular_intervals=irregular,
        )
    else:
        raise AssertionError(f"unknown model in fixture {name}: {case['model']!r}")

    expected_traj = case["traj"]
    if set(traj) != set(expected_traj):
        raise AssertionError(
            f"{name} trajectory fields mismatch: "
            f"Python={sorted(traj)} MATLAB={sorted(expected_traj)}"
        )

    for field in sorted(traj):
        expected = expected_traj[field]
        actual = np.asarray(traj[field])
        if (
            field == "w"
            and actual.ndim == 2
            and actual.shape[1] == 1
            and arr(expected).ndim == 1
            and arr(expected).size == actual.size
        ):
            expected = arr(expected).reshape(actual.shape)
        check(
            f"{name}.traj.{field}",
            actual,
            expected,
            rtol=TRAJ_RTOL,
            atol=TRAJ_ATOL,
        )

    check(
        f"{name}.inf_states",
        inf_states,
        case["inf_states"],
        rtol=TRAJ_RTOL,
        atol=TRAJ_ATOL,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))

    metadata = payload["metadata"]
    if metadata["reference_version"] != "8.2.0":
        raise AssertionError(f"unexpected HGF version: {metadata['reference_version']}")
    if metadata["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError(f"unexpected HGF commit: {metadata['reference_commit']}")
    if metadata["schema_version"] != "m5-1":
        raise AssertionError(f"unexpected fixture schema: {metadata['schema_version']}")

    check_safe_precision(payload)
    for name, case in payload["trajectories"].items():
        check_trajectory_case(name, case)

    print("M5 MATLAB/Python eHGF forward parity: PASS")


if __name__ == "__main__":
    main()
