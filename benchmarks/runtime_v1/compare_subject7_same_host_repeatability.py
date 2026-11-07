#!/usr/bin/env python3
"""PERF-01D / Issue #90: untimed 4-process A-B-B-A fixed-runner diagnostics.

No retrospective change to original full-fitting NON-PASS (63/64).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from compare_fits import TOLS
from compare_trialwise import decode_tree
from compare_subject7_full_fit_trajectories import (
    HGFX_SHA, MATLAB_SHA, BASE_RUN, load_original, validate_new, compare_pair
)

ORDER = ("auto_1", "Haswell_1", "Haswell_2", "auto_2")
STATUS = "AUTHOR_SIDE_ABBA_REPEATABILITY_DIAGNOSTIC_ONLY_ORIGINAL_63_OF_64_NONPASS"

def _mode(name):
    return "auto" if name.startswith("auto_") else "Haswell"

def fields(case):
    values = {k:case["optim"][k] for k in TOLS}
    values.update({"decompLME."+k:case["optim"]["decompLME"][k]
                   for k in ("logjoint","postpredcorr","freepars")})
    values.update({"traj."+k:v for k,v in case["traj"].items()})
    if len(values) != 28:
        raise ValueError("Original full 28-field output inventory incomplete")
    return values

def strict_pair(a,b):
    """Compare all 28 values as serialized float64, not via a tolerance."""
    aa,bb=fields(a),fields(b)
    if set(aa) != set(bb):
        raise ValueError("Original 28-field inventory differs")
    reports={}
    for name in sorted(aa):
        x=np.asarray(decode_tree(aa[name]),dtype=np.float64)
        y=np.asarray(decode_tree(bb[name]),dtype=np.float64)
        if x.shape != y.shape:
            raise ValueError("Original output shapes differ: "+name)
        equal=x.view(np.uint64)==y.view(np.uint64)
        pair=np.isfinite(x)&np.isfinite(y)
        diff=np.abs(x[pair]-y[pair])
        reports[name]={"shape":list(x.shape),
                       "serialized_binary64_equal":bool(np.all(equal)),
                       "differing_serialized_binary64_values":int(np.count_nonzero(~equal)),
                       "max_finite_abs_diff":float(diff.max()) if diff.size else None,
                       "finite_mask_equal":bool(np.array_equal(np.isfinite(x),np.isfinite(y)))}
    return {"field_count":len(reports),
            "all_serialized_binary64_equal":all(v["serialized_binary64_equal"] for v in reports.values()),
            "fields":reports,
            "caveat":"Parsed JSON float64, not raw in-memory NaN payloads"}

def validate_environment(env):
    if set(env)!=set(ORDER):
        raise ValueError("All four predeclared ABBA processes required")
    first=env["auto_1"]
    fixed=("run_id","github_sha","platform","machine","linux_cpu_model",
           "numpy","python","affinity","openblas_threads","cpu_set_requested","jax_platforms")
    if (first.get("numpy")!="2.3.5" or first.get("jax_platforms")!="cpu"
            or first.get("openblas_threads")!=4
            or len(first.get("affinity",[]))!=4
            or first["cpu_set_requested"]!=first["affinity"]):
        raise ValueError("Missing original matched four-core CPU control")
    for name in ORDER:
        row=env[name]
        if any(row.get(k)!=first.get(k) for k in fixed):
            raise ValueError("Same-runner provenance/affinity mismatch: "+name)
        if row.get("mode")!=_mode(name) or not row.get("raw_sha256"):
            raise ValueError("ABBA mode/checksum mismatch: "+name)
        requested=None if _mode(name)=="auto" else "Haswell"
        if row.get("openblas_coretype")!=requested:
            raise ValueError("Incorrect OpenBLAS requested dispatch: "+name)
        effective="SkylakeX" if _mode(name)=="auto" else "Haswell"
        if not any(p.get("internal_api")=="openblas" and p.get("architecture")==effective
                   and p.get("num_threads")==4 and p.get("version")=="0.3.30"
                   for p in row.get("pools",[])):
            raise ValueError("Effective OpenBLAS mode/thread/version not verified: "+name)
    if not str(first.get("run_id","")).isdigit():
        raise ValueError("No run identifier")
    return {"run_id":first["run_id"],"code_sha":first["github_sha"],
            "same_runner_affinity_verified":True,"order":list(ORDER)}

def derive(original,outputs,environment):
    summary,old_h,old_m=load_original(original)
    env=json.loads(environment.read_bytes())
    host=validate_environment(env)
    fresh={}
    for name in ORDER:
        raw=(outputs/(name+"_raw.json")).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=env[name]["raw_sha256"]:
            raise ValueError("Fresh evidence SHA256 mismatch: "+name)
        fresh[name]=validate_new(json.loads(raw),_mode(name),summary,old_h)
    historic=compare_pair(old_h,old_m)
    if (historic["mismatched_fields"]!=["traj.mu","traj.muhat"]
            or len(historic["critical_field_mismatch_details"]["traj.mu"])!=4
            or len(historic["critical_field_mismatch_details"]["traj.muhat"])!=4):
        raise ValueError("Original subject-7 4+4 scientific mismatch changed")
    pairs={"auto_within_mode":("auto_1","auto_2"),
           "Haswell_within_mode":("Haswell_1","Haswell_2"),
           "cross_mode_first":("auto_1","Haswell_1"),
           "cross_mode_second":("auto_2","Haswell_2"),
           "cross_mode_interleaved_a":("auto_1","Haswell_2"),
           "cross_mode_interleaved_b":("auto_2","Haswell_1")}
    comparisons={}
    for label,(a,b) in pairs.items():
        comparisons[label]={"left":a,"right":b,
            "original_numeric_tolerances":compare_pair(fresh[a],fresh[b]),
            "strict_serialized_binary64":strict_pair(fresh[a],fresh[b])}
    vs_original={name:{
        "vs_original_matlab":compare_pair(fresh[name],old_m),
        "vs_original_hgfx":compare_pair(fresh[name],old_h)
        } for name in ORDER}
    return {
        "schema":"perf01d-issue90-same-host-abba-repeatability-v1",
        "status":STATUS,"frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run":BASE_RUN,
        "original_64_raw_sha256":summary["raw_evidence_sha256"],
        "original_science":"63/64 NONPASS; original subject zero-based 7",
        "original_failed_fields":historic["mismatched_fields"],
        "original_failed_cells":{k:len(v) for k,v in historic["critical_field_mismatch_details"].items()},
        "environment":env,"same_runner_control":host,
        "fresh_raw_sha256":{k:env[k]["raw_sha256"] for k in ORDER},
        "pairwise":comparisons,"vs_original":vs_original,
        "limitations":[
            "Four fits are on one GitHub Actions runner and one four-core affinity set, not cross-host evidence.",
            "Two repeats per BLAS mode cannot establish universal repeatability.",
            "Original MATLAB reference was not rerun on this new host.",
            "The original 63/64 scientific NONPASS and all 28 preregistered cases are unchanged.",
            "No runtime timing, GPU, independent review, threshold change, scientific or performance PASS."
        ]}

def main():
    parser=argparse.ArgumentParser()
    for name in ("original","outputs","environment","output"):
        parser.add_argument("--"+name,required=True,type=Path)
    a=parser.parse_args()
    report=derive(a.original,a.outputs,a.environment)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":report["status"],"run":report["same_runner_control"]["run_id"],
        "within_mode_bitwise":{k:v["strict_serialized_binary64"]["all_serialized_binary64_equal"]
                               for k,v in report["pairwise"].items() if "within_mode" in k},
        "original_matlab_mismatches":{k:v["vs_original_matlab"]["mismatched_fields"]
                                    for k,v in report["vs_original"].items()},
        "original_science":"63/64 NONPASS; untimed"
        },sort_keys=True))

if __name__=="__main__":
    main()
