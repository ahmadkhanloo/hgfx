#!/usr/bin/env python3
"""PERF-01D: audit immutable 2x2 counterfactual omega forward tensor.

Predeclared corners, exact original full transformed vectors, 11 scientific
trajectory fields, original subject 7 and raw source checks. Shapley values
are algebraic signed contributions of two perceptual coordinate replacements,
NOT optimizer defect classification or a new scientific acceptance threshold.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from compare_fits import numeric
from compare_trialwise import decode_tree
from compare_subject7_crossed_forward import (
    RAW,HGFX_SHA,MATLAB_SHA,SOURCE,RTOL,ATOL,FIELDS,validate_source,anchors,compare_traj
)
from subject7_omega_counterfactual_hgfx import CORNERS,ORIGIN_INDEX,exact_vectors


STATUS="AUTHOR_SIDE_SIGNED_OMEGA_DECOMPOSITION_NOT_FIT_PARITY_OR_CAUSAL_OPTIMIZER_VERDICT"
EXPECTED_4={
    "MM_original_matlab":(0,0),
    "HM_hgfx_omega2_matlab_omega3":(1,0),
    "MH_matlab_omega2_hgfx_omega3":(0,1),
    "HH_original_hgfx":(1,1),
}


def to_array(x):
    return np.asarray(decode_tree(x),dtype=np.float64)


def validate(raw:dict,engine:str,summary:dict,vectors:dict)->dict:
    hashes=raw.get("original_raw_sha256")
    if engine=="matlab" and isinstance(hashes,dict):
        hashes={k.replace("_raw_json","_raw.json"):v for k,v in hashes.items()}
    if (
        raw.get("schema")!=f"perf01d-subject7-omega-counterfactual-{engine}-v1"
        or raw.get("status")!=
            "AUTHOR_SIDE_2X2_OMEGA_FORWARD_DIAGNOSTIC_NO_FITTING_OR_SCIENTIFIC_PASS"
        or raw.get("original_64_fit_run")!=SOURCE
        or raw.get("frozen_hgfx_sha")!=HGFX_SHA
        or raw.get("frozen_matlab_sha")!=MATLAB_SHA
        or hashes!=RAW
        or raw.get("source_input_sha256")!=summary["hgfx_input_sha256"]
        or raw.get("source_config_sha256")!=summary["hgfx_config_sha256"]
        or raw.get("subject_index_zero_based")!=7
        or raw.get("trials")!=128
        or raw.get("model")!="hgf_binary"
        or raw.get("observation")!="unitsq_sgm"
        or raw.get("perceptual_free_coordinates_zero_based")!=[12,13]
        or raw.get("observation_free_coordinate_zero_based")!=14
        or raw.get("observation_coordinate_role")!=
            "fixed_original_MATLAB_in_mixed_corners_not_used_in_perceptual_forward"
        or raw.get("original_full_parameter_ends_preserved") is not True
        or raw.get("predeclared_corner_order")!=list(CORNERS)
    ):
        raise ValueError(f"{engine}: frozen counterfactual protocol/identity mismatch")
    if CORNERS!=tuple(EXPECTED_4):
        raise ValueError("Fixed omega2/omega3 treatment protocol modified")
    cases=raw.get("cases")
    if not isinstance(cases,list) or len(cases)!=4:
        raise ValueError(f"{engine}: expected all four original fixed-grid corners")
    output={}
    for case,corner in zip(cases,CORNERS):
        coord2,coord3=EXPECTED_4[corner]
        if (
            case.get("corner")!=corner
            or case.get("status")!=f"EVALUATED_FROZEN_UNTIMED_{engine.upper()}_FORWARD"
            or case.get("omega2_from")!=("HGFX" if coord2 else "MATLAB")
            or case.get("omega3_from")!=("HGFX" if coord3 else "MATLAB")
            or not np.array_equal(to_array(case["full_transformed_vector"]),
                                  vectors[corner],equal_nan=True)
            or set(case["traj"])!=FIELDS
        ):
            raise ValueError(f"{engine}: missing/altered exact four-corner parameter vector")
        for field in FIELDS:
            expected_shape=(128,2) if field=="w" else (128,3)
            if to_array(case["traj"][field]).shape!=expected_shape:
                raise ValueError(f"{engine}: malformed original HGF {field} shape")
        if to_array(case["inf_states"]).shape!=(128,3,4):
            raise ValueError(f"{engine}: malformed original HGF inference states")
        output[corner]=case
    return output


def signed_decomposition(mm,mh,hm,hh,original_hgfx,original_matlab):
    """Two-feature Shapley identity, baseline MATLAB, target HGFX.

    x12 from MATLAB to HGFX: 1/2[(HM-MM)+(HH-MH)]
    x13 from MATLAB to HGFX: 1/2[(MH-MM)+(HH-HM)]
    Difference in original complete fit:
      original HGFX - original MATLAB
       = source-effect-at-HH + perceptual omega2 + perceptual omega3
         + numeric reproduction residual.
    """
    arrays=[to_array(x) for x in (mm,mh,hm,hh,original_hgfx,original_matlab)]
    if any(a.shape!=arrays[0].shape for a in arrays):
        raise ValueError("Cannot decompose unequal original trajectory shapes")
    if not all(np.array_equal(np.isfinite(a),np.isfinite(arrays[0])) for a in arrays):
        raise ValueError("Cannot algebraically decompose changed nonfinite masks")
    base,change3,change2,target,fit_h,fit_m=arrays
    omega2=0.5*((change2-base)+(target-change3))
    omega3=0.5*((change3-base)+(target-change2))
    forward_source=fit_h-target
    observed=fit_h-fit_m
    residual=observed-(forward_source+omega2+omega3)
    endpoint=target-base
    split_residual=endpoint-(omega2+omega3)
    return {
        "observed":observed,
        "omega2":omega2,
        "omega3":omega3,
        "same_vector_source_at_HH_plus_own_fit_reconstruction":forward_source,
        "reconstruction_residual":residual,
        "forward_endpoint":endpoint,
        "omega_sum_residual":split_residual,
    }


def details(comp:dict,original_matlab)->dict:
    observed=comp["observed"]
    ref=to_array(original_matlab)
    if observed.shape!=ref.shape:
        raise ValueError("No original reference available for mismatch denominator")
    bad=np.argwhere(np.abs(observed)>(ATOL+RTOL*np.abs(ref)))
    row=[]
    for idx in bad:
        index=tuple(int(x) for x in idx)
        if len(index)!=2:
            raise ValueError("Expected original HGF trialwise 2D field")
        row.append({
            "trial_one_based":index[0]+1,"level_one_based":index[1]+1,
            "index_zero_based":list(index),
            "original_signed_hgfx_minus_matlab":float(comp["observed"][index]),
            "omega2_signed_component":float(comp["omega2"][index]),
            "omega3_signed_component":float(comp["omega3"][index]),
            "same_vector_source_and_reproduction_component":
                float(comp["same_vector_source_at_HH_plus_own_fit_reconstruction"][index]),
            "arithmetic_reconstruction_residual":float(comp["reconstruction_residual"][index]),
            "unchanged_original_tolerance_bound":float(ATOL+RTOL*abs(ref[index])),
        })
    def mx(x):
        return float(np.nanmax(np.abs(x)))
    return {
        "num_original_outside_fixed_tolerance":len(row),
        "original_outside_fixed_tolerance":row,
        "max_abs_original_difference":mx(comp["observed"]),
        "max_abs_signed_omega2_component":mx(comp["omega2"]),
        "max_abs_signed_omega3_component":mx(comp["omega3"]),
        "max_abs_matched_vector_source_and_reproduction_component":
            mx(comp["same_vector_source_at_HH_plus_own_fit_reconstruction"]),
        "max_abs_arithmetic_reconstruction_residual":mx(comp["reconstruction_residual"]),
        "max_abs_omega_sum_residual":mx(comp["omega_sum_residual"]),
    }


def compare(hgfx:dict,matlab:dict,original:Path,input_root:Path)->dict:
    summary,old_h,old_m=validate_source(original)
    initial=anchors(input_root,old_h,old_m)
    expected=exact_vectors(initial["original_hgfx_fitted_endpoint"],
                           initial["original_matlab_fitted_endpoint"])
    hs=validate(hgfx,"hgfx",summary,expected)
    ms=validate(matlab,"matlab",summary,expected)

    # Both forward implementations must reproduce their OWN real public fitted
    # output at their own original endpoint before attributing any deviations.
    for own,raw,ref in (
        ("HGFX",hs["HH_original_hgfx"],old_h),
        ("MATLAB",ms["MM_original_matlab"],old_m),
    ):
        reproduced=compare_traj(raw["traj"],ref["traj"])
        if reproduced["mismatched_fields"]:
            raise ValueError(f"{own} original full public fitted trajectory not reproduced")

    same_x={}
    for name in CORNERS:
        same_x[name]=compare_traj(hs[name]["traj"],ms[name]["traj"])
        same_x[name]["inference_states"]=numeric(
            hs[name]["inf_states"],ms[name]["inf_states"],RTOL,ATOL)

    # All 11 original fields are included. The model's observational
    # parameter coordinate is intentionally omitted from HGF forward-only
    # decomposition; it may still influence the optimizer objective.
    original=compare_traj(old_h["traj"],old_m["traj"])
    if (original["mismatched_fields"]!=["mu","muhat"]
            or original["fields"]["mu"]["mismatch_count"]!=4
            or original["fields"]["muhat"]["mismatch_count"]!=4):
        raise ValueError("Original scientific 63/64 mismatch was silently reclassified")

    summary_fields={}
    for field in sorted(FIELDS):
        comp=signed_decomposition(
            ms["MM_original_matlab"]["traj"][field],
            ms["MH_matlab_omega2_hgfx_omega3"]["traj"][field],
            ms["HM_hgfx_omega2_matlab_omega3"]["traj"][field],
            ms["HH_original_hgfx"]["traj"][field],
            old_h["traj"][field],old_m["traj"][field])
        summary_fields[field]=details(comp,old_m["traj"][field])
        if (summary_fields[field]["num_original_outside_fixed_tolerance"]!=
                original["fields"][field]["mismatch_count"]):
            raise ValueError(f"Original historical coordinate mismatch count altered in {field}")

    return {
        "schema":"perf01d-subject7-omega-shapley-decomposition-v1",
        "status":STATUS,
        "original_full_fit_science":"63/64 full public fitting non-PASS, original subject 7 mu/muhat mismatch",
        "original_64_run":SOURCE,
        "original_64_raw_sha256":RAW,
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "subject_index_zero_based":7,
        "trials":128,
        "perceptual_param_names":{"12":"om[1] (level 2)","13":"om[2] (level 3)"},
        "obs_param_14_note":"logze does not enter HGF perceptual forward; it DOES enter full fitting objective",
        "omega_2x2_corners":list(CORNERS),
        "original_fitting_numeric_tolerances":{"rtol":RTOL,"atol":ATOL},
        "same_vector_cross_source_11_field_reports":same_x,
        "original_fitted_reference_11_field_report":original,
        "complete_11_field_signed_decomposition":summary_fields,
        "shapley_formula":"omega2=0.5*((HM-MM)+(HH-MH)); omega3=0.5*((MH-MM)+(HH-HM)); Hfit-Mfit=omega2+omega3+(Hfit-Mforward_at_HH)+residual",
        "scientific_limitations":[
            "This is exact two-coordinate descriptive forward counterfactual algebra, not a unique causal explanation for optimizer dynamics or fitted scientific identifiability.",
            "Mixed vectors were prospectively enumerated, not optimized or selected for numerical acceptance.",
            "MATLAB reference and HGFX original end-to-end fitted endpoints differ; original 63/64 full-fit scientific non-PASS remains.",
            "Full forward matched-vector conformity does not imply optimization/termination/simulation fitting parity.",
            "No fitting, no CPU/GPU timing, no independent reviewer approval, no selection of faster BLAS mode.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    for arg in ("hgfx","matlab","original","input","output"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    out=compare(json.loads(a.hgfx.read_bytes()),
                json.loads(a.matlab.read_bytes()),a.original,a.input)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({
        "status":out["status"],
        "original_failed":out["original_fitted_reference_11_field_report"]["mismatched_fields"],
        "same_x_failed":{name:entry["mismatched_fields"]
                         for name,entry in out["same_vector_cross_source_11_field_reports"].items()},
        "original_omega2_omega3_at_failure":{
            field:data["original_outside_fixed_tolerance"]
            for field,data in out["complete_11_field_signed_decomposition"].items()
            if data["num_original_outside_fixed_tolerance"]},
        "scientific_status":"ORIGINAL 63/64 NON-PASS, NO OPTIMIZATION/TIMING",
    },sort_keys=True))


if __name__=="__main__":
    main()
