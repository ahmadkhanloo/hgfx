#!/usr/bin/env python3
"""Untimed, noncausal algebraic direction analysis from original SHA-locked evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from compare_subject7_gradient_probes import compare as compare_paired
from derive_subject7_bfgs_branch import derive as verify_bfgs

BFGS_RUN = "42187240378"
PAIR_RUN = "42120381058"
PAIR_SHA = "b9e1982fb7fee931ea907f5a25d3bc7a7cbbd1e1"
PAIR_RAW = {
    "hgfx_raw.json": "17582f684f9db815dbd1986e5f67f2105c82f3ccf53f76d0e555cc16e2fd4057",
    "matlab_raw.json": "bea60b75cedf3bea6152f118f149d3ddeb8e8310793c55b9f4fcaf3dc09ec5d1",
}
ANCHORS = (0,1,13,14,23)


def two_term(T_h, T_m, g_h, g_m):
    """Non-unique algebraic partition of differences in own-point directions."""
    delta = -(T_h @ g_h - T_m @ g_m)
    from_T = -((T_h-T_m) @ g_m)
    from_g = -(T_h @ (g_h-g_m))
    return delta, from_T, from_g


def three_term(T_h, T_m, gh_xh, gm_xh, gm_xm):
    """Expand own-gradient term using independently evaluated same-x MATLAB Ridders."""
    return (-((T_h-T_m) @ gm_xm),
            -(T_h @ (gh_xh-gm_xh)),
            -(T_h @ (gm_xh-gm_xm)))


def scaled_direction(T,g):
    raw=-(T @ g)
    length=float(np.linalg.norm(raw))
    return raw, (raw * (1.0/length) if length>1.0 else raw.copy())


def norm(v): return float(np.linalg.norm(v))
def maximum(v): return float(np.max(np.abs(v)))


def read_paired(root:Path):
    summary=json.loads((root/"summary.json").read_bytes())
    if (str(summary.get("run_id"))!=PAIR_RUN
            or summary.get("candidate_sha")!=PAIR_SHA
            or summary.get("raw_evidence_sha256")!=PAIR_RAW):
        raise ValueError("Original matched-gradient archive provenance mismatch")
    raw={}
    for filename,expected in PAIR_RAW.items():
        content=(root/filename).read_bytes()
        if sha256(content).hexdigest()!=expected:
            raise ValueError(f"Original matched-gradient SHA256 mismatch: {filename}")
        raw[filename.split("_")[0]]=json.loads(content)
    checked=compare_paired(raw["hgfx"],raw["matlab"])
    if checked["fully_evaluated_pairs"]!=10:
        raise ValueError("Original ten identical-parameter paired comparisons incomplete")
    return raw


def history(raw,engine):
    if (raw.get("schema")!=f"perf01-subject7-bfgs-state-{engine}-v1"
            or raw.get("status")!="UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED"
            or raw.get("finite_slots")!=25
            or raw.get("n_rand_init")!=0
            or raw.get("ridders_min_steps")!=10
            or raw.get("frozen_start_matches") is not True):
        raise ValueError(f"Original {engine} optimizer source identity mismatch")
    T=np.asarray(raw["iter_inverse_hessian"],float)
    x=np.asarray(raw["iter_x"],float)
    g=np.asarray([r["grad"] for r in raw["ridders_recomputed_history"]],float)
    if (T.shape!=(24,3,3) or x.shape!=(101,3) or g.shape!=(25,3)
            or not np.all(np.isfinite(T)) or not np.all(np.isfinite(x[:25]))
            or not np.all(np.isfinite(g))):
        raise ValueError(f"Original {engine} optimizer history dimensions/nonfinite changed")
    return T,x,g


def report(bfgs_root:Path,paired_root:Path):
    audit=verify_bfgs(bfgs_root)  # verifies BOTH raw SHA256 and entire original comparator.
    if (audit["source_BFGS_decision_disagreements"]!=0
            or audit["full_step_candidate_both_count"]!=22):
        raise ValueError("Original BFGS source verdict changed")
    raw={engine:json.loads((bfgs_root/f"{engine}_raw.json").read_bytes())
         for engine in ("hgfx","matlab")}
    paired=read_paired(paired_root)
    th,xh,gh=history(raw["hgfx"],"hgfx")
    tm,xm,gm=history(raw["matlab"],"matlab")
    if (raw["hgfx"]["source_input_sha256"]!=raw["matlab"]["source_input_sha256"]
            or raw["hgfx"]["source_config_sha256"]!=raw["matlab"]["source_config_sha256"]):
        raise ValueError("Original cross-tool input/config SHA identity changed")
    rows=[]
    for i in range(24):
        delta,part_T,part_g=two_term(th[i],tm[i],gh[i],gm[i])
        d_h,step_h=scaled_direction(th[i],gh[i])
        d_m,step_m=scaled_direction(tm[i],gm[i])
        residual=maximum(delta-(part_T+part_g))
        if residual>2e-12:
            raise ValueError(f"Direction identity residual large at history slot {i}")
        row={
            "record_index_zero_based":i,
            "nonterminal_full_step_reconstruction":i<22,
            "raw_direction_difference_L2":norm(delta),
            "matrix_component_difference_max_abs":maximum(th[i]-tm[i]),
            "matrix_algebra_term_L2":norm(part_T),
            "own_gradient_algebra_term_L2":norm(part_g),
            "own_parameter_vector_difference_L2":norm(xh[i]-xm[i]),
            "clipped_direction_difference_L2":norm(step_h-step_m),
            "both_directions_clipped":bool(norm(d_h)>1 and norm(d_m)>1),
            "raw_direction_length_hgfx":norm(d_h),
            "raw_direction_length_matlab":norm(d_m),
            "algebraic_recomposition_error_max_abs":residual,
        }
        row["clipped_to_raw_difference_ratio"]=(row["clipped_direction_difference_L2"] /
             row["raw_direction_difference_L2"] if row["raw_direction_difference_L2"] else None)
        if i<22:
            row["hgfx_stored_next_point_reconstruction_error"]=maximum(xh[i]+step_h-xh[i+1])
            row["matlab_stored_next_point_reconstruction_error"]=maximum(xm[i]+step_m-xm[i+1])
            if max(row["hgfx_stored_next_point_reconstruction_error"],
                   row["matlab_stored_next_point_reconstruction_error"])>1e-12:
                raise ValueError(f"Recorded full-step arithmetic changed at {i}")
        rows.append(row)
    paired_keyed={engine:{
        (item["anchor_origin"],item["record_index_zero_based"]):item
        for item in paired[engine]["cases"]} for engine in ("hgfx","matlab")}
    anchored=[]
    for i in ANCHORS:
        for origin in ("hgfx","matlab"):
            h=paired_keyed["hgfx"][(origin,i)]
            m=paired_keyed["matlab"][(origin,i)]
            original_x=xh[i] if origin=="hgfx" else xm[i]
            if (not np.array_equal(np.asarray(h["free_parameters"],float),original_x)
                    or not np.array_equal(np.asarray(m["free_parameters"],float),original_x)):
                raise ValueError(f"Same-x gradient lost original matching x at {i}/{origin}")
            T=th[i] if origin=="hgfx" else tm[i]
            gradient_h=np.asarray(h["ridders_gradient"],float)
            gradient_m=np.asarray(m["ridders_gradient"],float)
            anchored.append({
                "record_index_zero_based":i,"anchor_origin":origin,
                "same_x_gradient_engine_difference_L2":norm(gradient_h-gradient_m),
                "same_x_T_weighted_direction_difference_L2":norm(T@(gradient_h-gradient_m)),
                "T_frobenius_norm":float(np.linalg.norm(T)),
                "terminal_slot_not_an_acceptance_event":i>=22,
            })
        matlab_gradient_at_hgfx_x=np.asarray(
            paired_keyed["matlab"][("hgfx",i)]["ridders_gradient"],float)
        terms=three_term(th[i],tm[i],gh[i],matlab_gradient_at_hgfx_x,gm[i])
        direction_difference=-(th[i]@gh[i]-tm[i]@gm[i])
        residual=maximum(direction_difference-sum(terms))
        if residual>2e-12:
            raise ValueError(f"Same-x 3-term decomposition residual too large at {i}")
        anchored.append({
            "record_index_zero_based":i,
            "anchor_origin":"3_term_algebraic_at_hgfx_x",
            "matrix_term_L2":norm(terms[0]),
            "same_x_gradient_engine_term_L2":norm(terms[1]),
            "different_x_gradient_state_term_L2":norm(terms[2]),
            "raw_direction_difference_L2":norm(direction_difference),
            "max_recomposition_error":residual,
            "note":"Nonunique algebra; this is NOT a causal intervention.",
        })
    eig=[]
    for i in (9,10):
        obj={"record_index_zero_based":i}
        for engine,T in (("hgfx",th[i]),("matlab",tm[i])):
            eigen=np.linalg.eigvalsh(T)
            obj[engine]={
                "eigenvalues_ascending":eigen.tolist(),
                "condition_number_if_spd":float(eigen[-1]/eigen[0]) if eigen[0]>0 else None,
                "frobenius_norm":float(np.linalg.norm(T)),
            }
        eig.append(obj)
    return {
        "schema":"perf01d-subject7-direction-algebraic-derived-v1",
        "status":"AUTHOR_SIDE_NOT_CAUSAL_NOT_SCIENTIFIC_PASS_NOT_TIMED",
        "original_bfgs_run":BFGS_RUN,
        "original_matched_gradient_run":PAIR_RUN,
        "original_matched_gradient_source_sha":PAIR_SHA,
        "original_bfgs_raw_sha256":audit["original_raw_sha256"],
        "original_paired_raw_sha256":PAIR_RAW,
        "original_scientific_failure":"63/64 public fits, zero-based subject 7 traj.mu and traj.muhat mismatch",
        "direction_records":rows,
        "same_vector_anchors":anchored,
        "matrix_eigenspectra":eig,
        "unambiguous_nonterminal_transition_indices":list(range(22)),
        "excluded_terminal_transition_indices":[22,23],
        "limitations":[
            "Algebraic partition is not unique/causal: each engine has its own previously diverged parameter state.",
            "Five post-hoc chosen anchors per original optimizer, not whole-vector gradient equivalence.",
            "maxStep=1 clips raw BFGS direction; the raw-direction difference is not the actual applied-step difference.",
            "Original frozen MATLAB optimizer terminal history overwrite excludes the last two transitions from acceptance conclusions.",
            "No new fitting, timing, GPU evidence, frozen threshold changes, eligibility changes, or independent review approval.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bfgs",type=Path,required=True)
    p.add_argument("--paired",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=report(a.bfgs,a.paired)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "run_bfgs":BFGS_RUN,"run_paired":PAIR_RUN,
        "nonterminal_steps":len(result["unambiguous_nonterminal_transition_indices"]),
        "same_vector_diagnostics":len(result["same_vector_anchors"]),
        "record_10":result["direction_records"][10],
        "spectra":result["matrix_eigenspectra"],
        "status":result["status"],
    },sort_keys=True))


if __name__=="__main__":
    main()
