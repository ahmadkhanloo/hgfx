#!/usr/bin/env python3
"""Strict source guard for a post-result, non-gated MATLAB private Armijo probe.

This does not re-fit, time, or certify HGFX. The original 63/64 NONPASS binds.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

CANDIDATE_SHA = "b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144"
HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
X6 = [-1.1621811570388512, -6.37816839506084, -0.23738383160834042]
SOURCE_KEYS = ("hgfx_original_source_gradient", "real_matlab_private_gradient_at_exact_hgfx_source_x")
SOURCE_GRADIENT_SHA = "2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def numeric_vector(values):
    return (isinstance(values, list) and len(values) == 3
            and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                    and math.isfinite(x) for x in values))


def validate_candidate(candidate):
    """All comparisons to fixed original source values are exact."""
    require(candidate.get("schema") == "perf01d-postresult-source-one-step-original-record6-v1",
            "Unexpected candidate schema")
    require(candidate.get("source_original_frozen_hgfx") == HGFX
            and candidate.get("source_original_frozen_matlab") == MATLAB,
            "Original frozen source identities changed")
    require(candidate.get("source_original_64_public_fit_science") == "63/64 SCIENTIFIC NONPASS"
            and candidate.get("source_original_zero_based_subject7_4_plus_4_mismatches")
            == {"traj.mu": 4, "traj.muhat": 4},
            "Original subject-7 63/64 failed evidence changed")
    require(candidate.get("source_original_bfgs_run") == "42187240378"
            and candidate.get("source_50_actual_private_probe_run") == "42305573614"
            and candidate.get("source_50_raw_sha256", {}).get(
                "paired-direct-private-gradient-bfgs-margins.json") == SOURCE_GRADIENT_SHA,
            "Original source evidence provenance changed")
    require(candidate.get("original_history_record_zero_based") == 6
            and candidate.get("subject_index_zero_based") == 7
            and candidate.get("original_trial_count") == 128
            and candidate.get("one_identical_x") == X6,
            "Original chosen x6 or case index changed")
    require(candidate.get("post_result_selection") is True
            and candidate.get("selection_already_preliminarily_calculated_before_script_commit") is True
            and candidate.get("one_step_is_NOT_a_completed_fitting_result") is True
            and candidate.get("one_step_is_NOT_an_unmodified_original_MATLAB_optimizer_branch_log") is True
            and candidate.get("same_source_hgfx_objective_used_for_two_counterfactual_one_step_candidates") is True,
            "Exploratory source interpretation changed")
    require(candidate.get("independent_scientific_review") == "NOT_RECEIVED"
            and candidate.get("perf01c") == "NOT_FROZEN"
            and candidate.get("timing") == "NOT_RUN",
            "Scientific gate was silently promoted")
    dirs = candidate.get("same_T6_and_x6_one_step_directions", {})
    require(isinstance(dirs, dict) and set(dirs) == set(SOURCE_KEYS),
            "Original two source candidates missing/renamed")
    q = []
    for key in SOURCE_KEYS:
        row = dirs[key]
        v = row.get("source_next_full_step_free_x")
        require(numeric_vector(v), "Candidate missing or nonfinite: " + key)
        require(row.get("original_source_clipping_applied") is True
                and math.isfinite(row.get("original_armijo_delta_RHS_using_unclipped_slope", float("nan")))
                and row.get("source_current_value") == 108.28848680066957,
                "Original source clipping/slope/base changed: " + key)
        q.append(v)
    require(q[0] != q[1] and all(v != X6 for v in q),
            "Counterfactual candidate vectors collapsed")
    return candidate


def load_candidate(path):
    raw = Path(path).read_bytes()
    require(sha256(raw).hexdigest() == CANDIDATE_SHA,
            "Original single-step candidate archived SHA-256 changed")
    return validate_candidate(json.loads(raw))


def validate_result(candidate, report):
    require(report.get("schema") == "perf01d-actual-private-matlab-candidate-armijo-v1"
            and report.get("source_original_candidate_sha256") == CANDIDATE_SHA
            and report.get("frozen_hgfx_sha") == HGFX
            and report.get("frozen_matlab_sha") == MATLAB
            and report.get("original_science") == "63/64 SCIENTIFIC NONPASS",
            "Private MATLAB raw provenance/gate changed")
    require(report.get("hook_count") == 1
            and report.get("original_optimizer_delegated") is True
            and report.get("native_instrumented_stable_fields_identical") is True
            and report.get("compared_stable_field_count") == 26,
            "Native frozen public fit neutrality/control failed")
    rows = report.get("calls")
    require(isinstance(rows, list) and len(rows) == 3, "Not all 3 real MATLAB objective calls recorded")
    labels = ["original_hgfx_source_x6", *SOURCE_KEYS]
    vectors = [candidate["one_identical_x"]] + [
        candidate["same_T6_and_x6_one_step_directions"][k]["source_next_full_step_free_x"]
        for k in SOURCE_KEYS]
    for row, label, vector in zip(rows, labels, vectors):
        require(row.get("name") == label and row.get("free_x") == vector
                and row.get("status") in ("EVALUATED_FINITE", "REALMAX_SENTINEL",
                                          "NONFINITE", "EXCEPTION"),
                "Private candidate call missing, changed, or unclassified")
        if row["status"] == "EVALUATED_FINITE":
            require(isinstance(row.get("private_objective"), (int, float))
                    and math.isfinite(row["private_objective"]),
                    "Finite private objective missing")
    for i, key in enumerate(SOURCE_KEYS, 1):
        row = rows[i]
        require(row.get("previous_hgfx_objective_at_candidate")
                == candidate["same_T6_and_x6_one_step_directions"][key][
                    "new_evaluated_hgfx_objective_at_candidate"],
                "Prior HGFX objective evidence was altered")
        require(row.get("original_armijo_delta_rhs")
                == candidate["same_T6_and_x6_one_step_directions"][key][
                    "original_armijo_delta_RHS_using_unclipped_slope"],
                "Original Armijo RHS changed")
        if rows[0]["status"] == "EVALUATED_FINITE" and row["status"] == "EVALUATED_FINITE":
            lhs = row["private_objective"] - rows[0]["private_objective"]
            require(row.get("private_armijo_delta_lhs") == lhs
                    and row.get("private_armijo_full_step") is (lhs < row["original_armijo_delta_rhs"]),
                    "Actual private MATLAB Armijo decision does not match original inequality")
    require(report.get("independent_scientific_review") == "NOT_RECEIVED"
            and report.get("perf01c") == "NOT_FROZEN"
            and report.get("timing") == "NOT_RUN",
            "Science/reviewer/performance status silently changed")
    return {
        "status": "AUTHOR_SIDE_THREE_PRIVATE_OBJECTIVE_CALLS_ONLY",
        "review": "NOT_RECEIVED",
        "original_science": "63/64 SCIENTIFIC NONPASS",
        "perf01c": "NOT_FROZEN",
        "raw_candidate_sha256": CANDIDATE_SHA,
        "matlab_raw_sha256": None,
        "original_candidates": [
            {"name": row["name"], "status": row["status"],
             "matlab_private_value": row.get("private_objective"),
             "private_armijo": row.get("private_armijo_full_step")}
            for row in rows
        ],
        "no_timing": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", choices=("prepare", "verify"), required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--matlab", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    source = load_candidate(args.candidate)
    if args.stage == "prepare":
        print(json.dumps({"source_original_nonpass": source["source_original_64_public_fit_science"],
                          "candidate_sha256": CANDIDATE_SHA,
                          "original_x6": source["one_identical_x"],
                          "source_candidate_count": len(SOURCE_KEYS),
                          "private_matlab_measurement": "NOT_YET_RUN"}, sort_keys=True))
        return
    require(args.matlab is not None and args.output is not None, "Missing full raw MATLAB result/output")
    raw = args.matlab.read_bytes()
    verdict = validate_result(source, json.loads(raw))
    verdict["matlab_raw_sha256"] = sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verdict, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(json.dumps(verdict, sort_keys=True))


if __name__ == "__main__":
    main()
