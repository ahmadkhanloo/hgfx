#!/usr/bin/env python3
"""Replay TRUE frozen MATLAB-owned direct objective callsites from raw archive.

Author-side untimed diagnostic. Source statements identified from original
MATLAB optimizer text, never inferred from proposed hypothetical x6/T6 steps.
Unknown/ambiguous calls are preserved, not reclassified as accepted branches.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import re

import numpy as np
from scipy.io import loadmat
from replay_subject7_matlab_26_public_fields import (
    OPT, compare_exact, matlab_strings, matlab_text, only_struct, scalar,
)

HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
SCHEMA = "perf01d-native-matlab-direct-objective-calls-v1"
ORIGINAL_BFGS_HGFX = "060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce"
ORIGINAL_BFGS_MATLAB = "4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a"
START = [-3., -6., 3.871201010907891]


def need(cond, message):
    if not cond:
        raise ValueError(message)


def strict_number(x):
    return type(x) in (int, float) and math.isfinite(x)


def source_lines(original_source):
    lines = original_source.splitlines()
    clean = [re.sub(r"\s+", "", line) for line in lines]
    init_reset = [i + 1 for i, line in enumerate(clean) if line == "val=f(x);"]
    search = [i + 1 for i, line in enumerate(clean) if line == "newval=f(newx);"]
    need(len(init_reset) == 2 and len(search) == 1
         and init_reset[0] < search[0] < init_reset[1],
         "Original frozen optimizer three direct-objective callsites changed")
    return {"INITIAL": init_reset[0], "LINESEARCH": search[0], "RESET": init_reset[1]}


def verify_original_fit(summary):
    need(summary.get("subject_count") == 64 and summary.get("classification_counts") == {
        "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
        "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1,
    }, "Original 63/64 scientific NONPASS classification changed")
    case = summary["cases"][7]
    need(case.get("mismatched_fields") == ["traj.mu", "traj.muhat"]
         and case["fields"]["traj.mu"]["mismatch_count"] == 4
         and case["fields"]["traj.muhat"]["mismatch_count"] == 4,
         "Original subject-7 4+4 scientific fitting failure changed")


def verify_bfgs_source(hgfx_bytes, matlab_bytes):
    need(sha256(hgfx_bytes).hexdigest() == ORIGINAL_BFGS_HGFX
         and sha256(matlab_bytes).hexdigest() == ORIGINAL_BFGS_MATLAB,
         "Original BFGS source files do not match immutable SHA-256")


def validate_trace(report, source, summary):
    verify_original_fit(summary)
    site = source_lines(source)
    m = report["metadata"]
    need(report.get("schema") == SCHEMA and m.get("schema") == SCHEMA
         and m.get("frozen_matlab_sha") == MATLAB
         and m.get("frozen_hgfx_sha") == HGFX
         and m.get("original_science") == "63/64 SCIENTIFIC NONPASS"
         and m.get("original_failure_mu") == 4
         and m.get("original_failure_muhat") == 4
         and m.get("subject_index_zero_based") == 7
         and m.get("original_trial_count") == 128
         and m.get("compared_26_fields") == 26
         and m.get("finite_native_history_count") == 25
         and m.get("hook_count") == 1 and m.get("delegated") is True
         and m.get("native_instrumented_stable_identical") is True
         and m.get("native_instrumented_history_identical") is True
         and m.get("not_an_original_optimizer_source_patch") is True
         and m.get("not_a_source_if_branch_event_trace") is True
         and m.get("independent_review") == "NOT_RECEIVED"
         and m.get("perf01c") == "NOT_FROZEN" and m.get("timing") == "NOT_RUN"
         and report.get("original_science") == "63/64 SCIENTIFIC NONPASS"
         and report.get("independent_review") == "NOT_RECEIVED"
         and report.get("perf01c") == "NOT_FROZEN"
         and report.get("timing") == "NOT_RUN",
         "Frozen source or scientific status changed in direct call trace")
    need(m.get("github_run_id") and len(m.get("tested_sha", "")) == 40,
         "MATLAB objective call trace needs actual run and commit")
    need(m.get("source_initial_line") == site["INITIAL"]
         and m.get("source_linesearch_line") == site["LINESEARCH"]
         and m.get("source_reset_line") == site["RESET"],
         "Recorded MATLAB line numbers are not frozen optimizer source callsites")
    calls = report.get("direct_calls")
    need(type(calls) is list and calls, "Full direct source call sequence missing")
    expected = m.get("direct_counts")
    need(type(expected) is list and len(expected) == 4,
         "Expected exactly 4 source-call classification counts")
    counts = Counter()
    last_ordinal = 0
    original_start_matches = []
    observed = []
    for i, event in enumerate(calls):
        kind = event.get("kind")
        idx = event.get("direct_index_zero_based")
        num = event.get("call_number")
        x = event.get("free_x")
        v = event.get("private_objective")
        need(kind in site and event.get("source_line") == site.get(kind)
             and event.get("optimizer_name") == "quasinewton_optim",
             "Actual directly-called MATLAB source objective site unknown")
        need(idx == i and type(num) is int and num > last_ordinal,
             "MATLAB original call order or direct ordinal changed")
        need(type(x) is list and len(x) == 3 and all(strict_number(q) for q in x)
             and strict_number(v) and event.get("finite") is True
             and event.get("realmax_sentinel") is (v == float.fromhex("0x1.fffffffffffffp+1023")),
             "Direct original MATLAB objective has missing/nonfinite/falsified value")
        last_ordinal = num
        counts[kind] += 1
        if kind == "INITIAL":
            original_start_matches.append(x == START)
        observed.append({"direct_index_zero_based": i, "call_number": num,
                         "kind": kind, "free_x": x, "private_objective": v})
    need(all(original_start_matches) and len(original_start_matches) == 1
         and counts["LINESEARCH"] > 0
         and [counts[k] for k in ("INITIAL", "LINESEARCH", "RESET")] + [0] == expected
         and m.get("direct_call_count") == len(calls)
         and m.get("total_calls") == len(calls) + m.get("indirect_calls", -1)
         and m.get("total_calls") >= last_ordinal,
         "Actual frozen direct call inventory/counters disagree")
    idxs, xs, vals = (report.get(k) for k in (
        "native_history_finite_zero_based", "native_history_x", "native_history_val"))
    need(type(idxs) is list and idxs == list(range(25))
         and type(xs) is list and len(xs) == 25
         and type(vals) is list and len(vals) == 25,
         "Original MATLAB history contains unexpected overwritten/finite record layout")
    for x, val in zip(xs, vals):
        need(type(x) is list and len(x) == 3
             and all(strict_number(z) for z in x) and strict_number(val),
             "MATLAB native history has missing finite vectors/values")
    need(xs[0] == START and observed[0]["kind"] == "INITIAL"
         and observed[0]["free_x"] == xs[0]
         and observed[0]["private_objective"] == vals[0],
         "Original frozen initial optimizer direct call and native history disagree")
    # This is a NON-CAUSAL *exact archive membership* diagnostic.
    # Repeated terminal/overwritten records may not correspond to distinct
    # accepted steps, and identical candidate values do not prove branch events.
    mappings = []
    for j, (x, v) in enumerate(zip(xs[1:], vals[1:]), start=1):
        hits = [a["direct_index_zero_based"] for a in observed
                if a["kind"] in ("LINESEARCH", "RESET")
                and a["free_x"] == x and a["private_objective"] == v]
        mappings.append({"history_index_zero_based": j,
                         "matching_direct_call_indices": hits,
                         "match_status": "EXACT_DIRECT_CALL_MATCH" if hits else "NOT_MATCHED_OR_OVERWRITTEN"})
    matched = sum(bool(row["matching_direct_call_indices"]) for row in mappings)
    return {"schema": "perf01d-native-matlab-direct-calltrace-archive-replay-v1",
            "status": "AUTHOR_SIDE_ACTUAL_MATLAB_SOURCE_CALLS_ONLY",
            "original_scientific_fitting": "63/64 SCIENTIFIC NONPASS",
            "matlab_owned_original_history_not_hgfx_x6": True,
            "original_initial_x": START,
            "direct_counts": dict(counts),
            "direct_source_line_numbers": site,
            "direct_source_call_count": len(observed),
            "total_objective_call_count": m["total_calls"],
            "indirect_gradient_or_other_call_count": m["indirect_calls"],
            "finite_original_history_rows": 25,
            "matching_source_direct_call_history_rows": matched,
            "noninitial_native_history_membership": mappings,
            "observed_direct_source_calls": observed,
            "ambiguous_terminal_slots_not_labelled_as_branch_events": True,
            "independent_scientific_review": "NOT_RECEIVED",
            "perf01c": "NOT_FROZEN",
            "performance_timing": "NOT_RUN",
            "matlab_run_id": m["github_run_id"],
            "tested_sha": m["tested_sha"]}


def validate_mat(raw_mat, raw_json):
    data = loadmat(raw_mat, struct_as_record=False,
                   squeeze_me=False, chars_as_strings=True, mat_dtype=True)
    native = only_struct(data["native_public"])
    wrapped = only_struct(data["instrumented_public"])
    m = only_struct(data["metadata"])
    json_m = raw_json["metadata"]
    need(matlab_text(m.schema) == SCHEMA
         and matlab_text(m.frozen_hgfx_sha) == HGFX
         and matlab_text(m.frozen_matlab_sha) == MATLAB
         and matlab_text(m.github_run_id) == json_m["github_run_id"]
         and matlab_text(m.tested_sha) == json_m["tested_sha"]
         and matlab_text(m.original_science) == "63/64 SCIENTIFIC NONPASS"
         and bool(scalar(m.native_instrumented_stable_identical))
         and bool(scalar(m.native_instrumented_history_identical)),
         "Actual MATLAB raw 26+history file does not match source record")
    optim_names, traj_names = matlab_strings(m.opt_fields), matlab_strings(m.traj_fields)
    need(tuple(optim_names) == OPT
         and len(traj_names) == 11 and len(set(traj_names)) == 11,
         "Preexisting native 15+11 MATLAB public field inventory changed")
    rows = []
    for group, names in (("optim", optim_names), ("traj", traj_names)):
        a, b = only_struct(getattr(native, group)), only_struct(getattr(wrapped, group))
        need(set(a._fieldnames) == set(names) == set(b._fieldnames),
             "Raw 26 fields incomplete: " + group)
        for name in names:
            issue = compare_exact(getattr(a, name), getattr(b, name), group + "." + name)
            rows.append({"field": group + "." + name,
                         "exact_equal_nan": issue is None,
                         "first_difference": issue})
    native_iter, instrumented_iter = (only_struct(data[k]) for k in
                                     ("native_iter", "instrumented_iter"))
    iter_issue = compare_exact(native_iter, instrumented_iter, "optimizer.iter")
    need(len(rows) == 26 and all(z["exact_equal_nan"] for z in rows)
         and iter_issue is None,
         "Original native-vs-wrapper raw 26-field / optimizer history changed")
    return {"mat_member_sha256": sha256(Path(raw_mat).read_bytes()).hexdigest(),
            "native_instrumented_26_fieldwise_exact": True,
            "all_26_fields": rows,
            "native_instrumented_full_optimizer_history_equal": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--optimizer-source", type=Path, required=True)
    parser.add_argument("--original-fit", type=Path, required=True)
    parser.add_argument("--mat", type=Path, required=True)
    parser.add_argument("--original-hgfx-bfgs", type=Path, required=True)
    parser.add_argument("--original-matlab-bfgs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify_bfgs_source(args.original_hgfx_bfgs.read_bytes(), args.original_matlab_bfgs.read_bytes())
    raw_bytes = args.trace.read_bytes()
    report = json.loads(raw_bytes)
    checked = validate_trace(report, args.optimizer_source.read_text(),
                             json.loads(args.original_fit.read_bytes()))
    checked["actual_matlab_trace_sha256"] = sha256(raw_bytes).hexdigest()
    checked["original_source_matlab_optimizer_file_sha256"] = sha256(args.optimizer_source.read_bytes()).hexdigest()
    checked.update(validate_mat(args.mat, report))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(checked, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k:v for k,v in checked.items()
                      if k not in ("observed_direct_source_calls","all_26_fields","noninitial_native_history_membership")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
