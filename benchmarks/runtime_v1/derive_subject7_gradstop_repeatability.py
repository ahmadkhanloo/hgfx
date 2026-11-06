#!/usr/bin/env python3
"""PERF-01D: hash-locked original BFGS gradient stopping-margin/replay audit.

No optimizer, model, data, reference, threshold, or timer is changed.
The numerical Ridders errors are HEURISTIC estimates, not rigorous bounds.
Two complete prior source-native run artifacts and the original BFGS archive
are inputs; no bitwise repeatability classification may become a science PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

from derive_subject7_direction_decomposition import verify_original_bfgs_archive
from compare_subject7_native_termination import HGFX,MATLAB,RUN
from compare_fits import TOLS

BFGS_RUN="42187240378"
NATIVE_RUNS=("42232378487","42232421468")
NATIVE_SHAS=("6351160b2b528a9db894e873ce65677ee847bbe5",
             "5d26ca719a2a3e996ca07edd2d29282fc3ca1173")
TOL_GRAD=1e-3
TRIAL_RTOL,TRIAL_ATOL=(3e-8,3e-10)
FIELDS={"mu","muhat","sa","sahat","da","epsi","psi","ud","v","w","wt"}
STATUS="AUTHOR_SIDE_SOURCE_NATIVE_GRADIENT_MARGIN_AND_TWO_RUN_REPLAY_NOT_SCIENTIFIC_PASS"


def read_native(root:Path,run:str,sha:str,old_sha:dict)->dict:
    report=json.loads((root/f"derived-native-termination-{run}.json").read_bytes())
    if (report.get("github_run_id")!=run or report.get("tested_sha")!=sha
        or report.get("schema")!="perf01d-subject7-source-native-termination-pair-v1"
        or report.get("status")!="AUTHOR_SIDE_NATIVE_TERMINATION_RECORDED_NO_SCIENTIFIC_FIT_PASS"
        or report.get("frozen_hgfx_sha")!=HGFX
        or report.get("frozen_matlab_sha")!=MATLAB
        or report.get("original_64_fit_run")!=RUN
        or report.get("original_64_raw_sha256")!=old_sha
        or report.get("original_scientific_result")!="63/64 NONPASS; original subject 7 mu/muhat fail"
        or report.get("matlab_source_termination_reason")!="tol_grad"
        or report.get("hgfx_source_termination_reason")!="tol_grad"
        or report.get("hgfx_source_iterations")!=24
        or report.get("hgfx_source_resets")!=0
        or report.get("matlab_normal_verbose_all_outputs_exact") is not True
        or report.get("hgfx_direct_vs_same_host_public_all_optimizer_states_exact") is not True
        or report.get("matlab_finite_history_slots")!=25
        or report.get("hgfx_finite_history_slots")!=25):
        raise ValueError(f"Native source-locked full public fit identity changed: {run}")
    raw={}
    for filename in ("hgfx_raw.json","matlab_raw.json"):
        payload=(root/filename).read_bytes()
        digest=hashlib.sha256(payload).hexdigest()
        if digest!=report["fresh_raw_sha256"][filename]:
            raise ValueError(f"Native original raw SHA256 tampered: {run} {filename}")
        obj=json.loads(payload)
        engine=filename.split("_")[0]
        if (obj.get("frozen_hgfx_sha")!=HGFX
            or obj.get("frozen_matlab_sha")!=MATLAB
            or obj.get("source_input_sha256") is None
            or obj.get("source_config_sha256") is None
            or obj.get("source_native_termination")!="tol_grad"
            or obj.get("subject_index_zero_based")!=7
            or obj.get("trials")!=128
            or obj.get("model")!="hgf_binary"
            or obj.get("observation_model")!="unitsq_sgm"):
            raise ValueError(f"Native frozen source raw identity changed: {run} {engine}")
        raw[engine]=obj
    h=raw["hgfx"]
    m=raw["matlab"]
    if (h.get("source_native_iterations")!=24 or h.get("source_native_reset_count")!=0
        or h.get("free_indices_zero_based")!=[12,13,14]
        or h.get("public_vs_same_source_direct_exact")!={
            "arg_min":True,"iter_x":True,"iter_val":True}
        or m.get("same_session_normal_verbose_exact_all_fields") is not True):
        raise ValueError(f"Native source internal same-session controls failed {run}")
    return {"summary":report,**raw}


def finite_comparison(first,second,expected_shape):
    a=np.asarray(first,float);b=np.asarray(second,float)
    if (a.shape!=expected_shape or b.shape!=expected_shape
        or not np.array_equal(np.isfinite(a),np.isfinite(b))
        or not np.array_equal(np.isnan(a),np.isnan(b))
        or not np.all(np.isfinite(a[np.isfinite(a)]))
        or not np.all(np.isfinite(b[np.isfinite(b)]))):
        raise ValueError("Source history finite mask/shape changed")
    ok=np.isfinite(a)&np.isfinite(b)
    diff=np.abs(a[ok]-b[ok])
    index=np.argwhere(ok & (a!=b))
    return {
        "shape":list(expected_shape),
        "same_binary64":bool(not index.size),
        "first_differing_index_zero_based":index[0].tolist() if index.size else None,
        "differing_finite_entries":int(len(index)),
        "maximum_absolute_difference":float(np.max(diff)) if diff.size else None,
    }


def metric(x,grad,err,objective):
    x=np.asarray(x,float);g=np.asarray(grad,float);e=np.asarray(err,float)
    if (x.shape!=(3,) or g.shape!=(3,) or e.shape!=(3,)
        or not np.isfinite(objective) or not np.isfinite(x).all()
        or not np.isfinite(g).all() or not np.isfinite(e).all()
        or np.any(e<0)):
        raise ValueError("Ridders own-state transformed gradient/error malformed")
    scale=np.maximum(np.abs(x),1.)/max(abs(float(objective)),1.)
    components=np.abs(g)*scale
    uncertainty=e*scale
    if not np.isfinite(components).all() or not np.isfinite(uncertainty).all():
        raise ValueError("Nonfinite source-normalized gradient metric")
    return {
        "source_tolGrad_metric":float(np.max(components)),
        "source_threshold":TOL_GRAD,
        "source_metric_fraction_of_threshold":float(np.max(components)/TOL_GRAD),
        "source_gradient_component_winning_index_zero_based":int(np.argmax(components)),
        "original_Ridders_grad":g.tolist(),
        "original_Ridders_error_HEURISTIC":e.tolist(),
        "source_scaled_gradient_components":components.tolist(),
        "Ridders_scaled_error_linf_HEURISTIC":float(np.max(uncertainty)),
        "estimated_margin_below_or_above_stop_threshold_SIGNED":
            float(TOL_GRAD-np.max(components)),
        "estimate_only_not_rigorous_error_bound":True,
    }


def original_gradient_history(bfgs:Path,branch:Path):
    summary,_=verify_original_bfgs_archive(bfgs,branch)
    both={}
    for engine in ("hgfx","matlab"):
        raw=json.loads((bfgs/f"{engine}_raw.json").read_bytes())
        if (raw.get("finite_slots")!=25
            or raw.get("ridders_min_steps")!=10
            or raw.get("source_run_id")!=RUN
            or raw.get("frozen_hgfx_sha")!=HGFX
            or raw.get("frozen_matlab_sha")!=MATLAB):
            raise ValueError(f"Original BFGS source/gradient inventory changed: {engine}")
        rec=raw["ridders_recomputed_history"]
        x=np.asarray(raw["iter_x"],float)
        v=np.asarray(raw["iter_val"],float)
        if (len(rec)!=25 or x.shape!=(101,3) or v.shape!=(101,)
            or np.flatnonzero(np.isfinite(v)).tolist()!=list(range(25))
            or not np.array_equal(x[23],x[24])):
            raise ValueError(f"Original BFGS terminal history changed: {engine}")
        rows={}
        for i in (21,22,23,24):
            entry=rec[i]
            params=np.asarray(entry["free_parameters"],float)
            if (entry["record_index_zero_based"]!=i
                or not np.array_equal(x[i],params)
                or not np.isclose(entry["objective_recomputed"],v[i],
                                  rtol=TRIAL_RTOL,atol=TRIAL_ATOL)):
                raise ValueError(f"Original recorded gradient owns wrong state {engine}/{i}")
            rows[str(i)]=metric(params,entry["grad"],entry["ridders_error"],
                                entry["objective_recomputed"])
        if not (rows["22"]["source_tolGrad_metric"]>TOL_GRAD
                and rows["23"]["source_tolGrad_metric"]<TOL_GRAD):
            raise ValueError(f"Original terminal gradient replay incompatible with source-native tol_grad {engine}")
        both[engine]=rows
    return summary,both


def trialwise_pair(a,b,reference):
    if set(a)!=FIELDS or set(b)!=FIELDS or set(reference)!=FIELDS:
        raise ValueError("Original all-11 HGF field inventory changed")
    report={}
    for k in sorted(FIELDS):
        x=np.asarray(a[k],float);y=np.asarray(b[k],float);m=np.asarray(reference[k],float)
        shape=(128,2) if k=="w" else (128,3)
        if (x.shape!=shape or y.shape!=shape or m.shape!=shape
                or not np.array_equal(np.isnan(x),np.isnan(y))
                or not np.array_equal(np.isnan(y),np.isnan(m))):
            raise ValueError(f"Original HGF trajectory field shape or NaN mask changed: {k}")
        report[k]={
            "between_two_HGFX_run_mismatched_cells_OLD_TOL":
                int(np.count_nonzero(~np.isclose(x,y,rtol=TRIAL_RTOL,atol=TRIAL_ATOL,equal_nan=True))),
            "HGFX_run_first_vs_MATLAB_mismatched_cells_OLD_TOL":
                int(np.count_nonzero(~np.isclose(x,m,rtol=TRIAL_RTOL,atol=TRIAL_ATOL,equal_nan=True))),
            "HGFX_run_second_vs_MATLAB_mismatched_cells_OLD_TOL":
                int(np.count_nonzero(~np.isclose(y,m,rtol=TRIAL_RTOL,atol=TRIAL_ATOL,equal_nan=True))),
            "max_between_HGFX_run_abs":float(np.nanmax(np.abs(x-y))),
        }
    if ([(k,v["HGFX_run_first_vs_MATLAB_mismatched_cells_OLD_TOL"],
           v["HGFX_run_second_vs_MATLAB_mismatched_cells_OLD_TOL"])
            for k,v in report.items()
            if v["HGFX_run_first_vs_MATLAB_mismatched_cells_OLD_TOL"]
            or v["HGFX_run_second_vs_MATLAB_mismatched_cells_OLD_TOL"]]
        !=[("mu",4,4),("muhat",4,4)]):
        raise ValueError("Original subject-7 4+4 non-PASS trialwise mismatch not preserved")
    return report


def derive(bfgs:Path,branch:Path,first:Path,second:Path)->dict:
    if TOLS["final"]!=(3e-8,3e-10):
        raise ValueError("Original final-parameter tolerance altered")
    frozen,grads=original_gradient_history(bfgs,branch)
    a=read_native(first,NATIVE_RUNS[0],NATIVE_SHAS[0],{
        "hgfx_raw.json":"6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb",
        "matlab_raw.json":"2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98",
    })
    b=read_native(second,NATIVE_RUNS[1],NATIVE_SHAS[1],a["summary"]["original_64_raw_sha256"])
    for key in ("source_input_sha256","source_config_sha256"):
        for engine in ("hgfx","matlab"):
            if a[engine][key]!=b[engine][key]:
                raise ValueError("Two-run source configuration differs")
    if first.resolve()==second.resolve():
        raise ValueError("Two independent source runs are required")
    if (a["summary"]["fresh_raw_sha256"]["matlab_raw.json"]
         !=b["summary"]["fresh_raw_sha256"]["matlab_raw.json"]):
        raise ValueError("Original MATLAB two raw runs not bitwise identical; needs separate scientific review")
    if (a["summary"]["fresh_raw_sha256"]["hgfx_raw.json"]
         ==b["summary"]["fresh_raw_sha256"]["hgfx_raw.json"]):
        raise ValueError("HGFX two raw runs expected to differ as documented; do not change case denominator")
    h1=a["hgfx"];h2=b["hgfx"]
    x1=np.asarray(h1["direct_iter_x"],float);x2=np.asarray(h2["direct_iter_x"],float)
    v1=np.asarray(h1["direct_iter_val"],float);v2=np.asarray(h2["direct_iter_val"],float)
    if (np.flatnonzero(np.isfinite(v1)).tolist()!=list(range(25))
        or np.flatnonzero(np.isfinite(v2)).tolist()!=list(range(25))
        or not np.array_equal(x1[0],x2[0])):
        raise ValueError("Original HGFX two-run starts/populated history changed")
    history=finite_comparison(x1,x2,(101,3))
    if history["same_binary64"]:
        raise ValueError("Expected documented HGFX cross-run bitwise difference")
    finals=finite_comparison(h1["public_fitted_full"],h2["public_fitted_full"],(15,))
    objects=finite_comparison(v1,v2,(101,))
    ref=a["matlab"]["baseline_traj"]
    trial=trialwise_pair(h1["public_traj"],h2["public_traj"],ref)
    return {
        "schema":"perf01d-subject7-final-gradient-margin-two-run-replay-v1",
        "status":STATUS,
        "original_64_scientific_full_fit":"63/64 NONPASS; original 4 mu and 4 muhat cells",
        "original_full_fit_run_id":RUN,
        "original_bfgs_run_id":BFGS_RUN,
        "original_bfgs_sha256":frozen["raw_evidence_sha256"],
        "original_bfgs_source_sha":frozen["candidate_sha"],
        "frozen_hgfx_sha":HGFX,
        "frozen_matlab_sha":MATLAB,
        "native_run_ids":list(NATIVE_RUNS),
        "native_tested_shas":list(NATIVE_SHAS),
        "native_raw_sha256_each":{
            r:obj["summary"]["fresh_raw_sha256"] for r,obj in zip(NATIVE_RUNS,(a,b))},
        "threshold_source_tolGrad":TOL_GRAD,
        "gradient_source":"original BFGS raw own-engine Ridders min_steps=10 recalculated POST FIT, heuristic errors; not in-loop internal instrumentation",
        "gradient_terminal_own_engine_states":grads,
        "original_source_native_termination_each":{
            r:{"hgfx":obj["hgfx"]["source_native_termination"],
               "matlab":obj["matlab"]["source_native_termination"]}
            for r,obj in zip(NATIVE_RUNS,(a,b))},
        "matlab_two_run_raw_sha_exact_same":True,
        "hgfx_two_run_raw_sha_exact_same":False,
        "hgfx_two_run_direct_history":history,
        "hgfx_two_run_public_final":finals,
        "hgfx_two_run_objective_history":objects,
        "hgfx_two_run_full_trialwise_11_fields":trial,
        "unchanged_original_trialwise_tolerances":{"rtol":TRIAL_RTOL,"atol":TRIAL_ATOL},
        "limitations":[
            "Ridders error entries are numerical heuristic estimates, not mathematically certified bounds on true derivatives.",
            "Original BFGS gradient history was POST-FIT re-evaluated at archived states, NOT instrumented inside source optimizer.",
            "Original terminal history is overwritten; no unsupported claims about accepted last two transitions.",
            "Two GitHub Actions runners are not matched hardware/CPU dispatch; exact BLAS/CPU culprit NOT identified.",
            "MATLAB raw SHA identical in these TWO recorded runs only; not universal cross-host deterministic equivalence.",
            "No changed original source, data, priors, starts, seed, model family, acceptance tolerance or exclusion.",
            "Both HGFX runs remain mismatched vs MATLAB in original scientific full fitted 4+4 mu/muhat cells.",
            "Original 63/64 scientific NON-PASS, PERF-01C NOT FROZEN; no performance timing, physical GPU, speedup, or independent scientific verdict.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("bfgs","branch","native-first","native-second","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    data=derive(a.bfgs,a.branch,a.native_first,a.native_second)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":data["status"],
        "gradient_last_record_ratio_hgfx":data["gradient_terminal_own_engine_states"]["hgfx"]["23"]["source_metric_fraction_of_threshold"],
        "gradient_last_record_ratio_matlab":data["gradient_terminal_own_engine_states"]["matlab"]["23"]["source_metric_fraction_of_threshold"],
        "hgfx_two_run_first_diff":data["hgfx_two_run_direct_history"]["first_differing_index_zero_based"],
        "hgfx_two_run_max_final_abs":data["hgfx_two_run_public_final"]["maximum_absolute_difference"],
        "matlab_sha_equal":data["matlab_two_run_raw_sha_exact_same"],
        "original_science":"63/64 NONPASS; no timing",
    },sort_keys=True))


if __name__=="__main__":
    main()
