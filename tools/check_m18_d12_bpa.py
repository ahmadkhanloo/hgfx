#!/usr/bin/env python3
"""Validate D12 Bayesian parameter averaging against frozen MATLAB evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat import CompatibilityResult, MatlabStruct, bayesian_parameter_average

PROTOCOL = "m18-d12-bpa-1"
RTOL = 3e-8
ATOL = 3e-10


def compare(label: str, actual: Any, expected: Any) -> dict[str, Any]:
    a = np.asarray(actual, dtype=np.float64)
    e = _array(expected)
    if a.shape != e.shape:
        if a.size == e.size:
            e = e.reshape(a.shape)
        else:
            return {
                "label": label,
                "pass": False,
                "reason": "shape",
                "actual_shape": list(a.shape),
                "expected_shape": list(e.shape),
            }
    close = np.isclose(a, e, rtol=RTOL, atol=ATOL, equal_nan=True)
    diff = np.abs(a - e)
    finite = np.isfinite(diff)
    if np.all(close):
        return {
            "label": label,
            "pass": True,
            "max_abs": float(np.max(diff[finite])) if np.any(finite) else 0.0,
        }
    idx = tuple(int(x) for x in np.argwhere(~close)[0]) if np.ndim(close) else ()
    av = a[idx] if idx else a
    ev = e[idx] if idx else e
    return {
        "label": label,
        "pass": False,
        "index": list(idx),
        "hgfx": float(av),
        "matlab": float(ev),
        "abs_diff": float(abs(av - ev)),
    }


def decode_estimate(item: dict[str, Any]) -> CompatibilityResult:
    c_prc = item["c_prc"]
    c_obs = item["c_obs"]
    return CompatibilityResult(
        kind="fit",
        u=_array(item["u"]),
        c_prc=MatlabStruct(
            {
                "model": c_prc["model"],
                "priormus": _array(c_prc["priormus"]),
                "priorsas": _array(c_prc["priorsas"]),
            }
        ),
        c_obs=MatlabStruct(
            {
                "model": c_obs["model"],
                "priormus": _array(c_obs["priormus"]),
                "priorsas": _array(c_obs["priorsas"]),
            }
        ),
        p_prc=MatlabStruct({"ptrans": _array(item["p_prc"]["ptrans"])}),
        p_obs=MatlabStruct({"ptrans": _array(item["p_obs"]["ptrans"])}),
        optim=MatlabStruct({"H": _array(item["optim"]["H"])}),
    )


def main(reference_path: Path, output_path: Path) -> int:
    reference = json.loads(reference_path.read_text())
    if reference.get("protocol") != PROTOCOL:
        raise ValueError("D12 protocol mismatch")
    if reference.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("D12 reference commit mismatch")
    if reference.get("case_id") != "D12_bpa" or [int(x) for x in reference.get("seeds", [])] != [123, 456]:
        raise ValueError("Frozen D12 case contract mismatch")

    estimates = [decode_estimate(item) for item in reference.get("estimates", [])]
    if len(estimates) != 2:
        raise ValueError("Frozen D12 requires exactly two estimates")
    result = bayesian_parameter_average(*estimates)
    expected = reference["bpa"]

    checks = [
        compare("optim.H", result.optim.H, expected["optim"]["H"]),
        compare("optim.Sigma", result.optim.Sigma, expected["optim"]["Sigma"]),
        compare("optim.Corr", result.optim.Corr, expected["optim"]["Corr"]),
        compare("p_prc.p", result.p_prc.p, expected["p_prc"]["p"]),
        compare("p_prc.ptrans", result.p_prc.ptrans, expected["p_prc"]["ptrans"]),
        compare("p_obs.p", result.p_obs.p, expected["p_obs"]["p"]),
        compare("p_obs.ptrans", result.p_obs.ptrans, expected["p_obs"]["ptrans"]),
    ]

    expected_traj = expected["traj"]
    for field, value in expected_traj.items():
        if field not in result.traj:
            checks.append({"label": f"traj.{field}", "pass": False, "reason": "missing_field"})
        else:
            checks.append(compare(f"traj.{field}", result.traj[field], value))

    failures = [item for item in checks if not item["pass"]]
    classification = "PASS" if not failures else "IMPLEMENTATION_MISMATCH"
    output = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D12_bpa",
        "classification": classification,
        "tolerance": {"rtol": RTOL, "atol": ATOL},
        "checks": checks,
        "failures": failures,
        "scope_note": (
            "The two MATLAB fit estimates are imported as frozen BPA inputs. "
            "This isolates D12 BPA algebra, transforms, covariance/correlation, and averaged trajectory from upstream optimizer parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"classification": classification, "failures": failures[:3]}), flush=True)
    return 0 if classification == "PASS" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reference, args.output))
