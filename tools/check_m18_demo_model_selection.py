#!/usr/bin/env python3
"""Gate HGFX model-selection behavior against the official frozen MATLAB demo.

The official HGF 8.2.0 demo contains a parameter regime that is intentionally
invalid for classic HGF but valid for eHGF. v1 compatibility requires HGFX to
reproduce both sides of that behavior, not to force classic HGF to pass.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.compat.simulation import sim_model

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CASE_ID = "D02_EHGF_CLASSIC_HGF_FAILURE_REGIME"
RTOL = 5e-11
ATOL = 5e-13


def _normalise(value: Any) -> Any:
    if value is None:
        return np.nan
    if isinstance(value, list):
        return [_normalise(item) for item in value]
    return value


def _array(value: Any) -> np.ndarray:
    return np.asarray(_normalise(value), dtype=np.float64)


def _run_hgfx(inputs: np.ndarray, parameters: np.ndarray, model: str) -> dict[str, Any]:
    try:
        result = sim_model(inputs, model, parameters)
        return {
            "success": True,
            "error": None,
            "trajectory": result.trajectory,
            "inf_states": result.inf_states,
        }
    except Exception as exc:  # evidence capture, not exception masking
        return {
            "success": False,
            "error": f"{type(exc).__name__}: {exc}",
            "trajectory": {},
            "inf_states": np.asarray([], dtype=np.float64),
        }


def _first_array_mismatch(label: str, actual: Any, expected: Any) -> str | None:
    a = _array(actual)
    e = _array(expected)
    if a.shape != e.shape:
        return f"{label}: shape mismatch HGFX={a.shape}, MATLAB={e.shape}"
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    if np.all(close):
        return None
    idx = tuple(int(i) for i in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = float(a[idx]) if idx else float(a)
    ev = float(e[idx]) if idx else float(e)
    trial = f", trial={idx[0] + 1}" if idx else ""
    return (
        f"{label}: first divergence{trial}, index={idx}, "
        f"MATLAB={ev:.17g}, HGFX={av:.17g}"
    )


def _compare_successful_variant(
    hgfx: dict[str, Any], matlab: dict[str, Any], label: str
) -> list[str]:
    mismatches: list[str] = []
    matlab_traj = matlab["traj"]
    if set(hgfx["trajectory"]) != set(matlab_traj):
        mismatches.append(
            f"{label}: trajectory fields differ: "
            f"HGFX={sorted(hgfx['trajectory'])}, MATLAB={sorted(matlab_traj)}"
        )
        return mismatches
    for field in sorted(matlab_traj):
        message = _first_array_mismatch(
            f"{label}.traj.{field}", hgfx["trajectory"][field], matlab_traj[field]
        )
        if message:
            mismatches.append(message)
            break
    message = _first_array_mismatch(
        f"{label}.inf_states", hgfx["inf_states"], matlab["inf_states"]
    )
    if message:
        mismatches.append(message)
    return mismatches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("matlab_json", type=Path)
    parser.add_argument(
        "--demo-input",
        type=Path,
        default=Path("external/hgf-toolbox/demo/example_binary_input.txt"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reference/generated/m18_demo_model_selection_classification.json"),
    )
    args = parser.parse_args()

    matlab = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    meta = matlab["metadata"]
    if meta["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError("Frozen MATLAB reference commit mismatch")
    if meta["case_id"] != CASE_ID:
        raise AssertionError("Unexpected MATLAB demo model-selection case")

    inputs = np.loadtxt(args.demo_input, dtype=np.float64).reshape(-1)
    parameters = _array(matlab["native_parameters"]).reshape(-1)
    exported_inputs = _array(matlab["inputs"]).reshape(-1)
    if not np.array_equal(inputs, exported_inputs, equal_nan=True):
        raise AssertionError("MATLAB and HGFX are not using identical official demo inputs")

    hgfx_hgf = _run_hgfx(inputs, parameters, "hgf_binary")
    hgfx_ehgf = _run_hgfx(inputs, parameters, "ehgf_binary")
    matlab_hgf = matlab["hgf_binary"]
    matlab_ehgf = matlab["ehgf_binary"]

    mismatches: list[str] = []

    # This is the product-level model-selection contract from the official demo.
    if bool(matlab_hgf["success"]):
        mismatches.append("MATLAB classic HGF unexpectedly succeeded in the frozen demo challenge")
    if not bool(matlab_ehgf["success"]):
        mismatches.append("MATLAB eHGF unexpectedly failed in the frozen demo challenge")
    if hgfx_hgf["success"] != bool(matlab_hgf["success"]):
        mismatches.append(
            f"classic HGF success mismatch: HGFX={hgfx_hgf['success']}, "
            f"MATLAB={bool(matlab_hgf['success'])}"
        )
    if hgfx_ehgf["success"] != bool(matlab_ehgf["success"]):
        mismatches.append(
            f"eHGF success mismatch: HGFX={hgfx_ehgf['success']}, "
            f"MATLAB={bool(matlab_ehgf['success'])}"
        )

    if hgfx_ehgf["success"] and bool(matlab_ehgf["success"]):
        mismatches.extend(_compare_successful_variant(hgfx_ehgf, matlab_ehgf, "ehgf_binary"))

    classification = "PASS_MODEL_SELECTION_PARITY" if not mismatches else "MODEL_SELECTION_MISMATCH"
    result = {
        "schema_version": 1,
        "case_id": CASE_ID,
        "reference_commit": REFERENCE_COMMIT,
        "classification": classification,
        "expected_reference_behavior": {
            "hgf_binary": "FAIL_VARIATIONAL_APPROXIMATION_INVALID",
            "ehgf_binary": "SUCCESS",
        },
        "matlab": {
            "hgf_binary": {
                "success": bool(matlab_hgf["success"]),
                "error_identifier": matlab_hgf.get("error_identifier", ""),
                "error_message": matlab_hgf.get("error_message", ""),
            },
            "ehgf_binary": {
                "success": bool(matlab_ehgf["success"]),
                "error_identifier": matlab_ehgf.get("error_identifier", ""),
                "error_message": matlab_ehgf.get("error_message", ""),
            },
        },
        "hgfx": {
            "hgf_binary": {"success": hgfx_hgf["success"], "error": hgfx_hgf["error"]},
            "ehgf_binary": {"success": hgfx_ehgf["success"], "error": hgfx_ehgf["error"]},
        },
        "mismatches": mismatches,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if mismatches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
