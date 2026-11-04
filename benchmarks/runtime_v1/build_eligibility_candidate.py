#!/usr/bin/env python3
"""PERF-01C author-side, fail-closed, 28-case pre-freeze eligibility inventory.

Machine classification is NOT independent scientific approval and does not
authorize timing. All originally preregistered cases stay in the output.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def indexed(rows, key):
    out={}
    for item in rows:
        k=key(item)
        if k in out:
            raise ValueError(f"Duplicate evidence key: {k}")
        out[k]=item
    return out


def classify(manifest, trialwise, fitting, cohort):
    if manifest.get("protocol_id")!="hgfx-matlab-runtime-1" or len(manifest.get("cases",[]))!=28:
        raise ValueError("Original 28-case protocol registry missing")
    if trialwise.get("schema")!="hgfx-perf01-trialwise-comparison-v1":
        raise ValueError("Missing accepted trialwise evidence format")
    if fitting.get("schema")!="perf01-fit-comparison-v1":
        raise ValueError("Missing fitting evidence")
    if cohort.get("schema")!="perf01-all-subject-paired-diagnostic-v1":
        raise ValueError("Missing all-64-subject evidence")
    if cohort.get("hgfx_source_sha")!="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27" or cohort.get("matlab_oracle_sha")!="2437f4dc241541072722a2695ddeca7b44d83dd3":
        raise ValueError("Wrong frozen comparator")
    keys=[case["id"] for case in manifest["cases"]]
    if len(set(keys))!=28:
        raise ValueError("Original case registry duplicates")
    tr=indexed(trialwise["rows"],lambda x:(x["model"],x["trials"],bool(x["masked"])))
    ft=indexed(fitting["rows"],lambda x:x["n_trials"])
    subjects=indexed(cohort["rows"],lambda x:(x["model"],x["trials"],x["subject_index_zero_based"]))
    if len(tr)!=10 or len(ft)!=3 or len(subjects)!=576:
        raise ValueError("Incomplete diagnostic evidence; fail closed")
    assert len(cohort["strata"])==27
    if cohort["input_manifest_sha256"]!=manifest.get("_bytes_sha256"):
        raise ValueError("Source input manifest SHA changed after scientific evidence")
    if trialwise.get("status")!="EXPLORATORY_NOT_FROZEN_NOT_FINAL_SCIENTIFIC_GATE":
        raise ValueError("Unexpected trialwise gate status")
    if fitting.get("status")!="DIAGNOSTIC_ONLY_UNFROZEN_NO_PERFORMANCE":
        raise ValueError("Unexpected fit gate status")
    strata=indexed(cohort["strata"],lambda x:(x["model"],x["trials"],x["submitted_subjects"]))
    for model in ("hgf_binary","ehgf_binary","uhgf_binary"):
        for n in (128,512,1024):
            for k in (1,16,64):
                record=strata[(model,n,k)]
                if record["matlab_objective_completed"]+record["both_invalid_reference_behavior_pairs"]+record["blocked_or_mismatched_subjects"]!=k:
                    raise ValueError(f"Data accounting mismatch {model}/{n}/{k}")
    trial_pass="FULL_TRIALWISE_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"
    trial_invalid="BOTH_FAILED_FIRST_INVALID_PREFIX_AGREES_UNVERIFIED_MECHANISM"
    fit_pass="FULL_FIT_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
    fit_block="BLOCKED_UNSTABLE_DEFAULT_START_NONCOMPARABLE_RESTART_POLICY"
    matched_scalar="COMPLETED_SCALAR_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"
    ref_invalid="BOTH_INVALID_REFERENCE_BEHAVIOR_MATCH_DIAGNOSTIC"
    rows=[]
    for c in manifest["cases"]:
        model=c["model"]
        n=c["n_trials"]
        tier=c["tier"]
        trial=tr.get((model,n,tier=="robustness"))
        stage=c["stage"]
        cohort_k=strata.get((model,n,64))
        record={
            "case_id":c["id"],"tier":tier,"model":model,
            "stage":stage,"trials":n,"subjects":c["subjects"],
            "source_file":c["source_file"],"source_sha256":c["source_sha256"],
            "classification":"BLOCKED_INCOMPLETE_SCIENTIFIC_EVIDENCE",
            "review_status":"INDEPENDENT_REVIEW_REQUIRED_NOT_FROZEN",
        }
        if tier=="primary":
            if n==128 and trial and trial["diagnostic_classification"]==trial_pass:
                if stage in ("forward","objective"):
                    record["classification"]="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
                elif stage=="fit_compat_full" and ft[n]["classification"]==fit_pass:
                    record["classification"]="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
            elif n in (512,1024) and trial and trial["diagnostic_classification"]==trial_invalid:
                if stage=="fit_compat_full" and ft[n]["classification"]==fit_block:
                    record["classification"]="BLOCKED_NONCOMPARABLE_FITTING_START_POLICY"
                elif stage in ("forward","objective"):
                    record["classification"]="BLOCKED_INVALID_FROZEN_REFERENCE_WORKLOAD"
        elif tier=="secondary":
            if (trial and trial["diagnostic_classification"]==trial_pass
                and cohort_k and cohort_k["completed_scalar_pairs"]==64
                and cohort_k["blocked_or_mismatched_subjects"]==0):
                record["classification"]="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
        elif tier=="throughput":
            k=c["subjects"]
            subset=strata.get((model,n,k))
            if n==128 and subset and subset["completed_scalar_pairs"]==k:
                if k==1 and ft[n]["classification"]==fit_pass:
                    record["classification"]="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
                else:
                    record["classification"]="BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED"
            elif n==512 and subset and subset["both_invalid_reference_behavior_pairs"]==k and ft[n]["classification"]==fit_block:
                record["classification"]="BLOCKED_INVALID_FROZEN_REFERENCE_WORKLOAD"
        elif tier=="robustness":
            if trial and trial["diagnostic_classification"]==trial_invalid:
                record["classification"]="BLOCKED_INVALID_FROZEN_REFERENCE_WORKLOAD"
        rows.append(record)
    counts=dict(sorted(Counter(x["classification"] for x in rows).items()))
    blocked=[x["case_id"] for x in rows if x["classification"].startswith("BLOCKED")]
    primary=[x for x in rows if x["tier"]=="primary"]
    return {
        "schema":"perf01-prospective-eligibility-candidate-v1",
        "protocol_id":"hgfx-matlab-runtime-1",
        "status":"AUTHOR_SIDE_INVENTORY_ONLY_NOT_REVIEWED_NOT_FROZEN_NOT_TIMED",
        "frozen_source_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "frozen_matlab_sha":"2437f4dc241541072722a2695ddeca7b44d83dd3",
        "total_predeclared_cases":len(rows),
        "primary_cases":len(primary),
        "all_nine_primary_eligible":all(
            x["classification"]=="DIAGNOSTIC_CONCORDANT_REVIEW_PENDING"
            for x in primary
        ),
        "original_nine_primary_headline":"NOT_AUTHORIZED_UNLESS_ALL_NINE_ELIGIBLE_AND_FINAL_PROTOCOL_FROZEN",
        "classification_counts":counts,
        "blocked_case_ids":blocked,
        "cases":rows,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("manifest","trialwise","fitting","cohort","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    source=json.loads(a.manifest.read_bytes())
    source["_bytes_sha256"]=sha256(a.manifest)
    obj=classify(source,json.loads(a.trialwise.read_bytes()),
        json.loads(a.fitting.read_bytes()),json.loads(a.cohort.read_bytes()))
    obj["evidence_sha256"]={k:sha256(getattr(a,k)) for k in
        ("manifest","trialwise","fitting","cohort")}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"total":obj["total_predeclared_cases"],
        "counts":obj["classification_counts"],
        "primary_all_eligible":obj["all_nine_primary_eligible"]},sort_keys=True))
    if any(x["classification"]=="BLOCKED_INCOMPLETE_SCIENTIFIC_EVIDENCE"
           for x in obj["cases"]):
        raise SystemExit("Evidence incomplete or unexpected; candidate frozen gate denied")


if __name__=="__main__":
    main()
