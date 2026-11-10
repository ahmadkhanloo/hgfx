#!/usr/bin/env python3
"""Independent read-only audit of the single immutable REV-2.2 D08 artifact.

Checks archive SHA-256 and all four member hashes BEFORE reading values.
Recomputes field-wise frozen gates and same-vector objective observations
without importing MATLAB, HGFX, model code, JAX, or optimizer functions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

ARTIFACT_SHA="a2864f8729d9e856eb3454cf1fbf4c26c08cd217695e58b79950cec2ac5b3534"
FILES={
    "matlab_reference.json":"5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165",
    "hgfx_published_wheel.json":"d06a2f961a27f73a9c38621a86fe2204aebb481f2857ce45368e176111a9f37d",
    "matlab_cross_evaluation.json":"8bdcad1f1c2c6bc628eb6622c258188343025136df9a345e7fb2a84da5d9f9b9",
    "paired_d08_comparison.json":"0304d8366c497d1e03cf9b75da1670a8a2d09e06979c064098cdd4e062595440",
}
PREFIX="compstat-rev2-2-d08-original-oracle-v1"


def check(ok,msg):
    if not ok:raise ValueError(msg)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def numeric(v):
    if isinstance(v,dict):
        check(v.get("hgfx_numeric")=="ieee-strings-v1","Unknown MATLAB IEEE transport")
        vals=np.array([float(x) for x in v["data"]],dtype=np.float64)
        shp=tuple(v["shape"])
        check(int(np.prod(shp))==len(vals),"Malformed MATLAB column-major matrix")
        return vals.reshape(shp,order="F")
    return np.asarray(v,dtype=np.float64)


def read_zip(p:Path):
    raw=p.read_bytes()
    check(sha(raw)==ARTIFACT_SHA,"Original science archive SHA-256 drift")
    with ZipFile(p) as z:
        check(set(z.namelist())==set(FILES),"Archive members changed or omitted")
        blobs={}
        for name,digest in FILES.items():
            data=z.read(name)
            check(sha(data)==digest,"Original science member hash mismatch: "+name)
            blobs[name]=json.loads(data)
    return blobs


def validate(p):
    z=read_zip(p)
    m=z["matlab_reference.json"]
    h=z["hgfx_published_wheel.json"]
    c=z["matlab_cross_evaluation.json"]
    prev=z["paired_d08_comparison.json"]
    check({m["protocol"],h["protocol"],c["protocol"],prev["protocol"]}=={PREFIX},
          "Mixing different experiments")
    check((m["source"],h["source"],c["source"])==
          ("matlab","hgfx","matlab_cross"),"Wrong source ordering")
    check(m["seed"]==h["seed"]==c["seed"]==123456789,"Seed drift")
    check(m["trials"]==h["trials"]==c["trials"]==614,
          "Response horizon changed")
    check(m["model"]==h["model"]==c["model"]=="uhgf"
          and m["observation_model"]==h["observation_model"]==
              c["observation_model"]=="gaussian_obs",
          "Not authentic D08 model family")
    check(h["wheel_sha256"]==
          "5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90",
          "Changed published Wheel")
    inp=numeric(m["inputs"]).reshape(-1)
    y=numeric(m["responses"]).reshape(-1)
    check(inp.shape==y.shape==(614,) and np.isfinite(inp).all()
          and np.isfinite(y).all(),"Original 614 responses missing")
    check(sha(np.asarray(inp,dtype="<f8").tobytes())==h["inputs_f64_sha256"]
          and sha(np.asarray(y,dtype="<f8").tobytes())==h["responses_f64_sha256"],
          "Matched response/input IEEE binary64 digests disagree")
    # Fully independent of the original postprocessor:
    fields=[("initial_transformed","init","initial"),
            ("final_transformed","final","final"),
            ("native_fit_perceptual","native_fit_perceptual","native_fit_perceptual"),
            ("native_fit_observation","native_fit_observation","native_fit_observation"),
            ("negative_log_likelihood","negLl","negLl"),
            ("negative_log_joint","negLj","negLj"),
            ("BIC","BIC","BIC"),("LME","LME","LME"),("H","H","H"),
            ("Sigma","Sigma","Sigma"),("Corr","Corr","Corr"),
            ("prediction","yhat","yhat"),("residual","res","res")]
    for key in sorted(set(m["traj"])|set(h["traj"])):
        check(key in m["traj"] and key in h["traj"],
              "No trajectory field may be silently excluded: "+key)
        fields.append(("traj."+key,("traj",key),("traj",key)))
    failures=[]
    field_summary=[]
    epsi_bad=None
    for name,mname,hname in fields:
        def get(src,key):
            if isinstance(key,tuple):return src[key[0]][key[1]]
            return src[key]
        a=numeric(get(m,mname));b=numeric(get(h,hname))
        if a.shape!=b.shape and a.size==b.size and a.ndim<=2 and b.ndim<=2 \
            and (a.ndim==1 or b.ndim==1):
            a=a.reshape(-1);b=b.reshape(-1)
        check(a.shape==b.shape,"Field shape mismatch: "+name)
        rtol,atol=((2e-6,2e-8) if name in ("H","LME")
                   else (5e-6,5e-8) if name in ("Sigma","Corr")
                   else (3e-8,3e-10))
        same_status=(np.isnan(a)==np.isnan(b))&(
            np.isposinf(a)==np.isposinf(b))&(
            np.isneginf(a)==np.isneginf(b))
        both=np.isfinite(a)&np.isfinite(b)
        diff=np.zeros_like(a,dtype=bool)
        diff[both]=np.abs(a[both]-b[both])>(atol+rtol*np.abs(a[both]))
        bad=~same_status|diff
        bad_count=int(np.count_nonzero(bad))
        field_summary.append({"field":name,"number":int(a.size),
                              "outside_frozen_gate":bad_count,
                              "status_disagreement":int((~same_status).sum())})
        if bad_count:failures.append(name)
        if name=="traj.epsi":
            coords=[tuple(int(x) for x in idx) for idx in np.argwhere(bad)]
            epsi_bad={"bad_trial_level_indices_zero_based":coords,
                      "first_matlab":float(a[coords[0]]),
                      "first_hgfx":float(b[coords[0]]),
                      "maximum_absolute_difference":float(np.max(np.abs(a-b)))}
    check(len(fields)==25 and failures==["traj.epsi"],
          "Independently observed direct failing field mismatch")
    check(epsi_bad["bad_trial_level_indices_zero_based"]==
          [(178,1),(322,1),(412,1),(577,1)],
          "Filing count/locations changed")
    for endpoint in ("matlab_endpoint","hgfx_endpoint"):
        for key in ("negLl","negLj"):
            ma=float(c[endpoint][key])
            py=float(h["objectives"][endpoint][key])
            check(ma==py,"Reported cross aggregate no longer equal: "+endpoint+"."+key)
    for key in ("negLl","negLj"):
        check(float(c["matlab_endpoint"][key])==float(m[key]),
              "MATLAB self objective discrepancy or changed reference")
    check(prev["classification"]=="UNRESOLVED_DISCREPANCY"
          and prev["direct_existing_scope_pass"] is False
          and prev["cross_family_objective_pass"]=="NO_PREDECLARED_UHGF_FAMILY_GATE"
          and prev["scientific_global_parity"]=="NOT_GLOBAL_PASS",
          "Unjustified historic success/reclassification")
    check(prev["first_direct_out_of_gate"]["field"]=="traj.epsi"
          and prev["first_direct_out_of_gate"]["first_bad_flat_index"]==357,
          "Original first failing field/index changed")
    return {
        "audit":"REV22_D08_ARCHIVED_READ_ONLY_INDEPENDENT",
        "science_executions":0,
        "source_run_id":42910756224,
        "source_artifact_id":13808150860,
        "zip_sha256":ARTIFACT_SHA,
        "member_sha256":FILES,
        "n_fixed_cases":1,
        "trials":614,
        "responses_identical_binary64":True,
        "all_25_fields_checked":len(fields),
        "fields_passing_frozen_direct_gate":sum(
            x["outside_frozen_gate"]==0 for x in field_summary),
        "fields_failing_frozen_direct_gate":failures,
        "field_counts":field_summary,
        "epsi_original_violations":epsi_bad,
        "cross_same_vector_aggregate_objectives_equal_at_both_original_endpoints":True,
        "cross_family_uHGF_objective_gate":"NOT_PREDECLARED",
        "matlab_hessian_positive_definite":prev["hessian_reference"]["positive_definite"],
        "hgfx_hessian_positive_definite":prev["hessian_hgfx"]["positive_definite"],
        "matlab_hessian_condition_2":prev["hessian_reference"]["condition_2"],
        "hgfx_hessian_condition_2":prev["hessian_hgfx"]["condition_2"],
        "new_scientific_classification":"UNRESOLVED_DISCREPANCY",
        "historical_original_d08_failure_overwritten":False,
        "rev24_global_parity":"NOT_GLOBAL_PASS",
        "D2_D3":"BLOCKED",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    check(not a.output.exists(),"Refuse to overwrite archived audit")
    data=validate(a.archive)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "read_only_audit":"PASS",
        "fields":data["all_25_fields_checked"],
        "failing_fields":data["fields_failing_frozen_direct_gate"],
        "epsi_cases":data["epsi_original_violations"]["bad_trial_level_indices_zero_based"],
        "cross_aggregate_equal":True,
        "global_science":"NOT_GLOBAL_PASS",
        "output_sha256":sha(a.output.read_bytes())
    },sort_keys=True))


if __name__=="__main__":main()
