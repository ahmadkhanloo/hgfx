#!/usr/bin/env python3
"""PERF-01D original subject-7 COMPLETE fitted output comparison.

All original v1 compare_fit_cohort fields and unchanged tolerances; retain
the full original 63/64 failed result and every new diagnostic mismatch.
This is NOT a new scientific PASS, eligibility decision or performance result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from compare_fits import TOLS, numeric
from fit_cohort_hgfx import FIT_FIELDS
from scientific_preflight import decode_number

HGFX_SHA="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA="2437f4dc241541072722a2695ddeca7b44d83dd3"
BASE_RUN="41863441006"
TRIAL_TOL=(3e-8,3e-10)
SOURCE_FIELDS=("mu","muhat")
DESCRIPTIVE="UNFROZEN_AUTHOR_SIDE_COMPLETE_TRAJECTORY_COMPARISON_NO_SCIENCE_PASS"


def load_original(root:Path)->tuple[dict,dict,dict]:
    summary=json.loads((root/f"summary-{BASE_RUN}.json").read_bytes())
    if (str(summary.get("github_run_id"))!=BASE_RUN
            or summary.get("hgfx_sha")!=HGFX_SHA
            or summary.get("matlab_sha")!=MATLAB_SHA
            or summary.get("subject_count")!=64
            or summary.get("classification_counts")!={
                "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1,
                "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
            }
            or summary["cases"][7]["classification"]!="FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"
            or summary["cases"][7]["mismatched_fields"]!=["traj.mu","traj.muhat"]):
        raise ValueError("Original full-cohort 63/64 scientific non-PASS provenance changed")
    old={}
    for kind in ("hgfx","matlab"):
        name=f"{kind}_raw.json"
        b=(root/name).read_bytes()
        if hashlib.sha256(b).hexdigest()!=summary["raw_evidence_sha256"][name]:
            raise ValueError("Original 64-fit raw SHA-256 altered: "+name)
        data=json.loads(b)
        if (len(data["cases"])!=64
                or [int(x["subject_index_zero_based"]) for x in data["cases"]]
                    != list(range(64))):
            raise ValueError("Original cohort inventory omitted/reordered")
        old[kind]=data["cases"][7]
    if (old["hgfx"]["status"]!="HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            or old["matlab"]["status"]!="MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            or old["hgfx"]["n_rand_init"]!=0
            or old["matlab"]["n_rand_init"]!=0
            or not old["hgfx"]["start_matches_frozen_snapshot"]
            or not old["matlab"]["start_matches_frozen_snapshot"]):
        raise ValueError("Original full public fitting workflow not matched")
    return summary,old["hgfx"],old["matlab"]


def validate_new(raw:dict,mode:str,summary:dict,original_hgfx:dict)->dict:
    expected_mode=None if mode=="auto" else "Haswell"
    if (raw.get("schema")!="perf01d-subject7-full-fit-traj-hgfx-v1"
            or raw.get("status")!="AUTHOR_SIDE_UNTIMED_COMPLETE_PUBLIC_FIT_NO_PARITY_DECISION"
            or raw.get("subject_index_zero_based")!=7
            or raw.get("trials")!=128
            or raw.get("model")!="hgf_binary"
            or raw.get("observation")!="unitsq_sgm"
            or raw.get("frozen_hgfx_sha")!=HGFX_SHA
            or raw.get("frozen_matlab_sha")!=MATLAB_SHA
            or str(raw.get("original_64_fit_run_id"))!=BASE_RUN
            or raw.get("original_64_raw_sha256")!=summary["raw_evidence_sha256"]
            or raw.get("source_input_sha256")!=summary["hgfx_input_sha256"]
            or raw.get("source_config_sha256")!=summary["hgfx_config_sha256"]
            or raw.get("frozen_start_matches") is not True
            or raw.get("n_rand_init")!=0
            or raw.get("history_buffer_slots")!=101
            or raw.get("finite_history_slots")!=25
            or raw.get("blas_mode_requested")!=expected_mode):
        raise ValueError(f"{mode}: original unchanged public refit identity not verified")
    if (set(raw["optim"])!=set(FIT_FIELDS)
            or set(raw["traj"])!=set(original_hgfx["traj"])):
        raise ValueError(f"{mode}: missing full fitModel output fields")
    if (not np.array_equal(np.asarray(raw["optim"]["init"],float),
                           np.asarray(original_hgfx["optim"]["init"],float),
                           equal_nan=True)
            or np.asarray(raw["traj"]["mu"],float).shape!=(128,3)
            or np.asarray(raw["traj"]["muhat"],float).shape!=(128,3)):
        raise ValueError(f"{mode}: original fitting start/trajectory shape changed")
    return raw


def detailed_differences(a,b,rtol,atol)->list[dict]:
    from compare_trialwise import decode_tree
    x=np.asarray(decode_tree(a),dtype=np.float64)
    y=np.asarray(decode_tree(b),dtype=np.float64)
    if x.shape!=y.shape:
        raise ValueError("Cannot report per-trial indices across different shape")
    bad=np.argwhere(~np.isclose(x,y,rtol=rtol,atol=atol,equal_nan=True))
    result=[]
    for ind in bad:
        key=tuple(int(i) for i in ind)
        left=float(x[key]);right=float(y[key])
        result.append({
            "index_zero_based":list(key),
            "trial_one_based":key[0]+1 if key else None,
            "level_one_based":key[1]+1 if len(key)>1 else None,
            "hgfx_value":left if np.isfinite(left) else None,
            "reference_value":right if np.isfinite(right) else None,
            "abs_difference":float(abs(left-right)),
            "unchanged_tolerance_bound_at_reference":float(atol+rtol*abs(right)),
        })
    return result


def compare_pair(hgfx:dict,reference:dict)->dict:
    fields={}
    if (set(hgfx["optim"])!=set(FIT_FIELDS)
            or set(reference["optim"])!=set(FIT_FIELDS)
            or set(hgfx["traj"])!=set(reference["traj"])):
        raise ValueError("Full originally committed fitting field inventory changed")
    for name,(rtol,atol) in TOLS.items():
        fields[name]=numeric(hgfx["optim"][name],reference["optim"][name],rtol,atol)
    for name in ("logjoint","postpredcorr","freepars"):
        fields["decompLME."+name]=numeric(
            hgfx["optim"]["decompLME"][name],reference["optim"]["decompLME"][name],
            2e-6,2e-8)
    for name in sorted(hgfx["traj"]):
        fields["traj."+name]=numeric(
            hgfx["traj"][name],reference["traj"][name],*TRIAL_TOL)
    failing=sorted(name for name,v in fields.items()
                   if v["status"]!="WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE")
    detailed={}
    for name in SOURCE_FIELDS:
        detailed["traj."+name]=detailed_differences(
            hgfx["traj"][name],reference["traj"][name],*TRIAL_TOL)
        if len(detailed["traj."+name])!=fields["traj."+name]["mismatch_count"]:
            raise ValueError("Index-by-index field inventory diverges from numeric comparison")
    return {
        "field_count":len(fields),
        "classification":("FULL_FIT_OUTPUTS_WITHIN_ORIGINAL_NUMERIC_TOLERANCES_DIAGNOSTIC_ONLY"
                          if not failing else "FULL_FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"),
        "mismatched_fields":failing,
        "fields":fields,
        "critical_field_mismatch_details":detailed,
    }


def run(root:Path,auto:dict,haswell:dict,metadata_path:Path)->dict:
    summary,old_h,old_m=load_original(root)
    a=validate_new(auto,"auto",summary,old_h)
    h=validate_new(haswell,"Haswell",summary,old_h)
    environment=json.loads(metadata_path.read_bytes())
    if (set(environment)!={"auto","Haswell"}
            or environment["auto"]["run_id"]!=environment["Haswell"]["run_id"]
            or environment["auto"]["platform"]!=environment["Haswell"]["platform"]
            or environment["auto"]["numpy"]!=environment["Haswell"]["numpy"]=="2.3.5"
            or environment["auto"]["openblas_coretype"] is not None
            or environment["Haswell"]["openblas_coretype"]!="Haswell"
            or not any(x.get("architecture")=="Haswell" for x in environment["Haswell"]["pools"])):
        raise ValueError("Two-source full-fit no-timing experiment has mismatched same-host provenance")
    pairs={
        "original_hgfx_vs_original_matlab":compare_pair(old_h,old_m),
        "new_auto_vs_original_matlab":compare_pair(a,old_m),
        "new_haswell_vs_original_matlab":compare_pair(h,old_m),
        "new_auto_vs_new_haswell":compare_pair(a,h),
        "new_auto_vs_original_hgfx":compare_pair(a,old_h),
        "new_haswell_vs_original_hgfx":compare_pair(h,old_h),
    }
    original=pairs["original_hgfx_vs_original_matlab"]
    recorded=summary["cases"][7]["fields"]
    if (set(original["fields"])!=set(recorded)
            or original["mismatched_fields"]!=["traj.mu","traj.muhat"]):
        raise ValueError("Original failure inventory was modified")
    for field in original["fields"]:
        fresh=original["fields"][field]
        historic=recorded[field]
        for name in ("status","mismatch_count","first_mismatch_index_zero_based",
                     "rtol","atol"):
            if fresh.get(name)!=historic.get(name):
                raise ValueError(f"Original strict scientific field changed: {field}.{name}")
    for name in SOURCE_FIELDS:
        if len(original["critical_field_mismatch_details"]["traj."+name])!=4:
            raise ValueError(f"Original source {name} four mismatch entries were lost")
    return {
        "schema":"perf01d-subject7-two-mode-full-fit-trajectory-v1",
        "status":DESCRIPTIVE,
        "original_64_fit_run_id":BASE_RUN,
        "original_64_raw_sha256":summary["raw_evidence_sha256"],
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "original_scientific_classification":"63/64 NON-PASS; original subject-7 traj.mu and traj.muhat mismatch",
        "original_64_denominator":64,
        "subject_index_zero_based":7,
        "trials":128,
        "original_unchanged_trajectory_tolerance":{"rtol":TRIAL_TOL[0],"atol":TRIAL_TOL[1]},
        "same_host":environment,
        "comparisons":pairs,
        "warning":"New case classifications are descriptive only and NEVER change the original 64-case scientific outcome or prospectively freeze PERF-01C.",
        "limitations":[
            "Old MATLAB reference is an original archived fitting from another run, NOT re-executed on the new CPU.",
            "Both new HGFX full public fits reused exact original data/config/starts and unchanged software v1.0.0.",
            "ALL original numeric fitting/trajectory fields and original tolerances are reported; failures are not excluded.",
            "Original 63/64 scientific non-PASS and all failed experiments remain immutable.",
            "NO timing, GPU validation, independent reviewer signoff, runtime speedup or release-gate approval.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("original","auto","haswell","environment","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    auto=json.loads(a.auto.read_bytes())
    haswell=json.loads(a.haswell.read_bytes())
    output=run(a.original,auto,haswell,a.environment)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":output["status"],
        "original":output["comparisons"]["original_hgfx_vs_original_matlab"]["mismatched_fields"],
        "new_auto":output["comparisons"]["new_auto_vs_original_matlab"]["mismatched_fields"],
        "new_haswell":output["comparisons"]["new_haswell_vs_original_matlab"]["mismatched_fields"],
        "both_modes":output["comparisons"]["new_auto_vs_new_haswell"]["mismatched_fields"],
        "critical_field_mismatch_counts":{
            name:{f:len(v) for f,v in result["critical_field_mismatch_details"].items()}
            for name,result in output["comparisons"].items()
        },
        "disposition":"NO NEW SCIENTIFIC PASS; ORIGINAL 63/64",
    },sort_keys=True))


if __name__=="__main__":
    main()
