#!/usr/bin/env python3
"""Independently verify genuine frozen 71-node HGF infStates and observation-stage swaps.

All prior original source private MATLAB/HGFX negative joints AND all 128 trial
logp values must be bitwise exact on each source's own predictor. Cross-stage
observation calculations are descriptive counterfactual diagnostics only.
Scientific 63/64 NONPASS, reviewer NOT RECEIVED, PERF-01C NOT FROZEN.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import struct

import numpy as np
from hgfx.responses.unitsq_sigmoid import unitsq_sgm
from hgfx.core.trials import build_trial_masks

from original_x0_hgfx_infstates import SCHEMA as H_SCHEMA, ORIGINAL_TERM_SHA
from replay_initial_ridders_stencil_archive import MEMBERS, scientific_original, RUN, SOURCE_SHA
from subject7_first_ridders_stencil import base_problem, xbits, xhex, HGFX, MATLAB

M_SCHEMA="perf01d-frozen-matlab-infstates-71-native-and-cross-obs-v1"
STAGES=("muhat","sahat","mu","sa")


def need(v,why):
    if not v:raise ValueError(why)


def bits(x):
    need(type(x) in (int,float) and math.isfinite(float(x)),"Nonfinite source scalar")
    return struct.pack(">d",float(x))


def equal(a,b):
    return a is None and b is None if a is None or b is None else bits(a)==bits(b)


def vector_check(v,label):
    need(type(v) is list and len(v)==128,label+" shape not 128")
    need(all(type(q) in (int,float) and math.isfinite(float(q)) for q in v),
         label+" contains null, nonfinite or malformed original predictor/logp")


def states_check(d,label):
    need(type(d) is dict and set(d)==set(STAGES),
         label+" source 4 original infState components missing")
    for field in STAGES:
        rows=d[field]
        need(type(rows) is list and len(rows)==128,
             label+" source 128 trial state matrix missing: "+field)
        for row in rows:
            need(type(row) is list and len(row)==3,
                 label+" source 3 perceptual levels missing: "+field)
            for v in row:
                need(v is None or
                     (type(v) in (float,int) and math.isfinite(float(v))),
                     label+" source NaN encoding/finite field invalid: "+field)
    return np.stack([
        np.array([[np.nan if x is None else float(x) for x in row]
                  for row in d[f]],dtype=np.float64) for f in STAGES],axis=2)


def mismatch(a,b):
    need(len(a)==len(b)==128,"Required complete original 128 trial comparison")
    return [i for i,(x,y) in enumerate(zip(a,b)) if not equal(x,y)]


def main_compare(h,m,realh,realm,fit,hbytes,problem,
                 source_run=None,tested_sha=None):
    scientific_original(fit)
    need(h["schema"]==H_SCHEMA and m["schema"]==M_SCHEMA
         and h["status"]=="ORIGINAL_FROZEN_HGFX_INFSTATES_AND_UNITSQ_SOURCE_EXACT_ALL_71"
         and m["status"]=="ORIGINAL_FROZEN_MATLAB_INFSTATES_NATIVE_EXACT_AND_OBS_ON_HGFX"
         and h["frozen_hgfx_sha"]==m["frozen_hgfx_sha"]==HGFX
         and h["frozen_matlab_sha"]==m["frozen_matlab_sha"]==MATLAB
         and h["original_true_private_ridders_run"]==
             m["original_true_private_ridders_run"]==RUN
         and h["original_true_private_ridders_sha"]==
             m["original_true_private_ridders_sha"]==SOURCE_SHA
         and h["original_constituents_source_run"]==
             m["original_constituents_source_run"]=="42402421462"
         and h["original_71_node_count"]==m["original_71_node_count"]==71
         and h["n_trials"]==m["n_trials"]==128
         and h["inf_states_shape_per_node"]==
             m["inf_states_shape_per_node"]==[128,3,4]
         and h["original_scientific_fitting"]==
             m["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS"
         and h["original_failures"]=={"traj.mu":4,"traj.muhat":4}
         and m["original_failures"]=={"traj_mu":4,"traj_muhat":4}
         and h["original_source_term_sha256"]==ORIGINAL_TERM_SHA
         and m["original_hgfx_infstates_sha256"]==sha256(hbytes).hexdigest()
         and h["independent_scientific_review"]==
             m["independent_scientific_review"]=="NOT_RECEIVED"
         and h["perf01c"]==m["perf01c"]=="NOT_FROZEN"
         and h["predorpost"]==m["predorpost"]==1
         and h["selected_source_infstate_component"]=="muhat"
         and m["native_fit_unmodified"] is True,
         "Original 71-node source model / scientific NONPASS provenance changed")
    expectedrun=source_run if source_run is not None else os.getenv("GITHUB_RUN_ID")
    expectedsha=tested_sha if tested_sha is not None else os.getenv("GITHUB_SHA")
    need(h["environment"]["run_id"]==m["github_run_id"]==expectedrun
         and h["environment"]["tested_sha"]==m["tested_sha"]==expectedsha,
         "Real HGFX and MATLAB HGF intermediate source samples not from same runner/commit")
    need(m["native_perceptual_function"]=="hgf_binary"
         and m["native_observation_function"]=="unitsq_sgm"
         and m["native_perceptual_file"].replace("\\","/").endswith("/_original_models/hgf_binary.m")
         and m["native_observation_file"].replace("\\","/").endswith("/observation/unitsq_sgm.m")
         and m["native_fitmodel_file"].replace("\\","/").endswith("/core/fitModel.m"),
         "Frozen original MATLAB source model lineage not verified")
    hr=h["nodes"];mr=m["nodes"]
    need(type(hr) is list and type(mr) is list and len(hr)==len(mr)==71
         and len(realh["nodes"])==len(realm["nodes"])==71,
         "Missing original first-gradient 71 HGF/observation source samples")
    mask=build_trial_masks(problem.responses,problem.inputs)
    irregular=np.flatnonzero(mask.irregular).astype(int).tolist()
    need(h["original_irregular_trial_indices_zero_based"]==irregular,
         "Original genuine ignored/irregular trial mask changed")
    counts={q:0 for q in (
        "first_level_muhat", "first_level_mu","native_per_trial_logp",
        "matlab_vs_hgfx_observation_on_hgfx_prediction",
        "hgfx_vs_matlab_observation_on_matlab_prediction",
        "hgfx_predictor_effect_on_hgfx_observation",
        "matlab_predictor_effect_on_matlab_observation",
        "zeta"
    )}
    every_128={k:[0]*128 for k in counts if k!="zeta"}
    total_comp={k:0 for k in STAGES}
    stage_nan_mask_mismatches={k:0 for k in STAGES}
    different_hgfx_on_hgfx_and_matlab_on_matlab=0
    nodes=[]
    for i,(a,b,past_h,past_m) in enumerate(zip(hr,mr,realh["nodes"],realm["nodes"])):
        x=a["x"]
        need(a["ordinal"]==b["ordinal"]==past_h["original_node_index"]==
             past_m["original_node_index"]==i
             and xbits(x)==xbits(b["x"])==xbits(past_h["x"])==xbits(past_m["x"])
             and xhex(x)==a["x_hex"]==b["x_hex"],
             "Original all-71 Ridders same-x x bits or ordering changed at "+str(i))
        require_joint=(bits(a["native_source_objective"])==bits(past_h["original_hgfx_source_scalar"])
         and bits(b["original_genuine_private_objective"])==bits(past_m["original_matlab_private_source_scalar"])
         and bits(a["original_matlab_private_source_objective"])==bits(b["original_genuine_private_objective"])
         and bits(a["native_source_objective"])==bits(b["original_hgfx_objective"]))
        need(require_joint,"Previously verified real frozen private/source objective scalar missing")
        for name,row,past in (("HGFX",a,past_h),("MATLAB",b,past_m)):
            vector_check(row["native_logp"],name+" original unitsq")
            vector_check(row["native_prediction_level1"],name+" original predictor")
            vector_check(row["native_posterior_level1"],name+" original posterior")
            old=past["components"]["full_trial_log_likelihood"]
            vector_check(old,name+" source oracle logp")
            need(not mismatch(row["native_logp"],old),
                 "Original native "+name+" unitsq logp does not reproduce original exact 128 source trial likelihoods at "+str(i))
        vector_check(b["matlab_unitsq_on_hgfx_prediction_logp"],
                     "Original MATLAB unitsq on HGFX prediction")
        ha=states_check(a["native_inf_states"],"HGFX")
        ma=states_check(b["native_inf_states"],"MATLAB")
        # Independently execute unchanged HGFX observation on its own
        # reconstituted original infStates before using them for a swap.
        check_hgfx_native=unitsq_sgm(
            problem.responses,ha,problem.expand(x)[problem.n_perceptual:],
            irregular_trials=irregular,predorpost=1)[0]
        check_hgfx_native=[float(z) for z in np.asarray(check_hgfx_native).reshape(-1)]
        need(not mismatch(check_hgfx_native,a["native_logp"]),
             "Source HGFX observation did not reproduce its own genuine all-128 native trial LL")
        for idx,(name,predictor,posterior,states) in enumerate((
            ("HGFX",a["native_prediction_level1"],a["native_posterior_level1"],ha),
            ("MATLAB",b["native_prediction_level1"],b["native_posterior_level1"],ma),
        )):
            need(all(equal(predictor[j],float(states[j,0,0])) and
                     equal(posterior[j],float(states[j,0,2])) for j in range(128)),
                 name+" source selected predictor/posterior not genuine infStates slice")
        for k,field in enumerate(STAGES):
            diff=0;nan_diff=0
            for t in range(128):
                for lvl in range(3):
                    aval=a["native_inf_states"][field][t][lvl]
                    bval=b["native_inf_states"][field][t][lvl]
                    if (aval is None)!=(bval is None):
                        nan_diff+=1
                    if not equal(aval,bval):
                        diff+=1
            if diff:total_comp[field]+=1
            if nan_diff:stage_nan_mask_mismatches[field]+=1
        full=problem.expand(x)
        obs=full[problem.n_perceptual:]
        source_zeta_h=float(a["native_zeta"])
        source_zeta_m=float(b["native_zeta"])
        need(math.isfinite(source_zeta_h) and math.isfinite(source_zeta_m),
             "Nonfinite original zeta observation parameter")
        # Frozen HGFX observation on genuine MATLAB selected predictor x
        # with untouched original HGFX original infStates for other components.
        substitute=ha.copy()
        substitute[:,0,0]=np.array(b["native_prediction_level1"],dtype=np.float64)
        hgfx_on_matlab_pred=unitsq_sgm(
            problem.responses,substitute,obs,
            irregular_trials=irregular,predorpost=1)[0]
        hgfx_on_matlab_pred=[float(z) for z in np.asarray(hgfx_on_matlab_pred).reshape(-1)]
        vector_check(hgfx_on_matlab_pred,"HGFX unitsq on genuine MATLAB predicted probability")
        # Four direct comparisons on the SAME frozen original free x.
        diffs={
            "first_level_muhat":mismatch(a["native_prediction_level1"],b["native_prediction_level1"]),
            "first_level_mu":mismatch(a["native_posterior_level1"],b["native_posterior_level1"]),
            "native_per_trial_logp":mismatch(a["native_logp"],b["native_logp"]),
            "matlab_vs_hgfx_observation_on_hgfx_prediction":
                mismatch(a["native_logp"],b["matlab_unitsq_on_hgfx_prediction_logp"]),
            "hgfx_vs_matlab_observation_on_matlab_prediction":
                mismatch(hgfx_on_matlab_pred,b["native_logp"]),
            "hgfx_predictor_effect_on_hgfx_observation":
                mismatch(a["native_logp"],hgfx_on_matlab_pred),
            "matlab_predictor_effect_on_matlab_observation":
                mismatch(b["matlab_unitsq_on_hgfx_prediction_logp"],b["native_logp"]),
        }
        if diffs["native_per_trial_logp"]:
            different_hgfx_on_hgfx_and_matlab_on_matlab+=1
        for key,differ in diffs.items():
            if differ:counts[key]+=1
            for t in differ:every_128[key][t]+=1
        if bits(source_zeta_h)!=bits(source_zeta_m):
            counts["zeta"]+=1
        nodes.append({
            "original_node_index":i,"original_source_x":x,
            "component_nan_or_finite_structure_matches":all(
                (a["native_inf_states"][f][t][lv] is None)==
                (b["native_inf_states"][f][t][lv] is None)
                for f in STAGES for t in range(128) for lv in range(3)),
            "per_node_bitwise_mismatch_trial_indices":diffs,
            "hgfx_original_observation_zeta":source_zeta_h,
            "matlab_original_observation_zeta":source_zeta_m,
            "hgfx_unitsq_on_matlab_pred_logp":hgfx_on_matlab_pred,
            "original_hgfx_native_logp":a["native_logp"],
            "original_matlab_native_logp":b["native_logp"],
            "original_matlab_unitsq_on_hgfx_prediction_logp":b["matlab_unitsq_on_hgfx_prediction_logp"],
        })
    need(different_hgfx_on_hgfx_and_matlab_on_matlab==71,
         "Original 71/71 per-trial likelihood mismatch observation unexpectedly changed")
    need(counts["native_per_trial_logp"]==71,
         "Original 71 genuine source native observation mismatch changed")
    return {
        "schema":"perf01d-original-hgf-infstates-observation-stage-bidirectional-audit-v1",
        "status":"AUTHOR_SIDE_SAME_X_FROZEN_HGF_OBSERVATION_STAGE_AUDIT_NOT_SCIENTIFIC_PASS",
        "original_true_private_ridders_run":"42389292284",
        "original_reproducible_source_terms_run":"42402421462",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_mu":4,"original_subject7_failed_muhat":4,
        "all_71_native_per_trial_ll_exact_vs_genuine_archived_source":True,
        "original_71_node_count":71,"original_trial_count":128,
        "per_component_infstate_node_any_bit_difference_counts":total_comp,
        "per_component_infstate_node_nan_mask_differences":stage_nan_mask_mismatches,
        "per_comparison_nodes_with_at_least_one_trial_difference":counts,
        "per_comparison_each_trial_bitwise_mismatch_frequency":every_128,
        "all_original_nodes_and_counterfactual_trial_indices":nodes,
        "counterfactual_observation_inputs_only_not_original_fit":True,
        "source_first_changed_instruction_or_operation":"NOT_IDENTIFIED",
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","paper_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }


def main():
    parser=argparse.ArgumentParser()
    for f in ("hgfx-source","matlab-source","prior-hgfx-terms",
              "prior-matlab-terms","original-fit","root","old-bfgs","output"):
        parser.add_argument("--"+f,required=True,type=Path)
    a=parser.parse_args()
    hbytes=a.hgfx_source.read_bytes()
    h=json.loads(hbytes)
    m=json.loads(a.matlab_source.read_bytes())
    past_h=json.loads(a.prior_hgfx_terms.read_bytes())
    past_m=json.loads(a.prior_matlab_terms.read_bytes())
    for f,v in ((a.prior_hgfx_terms,ORIGINAL_TERM_SHA["original-hgfx-71-objective-terms.json"]),
                (a.prior_matlab_terms,ORIGINAL_TERM_SHA["original-matlab-71-objective-terms.json"])):
        need(sha256(f.read_bytes()).hexdigest()==v,
             "Original last successful reference objective constituent source SHA changed")
    p,fit=base_problem(a.root,a.old_bfgs)
    report=main_compare(h,m,past_h,past_m,fit,hbytes,p)
    report["source_hgfx_stage_sha256"]=sha256(hbytes).hexdigest()
    report["source_matlab_stage_sha256"]=sha256(a.matlab_source.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":report["status"],
        "per_component_infstate_node_any_bit_difference_counts":
            report["per_component_infstate_node_any_bit_difference_counts"],
        "per_component_infstate_node_nan_mask_differences":
            report["per_component_infstate_node_nan_mask_differences"],
        "per_comparison_nodes_with_at_least_one_trial_difference":
            report["per_comparison_nodes_with_at_least_one_trial_difference"],
        "scientific":report["original_science"]},sort_keys=True))


if __name__=="__main__":main()
