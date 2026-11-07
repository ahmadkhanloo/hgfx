#!/usr/bin/env python3
"""SHA-locked archive-only independent second-run original HGF/unitsq 71-node replay.

No MATLAB is executed. Checks original full-fit 63/64 scientific NONPASS and
all original native source likelihoods, then reconstructs the entire original
genuine stage summary in a fresh codepath, requiring deep binary64 equality.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
from typing import Any

from compare_original_x0_infstates_observation import main_compare
from original_x0_hgfx_infstates import ORIGINAL_TERM_SHA
from subject7_first_ridders_stencil import base_problem, HGFX, MATLAB

RUN="42404444341"
SHA="a6168bb2b1be07a0f084abc07599e9ffda61b22b"
SOURCE_FILES={
    "original-hgfx-71-infstates-and-native-ll.json":"53c998070dbbfc8b8a5fe7c90a4d087418b307a9a6ac69c48dc219918bf039b6d",
    "original-matlab-71-infstates-and-cross-ll.json":"15c2f3e50d3ff257d333e412b881053cd6bc0240137ddbae448b3ce7d1647006",
    "independent-hgf-infstates-unitsq-71-source-stage.json":"5d1d03f200bb8be7bf058fe54d64e63ab8909a29857a6750014bad83db029af0",
}


def need(v,msg):
    if not v:raise ValueError(msg)


def read_checked(path,sha):
    raw=Path(path).read_bytes()
    need(sha256(raw).hexdigest()==sha,
         "Original real HGF/unitsq stage member SHA-256 changed: "+str(path))
    return json.loads(raw),raw


def first_difference(a,b,path="$"):
    """Exact binary64 source-value comparison including signed zeros."""
    if type(a)!=type(b):
        return path+": source types differ "+type(a).__name__+" vs "+type(b).__name__
    if isinstance(a,dict):
        if a.keys()!=b.keys():
            return path+": source report key sets differ"
        for key in a:
            d=first_difference(a[key],b[key],path+"."+key)
            if d:return d
    elif isinstance(a,list):
        if len(a)!=len(b):return path+": source report array length differs"
        for i,(x,y) in enumerate(zip(a,b)):
            d=first_difference(x,y,path+"["+str(i)+"]")
            if d:return d
    elif isinstance(a,float):
        need(math.isfinite(a) and math.isfinite(b),
             "Nonfinite floating source report values")
        if struct.pack(">d",a)!=struct.pack(">d",b):
            return path+": exact binary64 source report values differ"
    elif a!=b:
        return path+": original field differs"
    return None


def run(oldterms,originalstage,root,bfgs,out):
    original={}
    for name,expect in SOURCE_FILES.items():
        original[name],_=read_checked(originalstage/name,expect)
    old={}
    for name in ("original-hgfx-71-objective-terms.json",
                 "original-matlab-71-objective-terms.json"):
        old[name],_=read_checked(oldterms/name,ORIGINAL_TERM_SHA[name])
    p,failed=base_problem(root,bfgs)
    report=main_compare(
        original["original-hgfx-71-infstates-and-native-ll.json"],
        original["original-matlab-71-infstates-and-cross-ll.json"],
        old["original-hgfx-71-objective-terms.json"],
        old["original-matlab-71-objective-terms.json"],
        failed,
        (originalstage/"original-hgfx-71-infstates-and-native-ll.json").read_bytes(),
        p,
        source_run=RUN,
        tested_sha=SHA,
    )
    report["source_hgfx_stage_sha256"]=SOURCE_FILES["original-hgfx-71-infstates-and-native-ll.json"]
    report["source_matlab_stage_sha256"]=SOURCE_FILES["original-matlab-71-infstates-and-cross-ll.json"]
    original_report=original["independent-hgf-infstates-unitsq-71-source-stage.json"]
    diff=first_difference(report,original_report)
    outcome={
       "schema":"perf01d-real-original-x0-hgf-infstates-source-archive-replay-v1",
       "status":"EXACT_BINARY64_REPLAY_OF_ENTIRE_GENUINE_STAGE_REPORT" if diff is None
                else "NOT_EXACT_REAL_STAGE_REPORT_REPLAY",
       "original_source_run":RUN,
       "original_source_sha":SHA,
       "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
       "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
       "original_true_stage_member_sha256":SOURCE_FILES,
       "original_native_constituent_sha256":ORIGINAL_TERM_SHA,
       "independent_reconstructed_source_report":report,
       "first_report_bitwise_difference":diff,
       "independent_scientific_review":"NOT_RECEIVED",
       "perf01c":"NOT_FROZEN",
       "paper_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(outcome,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":outcome["status"],"first_bitwise_difference":diff,
        "native_source_zeta_nonidentical_nodes":
            report["per_comparison_nodes_with_at_least_one_trial_difference"]["zeta"],
        "first_level_predictor_nonidentical_nodes":
            report["per_comparison_nodes_with_at_least_one_trial_difference"]["first_level_muhat"],
        "observation_source_same_predictor_different_nodes":
            report["per_comparison_nodes_with_at_least_one_trial_difference"]["matlab_vs_hgfx_observation_on_hgfx_prediction"],
        "original_science":outcome["original_scientific_fitting"],
    },sort_keys=True))
    need(diff is None,"Original full HGF infStates/unitsq source stage report NOT bitwise identical: "+str(diff))


def main():
    parser=argparse.ArgumentParser()
    for key in ("original-stage","old-terms","root","old-bfgs","output"):
        parser.add_argument("--"+key,type=Path,required=True)
    a=parser.parse_args()
    run(a.old_terms,a.original_stage,a.root,a.old_bfgs,a.output)


if __name__=="__main__":main()
