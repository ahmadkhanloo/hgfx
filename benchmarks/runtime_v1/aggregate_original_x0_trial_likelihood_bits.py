#!/usr/bin/env python3
"""Archive-only 71-by-128 exact original trial LL difference frequency.

Derived from true source MATLAB + HGFX constituent archive, with source-member
SHA locked and 71/71 original private objective exact reproduction required.
No new threshold, fitting, MATLAB call, GPU or timing.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

from compare_original_x0_objective_terms import audit as full_objective_audit, equal_float
from replay_initial_ridders_stencil_archive import MEMBERS, scientific_original, ulps

SOURCE_RUN="42402421462"
SOURCE_SHA="3ae1ac5330bd1b6bc1ea8017f16f0f66be6b3b57"
SHA={
    "original-hgfx-71-objective-terms.json":"eb085a07e633aa10979602d9f9fb5e9221e2a1132aecd9fb7b73953a4d2850df",
    "original-matlab-71-objective-terms.json":"4d9cd77d1187f203a0b467b602d6ab74b4283f2c76476c97d5c8b9e3dc95d0ea",
    "independent-71-node-likelihood-and-prior-source-audit.json":"4bfedca4318343bfa3422a5f85e150b039771e53a7a2823995309feac15e0d25",
}


def need(value,why):
    if not value:raise ValueError(why)


def aggregate_trial_ll(h,m,verified):
    hc,mc=h["nodes"],m["nodes"]
    need(len(hc)==len(mc)==71
         and verified["schema"]=="perf01d-initial-source-objective-terms-71-bitwise-audit-v1"
         and verified["original_scientific_fit"]=="63/64 SCIENTIFIC NONPASS"
         and verified["original_subject7_failed_traj_mu"]==4
         and verified["original_subject7_failed_traj_muhat"]==4
         and verified["all_71_original_joint_source_values_reconstructed_exact_each_engine"] is True
         and verified["first_gradient_same_x_joint_unequal_count"]==14
         and verified["independent_scientific_review"]=="NOT_RECEIVED"
         and verified["perf01c"]=="NOT_FROZEN"
         and verified["full_original_71_node_component_counts"]["full_trial_log_likelihood"]["nodes_with_bit_difference"]==71
         and verified["full_original_71_node_component_counts"]["perceptual_prior_terms"]["nodes_with_bit_difference"]==0
         and verified["full_original_71_node_component_counts"]["observation_prior_terms"]["nodes_with_bit_difference"]==0
         and verified["full_original_71_node_component_counts"]["perceptual_prior_log_total"]["nodes_with_bit_difference"]==0
         and verified["full_original_71_node_component_counts"]["observation_prior_log_total"]["nodes_with_bit_difference"]==0,
         "Original genuine 71 source constituent audit/scientific provenance changed")
    freq=[0]*128;max_abs=[0.]*128;max_ulp=[0]*128
    all_indices=[[] for i in range(128)]
    node_rows=[]
    mismatched_joint=[]
    for i,(a,b) in enumerate(zip(hc,mc)):
        need(a["original_node_index"]==b["original_node_index"]==i
             and a["x_hex"]==b["x_hex"],
             "Original 71 genuine source Ridders positions reordered")
        ac,bc=a["components"],b["components"]
        aa,bb=ac["full_trial_log_likelihood"],bc["full_trial_log_likelihood"]
        need(type(aa) is list and type(bb) is list
             and len(aa)==len(bb)==128
             and ac["regular_trial_mask"]==bc["regular_trial_mask"]
             and len(ac["regular_trial_mask"])==128,
             "Missing or inconsistent original 128 per-trial source scalar/mask inventory")
        different=[]
        for j,(v,w) in enumerate(zip(aa,bb)):
            need(type(v) in (float,int) and type(w) in (float,int)
                 and math.isfinite(v) and math.isfinite(w),
                 "Original HGFX or MATLAB trial likelihood nonfinite")
            if not equal_float(v,w):
                freq[j]+=1
                all_indices[j].append(i)
                different.append(j)
                max_abs[j]=max(max_abs[j],abs(v-w))
                max_ulp[j]=max(max_ulp[j],ulps(v,w))
        same_joint=equal_float(ac["negative_log_joint"],bc["negative_log_joint"])
        if not same_joint:mismatched_joint.append(i)
        need(bool(different),"Original all-71 per-trial mismatch inventory unexpectedly decreased")
        node_rows.append({
            "original_source_node_index":i,
            "number_nonidentical_trial_ll_scalars":len(different),
            "first_nonidentical_trial_zero_based":different[0],
            "all_nonidentical_original_trial_indices":different,
            "final_original_joint_bits_differ":not same_joint,
            "original_hgfx_log_likelihood":ac["log_likelihood"],
            "original_matlab_log_likelihood":bc["log_likelihood"],
        })
    need(mismatched_joint==verified["all_14_original_joint_mismatch_indices"],
         "Original 14 genuine private objective discrepant nodes changed")
    columns=[]
    for j in range(128):
        columns.append({
            "original_trial_zero_based":j,
            "source_node_mismatch_count":freq[j],
            "original_71_source_mismatch_nodes":all_indices[j],
            "maximum_binary64_trial_ll_absolute_difference":max_abs[j],
            "maximum_binary64_trial_ll_ulp_distance":max_ulp[j],
        })
    hot=sorted(columns,key=lambda x:(-x["source_node_mismatch_count"],x["original_trial_zero_based"]))
    return {
        "schema":"perf01d-71x128-genuine-trial-likelihood-source-inventory-v1",
        "status":"AUTHOR_SIDE_ARCHIVE_ONLY_PER_TRIAL_LIKELIHOOD_LOCALIZATION_NOT_SCIENTIFIC_PASS",
        "original_genuine_source_run":SOURCE_RUN,
        "original_genuine_source_sha":SOURCE_SHA,
        "original_scientific_fit":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failed_mu":4,"original_subject7_failed_muhat":4,
        "original_71_trial_ll_vector_mismatch_nodes":71,
        "original_14_final_joint_mismatch_nodes":mismatched_joint,
        "different_trial_positions_across_all_71_nodes":sum(1 for n in freq if n>0),
        "identical_trial_positions_across_all_71_nodes":sum(1 for n in freq if n==0),
        "maximum_trial_positions_differing_at_any_node":max(r["number_nonidentical_trial_ll_scalars"] for r in node_rows),
        "minimum_trial_positions_differing_at_any_node":min(r["number_nonidentical_trial_ll_scalars"] for r in node_rows),
        "full_71_source_node_mismatch_rows":node_rows,
        "full_128_trial_position_mismatch_rows":columns,
        "top_10_most_frequently_differing_original_trial_positions":hot[:10],
        "all_71_original_free_perceptual_and_observation_prior_terms_equal":True,
        "source_math_first_difference_before_or_at_trial_observation_log_likelihood":True,
        "perceptual_forward_versus_observation_source_unresolved":True,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "paper_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }


def main():
    p=argparse.ArgumentParser()
    for k in ("real-source","original-x0","original-fit","output"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    files={}
    for name,expected in SHA.items():
        data=(a.real_source/name).read_bytes()
        need(sha256(data).hexdigest()==expected,
             "Genuine original 71-source terms SHA256 changed: "+name)
        files[name]=json.loads(data)
    orig={}
    for name in ("hgfx-first-ridders.json","matlab-first-private-ridders.json"):
        data=(a.original_x0/name).read_bytes()
        need(sha256(data).hexdigest()==MEMBERS[name],
             "Original frozen real 71-node objective source SHA256 changed")
        orig[name]=json.loads(data)
    fit=json.loads(a.original_fit.read_bytes())
    scientific_original(fit)
    h=files["original-hgfx-71-objective-terms.json"]
    m=files["original-matlab-71-objective-terms.json"]
    checked=full_objective_audit(
        h,m,orig["hgfx-first-ridders.json"],orig["matlab-first-private-ridders.json"],
        fit,(a.real_source/"original-hgfx-71-objective-terms.json").read_bytes(),
        source_run_id=SOURCE_RUN,source_tested_sha=SOURCE_SHA)
    verified=files["independent-71-node-likelihood-and-prior-source-audit.json"]
    need(checked["full_original_71_node_component_counts"]==
         verified["full_original_71_node_component_counts"]
         and checked["all_14_original_joint_mismatch_indices"]==
         verified["all_14_original_joint_mismatch_indices"],
         "Previously independent original 71 source term classification changed")
    result=aggregate_trial_ll(h,m,checked)
    result["original_unmodified_raw_source_member_sha256"]=SHA
    result["first_true_ridders_source_sha256"]={
        n:MEMBERS[n] for n in ("hgfx-first-ridders.json","matlab-first-private-ridders.json")}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":result["status"],"original_science":result["original_scientific_fit"],
        "different_trial_positions_across_71":result["different_trial_positions_across_all_71_nodes"],
        "min_trial_positions_per_node":result["minimum_trial_positions_differing_at_any_node"],
        "max_trial_positions_per_node":result["maximum_trial_positions_differing_at_any_node"],
        "top_10_trial_positions":result["top_10_most_frequently_differing_original_trial_positions"],
        "full_original_joint_mismatch_nodes":result["original_14_final_joint_mismatch_nodes"],
    },sort_keys=True))


if __name__=="__main__":main()
