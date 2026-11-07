#!/usr/bin/env python3
"""SHA-locked archived real MATLAB-owned candidate chronology vs original BFGS histories.

No MATLAB calls, source mutation, thresholds, timings, or scientific PASS.
The direct source-call record is actual MATLAB-owned; old HGFX history is
its OWN optimizer path from a separate original run, not a same-x comparator.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

import numpy as np

from replay_subject7_actual_matlab_optimizer_calls import (
    validate_trace, verify_bfgs_source, HGFX, MATLAB,
)

MATLAB_TRACE_SHA = "321393efe9aaf00c0fc96752de66fa27b4e9eebbc1b7f93ea485528ee59da2e9"
MATLAB_DERIVED_SHA = "1bdaa8c7a5db9c27bef65691e2a988ab6172554f8bc22af1089fdeb22014a802"
MATLAB_NATIVE_MAT_SHA = "5b0b0006e36d3fe5391d89a1a7121239e20a8425cd14e6b7032b1887ec929dae"
RAW_REFERENCE_RUN = "42380372791"
RAW_REFERENCE_SHA = "6b79b7a9c0e78777eae8994cb7312ec43a8a6f5d"
OLD_BFGS_RUN = "42187240378"
SOURCE_HISTORY_LEN = 25


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def scalar_bits(x: float) -> bytes:
    require(type(x) in (int, float) and math.isfinite(x),
            "source history contains nonfinite or missing binary64")
    return struct.pack(">d", float(x))


def same_bits(a: float, b: float) -> bool:
    return scalar_bits(a) == scalar_bits(b)


def vector_bits(x: list[float]) -> bytes:
    require(type(x) is list and len(x) == 3, "Expected 3-vector exact source coordinates")
    return b"".join(scalar_bits(v) for v in x)


def compare_vector(a: list[float], b: list[float]) -> tuple[bool, float]:
    require(type(a) is list and type(b) is list and len(a) == len(b) == 3,
            "Expected source vector of three coordinates")
    return vector_bits(a) == vector_bits(b), max(abs(float(p) - float(q)) for p, q in zip(a, b))


def read_old_hist(raw: dict, engine: str) -> tuple[list[list[float]], list[float]]:
    require(raw.get("schema") == f"perf01-subject7-bfgs-state-{engine}-v1"
            and raw.get("status") == "UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED"
            and raw.get("source_run_id") == "41863441006"
            and raw.get("subject_index_zero_based") == 7
            and raw.get("model") == "hgf_binary" and raw.get("trials") == 128
            and raw.get("frozen_hgfx_sha") == HGFX
            and raw.get("frozen_matlab_sha") == MATLAB
            and raw.get("original_raw_fits_verified") is True
            and raw.get("frozen_start_matches") is True
            and raw.get("finite_slots") == SOURCE_HISTORY_LEN
            and raw.get("ridders_min_steps") == 10
            and raw.get("n_rand_init") == 0,
            "Historical original BFGS source identity changed: " + engine)
    all_x, all_v = raw.get("iter_x"), raw.get("iter_val")
    require(type(all_x) is list and len(all_x) == 101
            and type(all_v) is list and len(all_v) == 101,
            "Historical original 101-slot BFGS source history missing")
    x, v = all_x[:SOURCE_HISTORY_LEN], all_v[:SOURCE_HISTORY_LEN]
    for xx, vv in zip(x, v):
        vector_bits(xx)
        scalar_bits(vv)
    return x, v


def compare_chronology(trace: dict, archived_hgfx: dict,
                       archived_matlab: dict) -> dict:
    """Compute exact chronological mappings with no discard, nearest-neighbor, or scientific rule."""
    m = trace["metadata"]
    require(trace["schema"] == "perf01d-native-matlab-direct-objective-calls-v1"
            and m["github_run_id"] == RAW_REFERENCE_RUN
            and m["tested_sha"] == RAW_REFERENCE_SHA
            and m["original_science"] == "63/64 SCIENTIFIC NONPASS"
            and m["independent_review"] == "NOT_RECEIVED"
            and m["perf01c"] == "NOT_FROZEN" and m["timing"] == "NOT_RUN"
            and m["direct_call_count"] == 25 and m["total_calls"] == 1938
            and m["indirect_calls"] == 1913 and m["direct_counts"] == [1,24,0,0]
            and m["native_instrumented_stable_identical"] is True
            and m["native_instrumented_history_identical"] is True,
            "Actual source MATLAB call inventory/provenance changed")
    direct = trace["direct_calls"]
    require(type(direct) is list and len(direct) == 25
            and direct[0]["kind"] == "INITIAL"
            and all(p["kind"] == "LINESEARCH" for p in direct[1:]),
            "Direct original MATLAB chronological source call order changed")
    new_x,new_v = trace["native_history_x"],trace["native_history_val"]
    require(type(new_x) is list and type(new_v) is list
            and len(new_x) == len(new_v) == SOURCE_HISTORY_LEN
            and trace["native_history_finite_zero_based"] == list(range(SOURCE_HISTORY_LEN)),
            "Same-run frozen MATLAB native source history shape/order changed")
    old_hx,old_hv = read_old_hist(archived_hgfx,"hgfx")
    old_mx,old_mv = read_old_hist(archived_matlab,"matlab")
    require(archived_hgfx["source_input_sha256"] == archived_matlab["source_input_sha256"]
            and archived_hgfx["source_config_sha256"] == archived_matlab["source_config_sha256"],
            "Frozen original HGFX versus MATLAB input/config identity changed")
    require(new_x[0] == [-3.,-6.,3.871201010907891]
            and old_hx[0] == old_mx[0] == new_x[0],
            "Frozen original source free start changed")
    actual_rows = []
    for i, row in enumerate(direct):
        got_x,got_v = new_x[i],new_v[i]
        same_x,component_error=compare_vector(row["free_x"],got_x)
        same_val=same_bits(row["private_objective"],got_v)
        actual_rows.append({
            "native_history_zero_based":i,
            "direct_index_zero_based": row["direct_index_zero_based"],
            "source_call_number": row["call_number"],
            "source_label":row["kind"],
            "direct_x_matches_same_run_native_history_bits":same_x,
            "direct_value_matches_same_run_native_history_bits":same_val,
            "exact_source_record_match":same_x and same_val,
            "component_max_abs_error":component_error,
            "direct_x":row["free_x"],
            "native_x":got_x,
            "native_value":got_v,
        })
    historical=[]
    for i in range(SOURCE_HISTORY_LEN):
        me,me_abs=compare_vector(new_x[i],old_mx[i])
        he,he_abs=compare_vector(new_x[i],old_hx[i])
        historical.append({
            "record_index_zero_based":i,
            "actual_matlab_native_vs_archived_matlab_equal_bits":me,
            "actual_matlab_native_vs_archived_matlab_max_abs":me_abs,
            "actual_matlab_native_vs_archived_hgfx_equal_bits":he,
            "actual_matlab_native_vs_archived_hgfx_max_abs":he_abs,
            "historical_matlab_own_vs_hgfx_own_max_abs":compare_vector(old_mx[i],old_hx[i])[1],
            "actual_matlab_native_vs_original_matlab_value_equal_bits":same_bits(new_v[i],old_mv[i]),
            "actual_matlab_native_vs_original_hgfx_value_equal_bits":same_bits(new_v[i],old_hv[i]),
        })
    candidate_bits=[vector_bits(row["free_x"]) for row in direct[1:]]
    terminal_duplicate = vector_bits(new_x[23]) == vector_bits(new_x[24]) and same_bits(new_v[23],new_v[24])
    matches=sum(bool(x["exact_source_record_match"]) for x in actual_rows)
    return {
        "schema":"perf01d-archived-actual-matlab-chronology-v1",
        "status":"AUTHOR_SIDE_ARCHIVED_CHRONOLOGY_ONLY_NOT_SCIENTIFIC_PASS",
        "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_traj_mu":4,
        "original_subject7_failed_traj_muhat":4,
        "actual_matlab_run":RAW_REFERENCE_RUN,
        "actual_matlab_source_sha":RAW_REFERENCE_SHA,
        "original_bfgs_source_run":OLD_BFGS_RUN,
        "source_input_sha256":archived_hgfx["source_input_sha256"],
        "source_config_sha256":archived_hgfx["source_config_sha256"],
        "direct_candidate_count":len(candidate_bits),
        "distinct_exact_binary64_direct_candidate_vectors":len(set(candidate_bits)),
        "total_direct_source_calls":len(actual_rows),
        "same_run_exact_chronological_call_to_history_match_count":matches,
        "same_run_exact_chronological_call_to_history_all_equal":matches==len(actual_rows),
        "first_nonmatching_direct_row":next((x["native_history_zero_based"] for x in actual_rows
                                            if not x["exact_source_record_match"]),None),
        "all_nonmatching_direct_row_indices": [
            x["native_history_zero_based"] for x in actual_rows
            if not x["exact_source_record_match"]],
        "last_source_direct_candidate_equals_last_native_history_bits":
            actual_rows[-1]["exact_source_record_match"],
        "penultimate_source_direct_candidate_equals_penultimate_history_bits":
            actual_rows[-2]["exact_source_record_match"],
        "terminal_history_duplicate_last_two":terminal_duplicate,
        "first_same_run_matlab_vs_prior_matlab_history_bit_difference":next(
            (x["record_index_zero_based"] for x in historical
             if not x["actual_matlab_native_vs_archived_matlab_equal_bits"]),None),
        "first_same_run_matlab_vs_prior_matlab_objective_value_bit_difference":next(
            (x["record_index_zero_based"] for x in historical
             if not x["actual_matlab_native_vs_original_matlab_value_equal_bits"]),None),
        "previous_matlab_objective_value_bit_difference_count":sum(
            not x["actual_matlab_native_vs_original_matlab_value_equal_bits"]
            for x in historical),
        "first_same_run_matlab_vs_archived_hgfx_history_bit_difference":next(
            (x["record_index_zero_based"] for x in historical
             if not x["actual_matlab_native_vs_archived_hgfx_equal_bits"]),None),
        "maximum_same_run_matlab_vs_prior_matlab_history_component_delta":max(
            x["actual_matlab_native_vs_archived_matlab_max_abs"] for x in historical),
        "maximum_same_run_matlab_vs_archived_hgfx_history_component_delta":max(
            x["actual_matlab_native_vs_archived_hgfx_max_abs"] for x in historical),
        "direct_call_to_history_chronological_rows":actual_rows,
        "historical_different_run_owned_path_row_comparisons":historical,
        "same_run_native_full_field_and_history_neutrality":"PREVIOUS_RAW_MAT_VERIFIED_NOT_REEXECUTED",
        "actual_internal_armijo_curvature_and_gradstop_boolean_events":"NOT_CAPTURED",
        "terminal_rows_actual_unique_steps":"AMBIGUOUS",
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","performance_timing":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for arg in ("trace","derived","native-mat","hgfx","matlab","source","original-fit","output"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    def source_member(path, expected):
        raw=path.read_bytes()
        require(sha256(raw).hexdigest()==expected,
                "Immutable historical MATLAB/derived/raw source member SHA mismatch: "+path.name)
        return raw
    trace_bytes=source_member(a.trace,MATLAB_TRACE_SHA)
    prior_bytes=source_member(a.derived,MATLAB_DERIVED_SHA)
    source_member(a.native_mat,MATLAB_NATIVE_MAT_SHA)
    hx=a.hgfx.read_bytes();mx=a.matlab.read_bytes()
    verify_bfgs_source(hx,mx)
    trace=json.loads(trace_bytes)
    summary=json.loads(a.original_fit.read_bytes())
    validated=validate_trace(trace,a.source.read_text(),summary)
    previous=json.loads(prior_bytes)
    require(previous["status"]=="AUTHOR_SIDE_ACTUAL_MATLAB_SOURCE_CALLS_ONLY"
            and previous["matlab_run_id"]==RAW_REFERENCE_RUN
            and previous["tested_sha"]==RAW_REFERENCE_SHA
            and previous["direct_source_call_count"]==25
            and previous["mat_member_sha256"]==MATLAB_NATIVE_MAT_SHA
            and previous["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS",
            "Prior source-normality replay not same original actual MATLAB run")
    assert validated["direct_source_call_count"]==25
    result=compare_chronology(trace,json.loads(hx),json.loads(mx))
    result["source_actual_matlab_trace_sha256"]=MATLAB_TRACE_SHA
    result["source_actual_native_mat_sha256"]=MATLAB_NATIVE_MAT_SHA
    result["source_previous_validated_replay_sha256"]=MATLAB_DERIVED_SHA
    result["source_historical_hgfx_bfgs_raw_sha256"]=sha256(hx).hexdigest()
    result["source_historical_matlab_bfgs_raw_sha256"]=sha256(mx).hexdigest()
    result["original_matlab_optimizer_source_sha256"]=sha256(a.source.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ("direct_call_to_history_chronological_rows",
                                    "historical_different_run_owned_path_row_comparisons")},
                     sort_keys=True))


if __name__=="__main__":
    main()
