from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat import hgf_ar1_config
from hgfx.models import hgf_ar1

RTOL = 5e-10
ATOL = 5e-12
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def norm(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [norm(x) for x in value]
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
        f"{label} divergence at {idx}: MATLAB={ev:.17g}, Python={av:.17g}, abs={abs(av-ev):.3e}"
    )


def compare_case(name: str, case: dict[str, Any], *, irregular: bool) -> None:
    inputs = arr(case["inputs"])
    params = arr(case["parameters"]).reshape(-1)
    ignored = []
    if "ignored_matlab" in case:
        ignored = [int(x) - 1 for x in arr(case["ignored_matlab"]).reshape(-1)]
    traj, inf = hgf_ar1(
        inputs,
        params,
        irregular_intervals=irregular,
        ignored_trials=ignored,
        validate=False,
    )
    check(f"{name}.infStates", inf, case["infStates"])
    for field, expected in case["traj"].items():
        check(f"{name}.traj.{field}", traj[field], expected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    metadata = payload["metadata"]
    assert metadata["schema_version"] == "m12a-1"
    assert metadata["reference_version"] == "8.2.0"
    assert metadata["reference_commit"] == REFERENCE_COMMIT

    compare_case("regular", payload["regular"], irregular=False)
    compare_case("irregular", payload["irregular"], irregular=True)

    t = payload["transform"]
    config = hgf_ar1_config()
    native = config.transformed_to_native(arr(t["ptrans"]).reshape(-1))
    check("transform.pnative", native, t["pnative"])
    structured = config.structure_vector(native)
    check("transform.phi", structured["phi"], t["phi"])
    check("transform.al", structured["al"], t["al"])

    print("M12A continuous AR1 MATLAB/Python parity: PASS")


if __name__ == "__main__":
    main()
