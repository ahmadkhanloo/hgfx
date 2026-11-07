#!/usr/bin/env python3
"""Independently compare two real same-runner frozen public optimizer callstreams.

Authors' untimed exploratory engineering trace, NEVER a scientific PASS.
MATLAB direct calls are source callsites, NOT captured MATLAB if-branch events.
Python executed optimizer body-line events are direct tracing observations.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

from replay_subject7_actual_matlab_optimizer_calls import validate_trace, validate_mat
from hgfx_actual_optimizer_calls import HGFX, MATLAB, OLD_H, OLD_M

SCHEMA="perf01d-original-public-hgfx-actual-optimizer-calls-v1"


def need(flag,reason):
    if not flag:
        raise ValueError(reason)


def samebits(a,b):
    return struct.pack(">d",float(a))==struct.pack(">d",float(b))


def xyzbits(v):
    need(type(v) is list and len(v)==3
         and all(type(q) in (int,float) and math.isfinite(q) for q in v),
         "Malformed/nonfinite original three-vector")
    return b"".join(struct.pack(">d",float(x)) for x in v)


def stable_original_summary(original):
    need(original.get("hgfx_sha")==HGFX and original.get("matlab_sha")==MATLAB
         and original.get("subject_count")==64
         and original.get("classification_counts")=={
             "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
             "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1,
         } and original["cases"][7]["mismatched_fields"]==["traj.mu","traj.muhat"]
         and all(original["cases"][7]["fields"][k]["mismatch_count"]==4
                 for k in ("traj.mu","traj.muhat")),
         "Original 63/64 scientific nonpass and subject 7 4+4 lost")


def check_hgfx(h):
    m=h["metadata"]
    need(m["schema"]==SCHEMA
         and m["status"]=="AUTHOR_SIDE_ACTUAL_FROZEN_HGFX_SOURCE_CALLS_NOT_SCIENTIFIC_PASS"
         and m["frozen_hgfx_sha"]==HGFX and m["frozen_matlab_sha"]==MATLAB
         and m["old_bfgs_hgfx_raw_sha256"]==OLD_H
         and m["old_bfgs_matlab_raw_sha256"]==OLD_M
         and m["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and m["original_subject7_failure"]=={"traj.mu":4,"traj.muhat":4}
         and m["subject_index_zero_based"]==7 and m["trials"]==128
         and m["neutrality_26_public_fields"] is True
         and m["neutrality_full_iter"] is True
         and m["original_finite_history_slots"]==25
         and m["independent_review"]=="NOT_RECEIVED"
         and m["perf01c"]=="NOT_FROZEN"
         and m["no_performance_timing"] is True,
         "Original frozen HGFX public trace scientific/provenance fields changed")
    sites=m["source_python_optimizer_sites"]
    labels=("INITIAL","LINESEARCH","RESET","ARMIO_BREAK_EXECUTED",
            "ACCEPTED_UPDATE_EXECUTED","BFGS_CURVATURE_UPDATE_EXECUTED",
            "TERMINATION_TOL_ARG_EXECUTED","TERMINATION_TOL_GRAD_EXECUTED",
            "TERMINATION_MAX_RESETS_EXECUTED","DESCENT_CLIPPED_EXECUTED")
    need(all(k in sites and type(sites[k]) is int and sites[k]>0 for k in labels)
         and len(set(sites.values()))==len(labels),
         "Frozen Python original optimizer source line schema changed")
    direct=h["calls"]
    need(type(direct) is list and direct
         and len(direct)==sum(m["direct_counts"].values())
         and m["all_objective_calls"]==len(direct)+m["indirect_call_count"],
         "Original HGFX source call accounting incomplete")
    seen=Counter();last_num=0
    for i,c in enumerate(direct):
        label=c["kind"]
        need(label in ("INITIAL","LINESEARCH","RESET")
             and c["source_line"]==sites[label]
             and c["direct_index_zero_based"]==i
             and type(c["call_number"]) is int and c["call_number"]>last_num
             and c["finite"] is True and type(c["objective"]) in (int,float)
             and math.isfinite(c["objective"]) and xyzbits(c["free_x"]),
             "Actual frozen HGFX direct call reordering/source tampering")
        seen[label]+=1; last_num=c["call_number"]
        if label=="LINESEARCH":
            need(type(c["actual_original_j"]) is int and 0<=c["actual_original_j"]<=16
                 and samebits(c["actual_original_step_fraction"],0.5**c["actual_original_j"])
                 and type(c["actual_original_matlab_i"]) is int
                 and 1<=c["actual_original_matlab_i"]<=100,
                 "Original HGFX line-search dispatch regularization index invalid")
    need(direct[0]["kind"]=="INITIAL"
         and direct[0]["free_x"]==[-3.,-6.,3.871201010907891]
         and seen==Counter(m["direct_counts"])
         and seen["INITIAL"]==1,
         "Original frozen HGFX source direct first/case counts altered")
    events=h["executed_source_branch_bodies"]
    need(type(events) is list and events
         and len(events)==sum(m["branch_executed_counts"].values()),
         "Actual frozen HGFX executed source-branch body events incomplete")
    observed=Counter()
    for e in events:
        need(e["label"] in labels[3:]
             and e["source_line"]==sites[e["label"]]
             and type(e["optimizer_iteration_one_based"]) is int
             and 1<=e["optimizer_iteration_one_based"]<=100,
             "Original HGFX executed source body line identity invalid")
        if e["label"] in ("ARMIO_BREAK_EXECUTED","ACCEPTED_UPDATE_EXECUTED"):
            xyzbits(e["candidate_x"])
            need(type(e["actual_j"]) is int and 0<=e["actual_j"]<=16
                 and type(e["candidate_value"]) in (int,float)
                 and math.isfinite(e["candidate_value"]),
                 "Original HGFX executed source Armijo/acceptance candidate missing")
        observed[e["label"]]+=1
    need(observed==Counter(m["branch_executed_counts"]),
         "Original HGFX actual executed branch-body counters altered")
    x=h["original_native_101_iter_x"];v=h["original_native_101_iter_val"]
    need(type(x) is list and len(x)==101 and type(v) is list and len(v)==101,
         "Original HGFX full history not archived")
    need(all(isinstance(row,list) and len(row)==3 for row in x)
         and all(v[i] is not None for i in range(25)),
         "Original HGFX native complete history or finite slot inventory missing")
    for row in x[:25]:
        xyzbits(row)
    for q in v[:25]:
        need(type(q) in (int,float) and math.isfinite(q),"HGFX native stored objective nonfinite")
    need(all(q is None for q in v[25:]),
         "Expected original 25 finite val rows (101 full preserved)")
    pairs=h["native_vs_wrapped_26_field_results"]
    need(len(pairs)==26 and len(set(r["field"] for r in pairs))==26
         and all(r["equal_nan_exact"] is True and r["first_difference"] is None for r in pairs),
         "HGFX public native versus wrapper incomplete or not neutral")
    return seen,observed


def compare_same_host(h,ma):
    hc,he=check_hgfx(h)
    mm=ma["metadata"]
    need(mm["schema"]=="perf01d-native-matlab-direct-objective-calls-v1"
         and mm["frozen_matlab_sha"]==MATLAB and mm["frozen_hgfx_sha"]==HGFX
         and mm["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and mm["independent_review"]=="NOT_RECEIVED"
         and mm["perf01c"]=="NOT_FROZEN" and mm["timing"]=="NOT_RUN"
         and mm["native_instrumented_stable_identical"] is True
         and mm["native_instrumented_history_identical"] is True
         and mm["direct_counts"]==[1,24,0,0],
         "MATLAB original direct-call source/science metadata changed")
    need(h["metadata"]["host"]["github_run_id"]==mm["github_run_id"]
         and h["metadata"]["host"]["github_sha"]==mm["tested_sha"],
         "MATLAB and HGFX traces must come from the exact SAME GitHub Actions run and candidate commit")
    ho=h["calls"];mo=ma["direct_calls"]
    need(len(mo)==25 and mo[0]["kind"]=="INITIAL"
         and all(x["kind"]=="LINESEARCH" for x in mo[1:]),
         "MATLAB original 25 direct source call inventory changed")
    hx=h["original_native_101_iter_x"][:25]
    hv=h["original_native_101_iter_val"][:25]
    mx=ma["native_history_x"];mv=ma["native_history_val"]
    need(len(mx)==len(mv)==25 and len(hx)==len(hv)==25,
         "Original native 25 stored source history rows missing")
    native_comparisons=[]
    for i in range(25):
        same=xyzbits(hx[i])==xyzbits(mx[i])
        diff=max(abs(x-y) for x,y in zip(hx[i],mx[i]))
        val_same=samebits(hv[i],mv[i])
        native_comparisons.append({
            "original_record_zero_based":i,
            "same_vector_binary64":same,
            "same_stored_objective_binary64":val_same,
            "vector_max_abs_difference":diff,
            "hgfx_owned_x":hx[i],
            "matlab_owned_x":mx[i],
            "scalar_difference_is_same_x_evidence":same,
        })
    htrials=[c for c in ho if c["kind"]=="LINESEARCH"]
    mtrials=mo[1:]
    paired=[]
    for i in range(max(len(htrials),len(mtrials))):
        a=htrials[i] if i<len(htrials) else None
        b=mtrials[i] if i<len(mtrials) else None
        both=a is not None and b is not None
        same=xyzbits(a["free_x"])==xyzbits(b["free_x"]) if both else None
        paired.append({
           "line_search_trial_ordinal_zero_based":i,
           "both_actual_source_evaluations_present":both,
           "exact_same_free_vector":same,
           "max_abs_free_vector_delta":max(abs(x-y) for x,y in zip(a["free_x"],b["free_x"])) if both else None,
           "same_vector_objective_equal_bits":samebits(a["objective"],b["private_objective"]) if both and same else None,
           "hgfx_actual_original_j":a["actual_original_j"] if a else None,
           "hgfx_actual_optimizer_iteration":a["actual_original_matlab_i"] if a else None,
           "hgfx_source_objective_call_ordinal":a["call_number"] if a else None,
           "matlab_source_objective_call_ordinal":b["call_number"] if b else None,
           "matlab_original_j_not_source_instrumented":True,
           "hgfx_own_x":a["free_x"] if a else None,
           "matlab_own_x":b["free_x"] if b else None,
        })
    first_path_diff=next((r["original_record_zero_based"] for r in native_comparisons if not r["same_vector_binary64"]),None)
    first_trial_diff=next((r["line_search_trial_ordinal_zero_based"] for r in paired if r["exact_same_free_vector"] is not True),None)
    return {
      "schema":"perf01d-paired-same-runner-original-public-source-calls-v1",
      "status":"AUTHOR_SIDE_SAME_RUNNER_REAL_SOURCE_CALL_COMPARISON_NOT_SCIENTIFIC_PASS",
      "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
      "same_github_run_id":mm["github_run_id"],
      "same_github_tested_sha":mm["tested_sha"],
      "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
      "subject7_failed_original_traj_mu":4,"subject7_failed_original_traj_muhat":4,
      "hgfx_direct_objective_call_counts":dict(hc),
      "matlab_direct_objective_call_counts":{"INITIAL":1,"LINESEARCH":24,"RESET":0},
      "hgfx_indirect_objective_call_count":h["metadata"]["indirect_call_count"],
      "matlab_indirect_objective_call_count":mm["indirect_calls"],
      "hgfx_observed_executed_branch_bodies":dict(he),
      "matlab_original_private_boolean_branch_events":"NOT_CAPTURED",
      "hgfx_line_search_source_trials":len(htrials),
      "matlab_line_search_source_trials":len(mtrials),
      "source_trial_ordinal_comparisons":paired,
      "native_25_record_history_own_path_comparisons":native_comparisons,
      "first_bitwise_history_path_difference_zero_based":first_path_diff,
      "first_bitwise_actual_trial_vector_difference_zero_based":first_trial_diff,
      "maximum_own_path_same_record_coordinate_delta":max(x["vector_max_abs_difference"] for x in native_comparisons),
      "same_x_cross_engine_trial_scalar_equal_count":sum(1 for x in paired if x["same_vector_objective_equal_bits"] is True),
      "same_x_cross_engine_trial_scalar_unequal_count":sum(1 for x in paired if x["same_vector_objective_equal_bits"] is False),
      "source_trial_count_difference":len(htrials)-len(mtrials),
      "no_paper_timing":True,
      "independent_scientific_review":"NOT_RECEIVED",
      "perf01c":"NOT_FROZEN",
      "physical_gpu_validation":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for k in ("hgfx","matlab","matlab-mat","matlab-source","original-fit","output","hgfx-frozen-source"):
        p.add_argument("--"+k,type=Path,required=True)
    args=p.parse_args()
    hb=args.hgfx.read_bytes()
    mb=args.matlab.read_bytes()
    h=json.loads(hb);m=json.loads(mb)
    stable_original_summary(json.loads(args.original_fit.read_bytes()))
    # The original source Python file is checked out at frozen v1.0.0 and its
    # actual SHA is compared to that used by the tracer, rather than inventing
    # a machine-specific install path.
    need(sha256(args.hgfx_frozen_source.read_bytes()).hexdigest()==h["metadata"]["source_python_optimizer_sha256"],
         "Actual traced installed HGFX source bytes disagree with frozen Git checkout")
    # Verify exact source MATLAB callsites against original frozen checkout,
    # AND 26 raw native/instrumented public fields plus FULL iter values.
    validated=validate_trace(m,args.matlab_source.read_text(),
                             json.loads(args.original_fit.read_bytes()))
    checked=validate_mat(args.matlab_mat,m)
    need(validated["direct_source_call_count"]==25
         and checked["native_instrumented_26_fieldwise_exact"]
         and checked["native_instrumented_full_optimizer_history_equal"],
         "Original MATLAB real raw source/native neutrality is invalid")
    result=compare_same_host(h,m)
    result["raw_hgfx_actual_source_sha256"]=sha256(hb).hexdigest()
    result["raw_matlab_actual_source_sha256"]=sha256(mb).hexdigest()
    result["raw_matlab_native_wrapper_mat_sha256"]=checked["mat_member_sha256"]
    result["raw_frozen_hgfx_optimizer_py_sha256"]=h["metadata"]["source_python_optimizer_sha256"]
    result["original_science_provenance"]="fit_cohort_results/summary-41863441006.json"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({k:v for k,v in result.items()
                     if k not in ("source_trial_ordinal_comparisons","native_25_record_history_own_path_comparisons")},
                     sort_keys=True))


if __name__=="__main__":
    main()
