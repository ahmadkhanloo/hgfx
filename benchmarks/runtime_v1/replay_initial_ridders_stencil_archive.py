#!/usr/bin/env python3
"""Independent SHA-locked archive-only x0 Ridders source-node and same-x objective audit.

All observed nodes and known unequal source values preserved; no source
threshold or new MATLAB fitting. Requires original 63/64 public NONPASS.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

from subject7_first_ridders_stencil import (
    HGFX,MATLAB,START,SCHEMA,normalize_node,classify_stencil,xbits,fbits
)

RUN="42389292284"
SOURCE_SHA="4ab5f42754b1200433d9b7dc6832e1ee7c45be8f"
MEMBERS={
    "hgfx-first-ridders.json":"fd8ea94bbf85e6f01feb1d7477ae15a42f86026cc0704503c9e0f00c9803599d",
    "matlab-first-private-ridders.json":"1826535a8e15c522bc3c987978c15978e14a5594664fae25d618e6f9f22a4685",
    "matlab-first-ridders-native-and-wrapped.mat":"6a4c30ccd4e9088fa373c5474522854972dd6bfcd15b577643f483e43d345ae4",
    "true-x0-both-stencils-cross-objective-audit.json":"13c2b32d10fbb508a651c954c13de3c674c5f06ae6a2bb1e641c710ec8abd0c6",
    "independent-matlab-26-fields-and-full-iter.json":"8c39b3f6709c76e805534bbe4ffd040bdc17251c1aa47d517f97763b195649d4",
}
MASK=(1<<64)-1
SIGN=1<<63


def need(value, reason):
    if not value:
        raise ValueError(reason)


def ulps(a,b):
    x,y=int.from_bytes(fbits(a),"big"),int.from_bytes(fbits(b),"big")
    def ordered(q):return ((~q)&MASK) if q&SIGN else (q|SIGN)
    return abs(ordered(x)-ordered(y))


def scientific_original(fit):
    need(fit.get("hgfx_sha")==HGFX and fit.get("matlab_sha")==MATLAB
         and fit.get("subject_count")==64
         and fit.get("classification_counts")=={
            "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
            "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1}
         and fit["cases"][7]["mismatched_fields"]==["traj.mu","traj.muhat"]
         and all(fit["cases"][7]["fields"][k]["mismatch_count"]==4
                 for k in ("traj.mu","traj.muhat")),
         "Original immutable 63/64 fitting scientific NONPASS changed")


def audit(h,m,d,native,original):
    scientific_original(original)
    need(h["schema"]==SCHEMA
         and h["status"]=="SOURCE_HGFX_INITIAL_RIDDERS_OWN_STENCIL"
         and h["frozen_hgfx_sha"]==HGFX and h["frozen_matlab_sha"]==MATLAB
         and h["original_63_subject_fit_status"]=="63/64 SCIENTIFIC NONPASS"
         and h["environment"]["github_run_id"]==RUN
         and h["environment"]["github_sha"]==SOURCE_SHA
         and h["independent_review"]=="NOT_RECEIVED" and h["perf01c"]=="NOT_FROZEN"
         and h["min_steps"]==m["min_steps"]==10,
         "Original HGFX source, run, scientific status or min_steps changed")
    need(m["schema"]=="perf01d-real-private-matlab-first-ridders-stencil-v1"
         and m["frozen_hgfx_sha"]==HGFX and m["frozen_matlab_sha"]==MATLAB
         and str(m["github_run_id"])==RUN and m["tested_sha"]==SOURCE_SHA
         and m["source_hgfx_stencil_sha256"]==MEMBERS["hgfx-first-ridders.json"]
         and m["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and m["original_failure"]=={"traj_mu":4,"traj_muhat":4}
         and m["source_hgfx_stencil_sha256"]==MEMBERS["hgfx-first-ridders.json"]
         and m["hook_count"]==1 and m["original_optimizer_delegated"] is True
         and m["native_wrapped_26_and_iter_exact"] is True
         and m["independent_review"]=="NOT_RECEIVED" and m["perf01c"]=="NOT_FROZEN",
         "Actual private MATLAB nested source, runner or neutrality changed")
    need(native["schema"]=="perf01d-matlab-initial-ridders-private-raw-public-verification-v1"
         and native["real_mat_sha256"]==MEMBERS["matlab-first-ridders-native-and-wrapped.mat"]
         and native["native_wrapped_26_exact"] is True
         and native["native_wrapped_complete_iter_exact"] is True
         and len(native["all_actual_26_field_pairs"])==26
         and all(r["exact_equal_nan"] is True for r in native["all_actual_26_field_pairs"])
         and native["original_full_fit"]=="63/64 SCIENTIFIC NONPASS"
         and native["independent_scientific_review"]=="NOT_RECEIVED",
         "Actual original MATLAB raw 26+iter independent-neutrality proof missing")
    need(d["schema"]=="perf01d-initial-ridders-same-x-both-objectives-v1"
         and d["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS"
         and d["source_hgfx_sha256"]==MEMBERS["hgfx-first-ridders.json"]
         and d["source_matlab_sha256"]==MEMBERS["matlab-first-private-ridders.json"]
         and d["independent_scientific_review"]=="NOT_RECEIVED"
         and d["perf01c"]=="NOT_FROZEN"
         and d["performance_timing"]=="NOT_RUN",
         "Old dual-objective source checksum/status changed")
    hn=normalize_node(h["hgfx_nodes"])
    mn=normalize_node(m["matlab_nodes"])
    hc,hrows=classify_stencil(hn)
    mc,mrows=classify_stencil(mn)
    need(hc==d["hgfx_step_counts"]==h["steps_per_coordinate"]
         and mc==d["matlab_step_counts"]
         and len(hn)==d["hgfx_objective_eval_count"]
         and len(mn)==d["matlab_objective_eval_count"]
         and len(d["all_hgfx_own_stencil_nodes"])==len(hn)
         and len(d["all_matlab_own_stencil_nodes"])==len(mn),
         "Full authentic source stencil inventory/step counts changed")
    for src,owned,cross in ((hn,"hgfx_value","matlab_value_same_x"),
                             (mn,"matlab_value","hgfx_value_same_x")):
        cases=(d["all_hgfx_own_stencil_nodes"] if owned=="hgfx_value"
               else d["all_matlab_own_stencil_nodes"])
        for i,(node,row) in enumerate(zip(src,cases)):
            need(row["index"]==i and xbits(row["x"])==xbits(node["x"])
                 and fbits(row[owned])==fbits(node["value"])
                 and row["same_objective_binary64"] is
                     (fbits(row[owned])==fbits(row[cross])),
                 "Raw real Ridders x, original function or same-x cross-eval changed")
    need(d["same_x_hgfx_own_stencil_objective_equal_binary64_count"]==
            sum(v["same_objective_binary64"] for v in d["all_hgfx_own_stencil_nodes"])
         and d["same_x_matlab_own_stencil_objective_equal_binary64_count"]==
            sum(v["same_objective_binary64"] for v in d["all_matlab_own_stencil_nodes"]),
         "Real original same-x scalar equality counts were altered")
    pairs=[]
    for axis in range(3):
        aa=[v for v in hrows if v["coord_zero_based"]==axis]
        bb=[v for v in mrows if v["coord_zero_based"]==axis]
        for j in range(max(len(aa),len(bb))):
            ah=aa[j] if j<len(aa) else None
            bm=bb[j] if j<len(bb) else None
            for sign in ("positive","negative"):
                x=ah[sign] if ah else None
                y=bm[sign] if bm else None
                eq=xbits(x["x"])==xbits(y["x"]) if x and y else None
                pairs.append({
                    "coord_zero_based":axis,"step_one_based":j+1,"sign":sign,
                    "both_present":x is not None and y is not None,
                    "source_coordinates_binary64_equal":eq,
                    "component_coordinate_ulps":ulps(x["x"][axis],y["x"][axis]) if x and y else None,
                    "hgfx_stencil_x":x["x"] if x else None,
                    "matlab_stencil_x":y["x"] if y else None,
                })
    need(len(d["original_own_stencil_pair_inventory"])==len(pairs),
         "Source original own stencil pair inventory dropped a pair")
    for i,(ours,old) in enumerate(zip(pairs,d["original_own_stencil_pair_inventory"])):
        need(ours["coord_zero_based"]==old["coord_zero_based"]
             and ours["step_one_based"]==old["step_one_based"]
             and ours["sign"]==old["sign"]
             and ours["source_coordinates_binary64_equal"]==old["same_stencil_x_binary64"],
             "Previous archived raw original paired source grids reordered/changed")
    by_grid={}
    for title,rows in (("hgfx",d["all_hgfx_own_stencil_nodes"]),
                       ("matlab",d["all_matlab_own_stencil_nodes"])):
        own,cross=("hgfx_value","matlab_value_same_x") if title=="hgfx" else ("matlab_value","hgfx_value_same_x")
        mism=[{"index":r["index"],"x":r["x"],
               "abs_objective_difference":abs(r[own]-r[cross]),
               "objective_ulp_difference":ulps(r[own],r[cross])}
              for r in rows if r["same_objective_binary64"] is False]
        by_grid[title]={
            "nodes":len(rows),"equal_scalar_bits":len(rows)-len(mism),
            "unequal_scalar_bits":len(mism),
            "maximum_same_x_objective_abs_difference":max((z["abs_objective_difference"] for z in mism),default=0.),
            "maximum_same_x_objective_ulp_difference":max((z["objective_ulp_difference"] for z in mism),default=0),
            "all_discrepant_real_nodes":mism,
        }
    all_here=[v for v in pairs if v["both_present"]]
    same=sum(v["source_coordinates_binary64_equal"] for v in all_here)
    return {
        "schema":"perf01d-authentic-initial-ridders-raw-stencil-ulps-v1",
        "status":"AUTHOR_SIDE_FROZEN_SAME_X_STENCIL_ARCHIVE_INDEPENDENT_REPLAY_NOT_SCIENTIFIC_PASS",
        "source_real_run":RUN,
        "source_real_commit":SOURCE_SHA,
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "hgfx_steps":hc,"matlab_steps":mc,
        "same_runner_initial_source_gradient_abs_delta":[abs(x-y) for x,y in zip(h["hgfx_gradient"],m["matlab_gradient"])],
        "paired_original_source_stencil_node_count":len(pairs),
        "paired_source_stencil_coordinates_exact_binary64_count":same,
        "paired_source_stencil_coordinates_different_binary64_count":len(all_here)-same,
        "original_source_grid_pair_details":pairs,
        "each_original_source_grid_cross_objective_comparison":by_grid,
        "original_first_stencil_not_full_path_causality":True,
        "ridders_private_internal_stop_if_event":"NOT_CAPTURED",
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "no_paper_timing_or_gpu":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--original-fit",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data={}
    for f,h in MEMBERS.items():
        src=a.archive/f
        raw=src.read_bytes()
        need(sha256(raw).hexdigest()==h,"Original same-runner real Ridders source SHA-256 mismatch: "+f)
        data[f]=json.loads(raw) if f.endswith(".json") else None
    result=audit(data["hgfx-first-ridders.json"],data["matlab-first-private-ridders.json"],
                 data["true-x0-both-stencils-cross-objective-audit.json"],
                 data["independent-matlab-26-fields-and-full-iter.json"],
                 json.loads(a.original_fit.read_bytes()))
    result["original_source_member_sha256"]=MEMBERS
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("original_source_grid_pair_details",
                                                                  "each_original_source_grid_cross_objective_comparison",
                                                                  "original_source_member_sha256")},sort_keys=True))
    print(json.dumps({k:{j:v for j,v in val.items() if j!="all_discrepant_real_nodes"}
                      for k,val in result["each_original_source_grid_cross_objective_comparison"].items()},
                     sort_keys=True))


if __name__=="__main__":main()
