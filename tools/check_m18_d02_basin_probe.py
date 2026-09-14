#!/usr/bin/env python3
"""Classify D02 same-vector parity on the frozen cross-endpoint grid."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array

PROTOCOL = "m18-d02-basin-probe-1"
ALPHAS = np.asarray([0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0])
RTOL = 3e-8
ATOL = 3e-10


def main(hgfx_path: Path, matlab_path: Path, output_path: Path) -> int:
    hgfx = json.loads(hgfx_path.read_text())
    matlab = json.loads(matlab_path.read_text())
    if hgfx.get("protocol") != PROTOCOL:
        raise ValueError("HGFX protocol mismatch")
    if matlab.get("metadata", {}).get("protocol") != PROTOCOL:
        raise ValueError("MATLAB protocol mismatch")
    if hgfx.get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("HGFX reference commit mismatch")
    if matlab.get("metadata", {}).get("reference_commit") != REFERENCE_COMMIT:
        raise ValueError("MATLAB reference commit mismatch")
    if matlab.get("metadata", {}).get("numeric_encoding") != "ieee-strings-v1":
        raise ValueError("MATLAB numeric encoding mismatch")
    if hgfx.get("case_id") != "D02_fit" or matlab.get("case_id") != "D02_fit":
        raise ValueError("Unexpected case")
    if int(matlab.get("seed")) != 123456789:
        raise ValueError("Frozen seed mismatch")

    alphas = np.asarray(hgfx.get("alphas"), dtype=np.float64)
    if not np.array_equal(alphas, ALPHAS):
        raise ValueError("Frozen alpha grid mismatch")
    hvals = np.asarray(hgfx.get("hgfx_negLj"), dtype=np.float64).reshape(-1)
    mvals = _array(matlab["negLj"]).reshape(-1)
    if hvals.shape != ALPHAS.shape or mvals.shape != ALPHAS.shape:
        raise ValueError("Incomplete preregistered grid")

    close = np.isclose(hvals, mvals, rtol=RTOL, atol=ATOL, equal_nan=False)
    rows = []
    for i, alpha in enumerate(ALPHAS):
        abs_diff = float(abs(hvals[i] - mvals[i]))
        allowed = float(ATOL + RTOL * abs(mvals[i]))
        rows.append(
            {
                "alpha": float(alpha),
                "hgfx_negLj": float(hvals[i]),
                "matlab_negLj": float(mvals[i]),
                "abs_diff": abs_diff,
                "allowed_abs_diff": allowed,
                "pass": bool(close[i]),
            }
        )

    if np.all(close):
        classification = "OPTIMIZER_NUMERICAL_BASIN_CANDIDATE"
        next_action = (
            "Same-vector objective parity passes on the preregistered line. D02 remains "
            "BLOCKED because inference outputs differ materially; next diagnose conditioning, "
            "gradient amplification and optimizer-path sensitivity without changing the gate."
        )
    else:
        classification = "SAME_VECTOR_IMPLEMENTATION_MISMATCH"
        first = int(np.flatnonzero(~close)[0])
        next_action = (
            f"D02 remains BLOCKED. Localize the same-vector implementation mismatch at "
            f"alpha={ALPHAS[first]:.3f} before further optimizer work."
        )

    result = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "case_id": "D02_fit",
        "status": "BLOCKING",
        "classification": classification,
        "rtol": RTOL,
        "atol": ATOL,
        "endpoint_max_abs_diff": float(hgfx["endpoint_max_abs_diff"]),
        "rows": rows,
        "all_same_vector_points_pass": bool(np.all(close)),
        "next_action": next_action,
        "integrity_note": (
            "Classification only. The D02 release failure and inferential-equivalence failure "
            "remain unchanged; no seed, model, start, optimizer, grid or tolerance was relaxed."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"classification": classification, "all_pass": bool(np.all(close))}), flush=True)
    # A diagnostic classification is a successfully executed test even when it finds mismatch.
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hgfx", type=Path)
    parser.add_argument("matlab", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.hgfx, args.matlab, args.output))