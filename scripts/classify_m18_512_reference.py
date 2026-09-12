#!/usr/bin/env python3
"""Classify issue #25 after the frozen MATLAB 512-trial run exists."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", default="reference/generated/m18_512_hgf")
    parser.add_argument("--atol", type=float, default=1e-8)
    parser.add_argument("--rtol", type=float, default=1e-7)
    args = parser.parse_args()
    root = Path(args.case_dir)
    matlab_path = root / "matlab" / "result.json"
    if not matlab_path.exists():
        print(json.dumps({"classification": "INSUFFICIENT_REFERENCE_EVIDENCE", "reason": "MATLAB result.json missing"}, indent=2))
        raise SystemExit(3)

    matlab = json.loads(matlab_path.read_text(encoding="utf-8"))
    if matlab.get("status") != "OK":
        print(json.dumps({
            "classification": "REFERENCE_LIMITATION_MATCH",
            "reason": "Frozen MATLAB reference fails on the identical case",
            "matlab_error_identifier": matlab.get("error_identifier"),
            "matlab_error_message": matlab.get("error_message"),
        }, indent=2))
        return

    python = json.loads((root / "responses.json").read_text(encoding="utf-8"))
    matlab_y = np.asarray(matlab.get("y", []), dtype=np.float64).reshape(-1)
    python_y = np.asarray(python["y"], dtype=np.float64).reshape(-1)
    n = min(matlab_y.size, python_y.size)
    if n == 0 or matlab_y.size != python_y.size:
        classification = "IMPLEMENTATION_MISMATCH"
        first = 0
        max_gap = None
    else:
        close = np.isclose(matlab_y, python_y, atol=args.atol, rtol=args.rtol, equal_nan=True)
        bad = np.flatnonzero(~close)
        first = int(bad[0]) if bad.size else None
        max_gap = float(np.nanmax(np.abs(matlab_y - python_y)))
        classification = "IMPLEMENTATION_MISMATCH" if bad.size else "INSUFFICIENT_REFERENCE_EVIDENCE"

    print(json.dumps({
        "classification": classification,
        "reason": (
            "MATLAB is valid but simulated outputs diverge" if classification == "IMPLEMENTATION_MISMATCH"
            else "MATLAB simulation is valid and y matches; compare latent trajectories/fit path before final classification"
        ),
        "first_response_divergence_zero_based": first,
        "max_abs_response_gap": max_gap,
        "matlab_status": matlab.get("status"),
    }, indent=2))
    if classification == "IMPLEMENTATION_MISMATCH":
        raise SystemExit(2)
    raise SystemExit(3)


if __name__ == "__main__":
    main()
