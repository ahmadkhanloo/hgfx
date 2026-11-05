#!/usr/bin/env python3
"""Derive a NEW author-side optimizer trace report from immutable CI artifacts.

Historical run 42115887599 must not be overwritten. No MATLAB, HGFX,
timing or optimizer is executed by this check.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from compare_optimizer_trace_subject7 import compare

ORIGINAL_RUN = "42115887599"
ORIGINAL_SHA = "b378fef6ff93f6efa041f4e8304dafba742ae4ab"
EXPECTED_RAW = {
    "hgfx_raw.json": "6fe10be1dd1860612859e6efbe7bee13717e4787aed4a62f0e6b67a2072aac7a",
    "matlab_raw.json": "ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f",
}
NEW_FIELDS = {"first_any_nonzero_double_difference", "terminal_duplicate_finite_slots"}


def evaluate(root: Path) -> dict:
    old = json.loads((root / "summary.json").read_bytes())
    if (str(old.get("github_run_id")) != ORIGINAL_RUN
            or old.get("candidate_sha") != ORIGINAL_SHA
            or old.get("source_run_id") != "41863441006"
            or old.get("status") != "AUTHOR_SIDE_TRACE_DIAGNOSTIC_NOT_INDEPENDENTLY_REVIEWED_NOT_TIMED"
            or old.get("raw_evidence_sha256") != EXPECTED_RAW):
        raise ValueError("Original optimizer trace source identity/provenance mismatch")
    for name, checksum in EXPECTED_RAW.items():
        if sha256((root / name).read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Archived optimizer trace raw SHA256 mismatch: {name}")
    actual = compare(
        json.loads((root / "hgfx_raw.json").read_bytes()),
        json.loads((root / "matlab_raw.json").read_bytes()),
    )
    prior = {k: v for k, v in old.items()
             if k not in {"github_run_id", "candidate_sha", "raw_evidence_sha256",
                          "raw_evidence_location"}}
    if {k: v for k,v in actual.items() if k not in NEW_FIELDS} != prior:
        raise ValueError("Derived trace comparator rewrote original scientific diagnostics")
    exact = actual["first_any_nonzero_double_difference"]
    outside = actual["first_different_record"]
    if not (actual["recorded_finite_slots"] == {"hgfx":25,"matlab":25}
            and exact["record_index_zero_based"] == 1
            and outside["record_index_zero_based"] == 14
            and actual["terminal_duplicate_finite_slots"] == {"hgfx": True,"matlab": True}
            and actual["classification"] ==
            "OPTIMIZER_PATH_DIAGNOSTIC_ONLY_FULL_FIT_PARITY_NOT_PROMOTED"):
        raise ValueError("Archived subject-7 trace forensic findings changed")
    actual.update({
        "derived_from_original_run": ORIGINAL_RUN,
        "derived_from_original_candidate_sha": ORIGINAL_SHA,
        "derived_only_no_fresh_optimizer_execution": True,
        "original_raw_sha256": EXPECTED_RAW,
        "scientific_disposition": "INDEPENDENT_REVIEW_REQUIRED_63_OF_64_FITTING_NONPASS",
    })
    return actual


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = evaluate(a.archive)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+"\n")
    print(json.dumps({
        "original_run": ORIGINAL_RUN,
        "first_nonzero": report["first_any_nonzero_double_difference"],
        "first_outside_final_tolerance": report["first_different_record"],
        "finite_slots": report["recorded_finite_slots"],
        "termination_reason": report["termination_reason"],
        "scientific_disposition": report["scientific_disposition"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
