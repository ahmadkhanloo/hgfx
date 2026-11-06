#!/usr/bin/env python3
"""PERF-01D: subject-7 fitted omega2 path divergence in original 25 records.

No fitting, no timers, no newly selected subjects. All original raw SHA-256
and successful prior BFGS source-branch provenance are verified; independent
scientific fitting 63/64 NON-PASS is retained. Last two saved transitions
are excluded from claims of actual accepted optimizer steps.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import numpy as np

from derive_subject7_direction_decomposition import (
    verify_original_bfgs_archive,history,scaled_direction,BFGS_RUN
)
from compare_fits import TOLS

EXPECTED="AUTHOR_SIDE_ORIGINAL_OMEGA2_25_HISTORY_NOT_CAUSAL_OR_SCIENTIFIC_PASS"


def first(predicate)->int|None:
    return next((i for i,x in enumerate(predicate) if x),None)


def pointwise_drift(h,m,rtol,atol)->list[dict]:
    if h.shape!=m.shape or h.ndim!=2 or h.shape[1]!=3:
        raise ValueError("Expected matching transformed free-coordinate histories Nx3")
    if not np.all(np.isfinite(h)) or not np.all(np.isfinite(m)):
        raise ValueError("Original archived transformed free-parameter history nonfinite")
    rows=[]
    for i,(a,b) in enumerate(zip(h,m)):
        delta=a-b
        old_final_lens=atol+rtol*np.abs(b)
        rows.append({
            "record_index_zero_based":i,
            "hgfx_free_parameter_omega2":float(a[0]),
            "matlab_free_parameter_omega2":float(b[0]),
            "omega2_signed_diff":float(delta[0]),
            "omega2_abs_diff":float(abs(delta[0])),
            "omega3_signed_diff":float(delta[1]),
            "obs_logze_signed_diff":float(delta[2]),
            "max_abs_any_free_coord":float(np.max(np.abs(delta))),
            "inherited_FINAL_parameter_tolerance_descriptive_only":[float(x) for x in old_final_lens],
            "omega2_outside_final_tolerance_descriptive_not_optimizer_iter_gate":
                bool(abs(delta[0])>old_final_lens[0]),
            "any_free_outside_final_tolerance_descriptive_not_optimizer_iter_gate":
                bool(np.any(np.abs(delta)>old_final_lens)),
        })
    return rows


def derive(root:Path,old_derived:Path)->dict:
    manifest,previous=verify_original_bfgs_archive(root,old_derived)
    raw={a:json.loads((root/f"{a}_raw.json").read_bytes())
         for a in ("hgfx","matlab")}
    th,xh,gh=history(raw["hgfx"],"hgfx")
    tm,xm,gm=history(raw["matlab"],"matlab")
    if (raw["hgfx"]["source_input_sha256"]!=raw["matlab"]["source_input_sha256"]
        or raw["hgfx"]["source_config_sha256"]!=raw["matlab"]["source_config_sha256"]
        or manifest["source_run_id"]!="41863441006"):
        raise ValueError("Original full source input/config/fit cohort mismatch")
    if not np.array_equal(xh[0],xm[0]):
        raise ValueError("Original public fit starts were not identical")
    if not np.array_equal(xh[23],xh[24]) or not np.array_equal(xm[23],xm[24]):
        raise ValueError("Original two terminal overwritten history slots changed")
    if TOLS["final"]!=(3e-8,3e-10):
        raise ValueError("Original final tolerance altered")
    rt,at=TOLS["final"]
    observations=pointwise_drift(xh[:25],xm[:25],rt,at)
    records=[]
    for i in range(24):
        row={"record_index_zero_based":i,
             "status":("SOURCE_NONTERMINAL_STORED_TRANSITION"
                       if i<22 else "TERMINAL_OVERWRITE_UNSAFE_AS_ACCEPTANCE_EVIDENCE")}
        if i<22:
            dh,step_h=scaled_direction(th[i],gh[i])
            dm,step_m=scaled_direction(tm[i],gm[i])
            old_diff=xh[i]-xm[i]
            observed_next_diff=xh[i+1]-xm[i+1]
            projected_step_diff=step_h-step_m
            reconstructed=old_diff+projected_step_diff
            residual=observed_next_diff-reconstructed
            if float(np.max(np.abs(residual)))>2e-12:
                raise ValueError(f"Previously accepted source-step arithmetic not reproduced at {i}")
            row.update({
                "previous_omega2_signed_diff":float(old_diff[0]),
                "hgfx_clipped_step_omega2":float(step_h[0]),
                "matlab_clipped_step_omega2":float(step_m[0]),
                "clipped_step_omega2_signed_diff":float(projected_step_diff[0]),
                "observed_next_omega2_signed_diff":float(observed_next_diff[0]),
                "omega2_signed_decomposition_residual":float(residual[0]),
                "hgfx_raw_direction_was_clipped":bool(np.linalg.norm(dh)>1),
                "matlab_raw_direction_was_clipped":bool(np.linalg.norm(dm)>1),
                "neither_step_measured_as_instrumented_line_search_event":True,
            })
        records.append(row)
    initial=observations[0]
    first_nonzero=first(row["omega2_abs_diff"]>0 for row in observations)
    first_outside=first(
        row["omega2_outside_final_tolerance_descriptive_not_optimizer_iter_gate"]
        for row in observations
    )
    endpoint_h=np.asarray(raw["hgfx"]["final_full"],float)[12:15]
    endpoint_m=np.asarray(raw["matlab"]["final_full"],float)[12:15]
    if endpoint_h.shape!=(3,) or endpoint_m.shape!=(3,) or not np.all(np.isfinite(endpoint_h)):
        raise ValueError("Original frozen public full fitted endpoint malformed")
    if not np.all(np.isfinite(endpoint_m)):
        raise ValueError("MATLAB frozen full fitted endpoint malformed")
    return {
        "schema":"perf01d-subject7-original-omega2-optimizer-history-v1",
        "status":EXPECTED,
        "original_bfgs_run":BFGS_RUN,
        "original_bfgs_tested_sha":manifest["candidate_sha"],
        "original_bfgs_raw_sha256":manifest["raw_evidence_sha256"],
        "original_source_branch_report_run":previous["derived_from_github_run"],
        "original_scientific_result":"63/64 FULL PUBLIC FITS NONPASS; subject 7 mu/muhat",
        "subject_index_zero_based":7,
        "n_trials":128,
        "model":"hgf_binary",
        "frozen_hgfx_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "frozen_matlab_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "free_parameter_names":["om[1] omega2","om[2] omega3","logze observation"],
        "source_history_allocated_slots":101,
        "source_history_populated_slots":25,
        "safe_nonterminal_transition_indices":list(range(22)),
        "excluded_terminal_transition_indices":[22,23],
        "inherited_final_fit_tolerance_descriptive_only":{"rtol":rt,"atol":at},
        "first_exact_binary64_omega2_record_difference":first_nonzero,
        "first_omega2_difference_beyond_inherited_FINAL_fit_tolerance_DESCRIPTIVE_ONLY":first_outside,
        "max_recorded_omega2_difference":max(x["omega2_abs_diff"] for x in observations),
        "last_populated_omega2_signed_diff":observations[24]["omega2_signed_diff"],
        "original_final_omega2_signed_diff":float(endpoint_h[0]-endpoint_m[0]),
        "original_final_omega3_signed_diff":float(endpoint_h[1]-endpoint_m[1]),
        "original_final_logze_signed_diff":float(endpoint_h[2]-endpoint_m[2]),
        "original_final_endpoint_from_saved_slot_23_max_abs_error":{
            "hgfx":float(np.max(np.abs(xh[23]-endpoint_h))),
            "matlab":float(np.max(np.abs(xm[23]-endpoint_m))),
        },
        "all_25_original_populated_history_records":observations,
        "source_derived_step_omega2_22_nonterminal_and_two_excluded_terminal_records":records,
        "limitations":[
            "This is original archived data with post-fit re-evaluated source gradients, not instrumented source optimizer event trace.",
            "The original MATLAB public optimizer overwrites two terminal iteration records; do not interpret slots 22 or 23 as accepted transitions.",
            "Applying existing FINAL fitted parameter tolerance to intermediate optimizer states is explicitly DESCRIPTIVE ONLY, not a new scientific acceptance gate.",
            "First floating-point difference is not a demonstrated unique cause; BLAS dispatch and BFGS amplification may affect path.",
            "Original source + oracle frozen, input/config/parameter count/seeds/grids unchanged; 63/64 full fit NON-PASS.",
            "No fitted trajectory parity PASS, optimizer defect or reference-only scientific limitation classification, timing/GPU/speedup or reviewer verdict.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--branch",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    j=derive(a.source,a.branch)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":j["status"],
        "first_binary64_omega2_nonzero":j["first_exact_binary64_omega2_record_difference"],
        "first_descriptive_final_tolerance_omega2_exceedance":
            j["first_omega2_difference_beyond_inherited_FINAL_fit_tolerance_DESCRIPTIVE_ONLY"],
        "last_omega2_signed_diff":j["last_populated_omega2_signed_diff"],
        "original_final_omega2_signed_diff":j["original_final_omega2_signed_diff"],
        "max_omega2_slot_delta":j["max_recorded_omega2_difference"],
        "nonterminal_steps":len(j["safe_nonterminal_transition_indices"]),
        "original_scientific_result":"63/64 NONPASS",
    },sort_keys=True))


if __name__=="__main__":
    main()
