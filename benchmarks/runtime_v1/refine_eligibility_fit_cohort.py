#!/usr/bin/env python3
"""PERF-01C author-only update of original 28-cell candidate from all-64 fit.

Creates a NEW immutable derived candidate. The prior 28-cell JSON, raw
failed fitting result, frozen inputs and acceptance tolerances stay unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ORIGINAL_STATUS="AUTHOR_SIDE_INVENTORY_ONLY_NOT_REVIEWED_NOT_FROZEN_NOT_TIMED"
FIT_STATUS="UNFROZEN_DIAGNOSTIC_NO_TIMING_NO_SCIENTIFIC_PASS"
OLD_BLOCKED="BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED"
NEW_BLOCKED="BLOCKED_MULTISUBJECT_FIT_NUMERICAL_MISMATCH"
FIT_SUCCESS="FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
FIT_MISMATCH="FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refine(original, full_fit):
    if (original.get("status")!=ORIGINAL_STATUS
        or original.get("schema")!="perf01-prospective-eligibility-candidate-v1"
        or original.get("total_predeclared_cases")!=28
        or len(original.get("cases",[]))!=28
        or len(set(c["case_id"] for c in original["cases"]))!=28
        or full_fit.get("schema")!="perf01-paired-full-cohort-fit-diagnostic-v1"
        or full_fit.get("status")!=FIT_STATUS
        or full_fit.get("hgfx_sha")!=original["frozen_source_sha"]
        or full_fit.get("matlab_sha")!=original["frozen_matlab_sha"]
        or full_fit.get("subject_count")!=64):
        raise ValueError("Incompatible or incomplete original/fitting evidence")
    if [s["subject_count"] for s in full_fit["by_prefix"]] != [1,16,64]:
        raise ValueError("The original nested cohort has been changed")
    fits={int(x["subject_index_zero_based"]):x for x in full_fit["cases"]}
    if len(fits)!=64 or set(fits)!=set(range(64)):
        raise ValueError("Missing or duplicate fit subjects in original evidence")
    original_by_id={c["case_id"]:c for c in original["cases"]}
    target_ids={"throughput_fit_1x128","throughput_fit_16x128","throughput_fit_64x128"}
    if not target_ids.issubset(original_by_id):
        raise ValueError("Missing original 1/16/64 throughput cell")
    rows=[]
    for case in original["cases"]:
        row=dict(case)
        if row["case_id"] in target_ids:
            prefix=int(row["subjects"])
            subset=[fits[k] for k in range(prefix)]
            n_success=sum(x["classification"]==FIT_SUCCESS for x in subset)
            n_mismatch=sum(x["classification"]==FIT_MISMATCH for x in subset)
            n_other=prefix-n_success-n_mismatch
            row["additional_fitting_evidence"]={
                "source_run_id":"41863441006",
                "submitted":prefix,
                "same_numerical_output":n_success,
                "numerical_mismatch":n_mismatch,
                "other_failures_or_noncomparable":n_other,
                "scientific_status":"DIAGNOSTIC_ONLY_NOT_INDEPENDENTLY_APPROVED",
            }
            if n_mismatch or n_other:
                if row["classification"]!=OLD_BLOCKED:
                    raise ValueError("Refusing to silently replace an unexpected old case status")
                row["previous_classification"]=row["classification"]
                row["classification"]=NEW_BLOCKED if n_mismatch else "BLOCKED_FITTING_FAILURE_OR_NONCOMPARABLE"
            elif row["classification"] not in ("DIAGNOSTIC_CONCORDANT_REVIEW_PENDING",OLD_BLOCKED):
                raise ValueError("Unexpected original evidence decision for cohort")
            # Do not promote any blocked case as PASS without separate
            # independently reviewed scientific acceptance, even if numerics match.
        rows.append(row)
    counts=dict(sorted(Counter(x["classification"] for x in rows).items()))
    return {
        "schema":"perf01-prospective-eligibility-candidate-v2-derived",
        "status":ORIGINAL_STATUS,
        "protocol_id":"hgfx-matlab-runtime-1",
        "original_candidate_status_preserved":True,
        "original_cases_total":28,
        "primary_nine_aggregate_eligible":False,
        "independent_review":"NOT_RECEIVED",
        "no_timing":True,
        "classification_counts":counts,
        "blocked_case_ids":[x["case_id"] for x in rows if x["classification"].startswith("BLOCKED")],
        "cases":rows,
        "new_fitting_source_run_id":"41863441006",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--fit",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=refine(json.loads(a.original.read_bytes()),json.loads(a.fit.read_bytes()))
    result["source_evidence_sha256"]={
        "original_candidate":digest(a.original),
        "64_subject_fit_diagnostic":digest(a.fit),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"total":len(result["cases"]),"counts":result["classification_counts"]},sort_keys=True))


if __name__=="__main__":
    main()
