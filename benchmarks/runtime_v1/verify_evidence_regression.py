#!/usr/bin/env python3
"""Recompute PERF-01C candidate diagnostics from ORIGINAL CI raw exports.

Author-side regression only. No MATLAB runs, no timing, no protocol freeze,
no acceptance threshold changes and no independent scientific sign-off.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path

from compare_trialwise import compare as compare_trialwise
from compare_fits import compare as compare_fits
from compare_all_subjects import analyze as compare_all_subjects
from compare_fit_cohort import compare as compare_fit_cohort
from build_eligibility_candidate import classify
from refine_eligibility_fit_cohort import refine

IDENTITY = {
    "hgfx": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
    "matlab": "2437f4dc241541072722a2695ddeca7b44d83dd3",
}
SOURCES = (
    ("41854644533", "trialwise_results/summary-41854644533.json", compare_trialwise),
    ("41855647245", "fitting_results/summary-41855647245.json", compare_fits),
    ("41860187774", "cohort_results/summary-41860187774.json", compare_all_subjects),
    ("41863441006", "fit_cohort_results/summary-41863441006.json", compare_fit_cohort),
)


def read(path: Path):
    return json.loads(path.read_bytes())


def digest(path: Path):
    return sha256(path.read_bytes()).hexdigest()


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def verify(root: Path, archives: Path):
    registry = root / "inputs_manifest.json"
    configs = root / "resolved_configs_manifest.json"
    manifest, config_manifest = read(registry), read(configs)
    manifest_hash = digest(registry)
    config_hash = digest(configs)

    require(manifest["case_count"] == len(manifest["cases"]) == 28
            and len({c["id"] for c in manifest["cases"]}) == 28,
            "Original 28-case registry changed")
    require(manifest["product_source_sha"] == IDENTITY["hgfx"]
            and manifest["matlab_oracle_sha"] == IDENTITY["matlab"],
            "Original comparator identity changed")
    require(config_manifest["input_manifest_sha256"] == manifest_hash
            and config_manifest["hgfx_source_expected_sha"] == IDENTITY["hgfx"]
            and config_manifest["matlab_reference_expected_sha"] == IDENTITY["matlab"],
            "Configuration provenance changed")
    require(len(config_manifest["entries"]) == 9, "Nine resolved configs missing")
    for case in manifest["cases"]:
        require(digest(root / case["source_file"]) == case["source_sha256"],
                f"Dataset bytes differ: {case['source_file']}")
    for entry in config_manifest["entries"]:
        require(digest(root / entry["config_file"]) == entry["config_sha256"],
                f"Config bytes differ: {entry['config_file']}")
        require(digest(root / entry["source_file"]) == entry["source_sha256"],
                f"Config source bytes differ: {entry['source_file']}")

    results, raw_hashes = {}, {}
    for run_id, relpath, comparator in SOURCES:
        historical = read(root / relpath)
        require(str(historical["github_run_id"]) == run_id,
                f"Archived run identity mismatch: {run_id}")
        expected = historical["raw_evidence_sha256"]
        require(set(expected) == {"hgfx_raw.json", "matlab_raw.json"},
                f"Raw file inventory incomplete: {run_id}")
        for name, checksum in expected.items():
            require(digest(archives / run_id / name) == checksum,
                    f"Raw evidence SHA-256 mismatch: {run_id}/{name}")
        recomputed = comparator(
            read(archives / run_id / "hgfx_raw.json"),
            read(archives / run_id / "matlab_raw.json"),
        )
        historical_without_provenance = {
            k: v for k, v in historical.items()
            if k not in {"github_run_id", "raw_evidence_sha256", "raw_evidence_location"}
        }
        require(recomputed == historical_without_provenance,
                f"Raw comparator regression: {run_id}")
        results[run_id] = recomputed
        raw_hashes[run_id] = expected
        print(f"REPLAY_MATCH {run_id} SHA256 and full comparator result")

    trialwise = results["41854644533"]
    counts = dict(Counter(r["diagnostic_classification"] for r in trialwise["rows"]))
    require(len(trialwise["rows"]) == 10 and counts == {
        "FULL_TRIALWISE_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE": 7,
        "BOTH_FAILED_FIRST_INVALID_PREFIX_AGREES_UNVERIFIED_MECHANISM": 3,
    }, "Trialwise denominator/status regression")
    invalid_prefix = {
        (r["model"], r["trials"], r["masked"]):
            r["hgfx_prefix"]["first_invalid_prefix_length"]
        for r in trialwise["rows"]
        if r["diagnostic_classification"].startswith("BOTH_FAILED")
    }
    require(invalid_prefix == {
        ("hgf_binary", 512, False): 348,
        ("hgf_binary", 1024, False): 346,
        ("hgf_binary", 512, True): 349,
    }, "Changed invalid-prefix evidence")

    cohort = results["41860187774"]
    require(len(cohort["rows"]) == 576 and len(cohort["strata"]) == 27,
            "576-case denominator regression")
    require(cohort["classification_counts"] == {
        "COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE": 448,
        "BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC": 128,
    }, "Cohort classification regression")
    fit = results["41863441006"]
    require(len(fit["cases"]) == 64
            and [x["numerical_output_concordant"] for x in fit["by_prefix"]]
            == [1, 15, 63], "64-subject fit cohort changed")
    mismatch = [r for r in fit["cases"]
                if r["classification"] == "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"]
    require(len(mismatch) == 1 and mismatch[0]["subject_index_zero_based"] == 7
            and mismatch[0]["mismatched_fields"] == ["traj.mu", "traj.muhat"],
            "Original subject-7 mismatch missing or modified")

    original_path = root / (
        "eligibility_candidates/"
        "trialwise41854644533_fit41855647245_cohort41860187774.json"
    )
    original = read(original_path)
    reconstructed = classify(
        dict(manifest, _bytes_sha256=manifest_hash),
        trialwise, results["41855647245"], cohort,
    )
    reconstructed["evidence_sha256"] = {
        "manifest": manifest_hash,
        "trialwise": digest(root / SOURCES[0][1]),
        "fitting": digest(root / SOURCES[1][1]),
        "cohort": digest(root / SOURCES[2][1]),
    }
    require(reconstructed == original, "Original 28-case ledger differs")
    refined = refine(original, fit)
    refined["source_evidence_sha256"] = {
        "original_candidate": digest(original_path),
        "64_subject_fit_diagnostic": digest(root / SOURCES[3][1]),
    }
    require(refined == read(root / "eligibility_candidates/candidate_v2_fullfit41863441006.json"),
            "Follow-up 28-case ledger differs")
    require(len(refined["cases"]) == 28
            and len(refined["blocked_case_ids"]) == 12
            and refined["classification_counts"]["DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"] == 16
            and not refined["primary_nine_aggregate_eligible"]
            and refined["independent_review"] == "NOT_RECEIVED"
            and refined["no_timing"] is True,
            "Unapproved eligibility has been promoted or evidence excluded")
    return {
        "status": "AUTHOR_SIDE_REAL_EVIDENCE_REGRESSION_NOT_INDEPENDENT_REVIEW_NOT_FROZEN_NOT_TIMED",
        "candidate_sha": os.environ.get("GITHUB_SHA", "LOCAL_UNVERIFIED"),
        "frozen_source_shas": IDENTITY,
        "input_manifest_sha256": manifest_hash,
        "config_manifest_sha256": config_hash,
        "raw_artifact_sha256": raw_hashes,
        "trialwise_10": counts,
        "cohort_576": cohort["classification_counts"],
        "full_fit_64": fit["classification_counts"],
        "original_cases_28": refined["classification_counts"],
        "independent_review": "NOT_RECEIVED",
        "perf01c_gate": "OPEN_NOT_FROZEN",
        "timings_executed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.root, args.archives)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
