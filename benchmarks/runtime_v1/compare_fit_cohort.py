#!/usr/bin/env python3
"""Strict descriptive all-64 fitModel comparator for PERF-01D.

Never changes starts/subjects/tolerances or infers an eligible speedup.
Preserves all numerical mismatches and asymmetries in an indexed report.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from compare_fits import TOLS, numeric

HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
SUBJECTS = 64


def index(cases, name):
    if len(cases) != SUBJECTS:
        raise ValueError(f"{name} subjects missing, {len(cases)} != {SUBJECTS}")
    ids = [int(item["subject_index_zero_based"]) for item in cases]
    if sorted(ids) != list(range(SUBJECTS)):
        raise ValueError(f"{name} must include exactly all 64 subjects without duplicates")
    for record in cases:
        if record["model"] != "hgf_binary" or record["n_trials"] != 128:
            raise ValueError(f"{name} unexpected scientific model or trial horizon")
    return {i: row for i, row in zip(ids, cases)}


def compare(hgfx, matlab):
    if (
        hgfx.get("schema") != "perf01-hgfx-full-cohort-fit-v1"
        or matlab.get("schema") != "perf01-matlab-full-cohort-fit-v1"
        or hgfx.get("hgfx_distribution") != "1.0.0"
        or hgfx.get("release_expected_sha") != HGFX_SHA
        or matlab.get("oracle_expected_sha") != MATLAB_SHA
        or matlab.get("matlab_release") != "2026a"
    ):
        raise ValueError("Unverified HGFX/MATLAB scientific comparator")
    h = index(hgfx["cases"], "HGFX")
    m = index(matlab["cases"], "MATLAB")
    rows = []
    for subject in range(SUBJECTS):
        a, b = h[subject], m[subject]
        row = {
            "subject_index_zero_based": subject,
            "model": "hgf_binary",
            "trials": 128,
            "hgfx_status": a["status"],
            "matlab_status": b["status"],
            "hgfx_iteration_count": a["optimizer_iteration_count"],
            "matlab_iteration_count": b["optimizer_iteration_count"],
            "hgfx_n_rand_init": a["n_rand_init"],
            "matlab_n_rand_init": b["n_rand_init"],
            "initial_start_both_matched": bool(
                a["start_matches_frozen_snapshot"]
                and b["start_matches_frozen_snapshot"]
            ),
            "classification": "UNASSESSED",
        }
        if (
            a["status"] == "HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            and b["status"] == "MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            and row["initial_start_both_matched"]
            and row["hgfx_n_rand_init"] == row["matlab_n_rand_init"] == 0
        ):
            fields = {}
            for field, (rtol, atol) in TOLS.items():
                fields[field] = numeric(a["optim"][field], b["optim"][field], rtol, atol)
            for field in ("logjoint", "postpredcorr", "freepars"):
                fields["decompLME."+field] = numeric(
                    a["optim"]["decompLME"][field],
                    b["optim"]["decompLME"][field], 2e-6, 2e-8,
                )
            if set(a["traj"]) != set(b["traj"]):
                fields["trajectory_keys"] = {
                    "status": "TRAJECTORY_SCHEMA_MISMATCH",
                    "hgfx_keys": sorted(a["traj"]),
                    "matlab_keys": sorted(b["traj"]),
                }
            for field in set(a["traj"]) & set(b["traj"]):
                fields["traj."+field] = numeric(
                    a["traj"][field], b["traj"][field], 3e-8, 3e-10,
                )
            row["fields"] = fields
            failures = {
                field: data for field, data in fields.items()
                if data["status"] != "WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"
            }
            row["mismatched_fields"] = sorted(failures)
            if failures:
                row["classification"] = "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"
            else:
                row["classification"] = "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
            row["iteration_count_equal"] = (
                row["hgfx_iteration_count"] == row["matlab_iteration_count"]
            )
            if not row["iteration_count_equal"]:
                row["optimization_path_caveat"] = "ITERATION_COUNT_DIFFERS"
        elif (
            a["status"] == "HGFX_FULL_FIT_ERROR"
            and b["status"] == "MATLAB_FULL_FIT_ERROR"
        ):
            row["classification"] = "BOTH_FITS_FAILED_MECHANISM_UNVERIFIED"
            row["hgfx_error"] = a.get("error")
            row["matlab_error"] = b.get("error_identifier")
            row["matlab_message"] = b.get("error_message")
        elif (
            a["status"] == "HGFX_UNEXPECTED_RESTART_OR_START"
            or b["status"] == "MATLAB_UNEXPECTED_RESTART_OR_START"
            or not row["initial_start_both_matched"]
        ):
            row["classification"] = "BLOCKED_START_POLICY_NOT_MATCHED"
        else:
            row["classification"] = "ASYMMETRIC_FIT_OR_UNEXPECTED_ERROR"
            row["hgfx_error"] = a.get("error")
            row["matlab_error"] = b.get("error_identifier")
            row["matlab_message"] = b.get("error_message")
        rows.append(row)
    counts = dict(sorted(Counter(x["classification"] for x in rows).items()))
    by_prefix = []
    for prefix in (1, 16, 64):
        included = rows[:prefix]
        by_prefix.append({
            "subject_count": prefix,
            "numerical_output_concordant": sum(
                x["classification"] == "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
                for x in included
            ),
            "numerical_mismatch": sum(
                x["classification"] == "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"
                for x in included
            ),
            "failed_or_noncomparable": sum(
                x["classification"] not in (
                    "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES",
                    "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH",
                ) for x in included
            ),
            "identical_iteration_count": sum(
                x.get("iteration_count_equal", False) for x in included
            ),
        })
    return {
        "schema": "perf01-paired-full-cohort-fit-diagnostic-v1",
        "status": "UNFROZEN_DIAGNOSTIC_NO_TIMING_NO_SCIENTIFIC_PASS",
        "hgfx_sha": HGFX_SHA,
        "matlab_sha": MATLAB_SHA,
        "matlab_release": matlab["matlab_release"],
        "hgfx_input_sha256": hgfx["input_sha256"],
        "hgfx_config_sha256": hgfx["config_sha256"],
        "subject_count": SUBJECTS,
        "classification_counts": counts,
        "by_prefix": by_prefix,
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    for name in ("hgfx", "matlab", "output"):
        parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    result = compare(
        json.loads(args.hgfx.read_bytes()),
        json.loads(args.matlab.read_bytes()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+"\n")
    print(json.dumps({
        "cases": result["subject_count"],
        "classification_counts": result["classification_counts"],
        "by_prefix": result["by_prefix"],
    }, sort_keys=True))
    if set(result["classification_counts"]) - {
        "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES",
    }:
        raise SystemExit("PERF-01 fitting parity not met; complete failure evidence retained")


if __name__ == "__main__":
    main()
