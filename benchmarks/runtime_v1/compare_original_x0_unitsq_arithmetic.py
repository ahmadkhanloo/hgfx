#!/usr/bin/env python3
"""Independent source-first unitsq arithmetic stage comparison on original same predictors.

Require all 71×128×2 native MATLAB/HGFX original-source LL values exactly,
plus exact source formula native output on each engine, before a validated
first active numeric difference claim. Raw intermediate mismatches are
preserved even when cross-host source-native replay is nonexact.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

from original_x0_unitsq_arithmetic_python import (
    SCHEMA as H_SCHEMA, STAGE_NAMES, SOURCE_H, SOURCE_M, SOURCE_AUDIT,
    SOURCE_RUN, SOURCE_COMMIT, bit, compare
)
from subject7_first_ridders_stencil import base_problem, xbits, HGFX, MATLAB
from replay_initial_ridders_stencil_archive import scientific_original

M_SCHEMA="perf01d-authentic-matlab-unitsq-arithmetic-stages-71x128x2-v1"
SCHEMA="perf01d-same-true-predictor-unitsq-first-arithmetic-stage-audit-v1"
ACTIVE_STAGES=(
    "one_minus_x","logx_selected","log1mx_selected","pow_one_minus_x",
    "pow_x","normalizer_sum","log_normalizer","log_ratio",
    "response_times_ze","response_term","base_term","positive_terms_sum",
    "formula_logp",
)


def need(ok,msg):
    if not ok:raise ValueError(msg)


def finite_vector(arr,label):
    need(type(arr) is list and len(arr)==128,label+": original complete 128-trial vector missing")
    need(all(type(v) in (int,float) and math.isfinite(v) for v in arr),
         label+": nonfinite/malformed authentic source intermediate")


def report(h,m,orig_h,orig_m,fit,source_hbytes,run_id,commit):
    scientific_original(fit)
    need(h["schema"]==H_SCHEMA and m["schema"]==M_SCHEMA
         and h["frozen_hgfx_sha"]==m["frozen_hgfx_sha"]==HGFX
         and h["frozen_matlab_sha"]==m["frozen_matlab_sha"]==MATLAB
         and h["source_genuine_run"]==m["source_genuine_run"]==SOURCE_RUN
         and h["source_genuine_sha"]==m["source_genuine_sha"]==SOURCE_COMMIT
         and h["original_63_64_fit"]==m["original_63_64_fit"]==
             "63/64 SCIENTIFIC NONPASS"
         and h["original_subject7_failures"]=={"traj.mu":4,"traj.muhat":4}
         and m["original_subject7_failures"]=={"traj_mu":4,"traj_muhat":4}
         and h["node_count"]==m["node_count"]==71
         and h["trials"]==m["trials"]==128
         and h["cases_each_node"]==m["cases_each_node"]==2
         and h["stage_fields"]==m["stage_fields"]==list(STAGE_NAMES)
         and h["source_digests"]==
             {"hgfx":SOURCE_H,"matlab":SOURCE_M,"original_stage_audit":SOURCE_AUDIT}
         and h["environment"]["github_run_id"]==m["github_run_id"]==run_id
         and h["environment"]["github_sha"]==m["tested_sha"]==commit
         and h["independent_scientific_reviewer"]==
             m["independent_scientific_reviewer"]=="NOT_RECEIVED"
         and h["perf01c"]==m["perf01c"]=="NOT_FROZEN"
         and m["native_fit_unmodified"] is True
         and m["native_obs_model"]=="unitsq_sgm"
         and m["native_obs_file"].replace("\\","/").endswith("/observation/unitsq_sgm.m")
         and m["native_fitmodel_file"].replace("\\","/").endswith("/core/fitModel.m"),
         "Original real unitsq source, model lineage or 63/64 NONPASS verification changed")
    need(len(h["nodes"])==len(m["nodes"])==len(orig_h["nodes"])==len(orig_m["nodes"])==71,
         "Full 71 authentic source model nodes required")
    raw_first=Counter()
    active_first=Counter()
    node_any={c:Counter() for c in ("hgfx_predictor","matlab_predictor")}
    final_diff_nodes={c:0 for c in node_any}
    valid_count=Counter()
    discrepancies=[]
    first_stage_rows=[]
    original_native_nonexact=[]
    original_formula_nonexact=[]
    for i,(hn,mn,oh,om) in enumerate(zip(h["nodes"],m["nodes"],
                                        orig_h["nodes"],orig_m["nodes"])):
        x=hn["x"]
        need(hn["original_node_index"]==mn["original_node_index"]==
             oh["ordinal"]==om["ordinal"]==i
             and xbits(x)==xbits(mn["x"])==xbits(oh["x"])==xbits(om["x"]),
             "Original real 71 x coordinate source identity/order modified")
        need(type(hn["cases"]) is list and type(mn["cases"]) is list
             and len(hn["cases"])==len(mn["cases"])==2,
             "Missing authentic HGFX or MATLAB predictor cases")
        for case_i in (0,1):
            hc=hn["cases"][case_i];mc=mn["cases"][case_i]
            case=("hgfx_predictor" if case_i==0 else "matlab_predictor")
            need(hc["input_case"]==mc["input_case"]==case,
                 "Original two source predictor case order changed")
            for k in ("input_prediction","native_hgfx_observation_ll",
                      "old_genuine_hgfx_observation_ll",
                      "old_genuine_matlab_observation_ll"):
                if k in hc:finite_vector(hc[k],"hgfx."+k)
            for k in ("input_prediction","native_matlab_observation_ll",
                      "old_genuine_matlab_observation_ll"):
                if k in mc:finite_vector(mc[k],"matlab."+k)
            need(not compare(hc["input_prediction"],mc["input_prediction"]),
                 "Not SAME original binary64 predictor inputs across both actual source models")
            predictor=(oh["native_prediction_level1"] if case_i==0
                       else om["native_prediction_level1"])
            need(not compare(hc["input_prediction"],predictor),
                 "Original real selected HGF predictor was changed in formula replay")
            old_h=(oh["native_logp"] if case_i==0 else
                   orig_h["old_hgfx_on_matlab_predictor"][i])
            old_m=(om["matlab_unitsq_on_hgfx_prediction_logp"] if case_i==0
                   else om["native_logp"])
            need(not compare(hc["old_genuine_hgfx_observation_ll"],old_h)
                 and not compare(mc["old_genuine_matlab_observation_ll"],old_m)
                 and not compare(hc["old_genuine_matlab_observation_ll"],old_m),
                 "Previous original frozen source native cross-observation result changed")
            hc_native=hc["native_hgfx_observation_ll"]
            mc_native=mc["native_matlab_observation_ll"]
            mismatch_h=compare(old_h,hc_native)
            mismatch_m=compare(old_m,mc_native)
            if mismatch_h or mismatch_m:
                original_native_nonexact.append({
                    "node":i,"case":case,"hgfx_native_vs_true_source":mismatch_h,
                    "matlab_native_vs_true_source":mismatch_m})
            need(hc["native_vs_old_source_differences"]==mismatch_h
                 and mc["native_vs_old_source_differences"]==mismatch_m,
                 "Source producer native exact-bit mismatch inventory cannot be independently reproduced")
            hs=hc["stage_arrays"];ms=mc["stage_arrays"]
            need(type(hs) is dict and type(ms) is dict
                 and set(hs)==set(ms)==set(STAGE_NAMES),
                 "Frozen source mathematical stage fields omitted or fabricated")
            for field in STAGE_NAMES:
                finite_vector(hs[field],"hgfx."+field)
                finite_vector(ms[field],"matlab."+field)
            need(not compare(hs["x"],predictor) and
                 not compare(ms["x"],predictor) and
                 not compare(hs["x"],hc["input_prediction"]) and
                 not compare(ms["x"],mc["input_prediction"]),
                 "Source formula not evaluated at exact genuine original x predictor")
            formula_h=compare(hs["formula_logp"],hc_native)
            formula_m=compare(ms["formula_logp"],mc_native)
            need(formula_h==hc["formula_vs_new_native_differences"]
                 and formula_m==mc["formula_vs_new_native_differences"],
                 "Source formula exact-bit mismatches not independently reproduced")
            if formula_h or formula_m:
                original_formula_nonexact.append({
                    "node":i,"case":case,"hgfx_formula_vs_native":formula_h,
                    "matlab_formula_vs_native":formula_m})
            need(not compare(hs["y"],ms["y"]) and
                 not compare(hs["zeta"],ms["zeta"]),
                 "Original source response y or native zeta differs on identical predictor")
            native_diff=compare(hc_native,mc_native)
            if native_diff:final_diff_nodes[case]+=1
            per_case_raw=Counter();per_case_active=Counter()
            for j in range(128):
                differing=[field for field in STAGE_NAMES if bit(hs[field][j])!=bit(ms[field][j])]
                first=differing[0] if differing else None
                active=next((q for q in ACTIVE_STAGES if q in differing),None)
                if first:raw_first[(case,first)]+=1
                if active:active_first[(case,active)]+=1
                for field in differing:
                    per_case_raw[field]+=1
                    node_any[case][field]+=1
                if differing or j in native_diff:
                    first_stage_rows.append({
                       "original_source_node_zero_based":i,
                       "original_trial_zero_based":j,
                       "predictor_case":case,
                       "first_recorded_source_order_stage":first,
                       "first_active_expression_stage":active,
                       "all_different_source_formula_stages":differing,
                       "native_trial_logp_bits_differ":j in native_diff,
                       "original_hgfx_native":hc_native[j],
                       "original_matlab_native":mc_native[j],
                       "first_active_hgfx_bits":(
                           bit(hs[active][j]).hex() if active else None),
                       "first_active_matlab_bits":(
                           bit(ms[active][j]).hex() if active else None),
                    })
            valid_count[case]+=128
            discrepancies.append({
                "original_source_node_index":i,
                "original_predictor_case":case,
                "native_bit_difference_trial_indices":native_diff,
                "raw_stage_bit_difference_counts":dict(per_case_raw),
                "native_source_check_hgfx_failures":mismatch_h,
                "native_source_check_matlab_failures":mismatch_m,
                "formula_reconstruction_hgfx_failures":formula_h,
                "formula_reconstruction_matlab_failures":formula_m,
            })
    need(valid_count=={"hgfx_predictor":9088,"matlab_predictor":9088},
         "Original true stage full 71x128x2 source denominator was shrunk")
    classification_ready=not original_native_nonexact and not original_formula_nonexact
    return {
        "schema":SCHEMA,
        "status":("VALIDATED_SAME_X_SOURCE_FORMULA_INTERMEDIATE_LOCALIZATION"
                  if classification_ready else
                  "INCONCLUSIVE_ORIGINAL_NATIVE_OR_FORMULA_EXACT_REPLAY_NONMATCH"),
        "original_source_run":SOURCE_RUN,"original_source_commit":SOURCE_COMMIT,
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "source_hgfx_arithmetic_sha256":sha256(source_hbytes).hexdigest(),
        "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_traj_mu":4,"original_subject7_failed_traj_muhat":4,
        "source_trial_comparisons_per_predictor":dict(valid_count),
        "source_formula_field_order":list(STAGE_NAMES),
        "source_order_first_differing_stage_freq":{
            c:{k:n for (cc,k),n in raw_first.items() if cc==c} for c in valid_count},
        "effective_first_differing_stage_freq":{
            c:{k:n for (cc,k),n in active_first.items() if cc==c} for c in valid_count},
        "native_observation_output_any_difference_nodes":final_diff_nodes,
        "all_named_stage_any_bit_difference_across_node_trial_values":{
            c:dict(v) for c,v in node_any.items()},
        "source_native_exact_guard_failures":original_native_nonexact,
        "formula_native_exact_guard_failures":original_formula_nonexact,
        "every_original_source_node_case_comparison":discrepancies,
        "every_original_trial_with_any_intermediate_difference":first_stage_rows,
        "source_intermediate_not_direct_private_matlab_tracing":True,
        "cross_cpu_original_observation_bitwise_reproducibility":"MIXED_NOT_PASS",
        "scientific_full_fit_unchanged":True,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","paper_timing":"NOT_RUN","gpu":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for field in ("hgfx-arithmetic","matlab-arithmetic","old-hgfx-stage","old-matlab-stage",
                  "old-independent-stage","root","old-bfgs","output"):
        p.add_argument("--"+field,type=Path,required=True)
    a=p.parse_args()
    hbytes=a.hgfx_arithmetic.read_bytes()
    h=json.loads(hbytes)
    m=json.loads(a.matlab_arithmetic.read_bytes())
    oldhraw=a.old_hgfx_stage.read_bytes()
    oldmraw=a.old_matlab_stage.read_bytes()
    oldindraw=a.old_independent_stage.read_bytes()
    need(sha256(oldhraw).hexdigest()==SOURCE_H
         and sha256(oldmraw).hexdigest()==SOURCE_M
         and sha256(oldindraw).hexdigest()==SOURCE_AUDIT,
         "Original genuine source stage SHA-256 changed")
    oh=json.loads(oldhraw);om=json.loads(oldmraw)
    orig_audit=json.loads(oldindraw)
    need(orig_audit["schema"]==
         "perf01d-original-hgf-infstates-observation-stage-bidirectional-audit-v1"
         and orig_audit["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and orig_audit["per_comparison_nodes_with_at_least_one_trial_difference"]["zeta"]==0,
         "Original prior audit changed")
    oh["old_hgfx_on_matlab_predictor"]=[
        z["hgfx_unitsq_on_matlab_pred_logp"]
        for z in orig_audit["all_original_nodes_and_counterfactual_trial_indices"]]
    _,fit=base_problem(a.root,a.old_bfgs)
    data=report(h,m,oh,om,fit,hbytes,
                h["environment"]["github_run_id"],
                h["environment"]["github_sha"])
    data["source_matlab_arithmetic_sha256"]=sha256(a.matlab_arithmetic.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":data["status"],
        "original_scientific_fitting":data["original_scientific_fitting"],
        "native_source_guard_failures":len(data["source_native_exact_guard_failures"]),
        "formula_guard_failures":len(data["formula_native_exact_guard_failures"]),
        "original_native_difference_nodes":data["native_observation_output_any_difference_nodes"],
        "effective_first_differing_stage_freq":data["effective_first_differing_stage_freq"],
    },sort_keys=True))
    need(data["status"]=="VALIDATED_SAME_X_SOURCE_FORMULA_INTERMEDIATE_LOCALIZATION",
         "SOURCE NATIVE/FORMULA INCONCLUSIVE: original source or stage formula not exact. Raw archived.")


if __name__=="__main__":
    main()
