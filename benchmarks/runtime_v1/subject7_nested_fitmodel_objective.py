#!/usr/bin/env python3
"""Frozen MATLAB private-nested fitModel objective, caught via public optimizer hook.

50 predeclared actual native MATLAB history occurrences (two 25-row histories).
No original fitting/acceptance gate promotion, no timer or changed thresholds.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path
import math
import numpy as np

SOURCE_RUN="42268256755"
SOURCE_COMMIT="331bb639dd65f3a3e2620b34f736a9b5156b8725"
MATLAB_RAW_SHA256="2133b60ca7dcd51b85d93dfad109f715bd8fe35fa71c2bd84ff4a63cac672139"
HGFX_SHA="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA="2437f4dc241541072722a2695ddeca7b44d83dd3"
GROUPS=("MATLAB_1","MATLAB_2")
ROWS=25
EXPECTED_START=(-3.,-6.,3.871201010907891)
STATUS="AUTHOR_SIDE_PRIVATE_FITMODEL_OBJECTIVE_CAPTURE_DIAGNOSTIC_NOT_SCIENTIFIC_PASS"

def check(ok:bool,why:str):
    if not ok:raise ValueError(why)

def rawhash(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()

def get_anchor_records(raw:dict)->list[dict]:
    check(raw.get("schema")=="perf01d-subject7-same-runner-matlab-v1"
          and raw.get("status")=="AUTHOR_SIDE_UNTIMED_FROZEN_MATLAB_TWO_PUBLIC_FITS_NO_PARITY_DECISION"
          and raw.get("github_run_id")==SOURCE_RUN
          and raw.get("github_sha")==SOURCE_COMMIT
          and raw.get("frozen_hgfx_sha")==HGFX_SHA
          and raw.get("frozen_matlab_sha")==MATLAB_SHA
          and str(raw.get("original_64_fit_run"))=="41863441006"
          and raw.get("original_63_64_nonpass") is True
          and raw.get("original_subject_index_zero_based")==7
          and raw.get("matlab_release")=="2026a"
          and raw.get("no_timing") is True
          and raw.get("no_scientific_gate_promotion") is True
          and raw.get("fit_order")==list(GROUPS),
          "original historical source/gate/identity changed")
    cases=raw.get("cases")
    check(isinstance(cases,list) and len(cases)==2,"two unmodified MATLAB fits are required")
    result=[]
    for n,case in enumerate(cases):
        check(case.get("subject_index_zero_based")==7
              and case.get("n_trials")==128
              and case.get("start_matches_frozen_snapshot") is True
              and case.get("n_rand_init")==0
              and case.get("finite_optimizer_history_slots")==ROWS
              and case.get("optimizer_iteration_count")==101,
              "original MATLAB fit/start/history identity changed")
        hist=case.get("optimizer_history",{})
        x=np.asarray(hist.get("x"),dtype=np.float64)
        vals=np.asarray(hist.get("val"),dtype=np.float64)
        check(x.shape==(101,3) and vals.shape==(101,),
              "original 101 allocated 3-dimensional optimizer history changed")
        check(np.array_equal(np.flatnonzero(np.isfinite(vals)),np.arange(ROWS))
              and np.isfinite(x[:ROWS]).all()
              and not np.isfinite(x[ROWS:]).any()
              and np.array_equal(x[0],np.asarray(EXPECTED_START,np.float64)),
              "original 25 finite history rows, trailing 76 NaNs or start changed")
        for i in range(ROWS):
            result.append({
                "anchor_origin":GROUPS[n],"record_index_zero_based":i,
                "free_parameters":x[i].tolist(),
                "original_public_iter_val":float(vals[i]),
            })
    check(len(result)==50,"fixed source-anchor denominator changed")
    return result

def prepare(native_path:Path, out_path:Path, root:Path)->dict:
    check(rawhash(native_path)==MATLAB_RAW_SHA256,
          "original same-runner MATLAB raw SHA-256 differs")
    raw=json.loads(native_path.read_bytes())
    rows=get_anchor_records(raw)
    src=root/"inputs"/"binary_128_s64.json"
    input_hash=rawhash(src)
    check(raw.get("source_input_sha256")==input_hash,"original input bytes changed")
    cfg=root/"configs"/"hgf_binary_128.json"
    check(raw.get("source_config_sha256")==rawhash(cfg),"original config bytes changed")
    out={
        "schema":"perf01d-original-matlab-native-optimizer-anchors-v1",
        "status":"FROZEN_50_ANCHORS_BEFORE_PRIVATE_OBJECTIVE_EVALUATION",
        "original_matlab_raw_sha256":MATLAB_RAW_SHA256,
        "original_fit_source_run":SOURCE_RUN,
        "original_fit_source_commit":SOURCE_COMMIT,
        "frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "source_input_sha256":input_hash,
        "source_config_sha256":rawhash(cfg),
        "source_subject_zero_based":7,
        "source_original_fitting":"63/64 NONPASS",
        "counts":{"MATLAB_1":25,"MATLAB_2":25},
        "anchor_indices_zero_based":list(range(ROWS)),
        "cases":rows,
        "no_timing":True,"perf01c":"NOT_FROZEN",
    }
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return out

def compare(root:Path,source:Path,anchor_path:Path,matlab_path:Path)->dict:
    from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
    from compare_subject7_full_fit_trajectories import compare_pair
    from compare_subject7_same_host_repeatability_v2 import strict_pair
    check(metadata.version("hgfx")=="1.0.0","frozen original hgfx package not installed")
    check(rawhash(source/"matlab_raw.json")==MATLAB_RAW_SHA256,
          "original same-runner native MATLAB raw SHA256 modified")
    orig=json.loads((source/"matlab_raw.json").read_bytes())
    anchor=json.loads(anchor_path.read_bytes())
    expected=get_anchor_records(orig)
    check(anchor.get("schema")=="perf01d-original-matlab-native-optimizer-anchors-v1"
          and anchor.get("status")=="FROZEN_50_ANCHORS_BEFORE_PRIVATE_OBJECTIVE_EVALUATION"
          and anchor.get("original_matlab_raw_sha256")==MATLAB_RAW_SHA256
          and anchor.get("source_original_fitting")=="63/64 NONPASS"
          and anchor.get("source_subject_zero_based")==7
          and anchor.get("counts")=={"MATLAB_1":25,"MATLAB_2":25}
          and anchor.get("anchor_indices_zero_based")==list(range(ROWS))
          and anchor.get("cases")==expected,
          "all 50 predeclared source anchor identities changed")
    raw=json.loads(matlab_path.read_bytes())
    check(raw.get("schema")=="perf01d-matlab-nested-objective-v1"
          and raw.get("status")=="INSTRUMENTED_MATLAB_FITMODEL_REAL_NESTED_OBJECTIVE_NOT_SCIENCE_PASS"
          and raw.get("frozen_matlab_sha")==MATLAB_SHA
          and raw.get("frozen_hgfx_sha")==HGFX_SHA
          and raw.get("source_run_id")==SOURCE_RUN
          and raw.get("source_matlab_raw_sha256")==MATLAB_RAW_SHA256
          and raw.get("subject_index_zero_based")==7
          and raw.get("n_trials")==128
          and raw.get("hook_call_count")==1
          and raw.get("original_optimizer_delegated") is True
          and raw.get("no_timing") is True,
          "actual frozen MATLAB nested objective not verified")
    native=orig["cases"][0]
    instr=raw["instrumented_fit"]
    check(instr.get("status")=="INSTRUMENTED_PUBLIC_FIT_OUTPUT_NOT_ORACLE"
          and instr.get("start_matches_native") is True
          and instr.get("no_random_initializations") is True,
          "instrumented public fitting start/restart not verified")
    comparison=compare_pair(instr,native)
    binary=strict_pair(instr,native)
    check(comparison["field_count"]==binary["field_count"]==28,
          "all native public fitting output fields required for neutrality assessment")
    probes=raw.get("cases")
    check(isinstance(probes,list) and len(probes)==len(expected)==50,
          "all 50 original nested MATLAB objective anchor occurrences required")
    inputs=json.loads((root/"inputs"/"binary_128_s64.json").read_bytes())
    check(raw["source_input_sha256"]==rawhash(root/"inputs"/"binary_128_s64.json")
          and raw["source_config_sha256"]==rawhash(root/"configs"/"hgf_binary_128.json"),
          "original frozen model input/config changed")
    u=np.asarray(inputs["u"][7],np.float64)
    y=np.asarray(inputs["y"][7],np.float64)
    problem=hgf_binary_unitsq_fit_problem(y,u)
    check(list(problem.free_indices)==[12,13,14]
          and np.array_equal(problem.initial_free,np.asarray(EXPECTED_START,np.float64)),
          "HGFX exact original three transformed free params/start changed")
    detailed=[]
    for i,(a,m) in enumerate(zip(expected,probes)):
        check(m.get("anchor_origin")==a["anchor_origin"]
              and m.get("record_index_zero_based")==a["record_index_zero_based"]
              and m.get("free_parameters")==a["free_parameters"]
              and m.get("status") in ("EVALUATED","ERROR"),
              "nested MATLAB objective anchor order/coordinates/status changed")
        value=float("nan") if m["status"]=="ERROR" else float(m["nested_objective"])
        h=float(problem.evaluate_free(np.asarray(a["free_parameters"],dtype=np.float64)))
        if m["status"]=="EVALUATED":
            check(math.isfinite(value),"nested objective yielded nonfinite scalar")
            delta=abs(h-value)
            desc_bound=3e-10+3e-8*abs(value)
        else:
            delta=None;desc_bound=None
        detailed.append({
            **a,"matlab_status":m["status"],
            "matlab_nested_objective":value if math.isfinite(value) else None,
            "hgfx_original_evaluate_free_objective":h if math.isfinite(h) else None,
            "abs_difference":delta,
            "original_final_parameter_tolerance_as_descriptive_lens":desc_bound,
            "relative_ratio_to_original_final_parameter_tolerance_as_lens":
                delta/desc_bound if delta is not None else None,
        })
    evaluated=sum(z["matlab_status"]=="EVALUATED" for z in detailed)
    return {
        "schema":"perf01d-original-nested-objective-50-anchor-comparison-v1",
        "status":STATUS,
        "source_six_fit_run_id":SOURCE_RUN,
        "source_six_fit_commit_sha":SOURCE_COMMIT,
        "source_matlab_raw_sha256":MATLAB_RAW_SHA256,
        "new_matlab_hook_raw_sha256":rawhash(matlab_path),
        "new_anchor_source_sha256":rawhash(anchor_path),
        "frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "anchor_occurrences":len(detailed),"matlab_nested_evaluated_count":evaluated,
        "original_64_subject_full_fit":"63/64 NONPASS; subject index 7",
        "native_vs_instrumented_matlab_public_full_28_fields":comparison,
        "native_vs_instrumented_strict_serialized_binary64":binary,
        "instrumentation_neutral_at_original_28_field_tolerances":
            comparison["mismatched_fields"]==[],
        "all_paired_original_nested_objective_evaluations":detailed,
        "original_strict_fit_gate":"63/64 NONPASS",
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "timing":"NOT_RUN",
        "no_reference_limitation_certification":True,
        "interpretation":[
            "This evaluates the actual frozen private MATLAB negLogJoint through an altered optimization callback; frozen MATLAB source files remain unchanged.",
            "The public MATLAB fit is instrumented; per-output neutrality versus the original native public fit must be reviewed before treating objective capture as a faithful oracle.",
            "All 50 anchor occurrences include duplicate history endpoints by protocol; no optimization is run by the HGFX source evaluate_free check.",
            "Inherited final-parameter tolerance on objective data is only a descriptive lens, NOT a preregistered gradient/objective acceptance gate.",
            "The original 63/64 full public fitting failure and eight same-runner out-of-tolerance comparisons remain intact; no timing, GPU, speed or independent review is implied."
        ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=("prepare","compare"),required=True)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--source-six",type=Path,required=True)
    p.add_argument("--anchors",type=Path,required=True)
    p.add_argument("--matlab",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    if args.stage=="prepare":
        report=prepare(args.source_six/"matlab_raw.json",args.anchors,args.root)
        print(json.dumps({"prespecified_anchor_occurrences":len(report["cases"]),
                          "source_run":SOURCE_RUN,"science":"63/64 NONPASS"}))
    else:
        check(args.matlab is not None and args.output is not None,"missing MATLAB or output")
        result=compare(args.root,args.source_six,args.anchors,args.matlab)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
        print(json.dumps({
            "status":STATUS,"anchor_occurrences":result["anchor_occurrences"],
            "matlab_nested_evaluated_count":result["matlab_nested_evaluated_count"],
            "instrumentation_neutral_at_original_28_field_tolerances":
               result["instrumentation_neutral_at_original_28_field_tolerances"],
            "max_objective_abs_delta":max((r["abs_difference"]
                        for r in result["all_paired_original_nested_objective_evaluations"]
                        if r["abs_difference"] is not None),default=None),
            "original_fit":"63/64 NONPASS","perf01c":"NOT_FROZEN",
        },sort_keys=True))
        if result["matlab_nested_evaluated_count"]!=50:
            raise SystemExit("One or more frozen MATLAB nested objective evaluations failed")
        if not result["instrumentation_neutral_at_original_28_field_tolerances"]:
            raise SystemExit("Instrumented MATLAB control fit differs from native public fit under unchanged original tolerances")

if __name__=="__main__":
    main()
