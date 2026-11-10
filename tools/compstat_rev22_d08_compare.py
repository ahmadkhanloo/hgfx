#!/usr/bin/env python3
"""REV-2.2 official D08 three-source comparator; preserve failures and no uHGF gate.

This is a postprocessor over immutable MATLAB fit, released-Wheel HGFX fit,
and exact MATLAB same-vector re-evaluations. No model/optimizer calls here.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
from tools.compstat_rev22_d08_hgfx import (
    PROTOCOL, NATIVE_SIM, f64, hessian_diagnostics, jsonarray,
)


def check(ok,reason):
    if not ok:
        raise ValueError(reason)


def as_vec(value):
    return f64(value).reshape(-1)


def pair_field(field,source,replica,*,rtol=3e-8,atol=3e-10):
    left=f64(source)
    right=f64(replica)
    if left.shape!=right.shape and left.size==right.size and (
        left.ndim==1 or right.ndim==1) and (left.ndim<=2 and right.ndim<=2):
        left=left.reshape(-1)
        right=right.reshape(-1)
    if left.shape!=right.shape:
        return {"field":field,"ok":False,"reason":"SHAPE_MISMATCH",
                "matlab_shape":list(left.shape),"hgfx_shape":list(right.shape),
                "rtol":rtol,"atol":atol}
    l=left.reshape(-1)
    r=right.reshape(-1)
    cls_l=np.array([("NaN" if np.isnan(v) else "Infinity" if np.isposinf(v)
                   else "-Infinity" if np.isneginf(v) else "FINITE") for v in l])
    cls_r=np.array([("NaN" if np.isnan(v) else "Infinity" if np.isposinf(v)
                   else "-Infinity" if np.isneginf(v) else "FINITE") for v in r])
    status_equal=cls_l==cls_r
    bothfinite=np.isfinite(l)&np.isfinite(r)
    finite_ok=np.zeros(l.shape,dtype=bool)
    finite_ok[bothfinite]=np.less_equal(
        np.abs(l[bothfinite]-r[bothfinite]),
        atol+rtol*np.abs(l[bothfinite]))
    per_elem_ok=status_equal & (finite_ok | (~np.isfinite(l) & ~np.isfinite(r)))
    ok=bool(np.all(per_elem_ok))
    first=np.flatnonzero(~per_elem_ok)
    finite_deltas=np.abs(l[bothfinite]-r[bothfinite])
    return {
        "field":field,"ok":ok,
        "shape":list(left.shape),"n":int(l.size),
        "finite_paired":int(bothfinite.sum()),
        "nonfinite_status_mismatches":int((~status_equal).sum()),
        "numeric_out_of_frozen_gate":int((bothfinite&~finite_ok).sum()),
        "first_bad_flat_index":int(first[0]) if len(first) else None,
        "matlab_first_bad":str(l[first[0]]) if len(first) else None,
        "hgfx_first_bad":str(r[first[0]]) if len(first) else None,
        "maximum_both_finite_absolute_difference":
            float(np.max(finite_deltas)) if finite_deltas.size else None,
        "rtol":rtol,"atol":atol,
    }


def input_identity(ref,hgfx,matlab_cross):
    check(ref["protocol"]==hgfx["protocol"]==matlab_cross["protocol"]==PROTOCOL,
          "Wrong new protocol or mixing old G/E source")
    check((ref["source"],hgfx["source"],matlab_cross["source"])==
          ("matlab","hgfx","matlab_cross"),"Input source provenance changed")
    for name in ("model","observation_model"):
        check(ref[name]==hgfx[name]==matlab_cross[name],
              f"Cross-model mismatch: {name}")
    check(ref["model"]=="uhgf" and ref["observation_model"]=="gaussian_obs",
          "Not the original continuous uHGF Gaussian workflow")
    for key in ("seed","trials"):
        check(ref[key]==hgfx[key]==matlab_cross[key],
              "Seed/horizon changed: "+key)
    check(ref["seed"]==123456789 and ref["trials"]==614,"Not official D08")
    expected_ref="2437f4dc241541072722a2695ddeca7b44d83dd3"
    for x in (ref,hgfx,matlab_cross):
        check(x["reference_commit"]==expected_ref,"Reference source changed")
    check(hgfx["wheel_sha256"]==
          "5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90",
          "Not original released Wheel")
    check(ref["release_source_commit"]==hgfx["release_source_commit"]==
          "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
          "Original release drift")
    inputs=f64(ref["inputs"]).reshape(-1)
    responses=f64(ref["responses"]).reshape(-1)
    check(inputs.shape==responses.shape==(614,) and
          np.isfinite(inputs).all() and np.isfinite(responses).all(),
          "Incomplete original 614 trial source")
    check(sha256(np.asarray(inputs,dtype="<f8").tobytes()).hexdigest()==
          hgfx["inputs_f64_sha256"] and
          sha256(np.asarray(responses,dtype="<f8").tobytes()).hexdigest()==
          hgfx["responses_f64_sha256"],
          "MATLAB and Python did NOT evaluate exact same raw binary64 input/response")
    check(np.array_equal(f64(ref["native_simulation"]).reshape(-1),NATIVE_SIM)
          and float(ref["native_observation"])==0.00002,
          "Original native simulated D08 parameters changed")
    return {"same_frozen_model":True,"same_614_input_values":True,
            "same_614_simulated_response_values":True,
            "response_f64_sha256":hgfx["responses_f64_sha256"]}


def compare(ref,hgfx,matlab_cross):
    source=input_identity(ref,hgfx,matlab_cross)
    checks=[]
    for label,matlab_key,hgfx_key in [
        ("initial_transformed","init","initial"),
        ("final_transformed","final","final"),
        ("native_fit_perceptual","native_fit_perceptual","native_fit_perceptual"),
        ("native_fit_observation","native_fit_observation","native_fit_observation"),
        ("negative_log_likelihood","negLl","negLl"),
        ("negative_log_joint","negLj","negLj"),
        ("BIC","BIC","BIC"),
        ("LME","LME","LME"),
        ("H","H","H"),("Sigma","Sigma","Sigma"),("Corr","Corr","Corr"),
        ("prediction","yhat","yhat"),("residual","res","res"),
    ]:
        tol=(2e-6,2e-8) if label in ("H","LME") else (
            (5e-6,5e-8) if label in ("Sigma","Corr") else (3e-8,3e-10))
        checks.append(pair_field(label,ref[matlab_key],hgfx[hgfx_key],
                                 rtol=tol[0],atol=tol[1]))
    orig_traj=ref.get("traj",{})
    wheel_traj=hgfx.get("traj",{})
    check(isinstance(orig_traj,dict) and isinstance(wheel_traj,dict)
          and len(orig_traj)>0 and len(wheel_traj)>0,
          "Missing authentic trajectory evidence")
    allfields=sorted(set(orig_traj)|set(wheel_traj))
    for field in allfields:
        if field not in orig_traj or field not in wheel_traj:
            checks.append({"field":"traj."+field,"ok":False,
                           "reason":"MISSING_FIELD_IN_ONE_IMPLEMENTATION"})
        else:
            checks.append(pair_field("traj."+field,orig_traj[field],wheel_traj[field]))
    ref_h=ref["H"]
    diag_reference=hessian_diagnostics(f64(ref_h))
    diag_hgfx=hessian_diagnostics(f64(hgfx["H"]))
    cross={}
    for endpoint in ("matlab_endpoint","hgfx_endpoint"):
        a=matlab_cross[endpoint]
        b=hgfx["objectives"][endpoint]
        check(a.get("valid") is not None and b.get("rval") is not None,
              "Cross-evaluation incomplete")
        alj=float(a["negLj"]);blj=float(b["negLj"])
        all_=float(a["negLl"]);bll=float(b["negLl"])
        cross[endpoint]={
            "matlab_valid":bool(a["valid"]),
            "hgfx_rval":int(b["rval"]),
            "matlab_negLj":a["negLj"],"hgfx_negLj":b["negLj"],
            "same_vector_negLj_absolute_gap":(
                float(abs(alj-blj)) if math.isfinite(alj) and math.isfinite(blj)
                else "NaN"),
            "matlab_negLl":a["negLl"],"hgfx_negLl":b["negLl"],
            "same_vector_negLl_absolute_gap":(
                float(abs(all_-bll)) if math.isfinite(all_) and math.isfinite(bll)
                else "NaN"),
            "trial_likelihood_status":{
                "field":endpoint+".trialLogLls",
                **pair_field(endpoint+".trialLogLls",
                             a["trialLogLls"],b["trialLogLls"],
                             rtol=0.0,atol=0.0)
            },
            "family_objective_parity_gate":"NOT_PREDECLARED_FOR_UHGF",
        }
    selfref=pair_field("matlab_self_reference_nlj",
                       ref["negLj"],matlab_cross["matlab_endpoint"]["negLj"])
    selfnll=pair_field("matlab_self_reference_nll",
                       ref["negLl"],matlab_cross["matlab_endpoint"]["negLl"])
    selfok=bool(selfref["ok"] and selfnll["ok"])
    direct=bool(all(row["ok"] for row in checks))
    discrepancy=next((row for row in checks if not row["ok"]),None)
    if not selfok:
        cls="INSUFFICIENT_REFERENCE_EVIDENCE"
    elif direct:
        cls="DIRECT_PARITY_NEW_REV22_SCOPE"
    else:
        cls="UNRESOLVED_DISCREPANCY"
    return {
        "protocol":PROTOCOL,
        "source":"postprocessor",
        "official_case":"D08_fit",
        "input_source_identity":source,
        "classification":cls,
        "existing_original_m18_d08_failed_status_overwritten":False,
        "release_version":"1.0.0",
        "direct_existing_scope_pass":direct,
        "direct_checks":checks,
        "first_direct_out_of_gate":discrepancy,
        "cross_objectives":cross,
        "cross_family_objective_pass":"NO_PREDECLARED_UHGF_FAMILY_GATE",
        "matlab_self_reference":{
            "negLj":selfref,"negLl":selfnll,"ok":selfok
        },
        "hessian_reference":diag_reference,
        "hessian_hgfx":diag_hgfx,
        "matlab_termination":"NOT_EXPORTED",
        "hgfx_release_termination":"NOT_EXPORTED",
        "matlab_warning_coverage":ref["warning_coverage"],
        "hgfx_warning_coverage":hgfx["warning_coverage"],
        "warning_mechanisms_categorized":False,
        "optimizer_trajectory_classification":"NOT_ASSESSED_FULL_PATH",
        "scientific_global_parity":"NOT_GLOBAL_PASS",
        "d2_d3":"BLOCKED",
        "historical_full_cpu":"NOT_PASS",
        "no_posthoc_new_tolerances":True,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for item in ("matlab_reference","hgfx","matlab_cross","output"):
        p.add_argument("--"+item.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    check(not a.output.exists(),"Refuse to overwrite derived comparison")
    j=lambda file:json.loads(file.read_text(encoding="utf-8"))
    result=compare(j(a.matlab_reference),j(a.hgfx),j(a.matlab_cross))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,
                                   allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "classification":result["classification"],
        "source_identical":result["input_source_identity"]["same_614_input_values"],
        "direct_criteria_pass":result["direct_existing_scope_pass"],
        "first_out_of_gate":result["first_direct_out_of_gate"],
        "cross_uHGF_family_gate":"NONE",
        "global_parity":"NOT_GLOBAL_PASS",
        "sha256":sha256(a.output.read_bytes()).hexdigest()
    },sort_keys=True))


if __name__=="__main__":
    main()
