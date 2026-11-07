#!/usr/bin/env python3
"""Independent original first Ridders x0 objective-term source comparison.

Validates every full MATLAB source-algebra reconstruction and frozen HGFX
objective against the exact 71 *original genuine private* source scalars,
requiring original SHA/subject/data/63/64 status and preserving all raw terms.
No threshold, no fit parity PASS, no GPU or timing.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import struct
from typing import Any

from decompose_original_x0_hgfx_objective import SCHEMA, b64
from replay_initial_ridders_stencil_archive import MEMBERS, RUN, SOURCE_SHA, scientific_original
from subject7_first_ridders_stencil import START, HGFX, MATLAB, xbits, xhex

MAT_SCHEMA="perf01d-matlab-objective-terms-71-v1"
FIELDS=("full_trial_log_likelihood","regular_trial_mask","log_likelihood",
        "negative_log_likelihood","perceptual_prior_terms",
        "perceptual_prior_log_total","observation_prior_terms",
        "observation_prior_log_total","negative_log_joint")
SEQUENCE=("full_trial_log_likelihood","log_likelihood",
          "perceptual_prior_terms","perceptual_prior_log_total",
          "observation_prior_terms","observation_prior_log_total",
          "negative_log_joint")


def need(ok,why):
    if not ok:raise ValueError(why)


def equal_float(a,b):
    return b64(a)==b64(b)


def compare_fields(h,m):
    need(set(h)==set(m)==set(FIELDS),"Original source objective constituent fields incomplete")
    diff={}
    for k in FIELDS:
        a,b=h[k],m[k]
        if k=="regular_trial_mask":
            need(type(a) is list and type(b) is list and
                 len(a)==len(b)==128 and all(type(q) is bool for q in a+b),
                 "Original regular trial mask invalid")
            eq=a==b
            need(eq,"Original model regular trial masks changed")
            continue
        if k in ("full_trial_log_likelihood","perceptual_prior_terms","observation_prior_terms"):
            need(type(a) is list and type(b) is list and len(a)==len(b)
                 and (len(a)==128 if k=="full_trial_log_likelihood" else True),
                 "Original model source constituent vector length changed: "+k)
            differ=[i for i,(x,y) in enumerate(zip(a,b)) if not equal_float(x,y)]
            diff[k]=differ
        else:
            diff[k]=([] if equal_float(a,b) else [0])
    return diff


def verify_sources(h,m,old_h,old_m,fit,sha_sidecar):
    scientific_original(fit)
    need(h["schema"]==SCHEMA
         and h["status"]=="AUTHOR_SIDE_FROZEN_HGFX_71_SOURCE_TERM_DECOMPOSITION"
         and h["frozen_hgfx_sha"]==HGFX and h["frozen_matlab_sha"]==MATLAB
         and h["original_real_source_run"]==RUN and h["original_real_source_sha"]==SOURCE_SHA
         and h["original_hgfx_source_member_sha256"]==MEMBERS["hgfx-first-ridders.json"]
         and h["original_matlab_source_member_sha256"]==MEMBERS["matlab-first-private-ridders.json"]
         and h["original_scientific_fit"]=="63/64 SCIENTIFIC NONPASS"
         and h["original_failed_fields"]=={"traj.mu":4,"traj.muhat":4}
         and h["original_71_source_node_count"]==71
         and h["independent_scientific_review"]=="NOT_RECEIVED"
         and h["perf01c"]=="NOT_FROZEN",
         "Original real HGFX source decomposition or scientific 63/64 provenance invalid")
    need(m["schema"]==MAT_SCHEMA
         and m["status"]=="AUTHOR_SIDE_REAL_FROZEN_MATLAB_MODEL_SOURCE_CONSTITUENTS"
         and m["original_hgfx_component_sha256"]==sha_sidecar
         and m["source_original_real_run"]==RUN
         and m["source_original_real_sha"]==SOURCE_SHA
         and m["frozen_hgfx_sha"]==HGFX and m["frozen_matlab_sha"]==MATLAB
         and m["subject_index_zero_based"]==7 and m["n_trials"]==128
         and m["original_scientific_fit"]=="63/64 SCIENTIFIC NONPASS"
         and m["original_failure"]=={"traj_mu":4,"traj_muhat":4}
         and m["original_native_optimization"]=="UNMODIFIED_FROZEN_FITMODEL"
         and m["original_71_source_node_count"]==71
         and m["independent_review"]=="NOT_RECEIVED" and m["perf01c"]=="NOT_FROZEN",
         "Genuine MATLAB source-term reconstruction or original failure altered")
    need(h["environment"]["run_id"]==m["github_run_id"]
         and h["environment"]["tested_sha"]==m["tested_sha"]
         and h["environment"]["run_id"]==os.getenv("GITHUB_RUN_ID")
         and m["tested_sha"]==os.getenv("GITHUB_SHA"),
         "Original frozen MATLAB and HGFX term outputs are NOT from same runner and commit")
    need(m["native_perceptual_function"]=="hgf_binary"
         and m["native_observation_function"]=="unitsq_sgm"
         and m["perceptual_source_file"].replace("\\","/").endswith("/_original_models/hgf_binary.m")
         and m["observation_source_file"].replace("\\","/").endswith("/unitsq_sgm.m")
         and m["negative_log_joint_source_file"].replace("\\","/").endswith("/core/fitModel.m"),
         "MATLAB native source function family/lineage not original frozen hgf_binary/unitsq_sgm")
    hh=h["nodes"];mm=m["nodes"]
    need(type(hh) is list and type(mm) is list and len(hh)==len(mm)==71
         and len(old_h["hgfx_nodes"])==len(old_m["matlab_nodes"])==71,
         "Original complete 71 source-node arrays missing")
    return hh,mm


def audit(h,m,original_h,original_m,fit,source_h_bytes):
    hh,mm=verify_sources(h,m,original_h,original_m,fit,sha256(source_h_bytes).hexdigest())
    rows=[];tallies=Counter()
    for i,(ha,ma,oh,om) in enumerate(zip(hh,mm,original_h["hgfx_nodes"],
                                       original_m["matlab_nodes"])):
        v=ha["x"]
        need(ha["original_node_index"]==ma["original_node_index"]==oh["ordinal"]==om["ordinal"]==i
             and xbits(v)==xbits(ma["x"])==xbits(oh["x"])==xbits(om["x"])
             and xhex(v)==ha["x_hex"]==ma["x_hex"],
             "Source MATLAB/HGFX original 71 Ridders x order or binary64 x changed")
        hcomp=ha["components"];mcomp=ma["components"]
        need(equal_float(ha["original_hgfx_source_scalar"],oh["value"])
             and equal_float(ma["original_matlab_private_source_scalar"],om["value"])
             and equal_float(hcomp["negative_log_joint"],oh["value"])
             and equal_float(mcomp["negative_log_joint"],om["value"])
             and equal_float(ha["original_matlab_private_source_scalar"],om["value"])
             and equal_float(ma["original_hgfx_source_scalar"],oh["value"]),
             "Actual genuine private MATLAB or HGFX first source scalar NOT exactly reproduced at "+str(i))
        difference=compare_fields(hcomp,mcomp)
        fields={k:len(v) for k,v in difference.items()}
        categories=[k for k,z in fields.items() if z]
        for k in categories:tallies[k]+=1
        rows.append({
            "original_node_index":i,
            "actual_hgfx_original_source_scalar":oh["value"],
            "actual_matlab_original_private_scalar":om["value"],
            "negative_joint_bits_differ":fields["negative_log_joint"]>0,
            "first_differing_component_in_declared_reporting_order":
                next((k for k in SEQUENCE if fields[k]>0),None),
            "original_128_trial_mismatch_indices":difference["full_trial_log_likelihood"],
            "perceptual_prior_term_mismatch_indices":difference["perceptual_prior_terms"],
            "observation_prior_term_mismatch_indices":difference["observation_prior_terms"],
            "component_mismatch_counts":fields,
            "all_changed_component_names":categories,
            "actual_71_original_source_x":v,
            "source_component_values":{k:{"hgfx":hcomp[k],"matlab":mcomp[k]} for k in FIELDS
                                       if k!="full_trial_log_likelihood" and k!="regular_trial_mask"},
        })
    needs=[z for z in rows if z["negative_joint_bits_differ"]]
    need(len(needs)==14 and sum(not z["negative_joint_bits_differ"] for z in rows)==57,
         "Original 14/71 same-x scalar difference inventory changed")
    aggregate={}
    for name in FIELDS:
        if name=="regular_trial_mask":continue
        flagged=[z["original_node_index"] for z in rows if z["component_mismatch_counts"][name]>0]
        aggregate[name]={
            "nodes_with_bit_difference":len(flagged),
            "all_original_indices":flagged,
            "bitwise_same_nodes":71-len(flagged),
        }
    return {
        "schema":"perf01d-initial-source-objective-terms-71-bitwise-audit-v1",
        "status":"AUTHOR_SIDE_REAL_71_NODE_SOURCE_COMPONENTS_NOT_SCIENTIFIC_PASS",
        "source_real_run":RUN,
        "source_real_sha":SOURCE_SHA,
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "original_scientific_fit":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_traj_mu":4,"original_subject7_failed_traj_muhat":4,
        "all_71_original_joint_source_values_reconstructed_exact_each_engine":True,
        "first_gradient_same_x_joint_unequal_count":len(needs),
        "full_original_71_node_component_counts":aggregate,
        "full_original_71_node_component_diagnostics":rows,
        "all_14_original_joint_mismatch_indices":[z["original_node_index"] for z in needs],
        "per_node_first_difference_is_constituent_not_machine_instruction":True,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","performance_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for k in ("hgfx","matlab","original-archive","original-fit","output"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    hbytes=a.hgfx.read_bytes()
    h=json.loads(hbytes);m=json.loads(a.matlab.read_bytes())
    originals={}
    for name in ("hgfx-first-ridders.json","matlab-first-private-ridders.json"):
        bb=(a.original_archive/name).read_bytes()
        need(sha256(bb).hexdigest()==MEMBERS[name],"Original genuine first-gradient source byte SHA changed")
        originals[name]=json.loads(bb)
    result=audit(h,m,originals["hgfx-first-ridders.json"],
                 originals["matlab-first-private-ridders.json"],
                 json.loads(a.original_fit.read_bytes()),hbytes)
    result["new_hgfx_decomposition_sha256"]=sha256(hbytes).hexdigest()
    result["new_matlab_decomposition_sha256"]=sha256(a.matlab.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":result["status"],
                      "original_71_final_objective_exact_per_engine":True,
                      "original_mismatched_joint_nodes":len(result["all_14_original_joint_mismatch_indices"]),
                      "component_counts":result["full_original_71_node_component_counts"],
                      "science":"63/64 NONPASS"},sort_keys=True))


if __name__=="__main__":main()
