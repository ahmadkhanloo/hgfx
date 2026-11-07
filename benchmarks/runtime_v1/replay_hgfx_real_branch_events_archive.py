#!/usr/bin/env python3
"""SHA-locked archive-only validation of ACTUAL frozen HGFX branch-body events.

Cross-check every executed HGFX Armijo-success and accepted-state body
against the *actual* unmodified objective call, x, value, j, iteration.
Never invent MATLAB hidden branch events from its source calls.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
from collections import Counter

from compare_same_runner_actual_optimizer_calls import (
    compare_same_host, check_hgfx, stable_original_summary,
)

RUN = "42387244467"
COMMIT = "52268e5220169aae3615d373bd52472e5e9a2336"
HASHES = {
    "actual-frozen-hgfx-original-optimizer-source-calls.json":
        "56b2e80272c42f0affd4c0084a28fc65e6ba737cf3d67335918c8ff49c335ac3",
    "actual-frozen-matlab-optimizer-source-calls.json":
        "7604e4311d2d66c3b5fc17e54db4f4fee62915e0988887168122d4cdbd58b94d",
    "matlab-native-and-wrapped-26-plus-iter.mat":
        "fe5e8ea763496a0f0fe76864bed42b849a4ad7f2878d4ad7edac383ff0c83b74",
    "independent-same-runner-source-comparison.json":
        "9ef73979f96627baa201aa72a2b9ad1b8df0a2b2273cb9b1d72ace14212d0cce",
}
MASK = (1<<64)-1
SIGN = 1<<63


def need(value, reason):
    if not value:
        raise ValueError(reason)


def float_bits(x):
    need(type(x) in (int,float) and math.isfinite(x),
         "Nonfinite/missing original source float")
    return struct.unpack(">Q",struct.pack(">d",float(x)))[0]


def vector_bits(v):
    need(type(v) is list and len(v)==3,
         "Original source 3-vector missing")
    return tuple(float_bits(x) for x in v)


def ulp_distance(a,b):
    aa,bb=float_bits(a),float_bits(b)
    ordered=lambda u: ((~u)&MASK) if (u&SIGN) else (u|SIGN)
    return abs(ordered(aa)-ordered(bb))


def reconcile(h,m):
    check_hgfx(h)
    result=compare_same_host(h,m)
    need(result["same_github_run_id"]==RUN
         and result["same_github_tested_sha"]==COMMIT
         and result["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS"
         and result["independent_scientific_review"]=="NOT_RECEIVED"
         and result["perf01c"]=="NOT_FROZEN",
         "Archived same-runner identity or original scientific failure changed")
    trial=[c for c in h["calls"] if c["kind"]=="LINESEARCH"]
    arms=[c for c in h["executed_source_branch_bodies"] if c["label"]=="ARMIO_BREAK_EXECUTED"]
    updates=[c for c in h["executed_source_branch_bodies"] if c["label"]=="ACCEPTED_UPDATE_EXECUTED"]
    need(len(trial)==len(arms)==len(updates)==24,
         "Not all 24 real HGFX source Armijo/acceptance body events exist")
    rows=[]
    for i,(call,arm,upd) in enumerate(zip(trial,arms,updates)):
        expected=(call["actual_original_matlab_i"],call["actual_original_j"],
                  vector_bits(call["free_x"]),float_bits(call["objective"]))
        am=(arm["optimizer_iteration_one_based"],arm["actual_j"],
            vector_bits(arm["candidate_x"]),float_bits(arm["candidate_value"]))
        ac=(upd["optimizer_iteration_one_based"],upd["actual_j"],
            vector_bits(upd["candidate_x"]),float_bits(upd["candidate_value"]))
        need(expected==am==ac,
             "Real source call / executed Armijo break / accepted update mismatch at trial "+str(i))
        rows.append({
            "trial_ordinal_zero_based":i,
            "optimizer_iteration_one_based":expected[0],
            "actual_original_j":expected[1],
            "actual_source_call_number":call["call_number"],
            "actual_candidate_x":call["free_x"],
            "actual_candidate_objective":call["objective"],
            "actual_armijo_true_branch_executed":True,
            "actual_public_update_executed":True,
        })
    desc=[v for v in h["executed_source_branch_bodies"] if v["label"]=="DESCENT_CLIPPED_EXECUTED"]
    curvature=[v for v in h["executed_source_branch_bodies"] if v["label"]=="BFGS_CURVATURE_UPDATE_EXECUTED"]
    gradstop=[v for v in h["executed_source_branch_bodies"] if v["label"]=="TERMINATION_TOL_GRAD_EXECUTED"]
    need(len(desc)==11 and len(curvature)==22 and len(gradstop)==1
         and all(1<=d["optimizer_iteration_one_based"]<=24 for d in desc)
         and all(1<=d["optimizer_iteration_one_based"]<=24 for d in curvature)
         and gradstop[0]["optimizer_iteration_one_based"]<=100,
         "Source body count or optimizer iteration assignments changed")
    matlab_trials=m["direct_calls"][1:]
    need(len(matlab_trials)==24, "Original MATLAB 24 line search candidates changed")
    paired=[]
    for i,(a,bb) in enumerate(zip(trial,matlab_trials)):
        ax,bx=a["free_x"],bb["free_x"]
        same=vector_bits(ax)==vector_bits(bx)
        paired.append({
            "trial_index_zero_based":i,
            "hgfx_actual_j":a["actual_original_j"],
            "exact_same_vector":same,
            "coordinate_max_abs_difference":max(abs(x-y) for x,y in zip(ax,bx)),
            "coordinate_ulp_distances":[ulp_distance(x,y) for x,y in zip(ax,bx)],
            "same_x_objective_binary64_equal":
                float_bits(a["objective"])==float_bits(bb["private_objective"]) if same else None,
            "same_x_objective_disagreement_is_assessable":same,
        })
    j_counts=Counter(row["actual_original_j"] for row in rows)
    matching=sum(bool(r["exact_same_vector"]) for r in paired)
    return {
        "schema":"perf01d-actual-hgfx-source-branch-body-archive-replay-v1",
        "status":"AUTHOR_SIDE_REAL_HGFX_EXECUTED_ARMIJO_REPLAYED_NOT_SCIENTIFIC_PASS",
        "source_run":RUN,
        "source_sha":COMMIT,
        "frozen_public_scientific_fit":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_traj_mu":4,
        "original_subject7_failed_traj_muhat":4,
        "hgfx_direct_line_search_objective_trials":24,
        "hgfx_actual_executed_armijo_true_body_events":24,
        "hgfx_actual_executed_accepted_state_body_events":24,
        "hgfx_original_regularization_exponent_j_counts":
            {str(k):v for k,v in sorted(j_counts.items())},
        "hgfx_actual_executed_curvature_update_bodies":len(curvature),
        "hgfx_actual_executed_descent_clipping_bodies":len(desc),
        "hgfx_actual_executed_gradient_stopping_bodies":len(gradstop),
        "matlab_actual_optimizer_direct_line_search_trials":24,
        "matlab_original_private_armijo_boolean_events":"NOT_CAPTURED",
        "same_vector_trial_count":matching,
        "different_vector_trial_count":len(paired)-matching,
        "first_different_trial_ordinal_zero_based":
            next((r["trial_index_zero_based"] for r in paired
                  if not r["exact_same_vector"]),None),
        "first_trial_max_coordinate_abs_delta":paired[0]["coordinate_max_abs_difference"],
        "first_trial_coordinate_ulp_distances":paired[0]["coordinate_ulp_distances"],
        "all_actual_hgfx_24_branch_call_ordinal_records":rows,
        "all_actual_same_runner_line_search_cross_engine_trials":paired,
        "original_fit_scientific_failure_not_changed":True,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN",
        "physical_gpu":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--original-fit",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    members={}
    for fn,expected in HASHES.items():
        src=a.archive/fn
        data=src.read_bytes()
        need(sha256(data).hexdigest()==expected,"Original real callstream SHA-256 tampered: "+fn)
        members[fn]=data
    stable_original_summary(json.loads(a.original_fit.read_bytes()))
    original=json.loads(members["independent-same-runner-source-comparison.json"])
    need(original["schema"]=="perf01d-paired-same-runner-original-public-source-calls-v1"
         and original["same_github_run_id"]==RUN
         and original["same_github_tested_sha"]==COMMIT
         and original["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS"
         and original["no_paper_timing"] is True
         and original["independent_scientific_review"]=="NOT_RECEIVED",
         "Original archived validated same-host comparison changed")
    result=reconcile(
        json.loads(members["actual-frozen-hgfx-original-optimizer-source-calls.json"]),
        json.loads(members["actual-frozen-matlab-optimizer-source-calls.json"]))
    result["original_raw_member_sha256"]=HASHES
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ("all_actual_hgfx_24_branch_call_ordinal_records",
                                    "all_actual_same_runner_line_search_cross_engine_trials",
                                    "original_raw_member_sha256")},
                     sort_keys=True))


if __name__=="__main__":
    main()
