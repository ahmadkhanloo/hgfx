#!/usr/bin/env python3
"""PERF-01D: identical parameter vector HGFX/MATLAB forward comparison, untimed.

This separates the model-forward question from end-to-end optimizer fitting.
Three prospectively declared original vectors; ALL original 11 trialwise fields.
No scientific-gate PASS or new subject eligibility may be inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from compare_fits import numeric
from compare_trialwise import decode_tree
from scientific_preflight import decode_number

HGFX_SHA="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA="2437f4dc241541072722a2695ddeca7b44d83dd3"
SOURCE="41863441006"
RAW={
    "hgfx_raw.json":"6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb",
    "matlab_raw.json":"2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98",
}
ANCHORS=("original_hgfx_fitted_endpoint","original_matlab_fitted_endpoint",
         "original_frozen_start")
FIELDS={"mu","muhat","sa","sahat","da","epsi","psi","ud","v","w","wt"}
RTOL,ATOL=3e-8,3e-10


def validate_source(root:Path)->tuple[dict,dict,dict]:
    summary=json.loads((root/f"summary-{SOURCE}.json").read_bytes())
    if (str(summary.get("github_run_id"))!=SOURCE
            or summary.get("hgfx_sha")!=HGFX_SHA
            or summary.get("matlab_sha")!=MATLAB_SHA
            or summary.get("classification_counts")!={
                "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1,
                "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
            } or summary.get("subject_count")!=64
            or summary["cases"][7]["mismatched_fields"]!=["traj.mu","traj.muhat"]):
        raise ValueError("Original all-64 scientific NONPASS provenance changed")
    originals={}
    for name,hashval in RAW.items():
        if summary["raw_evidence_sha256"][name]!=hashval:
            raise ValueError("Original historical SHA manifest changed: "+name)
        b=(root/name).read_bytes()
        if hashlib.sha256(b).hexdigest()!=hashval:
            raise ValueError("Archived original raw source changed: "+name)
        data=json.loads(b)
        if len(data["cases"])!=64:
            raise ValueError("Original public fit cohort is incomplete")
        key=name.split("_")[0]
        originals[key]=data["cases"][7]
        if (originals[key]["subject_index_zero_based"]!=7
                or originals[key]["n_rand_init"]!=0
                or not originals[key]["start_matches_frozen_snapshot"]
                or originals[key]["status"]!=
                    key.upper()+"_FULL_FIT_COMPLETED_NO_PARITY_DECISION"):
            raise ValueError("Original subject 7 public fitting source altered")
    return summary,originals["hgfx"],originals["matlab"]


def anchors(root:Path,h:dict,m:dict)->dict:
    config=json.loads((root/"configs"/"hgf_binary_128.json").read_bytes())
    initial=np.array([decode_number(v) for v in config["transformed_start_full"]],float)
    if (initial.shape!=(15,) or config["fit_free_indices_0based"]!=[12,13,14]
            or len(config["perceptual"]["parameters"])!=14
            or len(config["observation"]["parameters"])!=1
            or not np.array_equal(initial,np.asarray(h["optim"]["init"],float),equal_nan=True)
            or not np.array_equal(initial,np.asarray(m["optim"]["init"],float),equal_nan=True)):
        raise ValueError("Original transformed full-vector initial/start policy changed")
    return {
        "original_hgfx_fitted_endpoint":np.asarray(h["optim"]["final"],float),
        "original_matlab_fitted_endpoint":np.asarray(m["optim"]["final"],float),
        "original_frozen_start":initial,
    }


def verify_raw(raw:dict,engine:str,summary:dict,params:dict)->dict:
    canonical=summary["raw_evidence_sha256"]
    hashes=raw.get("original_raw_sha256")
    if engine=="matlab" and isinstance(hashes,dict):
        hashes={k.replace("_raw_json","_raw.json"):v for k,v in hashes.items()}
    if (raw.get("schema")!=f"perf01d-subject7-crossed-forward-{engine}-v1"
            or raw.get("status")!="SAME_VECTOR_FORWARD_DIAGNOSTIC_NO_FULL_FIT_NO_TIMING_NO_SCIENTIFIC_PASS"
            or raw.get("frozen_hgfx_sha")!=HGFX_SHA
            or raw.get("frozen_matlab_sha")!=MATLAB_SHA
            or str(raw.get("source_run_id"))!=SOURCE
            or hashes!=canonical
            or raw.get("source_input_sha256")!=summary["hgfx_input_sha256"]
            or raw.get("source_config_sha256")!=summary["hgfx_config_sha256"]
            or raw.get("subject_index_zero_based")!=7
            or raw.get("trials")!=128
            or raw.get("model")!="hgf_binary"
            or raw.get("perceptual_parameter_count")!=14
            or raw.get("observation_parameter_count")!=1
            or raw.get("free_indices_zero_based")!=[12,13,14]
            or raw.get("anchor_origins")!=list(ANCHORS)
            or raw.get("original_endpoints_unmodified") is not True):
        raise ValueError(f"Unverified original shared-vector source for {engine}")
    cases=raw.get("cases")
    if (not isinstance(cases,list) or len(cases)!=3
            or [c["origin"] for c in cases]!=list(ANCHORS)):
        raise ValueError(f"Changed {engine} anchor denominator/order")
    result={}
    for c in cases:
        anchor=c["origin"]
        x=np.asarray(decode_tree(c["full_transformed_vector"]),float)
        if (not np.array_equal(x,params[anchor],equal_nan=True)
                or c.get("status")!=f"EVALUATED_IDENTICAL_FROZEN_VECTOR_{engine.upper()}"
                or set(c["traj"])!=FIELDS):
            raise ValueError(f"{engine} did not evaluate exactly original transformed {anchor}")
        for k in FIELDS:
            if np.asarray(decode_tree(c["traj"][k]),float).shape!=((128,2) if k=="w" else (128,3)):
                raise ValueError(f"{engine} full HGF trialwise field shape changed: {k}")
        if np.asarray(decode_tree(c["inf_states"]),float).shape!=(128,3,4):
            raise ValueError(f"{engine} original forward inference state shape changed")
        result[anchor]=c
    return result


def mismatch_points(left,right)->list[dict]:
    x=np.asarray(decode_tree(left),float)
    y=np.asarray(decode_tree(right),float)
    if x.shape!=y.shape:
        raise ValueError("Cannot locate matched-vector mismatch positions across shape difference")
    bad=np.argwhere(~np.isclose(x,y,rtol=RTOL,atol=ATOL,equal_nan=True))
    points=[]
    for i,j in bad:
        points.append({
            "trial_one_based":int(i)+1,
            "level_one_based":int(j)+1,
            "index_zero_based":[int(i),int(j)],
            "hgfx_value":float(x[i,j]),
            "matlab_value":float(y[i,j]),
            "absolute_difference":float(abs(x[i,j]-y[i,j])),
            "unchanged_reference_bound":float(ATOL+RTOL*abs(y[i,j])),
        })
    return points


def compare_traj(a:dict,b:dict)->dict:
    if set(a)!=FIELDS or set(b)!=FIELDS:
        raise ValueError("Full original model trajectory field inventory lost")
    fields={name:numeric(a[name],b[name],RTOL,ATOL) for name in sorted(FIELDS)}
    mismatches=sorted(name for name,entry in fields.items()
                      if entry["status"]!="WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE")
    points={name:mismatch_points(a[name],b[name]) for name in ("mu","muhat")}
    for name in points:
        if len(points[name])!=fields[name]["mismatch_count"]:
            raise ValueError(f"Missing complete trialwise {name} mismatch coordinates")
    return {
        "field_count":len(fields),
        "fields":fields,
        "mismatched_fields":mismatches,
        "critical_coordinates":points,
        "status":("SOURCE_MATCHED_FORWARD_WITHIN_ORIGINAL_NUMERIC_TOLERANCES_DIAGNOSTIC_ONLY"
                  if not mismatches else "SOURCE_MATCHED_FORWARD_NUMERIC_MISMATCH_DIAGNOSTIC_ONLY"),
    }


def compare(h:dict,m:dict,original:Path,input_root:Path)->dict:
    summary,old_h,old_m=validate_source(original)
    params=anchors(input_root,old_h,old_m)
    hs=verify_raw(h,"hgfx",summary,params)
    ms=verify_raw(m,"matlab",summary,params)
    internal_checks={
        "hgfx_at_original_hgfx_endpoint_vs_original_hgfx_full_fit":
            compare_traj(hs[ANCHORS[0]]["traj"],old_h["traj"]),
        "matlab_at_original_matlab_endpoint_vs_original_matlab_full_fit":
            compare_traj(ms[ANCHORS[1]]["traj"],old_m["traj"]),
    }
    if any(v["mismatched_fields"] for v in internal_checks.values()):
        raise ValueError("Same-vector source API did not reproduce original respective full public fit; fail closed")
    cross={}
    for name in ANCHORS:
        cross[name]=compare_traj(hs[name]["traj"],ms[name]["traj"])
        cross[name]["inference_states"]=numeric(hs[name]["inf_states"],ms[name]["inf_states"],
                                                 RTOL,ATOL)
    prior=compare_traj(old_h["traj"],old_m["traj"])
    if (prior["mismatched_fields"]!=["mu","muhat"]
            or prior["fields"]["mu"]["mismatch_count"]!=4
            or prior["fields"]["muhat"]["mismatch_count"]!=4):
        raise ValueError("Original failed complete-fitting trajectory status was not preserved")
    return {
        "schema":"perf01d-subject7-crossed-same-vector-trialwise-report-v1",
        "status":"AUTHOR_SIDE_FORWARD_SOURCE_ISOLATION_NOT_PUBLIC_FIT_PASS_NOT_TIMED",
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run_id":SOURCE,
        "original_raw_sha256":RAW,
        "subject_index_zero_based":7,
        "trials":128,
        "model":"hgf_binary",
        "anchor_origins":list(ANCHORS),
        "unchanged_original_numeric_tolerances":{"rtol":RTOL,"atol":ATOL},
        "original_scientific_failure":"63/64 full public fits; subject 7 traj.mu and traj.muhat non-PASS",
        "reproduces_each_engine_original_full_fit_at_its_own_endpoint":internal_checks,
        "full_source_matched_vector_cross_engine_trajectories":cross,
        "original_public_fit_traj_cross_engine":prior,
        "limitations":[
            "Matched-vector forward equality is IMPLEMENTATION PARITY for isolated forward calculation, not full optimizer/published scientific fitting parity.",
            "Original 64 subject PUBLIC fitting 63/64 NON-PASS is unchanged.",
            "Original full fit endpoints are different; same-vector forward probes intentionally remove optimizer path as a variable.",
            "MATLAB reference 8.2.0 and HGFX 1.0.0 sources, original data/priors, all three vectors and unchanged tolerances are preserved.",
            "Three anchors predeclared by frozen history; no retrospective exclusion or threshold change.",
            "No timing, physical GPU results, external independent review or paper-ready speedup.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("hgfx","matlab","original","input","output"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    result=compare(
        json.loads(args.hgfx.read_bytes()),
        json.loads(args.matlab.read_bytes()),
        args.original,args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":result["status"],
        "public_fit_original_mismatch":result["original_public_fit_traj_cross_engine"]["mismatched_fields"],
        "same_vector_cross_mismatch":{
            name:v["mismatched_fields"]
            for name,v in result["full_source_matched_vector_cross_engine_trajectories"].items()},
        "same_vector_cross_critical_counts":{
            name:{k:len(points) for k,points in item["critical_coordinates"].items()}
            for name,item in result["full_source_matched_vector_cross_engine_trajectories"].items()},
        "self_source_reproduction":{
            k:v["mismatched_fields"]
            for k,v in result["reproduces_each_engine_original_full_fit_at_its_own_endpoint"].items()},
    },sort_keys=True))


if __name__=="__main__":
    main()
