#!/usr/bin/env python3
"""Replay ORIGINAL frozen HGFX unitsq arithmetic intermediates on two authentic predictors.

All 71 true MATLAB-private initial Ridders same-x points × 128 trials ×
two authentic HGF level-1 predictors. The previously captured native source
output is never replaced. Unexpected binary64 changes are recorded and
independent verifier must fail closed. No model edits or optimizer/timing.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys

import numpy as np
from hgfx.math.matlab_exp import matlab_exp_scalar
from hgfx.responses.unitsq_sigmoid import unitsq_sgm, _scalar_log
from hgfx.core.trials import build_trial_masks

from original_x0_hgfx_infstates import ORIGINAL_TERM_SHA
from compare_original_x0_infstates_observation import states_check
from replay_initial_ridders_stencil_archive import scientific_original, RUN, SOURCE_SHA
from subject7_first_ridders_stencil import base_problem, HGFX, MATLAB, xbits

SOURCE_H="53c998070dbbfc8b8a5c5ce7e8d962b44f9820635f60c567fd2012bf48fcd415"
SOURCE_M="15c2f3e50d3ff257d333e412b881053cd6bc0240137ddbae448b3ce7d1647006"
SOURCE_AUDIT="5d1d03f200bb8be7bf058fe54d64e63ab8909a29857a6750014bad83db029af0"
SOURCE_RUN="42404444341"
SOURCE_COMMIT="a6168bb2b1be07a0f084abc07599e9ffda61b22b"
SCHEMA="perf01d-authentic-hgfx-unitsq-arithmetic-stages-71x128x2-v1"
STAGE_NAMES=(
    "x", "y", "zeta", "one_minus_x", "logx_raw", "logx_alt",
    "logx_selected", "log1mx_raw", "log1mx_alt", "log1mx_selected",
    "pow_one_minus_x", "pow_x", "normalizer_sum", "log_normalizer",
    "log_ratio", "response_times_ze", "response_term", "base_term",
    "positive_terms_sum", "formula_logp",
)


def need(ok,msg):
    if not ok: raise ValueError(msg)


def bit(x):
    need(isinstance(x,(float,int,np.floating)) and math.isfinite(float(x)),
         "Nonfinite original regular source observation term")
    return struct.pack(">d",float(x))


def compare(original,actual):
    need(len(original)==len(actual)==128,"All original source 128 trials required")
    return [int(i) for i,(a,b) in enumerate(zip(original,actual))
            if bit(a)!=bit(b)]


def stage_formula(x,y,zeta):
    xx=np.asarray(x,dtype=np.float64)
    yy=np.asarray(y,dtype=np.float64)
    ze=np.float64(zeta)
    need(xx.shape==yy.shape==(128,) and np.isfinite(xx).all()
         and np.all((xx>0)&(xx<1)) and math.isfinite(ze) and ze>0,
         "Original true source input probabilities/zeta invalid")
    with np.errstate(divide="ignore",invalid="ignore",over="ignore",under="ignore"):
        one_minus=np.float64(1.0)-xx
        logx_raw=_scalar_log(xx)
        logx_alt=np.log1p(xx-np.float64(1.0))
        use_alt_x=(np.float64(1.0)-xx)<1e-4
        logx=logx_raw.copy()
        logx[use_alt_x]=logx_alt[use_alt_x]

        log1mx_raw=_scalar_log(np.float64(1.0)-xx)
        log1mx_alt=np.log1p(-xx)
        use_alt_one=xx<1e-4
        log1mx=log1mx_raw.copy()
        log1mx[use_alt_one]=log1mx_alt[use_alt_one]

        pow_one=one_minus**ze
        pow_x=xx**ze
        norm=pow_one+pow_x
        log_norm=_scalar_log(norm)
        ratio=logx-log1mx
        response_times_ze=yy*ze
        response_term=response_times_ze*ratio
        base_term=ze*log1mx
        added=response_term+base_term
        final=added-log_norm

    named={
      "x":xx,"y":yy,"zeta":np.full(128,ze,dtype=np.float64),
      "one_minus_x":one_minus,"logx_raw":logx_raw,"logx_alt":logx_alt,
      "logx_selected":logx,"log1mx_raw":log1mx_raw,
      "log1mx_alt":log1mx_alt,"log1mx_selected":log1mx,
      "pow_one_minus_x":pow_one,"pow_x":pow_x,
      "normalizer_sum":norm,"log_normalizer":log_norm,
      "log_ratio":ratio,"response_times_ze":response_times_ze,
      "response_term":response_term,"base_term":base_term,
      "positive_terms_sum":added,"formula_logp":final,
    }
    need(tuple(named)==STAGE_NAMES,"Original frozen observation intermediate stage inventory altered")
    need(all(z.shape==(128,) and np.isfinite(z).all() for z in named.values()),
         "Nonfinite genuine source arithmetic intermediate")
    return {k: [float(n) for n in v] for k,v in named.items()}


def load_json(path,digest):
    bb=path.read_bytes()
    need(sha256(bb).hexdigest()==digest,"Original immutable genuine raw 71-stage SHA changed: "+str(path.name))
    return json.loads(bb)


def produce(root,old_bfgs,old_stage,old_terms,out):
    p,origfit=base_problem(root,old_bfgs)
    scientific_original(origfit)
    h=load_json(old_stage/"original-hgfx-71-infstates-and-native-ll.json",SOURCE_H)
    m=load_json(old_stage/"original-matlab-71-infstates-and-cross-ll.json",SOURCE_M)
    audit=load_json(old_stage/"independent-hgf-infstates-unitsq-71-source-stage.json",SOURCE_AUDIT)
    hterms=load_json(old_terms/"original-hgfx-71-objective-terms.json",
                     ORIGINAL_TERM_SHA["original-hgfx-71-objective-terms.json"])
    mterms=load_json(old_terms/"original-matlab-71-objective-terms.json",
                     ORIGINAL_TERM_SHA["original-matlab-71-objective-terms.json"])
    need(h["schema"]=="perf01d-frozen-hgfx-infstates-71-native-obs-v1"
         and m["schema"]=="perf01d-frozen-matlab-infstates-71-native-and-cross-obs-v1"
         and audit["schema"]=="perf01d-original-hgf-infstates-observation-stage-bidirectional-audit-v1"
         and h["frozen_hgfx_sha"]==m["frozen_hgfx_sha"]==HGFX
         and h["frozen_matlab_sha"]==m["frozen_matlab_sha"]==MATLAB
         and h["original_scientific_fitting"]==m["original_scientific_fitting"]==
             "63/64 SCIENTIFIC NONPASS"
         and h["original_failures"]=={"traj.mu":4,"traj.muhat":4}
         and m["original_failures"]=={"traj_mu":4,"traj_muhat":4}
         and h["environment"]["run_id"]==m["github_run_id"]==SOURCE_RUN
         and h["environment"]["tested_sha"]==m["tested_sha"]==SOURCE_COMMIT
         and h["original_true_private_ridders_run"]==RUN
         and h["original_true_private_ridders_sha"]==SOURCE_SHA
         and h["original_71_node_count"]==m["original_71_node_count"]==71
         and len(h["nodes"])==len(m["nodes"])==len(hterms["nodes"])==len(mterms["nodes"])==71
         and audit["per_comparison_nodes_with_at_least_one_trial_difference"]["zeta"]==0
         and audit["per_comparison_nodes_with_at_least_one_trial_difference"]["first_level_muhat"]==8
         and audit["per_comparison_nodes_with_at_least_one_trial_difference"]["native_per_trial_logp"]==71
         and audit["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and h["predorpost"]==m["predorpost"]==1
         and h["independent_scientific_review"]==m["independent_scientific_review"]=="NOT_RECEIVED"
         and h["perf01c"]==m["perf01c"]=="NOT_FROZEN",
         "Original real first-gradient stage/failed scientific provenance altered")
    masks=build_trial_masks(p.responses,p.inputs)
    need(np.array_equal(np.flatnonzero(masks.irregular),np.asarray(h["original_irregular_trial_indices_zero_based"],dtype=int)),
         "Irregular response mask changed")
    need(not masks.irregular.any(),"Prespecified original 128 fully-regular trials required")
    yy=np.asarray(p.responses,dtype=np.float64)
    need(yy.shape==(128,) and np.all((yy==0)|(yy==1)),"Original binary responses changed")
    rows=[]
    for i,(hh,mm,ht,mt) in enumerate(zip(h["nodes"],m["nodes"],hterms["nodes"],mterms["nodes"])):
        x=hh["x"]
        need(i==hh["ordinal"]==mm["ordinal"]==ht["original_node_index"]==mt["original_node_index"]
             and xbits(x)==xbits(mm["x"])==xbits(ht["x"])==xbits(mt["x"]),
             "Original same-x real source order or float bits changed")
        observed_h=hh["native_prediction_level1"]
        observed_m=mm["native_prediction_level1"]
        need(len(observed_h)==len(observed_m)==128 and
             all(bit(t) for t in observed_h+observed_m),
             "Missing original genuine input predictions")
        full=p.expand(x)
        obs=full[p.n_perceptual:]
        zeta=float(matlab_exp_scalar(obs[0]))
        need(bit(zeta)==bit(hh["native_zeta"])==bit(mm["native_zeta"]),
             "Native HGF/observation zeta not original same 71-node bits")
        original_state=states_check(hh["native_inf_states"],"authentic frozen HGFX")
        cases=[]
        for case,pred in (
            ("hgfx_predictor",observed_h),
            ("matlab_predictor",observed_m),
        ):
            infstate=original_state.copy()
            infstate[:,0,0]=np.asarray(pred,dtype=np.float64)
            native=unitsq_sgm(p.responses,infstate,obs,predorpost=1,
                              irregular_trials=())[0]
            native=[float(v) for v in np.asarray(native).reshape(-1)]
            old_native=(hh["native_logp"] if case=="hgfx_predictor" else
                        audit["all_original_nodes_and_counterfactual_trial_indices"][i]["hgfx_unitsq_on_matlab_pred_logp"])
            old_matlab=(mm["matlab_unitsq_on_hgfx_prediction_logp"] if case=="hgfx_predictor"
                        else mm["native_logp"])
            need(len(old_native)==len(old_matlab)==128,"Original genuine cross-stage native source rows missing")
            algebra=stage_formula(pred,yy,zeta)
            cases.append({
                "input_case":case,"input_prediction":pred,
                "native_hgfx_observation_ll":native,
                "old_genuine_hgfx_observation_ll":old_native,
                "old_genuine_matlab_observation_ll":old_matlab,
                "native_vs_old_source_differences":compare(old_native,native),
                "formula_vs_new_native_differences":compare(native,algebra["formula_logp"]),
                "stage_arrays":algebra,
            })
        rows.append({"original_node_index":i,"x":x,"cases":cases})
    statuses={
        "native_against_genuine_previous_hgfx_mismatch_counts":
           sum(len(c["native_vs_old_source_differences"]) for row in rows for c in row["cases"]),
        "formula_against_new_native_mismatch_counts":
           sum(len(c["formula_vs_new_native_differences"]) for row in rows for c in row["cases"]),
    }
    result={
        "schema":SCHEMA,
        "status":"AUTHOR_SIDE_SOURCE_STAGE_REPLAY_UNVERIFIED_UNTIL_INDEPENDENT_VERIFIER",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "source_genuine_run":SOURCE_RUN,"source_genuine_sha":SOURCE_COMMIT,
        "original_63_64_fit":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failures":{"traj.mu":4,"traj.muhat":4},
        "node_count":71,"trials":128,"cases_each_node":2,
        "stage_fields":list(STAGE_NAMES),"source_digests":{
            "hgfx":SOURCE_H,"matlab":SOURCE_M,"original_stage_audit":SOURCE_AUDIT},
        "status_counts":statuses,"nodes":rows,
        "environment":{"github_run_id":os.environ.get("GITHUB_RUN_ID",""),
                       "github_sha":os.environ.get("GITHUB_SHA",""),
                       "platform":platform.platform(),"numpy":np.__version__,
                       "python":sys.version},
        "independent_scientific_reviewer":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","timing":"NOT_RUN","gpu":"NOT_RUN",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"source":"HGFX","nodes":len(rows),"cases_per_node":2,
                      "native_source_mismatch":statuses["native_against_genuine_previous_hgfx_mismatch_counts"],
                      "formula_mismatch":statuses["formula_against_new_native_mismatch_counts"],
                      "science":"63/64 NONPASS"},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    for k in ("root","old-bfgs","old-stage","old-terms","output"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    produce(a.root,a.old_bfgs,a.old_stage,a.old_terms,a.output)


if __name__=="__main__":
    main()
