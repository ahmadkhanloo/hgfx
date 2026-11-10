#!/usr/bin/env python3
"""REV-2.4 posthoc bounds from EXISTING original fit values and Panel E audit.

No fitting, MATLAB call or numerical objective evaluation. Mathematical
triangle-inequality bounds are NOT original acceptance gates. Public output
is aggregated and contains no original source endpoints or trial data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from tools.compstat_rev24_endpoint_sources import (
    SOURCES, audit_archive, require, sha256_bytes,
)
from tools.compstat_rev24_endpoint_coverage import (
    COHORT_INPUT_SHA256, read_zip_json,
)

FROZEN_PANEL_E_COMPARISON_SHA256 = (
    "051aea43a11f7788b85d64a9cb8e82a59a274a70aa347f1927920d991a8ce86d"
)
PROTOCOL = "compstat-rev2-4-objective-cross-eval-v1"


def finite(value,label):
    require(type(value) in (int,float) and math.isfinite(value),
            f"{label}: original fitted objective missing/nonfinite")
    return float(value)


def endpoint_bound(archived_matlab_at_its_endpoint,
                   archived_hgfx_at_its_endpoint,
                   same_vector_delta_at_matlab_endpoint,
                   same_vector_delta_at_hgfx_endpoint):
    """Exact triangle bound using only already-measured scalar absolutes.

    Let a=M(x_M), b=H(x_H), d_M=|M(x_M)-H(x_M)|, d_H=|M(x_H)-H(x_H)|.
    Then |M(x_M)-M(x_H)| lies in [max(0,|a-b|-d_H), |a-b|+d_H],
    while |H(x_M)-H(x_H)| is analogously bounded with d_M.
    """
    a=finite(archived_matlab_at_its_endpoint,"MATLAB original fit")
    b=finite(archived_hgfx_at_its_endpoint,"HGFX original fit")
    dm=finite(same_vector_delta_at_matlab_endpoint,"same-vector at MATLAB")
    dh=finite(same_vector_delta_at_hgfx_endpoint,"same-vector at HGFX")
    require(dm>=0 and dh>=0,"Negative absolute same-vector discrepancy")
    gap=abs(a-b)
    return {
        "observed_cross_fit_objective_gap": gap,
        "matlab_endpoint_objective_gap_lower_bound": max(0.0,gap-dh),
        "matlab_endpoint_objective_gap_upper_bound": gap+dh,
        "hgfx_endpoint_objective_gap_lower_bound": max(0.0,gap-dm),
        "hgfx_endpoint_objective_gap_upper_bound": gap+dm,
    }


def compare_pair(rows,case_id,model):
    require(isinstance(rows,list) and len(rows)==2,
            f"{case_id}: missing or duplicate original endpoint pair")
    a,b=rows
    for row,side in ((a,"matlab"),(b,"hgfx")):
        require(row.get("case_id")==case_id and
                row.get("at_original_endpoint")==side and
                row.get("model")==model,
                f"{case_id}: wrong source or endpoint order")
        require(row.get("matlab_valid") is True and
                row.get("hgfx_valid") is True,
                f"{case_id}: original paired objective invalid")
    return (
        finite(a["objective_field_abs_differences"]["neg_log_joint"]["abs_difference"],
               f"{case_id}/matlab"),
        finite(b["objective_field_abs_differences"]["neg_log_joint"]["abs_difference"],
               f"{case_id}/hgfx")
    )


def compute_bounds(d08_data,d08_comparison,matlab_raw,hgfx_raw,paired):
    require(paired.get("protocol")==PROTOCOL and paired.get("panel")=="E"
            and paired.get("case_denominator")==66
            and paired.get("endpoint_slot_denominator")==132
            and paired.get("scientific_gate")=="NOT_GLOBAL_PASS"
            and paired.get("original_cohort_inputs_sha256")==COHORT_INPUT_SHA256,
            "Wrong original paired Panel E source/report identity")
    rows=paired.get("cases")
    require(isinstance(rows,list) and len(rows)==132,
            "All original Panel E endpoint slots mandatory")
    d02=rows[:2]
    require(d02[0]["case_id"]=="D02_fit"
            and d02[1]["classification"]=="INSUFFICIENT_REFERENCE_EVIDENCE",
            "D02 absent original HGFX endpoint must remain missing")
    require(d08_data["case_id"]=="D08_fit"
            and d08_data["model"]=="uhgf"
            and d08_data["observation"]=="gaussian_obs",
            "D08 source model must not be substituted")
    d08m,d08h=compare_pair(rows[2:4],"D08_fit","uhgf")
    original_d08_ml=finite(d08_data["negLj"],"D08 original MATLAB fit")
    orig_d08=d08_comparison["objective"]
    require(original_d08_ml==
            finite(orig_d08["matlab_negLj"],"D08 independent MATLAB source"),
            "D08 original MATLAB fit objective inconsistent")
    d08_bound=endpoint_bound(
        original_d08_ml,orig_d08["hgfx_fit_negLj"],d08m,d08h)

    require(matlab_raw.get("model")==hgfx_raw.get("model")=="hgf_binary"
            and matlab_raw.get("observation_model")==hgfx_raw.get("observation_model")=="unitsq_sgm"
            and len(matlab_raw.get("cases",[]))==len(hgfx_raw.get("cases",[]))==64,
            "Original 64-subject frozen fit source incomplete")
    require(hgfx_raw.get("input_sha256")==COHORT_INPUT_SHA256,
            "Original 64 input identity mismatch")
    all_bounds=[]
    for i in range(64):
        original_ml=matlab_raw["cases"][i]
        original_h=hgfx_raw["cases"][i]
        require(original_ml.get("subject_index_zero_based")==
                original_h.get("subject_index_zero_based")==i,
                "Source subject order changed")
        cid=f"cohort64_subject_{i:02d}"
        dm,dh=compare_pair(rows[4+2*i:6+2*i],cid,"hgf_binary")
        bounds=endpoint_bound(
            original_ml["optim"]["negLj"],original_h["optim"]["negLj"],
            dm,dh)
        bounds["subject_zero_based"]=i
        all_bounds.append(bounds)

    def extremum(field):
        row=max(all_bounds,key=lambda rec:rec[field])
        return {"subject_zero_based":row["subject_zero_based"],
                "value":row[field]}

    return {
        "protocol":PROTOCOL,"panel":"E","kind":"POSTHOC_ORIGINAL_FIT_ENDPOINT_BOUNDS_NO_REPLAY",
        "original_subjects":64,"complete_original_endpoint_pairs":65,
        "missing_original_hgfx_endpoint":["D02_fit"],
        "science_execution":"NONE_NEW",
        "accepted_as_new_gate":False,
        "reported_panel_e_science_gate":"NOT_GLOBAL_PASS",
        "d08":{"endpoint_model":"uhgf+gaussian_obs",**d08_bound},
        "cohort64":{
            "model":"hgf_binary+unitsq_sgm",
            "max_observed_cross_fit_objective_gap":
                extremum("observed_cross_fit_objective_gap"),
            "median_observed_cross_fit_objective_gap":
                statistics.median(rec["observed_cross_fit_objective_gap"]
                                  for rec in all_bounds),
            "max_matlab_endpoint_gap_upper_bound":
                extremum("matlab_endpoint_objective_gap_upper_bound"),
            "max_hgfx_endpoint_gap_upper_bound":
                extremum("hgfx_endpoint_objective_gap_upper_bound"),
            "subject_7_bounds":{k:v for k,v in all_bounds[7].items()
                                if k!="subject_zero_based"},
        },
        "interpretation":"Triangle bounds from archived own-fit objectives and observed same-vector discrepancy. NOT fitted parameter, optimizer, trajectory, inference or scientific equivalence.",
        "individual_trial_data_or_full_endpoints_in_report":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("d08","cohort64","panel_e_comparison","sanitized_output"):
        p.add_argument("--"+key.replace("_","-"),required=True,type=Path)
    args=p.parse_args()
    require(not args.sanitized_output.exists(),
            "Original derived endpoint bounds must not be overwritten")
    audit_archive(args.d08,"d08",SOURCES["d08"])
    audit_archive(args.cohort64,"cohort64",SOURCES["cohort64"])
    raw=args.panel_e_comparison.read_bytes()
    require(sha256_bytes(raw)==FROZEN_PANEL_E_COMPARISON_SHA256,
            "Panel E successful original audit digest mismatch")
    data=compute_bounds(
        read_zip_json(args.d08,"m18_d08_endpoint.json"),
        read_zip_json(args.d08,"m18_d08_endpoint_comparison.json"),
        read_zip_json(args.cohort64,"matlab_raw.json"),
        read_zip_json(args.cohort64,"hgfx_raw.json"),
        json.loads(raw),
    )
    data["panel_e_comparison_sha256"]=FROZEN_PANEL_E_COMPARISON_SHA256
    data["original_source_zip_sha256"]={
        "d08":SOURCES["d08"]["zip_sha256"],
        "cohort64":SOURCES["cohort64"]["zip_sha256"],
    }
    args.sanitized_output.parent.mkdir(parents=True,exist_ok=True)
    args.sanitized_output.write_text(
        json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",
        encoding="utf-8")
    print(json.dumps({
        "status":data["kind"],"scientific_gate":data["reported_panel_e_science_gate"],
        "original_subjects":data["original_subjects"],
        "max_cross_fit_gap":data["cohort64"]["max_observed_cross_fit_objective_gap"],
        "output_sha256":hashlib.sha256(args.sanitized_output.read_bytes()).hexdigest(),
    },sort_keys=True))


if __name__=="__main__": main()
