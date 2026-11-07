#!/usr/bin/env python3
"""Cross-compare exact subject-7 MATLAB/HGFX fit endpoints, no optimization.

Different fitted endpoints are NOT supposed to be assumed identical. First
check MATLAB versus HGFX on *each identical vector*; then separately measure
the own-package endpoint sensitivity. Do not move predeclared thresholds.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_trialwise import compare_numeric

FIELDS = ("inf_states", "trial_log_likelihoods", "yhat", "residuals")
TRAJECTORY_FIELDS = ("mu", "sa", "muhat", "sahat", "v", "w", "da", "ud", "psi", "epsi", "wt")
EXPECTED_HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
EXPECTED_MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def indexed(payload):
    rows = payload["cases"]
    if len(rows) != 2 or set(x["endpoint_source"] for x in rows) != {"hgfx","matlab"}:
        raise ValueError("Both exact optimizer endpoints must be represented")
    return {x["endpoint_source"]:x for x in rows}


def vector_fields(left, right):
    fields={k:compare_numeric(left[k],right[k]) for k in FIELDS}
    traj_left,traj_right=left["traj"],right["traj"]
    if set(traj_left)!=set(traj_right) or set(traj_left)!=set(TRAJECTORY_FIELDS):
        raise ValueError("Full 11-field trajectory schema required")
    for k in TRAJECTORY_FIELDS:
        fields["traj."+k]=compare_numeric(traj_left[k],traj_right[k])
    return fields


def classify(hgfx, matlab):
    if any((
        hgfx.get("schema")!="perf01-subject7-hgfx-cross-replay-v1",
        matlab.get("schema")!="perf01-subject7-matlab-cross-replay-v1",
        hgfx.get("product_sha")!=EXPECTED_HGFX,
        matlab.get("product_sha")!=EXPECTED_HGFX,
        hgfx.get("oracle_sha")!=EXPECTED_MATLAB,
        matlab.get("oracle_sha")!=EXPECTED_MATLAB,
        hgfx.get("source_run_id")!="41863441006",
        matlab.get("source_run_id")!="41863441006",
        hgfx.get("subject_index_zero_based")!=7,
        matlab.get("subject_index_zero_based")!=7,
        hgfx.get("trials")!=128,
        matlab.get("trials")!=128,
    )):
        raise ValueError("Source, model, or subject identity not verified")
    h,m=indexed(hgfx),indexed(matlab)
    same=[]
    for origin in ("hgfx","matlab"):
        a,b=h[origin],m[origin]
        row={
            "endpoint_source":origin,
            "hgfx_replay_status":a["status"],
            "matlab_replay_status":b["status"],
            "status":"UNASSESSED",
        }
        if a["status"]=="HGFX_REPLAY_COMPLETED" and b["status"]=="MATLAB_REPLAY_COMPLETED":
            if a["transformed_final_vector"]!=b["transformed_final_vector"]:
                row["status"]="ENDPOINT_BYTES_NOT_MATCHED"
            else:
                fields=vector_fields(a,b)
                row["fields"]=fields
                fails=[k for k,v in fields.items()
                       if v["status"]!="WITHIN_DIAGNOSTIC_TOLERANCE"]
                row["failed_fields"]=fails
                row["status"]=(
                    "SAME_VECTOR_OUTPUT_CONCORDANT_DIAGNOSTIC"
                    if not fails else "SAME_VECTOR_OUTPUT_MISMATCH"
                )
        else:
            row["status"]="REPLAY_INCOMPLETE_OR_ERROR"
            row["hgfx_error"]=a.get("error")
            row["matlab_error"]=b.get("error_message")
        same.append(row)
    # Deliberately not an equivalence test: these compare DIFFERENT final
    # fitted parameter vectors within each implementation, characterizing
    # endpoint sensitivity, without calling it an implementation mismatch.
    within={}
    for name,record in (("hgfx",h),("matlab",m)):
        if all(record[k]["status"]==(
            "HGFX_REPLAY_COMPLETED" if name=="hgfx" else "MATLAB_REPLAY_COMPLETED"
        ) for k in ("hgfx","matlab")):
            within[name]=vector_fields(record["hgfx"],record["matlab"])
        else:
            within[name]={"status":"NOT_ASSESSED_INCOMPLETE_REPLAY"}
    outcomes=[x["status"] for x in same]
    if outcomes==["SAME_VECTOR_OUTPUT_CONCORDANT_DIAGNOSTIC"]*2:
        decision="OPTIMIZER_ENDPOINT_SENSITIVITY_CANDIDATE_NOT_SCIENTIFIC_PASS"
    elif any(x=="SAME_VECTOR_OUTPUT_MISMATCH" for x in outcomes):
        decision="COMMON_VECTOR_INFERENCE_OR_OBSERVATION_MISMATCH"
    else:
        decision="UNRESOLVED_REPLAY_OR_SOURCE_MISMATCH"
    return {
        "schema":"perf01-subject7-cross-replay-comparison-v1",
        "status":"DIAGNOSTIC_ONLY_NO_TIMING_NO_GATE_PROMOTION",
        "source_run_id":"41863441006",
        "frozen_hgfx_sha":EXPECTED_HGFX,
        "frozen_matlab_sha":EXPECTED_MATLAB,
        "subject_index_zero_based":7,
        "endpoint_max_abs_delta":hgfx.get("endpoint_max_abs_delta"),
        "classification":decision,
        "same_vector_cross_implementation":same,
        "different_vector_within_implementation":within,
        "interpretation":"Same-vector replay is distinct from the original failed cross-endpoint fitting comparison. No threshold, dataset, optimizer, start, or reference was modified.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hgfx",type=Path,required=True)
    p.add_argument("--matlab",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=classify(json.loads(a.hgfx.read_bytes()),json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "classification":out["classification"],
        "same_vector_statuses":[r["status"] for r in out["same_vector_cross_implementation"]],
        "same_vector_failed_fields":{
            r["endpoint_source"]:r.get("failed_fields")
            for r in out["same_vector_cross_implementation"]
        },
    },sort_keys=True))
    if out["classification"]!="OPTIMIZER_ENDPOINT_SENSITIVITY_CANDIDATE_NOT_SCIENTIFIC_PASS":
        raise SystemExit("Same-vector replay unresolved or mismatch; evidence preserved")


if __name__=="__main__":
    main()
