#!/usr/bin/env python3
"""REV-2.4 Panel E: fail-closed 66-original-case, 132-slot paired objective audit.

Only this SANITIZED audit may be made public; full original trial data,
endpoint parameter vectors and per-trial likelihoods stay private.
No acceptance gate is invented for eHGF/uHGF.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

from tools.compstat_rev24_panel_e_inputs import PROTOCOL,digest
from tools.compstat_rev24_panel_e_hgfx import EXPECTED,validate_inputs

HGF_M8_ATOL = 2e-13
HGF_M8_RTOL = 2e-11
FIELDS=("log_likelihood","neg_log_likelihood","neg_log_joint",
        "perceptual_prior_total","observation_prior_total")
SOURCES=("matlab","hgfx")


def check(ok,msg):
    if not ok:raise ValueError(msg)


def finite(value):
    if isinstance(value,bool) or isinstance(value,str) or value is None:
        return None
    if not isinstance(value,(int,float)):return None
    return float(value) if math.isfinite(value) else None


def sha(doc):
    return hashlib.sha256(
        json.dumps(doc,sort_keys=True,separators=(",",":"),
                   allow_nan=False).encode("utf-8")).hexdigest()


def first_trial_difference(left,right,length,threshold_defined):
    if not isinstance(left,list) or not isinstance(right,list) or (
        len(left)!=length or len(right)!=length):
        return {"reason":"UNAVAILABLE_OR_WRONG_TRIAL_LENGTH"}
    for t,(a,b) in enumerate(zip(left,right)):
        x,y=finite(a),finite(b)
        if x is None or y is None:
            return {"trial_zero_based":t,"reason":"NONFINITE_OR_MISSING"}
        limit=HGF_M8_ATOL+HGF_M8_RTOL*abs(x)
        if (abs(x-y)>limit) if threshold_defined else (x!=y):
            return {"trial_zero_based":t,
                    "reason":"OUTSIDE_FROZEN_HGF_GATE" if threshold_defined
                             else "NUMERICALLY_DIFFERENT_NO_FAMILY_GATE",
                    "absolute_difference":abs(x-y)}
    return None


def verify_output(doc,side,inputs):
    check(doc.get("protocol")==PROTOCOL and doc.get("panel")=="E"
          and doc.get("source")==side,
          f"{side}: wrong source identity")
    check(doc.get("release_source_commit")==
          "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
          f"{side}: wrong original HGFX release")
    check(doc.get("matlab_reference_commit")==
          "2437f4dc241541072722a2695ddeca7b44d83dd3",
          f"{side}: wrong frozen MATLAB oracle")
    check(doc.get("original_cohort_inputs_sha256",
                  inputs["original_cohort_inputs_sha256"]) ==
                  inputs["original_cohort_inputs_sha256"],
          f"{side}: original cohort data hash drift")
    if side=="hgfx":
        check(doc.get("private_source_sha256")==digest(inputs),
              "HGFX private original input hash drift")
    rows=doc.get("cases")
    check(isinstance(rows,list) and len(rows)==132,
          f"{side}: 132 slots including missing D02 mandatory")
    for i,case in enumerate(inputs["cases"]):
        for ei,endpoint in enumerate(SOURCES):
            row=rows[2*i+ei]
            check(row.get("case_id")==case["case_id"] and
                  row.get("case_sha256")==case["case_sha256"] and
                  row.get("at_original_endpoint")==endpoint and
                  row.get("source")==side and
                  row.get("model")==case["perceptual_model"] and
                  row.get("observation_model")==case["observation_model"],
                  f"{side}: case/endpoint source drift at {case['case_id']}/{endpoint}")
            check(isinstance(row.get("valid"),bool) and
                  type(row.get("rval")) is int,
                  f"{side}: explicit validity and rval mandatory")
            if i==0 and endpoint=="hgfx":
                check(row["status"]=="INSUFFICIENT_REFERENCE_EVIDENCE",
                      f"{side}: cannot fabricate original D02 HGFX endpoint")
            else:
                check(row["status"] in
                      ("VALID","INVALID_OBJECTIVE","EVALUATION_ERROR"),
                      f"{side}: unexplained missing endpoint")
            if row["valid"]:
                check(row["status"]=="VALID" and row["rval"]==0,
                      f"{side}: valid outcome inconsistent")
                check(all(finite(row.get(field)) is not None for field in FIELDS),
                      f"{side}: valid numeric fields absent")
                check(isinstance(row.get("trial_log_likelihoods"),list)
                      and len(row["trial_log_likelihoods"])==case["trials"]
                      and all(finite(x) is not None for x in row["trial_log_likelihoods"]),
                      f"{side}: valid per-trial likelihoods absent")
    return rows


def audit(inputs,matlab,hgfx):
    cases=validate_inputs(inputs)
    ml=verify_output(matlab,"matlab",inputs)
    hg=verify_output(hgfx,"hgfx",inputs)
    result=[]
    groups={}
    for i,case in enumerate(cases):
        model=case["perceptual_model"]
        group=groups.setdefault(model,Counter())
        for ei,endpoint in enumerate(SOURCES):
            m,h=ml[2*i+ei],hg[2*i+ei]
            record={
                "case_id":case["case_id"],
                "case_sha256":case["case_sha256"],
                "model":model,"observation_model":case["observation_model"],
                "at_original_endpoint":endpoint,
                "matlab_valid":m["valid"],"hgfx_valid":h["valid"],
                "matlab_status":m["status"],"hgfx_status":h["status"],
                "first_causal_state":"NOT_EXPORTED",
                "gradient":"NOT_AVAILABLE",
            }
            if case["endpoints"][endpoint] is None:
                category="INSUFFICIENT_REFERENCE_EVIDENCE"
            elif not m["valid"] and not h["valid"]:
                category="SHARED_INVALID_OBJECTIVE"
            elif m["valid"]!=h["valid"]:
                category="ONE_SIDED_INVALID"
            else:
                discrepancies={}
                within=True
                for field in FIELDS:
                    a,b=finite(m[field]),finite(h[field])
                    check(a is not None and b is not None,"Both valid but missing numeric fields")
                    diff=abs(a-b)
                    discrepancies[field]={"abs_difference":diff}
                    if model=="hgf_binary":
                        limit=HGF_M8_ATOL+HGF_M8_RTOL*abs(a)
                        discrepancies[field]["frozen_gate_limit"]=limit
                        discrepancies[field]["within_gate"]=diff<=limit
                        if diff>limit:within=False
                first=first_trial_difference(
                    m["trial_log_likelihoods"],h["trial_log_likelihoods"],
                    case["trials"],model=="hgf_binary")
                record["first_likelihood_difference"]=first
                record["objective_field_abs_differences"]=discrepancies
                if model=="hgf_binary":
                    category=("SHARED_OBJECTIVE_WITHIN_EXISTING_GATE" if
                              within and first is None else
                              "SHARED_OBJECTIVE_MISMATCH")
                else:
                    category="NO_PREDECLARED_FAMILY_OBJECTIVE_GATE"
            record["classification"]=category
            group[category]+=1
            result.append(record)
    check(len(result)==132,"Panel E source row denominator must stay 132")
    check(sum(x["classification"]=="INSUFFICIENT_REFERENCE_EVIDENCE"
              for x in result)==1,"Expected exactly one missing D02 endpoint slot")
    return {
        "protocol":PROTOCOL,"panel":"E",
        "scope":"ORIGINAL_66_CASES_132_ENDPOINTS_PAIRED_OBJECTIVES_ONLY",
        "source_archive_sha256":inputs["source_sha256"],
        "original_cohort_inputs_sha256":inputs["original_cohort_inputs_sha256"],
        "private_input_sha256":digest(inputs),
        "private_matlab_output_sha256":sha(matlab),
        "private_hgfx_output_sha256":sha(hgfx),
        "scientific_gate":"NOT_GLOBAL_PASS",
        "case_denominator":66,"endpoint_slot_denominator":132,
        "total_valid_both":sum(m["valid"] and h["valid"]
                               for m,h in zip(ml,hg)),
        "summary_by_model":{model:{"endpoint_slots":
            sum(x["model"]==model for x in result), **dict(group)}
            for model,group in groups.items()},
        "cases":result,
        "includes_trial_data_or_full_endpoints":False,
        "history_reclassified":False,
        "scientific_interpretation":"OBJECTIVE_ONLY_NOT_FITTING_OR_IDENTIFIABILITY",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("private_input","private_matlab","private_hgfx","sanitized_output"):
        p.add_argument("--"+key.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    check(not a.sanitized_output.exists(),"Refuse overwrite of scientific audit")
    doc=json.loads(a.private_input.read_text(encoding="utf-8"))
    mat=json.loads(a.private_matlab.read_text(encoding="utf-8"))
    hg=json.loads(a.private_hgfx.read_text(encoding="utf-8"))
    out=audit(doc,mat,hg)
    a.sanitized_output.parent.mkdir(parents=True,exist_ok=True)
    a.sanitized_output.write_text(
        json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "endpoint_slots":out["endpoint_slot_denominator"],
        "source_cases":out["case_denominator"],
        "paired_valid":out["total_valid_both"],
        "summary":out["summary_by_model"],
        "science":out["scientific_gate"],
        "sha256":hashlib.sha256(a.sanitized_output.read_bytes()).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":main()
