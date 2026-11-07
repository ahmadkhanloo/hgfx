#!/usr/bin/env python3
"""Compare HGFX-only and MATLAB-only PERF-01 preflights without granting parity PASS."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SCHEMA = "hgfx-runtime-paired-preflight-v1"


def compare(hgfx: dict, matlab: dict) -> dict:
    if hgfx["protocol_id"] != "hgfx-matlab-runtime-1":
        raise ValueError("Invalid HGFX protocol")
    if hgfx["hgfx_installed"] != "1.0.0":
        raise ValueError("Not the immutable HGFX v1 release")
    if matlab["oracle_expected_sha"] != "2437f4dc241541072722a2695ddeca7b44d83dd3":
        raise ValueError("Wrong MATLAB reference")
    if len(hgfx["cases"]) != 28 or len(matlab["cells"]) != 9:
        raise ValueError("Incomplete observed matrix")
    matlab_cells = {(x["model"], x["n_trials"]): x for x in matlab["cells"]}
    if len(matlab_cells) != 9:
        raise ValueError("Duplicated MATLAB cell")
    rows = []
    for cell in hgfx["cases"]:
        record = {
            "case_id": cell["case_id"],
            "stage": cell["stage"],
            "model": cell["model"],
            "n_trials": cell["n_trials"],
            "hgfx_status": cell["status"],
            "matlab_status": "NOT_RUN",
            "classification": "UNASSESSED",
        }
        if cell["tier"] == "throughput" or cell["stage"] == "fit_compat_full":
            record["classification"] = "NOT_RUN_FITTING_UNASSESSED"
        else:
            if cell["tier"] == "robustness":
                oracle = matlab["robustness"]
            else:
                oracle = matlab_cells[(cell["model"], cell["n_trials"])]
            ms = oracle["status"]
            hs = cell["status"]
            record["matlab_status"] = ms
            if ms == "MATLAB_PRIOR_START_MISMATCH":
                record["classification"] = "BLOCKED_CONTRACT_STARTS"
            elif ms == "MATLAB_ERROR":
                if hs == "HGFX_ONLY_ERROR":
                    record["classification"] = "BOTH_FAILED_UNCLASSIFIED"
                else:
                    record["classification"] = "MATLAB_ONLY_FAILED_UNCLASSIFIED"
                record["matlab_error"] = oracle.get("error_identifier", "")
                record["hgfx_error"] = cell.get("error", "")
            elif hs == "HGFX_ONLY_ERROR":
                record["classification"] = "HGFX_ONLY_FAILED_UNCLASSIFIED"
                record["hgfx_error"] = cell.get("error", "")
            elif ms.startswith("MATLAB_ONLY_") and hs.startswith("HGFX_ONLY_"):
                record["classification"] = "BOTH_COMPLETED_NUMERICAL_PARITY_NOT_ASSESSED"
                if cell["stage"] == "objective" and oracle.get("neg_log_joint") is not None:
                    m = float(oracle["neg_log_joint"])
                    h = float(cell["neg_log_joint"])
                    if math.isfinite(h) and math.isfinite(m):
                        record["neg_log_joint_abs_delta"] = abs(h-m)
                        record["neg_log_joint_rel_delta"] = abs(h-m)/max(abs(m), 1.0)
            else:
                record["classification"] = "UNASSESSED"
        rows.append(record)
    return {
        "schema": SCHEMA,
        "protocol_id": "hgfx-matlab-runtime-1",
        "status": "PRELIMINARY_ONLY_NUMERICAL_PARITY_UNASSESSED_PERFORMANCE_NOT_RUN",
        "hgfx_version": hgfx["hgfx_installed"],
        "matlab_release": matlab["matlab_release"],
        "matlab_oracle_sha": matlab["oracle_expected_sha"],
        "classification_counts": {
            status: sum(x["classification"] == status for x in rows)
            for status in sorted(set(x["classification"] for x in rows))
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hgfx", type=Path, required=True)
    parser.add_argument("--matlab", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = compare(json.loads(args.hgfx.read_bytes()), json.loads(args.matlab.read_bytes()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["classification_counts"], sort_keys=True))


if __name__ == "__main__":
    main()
