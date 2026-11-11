#!/usr/bin/env python3
"""Read-only original three-archive D08 audit. NO hgfx/JAX/MATLAB/model imports.

Predeclared: evidence/revision/protocols/REV-2.2_D08_THREE_ARCHIVE_READONLY_PROTOCOL_2026-11-11.md.
Never silently rebuild, select, overwrite or expand any scientific run.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

ARCHIVES={
 "historical":{
  "sha":"c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de",
  "members":{
   "m18_d08_endpoint.json":"d6c0182e60bdc3c418df533cf1f0077bd45114fb9df33cbcae248399f52448c2",
   "m18_d08_endpoint_comparison.json":"f112129c29c36d208042fe9215b16147bedfd69a796a50a18fac59df4c25b409",
  }},
 "A":{
  "sha":"a2864f8729d9e856eb3454cf1fbf4c26c08cd217695e58b79950cec2ac5b3534",
  "members":{
   "hgfx_published_wheel.json":"d06a2f961a27f73a9c38621a86fe2204aebb481f2857ce45368e176111a9f37d",
   "matlab_reference.json":"5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165",
   "matlab_cross_evaluation.json":"8bdcad1f1c2c6bc628eb6622c258188343025136df9a345e7fb2a84da5d9f9b9",
   "paired_d08_comparison.json":"0304d8366c497d1e03cf9b75da1670a8a2d09e06979c064098cdd4e062595440",
  }},
 "B":{
  "sha":"ea577dc80b2194d1658eeb8c296a021f51332199be0ea7d4924608fe12891132",
  "members":{
   "hgfx_released_fit.json":"202fb1ab5177d39c6104c9a5004057fc19ae58637e706b0459ea48aa3bc27b13",
   "matlab_reference.json":"5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165",
   "matlab_cross_endpoints.json":"4228c9232ef51a724faa0773477b158935b2004dbd3c09bec89a1ca5d7478842",
   "rev22_comparison.json":"eb8f598158d057df0c574fd0cd188bed629ff13c7e40fbcde24627daebac5422",
  }}
}
RTOL=3e-8
ATOL=3e-10
TRAJECTORIES=frozenset(("mu","sa","muhat","sahat","v","w","da","dau","ud","psi","epsi","wt"))
OLD="m18-d08-endpoint-diagnostic-2"
NEW="compstat-rev2-2-d08-original-oracle-v1"
REFERENCE_COMMIT="2437f4dc241541072722a2695ddeca7b44d83dd3"
WHEEL="5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90"


def require(ok,reason):
    if not ok:raise ValueError(reason)


def hash_bytes(raw):
    return sha256(raw).hexdigest()


def read_original_zip(path,identity):
    raw=path.read_bytes()
    record=ARCHIVES[identity]
    require(hash_bytes(raw)==record["sha"],identity+" archive SHA drift")
    with ZipFile(path) as z:
        require(set(z.namelist())==set(record["members"]),identity+" archive members changed")
        out={}
        for member,digest in record["members"].items():
            data=z.read(member)
            require(hash_bytes(data)==digest,identity+"/"+member+" SHA drift")
            out[member]=json.loads(data)
    return out


def f64(data):
    if isinstance(data,dict) and data.get("hgfx_numeric")=="ieee-strings-v1":
        shape=tuple(int(i) for i in data["shape"])
        values=np.array(data["data"],dtype=np.float64)
        require(int(np.prod(shape))==values.size,"Malformed MATLAB column-major array")
        return values.reshape(shape,order="F")
    return np.asarray(data,dtype=np.float64)


def arrays_identical(a,b):
    x=f64(a);y=f64(b)
    if x.shape!=y.shape and x.size==y.size and (x.ndim==1 or y.ndim==1):
        x=x.reshape(-1);y=y.reshape(-1)
    return bool(x.shape==y.shape and np.array_equal(x,y,equal_nan=True))


def paired_status(a,b):
    x=f64(a);y=f64(b)
    if x.shape!=y.shape and x.size==y.size and (x.ndim==1 or y.ndim==1):
        x=x.reshape(-1);y=y.reshape(-1)
    require(x.shape==y.shape,"Same-vector trajectory shape mismatch")
    statuses=(np.isnan(x)==np.isnan(y)) & (np.isposinf(x)==np.isposinf(y)) & (np.isneginf(x)==np.isneginf(y))
    finite=np.isfinite(x)&np.isfinite(y)
    bad=~statuses
    with np.errstate(invalid="ignore",over="ignore"):
        delta=np.abs(x-y)
        bad=bad | (finite & (delta > ATOL + RTOL*np.abs(x)))
    coords=[list(map(int,k)) for k in np.argwhere(bad)]
    valid_diff=delta[finite]
    return {
        "shape":list(x.shape),
        "n_values":int(x.size),
        "nonfinite_status_differences":int(np.count_nonzero(~statuses)),
        "out_of_existing_numeric_yardstick":len(coords),
        "bad_zero_based_coordinates":coords,
        "max_absolute_difference_on_finite_pairs":float(valid_diff.max()) if valid_diff.size else None,
        "rtol_descriptive_existing_M18":RTOL,
        "atol_descriptive_existing_M18":ATOL,
        "scientific_family_gate":"NO_PREDECLARED_UHGF_SAME_VECTOR_GATE",
    }


def audit(historical_path,run_a_path,run_b_path):
    h=read_original_zip(historical_path,"historical")
    a=read_original_zip(run_a_path,"A")
    b=read_original_zip(run_b_path,"B")
    older=h["m18_d08_endpoint.json"]
    prior=h["m18_d08_endpoint_comparison.json"]
    m=a["matlab_reference.json"]
    mb=b["matlab_reference.json"]
    require(m==mb,"Original MATLAB reference must be structurally identical A/B")
    require(older["protocol"]==prior["protocol"]==OLD and
            m["protocol"]==NEW and m["seed"]==older["seed"]==123456789,
            "Mixed original seed or protocol")
    require(older["reference_commit"]==m["reference_commit"]==REFERENCE_COMMIT,
            "Wrong historical MATLAB source")
    require("R2026a" in older["matlab_version"] and "R2026b" in m["matlab_version"],
            "Historical/current MATLAB runtime version not as documented")
    require(m["trials"]==614 and
            all(arrays_identical(older[k],m[k]) for k in ("inputs","responses","final")),
            "Official inputs, simulated responses or MATLAB result changed")
    old_trace=older["trace"]
    new_trace=m["iter"]
    require(arrays_identical(old_trace["x"],new_trace["x"]) and
            arrays_identical(old_trace["val"],new_trace["val"]) and
            arrays_identical(old_trace["rst"],new_trace["rst"]),
            "MATLAB historical vs new BFGS trace differs")
    require(f64(old_trace["x"]).shape==(101,7) and
            f64(old_trace["val"]).size==101,
            "Original 101x7 trace shape changed")
    first=prior["optimizer_trace"]["first_exact_x_difference"]
    require(first["index"]==[3,0] and
            float(first["abs_diff"])==3.552713678800501e-15 and
            prior["optimizer_trace"]["first_gate_x_difference"] is None and
            prior["optimizer_trace"]["first_exact_rst_difference"] is None,
            "Historical earlier source-comparator trace result altered")
    require(float(f64(old_trace["x"])[3,0])==float(first["matlab"]),
            "Historical MATLAB row 3 first-exact difference not source grounded")
    rowdata={}
    for name,source,fit_name,cross_name,cmp_name,n_bad in (
        ("A",a,"hgfx_published_wheel.json","matlab_cross_evaluation.json",
         "paired_d08_comparison.json",4),
        ("B",b,"hgfx_released_fit.json","matlab_cross_endpoints.json",
         "rev22_comparison.json",3),
    ):
        fit=source[fit_name];cross=source[cross_name];cmp=source[cmp_name]
        require(fit["protocol"]==cross["protocol"]==cmp["protocol"]==NEW
                and fit["wheel_sha256"]==WHEEL
                and fit["source"]=="hgfx"
                and cross["source"]=="matlab_cross"
                and cmp["classification"]=="UNRESOLVED_DISCREPANCY"
                and cmp["scientific_global_parity"]=="NOT_GLOBAL_PASS",
                name+": source result/status drift")
        require(fit["runtime"]["installed_hgfx"]=="1.0.0" and
                fit["runtime"]["numpy"]=="2.0.2" and
                fit["runtime"]["jax"]=="0.10.2",
                name+": installed runtime not same frozen public Wheel")
        require("iter" not in fit and fit["termination"]=="NOT_EXPORTED",
                name+": HGFX stepwise numerical history unexpectedly present")
        require(cross["hgfx_endpoint"]["valid"],name+": MATLAB cross endpoint invalid")
        traj_mat=cross["hgfx_endpoint"]["traj"]
        traj_hg=fit["traj"]
        require(set(traj_mat)==set(traj_hg)==TRAJECTORIES,
                name+": one of the 12 trajectory fields omitted")
        all_checks={key:paired_status(traj_mat[key],traj_hg[key])
                    for key in sorted(TRAJECTORIES)}
        require(all(not metric["out_of_existing_numeric_yardstick"]
                    and not metric["nonfinite_status_differences"]
                    for metric in all_checks.values()),
                name+": same-vector trajectory difference exceeds old yardstick")
        ownfit=paired_status(m["traj"]["epsi"],fit["traj"]["epsi"])
        require(ownfit["out_of_existing_numeric_yardstick"]==n_bad and
                cmp["first_direct_out_of_gate"]["field"]=="traj.epsi",
                name+": original published own-endpoint epsi failure altered")
        origin=[k[0] for k in ownfit["bad_zero_based_coordinates"]]
        require(origin==([178,322,412,577] if name=="A" else [178,412,577]),
                name+": original discrepancy trial locations changed")
        cross_raw={}
        for endpoint in ("matlab_endpoint","hgfx_endpoint"):
            for obj in ("negLj","negLl"):
                cv=float(cross[endpoint][obj])
                hv=float(fit["objectives"][endpoint][obj])
                cross_raw[endpoint+"."+obj+".absolute_gap"]=abs(cv-hv)
        samevector=all_checks["epsi"]
        rowdata[name]={
            "science_source_run":42910756224 if name=="A" else 42910835710,
            "source_artifact":13808150860 if name=="A" else 13808625206,
            "runtime":fit["runtime"],
            "original_own_fit_eps_out_of_gate":n_bad,
            "original_own_fit_eps_bad_indices_zero_based":ownfit["bad_zero_based_coordinates"],
            "same_HGFX_endpoint_trajectory_fields":all_checks,
            "same_HGFX_endpoint_all_12_fields_within_old_numeric_yardstick":True,
            "same_HGFX_endpoint_eps_max_absolute_diff":
                samevector["max_absolute_difference_on_finite_pairs"],
            "same_vector_objective_absolute_gaps_descriptive_only":cross_raw,
            "full_HGFX_optimizer_trace_saved":False,
        }
    fitted_a=f64(a["hgfx_published_wheel.json"]["final"]).reshape(-1)
    fitted_b=f64(b["hgfx_released_fit.json"]["final"]).reshape(-1)
    require(fitted_a.shape==fitted_b.shape and not np.array_equal(fitted_a,fitted_b),
            "Original A/B non-bitwise identical fitted parameters lost")
    return {
        "protocol":"REV22_D08_THREE_ARCHIVE_ORIGINAL_READONLY_2026_11_11",
        "archived_scientific_fits_executed_by_this_audit":0,
        "original_source_artifact_SHA256":{k:ARCHIVES[k]["sha"] for k in ("historical","A","B")},
        "original_historical_M18_matlab_version":older["matlab_version"],
        "original_new_MATLAB_version":m["matlab_version"],
        "original_MATLAB_614_inputs_responses_final_and_101x7_optimizer_trace_bitwise_equal_across_versions":True,
        "historical_reported_first_exact_HGFX_vs_MATLAB_optimizer_x":
            first,
        "historical_original_HGFX_vs_MATLAB_optimizer_trace_gate_difference":None,
        "no_new_HGFX_stepwise_BFGS_or_Ridders_trace_saved":True,
        "cannot_establish_first_new_run_BFGS_decision":True,
        "A_B_max_abs_fitted_parameter_difference":
            float(np.max(np.abs(fitted_a-fitted_b))),
        "run_results":rowdata,
        "same_vector_numeric_check_descriptive_only":True,
        "no_frozen_uhgf_family_scientific_parity_gate":True,
        "new_direct_fit_classification":"UNRESOLVED_DISCREPANCY",
        "concurrent_dual_run_protocol_deviation":"RETAINED_NOT_PREDECLARED_REPLICATES",
        "historic_M18_D08_FAIL":"PRESERVED",
        "REV24_global":"NOT_GLOBAL_PASS",
        "D2_D3":"BLOCKED",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical",required=True,type=Path)
    parser.add_argument("--run-a",required=True,type=Path)
    parser.add_argument("--run-b",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    require(not a.output.exists(),"Immutable source-only audit output must not be overwritten")
    result=audit(a.historical,a.run_a,a.run_b)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",
                        encoding="utf-8")
    print(json.dumps({
       "classification":result["new_direct_fit_classification"],
       "historical_101x7_MATLAB_BFGS_trace_bitwise_equal":True,
       "same_endpoint_12_trajectory_fields_A":True,
       "same_endpoint_12_trajectory_fields_B":True,
       "A_own_fit_out_of_gate":4,"B_own_fit_out_of_gate":3,
       "HGFX_new_full_BFGS_trace_available":False,
       "global_gate":"NOT_GLOBAL_PASS",
       "sha256":hash_bytes(a.output.read_bytes()),
    },sort_keys=True))


if __name__=="__main__":main()
