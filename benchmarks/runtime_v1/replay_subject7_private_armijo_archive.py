#!/usr/bin/env python3
"""Archive-only, separately implemented author-side replay of the private MATLAB
subject-7 x6/T6 Armijo result. Not an independent scientific reviewer verdict.

Recomputes the three source-level Armijo conditions without importing the
original generating/comparison Python module. All archived inputs are SHA-locked.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

SOURCE_CANDIDATE_SHA = "b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144"
MATLAB_RAW_SHA = "b901486c9f8a17cc414f60b284ecc707c0fb314652e1089db29a91ae208fadd7"
ORIGINAL_DERIVED_SHA = "f42274c7f284edaa19bbb5ff09e69887471be9e04bbb615e9effca3a35a75275"
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
REF_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
ORIGINAL_RUN = "42375431029"
ORIGINAL_SHA = "b3821627e787380766843660a36ae04017535987"
ORIGINAL_PROTOCOL = "a79cd7a0f83f14b4959b16dadbb1c696960c96bc"
GRADIENT_KEYS = (
    "hgfx_original_source_gradient",
    "real_matlab_private_gradient_at_exact_hgfx_source_x",
)
FIRST_X = [-1.1621811570388512, -6.37816839506084, -0.23738383160834042]


def check(test, reason):
    if not test:
        raise ValueError(reason)


def is_number(v):
    return type(v) in (int, float) and math.isfinite(v)


def sha_read(path, expected):
    raw = Path(path).read_bytes()
    check(sha256(raw).hexdigest() == expected,
          "Immutable archived member hash mismatch: " + Path(path).name)
    return json.loads(raw)


def replay(source, raw, derived, provenance, original):
    """Independent arithmetic replay, no new MATLAB calls and no threshold changes."""
    check(original.get("subject_count") == 64
          and original.get("classification_counts") == {
              "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
              "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1,
          } and original["cases"][7]["mismatched_fields"] == [
              "traj.mu", "traj.muhat"]
          and all(original["cases"][7]["fields"][k]["mismatch_count"] == 4
                  for k in ("traj.mu", "traj.muhat")),
          "Original public 63/64 and 4+4 failure changed")
    check(source.get("schema") == "perf01d-postresult-source-one-step-original-record6-v1"
          and source.get("source_original_frozen_hgfx") == HGFX_SHA
          and source.get("source_original_frozen_matlab") == REF_SHA
          and source.get("source_original_64_public_fit_science") == "63/64 SCIENTIFIC NONPASS"
          and source.get("source_original_zero_based_subject7_4_plus_4_mismatches")
          == {"traj.mu": 4, "traj.muhat": 4}
          and source.get("subject_index_zero_based") == 7
          and source.get("original_history_record_zero_based") == 6
          and source.get("one_identical_x") == FIRST_X
          and source.get("post_result_selection") is True,
          "Wrong original source/selection or scientific failure")
    check(raw.get("schema") == "perf01d-actual-private-matlab-candidate-armijo-v1"
          and raw.get("source_original_candidate_sha256") == SOURCE_CANDIDATE_SHA
          and raw.get("tested_sha") == ORIGINAL_SHA
          and str(raw.get("github_run_id")) == ORIGINAL_RUN
          and raw.get("frozen_hgfx_sha") == HGFX_SHA
          and raw.get("frozen_matlab_sha") == REF_SHA
          and raw.get("original_science") == "63/64 SCIENTIFIC NONPASS"
          and raw.get("hook_count") == 1
          and raw.get("original_optimizer_delegated") is True
          and raw.get("native_instrumented_stable_fields_identical") is True
          and raw.get("compared_stable_field_count") == 26,
          "Real MATLAB experiment identity or native instrument neutrality flag changed")
    check(provenance.get("run_id") == ORIGINAL_RUN
          and provenance.get("tested_candidate_commit") == ORIGINAL_SHA
          and provenance.get("protocol_commit") == ORIGINAL_PROTOCOL
          and provenance.get("original_public_fit") == "63/64 SCIENTIFIC NONPASS"
          and provenance.get("independent_review") == "NOT_RECEIVED"
          and provenance.get("perf01c") == "NOT_FROZEN"
          and provenance.get("performance_timing") == "NOT_RUN"
          and provenance.get("sha256", {}).get("private-matlab-three-candidate-objectives.json") == MATLAB_RAW_SHA
          and provenance.get("sha256", {}).get("derived-private-matlab-armijo-summary.json") == ORIGINAL_DERIVED_SHA,
          "Unverified artifact/run provenance")
    check(derived.get("matlab_raw_sha256") == MATLAB_RAW_SHA
          and derived.get("raw_candidate_sha256") == SOURCE_CANDIDATE_SHA
          and derived.get("status") == "AUTHOR_SIDE_THREE_PRIVATE_OBJECTIVE_CALLS_ONLY"
          and derived.get("original_science") == "63/64 SCIENTIFIC NONPASS"
          and derived.get("review") == "NOT_RECEIVED"
          and derived.get("perf01c") == "NOT_FROZEN",
          "Historical derived report changed")
    calls = raw.get("calls")
    check(type(calls) is list and len(calls) == 3
          and type(source.get("same_T6_and_x6_one_step_directions")) is dict,
          "Three complete original MATLAB observations required")
    source_d = source["same_T6_and_x6_one_step_directions"]
    check(set(source_d) == set(GRADIENT_KEYS), "Both original gradient origins required")
    names = ("original_hgfx_source_x6",) + GRADIENT_KEYS
    coords = [FIRST_X] + [source_d[k]["source_next_full_step_free_x"]
                          for k in GRADIENT_KEYS]
    for row, name, x in zip(calls, names, coords):
        check(row.get("name") == name and row.get("free_x") == x
              and row.get("status") == "EVALUATED_FINITE"
              and is_number(row.get("private_objective")),
              "Archived actual 3/3 finite objective samples changed")
    base = calls[0]["private_objective"]
    check(derived.get("original_candidates") and len(derived["original_candidates"]) == 3,
          "Historical three-row derived report missing")
    conclusions = []
    for i, name in enumerate(GRADIENT_KEYS, 1):
        stored = source_d[name]
        actual = calls[i]
        slope = stored.get("original_source_unclipped_gradient_dot_direction")
        rhs = stored.get("original_armijo_delta_RHS_using_unclipped_slope")
        check(is_number(slope) and is_number(rhs) and rhs == 1e-4 * slope
              and stored.get("original_source_clipping_applied") is True,
              "Original unchanged slope/RHS source formula not established")
        check(actual.get("original_armijo_delta_rhs") == rhs
              and actual.get("previous_hgfx_objective_at_candidate")
              == stored["new_evaluated_hgfx_objective_at_candidate"],
              "Source original one-step candidate evidence was changed")
        lhs = actual["private_objective"] - base
        accepted = lhs < rhs
        check(actual.get("private_armijo_delta_lhs") == lhs
              and actual.get("private_armijo_full_step") is accepted,
              "Private MATLAB Armijo condition fails independent arithmetic replay")
        historical_derived = derived["original_candidates"][i]
        check(historical_derived.get("name") == name
              and historical_derived.get("status") == actual["status"]
              and historical_derived.get("matlab_private_value") == actual["private_objective"]
              and historical_derived.get("private_armijo") is accepted,
              "Archived author-side derived decision differs from fresh replay")
        conclusions.append({
            "candidate": name,
            "matlab_private_objective": actual["private_objective"],
            "prior_hgfx_objective": stored["new_evaluated_hgfx_objective_at_candidate"],
            "exact_equal_to_prior_hgfx_objective": actual["private_objective"] == stored["new_evaluated_hgfx_objective_at_candidate"],
            "armijo_lhs": lhs,
            "armijo_rhs": rhs,
            "armijo_margin_rhs_minus_lhs": rhs - lhs,
            "source_formula_full_step_armijo": accepted,
        })
    check(derived["original_candidates"][0].get("name") == names[0]
          and derived["original_candidates"][0].get("matlab_private_value") == base,
          "Archived original x6 objective differs")
    return {
        "schema": "perf01d-independent-codepath-archive-replay-v1",
        "status": "AUTHOR_SIDE_SHA_LOCKED_ARCHIVE_ARITHMETIC_REPLAY_ONLY",
        "original_scientific_fitting": "63/64 SCIENTIFIC NONPASS",
        "post_result_selection": True,
        "source_actual_private_matlab_run": ORIGINAL_RUN,
        "source_actual_private_matlab_commit": ORIGINAL_SHA,
        "source_candidate_sha256": SOURCE_CANDIDATE_SHA,
        "private_matlab_raw_sha256": MATLAB_RAW_SHA,
        "original_derived_sha256": ORIGINAL_DERIVED_SHA,
        "original_source_base_x6": FIRST_X,
        "actual_private_base_objective": base,
        "actual_private_equals_original_stored_base": base == source.get("source_original_record6_value"),
        "candidate_arithmetic": conclusions,
        "original_full_fit_4_plus_4_failures_retained": True,
        "full_original_matlab_optimizer_branch_log": "NOT_EVALUATED",
        "native_26_field_neutrality": "PRODUCER_BOOL_ONLY_NOT_INDEPENDENT_RAW_FIELD_REPLAY",
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "performance_timing": "NOT_RUN",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--matlab", type=Path, required=True)
    ap.add_argument("--derived", type=Path, required=True)
    ap.add_argument("--provenance", type=Path, required=True)
    ap.add_argument("--original-fit", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    source = sha_read(args.candidate, SOURCE_CANDIDATE_SHA)
    matlab = sha_read(args.matlab, MATLAB_RAW_SHA)
    prior = sha_read(args.derived, ORIGINAL_DERIVED_SHA)
    provenance = json.loads(args.provenance.read_bytes())
    original = json.loads(args.original_fit.read_bytes())
    result = replay(source, matlab, prior, provenance, original)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
