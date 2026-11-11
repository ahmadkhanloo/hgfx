#!/usr/bin/env python3
"""Fail-closed *draft-only* REV-2.3 eligibility ledger audit.

This checker cannot authorize scientific runs; post-review/frozen protocols
need their own explicitly reviewed gate version. No numerical model calls.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

WORKLOADS = {
    "F128": ("forward_filter", 128, 1),
    "F1024": ("forward_filter", 1024, 1),
    "F8192": ("forward_filter", 8192, 1),
    "F65536": ("forward_filter", 65536, 1),
    "S128": ("full_single_subject_fit", 128, 1),
    "S512": ("full_single_subject_fit", 512, 1),
    "B1": ("native_batch", 256, 1),
    "B32": ("native_batch", 256, 32),
    "B256": ("native_batch", 256, 256),
    "B1024": ("native_batch", 256, 1024),
    "D08": ("usdchf_full_fit", 614, 1),
}
BACKENDS = ("M-CPU", "H-COMP", "H-JCPU", "H-GPU1")
RELEASE_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def audit(manifest: object) -> dict:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return {"status": "BLOCKED_DRAFT_LEDGER", "errors": ["root must be object"],
                "scientific_validation": "NOT_EVALUATED", "timing_authorized": False}
    if manifest.get("schema") != "rev23-eligibility-draft-v1":
        errors.append("draft schema changed without a new review")
    if manifest.get("protocol_id") != "compstat-rev23-performance-1":
        errors.append("protocol ID changed")
    if manifest.get("status") != "DRAFT_NOT_FROZEN":
        errors.append("draft ledger cannot claim a frozen protocol")
    if manifest.get("perf01c_gate") != "BLOCK_FREEZE":
        errors.append("PERF-01C gate changed without independent approval")
    if manifest.get("independent_review") != "PENDING":
        errors.append("draft ledger must not claim independent approval")
    if manifest.get("timing_executed") is not False or manifest.get("recorded_speedups") != 0:
        errors.append("draft ledger contains timing or speed claims")
    versions = manifest.get("source_versions")
    if not isinstance(versions, dict):
        versions = {}
    if versions.get("hgfx_release_commit") != RELEASE_SHA or versions.get("matlab_toolbox_commit") != MATLAB_SHA:
        errors.append("frozen reference commit changed")
    if versions.get("hgfx_wheel_sha256") is not None or versions.get("matlab_release") is not None:
        errors.append("unverified runtime identity inserted into draft")
    repeats = manifest.get("study_repetition_policy")
    if not isinstance(repeats, dict) or (repeats.get("warmups"), repeats.get("timed_repeats"),
                                          repeats.get("precision")) != (1, 5, "float64"):
        errors.append("original repetition/precision design changed")
    workloads = manifest.get("workloads")
    if not isinstance(workloads, list):
        workloads = []
        errors.append("workloads must be a list")
    names = [w.get("id") for w in workloads if isinstance(w, dict)]
    if len(workloads) != len(WORKLOADS) or len(set(names)) != len(WORKLOADS) or set(names) != set(WORKLOADS):
        errors.append("original 11 workload IDs changed or duplicated")
    for work in workloads:
        if not isinstance(work, dict) or work.get("id") not in WORKLOADS:
            errors.append("invalid workload object")
            continue
        op, trials, subjects = WORKLOADS[work["id"]]
        if (work.get("operation"), work.get("trials"), work.get("subjects")) != (op, trials, subjects):
            errors.append(f"{work['id']}: operation/trial/subject scope changed")
        if work["id"] in ("S128", "S512") and work.get("model") != "hgf_binary":
            errors.append(f"{work['id']}: original fit model changed")
        if work["id"] == "D08" and (work.get("model"), work.get("observation")) != ("uhgf", "gaussian_obs"):
            errors.append("D08: original family changed")
        if work["id"].startswith(("F", "B")) and (work.get("model") is not None or work.get("observation") is not None):
            errors.append(f"{work['id']}: F/B author choice inserted before signed review")
    if manifest.get("backend_ids") != list(BACKENDS):
        errors.append("original four backend surfaces changed")
    expected = {f"{w}:{backend}" for w in WORKLOADS for backend in BACKENDS}
    cells = manifest.get("cells")
    if not isinstance(cells, list):
        cells = []
        errors.append("cells must be a list")
    ids = [cell.get("id") for cell in cells if isinstance(cell, dict)]
    if len(cells) != 44 or len(set(ids)) != 44 or set(ids) != expected:
        errors.append("44-cell denominator changed, duplicated or removed")
    for cell in cells:
        if not isinstance(cell, dict):
            errors.append("malformed cell")
            continue
        ident = cell.get("id", "?")
        if ident != f"{cell.get('workload_id')}:{cell.get('backend')}":
            errors.append(f"{ident}: workload/backend identity mismatch")
        if cell.get("eligibility") != "PENDING_INDEPENDENT_REVIEW":
            errors.append(f"{ident}: premature eligibility promotion")
        if cell.get("timing_status") != "NOT_RUN" or cell.get("scientific_status") != "NOT_ESTABLISHED":
            errors.append(f"{ident}: unsupported scientific or timing verdict")
        if cell.get("timed_values_seconds") != []:
            errors.append(f"{ident}: draft timing values must be empty")
        for key in ("input_sha256", "install_sha256", "host_id", "entrypoint", "parity_evidence"):
            if cell.get(key) is not None:
                errors.append(f"{ident}: unsupported {key} provenance inserted")
    if (manifest.get("candidate_cell_count"), manifest.get("eligible_cell_count"),
        manifest.get("blocked_or_review_pending_cell_count")) != (44, 0, 44):
        errors.append("denominators inconsistent with draft gates")
    return {"schema": "rev23_draft_ledger_audit_v1",
            "status": "DRAFT_STRUCTURE_CHECK_PASS" if not errors else "BLOCKED_DRAFT_LEDGER",
            "workloads_seen": len(workloads), "cells_seen": len(cells),
            "errors": errors,
            "scientific_validation": "NOT_EVALUATED",
            "timing_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = audit(data)
    except (OSError, ValueError) as exc:
        result = {"status": "BLOCKED_DRAFT_LEDGER", "errors": [str(exc)],
                  "scientific_validation": "NOT_EVALUATED", "timing_authorized": False}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "DRAFT_STRUCTURE_CHECK_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
