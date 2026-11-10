#!/usr/bin/env python3
"""REV-2.4 D019 prospective *diagnostic-only* MATLAB/HGFX trace comparator.

No new objective gate, no variant switch, no data/parameter changes.
An earliest observed state difference is NOT a demonstrated causal term.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from tools.compstat_rev24_ehgf019_hgfx_trace import (
    DIAGNOSTIC, SOURCE_CASE, SOURCE_CASE_SHA, SOURCE_MANIFEST_SHA,
    MATRIX_FIELDS, STATE_FIELDS, source_case,
)
from tools.compstat_rev24_manifest import (
    FROZEN_RELEASE, MATLAB_REFERENCE, validate_manifest,
)

ORIGINAL_ARCHIVE_SHA256 = "faebd113e9ee050a2490d08e1d1fbc54ba589becd1015d41cab4e7879a785b1c"
ORIGINAL_MEMBERS = {
    "manifest.json": "59d86cb1687944841b802a2d6f4d4f9e2851eb59ba28abf9edbf332668718cec",
    "matlab.json": "54df9fd43c1044f6a7dd6d2c485a9bd76c8da7757d1dee276a4003f31d5b2397",
    "hgfx.json": "70fd09db1efac4d8d4df2e441525216850d302bd9cd0ee315f5681597c701503",
    "comparison.json": "cfd0c7e9f66890c2873706b77518a721119b725a04393ad99ef71e573c780430",
}


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def classify(v):
    if isinstance(v, bool) or v is None:
        raise ValueError("Unsupported latent scalar")
    if isinstance(v, str):
        check(v in ("NaN","+Inf","-Inf"),
              "Unsupported source scalar string")
        return v
    check(type(v) in (float,int),"Not an original numeric scalar")
    x=float(v)
    if math.isnan(x):
        raise ValueError("Non-standard raw JSON NaN encoding")
    check(math.isfinite(x),"Nonfinite source must be string-encoded")
    return "FINITE"


def values_checked(trace, side):
    check(trace.get("diagnostic")==DIAGNOSTIC
          and trace.get("source")==side
          and trace.get("source_manifest_sha256")==SOURCE_MANIFEST_SHA
          and trace.get("source_case_id")==SOURCE_CASE
          and trace.get("source_case_sha256")==SOURCE_CASE_SHA
          and trace.get("release_source_commit")==FROZEN_RELEASE
          and trace.get("matlab_reference_commit")==MATLAB_REFERENCE
          and trace.get("trials")==128
          and trace.get("levels")==3
          and trace.get("original_600_case_grid_modified") is False
          and trace.get("scientific_gate")=="NOT_ASSESSED_DIAGNOSTIC_ONLY",
          f"{side}: source identity changed")
    check(set(trace.get("inferred_states",{}))==set(STATE_FIELDS),
          f"{side}: missing inferred state")
    check(set(trace.get("trajectories",{}))==set(MATRIX_FIELDS),
          f"{side}: missing trajectory")
    check(len(trace.get("trial_log_likelihoods",[]))==128,
          f"{side}: original response length changed")
    for x in trace["trial_log_likelihoods"]:
        classify(x)
    for family, names in (("inferred_states",STATE_FIELDS),
                          ("trajectories",MATRIX_FIELDS)):
        for name in names:
            matrix=trace[family][name]
            expected_cols=2 if name=="w" and family=="trajectories" else 3
            check(isinstance(matrix,list) and len(matrix)==128,
                  f"{side}/{family}/{name}: wrong trial dimension")
            for row in matrix:
                check(isinstance(row,list) and len(row)==expected_cols,
                      f"{side}/{family}/{name}: wrong level dimension")
                for entry in row:classify(entry)


def first_status_event(reference, test, context):
    for t,(lrow,rrow) in enumerate(zip(reference,test)):
        for level,(a,b) in enumerate(zip(lrow,rrow)):
            ca,cb=classify(a),classify(b)
            if ca!=cb:
                return {
                    "trial_zero_based":t,
                    "level_zero_based":level,
                    "location":context,
                    "matlab_status":ca,
                    "hgfx_status":cb,
                    "matlab_value":a,
                    "hgfx_value":b,
                }
    return None


def paired_numeric_summary(reference,test,context):
    checked=0;max_abs=0.;first=None
    for t,(lrow,rrow) in enumerate(zip(reference,test)):
        for level,(a,b) in enumerate(zip(lrow,rrow)):
            if classify(a)==classify(b)=="FINITE":
                checked+=1
                delta=abs(float(a)-float(b))
                if delta>max_abs:max_abs=delta
                if delta!=0 and first is None:
                    first={"trial_zero_based":t,
                           "level_zero_based":level,
                           "location":context,
                           "matlab_value":a,"hgfx_value":b,
                           "absolute_difference":delta}
    return {"both_finite_elements":checked,"max_abs_difference":max_abs,
            "first_nonidentical_finite":first,
            "numeric_gate":"NONE_PREDECLARED_FOR_EHGF"}


def likelihood_status_reproduction(original,diagnostic):
    a=original["trial_log_likelihoods"]
    b=diagnostic["trial_log_likelihoods"]
    check(len(a)==len(b)==128,"Original 128-trial source missing")
    mismatch=[
        {"trial_zero_based":i,"archived":classify(x),
         "diagnostic":classify(y)}
        for i,(x,y) in enumerate(zip(a,b)) if classify(x)!=classify(y)
    ]
    return {"archived_valid":original["valid"],
            "diagnostic_all_finite":all(classify(x)=="FINITE" for x in b),
            "nonfinite_status_reproduced":not mismatch,
            "first_status_disagreement":mismatch[0] if mismatch else None,
            "archived_nonfinite_first_trial":next(
                (i for i,x in enumerate(a) if classify(x)!="FINITE"),None),
            "diagnostic_nonfinite_first_trial":next(
                (i for i,x in enumerate(b) if classify(x)!="FINITE"),None)}


def compare(manifest, matlab, hgfx, original_matlab, original_hgfx):
    validate_manifest(manifest)
    group,case=source_case(manifest)
    check(case["case_sha256"]==SOURCE_CASE_SHA,"Manifest case changed")
    values_checked(matlab,"matlab")
    values_checked(hgfx,"hgfx")
    original_pair=[]
    for name,src in (("matlab",original_matlab),("hgfx",original_hgfx)):
        cases=src.get("cases")
        check(isinstance(cases,list) and len(cases)==600,
              f"Original {name} source grid missing")
        row=cases[219]
        check(row["case_id"]==SOURCE_CASE
              and row["case_sha256"]==SOURCE_CASE_SHA
              and row["model"]=="ehgf_binary"
              and row["config_sha256"]==group["config_sha256"],
              f"Original {name} 019 identity mismatch")
        original_pair.append(row)
    original_against_trace={
        "matlab":likelihood_status_reproduction(original_pair[0],matlab),
        "hgfx":likelihood_status_reproduction(original_pair[1],hgfx),
    }
    rows=[];status_events=[];numeric=[]
    for family,names in (("inferred_states",STATE_FIELDS),
                         ("trajectories",MATRIX_FIELDS)):
        for name in names:
            context=family+"."+name
            left=matlab[family][name]
            right=hgfx[family][name]
            event=first_status_event(left,right,context)
            numerics=paired_numeric_summary(left,right,context)
            rows.append({"field":context,"first_finite_status_difference":event,
                         **numerics})
            if event is not None: status_events.append(event)
            if numerics["first_nonidentical_finite"] is not None:
                numeric.append(numerics["first_nonidentical_finite"])
    left=[[x] for x in matlab["trial_log_likelihoods"]]
    right=[[x] for x in hgfx["trial_log_likelihoods"]]
    event=first_status_event(left,right,"observation.trial_log_likelihoods")
    numerics=paired_numeric_summary(left,right,"observation.trial_log_likelihoods")
    rows.append({"field":"observation.trial_log_likelihoods",
                 "first_finite_status_difference":event,**numerics})
    if event:status_events.append(event)
    if numerics["first_nonidentical_finite"]:numeric.append(
        numerics["first_nonidentical_finite"])
    status_events.sort(key=lambda e:(e["trial_zero_based"],
                                      e["location"].startswith("observation."),
                                      e["location"],e["level_zero_based"]))
    numeric.sort(key=lambda e:(e["trial_zero_based"],e["location"],
                               e["level_zero_based"]))
    first=status_events[0] if status_events else None
    obs=next(r["first_finite_status_difference"] for r in rows
             if r["field"]=="observation.trial_log_likelihoods")
    reproducible=all(x["nonfinite_status_reproduced"]
                     for x in original_against_trace.values())
    observed_classification=(
        "ORIGINAL_STATUS_NOT_REPRODUCED" if not reproducible else
        "UNRESOLVED" if first is None else
        "STATE_FINITE_STATUS_ASYMMETRY" if first["location"].startswith(
            ("inferred_states.","trajectories.")) else
        "OBSERVATION_ONLY_INVALID"
    )
    return {
        "diagnostic":DIAGNOSTIC,
        "case_id":SOURCE_CASE,
        "case_sha256":SOURCE_CASE_SHA,
        "original_panel_g_manifest_sha256":SOURCE_MANIFEST_SHA,
        "original_panel_g_zip_sha256":ORIGINAL_ARCHIVE_SHA256,
        "matlab_trace_sha256":hashlib.sha256(json.dumps(
            matlab,sort_keys=True,separators=(",",":"),allow_nan=False
            ).encode()).hexdigest(),
        "hgfx_trace_sha256":hashlib.sha256(json.dumps(
            hgfx,sort_keys=True,separators=(",",":"),allow_nan=False
            ).encode()).hexdigest(),
        "source_trace_status_reproduction":original_against_trace,
        "first_finite_status_difference":first,
        "first_nonidentical_finite_value":numeric[0] if numeric else None,
        "first_observation_finite_status_difference":obs,
        "all_field_checks":rows,
        "diagnostic_classification":observed_classification,
        "causal_expression_and_mechanism":"NOT_ESTABLISHED",
        "scientific_gate":"NOT_GLOBAL_PASS",
        "model_family_objective_gate":"NO_PREDECLARED_FAMILY_OBJECTIVE_GATE",
        "original_one_sided_invalid_reclassified":False,
        "original_global_600_row_grid_replaced":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for item in ("manifest","matlab_trace","hgfx_trace",
                 "original_matlab","original_hgfx","output"):
        p.add_argument("--"+item.replace("_","-"),type=Path,required=True)
    args=p.parse_args()
    check(not args.output.exists(),"Refuse overwrite of original trace diagnostic")
    read=lambda path:json.loads(path.read_text(encoding="utf-8"))
    result=compare(read(args.manifest),read(args.matlab_trace),
                   read(args.hgfx_trace),read(args.original_matlab),
                   read(args.original_hgfx))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,
                                      allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "classification":result["diagnostic_classification"],
        "first_status_event":result["first_finite_status_difference"],
        "first_observation_event":result["first_observation_finite_status_difference"],
        "archived_status_reproduced":all(
            v["nonfinite_status_reproduced"] for
            v in result["source_trace_status_reproduction"].values()),
        "causal_mechanism":result["causal_expression_and_mechanism"],
        "output_sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "scientific_gate":result["scientific_gate"]
    },sort_keys=True))


if __name__=="__main__":main()
