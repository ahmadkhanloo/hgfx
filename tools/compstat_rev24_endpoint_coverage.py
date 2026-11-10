#!/usr/bin/env python3
"""REV-2.4 Panel E ORIGINAL source coverage; no optimization or objective calls.

Consume three historical, SHA-pinned GitHub Actions ZIPs plus the original
PERF-01D source-commit fixture. Never serialize any subject data or endpoints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from tools.compstat_rev24_endpoint_sources import SOURCES, audit_sources, require

COHORT_INPUT_SHA256 = "6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae"
COHORT_INPUT_SOURCE_COMMIT = "81ae256b318e18ea08b03ab6fcb69100ac6c836d"
COHORT_INPUT_GIT_BLOB = "bb8989b96de1cbe66a6b880a0146b82a9b1817dc"
COHORT_INPUT_REPO_PATH = "benchmarks/runtime_v1/inputs/binary_128_s64.json"
COHORT_CONFIG_SHA256 = "2523e0438fe28ca5f6e4bdf0c8b8530fb0b3cbe5cc50a87f5b5b55dbfd56c180"


def read_zip_json(path: Path, filename: str) -> dict:
    with ZipFile(path) as archive:
        require(filename in archive.namelist(), f"Original ZIP missing {filename}")
        value = json.loads(archive.read(filename))
    require(isinstance(value, dict), f"Malformed archived {filename}")
    return value


def vector(value, count: int, context: str) -> None:
    require(isinstance(value, list) and len(value) == count,
            f"{context}: expected full {count}-parameter original endpoint")
    for v in value:
        require(v is None or isinstance(v, (int, float, str)),
                f"{context}: invalid original endpoint encoding")


def cohort_source(path: Path) -> dict:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == COHORT_INPUT_SHA256, "Original cohort input SHA256 mismatch")
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()
    require(git_blob == COHORT_INPUT_GIT_BLOB,
            "Original run-commit source fixture git blob mismatch")
    data = json.loads(raw)
    require(data.get("seed") == 20261232 and data.get("trial_count") == 128
            and data.get("subject_count") == 64, "Original cohort fixture grid changed")
    require(data.get("subject_indices_zero_based") == list(range(64)),
            "Original subject order changed")
    for field in ("u", "y"):
        rows = data.get(field)
        require(isinstance(rows, list) and len(rows) == 64, "Missing original input rows")
        require(all(isinstance(row, list) and len(row) == 128 for row in rows),
                "Malformed original input trial count")
    return {
        "sha256": digest,
        "git_blob_sha1": git_blob,
        "source_commit": COHORT_INPUT_SOURCE_COMMIT,
        "source_path": COHORT_INPUT_REPO_PATH,
        "subject_count": 64,
        "trials": 128,
    }


def audit_coverage(d02: Path, d08: Path, cohort64: Path,
                   cohort_input: Path) -> dict:
    archive_sources = audit_sources({
        "d02": d02, "d08": d08, "cohort64": cohort64,
    })
    original_input = cohort_source(cohort_input)

    d02_data = read_zip_json(d02, "m18_workflows.json")
    d02_matches = [row for row in d02_data["cases"] if row.get("id") == "D02_fit"]
    require(len(d02_matches) == 1, "Original D02_fit identity not unique")
    case = d02_matches[0]
    require(case.get("model") == "ehgf_binary"
            and case.get("observation") == "unitsq_sgm"
            and case.get("seed") == 123456789,
            "D02 original model/seed changed")
    require(len(case["inputs"]) == len(case["responses"]) == 320,
            "D02 original trial length wrong")
    tagged = case["fit"]["final"]
    require(tagged.get("shape") == [1, 15], "D02 original full endpoint shape changed")
    vector(tagged["data"], 15, "D02 MATLAB")

    d08_data = read_zip_json(d08, "m18_d08_endpoint.json")
    d08_comparison = read_zip_json(d08, "m18_d08_endpoint_comparison.json")
    require(d08_data.get("case_id") == "D08_fit"
            and d08_data.get("model") == "uhgf"
            and d08_data.get("observation") == "gaussian_obs",
            "D08 original model family mismatch")
    require(len(d08_data["inputs"]) == len(d08_data["responses"]) == 614,
            "D08 original trial length changed")
    vector(d08_data["final"], 11, "D08 MATLAB")
    endpoint_rows = d08_comparison.get("endpoint_parameters", [])
    require(isinstance(endpoint_rows, list) and len(endpoint_rows) == 11,
            "D08 both-endpoint parameter record incomplete")
    require([row.get("index") for row in endpoint_rows] == list(range(11)),
            "D08 original parameter ordering changed")
    require(all(row.get("matlab") == d08_data["final"][i]
                for i, row in enumerate(endpoint_rows)),
            "D08 archived MATLAB endpoints disagree between source records")
    for row in endpoint_rows:
        require(isinstance(row.get("hgfx"), (int, float)) and
                math.isfinite(row["hgfx"]),
                "D08 original HGFX parameter missing/nonfinite")

    hgfx = read_zip_json(cohort64, "hgfx_raw.json")
    matlab = read_zip_json(cohort64, "matlab_raw.json")
    require(hgfx.get("input_sha256") == original_input["sha256"],
            "Original HGFX full-fit input does not match source fixture")
    require(hgfx.get("config_sha256") == COHORT_CONFIG_SHA256,
            "Original 64-subject config changed")
    coverage = {}
    for side, result in (("hgfx", hgfx), ("matlab", matlab)):
        require(result.get("model") == "hgf_binary" and
                result.get("observation_model") == "unitsq_sgm",
                f"{side}: original cohort model family changed")
        require(result.get("subjects") == 64 and result.get("trials") == 128,
                f"{side}: original cohort dimensions changed")
        rows = result.get("cases")
        require(isinstance(rows, list) and len(rows) == 64,
                f"{side}: original case count not 64")
        require([row.get("subject_index_zero_based") for row in rows]
                == list(range(64)), f"{side}: missing or reordered subject")
        for row in rows:
            i = row["subject_index_zero_based"]
            require(row.get("start_matches_frozen_snapshot") is True,
                    f"{side}: start mismatch subject {i}")
            require(isinstance(row.get("optim"), dict),
                    f"{side}: missing original optimizer endpoint subject {i}")
            endpoint = row["optim"].get("final")
            vector(endpoint, 15, f"{side}: subject {i}")
            require(all(isinstance(endpoint[k], (int, float)) and
                        math.isfinite(endpoint[k]) for k in (12, 13, 14)),
                    f"{side}: missing original free endpoint subject {i}")
        coverage[side] = {"original_cases": 64, "original_full_endpoints": 64,
                          "parameters_per_endpoint": 15,
                          "source_raw": f"{side}_raw.json"}

    return {
        "protocol": "compstat-rev2-4-objective-cross-eval-v1",
        "panel": "E",
        "status": "SOURCE_COVERAGE_ONLY_NOT_OBJECTIVE_PARITY",
        "original_archives": archive_sources["sources"],
        "cases": [
            {"id": "D02_fit", "model": "ehgf_binary + unitsq_sgm",
             "trials": 320, "original_matlab_endpoint": True,
             "original_hgfx_full_endpoint": "NOT_FOUND_IN_PINNED_ARCHIVE",
             "endpoint_parameter_count": 15,
             "objective_cross_evaluated": False},
            {"id": "D08_fit", "model": "uhgf + gaussian_obs",
             "trials": 614, "original_matlab_endpoint": True,
             "original_hgfx_full_endpoint": True,
             "endpoint_parameter_count": 11,
             "objective_cross_evaluated": False},
            {"id": "cohort64", "model": "hgf_binary + unitsq_sgm",
             "trials_per_subject": 128, "expected_subjects": 64,
             "full_endpoint_counts": coverage,
             "original_input": original_input,
             "objective_cross_evaluated": False},
        ],
        "d02_hgfx_original_endpoint_blocker":
            "Full original HGFX 15-vector not present in checked official artifact; "
            "first-divergence scalar is not an endpoint replacement",
        "source_git_commit_does_not_imply_scientific_success": True,
        "participant_data_in_report": False,
        "matlab_hgfx_paired_objective_executed": False,
        "scientific_gate": "NOT_ASSESSED",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    for key in ("d02", "d08", "cohort64", "cohort_input", "output"):
        ap.add_argument("--" + key.replace("_", "-"), type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "Original source coverage audit cannot be overwritten")
    result = audit_coverage(args.d02, args.d08, args.cohort64, args.cohort_input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "cohort_original_endpoints": "64/64 per implementation",
                      "d02_hgfx_original_endpoint": "NOT_FOUND_IN_PINNED_ARCHIVE",
                      "scientific_gate": result["scientific_gate"]}, sort_keys=True))


if __name__ == "__main__":
    main()
