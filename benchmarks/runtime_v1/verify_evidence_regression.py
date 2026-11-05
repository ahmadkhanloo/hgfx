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
import math
import os
from pathlib import Path

from compare_trialwise import compare as compare_trialwise
from compare_fits import compare as compare_fits, TOLS as FIT_TOLS
from compare_all_subjects import analyze as compare_all_subjects
from compare_fit_cohort import compare as compare_fit_cohort
from compare_subject7_replay import classify as compare_subject7_replay
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
    followups = verify_subject7_followups(root, archives, raw_hashes)
    return {
        "status": "AUTHOR_SIDE_REAL_EVIDENCE_REGRESSION_NOT_INDEPENDENT_REVIEW_NOT_FROZEN_NOT_TIMED",
        "subject7_followup_evidence": followups,
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


def verify_reference_sensitivity(source: dict, original_matlab_fit: dict):
    """Check recorded MATLAB-only perturbations, not scientific acceptability."""
    require(source["schema"] == "perf01-subject7-matlab-self-sensitivity-v1"
            and source["matlab_reference_sha"] == IDENTITY["matlab"]
            and source["matlab_release"] == "2026a"
            and source["source_run_id"] == "41863441006"
            and source["subject_index_zero_based"] == 7
            and source["model"] == "hgf_binary"
            and source["trials"] == 128
            and source["opt_idx_one_based"] == [13, 14, 15],
            "Reference-only source/subject/model/optimizer identity changed")
    original = original_matlab_fit["cases"][7]["optim"]
    require(source["original_full_final"] == original["final"],
            "Reference sensitivity is not using original MATLAB fitted endpoint")
    require(source["original_optimal_negative_log_joint"] == original["negLj"],
            "Reference sensitivity is not using original MATLAB joint objective")
    baseline = source["reproduction"]
    require(baseline["status"] == "COMPLETED"
            and baseline["optimized_full_final"] == original["final"]
            and baseline["negative_log_joint"] == original["negLj"]
            and baseline["max_endpoint_shift"] == 0
            and baseline["outside_old_v1_final_parameter_tolerance"] is False,
            "Unperturbed independent MATLAB objective did not exactly reproduce frozen fit")
    probes = source["perturbations"]
    require(len(probes) == 6, "Must preserve all six MATLAB-only perturbation probes")
    actual = set()
    sensitive = []
    for probe in probes:
        coordinate = probe["free_coord_zero_based"]
        signed = float(probe["signed_step"])
        step = float(probe["step_size"])
        require(coordinate in (0, 1, 2) and step > 0
                and signed in (-step, step)
                and probe["status"] == "COMPLETED", "Invalid MATLAB-only perturbation probe")
        require(step == math.ulp(float(probe["original_start"])),
                "Reference sensitivity step is not one MATLAB eps(start) ULP")
        require(math.isclose(float(probe["original_start"]),
                             float(original_matlab_fit["cases"][7]["optim"]["init"][12+coordinate]),
                             rel_tol=0, abs_tol=0),
                "Original optimization start for reference probe changed")
        actual.add((coordinate, -1 if signed < 0 else 1))
        final = probe["optimized_full_final"]
        ref_final = source["original_full_final"]
        require(len(final) == len(ref_final), "Reference endpoint shape changed")
        require(all((x is None) == (y is None) for x, y in zip(final, ref_final)),
                "Reference nonfinite fixed-parameter mask changed")
        paired = [(float(x), float(y)) for x, y in zip(final, ref_final)
                  if x is not None and y is not None]
        require(paired and all(math.isfinite(x) and math.isfinite(y) for x, y in paired),
                "Reference sensitivity has invalid or empty finite endpoint pairs")
        calculated = max(abs(x-y) for x, y in paired)
        require(math.isclose(calculated, float(probe["max_endpoint_shift"]),
                             abs_tol=1e-14, rel_tol=1e-12),
                "Recorded reference endpoint shift differs from actual saved endpoint")
        rtol, atol = FIT_TOLS["final"]
        outside = any(abs(x-y) > atol + rtol*abs(y) for x, y in paired)
        require(outside == probe["outside_old_v1_final_parameter_tolerance"],
                "Recorded reference-limit boolean conflicts with original numerical threshold")
        if outside:
            sensitive.append((coordinate, -1 if signed < 0 else 1))
    require(len(actual) == 6 and actual ==
            {(i, sign) for i in range(3) for sign in (-1, 1)},
            "Missing or duplicate original +/-eps reference sensitivity probes")
    require(sensitive == [(2, -1)]
            and source["classification"] ==
                "REFERENCE_SELF_SENSITIVITY_CANDIDATE_NOT_INDEPENDENTLY_REVIEWED"
            and source["status"] == "DIAGNOSTIC_ONLY_NOT_SCIENTIFIC_PASS_NOT_TIMED",
            "Reference sensitivity must not be hidden or misclassified as scientific PASS")
    return {"original_probes": 6, "out_of_tolerance_probe": "free_coord_2_minus_eps",
            "max_shift": max(p["max_endpoint_shift"] for p in probes),
            "scientific_disposition": "INDEPENDENT_REVIEW_REQUIRED_NOT_PASS"}


def verify_subject7_followups(root: Path, archives: Path, raw_hashes: dict):
    """Recompute archived same-vector replay and verify MATLAB-only raw probe."""
    run = "41868723514"
    historical = read(root / f"subject7_results/summary-{run}.json")
    require(str(historical["github_run_id"]) == run,
            "Subject-7 cross-replay run identifier changed")
    expected = historical["raw_evidence_sha256"]
    require(set(expected) == {"hgfx_raw.json", "matlab_raw.json"},
            "Subject-7 replay raw evidence incomplete")
    for name, checksum in expected.items():
        require(digest(archives / run / name) == checksum,
                f"Subject-7 replay raw SHA-256 mismatch: {name}")
    recomputed = compare_subject7_replay(
        read(archives / run / "hgfx_raw.json"),
        read(archives / run / "matlab_raw.json"),
    )
    trimmed = {k: v for k, v in historical.items()
               if k not in {"github_run_id", "raw_evidence_sha256", "raw_evidence_location"}}
    require(recomputed == trimmed, "Same-vector subject-7 comparator regression")
    require(recomputed["classification"] ==
            "OPTIMIZER_ENDPOINT_SENSITIVITY_CANDIDATE_NOT_SCIENTIFIC_PASS"
            and len(recomputed["same_vector_cross_implementation"]) == 2
            and all(x["status"] == "SAME_VECTOR_OUTPUT_CONCORDANT_DIAGNOSTIC"
                    and len(x["fields"]) == 15 and not x["failed_fields"]
                    for x in recomputed["same_vector_cross_implementation"]),
            "Same-vector diagnostics incomplete or improperly promoted")
    raw_hashes[run] = expected
    print(f"REPLAY_MATCH {run} SHA256 and full 15-field two-endpoint comparator result")

    run = "41870479069"
    summary = read(root / f"matlab_sensitivity_results/summary-{run}.json")
    raw_path = archives / run / f"run-{run}.json"
    require(digest(raw_path) == summary["raw_evidence_sha256"],
            "Original MATLAB-only self-sensitivity raw JSON SHA-256 mismatch")
    require(str(summary["workflow_id"]) == run
            and summary["original_artifact"] == "perf01-64-full-fits-41863441006",
            "Reference-only sensitivity source artifact identity differs")
    original = read(raw_path)
    trimmed = {k: v for k, v in summary.items()
               if k not in {"workflow_id", "raw_evidence_sha256", "original_artifact"}}
    require(original == trimmed,
            "MATLAB sensitivity raw probe differs from archived summary")
    base_matlab_fit = read(archives / "41863441006" / "matlab_raw.json")
    sensitivity = verify_reference_sensitivity(original, base_matlab_fit)
    raw_hashes[run] = {"run-41870479069.json": summary["raw_evidence_sha256"]}
    print(f"REPLAY_MATCH {run} raw SHA256, exact baseline, all six +/-eps probes")
    return {"two_exact_endpoints_and_15_fields": "REPLAY_MATCH",
            "reference_sensitivity": sensitivity}



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
