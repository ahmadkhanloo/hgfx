#!/usr/bin/env python3
"""Compare MATLAB/HGFX Ridders gradients evaluated at IDENTICAL saved vectors.

Two groups of archived fit anchors x five indices; does not rerun fitting,
change scientific acceptance thresholds or approve a speed benchmark.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import numpy as np

from compare_fits import TOLS

PRODUCT = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
REFERENCE = "2437f4dc241541072722a2695ddeca7b44d83dd3"
TRACE = "42115887599"
TRACE_SHA = "b378fef6ff93f6efa041f4e8304dafba742ae4ab"
ANCHORS = [0, 1, 13, 14, 23]
TRACE_HASHES = {
    "hgfx_raw.json": "6fe10be1dd1860612859e6efbe7bee13717e4787aed4a62f0e6b67a2072aac7a",
    "matlab_raw.json": "ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f",
}


def keyed(payload: dict, engine: str) -> dict:
    expected_schema=f"perf01d-subject7-{engine}-same-vector-gradient-v1"
    source_hashes=payload.get("original_trace_raw_sha256")
    if isinstance(source_hashes,dict):
        source_hashes={key.replace("_raw_json","_raw.json"):value
                       for key,value in source_hashes.items()}
    if (payload.get("schema") != expected_schema
            or payload.get("status") != "AUTHOR_SIDE_DIAGNOSTIC_UNTIMED_NO_FIT_NO_GATE_PASS"
            or payload.get("frozen_hgfx_sha") != PRODUCT
            or payload.get("frozen_matlab_sha") != REFERENCE
            or payload.get("original_trace_run") != TRACE
            or payload.get("original_trace_sha") != TRACE_SHA
            or source_hashes != TRACE_HASHES
            or payload.get("source_run_id") != "41863441006"
            or payload.get("subject_index_zero_based") != 7
            or payload.get("trials") != 128
            or payload.get("model") != "hgf_binary"
            or payload.get("observation") != "unitsq_sgm"
            or payload.get("free_indices_zero_based") != [12,13,14]
            or payload.get("gradient_method") != "frozen_Ridders_min_steps_10"
            or payload.get("anchor_indices_zero_based") != ANCHORS):
        raise ValueError(f"Unverified {engine} frozen gradient source/identity")
    cases=payload["cases"]
    if len(cases)!=10:
        raise ValueError(f"{engine}: must retain all 10 original anchor cases")
    keys=[(c["anchor_origin"],int(c["record_index_zero_based"])) for c in cases]
    expected={(o,i) for o in ("hgfx","matlab") for i in ANCHORS}
    if len(set(keys))!=10 or set(keys)!=expected:
        raise ValueError(f"{engine}: incomplete or duplicate source/anchor inventory")
    return dict(zip(keys,cases))


def finite_compare(left,right,*,relative_tolerance,absolute_tolerance):
    a=np.asarray(left,dtype=np.float64).reshape(-1)
    b=np.asarray(right,dtype=np.float64).reshape(-1)
    if a.shape!=b.shape:
        return {"status":"SHAPE_MISMATCH","shape_hgfx":list(a.shape),"shape_matlab":list(b.shape)}
    m=np.isfinite(a) & np.isfinite(b)
    masks_equal=bool(np.array_equal(np.isnan(a),np.isnan(b))
                     and np.array_equal(np.isposinf(a),np.isposinf(b))
                     and np.array_equal(np.isneginf(a),np.isneginf(b)))
    delta=np.abs(a[m]-b[m])
    tol=absolute_tolerance+relative_tolerance*np.abs(b[m])
    failures=np.flatnonzero(delta>tol)
    return {
        "status": ("FINITE_DIAGNOSTIC_WITHIN_EXISTING_FINAL_PARAMETER_TOLERANCE"
                   if masks_equal and failures.size==0 and m.any()
                   else "DIAGNOSTIC_DISCREPANCY_OR_NONFINITE"),
        "shape":list(a.shape),
        "finite_pairs":int(m.sum()),
        "nonfinite_masks_match":masks_equal,
        "max_abs_difference":float(delta.max()) if delta.size else None,
        "number_outside_existing_final_parameter_tolerance":int(failures.size),
        "first_outside_finite_component_index":int(failures[0]) if failures.size else None,
    }


def compare(hgfx:dict,matlab:dict)->dict:
    a,b=keyed(hgfx,"hgfx"),keyed(matlab,"matlab")
    atol=TOLS["final"][1]
    rtol=TOLS["final"][0]
    rows=[]
    for origin in ("hgfx","matlab"):
        for i in ANCHORS:
            key=(origin,i)
            h,m=a[key],b[key]
            if (h["status"]!="EVALUATED" or m["status"]!="EVALUATED"):
                rows.append({"anchor_origin":origin,"record_index_zero_based":i,
                             "status":"PROBE_ERROR_OR_INCOMPLETE",
                             "hgfx_status":h["status"],"matlab_status":m["status"]})
                continue
            x_h=np.asarray(h["free_parameters"],np.float64)
            x_m=np.asarray(m["free_parameters"],np.float64)
            if x_h.shape!=(3,) or x_m.shape!=(3,) or not np.array_equal(x_h,x_m):
                rows.append({"anchor_origin":origin,"record_index_zero_based":i,
                             "status":"SAME_VECTOR_IDENTITY_VIOLATION"})
                continue
            if (not math.isfinite(float(h["objective"]))
                    or not math.isfinite(float(m["objective"]))):
                rows.append({"anchor_origin":origin,"record_index_zero_based":i,
                             "status":"NONFINITE_OBJECTIVE"})
                continue
            grad=finite_compare(h["ridders_gradient"],m["ridders_gradient"],
                relative_tolerance=rtol,absolute_tolerance=atol)
            err=finite_compare(h["ridders_error"],m["ridders_error"],
                relative_tolerance=rtol,absolute_tolerance=atol)
            obj=finite_compare([h["objective"]],[m["objective"]],
                relative_tolerance=rtol,absolute_tolerance=atol)
            rows.append({
                "anchor_origin":origin,"record_index_zero_based":i,
                "status":"SCIENTIFIC_GRADIENT_DIAGNOSTIC_NO_GATE_DECISION",
                "exact_free_parameters":h["free_parameters"],
                "hgfx_objective":h["objective"],"matlab_objective":m["objective"],
                "objective":obj,"ridders_gradient":grad,"ridders_error_estimate":err,
                "hgfx_archived_iter_val_abs_diff":h["archived_objective_abs_diff"],
                "matlab_archived_iter_val_abs_diff":m["archived_objective_abs_diff"],
                "hgfx_gradient":h["ridders_gradient"],
                "matlab_gradient":m["ridders_gradient"],
            })
    diagnostic=[r for r in rows if r["status"]=="SCIENTIFIC_GRADIENT_DIAGNOSTIC_NO_GATE_DECISION"]
    changed=[r for r in diagnostic if r["ridders_gradient"]["number_outside_existing_final_parameter_tolerance"]>0
             or not r["ridders_gradient"]["nonfinite_masks_match"]]
    return {
        "schema":"perf01d-subject7-paired-gradient-diagnostic-v1",
        "status":"AUTHOR_SIDE_GRADIENT_DIAGNOSTIC_NO_SCIENTIFIC_PASS_NO_TIMING",
        "frozen_hgfx_sha":PRODUCT,"frozen_matlab_sha":REFERENCE,
        "original_trace_run":TRACE,"original_trace_raw_sha256":TRACE_HASHES,
        "source_run_id":"41863441006",
        "anchor_count":len(rows),"fully_evaluated_pairs":len(diagnostic),
        "gradient_discrepancy_count_under_existing_final_tolerance_as_lens":len(changed),
        "original_failure_preserved": "64 full fits 63/64; subject index 7 traj.mu and traj.muhat mismatch",
        "interpretation": (
            "Gradient and objective on exactly identical recorded parameter vectors, not "
            "optimizer endpoint fitting equivalence; inherited final-vector tolerance "
            "is shown only as a descriptive lens, not a preregistered per-gradient gate."
        ),
        "cases":rows,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("hgfx","matlab","output"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    report=compare(json.loads(args.hgfx.read_bytes()),json.loads(args.matlab.read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "full_cases":report["fully_evaluated_pairs"],"total":report["anchor_count"],
        "gradient_discrepancy_count_descriptive":report["gradient_discrepancy_count_under_existing_final_tolerance_as_lens"],
        "case_diagnostics":[[r["anchor_origin"],r["record_index_zero_based"],r["status"],
             r.get("ridders_gradient",{}).get("max_abs_difference")]
             for r in report["cases"]],
        "status":report["status"],
    },sort_keys=True))
    if report["fully_evaluated_pairs"]!=10:
        raise SystemExit("Not all 10 original gradient anchors evaluated; failed evidence retained")


if __name__=="__main__":
    main()
