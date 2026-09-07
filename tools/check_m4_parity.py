from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.models.hgf import hgf
from hgfx.models.hgf_binary import hgf_binary
from hgfx.updates.binary_l1 import hgf_binary_level1
from hgfx.updates.binary_l2 import hgf_binary_level2
from hgfx.updates.continuous_l1 import hgf_continuous_level1
from hgfx.updates.precision_prediction import hgf_pihat, hgf_pihat_last
from hgfx.updates.prediction import hgf_prediction
from hgfx.updates.volatility import hgf_volatility_update
from hgfx.updates.volatility_pe import hgf_volatility_pe

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
BLOCK_RTOL = 2e-13
BLOCK_ATOL = 2e-14
TRAJ_RTOL = 5e-11
TRAJ_ATOL = 5e-13


def _normalize(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(_normalize(value), dtype=np.float64)


def check(
    label: str,
    actual: Any,
    expected: Any,
    *,
    rtol: float,
    atol: float,
) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        raise AssertionError(
            f"{label} shape mismatch: Python={a.shape} MATLAB={e.shape}"
        )
    close = np.isclose(a, e, rtol=rtol, atol=atol, equal_nan=True)
    if np.all(close):
        return

    index = (
        tuple(int(i) for i in np.argwhere(~close)[0])
        if np.ndim(close)
        else ()
    )
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


def check_blocks(payload: dict[str, Any]) -> None:
    b = payload["blocks"]
    check(
        "prediction.standard",
        hgf_prediction(0.4, 1.7, rho=-0.15),
        b["prediction"]["standard"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    check(
        "prediction.ar",
        hgf_prediction(0.4, 1.7, rho=-0.15, phi=0.2, m=1.1),
        b["prediction"]["ar"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    check(
        "pihat",
        hgf_pihat(2.5, 1.3, 0.7, 0.25, -2.0),
        b["pihat"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    check(
        "pihat_last",
        hgf_pihat_last(2.5, 1.3, 0.02),
        b["pihat_last"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )

    l1 = hgf_binary_level1(1.0, 1.2, -0.4)
    check(
        "binary_l1.standard",
        [l1[0], l1[2], l1[3], l1[4]],
        b["binary_l1"]["standard"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    if not np.isinf(l1[1]) or not b["binary_l1"]["pi_is_inf"]:
        raise AssertionError(
            "binary_l1 posterior precision must be Inf in both implementations"
        )
    check(
        "binary_l1.clamp",
        [
            hgf_binary_level1(1.0, 1.0, -20.0)[2],
            hgf_binary_level1(0.0, 1.0, 20.0)[2],
        ],
        b["binary_l1"]["clamp"],
        rtol=0.0,
        atol=0.0,
    )
    check(
        "binary_l2",
        hgf_binary_level2(0.3, 2.0, 1.0, 4.0, 0.2),
        b["binary_l2"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    c1 = hgf_continuous_level1(0.4, 0.3, 2.0, 0.05)
    check(
        "continuous_l1",
        c1,
        b["continuous_l1"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )
    check(
        "volatility_pe",
        hgf_volatility_pe(c1[0], c1[1], 0.3, 2.0),
        b["volatility_pe"],
        rtol=BLOCK_RTOL,
        atol=BLOCK_ATOL,
    )

    vargs = (
        0.25, 2.0, 0.7, 3.0, 0.2, 0.1,
        -2.0, 2.5, 3.2, 0.4, 0.35, 1.3,
    )
    for update_type in ("hgf", "ehgf", "uhgf"):
        check(
            f"volatility_update.{update_type}",
            hgf_volatility_update(*vargs, update_type),
            b["volatility_update"][update_type],
            rtol=5e-12 if update_type == "uhgf" else BLOCK_RTOL,
            atol=5e-14 if update_type == "uhgf" else BLOCK_ATOL,
        )


def check_trajectory_case(name: str, case: dict[str, Any]) -> None:
    inputs = arr(case["inputs"])
    ptrans = arr(case["ptrans"])
    irregular = bool(case["irregular_intervals"])
    if case["model"] == "hgf_binary":
        traj, inf_states = hgf_binary(
            inputs,
            ptrans,
            transformed=True,
            irregular_intervals=irregular,
        )
    elif case["model"] == "hgf":
        traj, inf_states = hgf(
            inputs,
            ptrans,
            transformed=True,
            irregular_intervals=irregular,
        )
    else:
        raise AssertionError(
            f"unknown model in fixture {name}: {case['model']!r}"
        )

    expected_traj = case["traj"]
    if set(traj) != set(expected_traj):
        raise AssertionError(
            f"{name} trajectory fields mismatch: "
            f"Python={sorted(traj)} MATLAB={sorted(expected_traj)}"
        )
    for field in sorted(traj):
        check(
            f"{name}.traj.{field}",
            traj[field],
            expected_traj[field],
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
        raise AssertionError(
            f"unexpected HGF version: {metadata['reference_version']}"
        )
    if metadata["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError(
            f"unexpected HGF commit: {metadata['reference_commit']}"
        )
    if metadata["schema_version"] != "m4-1":
        raise AssertionError(
            f"unexpected fixture schema: {metadata['schema_version']}"
        )

    check_blocks(payload)
    for name, case in payload["trajectories"].items():
        check_trajectory_case(name, case)

    print("M4 MATLAB/Python standard HGF forward parity: PASS")


if __name__ == "__main__":
    main()
