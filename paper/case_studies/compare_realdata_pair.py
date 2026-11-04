"""Compare actual pinned MATLAB 8.2 and installed HGFX 1.0 forward trajectories.

One prospectively chosen 80-trial public input per published study. This is
fixed-vector perceptual-forward parity, NOT a full scientific paper reproduction.
Never export observed input vectors or per-trial posterior trajectories.
"""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path

import jax
import numpy as np
from scipy.io import loadmat
from hgfx.models import hgf_ar1_binary_mab

RTOL = 2e-9
ATOL = 2e-11
P = np.asarray([np.nan,0,1,np.nan,.1,1,np.nan,0,.2,np.nan,0,1,1,1,np.nan,-2,-6],dtype=np.float64)
CASES = ("suthaharan_2021","reed_2020")
EXPECTED_TRIALS = 80
HGF_REF_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def check_one(label, got, expected):
    actual = np.asarray(got, dtype=np.float64)
    ref = np.asarray(expected, dtype=np.float64)
    result = {"field":label, "hgfx_shape":list(actual.shape), "matlab_shape":list(ref.shape)}
    if actual.shape != ref.shape:
        if actual.size == ref.size and (actual.ndim == 0 or ref.ndim == 0 or 1 in actual.shape or 1 in ref.shape):
            ref = ref.reshape(actual.shape)
        else:
            return {**result,"status":"FAIL_SHAPE"}
    matches = np.isclose(actual,ref,rtol=RTOL,atol=ATOL,equal_nan=True)
    ok = bool(np.all(matches))
    valid = np.isfinite(actual) & np.isfinite(ref)
    abs_diff = np.abs(actual[valid]-ref[valid])
    rel_diff = abs_diff/np.maximum(np.abs(ref[valid]),1e-12)
    result.update({
        "elements":int(actual.size),
        "finite_pairs":int(valid.sum()),
        "nonfinite_pairs":int(actual.size-valid.sum()),
        "failing_elements":int((~matches).sum()),
        "max_abs_diff":float(np.max(abs_diff)) if abs_diff.size else None,
        "max_rel_diff_descriptive":float(np.max(rel_diff)) if rel_diff.size else None,
        "status":"PASS_NUMERIC_GATE" if ok else "FAIL_NUMERIC_GATE",
    })
    if not ok:
        idx=tuple(int(v) for v in np.argwhere(~matches)[0])
        result["first_divergence_zero_based"]=list(idx)
        result["first_divergence_trial_1_based"]=idx[0]+1 if idx else None
        result["first_divergence_level_1_based"]=idx[1]+1 if len(idx)>1 else None
        # No participant observed data or per-trial prediction values in public artifact.
        result["first_divergence_values_redacted"]=True
    return result


def check_case(case,folder):
    source=np.loadtxt(folder/f"{case}_input.txt",dtype=np.float64,ndmin=2)
    if source.shape != (EXPECTED_TRIALS,2):
        raise ValueError(f"Expected 80x2 input for {case}, got {source.shape}")
    values, choices = source.T
    masks=np.flatnonzero(np.isnan(values)|np.isnan(choices)).tolist()
    if not np.all(np.isin(values[np.isfinite(values)],[0,1])):
        raise ValueError("Non-native input coding")
    if not np.all(np.isin(choices[np.isfinite(choices)],[1,2,3])):
        raise ValueError("Non-native choice coding")
    expected=loadmat(folder/f"{case}_matlab_result.mat",struct_as_record=False,squeeze_me=True)
    matlab_traj=expected["traj"]
    matlab_fields=list(matlab_traj._fieldnames)
    actual_traj, actual_states=hgf_ar1_binary_mab(values,P,choices=choices,
        n_bandits=3,coupled=False,irregular_intervals=False,
        ignored_trials=masks,validate=False)
    checked=[]
    checked.append(check_one("infStates",actual_states,expected["infStates"]))
    for field in matlab_fields:
        if field not in actual_traj:
            checked.append({"field":"traj."+field,"status":"FAIL_MISSING_HGFX_FIELD"})
        else:
            checked.append(check_one("traj."+field,actual_traj[field],getattr(matlab_traj,field)))
    for field in actual_traj:
        if field not in matlab_fields:
            checked.append({"field":"traj."+field,"status":"FAIL_MISSING_MATLAB_FIELD"})
    passed=all(x["status"]=="PASS_NUMERIC_GATE" for x in checked)
    return {"case":case,"source_input_sha256":hashlib.sha256((folder/f"{case}_input.txt").read_bytes()).hexdigest(),
        "trials":EXPECTED_TRIALS,"ignored_trials":len(masks),"scored_fields":len(checked),
        "status":"PASS_FIXED_VECTOR_FORWARD_PARITY" if passed else "FAIL_FIXED_VECTOR_FORWARD_PARITY",
        "field_checks":checked}


def main():
    folder=Path(sys.argv[1]).resolve()
    dest=Path(sys.argv[2]).resolve()
    if importlib.metadata.version("hgfx")!="1.0.0":
        raise SystemExit("Wrong HGFX version; stable 1.0.0 required")
    if not jax.config.jax_enable_x64 or any(d.platform!="cpu" for d in jax.devices()):
        raise SystemExit("CPU/x64 requirement violated")
    results={
        "scope":"prospective two-published-study first-subject fixed-vector perceptual forward only; NOT published fit replication",
        "criteria":{"rtol":RTOL,"atol":ATOL,"source":"tools/check_m12bc_parity.py existing frozen M12B numerical policy"},
        "frozen_matlab_oracle_commit":HGF_REF_SHA,
        "hgfx_version":importlib.metadata.version("hgfx"),
        "hgfx_import_path":__import__("hgfx").__file__,
        "jax_version":jax.__version__,
        "jax_enable_x64":bool(jax.config.jax_enable_x64),
        "device_platforms":[d.platform for d in jax.devices()],
        "python_version":sys.version.split()[0],
        "github_sha":os.getenv("GITHUB_SHA"),
        "github_run_id":os.getenv("GITHUB_RUN_ID"),
        "results":[],
    }
    for case in CASES:
        try:
            row=check_case(case,folder)
        except Exception as exc:
            row={"case":case,"status":"BLOCKED_EXECUTION_OR_SEMANTICS",
                 "error_type":type(exc).__name__,"reason":str(exc)[:400]}
        results["results"].append(row)
    results["overall_status"]="PASS_BOUNDED_BOTH_CASES" if all(
        c["status"]=="PASS_FIXED_VECTOR_FORWARD_PARITY" for c in results["results"]
    ) else "NOT_PASSED"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(results,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    # Never print subject-level values, predictions or traces.
    print(json.dumps({"overall_status":results["overall_status"],"results":[
        {"case":r["case"],"status":r["status"],"scored_fields":r.get("scored_fields"),
         "worst_fields":sorted((x for x in r.get("field_checks",[]) if x["status"]!="PASS_NUMERIC_GATE"),
             key=lambda x:x.get("failing_elements",0),reverse=True)[:5],
         "reason":r.get("reason")} for r in results["results"]
    ]},indent=2))
    if results["overall_status"]!="PASS_BOUNDED_BOTH_CASES":
        raise SystemExit("BOUNDED_FORWARD_PARITY_NOT_PASSED: see uploaded summary")


if __name__=="__main__":
    main()
