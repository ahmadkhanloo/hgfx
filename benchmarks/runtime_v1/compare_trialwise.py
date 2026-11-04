#!/usr/bin/env python3
"""Trialwise diagnostics for PERF-01; not a prospective scientific PASS."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

RTOL = 3e-8
ATOL = 3e-10
EXPECTED = {
    (m,n,False) for m in ("hgf_binary","ehgf_binary","uhgf_binary")
    for n in (128,512,1024)
} | {("hgf_binary",512,True)}
FIELDS = ("inf_states","trial_log_likelihoods","yhat","residuals")
TRAJ = ("mu","sa","muhat","sahat","v","w","da","ud","psi","epsi","wt")


def decode_tree(value):
    if isinstance(value, list):
        return [decode_tree(v) for v in value]
    if value == "Infinity":
        return float("inf")
    if value == "-Infinity":
        return float("-inf")
    if value is None:
        return float("nan")
    return value


def compare_numeric(left, right):
    a = np.asarray(decode_tree(left), dtype=np.float64)
    b = np.asarray(decode_tree(right), dtype=np.float64)
    if a.shape != b.shape:
        return {"status":"SHAPE_MISMATCH","hgfx_shape":list(a.shape),"matlab_shape":list(b.shape)}
    finite = np.isfinite(a) & np.isfinite(b)
    special = np.isclose(a,b,rtol=RTOL,atol=ATOL,equal_nan=True)
    mismatch = ~special
    failed = np.argwhere(mismatch)
    return {
        "status": "WITHIN_DIAGNOSTIC_TOLERANCE" if not len(failed) else "MISMATCH",
        "shape": list(a.shape),
        "finite_pair_count": int(finite.sum()),
        "nan_or_inf_mask_mismatch_count": int(np.sum(
            np.isnan(a) != np.isnan(b)
        ) + np.sum(np.isposinf(a) != np.isposinf(b)) +
            np.sum(np.isneginf(a) != np.isneginf(b))),
        "mismatch_count": int(mismatch.sum()),
        "max_abs_delta": float(np.max(np.abs(a[finite]-b[finite]))) if finite.any() else None,
        "first_mismatch_index_zero_based": failed[0].tolist() if len(failed) else None,
        "first_mismatch_trial_one_based": int(failed[0][0])+1 if len(failed) else None,
    }


def compare(hgfx,matlab):
    if hgfx.get("source") != "hgfx==1.0.0 @ 4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27":
        raise ValueError("Not the frozen HGFX release")
    if matlab.get("oracle_sha") != "2437f4dc241541072722a2695ddeca7b44d83dd3":
        raise ValueError("Not the frozen MATLAB oracle")
    hs={(c["model"],int(c["trials"]),bool(c["masked"])):c for c in hgfx["cells"]}
    ms={(c["model"],int(c["trials"]),bool(c["masked"])):c for c in matlab["cells"]}
    if len(hs)!=10 or len(ms)!=10 or set(hs)!=EXPECTED or set(ms)!=EXPECTED:
        raise ValueError("Incomplete or duplicate trialwise cells")
    rows=[]
    for key in sorted(EXPECTED):
        h,m=hs[key],ms[key]
        item={
            "model":key[0], "trials":key[1], "masked":key[2],
            "hgfx_status":h["status"], "matlab_status":m["status"],
            "start_matched":bool(h["start_matches_resolved_prior"] and m["start_matches_resolved_prior"]),
            "trial_mask_ids_equal": (
                h["ignored_trial_ids_one_based"] == m["ignored_trial_ids_one_based"] and
                h["irregular_trial_ids_one_based"] == m["irregular_trial_ids_one_based"]
            ),
            "diagnostic_classification":"UNASSESSED",
        }
        if not item["start_matched"] or not item["trial_mask_ids_equal"]:
            item["diagnostic_classification"]="BLOCKED_INPUT_START_OR_MASK"
        elif h["status"]=="HGFX_COMPLETED_REFERENCE_UNVERIFIED" and m["status"]=="MATLAB_COMPLETED_HGFX_UNVERIFIED":
            vectors={f:compare_numeric(h[f],m[f]) for f in FIELDS}
            trajectories={f:compare_numeric(h["traj"][f],m["traj"][f]) for f in TRAJ}
            item["fields"]=vectors
            item["trajectory_fields"]=trajectories
            all_e=list(vectors.values())+list(trajectories.values())
            item["diagnostic_classification"]=(
                "FULL_TRIALWISE_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE"
                if all(v["status"]=="WITHIN_DIAGNOSTIC_TOLERANCE" for v in all_e)
                else "TRIALWISE_MISMATCH"
            )
            discrepancies=[(name,v["first_mismatch_trial_one_based"]) for name,v in {**vectors,**trajectories}.items()
                           if v.get("first_mismatch_trial_one_based") is not None]
            item["first_mismatched_trial_one_based"]=min((n for _,n in discrepancies),default=None)
        elif h["status"]=="HGFX_ERROR" and m["status"]=="MATLAB_ERROR":
            hp=h.get("prefix_diagnostic",{})
            mp=m.get("prefix_diagnostic",{})
            item["hgfx_prefix"]=hp
            item["matlab_prefix"]=mp
            item["matlab_error_identifier"]=m.get("error_identifier")
            item["hgfx_error"]=h.get("error")
            same_prefix=(hp.get("first_invalid_prefix_length") is not None
                         and hp.get("first_invalid_prefix_length")==mp.get("first_invalid_prefix_length"))
            item["diagnostic_classification"]=(
                "BOTH_FAILED_FIRST_INVALID_PREFIX_AGREES_UNVERIFIED_MECHANISM"
                if same_prefix and m.get("error_identifier")=="tapas:hgf:VarApproxInvalid"
                else "BOTH_FAILED_PREFIX_DISAGREEMENT_OR_UNRESOLVED"
            )
        else:
            item["diagnostic_classification"]="ASYMMETRIC_FAILURE"
        rows.append(item)
    counts={s:sum(x["diagnostic_classification"]==s for x in rows)
            for s in sorted({x["diagnostic_classification"] for x in rows})}
    return {
        "schema":"hgfx-perf01-trialwise-comparison-v1",
        "status":"EXPLORATORY_NOT_FROZEN_NOT_FINAL_SCIENTIFIC_GATE",
        "matlab_release":matlab.get("matlab_release"),
        "rTolerance":RTOL,"aTolerance":ATOL,
        "tolerance_origin":"existing v1 numerical family diagnostic (not new eligibility gate)",
        "counts":counts,
        "rows":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hgfx",type=Path,required=True)
    p.add_argument("--matlab",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=compare(json.loads(a.hgfx.read_bytes()),json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps(result["counts"],sort_keys=True))
    # The summary preserves all outcomes even if the scientific diagnostics fail.
    if any(s in result["counts"] for s in (
        "BLOCKED_INPUT_START_OR_MASK","TRIALWISE_MISMATCH",
        "ASYMMETRIC_FAILURE","BOTH_FAILED_PREFIX_DISAGREEMENT_OR_UNRESOLVED")):
        raise SystemExit("Trialwise diagnostics reveal mismatches; evidence retained")


if __name__=="__main__":
    main()
