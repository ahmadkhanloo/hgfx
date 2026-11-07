#!/usr/bin/env python3
"""Compare every predeclared 64-subject HGF/eHGF/uHGF fixed-vector pair.

Diagnostics only; no timing, fitting, subject exclusion or scientific PASS.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

MODELS=("hgf_binary","ehgf_binary","uhgf_binary")
HORIZONS=(128,512,1024)
SUBJECTS=64
RTOL=3e-8
ATOL=3e-10
FROZEN_HGFX="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
FROZEN_ORACLE="2437f4dc241541072722a2695ddeca7b44d83dd3"


def index(records, name):
    expected={(m,n,s) for m in MODELS for n in HORIZONS for s in range(SUBJECTS)}
    keys=[(r["model"],int(r["trials"]),int(r["subject_index_zero_based"]))
          for r in records]
    if len(keys)!=576 or len(set(keys))!=576 or set(keys)!=expected:
        raise ValueError(f"{name}: missing/duplicated cohort entries")
    return {key:record for key,record in zip(keys,records)}


def analyze(hgfx, matlab):
    if (hgfx.get("source_sha")!=FROZEN_HGFX
        or hgfx.get("versions",{}).get("hgfx")!="1.0.0"
        or matlab.get("oracle_sha")!=FROZEN_ORACLE
        or hgfx.get("protocol_id")!="hgfx-matlab-runtime-1"
        or matlab.get("protocol_id")!="hgfx-matlab-runtime-1"):
        raise ValueError("Frozen comparator/protocol identity mismatch")
    h=index(hgfx["cases"],"hgfx")
    m=index(matlab["cases"],"matlab")
    rows=[]
    for key in sorted(h):
        a,b=h[key],m[key]
        row={
            "model":key[0],"trials":key[1],"subject_index_zero_based":key[2],
            "hgfx_forward_status":a["forward_status"],
            "matlab_forward_status":b["forward_status"],
            "hgfx_objective_status":a["objective_status"],
            "matlab_objective_status":b["objective_status"],
            "config_both_verified":bool(a["config_matches_snapshot"] and b["config_matches_snapshot"]),
            "classification":"UNASSESSED",
        }
        if not row["config_both_verified"]:
            row["classification"]="BLOCKED_CONFIG_MISMATCH"
        elif a["forward_status"]==b["forward_status"]=="COMPLETE" and a["objective_status"]==b["objective_status"]=="COMPLETE":
            ja=float(a["negative_log_joint"])
            jb=float(b["negative_log_joint"])
            la=float(a["negative_log_likelihood"])
            lb=float(b["negative_log_likelihood"])
            if not all(math.isfinite(x) for x in (ja,jb,la,lb)):
                row["classification"]="NONFINITE_UNEXPECTED"
            elif (math.isclose(ja,jb,rel_tol=RTOL,abs_tol=ATOL)
                  and math.isclose(la,lb,rel_tol=RTOL,abs_tol=ATOL)
                  and int(a.get("valid_likelihood_trials",-1))==int(b.get("valid_likelihood_trials",-2))):
                row["classification"]="COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"
                row["joint_abs_delta"]=abs(ja-jb)
                row["likelihood_abs_delta"]=abs(la-lb)
            else:
                row["classification"]="SCALAR_MISMATCH"
                row["joint_abs_delta"]=abs(ja-jb)
                row["likelihood_abs_delta"]=abs(la-lb)
        elif (a["forward_status"]==b["forward_status"]=="INVALID_OR_ERROR"
              and a["objective_status"]==b["objective_status"]=="INVALID_OR_ERROR"):
            row["matlab_error_identifier"]=b.get("error_identifier","")
            row["hgfx_error"]=a.get("forward_error",a.get("exception",""))
            if (row["matlab_error_identifier"]=="tapas:hgf:VarApproxInvalid"
                and "Variational approximation invalid" in row["hgfx_error"]
                and key[0]=="hgf_binary"):
                row["classification"]="BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC"
            else:
                row["classification"]="BOTH_INVALID_MECHANISM_UNVERIFIED"
        else:
            row["classification"]="ASYMMETRIC_STATUS_OR_OBJECTIVE"
            row["matlab_error_identifier"]=b.get("error_identifier","")
            row["hgfx_error"]=a.get("forward_error",a.get("exception",""))
        rows.append(row)

    counts=Counter(x["classification"] for x in rows)
    strata=[]
    for model in MODELS:
        for n in HORIZONS:
            for prefix in (1,16,64):
                part=[x for x in rows if x["model"]==model and x["trials"]==n
                      and x["subject_index_zero_based"]<prefix]
                strata.append({
                    "model":model,"trials":n,"submitted_subjects":prefix,
                    "completed_scalar_pairs":sum(x["classification"]=="COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE" for x in part),
                    "both_invalid_reference_behavior_pairs":sum(x["classification"]=="BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC" for x in part),
                    "blocked_or_mismatched_subjects":sum(x["classification"] not in (
                       "COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE",
                       "BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC") for x in part),
                    "matlab_objective_completed":sum(x["matlab_objective_status"]=="COMPLETE" for x in part),
                    "hgfx_objective_completed":sum(x["hgfx_objective_status"]=="COMPLETE" for x in part),
                })
    return {
      "schema":"perf01-all-subject-paired-diagnostic-v1",
      "protocol_id":"hgfx-matlab-runtime-1",
      "status":"DIAGNOSTIC_ONLY_NO_TIMING_NO_SCIENTIFIC_PASS",
      "hgfx_source_sha":FROZEN_HGFX,"matlab_oracle_sha":FROZEN_ORACLE,
      "matlab_release":matlab.get("matlab_release"),
      "input_manifest_sha256":hgfx.get("input_manifest_sha256"),
      "config_manifest_sha256":hgfx.get("config_manifest_sha256"),
      "rtol":RTOL,"atol":ATOL,
      "classification_counts":dict(sorted(counts.items())),
      "strata":strata,"rows":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hgfx",type=Path,required=True)
    p.add_argument("--matlab",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    obj=analyze(json.loads(a.hgfx.read_bytes()),json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"subjects_total":len(obj["rows"]),"counts":obj["classification_counts"]},sort_keys=True))
    disallowed=set(obj["classification_counts"])-{
      "COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE",
      "BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC",
    }
    if disallowed:
        raise SystemExit(f"PERF-01 all-subject mismatches preserved: {sorted(disallowed)}")


if __name__=="__main__":
    main()
