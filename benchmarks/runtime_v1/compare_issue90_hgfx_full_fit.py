#!/usr/bin/env python3
"""PERF-01D: non-timed same-host FULL HGFX public fit BLAS dispatch sensitivity.

Original HGFX release v1.0.0 and MATLAB HGF 8.2.0 are unchanged. Distinct
diagnostic refits never supersede original 64-fit scientific acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

HGFX="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB="2437f4dc241541072722a2695ddeca7b44d83dd3"
BFGS_RAW={
    "hgfx_raw.json":"060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce",
    "matlab_raw.json":"4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a",
}


def read_archive(path:Path)->dict:
    summary=json.loads((path/"summary.json").read_bytes())
    if (str(summary.get("github_run_id"))!="42187240378"
            or summary.get("candidate_sha")!="5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d"
            or summary.get("raw_evidence_sha256")!=BFGS_RAW):
        raise ValueError("Immutable original BFGS scientific source/provenance changed")
    src={}
    for name,digest in BFGS_RAW.items():
        b=(path/name).read_bytes()
        if hashlib.sha256(b).hexdigest()!=digest:
            raise ValueError(f"Original archived source SHA256 changed: {name}")
        src[name.split("_")[0]]=json.loads(b)
    if src["matlab"]["status"]!="UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED":
        raise ValueError("Original MATLAB frozen reference is incomplete")
    return src


def validate_mode(raw:dict,label:str,reference:dict)->dict:
    if (raw.get("schema")!="perf01-subject7-bfgs-state-hgfx-v1"
            or raw.get("status")!="UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED"
            or raw.get("subject_index_zero_based")!=7
            or raw.get("trials")!=128
            or raw.get("source_run_id")!="41863441006"
            or raw.get("frozen_hgfx_sha")!=HGFX
            or raw.get("frozen_matlab_sha")!=MATLAB
            or raw.get("n_rand_init")!=0
            or raw.get("finite_slots")!=25
            or raw.get("ridders_min_steps")!=10
            or raw.get("original_raw_fits_verified") is not True
            or raw.get("frozen_start_matches") is not True):
        raise ValueError(f"{label}: frozen full fit workflow metadata invalid")
    if (raw.get("source_input_sha256")!=reference["source_input_sha256"]
            or raw.get("source_config_sha256")!=reference["source_config_sha256"]):
        raise ValueError(f"{label}: original data/config checksum differs")
    x=np.asarray(raw["iter_x"],np.float64)
    v=np.asarray(raw["iter_val"],np.float64)
    T=np.asarray(raw["iter_inverse_hessian"],np.float64)
    final=np.asarray(raw["final_full"],np.float64)
    grad=np.asarray([row["grad"] for row in raw["ridders_recomputed_history"]],np.float64)
    if (x.shape!=(101,3) or v.shape!=(101,)
            or T.shape!=(24,3,3) or grad.shape!=(25,3)
            or final.shape!=np.asarray(reference["final_full"],float).shape
            or not np.all(np.isfinite(T))
            or not np.all(np.isfinite(grad))
            or not np.array_equal(np.flatnonzero(np.isfinite(v)),np.arange(25))
            or not np.array_equal(np.flatnonzero(np.all(np.isfinite(x),axis=1)),np.arange(25))):
        raise ValueError(f"{label}: unexpected source history, finite masks or endpoint dimensions")
    if not np.array_equal(x[0],np.array([-3.,-6.,3.871201010907891])):
        raise ValueError(f"{label}: original start altered")
    return {"x":x, "v":v, "T":T, "final":final,"grad":grad}


def delta(a,b)->dict:
    aa=np.asarray(a,np.float64)
    bb=np.asarray(b,np.float64)
    if aa.shape!=bb.shape:
        raise ValueError("Compared frozen output shapes differ")
    masks_match=bool(np.array_equal(np.isfinite(aa),np.isfinite(bb))
            and np.array_equal(np.isnan(aa),np.isnan(bb))
            and np.array_equal(np.isposinf(aa),np.isposinf(bb))
            and np.array_equal(np.isneginf(aa),np.isneginf(bb)))
    both=np.isfinite(aa)&np.isfinite(bb)
    d=np.abs(aa[both]-bb[both])
    return {
        "shape":list(aa.shape),
        "finite_pairs":int(both.sum()),
        "nonfinite_masks_match":masks_match,
        "bitwise_value_equality":bool(np.array_equal(aa,bb,equal_nan=True)),
        "max_abs_diff":float(d.max()) if d.size else None,
        "number_nonzero_finite_coordinate_differences":int(np.count_nonzero(d)),
    }


def compare(auto:dict,haswell:dict,archive:dict)->dict:
    old=read_archive(archive)
    a=validate_mode(auto,"auto",old["matlab"])
    h=validate_mode(haswell,"Haswell",old["matlab"])
    ref=validate_mode(old["hgfx"],"archived_hgfx",old["matlab"])
    matlab=old["matlab"]
    m={
        "x":np.asarray(matlab["iter_x"],float),
        "v":np.asarray(matlab["iter_val"],float),
        "T":np.asarray(matlab["iter_inverse_hessian"],float),
        "final":np.asarray(matlab["final_full"],float),
        "grad":np.asarray([row["grad"] for row in matlab["ridders_recomputed_history"]],float),
    }
    for label,raw in (("auto",auto),("Haswell",haswell)):
        if raw["source_input_sha256"]!=old["hgfx"]["source_input_sha256"]:
            raise ValueError(f"{label}: not same source input as original archived HGFX fit")
    comparisons={}
    for name,p,q in (
        ("auto_vs_haswell",a,h),
        ("auto_vs_historical_hgfx",a,ref),
        ("haswell_vs_historical_hgfx",h,ref),
        ("auto_vs_historical_matlab",a,m),
        ("haswell_vs_historical_matlab",h,m),
        ("original_hgfx_vs_matlab",ref,m),
    ):
        comparisons[name]={key:delta(p[key],q[key]) for key in ("x","v","T","final","grad")}
    return {
        "schema":"perf01d-issue90-public-fit-dispatch-sensitivity-v1",
        "status":"AUTHOR_SIDE_UNTIMED_SAME_HOST_FULL_FIT_DIAGNOSTIC_NO_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":HGFX,
        "frozen_matlab_sha":MATLAB,
        "original_64_fit_reference_run":"41863441006",
        "original_BFGS_reference_run":"42187240378",
        "original_bfgs_raw_sha256":BFGS_RAW,
        "subject_index_zero_based":7,
        "n_trials":128,
        "model":"hgf_binary",
        "observation":"unitsq_sgm",
        "identical_archived_input_config":True,
        "source_accepted_trials_altered":False,
        "results":comparisons,
        "limitations":[
            "Both new runs reuse frozen HGFX v1.0.0 on one host; MATLAB has NOT been rerun on that same host/dispatch.",
            "Original 63/64 public MATLAB vs HGFX fitting mismatch remains NON-PASS and no new release gate decision is made.",
            "Comparisons with historical MATLAB or original HGFX are across different hosts/CI executions, not same-machine causal pairing.",
            "No data, priors, starts, optimizer thresholds, code releases or scientific sample denominators were changed.",
            "No CPU/GPU timing or speedup claim or independent approval is produced.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--auto",type=Path,required=True)
    p.add_argument("--haswell",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    auto=json.loads(args.auto.read_bytes())
    haswell=json.loads(args.haswell.read_bytes())
    result=compare(auto,haswell,args.archive)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":result["status"],
        "mode_comparison":result["results"]["auto_vs_haswell"],
        "historical_hgfx_endpoint_auto":result["results"]["auto_vs_historical_hgfx"]["final"],
        "historical_hgfx_endpoint_haswell":result["results"]["haswell_vs_historical_hgfx"]["final"],
        "historical_matlab_endpoint_auto":result["results"]["auto_vs_historical_matlab"]["final"],
        "historical_matlab_endpoint_haswell":result["results"]["haswell_vs_historical_matlab"]["final"],
    },sort_keys=True))


if __name__=="__main__":
    main()
