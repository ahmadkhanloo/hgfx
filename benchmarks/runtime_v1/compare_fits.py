#!/usr/bin/env python3
"""Conservative full-workflow fit diagnostic, preserving all frozen cells."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_trialwise import compare_numeric as compare_trialwise_numeric
import numpy as np

# Existing v1 M10 check_m10_parity.py defaults; these are diagnostics, NOT
# retroactive acceptance or a new performance benchmark protocol.
TOLS={
    "final":(3e-8,3e-10), "H":(2e-6,2e-8),
    "Sigma":(5e-6,5e-8), "Corr":(5e-6,5e-8),
    "negLl":(3e-8,3e-10), "negLj":(3e-8,3e-10),
    "LME":(2e-6,2e-8), "AIC":(2e-6,2e-8), "BIC":(2e-6,2e-8),
    "trialLogLlsplit":(3e-8,3e-10),
    "yhat":(3e-8,3e-10), "res":(3e-8,3e-10), "resAC":(3e-8,3e-10),
    "init":(0.0,0.0),
}


def numeric(a,b,rtol,atol):
    from compare_trialwise import decode_tree
    x=np.asarray(decode_tree(a),dtype=np.float64)
    y=np.asarray(decode_tree(b),dtype=np.float64)
    if x.shape!=y.shape and x.size==y.size:
        x=x.reshape(-1)
        y=y.reshape(-1)
    if x.shape!=y.shape:
        return {"status":"SHAPE_MISMATCH","hgfx_shape":list(x.shape),"matlab_shape":list(y.shape)}
    good=np.isclose(x,y,rtol=rtol,atol=atol,equal_nan=True)
    bad=np.argwhere(~good)
    finite=np.isfinite(x)&np.isfinite(y)
    return {
        "status":"WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE" if not len(bad) else "MISMATCH",
        "first_mismatch_index_zero_based":bad[0].tolist() if len(bad) else None,
        "mismatch_count":int((~good).sum()),
        "max_abs_delta":float(np.max(np.abs(x[finite]-y[finite]))) if finite.any() else None,
        "rtol":rtol,"atol":atol,
    }


def compare(hgfx,matlab):
    if hgfx.get("hgfx_version")!="1.0.0" or matlab.get("oracle_sha")!="2437f4dc241541072722a2695ddeca7b44d83dd3":
        raise ValueError("Unexpected source identity")
    hs={int(c["n_trials"]):c for c in hgfx["cases"]}
    ms={int(c["n_trials"]):c for c in matlab["cases"]}
    if set(hs)!={128,512,1024} or set(ms)!={128,512,1024}:
        raise ValueError("Incomplete primary fitting matrix")
    out=[]
    for n in (128,512,1024):
        h,m=hs[n],ms[n]
        row={"case_id":f"primary_fit_compat_full_{n}","n_trials":n,
             "hgfx_status":h["status"],"matlab_status":m["status"],
             "classification":"UNASSESSED"}
        if n in (512,1024):
            row["classification"]=(
                "BLOCKED_UNSTABLE_DEFAULT_START_NONCOMPARABLE_RESTART_POLICY"
                if h["status"]==m["status"]=="BLOCKED_UNSTABLE_DEFAULT_START_MATLAB_RESAMPLES_HGFX_REJECTS"
                else "FITTING_BLOCKER_MISCLASSIFIED"
            )
        elif h["status"]=="HGFX_FULL_FIT_COMPLETED_PARITY_NOT_ASSESSED" and m["status"]=="MATLAB_FULL_FIT_COMPLETED_PARITY_NOT_ASSESSED":
            fields={}
            for f,(rtol,atol) in TOLS.items():
                fields[f]=numeric(h["optim"][f],m["optim"][f],rtol,atol)
            for f in ("logjoint","postpredcorr","freepars"):
                fields["decompLME."+f]=numeric(h["optim"]["decompLME"][f],m["optim"]["decompLME"][f],2e-6,2e-8)
            for field in h["traj"]:
                if field not in m["traj"]:
                    fields["traj."+field]={"status":"MATLAB_TRAJ_MISSING"}
                else:
                    fields["traj."+field]=numeric(h["traj"][field],m["traj"][field],3e-8,3e-10)
            row["fields"]=fields
            row["classification"]=(
                "FULL_FIT_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"
                if all(x["status"]=="WITHIN_EXISTING_DIAGNOSTIC_TOLERANCE" for x in fields.values())
                   and h["n_rand_init"]==m["n_rand_init"]==0
                else "FULL_FIT_NUMERICAL_OR_WORKFLOW_MISMATCH"
            )
        elif h["status"]=="HGFX_FULL_FIT_ERROR" and m["status"]=="MATLAB_FULL_FIT_ERROR":
            row["classification"]="BOTH_FIT_FAILED_UNCLASSIFIED"
            row["matlab_error"]=m.get("error_identifier")
            row["hgfx_error"]=h.get("error")
        else:
            row["classification"]="FITTING_ASYMMETRIC_OR_UNEXPECTED"
            row["matlab_error"]=m.get("error_identifier")
            row["hgfx_error"]=h.get("error")
        out.append(row)
    return {
        "schema":"perf01-fit-comparison-v1",
        "status":"DIAGNOSTIC_ONLY_UNFROZEN_NO_PERFORMANCE",
        "matlab_release":matlab.get("matlab_release"),
        "classification_counts":{k:sum(x["classification"]==k for x in out) for k in sorted({x["classification"] for x in out})},
        "rows":out
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hgfx",type=Path,required=True)
    p.add_argument("--matlab",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    obj=compare(json.loads(a.hgfx.read_bytes()),json.loads(a.matlab.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps(obj["classification_counts"],sort_keys=True))
    if any(k in obj["classification_counts"] for k in ("FITTING_BLOCKER_MISCLASSIFIED","FULL_FIT_NUMERICAL_OR_WORKFLOW_MISMATCH","FITTING_ASYMMETRIC_OR_UNEXPECTED")):
        raise SystemExit("Fitting scientific mismatch; raw evidence retained")


if __name__=="__main__":
    main()
