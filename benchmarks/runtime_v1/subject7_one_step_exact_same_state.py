#!/usr/bin/env python3
"""PERF-01D author-side one-step *algebraic* BFGS sensitivity at observed x6.

Post-result exploratory: a preliminary local calculation already examined this
one step. Therefore this is NOT a prospectively preregistered scientific gate
or an original public fit. Preserve original 63/64 NONPASS without reinterpretation.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from importlib import metadata
import json
import math
from pathlib import Path
import platform

import numpy as np
from subject7_direct_nested_gradient_bfgs import original_inventory,HASHES,HGFX,REF


PAIR_HASH="2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d"
ANCHOR_HASH="d92690111b2fa128c045f29b39aa95110b5e5cd838f90c48a733400a3e537913"
MATLAB_RAW_HASH="90de6c75c13736fae95bc0645950ac0352546fd7262c4d5f70d97f8b9b14e978"
INDEX=6


def require(c,msg):
    if not c:raise ValueError(msg)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def original_direction(x,t,gradient,objective):
    """Frozen quasinewton_optim.m: raw direction, unclipped slope, maxStep=1."""
    x=np.asarray(x,np.float64).reshape(-1)
    t=np.asarray(t,np.float64)
    gradient=np.asarray(gradient,np.float64).reshape(-1)
    require(x.shape==(3,) and t.shape==(3,3) and gradient.shape==(3,)
            and np.isfinite(x).all() and np.isfinite(t).all()
            and np.isfinite(gradient).all() and math.isfinite(float(objective)),
            "Incomplete original source x/T/gradient/objective")
    raw=-(t@gradient)
    raw_norm=float(np.sqrt(raw@raw))
    require(math.isfinite(raw_norm) and raw_norm>0,"Source direction norm invalid")
    clipped=raw if raw_norm<=1. else raw/raw_norm
    xnext=x+clipped
    lhs=float("nan")
    slope=float(gradient@raw)
    rhs=float(1e-4*slope)
    return {
        "original_source_step_norm":raw_norm,
        "original_source_clipping_applied":bool(raw_norm>1.),
        "original_source_unclipped_gradient_dot_direction":slope,
        "original_armijo_delta_RHS_using_unclipped_slope":rhs,
        "source_unclipped_direction":raw.tolist(),
        "source_clipped_full_step_direction":clipped.tolist(),
        "source_next_full_step_free_x":xnext.tolist(),
        "source_current_value":float(objective),
    }


def analyze(root,archive_bfgs,archive50):
    from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
    require(metadata.version("hgfx")=="1.0.0","Frozen source version changed")
    raw,_=original_inventory(root,archive_bfgs)
    for name,expected in (
        ("paired-direct-private-gradient-bfgs-margins.json",PAIR_HASH),
        ("locked-50-bfgs-anchors.json",ANCHOR_HASH),
        ("real-private-matlab-ridders.json",MATLAB_RAW_HASH),
    ):
        require(digest(archive50/name)==expected,"Original direct-private source SHA tamper: "+name)
    paired=json.loads((archive50/"paired-direct-private-gradient-bfgs-margins.json").read_bytes())
    require(paired["status"]=="AUTHOR_SIDE_50_DIRECT_PRIVATE_RIDDERS_DIAGNOSTIC_REVIEW_PENDING"
            and paired["source_original_64_full_fit"]=="63/64 SCIENTIFIC NONPASS"
            and paired["source_original_zero_based_subject_7_failure"]=={"traj.mu":4,"traj.muhat":4}
            and paired["frozen_matlab_sha"]==REF and paired["frozen_hgfx_sha"]==HGFX
            and paired["full_original_50_anchor_occurrences"]==50
            and paired["instrumentation_neutral"] is True
            and paired["independent_scientific_review"]=="NOT_RECEIVED"
            and paired["perf01c"]=="NOT_FROZEN",
            "Prior original failed-fit and actual private gradient source changed")
    row=paired["all_50_original_same_x_paired_gradient_records"][INDEX]
    h=raw["hgfx"];m=raw["matlab"]
    x=np.asarray(h["iter_x"][INDEX],float)
    x_m=np.asarray(m["iter_x"][INDEX],float)
    T=np.asarray(h["iter_inverse_hessian"][INDEX],float)
    require(row["anchor_origin"]=="hgfx"
            and row["record_index_zero_based"]==INDEX
            and np.array_equal(np.asarray(row["free_parameters"],float),x)
            and row["matlab_status"]=="EVALUATED"
            and row["same_x_abs_objective_difference"]==0.
            and row["same_x_max_abs_gradient_component_difference"]==6.884955006114524e-08,
            "Observed source record 6 was altered or not the selected counterexample")
    g_h=np.asarray(row["hgfx"]["gradient"],float)
    g_m=np.asarray(row["matlab"]["gradient"],float)
    original_val=float(h["iter_val"][INDEX])
    require(original_val==float(row["hgfx"]["objective"])
            and original_val==float(row["matlab"]["objective"]),
            "Original HGFX same-x objective did not equal source direct-private MATLAB")
    directions={
        "hgfx_original_source_gradient":original_direction(x,T,g_h,original_val),
        "real_matlab_private_gradient_at_exact_hgfx_source_x":original_direction(x,T,g_m,original_val),
    }
    saved_x7_h=np.asarray(h["iter_x"][INDEX+1],float)
    saved_x7_m=np.asarray(m["iter_x"][INDEX+1],float)
    q0=np.asarray(directions["hgfx_original_source_gradient"]["source_next_full_step_free_x"],float)
    q1=np.asarray(directions["real_matlab_private_gradient_at_exact_hgfx_source_x"]["source_next_full_step_free_x"],float)
    data=json.loads((root/"inputs"/"binary_128_s64.json").read_bytes())
    problem=hgf_binary_unitsq_fit_problem(
        np.asarray(data["y"][7],float),np.asarray(data["u"][7],float))
    require(problem.free_indices==(12,13,14)
            and np.array_equal(problem.initial_free,[-3.,-6.,3.871201010907891]),
            "Frozen subject7 source start changed")
    for key in directions:
        D=directions[key]
        val=float(problem.evaluate_free(D["source_next_full_step_free_x"]))
        require(math.isfinite(val),"Source next candidate objective nonfinite; archive entire failure")
        D["new_evaluated_hgfx_objective_at_candidate"]=val
        D["armijo_source_delta_LHS_new_minus_original"]=val-original_val
        D["armijo_original_source_inequality_full_step"]=bool(
            val-original_val < D["original_armijo_delta_RHS_using_unclipped_slope"])
        D["max_abs_candidate_next_x_minus_original_hgfx_saved_x7"]=float(
            np.max(np.abs(np.asarray(D["source_next_full_step_free_x"])-saved_x7_h)))
        D["max_abs_candidate_next_x_minus_original_matlab_saved_x7"]=float(
            np.max(np.abs(np.asarray(D["source_next_full_step_free_x"])-saved_x7_m)))
    return {
        "schema":"perf01d-postresult-source-one-step-original-record6-v1",
        "status":"AUTHOR_SIDE_SOURCE_ALGEBRA_ONE_STEP_NOT_ORIGINAL_FIT_OR_CAUSAL_PROOF",
        "post_result_selection":True,
        "selection_already_preliminarily_calculated_before_script_commit":True,
        "source_original_bfgs_run":"42187240378",
        "source_original_bfgs_raw_sha256":HASHES,
        "source_50_actual_private_probe_run":"42305573614",
        "source_50_raw_sha256":{
            "paired-direct-private-gradient-bfgs-margins.json":PAIR_HASH,
            "locked-50-bfgs-anchors.json":ANCHOR_HASH,
            "real-private-matlab-ridders.json":MATLAB_RAW_HASH,
        },
        "source_original_frozen_hgfx":HGFX,
        "source_original_frozen_matlab":REF,
        "subject_index_zero_based":7,
        "original_trial_count":128,
        "original_history_record_zero_based":INDEX,
        "one_identical_x":x.tolist(),
        "original_matlab_own_x6_different_x":x_m.tolist(),
        "original_hgfx_source_T6":T.tolist(),
        "original_hgfx_gradient_at_x":g_h.tolist(),
        "real_matlab_private_gradient_at_same_x":g_m.tolist(),
        "source_gradient_difference_matlab_minus_hgfx":(g_m-g_h).tolist(),
        "source_original_saved_hgfx_x7":saved_x7_h.tolist(),
        "source_original_saved_matlab_x7":saved_x7_m.tolist(),
        "source_original_record6_value":original_val,
        "same_T6_and_x6_one_step_directions":directions,
        "max_abs_change_in_single_step_candidate_from_gradient_substitution":float(
            np.max(np.abs(q1-q0))),
        "max_abs_original_hgfx_matlab_next_x7_difference":float(
            np.max(np.abs(saved_x7_m-saved_x7_h))),
        "same_source_hgfx_objective_used_for_two_counterfactual_one_step_candidates":True,
        "one_step_is_NOT_an_unmodified_original_MATLAB_optimizer_branch_log":True,
        "one_step_is_NOT_a_completed_fitting_result":True,
        "source_original_64_public_fit_science":"63/64 SCIENTIFIC NONPASS",
        "source_original_zero_based_subject7_4_plus_4_mismatches":{"traj.mu":4,"traj.muhat":4},
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "timing":"NOT_RUN",
        "host":{
            "python":platform.python_version(),
            "machine":platform.machine(),
            "numpy":metadata.version("numpy"),
            "hgfx":metadata.version("hgfx"),
        },
        "limits":[
            "Original T6 came from the HGFX source history; MATLAB-own source T6/x6 are different, not tested here.",
            "This is a SINGLE full-step candidate algebraic sensitivity, not the entire subsequent optimizer trajectory.",
            "Archived different-x reference next steps must not be called original MATLAB same-state step oracle.",
            "The frozen actual private MATLAB objective at these new x7 candidates was NOT evaluated in this study.",
            "The observed original 63/64 fit NONPASS remains binding, no tolerance changes, timing, GPU or scientific PASS.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--private50",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=analyze(a.root,a.original,a.private50)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "diagnostic":report["status"],
        "source_original_fitting":report["source_original_64_public_fit_science"],
        "one_step_candidate_change":report["max_abs_change_in_single_step_candidate_from_gradient_substitution"],
        "original_next_state_difference":report["max_abs_original_hgfx_matlab_next_x7_difference"],
        "same_state_armijo_hgfx":report["same_T6_and_x6_one_step_directions"]["hgfx_original_source_gradient"]["armijo_original_source_inequality_full_step"],
        "same_state_armijo_matlab_gradient":report["same_T6_and_x6_one_step_directions"]["real_matlab_private_gradient_at_exact_hgfx_source_x"]["armijo_original_source_inequality_full_step"],
        "perf01c":report["perf01c"],
    },sort_keys=True))


if __name__=="__main__":
    main()
