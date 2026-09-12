#!/usr/bin/env python3
"""Gate the official frozen MATLAB uHGF -> uHGF-AR(1) demo workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.models.hgf_ar1_binary import uhgf_ar1_binary
from hgfx.models.uhgf_binary import uhgf_binary

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
CASE_ID = "D04_UHGF_TO_AR1_WORKFLOW"
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


def _run(model: str, inputs: np.ndarray, parameters: np.ndarray) -> dict[str, Any]:
    try:
        if model == "uhgf_binary":
            traj, inf_states = uhgf_binary(inputs, parameters, transformed=False)
        elif model == "uhgf_ar1_binary":
            traj, inf_states = uhgf_ar1_binary(inputs, parameters, transformed=False)
        else:
            raise ValueError(f"Unsupported model {model}")
        mu = np.asarray(traj["mu"], dtype=np.float64)
        return {
            "success": True,
            "error": None,
            "traj": traj,
            "inf_states": inf_states,
            "max_abs_mu_all": float(np.nanmax(np.abs(mu))),
            "max_abs_mu_level3": float(np.nanmax(np.abs(mu[:, 2]))) if mu.shape[1] >= 3 else None,
        }
    except Exception as exc:  # evidence capture
        return {
            "success": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traj": {},
            "inf_states": np.asarray([], dtype=np.float64),
            "max_abs_mu_all": None,
            "max_abs_mu_level3": None,
        }


def _first_mismatch(label: str, actual: Any, expected: Any) -> str | None:
    a = _array(actual)
    e = _array(expected)
    if a.shape != e.shape:
        # MATLAB jsonencode commonly collapses singleton dimensions. Allow only
        # shape differences that disappear under squeeze and preserve element order.
        asq, esq = np.squeeze(a), np.squeeze(e)
        if asq.shape == esq.shape:
            a, e = asq, esq
        else:
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


def _compare_variant(label: str, hgfx: dict[str, Any], matlab: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    matlab_success = bool(matlab["success"])
    if hgfx["success"] != matlab_success:
        mismatches.append(
            f"{label}: success mismatch HGFX={hgfx['success']}, MATLAB={matlab_success}"
        )
        return mismatches
    if not hgfx["success"]:
        return mismatches

    matlab_traj = matlab["traj"]
    if set(hgfx["traj"]) != set(matlab_traj):
        mismatches.append(
            f"{label}: trajectory fields differ HGFX={sorted(hgfx['traj'])}, "
            f"MATLAB={sorted(matlab_traj)}"
        )
        return mismatches

    for field in sorted(matlab_traj):
        message = _first_mismatch(
            f"{label}.traj.{field}", hgfx["traj"][field], matlab_traj[field]
        )
        if message:
            mismatches.append(message)
            break

    message = _first_mismatch(
        f"{label}.inf_states", hgfx["inf_states"], matlab["inf_states"]
    )
    if message:
        mismatches.append(message)

    for metric in ("max_abs_mu_all", "max_abs_mu_level3"):
        matlab_value = matlab.get(metric)
        hgfx_value = hgfx.get(metric)
        if matlab_value is None or hgfx_value is None:
            continue
        if not np.isclose(float(hgfx_value), float(matlab_value), rtol=RTOL, atol=ATOL):
            mismatches.append(
                f"{label}.{metric}: MATLAB={float(matlab_value):.17g}, "
                f"HGFX={float(hgfx_value):.17g}"
            )

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
        default=Path("reference/generated/m18_demo_uhgf_ar1_classification.json"),
    )
    args = parser.parse_args()

    matlab = json.loads(args.matlab_json.read_text(encoding="utf-8"))
    metadata = matlab["metadata"]
    if metadata["reference_commit"] != REFERENCE_COMMIT:
        raise AssertionError("Frozen MATLAB reference commit mismatch")
    if metadata["case_id"] != CASE_ID:
        raise AssertionError("Unexpected D04 reference case")

    inputs = np.loadtxt(args.demo_input, dtype=np.float64).reshape(-1)
    exported_inputs = _array(matlab["inputs"]).reshape(-1)
    if not np.array_equal(inputs, exported_inputs, equal_nan=True):
        raise AssertionError("MATLAB and HGFX are not using identical official demo inputs")

    p_uhgf = _array(matlab["uhgf_native_parameters"]).reshape(-1)
    p_ar1 = _array(matlab["uhgf_ar1_native_parameters"]).reshape(-1)
    hgfx_uhgf = _run("uhgf_binary", inputs, p_uhgf)
    hgfx_ar1 = _run("uhgf_ar1_binary", inputs, p_ar1)

    mismatches: list[str] = []
    mismatches.extend(_compare_variant("uhgf_binary", hgfx_uhgf, matlab["uhgf_binary"]))
    mismatches.extend(_compare_variant("uhgf_ar1_binary", hgfx_ar1, matlab["uhgf_ar1_binary"]))

    if not bool(matlab["uhgf_binary"]["success"]):
        mismatches.append("Frozen MATLAB uhgf_binary demo path unexpectedly failed")
    if not bool(matlab["uhgf_ar1_binary"]["success"]):
        mismatches.append("Frozen MATLAB uhgf_ar1_binary demo path unexpectedly failed")

    # Descriptive only: capture the reference's level-3 excursion comparison.
    matlab_excursion = {
        "uhgf_binary_max_abs_mu_level3": matlab["uhgf_binary"].get("max_abs_mu_level3"),
        "uhgf_ar1_binary_max_abs_mu_level3": matlab["uhgf_ar1_binary"].get("max_abs_mu_level3"),
    }
    hgfx_excursion = {
        "uhgf_binary_max_abs_mu_level3": hgfx_uhgf.get("max_abs_mu_level3"),
        "uhgf_ar1_binary_max_abs_mu_level3": hgfx_ar1.get("max_abs_mu_level3"),
    }

    classification = (
        "PASS_UHGF_AR1_WORKFLOW_PARITY" if not mismatches else "MODEL_SELECTION_MISMATCH"
    )
    result = {
        "schema_version": 1,
        "case_id": CASE_ID,
        "reference_commit": REFERENCE_COMMIT,
        "classification": classification,
        "mismatches": mismatches,
        "matlab": {
            "uhgf_binary": {
                "success": bool(matlab["uhgf_binary"]["success"]),
                "error_identifier": matlab["uhgf_binary"].get("error_identifier", ""),
                "error_message": matlab["uhgf_binary"].get("error_message", ""),
            },
            "uhgf_ar1_binary": {
                "success": bool(matlab["uhgf_ar1_binary"]["success"]),
                "error_identifier": matlab["uhgf_ar1_binary"].get("error_identifier", ""),
                "error_message": matlab["uhgf_ar1_binary"].get("error_message", ""),
            },
            "level3_excursion": matlab_excursion,
        },
        "hgfx": {
            "uhgf_binary": {"success": hgfx_uhgf["success"], "error": hgfx_uhgf["error"]},
            "uhgf_ar1_binary": {"success": hgfx_ar1["success"], "error": hgfx_ar1["error"]},
            "level3_excursion": hgfx_excursion,
        },
        "gate_semantics": (
            "Both official MATLAB model paths must execute and HGFX must reproduce their "
            "trajectories/inference states. Excursion reduction is recorded descriptively, "
            "not used as an invented acceptance threshold."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if mismatches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
