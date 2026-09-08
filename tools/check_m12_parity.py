from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.models.hgf_ar1_binary import ehgf_ar1_binary, hgf_ar1_binary, uhgf_ar1_binary
from hgfx.models.hgf_binary_pu import (
    ehgf_binary_pu,
    ehgf_binary_pu_tbt,
    hgf_binary_pu,
    hgf_binary_pu_tbt,
    uhgf_binary_pu,
    uhgf_binary_pu_tbt,
)
from hgfx.models.legacy import (
    hidden_markov_model,
    kalman_filter,
    pearce_hall_binary,
    rw_binary,
    rw_binary_dual,
    sutton_k1_binary,
)

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
RTOL = 5e-10
ATOL = 5e-12


def norm(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [norm(item) for item in value]
    return value


def arr(value: Any) -> np.ndarray:
    return np.asarray(norm(value), dtype=np.float64)


def check(label: str, actual: Any, expected: Any) -> None:
    a = arr(actual)
    e = arr(expected)
    if a.shape != e.shape:
        if a.size == e.size:
            e = e.reshape(a.shape)
        else:
            raise AssertionError(f"{label} shape Python={a.shape} MATLAB={e.shape}")
    ok = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(ok):
        return
    idx = tuple(int(i) for i in np.argwhere(~ok)[0]) if np.ndim(ok) else ()
    av = float(a[idx]) if idx else float(a)
    ev = float(e[idx]) if idx else float(e)
    raise AssertionError(
        f"{label} divergence at {idx}: MATLAB={ev:.17g}, Python={av:.17g}, "
        f"abs={abs(av-ev):.3e}"
    )


def compare_case(name: str, actual, expected: dict[str, Any]) -> None:
    traj, inf = actual
    check(f"{name}.infStates", inf, expected["infStates"])
    for field, matlab_value in expected["traj"].items():
        if field not in traj:
            raise AssertionError(f"{name}: missing trajectory field {field}")
        check(f"{name}.traj.{field}", traj[field], matlab_value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    metadata = payload["metadata"]
    assert metadata["schema_version"] == "m12-1"
    assert metadata["reference_version"] == "8.2.0"
    assert metadata["reference_commit"] == REFERENCE_COMMIT

    u = np.array([0, 1, 1, 0, 1, np.nan, 0, 1, 1, 0, 0, 1], dtype=np.float64)
    ign = [5]
    alpha = np.array([.25, .3, .2, .35, .3, .25, .2, .3, .35, .25, .2, .3])
    ut = np.column_stack((u, alpha))

    p_pu = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, 0, 1, 1, np.nan, -3, -6, .35, 0, 1]
    )
    p_pu_e = p_pu.copy()
    p_pu_e[13] = 2.0
    p_tbt = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, 0, 1, 1, np.nan, -5, -6, 0, 1]
    )
    p_ar_hgf = np.array(
        [np.nan, 0, 1, np.nan, .006, 4, np.nan, 0, .2, np.nan, 0, 1, 1, 1, np.nan, -2, -6]
    )
    p_ar_ext = np.array(
        [np.nan, 0, 1, np.nan, .1, 1, np.nan, 0, .45, np.nan, 0, 1,
         np.nan, 0, 0, 1, 1, np.nan, -3, 2]
    )

    actual = {
        "hgf_binary_pu": hgf_binary_pu(u, p_pu, ignored_trials=ign, validate=False),
        "ehgf_binary_pu": ehgf_binary_pu(u, p_pu_e, ignored_trials=ign, validate=False),
        "uhgf_binary_pu": uhgf_binary_pu(u, p_pu, ignored_trials=ign, validate=False),
        "hgf_binary_pu_tbt": hgf_binary_pu_tbt(ut, p_tbt, ignored_trials=ign, validate=False),
        "ehgf_binary_pu_tbt": ehgf_binary_pu_tbt(ut, p_tbt, ignored_trials=ign, validate=False),
        "uhgf_binary_pu_tbt": uhgf_binary_pu_tbt(ut, p_tbt, ignored_trials=ign, validate=False),
        "hgf_ar1_binary": hgf_ar1_binary(u, p_ar_hgf, ignored_trials=ign, validate=False),
        "ehgf_ar1_binary": ehgf_ar1_binary(u, p_ar_ext, ignored_trials=ign, validate=False),
        "uhgf_ar1_binary": uhgf_ar1_binary(u, p_ar_ext, ignored_trials=ign, validate=False),
        "rw_binary": rw_binary(u, [.5, .3], ignored_trials=ign),
        "rw_binary_dual": rw_binary_dual(
            u,
            np.array([1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1], dtype=np.float64),
            [.4, .6, .3, .5],
            ignored_trials=ign,
        ),
        "ph_binary": pearce_hall_binary(u, [.5, .4, .2], ignored_trials=ign),
        "sutton_k1_binary": sutton_k1_binary(u, [1, 1, .5, .01], ignored_trials=ign),
        "kalman": kalman_filter(
            np.array([.2, .4, .3, .7, .8, np.nan, .5, .6, .55, .9, .4, .3]),
            [.2, .3, -2, 5],
            ignored_trials=ign,
        ),
        "hmm": hidden_markov_model(
            np.array([1, 1, 2, 2, 1, 2, 2, 1, 1, 2, 1, 2], dtype=np.float64),
            [.6, .85, .2],
            outcome_matrix=np.array([[.9, .1], [.1, .9]], dtype=np.float64),
            n_states=2,
        ),
    }

    expected_cases = payload["cases"]
    if set(actual) != set(expected_cases):
        raise AssertionError(
            f"case mismatch Python={sorted(actual)} MATLAB={sorted(expected_cases)}"
        )

    for name, result in actual.items():
        compare_case(name, result, expected_cases[name])

    print("M12 MATLAB/Python specialized model parity: PASS")


if __name__ == "__main__":
    main()
