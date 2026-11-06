#!/usr/bin/env python3
"""Same-Actions-runner MATLAB/HGFX subject7 full public fits (untimed).

Prospectively specified in PERF01D_SUBJECT7_MATCHED_RUNNER_PRESPEC_2026-11-06.
Preserve every original/nonconcordant 28-field result; no changed thresholds.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from fit_cohort_hgfx import FIT_FIELDS
from compare_subject7_full_fit_trajectories import (
    BASE_RUN, HGFX_SHA, MATLAB_SHA, load_original, compare_pair,
)
from compare_subject7_same_host_repeatability_v2 import (
    ORDER, validate_environment, validate_explicit_coretype, strict_pair,
)
from compare_trialwise import decode_tree

STATUS = "AUTHOR_SIDE_SAME_RUNNER_FRESH_MATLAB_HGFX_FITS_NOT_SCIENTIFIC_PASS"
MATLAB_SCHEMA = "perf01d-subject7-same-runner-matlab-v1"
REF_ORDER=("MATLAB_1","MATLAB_2")
EXPECTED_MATLAB_STATUS = "AUTHOR_SIDE_UNTIMED_FROZEN_MATLAB_TWO_PUBLIC_FITS_NO_PARITY_DECISION"

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def validate_matlab(data, summary, original, expected_run, expected_sha):
    require(data.get("schema")==MATLAB_SCHEMA
            and data.get("status")==EXPECTED_MATLAB_STATUS
            and data.get("frozen_hgfx_sha")==HGFX_SHA
            and data.get("frozen_matlab_sha")==MATLAB_SHA
            and str(data.get("original_64_fit_run"))==BASE_RUN
            and data.get("original_64_raw_sha256")==summary["raw_evidence_sha256"]
            and data.get("original_63_64_nonpass") is True
            and data.get("original_subject_index_zero_based")==7
            and data.get("source_input_sha256")==summary["hgfx_input_sha256"]
            and data.get("source_config_sha256")==summary["hgfx_config_sha256"]
            and data.get("matlab_release")=="2026a"
            and data.get("github_run_id")==expected_run
            and data.get("github_sha")==expected_sha
            and data.get("no_timing") is True
            and data.get("no_scientific_gate_promotion") is True
            and data.get("fit_order")==list(REF_ORDER),
            "Fresh MATLAB source, input, two-run inventory or no-timing provenance changed")
    require(data.get("runner_name") and data.get("machine_arch")=="glnxa64"
            and data.get("matlab_fitModel_resolved_path")
            and data.get("matlab_hgf_binary_resolved_path"),
            "MATLAB runner or frozen path resolution unverified")
    # The two source-file paths must contain the same fresh frozen toolbox root.
    for name in ("matlab_fitModel_resolved_path","matlab_hgf_binary_resolved_path"):
        p=data[name].replace("\\","/")
        require("/matlab-reference/" in p and p.endswith(".m"),
                "MATLAB model/fit resolved outside frozen checkout: "+name)
    cases=data.get("cases")
    require(isinstance(cases,list) and len(cases)==2,
            "Two predeclared MATLAB public fits missing")
    for record in cases:
        require(record.get("subject_index_zero_based")==7
                and record.get("n_trials")==128
                and record.get("model")=="hgf_binary"
                and record.get("observation")=="unitsq_sgm"
                and record.get("status")=="MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
                and record.get("n_rand_init")==0
                and record.get("start_matches_frozen_snapshot") is True
                and record.get("console_characters",0)>0
                and set(record.get("optim",{}))==set(FIT_FIELDS)
                and set(record.get("traj",{}))==set(original["traj"]),
                "MATLAB full fit, output inventory, original start or stdout not verified")
        old_start=np.asarray(decode_tree(original["optim"]["init"]),np.float64)
        new_start=np.asarray(decode_tree(record["optim"]["init"]),np.float64)
        require(np.array_equal(old_start,new_start,equal_nan=True),
                "MATLAB optimizer start changed")
        hist=record.get("optimizer_history",{})
        vals=np.asarray(decode_tree(hist.get("val",[])),np.float64)
        x=np.asarray(decode_tree(hist.get("x",[])),np.float64)
        require(vals.shape==(101,) and x.shape==(101,3)
                and record.get("optimizer_iteration_count")==101
                and record.get("finite_optimizer_history_slots")==25
                and np.array_equal(np.flatnonzero(np.isfinite(vals)),np.arange(25)),
                "Original MATLAB 101 allocated / 25 finite history structure changed")
        for field in ("mu","muhat"):
            require(np.asarray(decode_tree(record["traj"][field]),np.float64).shape==(128,3),
                    "Original MATLAB source trajectory shape changed: "+field)
    return cases

def validate_hgfx(raw, expected_mode, summary, old_hgfx):
    return validate_explicit_coretype(raw,expected_mode,summary,old_hgfx)

def full_history_pair(a,b):
    aa,bb=a["optimizer_history"],b["optimizer_history"]
    out={}
    for field in ("val","x"):
        x=np.asarray(decode_tree(aa[field]),np.float64)
        y=np.asarray(decode_tree(bb[field]),np.float64)
        require(x.shape==y.shape, "MATLAB history shapes changed")
        equal=(x.view(np.uint64)==y.view(np.uint64))
        out[field]={"shape":list(x.shape),
                    "serialized_binary64_equal":bool(np.all(equal)),
                    "differing_serialized_binary64_values":int(np.count_nonzero(~equal))}
    return out

def derive(original:Path, matlab_file:Path, hgfx_folder:Path,
           environments:Path, expected_run:str, expected_sha:str):
    summary,old_h,old_m=load_original(original)
    environment=json.loads(environments.read_bytes())
    host=validate_environment(environment)
    require(host["run_id"]==expected_run and host["code_sha"]==expected_sha,
            "New run source/hardware identifier diverges")
    newmat=json.loads(matlab_file.read_bytes())
    m=validate_matlab(newmat,summary,old_m,expected_run,expected_sha)
    # Verify same Actions job and runner; scientific scope ONLY, MATLAB BLAS
    # and Python OpenBLAS affinity are not falsely claimed equivalent.
    require(host["code_sha"]==newmat["github_sha"]
            and host["run_id"]==newmat["github_run_id"],
            "MATLAB/HGFX do not belong to same GitHub Actions execution")
    h={}
    for name in ORDER:
        p=hgfx_folder/(name+"_raw.json")
        require(digest(p)==environment[name]["raw_sha256"],
                "Fresh HGFX source SHA256 differs: "+name)
        h[name]=validate_hgfx(json.loads(p.read_bytes()),
                              "SkylakeX" if name.startswith("SkylakeX") else "Haswell",
                              summary,old_h)
    original_compare=compare_pair(old_h,old_m)
    require(original_compare["mismatched_fields"]==["traj.mu","traj.muhat"]
            and len(original_compare["critical_field_mismatch_details"]["traj.mu"])==4
            and len(original_compare["critical_field_mismatch_details"]["traj.muhat"])==4,
            "The failed original subject-7 63/64 gate changed")
    pairwise={}
    for hn in ORDER:
        for mi,mname in enumerate(REF_ORDER):
            pairwise[hn+"_vs_"+mname]=compare_pair(h[hn],m[mi])
    require(len(pairwise)==8, "All eight predeclared cross-implementation contrasts required")
    old_reference={
        hn:compare_pair(h[hn],old_m) for hn in ORDER
    }
    fresh_vs_old={
        mname:compare_pair(m[i],old_m) for i,mname in enumerate(REF_ORDER)
    }
    source_self={
        "matlab_full_28_field":strict_pair(m[0],m[1]),
        "matlab_full_optimizer_history":full_history_pair(m[0],m[1]),
        "hgfx_skylakex_full_28_field":strict_pair(h[ORDER[0]],h[ORDER[3]]),
        "hgfx_haswell_full_28_field":strict_pair(h[ORDER[1]],h[ORDER[2]]),
    }
    require(source_self["matlab_full_28_field"]["field_count"]==28
            and all(r["field_count"]==28 for r in (source_self["hgfx_skylakex_full_28_field"],
                                                    source_self["hgfx_haswell_full_28_field"])),
            "All 28 scientific output fields must be available")
    # New scientific results have no mandatory "must pass" condition.
    return {
        "schema":"perf01d-subject7-real-matched-actions-runner-matlab-hgfx-v1",
        "status":STATUS,
        "frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run_id":BASE_RUN,
        "original_64_raw_sha256":summary["raw_evidence_sha256"],
        "original_scientific":"63/64 NONPASS; original subject-7 traj.mu and traj.muhat 4+4",
        "original_failed_fit":original_compare,
        "subject_index_zero_based":7,"trials":128,
        "new_matlab_run":expected_run,"new_hgfx_run":expected_run,
        "new_matlab_raw_sha256":digest(matlab_file),
        "new_hgfx_raw_sha256":{x:environment[x]["raw_sha256"] for x in ORDER},
        "matlab_environment":{
            key:newmat[key] for key in (
                "matlab_release","matlab_version","runner_name","machine_arch",
                "matlab_fitModel_resolved_path","matlab_hgf_binary_resolved_path",
                "matlab_max_computational_threads","requested_shared_cpu_set")
        },
        "hgfx_same_runner_environment":environment,
        "hgfx_environment_verified":host,
        "fresh_matlab_console_characters":{name:m[i]["console_characters"]
                                           for i,name in enumerate(REF_ORDER)},
        "same_source_repeated_fit":source_self,
        "all_eight_fresh_matlab_hgfx_28_field_comparisons":pairwise,
        "fresh_hgfx_vs_old_matlab":old_reference,
        "fresh_matlab_vs_old_matlab":fresh_vs_old,
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN",
        "no_original_scientific_result_overwrite":True,
        "limitations":[
            "Same GitHub Actions runner is not identical MATLAB and HGFX BLAS kernels, affinity or thread runtime.",
            "There are exactly two MATLAB and two HGFX fits per selected mode, not an identifiability proof.",
            "Eight new original-tolerance scientific comparisons are DESCRIPTIVE, without automatic PASS/freeze.",
            "Original 64-subject 63/64 NONPASS, all original cases and acceptance thresholds remain unchanged.",
            "No performance timing, GPU evidence, prospective benchmark freeze or independent reviewer verdict."
        ],
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("original","matlab","hgfx","environment","output"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--run-id",required=True)
    p.add_argument("--sha",required=True)
    args=p.parse_args()
    result=derive(args.original,args.matlab,args.hgfx,args.environment,
                  args.run_id,args.sha)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":result["status"],"original_science":result["original_scientific"],
        "eight_cross_implementation_mismatched_fields":{
            k:v["mismatched_fields"]
            for k,v in result["all_eight_fresh_matlab_hgfx_28_field_comparisons"].items()},
        "matlab_self_bitwise":result["same_source_repeated_fit"]["matlab_full_28_field"]["all_serialized_binary64_equal"],
        "perf01c":"NOT_FROZEN","performance_timing":"NOT_RUN",
    },sort_keys=True))

if __name__=="__main__":
    main()
