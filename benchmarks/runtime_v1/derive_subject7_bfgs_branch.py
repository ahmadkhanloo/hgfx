#!/usr/bin/env python3
"""Recompute source-frozen PERF-01D BFGS curvature/Armijo evidence from raw CI.

Distinct derived record; does NOT modify/re-run the original fitting,
freeze the prospective benchmark, or promote the 63/64 scientific mismatch.
The last two stored transitions are excluded from acceptance conclusions
because frozen MATLAB rewrites history at termination.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

from compare_subject7_bfgs_state import compare

ORIGINAL_RUN = "42187240378"
ORIGINAL_SHA = "5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d"
EXPECTED = {
    "hgfx_raw.json": "060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce",
    "matlab_raw.json": "4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a",
}
SAFE_BFGS_SLOTS = tuple(range(1, 23))
SAFE_STEP_SLOTS = tuple(range(22))


def curvature_decisions(raw: dict) -> list[dict]:
    x = np.asarray(raw["iter_x"], dtype=np.float64)
    grads = np.asarray([row["grad"] for row in raw["ridders_recomputed_history"]], dtype=np.float64)
    matrices = np.asarray(raw["iter_inverse_hessian"], dtype=np.float64)
    if (x.shape != (101, 3) or grads.shape != (25, 3)
            or matrices.ndim != 3 or matrices.shape[1:] != (3, 3)
            or len(matrices) < 23):
        raise ValueError("Original BFGS history dimensions missing or changed")
    out=[]
    for i in SAFE_BFGS_SLOTS:
        dx=x[i]-x[i-1]
        dgrad=grads[i]-grads[i-1]
        if np.any(~np.isfinite(dx)) or np.any(~np.isfinite(dgrad)):
            raise ValueError("Unverified nonfinite source vector or Ridders gradient")
        lhs=float(dgrad @ dx)
        rhs=float(np.sqrt(np.finfo(np.float64).eps
            * float(dgrad @ dgrad) * float(dx @ dx)))
        source_branch=bool(lhs>rhs)
        stored_change=bool(np.any(matrices[i] != matrices[i-1]))
        out.append({
            "record_index_zero_based":i,
            "curvature_scalar_dgrad_dot_dx":lhs,
            "curvature_source_threshold":rhs,
            "source_condition_would_apply_update":source_branch,
            "observed_saved_matrix_changed":stored_change,
            "condition_vs_saved_matrix_change_agree":bool(source_branch==stored_change),
            "stored_matrix_change_max_abs":float(np.max(np.abs(matrices[i]-matrices[i-1]))),
        })
    return out


def derive(root: Path) -> dict:
    old=json.loads((root/"summary.json").read_bytes())
    if (str(old.get("github_run_id")) != ORIGINAL_RUN
            or old.get("candidate_sha") != ORIGINAL_SHA
            or old.get("raw_evidence_sha256") != EXPECTED
            or old.get("status") != "AUTHOR_SIDE_BFGS_STATE_RECONSTRUCTION_NOT_SCIENTIFIC_PASS_NOT_TIMED"
            or old.get("source_run_id") != "41863441006"):
        raise ValueError("Original BFGS CI evidence provenance changed")
    raw={}
    for name,expected in EXPECTED.items():
        content=(root/name).read_bytes()
        if hashlib.sha256(content).hexdigest()!=expected:
            raise ValueError(f"Original BFGS source artifact altered: {name}")
        raw[name.split("_")[0]]=json.loads(content)
    recomputed=compare(raw["hgfx"],raw["matlab"])
    original_body={k:v for k,v in old.items() if k not in {
        "github_run_id","candidate_sha","raw_evidence_sha256","raw_evidence_location"}}
    if recomputed!=original_body:
        raise ValueError("Recomputed BFGS comparison changed original scientific diagnostic")

    h=curvature_decisions(raw["hgfx"])
    m=curvature_decisions(raw["matlab"])
    hs={a["record_index_zero_based"]:a for a in h}
    ms={a["record_index_zero_based"]:a for a in m}
    branches=[
        {"record_index_zero_based":i,
         "hgfx":hs[i],
         "matlab":ms[i],
         "same_curvature_decision":bool(
             hs[i]["source_condition_would_apply_update"] ==
             ms[i]["source_condition_would_apply_update"]),
         "both_source_branches_match_saved_T_changes":bool(
             hs[i]["condition_vs_saved_matrix_change_agree"]
             and ms[i]["condition_vs_saved_matrix_change_agree"])}
        for i in SAFE_BFGS_SLOTS
    ]
    old_steps=recomputed["line_search_candidates"]
    steps=[]
    for i in SAFE_STEP_SLOTS:
        a=old_steps[i]["hgfx"]
        b=old_steps[i]["matlab"]
        steps.append({
            "from_record_zero_based":i,
            "hgfx_candidate_halving_exponent":a["best_half_step_exponent"],
            "matlab_candidate_halving_exponent":b["best_half_step_exponent"],
            "hgfx_candidate_reconstruction_residual_max_abs":
                a["candidate_reconstruction_max_abs_residual"],
            "matlab_candidate_reconstruction_residual_max_abs":
                b["candidate_reconstruction_max_abs_residual"],
            "hgfx_candidate_armijo_from_stored_values":
                a["candidate_armijo_test_from_stored_next_value"],
            "matlab_candidate_armijo_from_stored_values":
                b["candidate_armijo_test_from_stored_next_value"],
            "same_candidate_halving_exponent":bool(
                a["best_half_step_exponent"]==b["best_half_step_exponent"]),
            "both_candidate_full_steps":bool(
                a["best_half_step_exponent"]==b["best_half_step_exponent"]==0),
            "both_candidate_armijo":bool(
                a["candidate_armijo_test_from_stored_next_value"]
                and b["candidate_armijo_test_from_stored_next_value"]),
        })
    matrices={}
    for label in ("hgfx","matlab"):
        t=np.asarray(raw[label]["iter_inverse_hessian"], dtype=np.float64)
        matrices[label]={
            "record_9_frobenius_norm":float(np.linalg.norm(t[9])),
            "record_10_frobenius_norm":float(np.linalg.norm(t[10])),
            "record_10_over_9_frobenius_norm_ratio":
                float(np.linalg.norm(t[10])/np.linalg.norm(t[9])),
        }
    outcome={
        "schema":"perf01d-subject7-bfgs-branch-immutable-derived-v1",
        "status":"AUTHOR_SIDE_UNTIMED_SOURCE_DERIVED_NO_SCIENTIFIC_PASS",
        "derived_from_github_run":ORIGINAL_RUN,
        "derived_from_exact_candidate_sha":ORIGINAL_SHA,
        "original_raw_sha256":EXPECTED,
        "original_64_full_fit_scientific_result":"63/64 (subject 7 fails traj.mu/traj.muhat)",
        "excluded_terminal_ambiguous_transition_indices":[22,23],
        "safe_bfgs_decision_slots":list(SAFE_BFGS_SLOTS),
        "safe_line_search_transition_slots":list(SAFE_STEP_SLOTS),
        "source_BFGS_decision_comparisons":branches,
        "source_BFGS_decision_disagreements":sum(
            not row["same_curvature_decision"] for row in branches),
        "source_BFGS_decision_vs_saved_matrix_disagreements":sum(
            not row["both_source_branches_match_saved_T_changes"] for row in branches),
        "source_BFGS_skip_slots_hgfx":[r["record_index_zero_based"]
                                   for r in h if not r["source_condition_would_apply_update"]],
        "source_BFGS_skip_slots_matlab":[r["record_index_zero_based"]
                                     for r in m if not r["source_condition_would_apply_update"]],
        "full_half_step_reconstruction_comparisons":steps,
        "full_step_candidate_both_count":sum(r["both_candidate_full_steps"] for r in steps),
        "both_candidate_Armijo_count":sum(r["both_candidate_armijo"] for r in steps),
        "maximum_reconstruction_residual_safe_transitions":max(
            max(r["hgfx_candidate_reconstruction_residual_max_abs"],
                r["matlab_candidate_reconstruction_residual_max_abs"])
            for r in steps),
        "BFGS_T_frobenius_spike":matrices,
        "cross_implementation_T_max_component_diff":
            recomputed["maximum_matrix_component_difference"],
        "cross_implementation_first_nonzero_T":
            recomputed["first_nonzero_matrix_difference"],
        "source_hgfx_reset_indices_one_based":
            recomputed["hgfx_one_based_reset_indices"],
        "source_matlab_reset_indices_one_based":
            recomputed["matlab_one_based_reset_indices"],
        "limitations":[
            "Source-derived BFGS curvature calculations reuse frozen post-fit Ridders gradients; not independently instrumented internal optimizer operations.",
            "Full-step and Armijo decisions are compatible with reconstructed saved transitions, not a public MATLAB internal acceptance event log.",
            "Frozen reference overwrites terminal history; record transitions 22 and 23 are excluded from source-branch/acceptance interpretations.",
            "BFGS amplification is a candidate numerical mechanism, not proof of complete fitting scientific parity or a reference-only limitation.",
            "All data, starts, thresholds and failed source evidence remain unchanged; no timing was executed.",
        ],
    }
    return outcome


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=derive(a.archive)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "from":ORIGINAL_RUN,
        "branch_mismatch":result["source_BFGS_decision_disagreements"],
        "branch_vs_saved_T_mismatch":
            result["source_BFGS_decision_vs_saved_matrix_disagreements"],
        "both_full_step_candidates":result["full_step_candidate_both_count"],
        "both_armijo":result["both_candidate_Armijo_count"],
        "skip_hgfx":result["source_BFGS_skip_slots_hgfx"],
        "skip_matlab":result["source_BFGS_skip_slots_matlab"],
        "T_spike":result["BFGS_T_frobenius_spike"],
        "status":result["status"],
    },sort_keys=True))


if __name__=="__main__":
    main()
