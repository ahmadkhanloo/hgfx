#!/usr/bin/env python3
"""PERF-01C: cross-ledger consistency guard for independent-review handoff.

Verifies *tracked DERIVED JSON* under the current source checkout, not remote
raw Actions artifacts, live MATLAB/HGFX scientific compatibility, or an
independent reviewer decision. Never changes the release/acceptance gate.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
MODELS = ("ehgf_binary", "hgf_binary", "uhgf_binary")
TRIALS = (128, 512, 1024)
SUBJECTS = tuple(range(64))
FAIL_FIELDS = ("traj.mu", "traj.muhat")
OLD_CLASS = "BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED"
NEW_CLASS = "BLOCKED_MULTISUBJECT_FIT_NUMERICAL_MISMATCH"
MISMATCH_CASES = {"throughput_fit_16x128", "throughput_fit_64x128"}
EXPECTED_CLASSES = {
    "BLOCKED_INVALID_FROZEN_REFERENCE_WORKLOAD": 8,
    NEW_CLASS: 2,
    "BLOCKED_NONCOMPARABLE_FITTING_START_POLICY": 2,
    "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING": 16,
}
PATHS = {
    "cohort": "benchmarks/runtime_v1/cohort_results/summary-41860187774.json",
    "fit": "benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json",
    "original": "benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json",
    "candidate": "benchmarks/runtime_v1/eligibility_candidates/candidate_v2_fullfit41863441006.json",
    "abba": "benchmarks/runtime_v1/issue90_results/derived-archived-v2-42250539438.json",
}
ORDER = ("SkylakeX_1", "Haswell_1", "Haswell_2", "SkylakeX_2")
PAIRS = {
    "SkylakeX_within_mode": ("SkylakeX_1", "SkylakeX_2"),
    "Haswell_within_mode": ("Haswell_1", "Haswell_2"),
    "cross_mode_first": ("SkylakeX_1", "Haswell_1"),
    "cross_mode_second": ("SkylakeX_2", "Haswell_2"),
    "cross_mode_interleaved_a": ("SkylakeX_1", "Haswell_2"),
    "cross_mode_interleaved_b": ("SkylakeX_2", "Haswell_1"),
}
RESULT_STATUS = "AUTHOR_SIDE_TRACKED_LEDGER_CONSISTENT_NOT_INDEPENDENT_REVIEW"
OLDS = {"traj.mu": [83, 1], "traj.muhat": [84, 1]}

def require(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)

def load(root: Path) -> tuple[dict, dict]:
    reports, digests = {}, {}
    for key, relative in PATHS.items():
        p = root / relative
        raw = p.read_bytes()  # file must exist, no fallback to rewritten evidence
        reports[key] = json.loads(raw)
        digests[key] = hashlib.sha256(raw).hexdigest()
    return reports, digests

def check_cohort(d):
    require(d.get("github_run_id") == "41860187774" and
            d.get("hgfx_source_sha") == HGFX and d.get("matlab_oracle_sha") == MATLAB,
            "cohort frozen source/run identity")
    rows = d["rows"]
    expected = {(model, trial, index) for model in MODELS for trial in TRIALS
                for index in SUBJECTS}
    keys = [(r["model"], r["trials"], r["subject_index_zero_based"]) for r in rows]
    require(len(rows) == 576 and len(set(keys)) == 576 and set(keys) == expected,
            "cohort 576-case unique cartesian denominator changed")
    classifications = Counter(row["classification"] for row in rows)
    require(dict(classifications) == {
        "COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE": 448,
        "BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC": 128,
    } and dict(classifications) == d["classification_counts"],
            "cohort 448/128 outcome changed")
    for r in rows:
        expected_invalid = (r["model"] == "hgf_binary" and r["trials"] in (512, 1024))
        require(r["config_both_verified"] is True, "cohort config not verified")
        require((r["classification"] == "BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC") == expected_invalid,
                "cohort invalid horizon/model eligibility changed")
    require(d.get("status") == "DIAGNOSTIC_ONLY_NO_TIMING_NO_SCIENTIFIC_PASS" and
            d.get("rtol") == 3e-8 and d.get("atol") == 3e-10,
            "cohort diagnostic only and unchanged threshold")
    return {"rows": 576, "completed": 448, "both_invalid": 128}

def check_fit(d):
    require(d.get("github_run_id") == "41863441006" and d.get("hgfx_sha") == HGFX
            and d.get("matlab_sha") == MATLAB and d.get("subject_count") == 64,
            "fit archived 64-source identity changed")
    rows = d["cases"]
    require(len(rows) == 64 and [r["subject_index_zero_based"] for r in rows] == list(SUBJECTS),
            "fit exact 64 original subjects missing/reordered")
    counts = Counter(r["classification"] for r in rows)
    require(dict(counts) == {
        "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
        "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1
    } and d["classification_counts"] == dict(counts), "original 63/64 mismatch lost")
    inventory = set(rows[0]["fields"])
    require(len(inventory) == 28, "original 28-field fit inventory changed")
    for r in rows:
        idx = r["subject_index_zero_based"]
        fails = list(FAIL_FIELDS) if idx == 7 else []
        require(set(r["fields"]) == inventory and r["mismatched_fields"] == fails and
                r["model"] == "hgf_binary" and r["trials"] == 128,
                "fit subject per-field model/failure inventory changed")
        require(r["initial_start_both_matched"] is True and
                r["hgfx_n_rand_init"] == r["matlab_n_rand_init"] == 0,
                "fit start / restart pairing changed")
        for name, rec in r["fields"].items():
            bad = name in fails
            require(rec.get("status") == ("MISMATCH" if bad else "WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE")
                    and rec.get("mismatch_count") == (4 if bad else 0),
                    "fit numerical field outcome/mismatch count changed")
            if name.startswith("traj."):
                require((rec["rtol"], rec["atol"]) == (3e-8, 3e-10),
                        "original fit trajectory tolerance changed")
        if idx == 7:
            for name in FAIL_FIELDS:
                rec = r["fields"][name]
                require(rec["first_mismatch_index_zero_based"] == OLDS[name] and
                        rec["max_abs_delta"] == 1.5704625655477145e-9,
                        "original subject7 first mismatch/max delta changed")
    require([(x["subject_count"], x["numerical_output_concordant"],
              x["numerical_mismatch"], x["failed_or_noncomparable"])
             for x in d["by_prefix"]] == [(1,1,0,0),(16,15,1,0),(64,63,1,0)],
            "fit nested denominators 1/1 15/16 63/64 changed")
    return {"fitting": "63/64 NONPASS", "failed_subject_index_zero_based": 7,
            "failed_fields": list(FAIL_FIELDS)}

def check_eligibility(old, new):
    require(old["status"] == new["status"] ==
            "AUTHOR_SIDE_INVENTORY_ONLY_NOT_REVIEWED_NOT_FROZEN_NOT_TIMED",
            "candidate is not independent gate/benchmark")
    require(old["total_predeclared_cases"] == new["original_cases_total"] == 28
            and new["new_fitting_source_run_id"] == "41863441006"
            and new["independent_review"] == "NOT_RECEIVED"
            and new["primary_nine_aggregate_eligible"] is False
            and new["no_timing"] is True,
            "candidate frozen 28 cells/review/timing status changed")
    a, b = old["cases"], new["cases"]
    require(len(a) == len(b) == 28 and
            [x["case_id"] for x in a] == [x["case_id"] for x in b] and
            len({x["case_id"] for x in a}) == 28,
            "candidate original 28-case order/identity changed")
    expected_additions = {
        "throughput_fit_1x128": (1,1,0),
        "throughput_fit_16x128": (16,15,1),
        "throughput_fit_64x128": (64,63,1),
    }
    modified = []
    for one, two in zip(a,b):
        key=one["case_id"]
        if key not in expected_additions:
            require(one == two, "candidate unauthorized change outside 3 exact original fitting cells")
            continue
        submitted,concordant,mismatched = expected_additions[key]
        require("additional_fitting_evidence" not in one and
                "previous_classification" not in one,
                "candidate original historical fitting evidence was rewritten")
        annotation=two.get("additional_fitting_evidence")
        expected_annotation={
            "submitted":submitted, "same_numerical_output":concordant,
            "numerical_mismatch":mismatched, "other_failures_or_noncomparable":0,
            "source_run_id":"41863441006",
            "scientific_status":"DIAGNOSTIC_ONLY_NOT_INDEPENDENTLY_APPROVED",
        }
        require(annotation == expected_annotation, "candidate exact new full-fit evidence annotation changed")
        old_core = {k:v for k,v in one.items()}
        new_core = {k:v for k,v in two.items()
                    if k not in ("additional_fitting_evidence","previous_classification")}
        if key in MISMATCH_CASES:
            require(one["classification"] == OLD_CLASS and
                    two["classification"] == NEW_CLASS and
                    two.get("previous_classification") == OLD_CLASS,
                    "candidate prior blocked classification not preserved")
            old_core["classification"] = NEW_CLASS
            modified.append(key)
        else:
            require("previous_classification" not in two and
                    two["classification"] == one["classification"] ==
                    "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING",
                    "candidate original one-subject fit review status changed")
        require(old_core == new_core,
                "candidate unsupported changes beyond prespecified fitting evidence/classification")
    require(set(modified) == MISMATCH_CASES, "candidate two blocked fitting reasons absent")
    classes = Counter(x["classification"] for x in b)
    require(dict(classes) == EXPECTED_CLASSES and new["classification_counts"] == dict(classes)
            and set(new["blocked_case_ids"]) ==
            {x["case_id"] for x in b if x["classification"].startswith("BLOCKED_")}
            and len(new["blocked_case_ids"]) == 12,
            "candidate 16 pending and 12 blocked accounting changed")
    return {"total": 28, "review_pending": 16, "blocked": 12,
            "additional_exact_full_fit_evidence": sorted(expected_additions),
            "newly_evidenced_blocked_fitting_cases": sorted(MISMATCH_CASES)}

def check_abba(d, fit):
    p = d["analysis_provenance"]
    require(d["schema"] == "perf01d-issue90-same-host-abba-explicit-coretype-v2"
            and d["status"] == "AUTHOR_SIDE_ABBA_V2_EXPLICIT_CORES_DIAGNOSTIC_ORIGINAL_63_OF_64_NONPASS"
            and d["frozen_hgfx_sha"] == HGFX and d["frozen_matlab_sha"] == MATLAB,
            "ABBA diagnostic identity or science promotion")
    require(d["original_64_fit_run"] == "41863441006"
            and d["original_64_raw_sha256"] == fit["raw_evidence_sha256"]
            and d["original_science"] == "63/64 NONPASS; original subject zero-based 7"
            and d["original_failed_fields"] == list(FAIL_FIELDS)
            and d["original_failed_cells"] == {k: 4 for k in FAIL_FIELDS},
            "ABBA original scientific non-PASS preservation")
    require(p["analysis_run_id"] == "42250539438" and
            p["analysis_sha"] == "9b8d6cd69382248ac1fabdff92fd242992cf63e9"
            and p["archived_source_run_id"] == "42249566219"
            and p["archived_source_sha"] == "c84e76ac15779357b620a3d273add224cad2cdf5"
            and p["not_new_fitting"] is True
            and p["original_63_64_unchanged"] is True
            and p["original_numeric_tolerances_unchanged"] is True,
            "ABBA original archived source/analysis provenance changed")
    require(d["same_runner_control"]["order"] == list(ORDER)
            and d["same_runner_control"]["same_runner_affinity_verified"] is True
            and set(d["environment"]) == set(ORDER) == set(d["fresh_raw_sha256"]),
            "ABBA four-run order/identity changed")
    sha = {
        "SkylakeX_1": "8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2",
        "SkylakeX_2": "8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2",
        "Haswell_1": "10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a",
        "Haswell_2": "10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a",
    }
    require(d["fresh_raw_sha256"] == sha, "ABBA fresh source raw hashes changed")
    for name in ORDER:
        meta = d["environment"][name]
        mode = name.split("_")[0]
        require(meta["raw_sha256"] == sha[name] and meta["mode"] == mode
                and meta["openblas_coretype"] == mode and meta["affinity"] == [0,1,2,3]
                and meta["openblas_threads"] == 4 and meta["numpy"] == "2.3.5"
                and meta["run_id"] == "42249566219" and
                meta["github_sha"] == p["archived_source_sha"]
                and any(x["internal_api"] == "openblas" and
                        x["architecture"] == mode and x["version"] == "0.3.30"
                        and x["num_threads"] == 4 for x in meta["pools"]),
                "ABBA original physical host/BLAS kernel/threads/sha changed")
    require(set(d["pairwise"]) == set(PAIRS), "ABBA four cross- and two same-mode contrasts changed")
    for name,(left,right) in PAIRS.items():
        row = d["pairwise"][name]
        within = "within_mode" in name
        numerical, binary = row["original_numeric_tolerances"], row["strict_serialized_binary64"]
        require((row["left"],row["right"]) == (left,right)
                and numerical["field_count"] == binary["field_count"] == 28
                and len(numerical["fields"]) == len(binary["fields"]) == 28,
                "ABBA original fitting field count or paired identities changed")
        wanted = [] if within else list(FAIL_FIELDS)
        require(numerical["mismatched_fields"] == wanted
                and binary["all_serialized_binary64_equal"] is within,
                "ABBA within-mode bitwise or cross-mode numerical result changed")
        for fld in FAIL_FIELDS:
            require(len(numerical["critical_field_mismatch_details"][fld]) == (0 if within else 4),
                    "ABBA critical trialwise discrepancies dropped")
        require(all(bool(x["serialized_binary64_equal"]) == within
                    for x in binary["fields"].values()) if within else
                any(not x["serialized_binary64_equal"] for x in binary["fields"].values()),
                "ABBA bitwise per-field consistency changed")
    require(set(d["vs_original"]) == set(ORDER), "ABBA archived reference comparison denominator changed")
    for name,v in d["vs_original"].items():
        wanted = list(FAIL_FIELDS) if name.startswith("SkylakeX") else [
            "traj.epsi", "traj.mu", "traj.muhat", "traj.psi"]
        matlab = v["vs_original_matlab"]
        require(matlab["field_count"] == v["vs_original_hgfx"]["field_count"] == 28
                and matlab["mismatched_fields"] == wanted,
                "ABBA original MATLAB old-tolerance result altered")
        require(all(len(matlab["critical_field_mismatch_details"][field]) ==
                    (4 if name.startswith("SkylakeX") else 14) for field in FAIL_FIELDS),
                "ABBA original MATLAB four/14 critical cells changed")
    return {"within_dispatch_bitwise_equal": 2, "cross_dispatch_numeric_mismatch": 4,
            "matlab_reference_still_nonpass": True}

def verify(d):
    return {
        "status": RESULT_STATUS,
        "scope": "DERIVED_TRACKED_JSON_CROSS_CHECK_ONLY_NOT_RAW_SOURCE_REPLAY",
        "reviewer_independent_verdict": "NOT_RECEIVED",
        "perf01c_prospective_freeze": "NOT_FROZEN",
        "performance_timing": "NOT_RUN",
        "cohort": check_cohort(d["cohort"]),
        "fit": check_fit(d["fit"]),
        "eligibility": check_eligibility(d["original"], d["candidate"]),
        "abba": check_abba(d["abba"], d["fit"]),
        "required_next_step": "Independent reviewer must download and verify original Actions raw artifacts, audit scientific source and sign issue #88; this check is not that review.",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    reports, file_sha256 = load(a.root)
    verdict = verify(reports)
    verdict["tracked_report_sha256"] = file_sha256
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(verdict,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps(verdict,sort_keys=True))
if __name__ == "__main__":
    main()
