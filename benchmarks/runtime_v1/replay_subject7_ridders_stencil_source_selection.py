#!/usr/bin/env python3
"""Exact-source-formula Ridders Richardson selection replay of archived calls.

This is a POST-RESULT exploration of one observed subject-7 gradient anomaly.
Source objective values came from actual frozen MATLAB fitModel and HGFX; the
matrix-selection replay here is descriptive and not an internal branch log.
It cannot establish scientific fitting PASS or justify benchmark timing.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

import numpy as np

RUN = "42361286407"
SOURCE_SHA = "fd32140920dce7d88559c79c44b08d32b303eb62"
PROTOCOL_SHA = "e1c3e2e83045896195701926a5f94fa361b0f091"
INPUT_SHA = "45d06ee935637c6c110a75d56e77b42db0d6d9977abac58f6969115ee407f66e"
MATLAB_SHA = "8f068c88cde8fd18df03e40c8f525214239786d43b3f524b06898a14a2fd1986"
ANCHOR_SHA = "12f7ea77552cc48a50fbaa26ef8b89c9a22c7f94a444900eb4862aa6b2e498f7"
TARGET = [-1.1621811570388512, -6.37816839506084, -0.23738383160834042]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def hashfile(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def raw_bits(x):
    return struct.pack(">d", float(x))


def source_components(trace, x0):
    """Split all native evaluation calls; no omitted or reordered probes."""
    require(isinstance(trace, list) and len(trace) >= 61 and len(trace) <= 601,
            "Unexpected source Ridders call count")
    require(len(trace[0]["free_parameters"]) == 3
            and all(raw_bits(a) == raw_bits(b) for a, b in zip(trace[0]["free_parameters"], x0)),
            "Original call zero must be f(x)")
    groups = [[], [], []]
    current_dim = 0
    for n, entry in enumerate(trace[1:], 1):
        x = entry["free_parameters"]
        v = float(entry["objective"])
        require(len(x) == 3 and all(math.isfinite(float(q)) for q in x)
                and math.isfinite(v), "Nonfinite or malformed original objective call")
        changed = [k for k in range(3) if raw_bits(x[k]) != raw_bits(x0[k])]
        require(len(changed) == 1, "Original source Ridders call changed multiple coordinates")
        axis = changed[0]
        require(axis >= current_dim, "Ridders coordinates were reordered/omitted")
        current_dim = axis
        groups[axis].append((tuple(float(a) for a in x), v))
    require(all(len(g) % 2 == 0 and len(g) >= 22 and len(g) <= 200 for g in groups),
            "Original three-dimensional Ridders step inventory invalid")
    for k, group in enumerate(groups):
        h = 1.0
        for i in range(len(group)//2):
            if i: h /= 1.2
            plus, minus = group[2*i:2*i+2]
            xplus, xminus = plus[0], minus[0]
            for j in range(3):
                expected_plus = float(x0[j]) + h if j == k else float(x0[j])
                expected_minus = float(x0[j]) - h if j == k else float(x0[j])
                require(raw_bits(xplus[j]) == raw_bits(expected_plus)
                        and raw_bits(xminus[j]) == raw_bits(expected_minus),
                        "Original Ridders x±h order/coordinates changed")
    return groups


def replay_group(group, expected_gradient, expected_error):
    """Exact frozen MATLAB utilities/riddersdiff.m formula, zero-based indexing."""
    n = len(group)//2
    require(11 <= n <= 100, "Original Ridders min_steps=10/max_steps=100 violated")
    p = np.full((100, 100), np.nan, dtype=np.float64)
    h = 1.0
    value = float("nan")
    err = float(np.finfo(np.float64).max)
    best = None
    stop_at = None
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for i in range(n):
            if i: h /= 1.2
            p[i, 0] = (float(group[2*i][1]) - float(group[2*i+1][1])) / (2.0 * h)
            if i:
                divsq = 1.2 ** 2
                factor = divsq
                for j in range(1,i+1):
                    p[i,j] = (factor*p[i,j-1] - p[i-1,j-1])/(factor-1.0)
                    factor *= divsq
                    currerr = max(abs(p[i,j]-p[i,j-1]), abs(p[i,j]-p[i-1,j-1]))
                    if currerr < err:
                        err = float(currerr)
                        value = float(p[i,j])
                        best = (i,j)
                if i + 1 > 10 and abs(p[i,i]-p[i-1,i-1]) > 2.0*err:
                    stop_at = i
                    break
    require(stop_at is None or n == stop_at+1,
            "Captured source stopped at a different point than frozen formula")
    require(stop_at is not None or n == 100,
            "Captured Ridders did not reach 100-step source cap or stopping test")
    require(best is not None and raw_bits(value) == raw_bits(expected_gradient)
            and raw_bits(err) == raw_bits(expected_error),
            "Archived original frozen gradient/error is not reproduced by exact Richardson source formula")
    coords = [(i,j) for i in range(n) for j in range(i+1)]
    infcount = sum(math.isinf(float(p[i,j])) for i,j in coords)
    nancount = sum(math.isnan(float(p[i,j])) for i,j in coords)
    hbest = 1.0
    for _ in range(best[0]): hbest /= 1.2
    return {
        "source_extrapolation_levels_evaluated": n,
        "source_stopped_early_after_zero_based_level": stop_at,
        "source_selected_row_zero_based": best[0],
        "source_selected_column_zero_based": best[1],
        "source_selected_h": hbest,
        "source_selected_gradient": value,
        "source_selected_internal_error": err,
        "source_first_plus_objective": float(group[0][1]),
        "source_first_minus_objective": float(group[1][1]),
        "max_finite_binary64": float(np.finfo(np.float64).max),
        "source_frozen_returning_realmax_sentinel_at_first_plus": bool(float(group[0][1]) == float(np.finfo(np.float64).max)),
        "reconstructed_nonfinite_richardson_entries_inf": infcount,
        "reconstructed_nonfinite_richardson_entries_nan": nancount,
        "reconstructed_nonfinite_diagonal_first_nan_level": next((i for i in range(n) if math.isnan(float(p[i,i]))), None),
        "source_formula_reconstruction_not_internal_selection_branch_log": True,
    }


def analyze_archive(archive):
    names = {
        "paired-actual-ridders-call-streams.json": INPUT_SHA,
        "actual-private-matlab-stencil-trace.json": MATLAB_SHA,
        "locked-postresult-stencil-target.json": ANCHOR_SHA,
    }
    for name, expected in names.items():
        require(hashfile(archive/name) == expected, "Original 42361286407 archived bytes changed: " + name)
    d = json.loads((archive/"paired-actual-ridders-call-streams.json").read_bytes())
    mat = json.loads((archive/"actual-private-matlab-stencil-trace.json").read_bytes())
    lock = json.loads((archive/"locked-postresult-stencil-target.json").read_bytes())
    require(mat["github_run_id"] == RUN and mat["github_sha"] == SOURCE_SHA
            and mat["protocol_commit_before_new_stencil_samples"] == PROTOCOL_SHA
            and lock["protocol_commit_before_new_stencil_samples"] == PROTOCOL_SHA
            and d["source_protocol_sha"] == PROTOCOL_SHA
            and lock["target_record_index_zero_based"] == 6
            and d["original_scientific_full_fit"] == "63/64 NONPASS"
            and d["independent_scientific_review"] == "NOT_RECEIVED"
            and d["perf01c"] == "NOT_FROZEN"
            and d["timing"] == "NOT_RUN"
            and d["same_session_matlab_28_field_neutrality"]["all_serialized_binary64_equal"] is True
            and d["source_50_run_id"] == "42305573614",
            "Source SHA/protocol/original scientific failure has changed")
    require(len(d["matlab_trace_full_all_actual_calls"]) == len(mat["actual_private_objective_evaluation_calls"]),
            "Reference source MATLAB trace length changed")
    out = {}
    for origin in ("hgfx","matlab"):
        stream = d[origin+"_trace_full_all_actual_calls"]
        groups = source_components(stream,TARGET)
        grads = d["new_"+origin+"_gradient"]
        errs = d["new_"+origin+"_ridders_internal_error_estimate"]
        out[origin] = [replay_group(g,grads[k],errs[k]) for k,g in enumerate(groups)]
    require(out["hgfx"][0]["source_extrapolation_levels_evaluated"] == 100
            and out["matlab"][0]["source_extrapolation_levels_evaluated"] == 100
            and out["hgfx"][0]["source_frozen_returning_realmax_sentinel_at_first_plus"]
            and out["matlab"][0]["source_frozen_returning_realmax_sentinel_at_first_plus"],
            "Selected observed 100-step realmax numeric mechanism missing")
    return {
        "schema": "perf01d-post-result-ridders-source-selection-replay-v1",
        "status": "AUTHOR_SIDE_SOURCE_FORMULA_RECONSTRUCTION_NOT_INDEPENDENT_SCIENCE",
        "original_target_selected_post_result": True,
        "original_50_probe_run": "42305573614",
        "source_exploratory_stencil_run": RUN,
        "original_63_64_nonpass": "63/64 SCIENTIFIC NONPASS",
        "original_trace_sha256": names,
        "source_matlab_ridders": "hgf-toolbox/utilities/riddersdiff.m @ 2437f4dc241541072722a2695ddeca7b44d83dd3",
        "ridders_default_max_steps": 100,
        "ridders_min_steps": 10,
        "selected_original_zero_based_subject": 7,
        "selected_original_hgfx_history_record_zero_based": 6,
        "selected_original_x": TARGET,
        "reconstructed_sources": out,
        "archived_same_x_paired_objective_summary": {k:v for k,v in d["objective_call_pairing"].items() if k != "all_calls_by_original_index_with_unpaired_coordinates_explicit"},
        "original_first_grad_component_abs_difference": d["gradient_same_x_component_abs_difference"][0],
        "independent_scientific_review": "NOT_RECEIVED",
        "perf01c": "NOT_FROZEN",
        "performance_timing": "NOT_RUN",
        "limitations": [
            "Post-result selected extreme: this is exploratory not an original scientific acceptance cohort.",
            "Richardson selection positions are source-formula replays of actual f(x±h) calls, not directly logged internal MATLAB branch events.",
            "The exact MATLAB realmax sentinel may come from perceptual forward error or NaN log-likelihood; the precise error category was not captured.",
            "Ridders internal extrapolation error is not a bound on cross-platform or cross-implementation gradient error.",
            "Observed mechanism does not prove causality for original 4+4 trajectory fit mismatch; all original failed evidence persists.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    d = analyze_archive(args.archive)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"source_stencil_run":d["source_exploratory_stencil_run"],
                      "hgfx_first_gradient":d["reconstructed_sources"]["hgfx"][0],
                      "matlab_first_gradient":d["reconstructed_sources"]["matlab"][0],
                      "original_fit_science":d["original_63_64_nonpass"],
                      "perf01c":d["perf01c"]},sort_keys=True))
    require(d["status"] == "AUTHOR_SIDE_SOURCE_FORMULA_RECONSTRUCTION_NOT_INDEPENDENT_SCIENCE",
            "Never promote derived source replay to scientific PASS")


if __name__ == "__main__":
    main()
