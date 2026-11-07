#!/usr/bin/env python3
"""Independent SHA-locked archive-only real Ridders/Richardson table reconstruction.

Replay original unmodified HGFX and MATLAB *recorded* first-gradient f(x±h)
scalar observations with the frozen source formula (not a replacement gradient).
Exact output bit equality is observed, never tolerance-gated or assumed;
reconstructed if events are NOT directly instrumented original source events.
Original 63/64 scientific NONPASS and original raw failure evidence are preserved.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

from replay_initial_ridders_stencil_archive import (
    MEMBERS as SOURCE, RUN, SOURCE_SHA, audit as audit_raw, ulps
)
from subject7_first_ridders_stencil import (
    HGFX, MATLAB, START, classify_stencil, xbits, fbits
)

SOURCE_ZIP_SHA256 = "99a00582ab9fe3f52546b105490f609de4299fd0177ed4afdae456f18c4c23f1"
DERIVED_PRIOR_SHA256 = "1bfa7dc78c5878d8b441d6d0d6b551d9f0bb2b214c8892fc46685b45d63a37ff"
NUM_AXES = 3
MIN_STEPS = 10
MAX_STEPS = 100
DIV = 1.2
TF = 2.0
INITIAL_H = 1.0


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def binary_equal(x,y):
    return fbits(float(x))==fbits(float(y))


def compare_scalar(estimate, source):
    need(type(source) in (int,float) and math.isfinite(source),
         "Original frozen Ridders source returned nonfinite/missing scalar")
    return {
        "source_observed":float(source),
        "source_formula_reconstructed":float(estimate),
        "exact_equal_binary64":binary_equal(estimate,source),
        "absolute_difference":abs(float(estimate)-float(source)),
        "ulp_distance":ulps(float(estimate),float(source)),
    }


def pair_to_row(pair,axis):
    need(pair["coord_zero_based"]==axis,"Original Ridders axis unexpectedly changed")
    a,b=pair["positive"],pair["negative"]
    need(type(a["value"]) in (int,float) and type(b["value"]) in (int,float)
         and math.isfinite(a["value"]) and math.isfinite(b["value"]),
         "Original Ridders raw source samples nonfinite/missing")
    return a["value"],b["value"]


def reconstruct_axis(raw_pairs, axis, min_steps=MIN_STEPS, max_steps=MAX_STEPS,
                     div=DIV, tf=TF, init_h=INITIAL_H):
    """Independent scalar formulation of original Ridders source, zero-based P.

    Consumes observed (+,-) pairs only; does NOT evaluate an objective function.
    Separately reports if source-formula termination is consistent with *observed*
    number of pairs, without asserting original MATLAB internal branches logged.
    """
    need(type(raw_pairs) is list and bool(raw_pairs)
         and type(min_steps) is int and min_steps==MIN_STEPS
         and type(max_steps) is int and max_steps==MAX_STEPS
         and type(div) is float and div==DIV
         and type(tf) is float and tf==TF
         and type(init_h) is float and init_h==INITIAL_H,
         "Original Ridders source options/steps changed")
    need(min_steps+1<=len(raw_pairs)<=max_steps,
         "Original Ridders source min_steps/steps inventory invalid")
    n=len(raw_pairs)
    p=[[float("nan")]*n for _ in range(n)]
    events=[]
    table=[]
    h=float(init_h)
    best_df=float("nan")
    best_err=float.fromhex("0x1.fffffffffffffp+1023")  # original realmax
    best_index=None
    stopped_at=None
    divsq=div**2

    for i,pair in enumerate(raw_pairs):
        plus,minus=pair_to_row(pair,axis)
        if i:
            h/=div
        need(math.isfinite(h) and h>0,"Ridders interpolation h nonfinite")
        p[i][0]=(float(plus)-float(minus))/(2.0*h)
        need(math.isfinite(p[i][0]),"Ridders base difference nonfinite")
        row_cells=[{"col_zero_based":0,"value":p[i][0],
                    "candidate_error":None,"strict_best_update":False}]
        t=divsq
        for j in range(1,i+1):
            value=(t*p[i][j-1]-p[i-1][j-1])/(t-1.0)
            need(math.isfinite(value),"Ridders Richardson table contains nonfinite cell")
            p[i][j]=value
            t*=divsq
            candidate_error=max(abs(p[i][j]-p[i][j-1]),
                                abs(p[i][j]-p[i-1][j-1]))
            need(math.isfinite(candidate_error),"Original Ridders candidate error nonfinite")
            did_update=bool(candidate_error<best_err)
            if did_update:
                best_err=candidate_error
                best_df=value
                best_index=[i,j]
                events.append({
                    "row_zero_based":i,"col_zero_based":j,
                    "candidate_value":value,"candidate_error":candidate_error,
                    "previous_best_replaced":True,
                })
            row_cells.append({"col_zero_based":j,"value":value,
                              "candidate_error":candidate_error,
                              "strict_best_update":did_update})
        score=None
        rhs=None
        eligible=bool(i+1>min_steps)
        should_stop=False
        if eligible:
            score=abs(p[i][i]-p[i-1][i-1])
            rhs=tf*best_err
            should_stop=bool(score>rhs)
            if should_stop and stopped_at is None:
                stopped_at=i+1
        table.append({
            "row_zero_based":i,"step_one_based":i+1,"h":h,
            "raw_plus":plus,"raw_minus":minus,
            "p_cells":row_cells,"best_after_row":best_df,
            "best_error_after_row":best_err,
            "best_cell_after_row":best_index,
            "source_stop_eligible":eligible,
            "source_stop_diagonal_gap":score,
            "source_stop_rhs":rhs,
            "source_stop_if_reconstructed_true":should_stop,
        })
    need(best_index is not None and math.isfinite(best_df)
         and math.isfinite(best_err),"Original Ridders could not choose finite Richardson best cell")
    # In actual frozen source, return immediately on first source if; source raw
    # objective calls are a separate *observed* count which must be consistent.
    return {
        "axis_zero_based":axis,
        "observed_pair_count":n,
        "reconstructed_first_source_stop_step":stopped_at,
        "reconstructed_stopping_matches_observed_source_pair_count":
            stopped_at==n if stopped_at is not None else n==max_steps,
        "reconstructed_best_cell_zero_based":best_index,
        "reconstructed_best_derivative":best_df,
        "reconstructed_best_error":best_err,
        "number_strict_best_updates":len(events),
        "strict_best_update_events":events,
        "full_triangular_row_source_reconstruction":table,
        "internal_original_source_if_events_directly_logged":False,
    }


def original_axis_pairs(nodes):
    steps,rows=classify_stencil(nodes)
    return steps,[[row for row in rows if row["coord_zero_based"]==i]
                  for i in range(NUM_AXES)]


def compare_h_vs_m(h,m,d,native,original,prior):
    # Reuse previous separately implemented archive source checker for immutable
    # 63/64, genuine MATLAB private source, all 71 nodes, xbits and 26+full iter.
    previous=audit_raw(h,m,d,native,original)
    need(prior["schema"]=="perf01d-authentic-initial-ridders-raw-stencil-ulps-v1"
         and prior["status"]=="AUTHOR_SIDE_FROZEN_SAME_X_STENCIL_ARCHIVE_INDEPENDENT_REPLAY_NOT_SCIENTIFIC_PASS"
         and prior["source_real_run"]==RUN
         and prior["source_real_commit"]==SOURCE_SHA
         and prior["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and prior["paired_original_source_stencil_node_count"]==70
         and prior["paired_source_stencil_coordinates_exact_binary64_count"]==70
         and prior["paired_source_stencil_coordinates_different_binary64_count"]==0
         and prior["independent_scientific_review"]=="NOT_RECEIVED"
         and prior["perf01c"]=="NOT_FROZEN",
         "Prior original Ridders source archive replay or scientific integrity changed")
    for attr in ("hgfx_steps","matlab_steps"):
        need(previous[attr]==prior[attr],
             "Two distinct verified historical source archive audits disagree")
    hsteps,haxes=original_axis_pairs(h["hgfx_nodes"])
    msteps,maxes=original_axis_pairs(m["matlab_nodes"])
    need(hsteps==msteps==[11,11,13],
         "Original source Ridders first x0 11,11,13 grid must not change")
    for i in range(NUM_AXES):
        for a,b in zip(haxes[i],maxes[i]):
            for sign in ("positive","negative"):
                need(xbits(a[sign]["x"])==xbits(b[sign]["x"]),
                     "Original HGFX vs MATLAB Ridders x±h coordinate binary64 mismatch")
    need(len(d["all_hgfx_own_stencil_nodes"])==len(h["hgfx_nodes"])==71
         and len(d["all_matlab_own_stencil_nodes"])==len(m["matlab_nodes"])==71,
         "Original complete real Ridders same-x source nodes missing")

    by_engine={}
    for name,pairs,reported_grad,reported_err in (
        ("hgfx",haxes,h["hgfx_gradient"],h["hgfx_error"]),
        ("matlab",maxes,m["matlab_gradient"],m["matlab_error"]),
    ):
        reconstructed=[]
        for axis in range(NUM_AXES):
            rr=reconstruct_axis(pairs[axis],axis)
            rr["real_original_observed_gradient"] = compare_scalar(
                rr["reconstructed_best_derivative"],reported_grad[axis])
            rr["real_original_observed_error"] = compare_scalar(
                rr["reconstructed_best_error"],reported_err[axis])
            reconstructed.append(rr)
        by_engine[name]=reconstructed

    # Same-x, cross-evaluated genuine nested MATLAB objective on HGFX first
    # grid: the two SOURCE Ridders grids were byte-identical before analysis.
    # This is a hypothetical scalar replacement diagnostic and is NOT another
    # execution of the frozen MATLAB or HGFX derivative source algorithm.
    swap_values={
        "matlab_on_hgfx_grid":[z["matlab_value_same_x"]
                                for z in d["all_hgfx_own_stencil_nodes"]],
        "hgfx_on_matlab_grid":[z["hgfx_value_same_x"]
                                for z in d["all_matlab_own_stencil_nodes"]],
    }
    counterfactual={}
    for title,nodes,values,axes in (
        ("matlab_on_hgfx_grid",h["hgfx_nodes"],swap_values["matlab_on_hgfx_grid"],haxes),
        ("hgfx_on_matlab_grid",m["matlab_nodes"],swap_values["hgfx_on_matlab_grid"],maxes),
    ):
        need(len(values)==len(nodes)==71,
             "Original source counterfactual scalar inventory incomplete")
        patched=[]
        for j,(item,value) in enumerate(zip(nodes,values)):
            need(item["ordinal"]==j and type(value) in (float,int) and math.isfinite(value),
                 "Original source same-x scalar replacement invalid")
            row=dict(item)
            row["value"]=float(value)
            patched.append(row)
        _,new_axes=original_axis_pairs(patched)
        counterfactual[title]=[]
        for axis in range(NUM_AXES):
            result=reconstruct_axis(new_axes[axis],axis)
            real=("matlab" if title=="matlab_on_hgfx_grid" else "hgfx")
            original_replay=by_engine[real][axis]
            result["exact_same_returned_source_formula_bits_as_real_"+real] = {
                "gradient":binary_equal(result["reconstructed_best_derivative"],
                                        original_replay["reconstructed_best_derivative"]),
                "error":binary_equal(result["reconstructed_best_error"],
                                     original_replay["reconstructed_best_error"]),
            }
            result["same_best_selected_cell_as_real_"+real] = (
                result["reconstructed_best_cell_zero_based"]==
                original_replay["reconstructed_best_cell_zero_based"])
            result["same_predicted_stop_as_real_"+real] = (
                result["reconstructed_first_source_stop_step"]==
                original_replay["reconstructed_first_source_stop_step"])
            counterfactual[title].append(result)

    comparisons=[]
    for i in range(NUM_AXES):
        a=by_engine["hgfx"][i]
        b=by_engine["matlab"][i]
        comparisons.append({
            "coordinate_zero_based":i,
            "observed_original_source_gradient_delta":abs(
                float(h["hgfx_gradient"][i])-float(m["matlab_gradient"][i])),
            "source_reconstructed_gradient_delta":abs(
                a["reconstructed_best_derivative"]-b["reconstructed_best_derivative"]),
            "same_selected_table_cell":a["reconstructed_best_cell_zero_based"]==
                                      b["reconstructed_best_cell_zero_based"],
            "same_predicted_stop_row":a["reconstructed_first_source_stop_step"]==
                                      b["reconstructed_first_source_stop_step"],
            "exact_source_returned_gradient_bits_per_engine": {
                "hgfx":a["real_original_observed_gradient"]["exact_equal_binary64"],
                "matlab":b["real_original_observed_gradient"]["exact_equal_binary64"],
            },
            "exact_source_returned_error_bits_per_engine": {
                "hgfx":a["real_original_observed_error"]["exact_equal_binary64"],
                "matlab":b["real_original_observed_error"]["exact_equal_binary64"],
            },
        })
    return {
        "schema":"perf01d-authentic-initial-ridders-richardson-full-table-replay-v1",
        "status":"AUTHOR_SIDE_ARCHIVED_SOURCE_FORMULA_RECONSTRUCTION_NOT_SCIENTIFIC_PASS",
        "actual_true_raw_source_run":RUN,
        "actual_true_source_sha":SOURCE_SHA,
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_traj_mu":4,"original_subject7_failed_traj_muhat":4,
        "original_ridders_options":{"init_h":INITIAL_H,"div":DIV,
                                    "min_steps":MIN_STEPS,"max_steps":MAX_STEPS,"tf":TF},
        "all_70_source_stencil_vectors_binary64_same":True,
        "original_71_same_x_objective_scalar_equal_count":57,
        "original_71_same_x_objective_scalar_unequal_count":14,
        "observed_original_hgfx_gradient":h["hgfx_gradient"],
        "observed_original_matlab_private_gradient":m["matlab_gradient"],
        "observed_original_hgfx_ridders_error":h["hgfx_error"],
        "observed_original_matlab_private_ridders_error":m["matlab_error"],
        "all_original_source_formula_axis_tables":by_engine,
        "all_same_x_scalar_only_counterfactual_axis_tables":counterfactual,
        "original_vs_reconstructed_coordinate_comparisons":comparisons,
        "original_source_ridders_selection_if_events":"NOT_DIRECTLY_CAPTURED",
        "cross_objective_counterfactual_is_not_original_execution":True,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN","physical_gpu_validation":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for k in ("source-archive","previous-archive","original-fit","output",
              "frozen-hgfx-ridders","frozen-matlab-ridders"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    raw={}
    for fname,expected in SOURCE.items():
        bb=(a.source_archive/fname).read_bytes()
        need(sha256(bb).hexdigest()==expected,
             "Original MATLAB/HGFX Ridders source member SHA256 mismatch: "+fname)
        raw[fname]=json.loads(bb) if fname.endswith(".json") else None
    prevbytes=(a.previous_archive/"independent-original-stencils-grid-and-same-x-ulps.json").read_bytes()
    need(sha256(prevbytes).hexdigest()==DERIVED_PRIOR_SHA256,
         "Prior separately validated original Ridders archive source hash changed")
    prior=json.loads(prevbytes)
    py_src=a.frozen_hgfx_ridders.read_text()
    ml_src=a.frozen_matlab_ridders.read_text()
    need("def _ridders_extrapolate(" in py_src
         and "if currerr < error:" in py_src
         and "matlab_i > options.min_steps" in py_src
         and "abs(p[i, i] - p[i - 1, i - 1]) > options.tf * error" in py_src
         and "P(i,j) = (t*P(i,j-1)-P(i-1,j-1))/(t-1);" in ml_src
         and "if currerr < err" in ml_src
         and "if i > min_steps && abs(P(i,i)-P(i-1,i-1)) > tf*err" in ml_src,
         "Frozen original Ridders Richardson source formula/stop body changed")
    original=json.loads(a.original_fit.read_bytes())
    result=compare_h_vs_m(
        raw["hgfx-first-ridders.json"],
        raw["matlab-first-private-ridders.json"],
        raw["true-x0-both-stencils-cross-objective-audit.json"],
        raw["independent-matlab-26-fields-and-full-iter.json"],
        original,prior)
    result["source_real_member_sha256"]=SOURCE
    result["source_previous_ulp_archive_sha256"]=DERIVED_PRIOR_SHA256
    result["frozen_hgfx_ridders_source_sha256"]=sha256(a.frozen_hgfx_ridders.read_bytes()).hexdigest()
    result["frozen_matlab_ridders_source_sha256"]=sha256(a.frozen_matlab_ridders.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"run":RUN,"status":result["status"],
        "per_axis":[{
            "axis":i,
            "real_hgfx_gradient":result["observed_original_hgfx_gradient"][i],
            "replay_hgfx_gradient":result["all_original_source_formula_axis_tables"]["hgfx"][i]["reconstructed_best_derivative"],
            "real_matlab_gradient":result["observed_original_matlab_private_gradient"][i],
            "replay_matlab_gradient":result["all_original_source_formula_axis_tables"]["matlab"][i]["reconstructed_best_derivative"],
            "hgfx_selected":result["all_original_source_formula_axis_tables"]["hgfx"][i]["reconstructed_best_cell_zero_based"],
            "matlab_selected":result["all_original_source_formula_axis_tables"]["matlab"][i]["reconstructed_best_cell_zero_based"],
            "hgfx_stop_row":result["all_original_source_formula_axis_tables"]["hgfx"][i]["reconstructed_first_source_stop_step"],
            "matlab_stop_row":result["all_original_source_formula_axis_tables"]["matlab"][i]["reconstructed_first_source_stop_step"],
            "hgfx_original_gradient_exact_bits":result["original_vs_reconstructed_coordinate_comparisons"][i]["exact_source_returned_gradient_bits_per_engine"]["hgfx"],
            "matlab_original_gradient_exact_bits":result["original_vs_reconstructed_coordinate_comparisons"][i]["exact_source_returned_gradient_bits_per_engine"]["matlab"],
            "best_cell_equal":result["original_vs_reconstructed_coordinate_comparisons"][i]["same_selected_table_cell"]
        } for i in range(NUM_AXES)]},sort_keys=True))


if __name__=="__main__":
    main()
