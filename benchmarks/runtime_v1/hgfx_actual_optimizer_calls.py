#!/usr/bin/env python3
"""Real frozen HGFX public-fit optimizer direct calls and executed source branches.

The original installed HGFX v1.0.0 code is NEVER rewritten. A temporary,
transparent class-method wrapper captures actual free objective evaluations
during a public fit. A temporary Python source-line tracer records execution
of original optimizer branch BODY lines, not just calculated conditions.
This remains author-side experimental evidence, not scientific parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
from hashlib import sha256
from importlib import metadata
import inspect
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys

import numpy as np

HGFX = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB = "2437f4dc241541072722a2695ddeca7b44d83dd3"
OLD_H = "060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce"
OLD_M = "4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a"
OPT = ("init", "final", "H", "Sigma", "Corr", "trialLogLlsplit", "negLl",
       "negLj", "LME", "decompLME", "AIC", "BIC", "yhat", "res", "resAC")
START = [-3.0, -6.0, 3.871201010907891]


def need(flag, reason):
    if not flag:
        raise ValueError(reason)


def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def xyz(values):
    a = np.asarray(values, dtype=np.float64).reshape(-1)
    need(a.shape == (3,) and np.isfinite(a).all(), "Original 3-coordinate vector invalid")
    return [float(q) for q in a]


def bits_num(value):
    return struct.pack(">d", float(value))


def coords_equal(a, b):
    return b"".join(bits_num(x) for x in a) == b"".join(bits_num(x) for x in b)


def raw_json(array):
    if isinstance(array, np.ndarray):
        return raw_json(array.tolist())
    if isinstance(array, (np.floating, float)):
        return float(array) if np.isfinite(float(array)) else None
    if isinstance(array, (np.integer, int, bool, str)) or array is None:
        return int(array) if isinstance(array, np.integer) else array
    if isinstance(array, Mapping):
        return {str(k): raw_json(v) for k, v in array.items()}
    if isinstance(array, (tuple, list)):
        return [raw_json(v) for v in array]
    raise ValueError("Unsupported source type in frozen public record: " + type(array).__name__)


def exact_pair(left, right, path="output"):
    """No scientific tolerance: exact array shapes, dtypes, values, matched NaNs."""
    if isinstance(left, Mapping) or isinstance(right, Mapping):
        if not isinstance(left, Mapping) or not isinstance(right, Mapping) or set(left) != set(right):
            return path + ": mapping fields changed"
        for k in left:
            result = exact_pair(left[k], right[k], path + "." + k)
            if result:
                return result
        return None
    if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
        if not isinstance(left, np.ndarray) or not isinstance(right, np.ndarray):
            return path + ": MATLAB-style ndarray type mismatch"
        if left.shape != right.shape or left.dtype != right.dtype:
            return path + ": MATLAB-style array shape/dtype mismatch"
        if left.dtype.kind in "fc":
            same = np.array_equal(left, right, equal_nan=True)
        elif left.dtype.kind in "buiUS":
            same = np.array_equal(left, right)
        else:
            return path + ": unsupported frozen array dtype"
        return None if same else path + ": exact element/NaN-position mismatch"
    if isinstance(left, (tuple, list)) or isinstance(right, (tuple, list)):
        if type(left) is not type(right) or len(left) != len(right):
            return path + ": tuple/list shape mismatch"
        for i,(a,b) in enumerate(zip(left,right)):
            issue=exact_pair(a,b,path+f"[{i}]")
            if issue:
                return issue
        return None
    if type(left) is not type(right):
        return path + ": scalar type mismatch"
    if isinstance(left, (float, np.floating)):
        return None if np.array_equal(np.asarray([left]),np.asarray([right]),equal_nan=True) else path + ": float mismatch"
    if isinstance(left, (int,bool,str,type(None),np.integer,np.bool_)):
        return None if left==right else path + ": scalar mismatch"
    return path + ": unsupported scalar " + type(left).__name__


def original_science_and_sources(root: Path, archive: Path):
    summary=json.loads((root/"fit_cohort_results/summary-41863441006.json").read_bytes())
    need(summary["hgfx_sha"]==HGFX and summary["matlab_sha"]==MATLAB
         and summary["subject_count"]==64
         and summary["classification_counts"]=={
             "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
             "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1}
         and summary["cases"][7]["mismatched_fields"]==["traj.mu","traj.muhat"]
         and all(summary["cases"][7]["fields"][k]["mismatch_count"]==4
                 for k in ("traj.mu","traj.muhat")),
         "Original immutable 63/64 subject7 scientific NONPASS must remain unchanged")
    need(sha(archive/"hgfx_raw.json")==OLD_H and sha(archive/"matlab_raw.json")==OLD_M,
         "Original real BFGS source SHA-256 changed")
    need(sha(root/"inputs/binary_128_s64.json")==summary["hgfx_input_sha256"]
         and sha(root/"configs/hgf_binary_128.json")==summary["hgfx_config_sha256"],
         "Frozen original subject source or config SHA changed")
    old_h=json.loads((archive/"hgfx_raw.json").read_bytes())
    old_m=json.loads((archive/"matlab_raw.json").read_bytes())
    need(old_h["source_run_id"]==old_m["source_run_id"]=="41863441006"
         and old_h["frozen_hgfx_sha"]==old_m["frozen_hgfx_sha"]==HGFX
         and old_h["frozen_matlab_sha"]==old_m["frozen_matlab_sha"]==MATLAB,
         "Old source BFGS model/run changed")
    return summary,old_h,old_m


def catalog_source(path: Path):
    """Identify original frozen optimizer source statements by their *contents*."""
    lines=path.read_text().splitlines()
    trimmed=["".join(s.split()) for s in lines]
    def get_one(label):
        indices=[i+1 for i,s in enumerate(trimmed) if s==label]
        need(len(indices)==1, "Frozen HGFX optimizer source statement missing/nonunique: "+label)
        return indices[0]
    call_initial_reset=[i+1 for i,s in enumerate(trimmed) if s=="val=float(function(x))"]
    direct_line=get_one("newval=float(function(newx))")
    need(len(call_initial_reset)==2 and call_initial_reset[0]<direct_line<call_initial_reset[1],
         "Source initial and reset direct objective statement sequence changed")
    armijo_if=get_one("ifdval<1e-4*step_fraction*slope:")
    need(trimmed[armijo_if]=="break", "Frozen Armijo source branch body has changed")
    curvature_if=get_one("ifdgdx>curvature_threshold:")
    need(trimmed[curvature_if]=="dg_t=dgrad@t_inv_hessian", "Frozen BFGS curvature branch body changed")
    return {
      "INITIAL":call_initial_reset[0], "LINESEARCH":direct_line,
      "RESET":call_initial_reset[1],
      "ARMIO_BREAK_EXECUTED":armijo_if+1,
      "ACCEPTED_UPDATE_EXECUTED":get_one("dx=newx-x"),
      "BFGS_CURVATURE_UPDATE_EXECUTED":curvature_if+1,
      "TERMINATION_TOL_ARG_EXECUTED":get_one('termination="tol_arg"'),
      "TERMINATION_TOL_GRAD_EXECUTED":get_one('termination="tol_grad"'),
      "TERMINATION_MAX_RESETS_EXECUTED":get_one('termination="max_resets"'),
      "DESCENT_CLIPPED_EXECUTED":get_one("descvec=descvec*opts.max_step/step_size"),
    }


def trace_record(root: Path, archive: Path, output: Path):
    from hgfx import fit_model
    from hgfx.compat.fitting import FitProblem, hgf_binary_unitsq_fit_problem
    import hgfx.optim.compat_quasinewton as q
    need(metadata.version("hgfx")=="1.0.0", "Expected original installed HGFX v1.0.0")
    summary, old_h, old_m=original_science_and_sources(root,archive)
    source=Path(q.__file__).resolve()
    sites=catalog_source(source)
    code=q.quasinewton_optim.__code__
    need(Path(code.co_filename).resolve()==source,
         "Frozen Python source must be original optimizer co_filename")
    data=json.loads((root/"inputs/binary_128_s64.json").read_bytes())
    u=np.asarray(data["u"][7],np.float64)
    y=np.asarray(data["y"][7],np.float64)
    need(u.shape==y.shape==(128,), "Wrong 128-trial original binary data")
    problem=hgf_binary_unitsq_fit_problem(y,u)
    need(tuple(problem.free_indices)==(12,13,14)
         and coords_equal(xyz(problem.initial_free),START),
         "Original HGFX free-coordinate start changed")
    untouched=FitProblem.evaluate_free
    old_trace=sys.gettrace()
    native=fit_model(y,u,"hgf_binary_config","unitsq_sgm_config","quasinewton_optim_config")
    direct=[]
    actions=[]
    counted=Counter()
    unknown=[]
    callcount=0

    def watch_evaluate(self,free):
        nonlocal callcount
        v=float(untouched(self,free))  # EXACTLY ONE original frozen objective evaluation.
        callcount+=1
        caller=inspect.currentframe().f_back
        if caller.f_code is code:
            line=int(caller.f_lineno)
            kind=next((k for k in ("INITIAL","LINESEARCH","RESET") if line==sites[k]),"UNRECOGNIZED")
            counted[kind]+=1
            if kind=="UNRECOGNIZED":
                unknown.append({"line":line,"call":callcount})
            rec={"call_number":callcount,"direct_index_zero_based":len(direct),
                 "source_line":line,"kind":kind,
                 "free_x":xyz(free),"objective":v,
                 "finite":bool(math.isfinite(v)),
                 "realmax_sentinel":bool(v==np.finfo(float).max)}
            if kind=="LINESEARCH":
                rec["actual_original_j"]=int(caller.f_locals["j"])
                rec["actual_original_matlab_i"]=int(caller.f_locals["matlab_i"])
                rec["actual_original_step_fraction"]=float(caller.f_locals["step_fraction"])
            direct.append(rec)
        else:
            counted["INDIRECT"]+=1
        return v

    action_names={site:name for name,site in sites.items()
                  if name not in ("INITIAL","LINESEARCH","RESET")}
    def per_line(frame,event,arg):
        if event=="line" and frame.f_lineno in action_names:
            label=action_names[frame.f_lineno]
            local=frame.f_locals
            rec={"label":label,
                 "source_line":int(frame.f_lineno),
                 "optimizer_iteration_one_based":int(local.get("matlab_i",0)),
                 "actual_j":int(local["j"]) if "j" in local and label in ("ARMIO_BREAK_EXECUTED","ACCEPTED_UPDATE_EXECUTED") else None}
            if label in ("ARMIO_BREAK_EXECUTED","ACCEPTED_UPDATE_EXECUTED"):
                rec["candidate_x"]=xyz(local["newx"])
                rec["candidate_value"]=float(local["newval"])
            actions.append(rec)
        return per_line

    def global_trace(frame,event,arg):
        if event=="call" and frame.f_code is code:
            return per_line
        return None
    need(old_trace is None, "Cannot safely replace preexisting tracing agent")
    try:
        FitProblem.evaluate_free=watch_evaluate
        sys.settrace(global_trace)
        wrapped=fit_model(y,u,"hgf_binary_config","unitsq_sgm_config","quasinewton_optim_config")
    finally:
        sys.settrace(old_trace)
        FitProblem.evaluate_free=untouched
    need(FitProblem.evaluate_free is untouched and sys.gettrace() is old_trace,
         "Original HGFX objective method or Python trace was not restored")
    need(not unknown and callcount==sum(counted.values()) and
         len(direct)==sum(counted[k] for k in ("INITIAL","LINESEARCH","RESET"))
         and counted["INITIAL"]==1 and counted["LINESEARCH"]>=1,
         "Frozen HGFX source call classification/inventory has unknown or missing calls")
    need(direct[0]["kind"]=="INITIAL" and coords_equal(direct[0]["free_x"],START),
         "Original source optimizer direct initial free vector changed")
    need(all(x["finite"] for x in direct),
         "Unexpected nonfinite original direct optimizer call cannot be suppressed")
    need(len(native.traj)==len(wrapped.traj)==11, "Original 11 trajectory fields missing")
    pairs=[]
    for group, fields in (("optim",OPT),("traj",tuple(native.traj.keys()))):
        left,right=getattr(native,group),getattr(wrapped,group)
        need(all(k in left and k in right for k in fields),
             "Missing original native/instrumented public field")
        for k in fields:
            reason=exact_pair(left[k],right[k],group+"."+k)
            pairs.append({"field":group+"."+k,"equal_nan_exact":reason is None,
                          "first_difference":reason})
    history_issue=exact_pair(native.optim["iter"],wrapped.optim["iter"],"optim.iter")
    need(len(pairs)==26 and all(v["equal_nan_exact"] for v in pairs)
         and history_issue is None, "Original native HGFX fit changed under objective wrapper")
    hist=native.optim["iter"]
    ix=np.asarray(hist["x"],np.float64)
    iv=np.asarray(hist["val"],np.float64)
    need(ix.shape==(101,3) and iv.shape==(101,)
         and np.flatnonzero(np.isfinite(iv)).tolist()==list(range(25)),
         "Original frozen HGFX 25 finite public optimizer history records changed")
    need([x["label"] for x in actions].count("TERMINATION_TOL_GRAD_EXECUTED")==1
         and [x["label"] for x in actions].count("TERMINATION_TOL_ARG_EXECUTED")==0
         and counted["RESET"]==0,
         "Unexpected frozen HGFX optimizer exit/reset instrumentation state")
    prior_ix=np.asarray(old_h["iter_x"][:25],np.float64)
    prior_mx=np.asarray(old_m["iter_x"][:25],np.float64)
    comparisons=[]
    for i in range(25):
        comparisons.append({
            "record_index_zero_based":i,
            "native_new_hgfx_vs_prior_original_hgfx_equal_bits":coords_equal(ix[i].tolist(),prior_ix[i].tolist()),
            "native_new_hgfx_vs_prior_original_hgfx_max_abs":float(np.max(np.abs(ix[i]-prior_ix[i]))),
            "native_new_hgfx_vs_prior_original_matlab_equal_bits":coords_equal(ix[i].tolist(),prior_mx[i].tolist()),
            "native_new_hgfx_vs_prior_original_matlab_max_abs":float(np.max(np.abs(ix[i]-prior_mx[i]))),
        })
    branch_counts=Counter(x["label"] for x in actions)
    meta={
        "schema":"perf01d-original-public-hgfx-actual-optimizer-calls-v1",
        "status":"AUTHOR_SIDE_ACTUAL_FROZEN_HGFX_SOURCE_CALLS_NOT_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "old_bfgs_run_id":"42187240378",
        "old_bfgs_hgfx_raw_sha256":OLD_H,
        "old_bfgs_matlab_raw_sha256":OLD_M,
        "subject_index_zero_based":7,"trials":128,
        "input_sha256":summary["hgfx_input_sha256"],
        "config_sha256":summary["hgfx_config_sha256"],
        "original_science":"63/64 SCIENTIFIC NONPASS",
        "original_subject7_failure":{"traj.mu":4,"traj.muhat":4},
        "source_python_optimizer_path":str(source),
        "source_python_optimizer_sha256":sha(source),
        "source_python_optimizer_sites":sites,
        "host":{"platform":platform.platform(),"machine":platform.machine(),
                "processor":platform.processor(),"python":sys.version,
                "numpy":np.__version__,
                "github_runner_name":os.environ.get("RUNNER_NAME",""),
                "github_run_id":os.environ.get("GITHUB_RUN_ID",""),
                "github_sha":os.environ.get("GITHUB_SHA","")},
        "direct_counts":{k:int(counted[k]) for k in ("INITIAL","LINESEARCH","RESET")},
        "indirect_call_count":int(counted["INDIRECT"]),
        "all_objective_calls":callcount,
        "branch_executed_counts":dict(branch_counts),
        "neutrality_26_public_fields":True,
        "neutrality_full_iter":True,
        "original_finite_history_slots":25,
        "independent_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "no_performance_timing":True,
    }
    report={"metadata":meta,"calls":direct,"executed_source_branch_bodies":actions,
            "original_native_101_iter_x":raw_json(ix),
            "original_native_101_iter_val":raw_json(iv),
            "native_vs_wrapped_26_field_results":pairs,
            "history_original_own_engine_cross_run":comparisons,
            "non_native_if_branch_disposition":"MATLAB_SOURCE_CALLS_NOT_BOOLEAN_TRACED"}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":meta["status"],
        "direct_counts":meta["direct_counts"],
        "indirect_calls":meta["indirect_call_count"],
        "total_calls":callcount,
        "actual_executed_branch_counts":meta["branch_executed_counts"],
        "matches_original_hgfx_history_bits":sum(z["native_new_hgfx_vs_prior_original_hgfx_equal_bits"] for z in comparisons),
        "first_difference_to_original_matlab":next((z["record_index_zero_based"] for z in comparisons
            if not z["native_new_hgfx_vs_prior_original_matlab_equal_bits"]),None),
        "scientific_fit":"63/64 NONPASS",
    },sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--old-bfgs",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    trace_record(a.root,a.old_bfgs,a.output)


if __name__=="__main__":
    main()
