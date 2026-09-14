#!/usr/bin/env python3
"""Classify exact-state D08 holdout Ridders objective samples at frozen row 38."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from check_m18_demo_uhgf_ar1 import REFERENCE_COMMIT, _array
from hgfx.compat.workflows import WorkflowFitProblem, resolve_config

PROTOCOL = "m18-d08-holdout-source-probe-1"

def scalar(value): return np.float64(_array(value).reshape(-1)[0])
def scalar_cmp(actual, expected):
    a=np.float64(actual); e=np.float64(expected)
    return {"hgfx":float(a),"matlab":float(e),"abs_diff":float(abs(a-e)),"exact":bool(a==e)}

def make_problem(reference):
    u=_array(reference["inputs"]).reshape(-1); y=_array(reference["responses"]).reshape(-1)
    prc=resolve_config("uhgf").resolve_placeholders(u)
    obs=resolve_config("gaussian_obs").resolve_placeholders(u)
    return WorkflowFitProblem(y,u,prc,obs)

def decompose(problem, free):
    out=problem.evaluate_full(problem.expand(free))
    return {"log_likelihood":np.float64(out.log_likelihood),"perceptual_prior":np.float64(out.perceptual_prior.total),"observation_prior":np.float64(out.observation_prior.total),"neg_log_joint":np.float64(out.neg_log_joint)}

def compare_decomp(actual, expected): return {k:scalar_cmp(actual[k],scalar(expected[k])) for k in actual}

def ridders_replay(hvals,fplus,fminus):
    n=len(hvals); p=np.full((n,n),np.nan,dtype=np.float64); result=np.float64(np.nan); error=np.float64(np.finfo(np.float64).max); diag=np.full(n,np.nan)
    for i in range(n):
        h=np.float64(hvals[i]); p[i,0]=np.float64((np.float64(fplus[i])-np.float64(fminus[i]))/(np.float64(2.0)*h))
        if i>0:
            divsq=np.float64(1.2)**2; t=np.float64(divsq)
            for j in range(1,i+1):
                p[i,j]=np.float64((t*p[i,j-1]-p[i-1,j-1])/(t-np.float64(1.0))); t=np.float64(t*divsq)
                curr=np.float64(max(abs(p[i,j]-p[i,j-1]),abs(p[i,j]-p[i-1,j-1])))
                if curr<error: error=curr; result=p[i,j]
        diag[i]=p[i,i]
    return result,error,diag

def main(reference_path:Path, output_path:Path)->int:
    ref=json.loads(reference_path.read_text())
    if ref.get("protocol")!=PROTOCOL or ref.get("reference_commit")!=REFERENCE_COMMIT: raise ValueError("Frozen protocol/reference mismatch")
    if ref.get("case_id")!="D08_fit" or int(ref.get("seed"))!=314159265 or int(ref.get("source_trace_row_1based"))!=38: raise ValueError("Frozen D08 holdout contract mismatch")
    problem=make_problem(ref); source=_array(ref["source_x"]).reshape(-1)
    if source.size!=7 or len(problem.free_indices)!=7: raise ValueError("Expected seven free D08 parameters")
    first=None; all_samples=True; all_ml=True; all_hgfx=True; components=[]
    full_idx=_array(ref["free_full_indices_1based"]).reshape(-1).astype(int)
    for c0,probe in enumerate(ref["probes"]):
        if int(probe["component_free_index_1based"])!=c0+1: raise ValueError("Component ordering mismatch")
        h=_array(probe["h"]).reshape(-1); xp=_array(probe["x_plus"]).reshape(-1); xm=_array(probe["x_minus"]).reshape(-1)
        mfp=_array(probe["f_plus"]).reshape(-1); mfm=_array(probe["f_minus"]).reshape(-1); hfp=[]; hfm=[]; samples=[]
        for i in range(len(h)):
            pv=source.copy(); mv=source.copy(); pv[c0]=xp[i]; mv[c0]=xm[i]
            pd=decompose(problem,pv); md=decompose(problem,mv); pc=scalar_cmp(pd["neg_log_joint"],mfp[i]); mc=scalar_cmp(md["neg_log_joint"],mfm[i]); pp=compare_decomp(pd,probe["plus_decomposition"][i]); mp=compare_decomp(md,probe["minus_decomposition"][i]); hfp.append(pd["neg_log_joint"]); hfm.append(md["neg_log_joint"])
            samples.append({"step_zero_based":i,"h":float(h[i]),"plus":{"objective":pc,"decomposition":pp},"minus":{"objective":mc,"decomposition":mp}})
            for side,cmp,parts in (("plus",pc,pp),("minus",mc,mp)):
                if not cmp["exact"]:
                    all_samples=False
                    if first is None:
                        name=next((k for k,v in parts.items() if not v["exact"]),None)
                        first={"component_free_index_zero_based":c0,"component_full_index_zero_based":int(full_idx[c0])-1,"step_zero_based":i,"side":side,"h":float(h[i]),"objective_abs_diff":cmp["abs_diff"],"first_differing_decomposition":name,"decomposition":parts}
        md,me,mdi=ridders_replay(h,mfp,mfm); hd,he,hdi=ridders_replay(h,hfp,hfm); ed=scalar(probe["selected_derivative"]); ee=scalar(probe["selected_error"])
        mdc=scalar_cmp(md,ed); mec=scalar_cmp(me,ee); hdc=scalar_cmp(hd,ed); hec=scalar_cmp(he,ee); all_ml &= mdc["exact"] and mec["exact"]; all_hgfx &= hdc["exact"] and hec["exact"]
        exported=_array(probe["diagonal"]).reshape(-1)
        components.append({"component_free_index_zero_based":c0,"component_full_index_zero_based":int(full_idx[c0])-1,"stop_step":int(scalar(probe["stop_step"])),"matlab_samples_python_replay":{"derivative":mdc,"error":mec,"diagonal_max_abs":float(np.max(np.abs(mdi-exported)))},"hgfx_samples_python_replay":{"derivative":hdc,"error":hec,"diagonal_max_abs":float(np.max(np.abs(hdi-exported)))},"samples":samples})
    if not all_samples: cls="OBJECTIVE_SAMPLE_DIVERGENCE"
    elif not all_ml: cls="RIDDERS_EXTRAPOLATION_ARITHMETIC_DIVERGENCE"
    elif not all_hgfx: cls="RIDDERS_REPLAY_UNEXPLAINED_DIVERGENCE"
    else: cls="NO_RIDDERS_DIVERGENCE_AT_SOURCE"
    result={"protocol":PROTOCOL,"reference_commit":REFERENCE_COMMIT,"case_id":"D08_fit","seed":314159265,"classification":cls,"source_trace_row_zero_based":37,"source_objective_replay":scalar_cmp(problem.evaluate_free(source),scalar(ref["source_val"])),"first_objective_difference":first,"components":components,"acceptance_effect":"NONE_DIAGNOSTIC_ONLY","decision_note":"The failed prospective D08 holdout remains preserved; this probe only localizes the numerical source."}
    output_path.parent.mkdir(parents=True,exist_ok=True); output_path.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"classification":cls,"first_objective_difference":first}),flush=True); return 0

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("reference",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); raise SystemExit(main(a.reference,a.output))
