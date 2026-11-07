#!/usr/bin/env python3
"""Original first frozen HGFX Ridders stencil; actual same-host MATLAB-private cross-evaluation.

Two stages: prepare original exact HGFX x+h/x-h calls, then after real MATLAB
callback replay all MATLAB own nodes against HGFX objective at SAME binary64 x.
Does not claim original fit parity, Ridders source branch event parity, or speed.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from importlib import metadata
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys
import warnings

import numpy as np

HGFX="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB="2437f4dc241541072722a2695ddeca7b44d83dd3"
BFGS_H="060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce"
BFGS_M="4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a"
START=[-3.0,-6.0,3.871201010907891]
SCHEMA="perf01d-initial-real-ridders-3coord-v1"


def need(ok,msg):
    if not ok: raise ValueError(msg)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def fbits(v):
    need(type(v) in (float,int) and math.isfinite(v),"missing/nonfinite float")
    return struct.pack(">d",float(v))


def xbits(v):
    need(type(v) is list and len(v)==3,"missing three-vector")
    return b"".join(fbits(x) for x in v)


def xhex(v):
    return [fbits(x).hex() for x in v]


def base_problem(root,archive):
    from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
    need(metadata.version("hgfx")=="1.0.0","HGFX must be frozen v1.0.0")
    original=json.loads((root/"fit_cohort_results/summary-41863441006.json").read_bytes())
    need(original["hgfx_sha"]==HGFX and original["matlab_sha"]==MATLAB
         and original["subject_count"]==64
         and original["classification_counts"]=={
             "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63,
             "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1}
         and original["cases"][7]["mismatched_fields"]==["traj.mu","traj.muhat"]
         and all(original["cases"][7]["fields"][k]["mismatch_count"]==4
                 for k in ("traj.mu","traj.muhat")),
         "Original full 63/64 scientific NONPASS, subject-7 4+4 or source SHA changed")
    need(digest(archive/"hgfx_raw.json")==BFGS_H
         and digest(archive/"matlab_raw.json")==BFGS_M,
         "Original unchanged BFGS own-history SHA256 invalid")
    need(digest(root/"inputs/binary_128_s64.json")==original["hgfx_input_sha256"]
         and digest(root/"configs/hgf_binary_128.json")==original["hgfx_config_sha256"],
         "Original canonical input/config SHA256 invalid")
    data=json.loads((root/"inputs/binary_128_s64.json").read_bytes())
    need(data["subject_count"]==64 and data["trial_count"]==128,
         "Original 64 subjects/128 trials changed")
    y=np.asarray(data["y"][7],np.float64);u=np.asarray(data["u"][7],np.float64)
    need(y.shape==u.shape==(128,),"Original subject 7 128-trial input wrong")
    p=hgf_binary_unitsq_fit_problem(y,u)
    need(p.free_indices==(12,13,14)
         and xbits(np.asarray(p.initial_free,np.float64).tolist())==xbits(START),
         "Frozen free start or free parameter indices changed")
    return p,original


def normalize_node(nodes):
    need(type(nodes) is list and bool(nodes),"Missing real Ridders stencil nodes")
    out=[]
    for i,record in enumerate(nodes):
        x=record["x"]
        v=record["value"]
        need(record.get("ordinal") == i and xhex(x)==record["x_hex"] and math.isfinite(v),
             "Real Ridders source node ordinal, x bits or value invalid")
        out.append({"ordinal":i,"x":x,"x_hex":record["x_hex"],"value":v})
    return out


def classify_stencil(nodes):
    """Exact-order center then 3 contiguous variable-axis positive/negative pairs."""
    rows=normalize_node(nodes)
    need(xbits(rows[0]["x"])==xbits(START),"Original Ridders center check x changed")
    need((len(rows)-1)%2==0,"Source Ridders +/- stencil pair missing")
    remaining=rows[1:]
    classified=[]
    seen=[0,0,0]
    last_coord=-1
    i=0
    while i<len(remaining):
        a,bb=remaining[i:i+2]
        ax,bx=a["x"],bb["x"]
        diffa=[k for k in range(3) if fbits(ax[k])!=fbits(START[k])]
        diffb=[k for k in range(3) if fbits(bx[k])!=fbits(START[k])]
        need(len(diffa)==len(diffb)==1 and diffa==diffb,
             "Original Ridders source stencil changed more than one coordinate")
        coord=diffa[0]
        need(coord>=last_coord and coord<=last_coord+1,
             "Original Ridders coordinate order swapped or skipped")
        need(ax[coord]>START[coord] and bx[coord]<START[coord],
             "Original Ridders positive/negative stencil sign/order invalid")
        need(coord<=2,"Unexpected Ridders source coordinate")
        seen[coord]+=1
        step=seen[coord]
        if step==1:
            need(fbits(ax[coord])==fbits(START[coord]+1.)
                 and fbits(bx[coord])==fbits(START[coord]-1.),
                 "Frozen Ridders initial h=1 changed")
        classified.append({
            "coord_zero_based":coord,
            "step_one_based":step,
            "positive":a,"negative":bb,
        })
        last_coord=coord
        i+=2
    need(all(11<=n<=100 for n in seen),
         "Original Ridders min_steps=10/max_steps=100 inventory invalid")
    return seen,classified


def prepare(root,archive,out):
    from hgfx.optim.ridders import RiddersOptions, ridders_gradient
    p,original=base_problem(root,archive)
    source=Path(sys.modules[ridders_gradient.__module__].__file__)
    opts=RiddersOptions(min_steps=10)
    need(opts.init_h==1. and opts.div==1.2 and opts.max_steps==100 and opts.tf==2.,
         "Original frozen Ridders policy changed")
    nodes=[]
    def counted(x):
        a=np.asarray(x,np.float64).reshape(-1)
        xx=a.tolist()
        val=float(p.evaluate_free(a))
        need(np.isfinite(a).all() and math.isfinite(val),
             "Original frozen source objective returned nonfinite value")
        nodes.append({"ordinal":len(nodes),"x":xx,"x_hex":xhex(xx),"value":val})
        return val
    # Do not suppress original source NumPy warnings; capture only whether seen.
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter("always")
        grad,err=ridders_gradient(counted,np.asarray(START,np.float64),opts)
    for w in notices:
        print("Original HGFX Ridders warning: "+str(w.message),file=sys.stderr)
    need(grad.shape==err.shape==(3,) and np.isfinite(grad).all() and np.isfinite(err).all(),
         "Original source Ridders gradient/error nonfinite")
    steps,classified=classify_stencil(nodes)
    result={
        "schema":SCHEMA,"status":"SOURCE_HGFX_INITIAL_RIDDERS_OWN_STENCIL",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "subject_index_zero_based":7,"n_trials":128,
        "source_input_sha256":original["hgfx_input_sha256"],
        "source_config_sha256":original["hgfx_config_sha256"],
        "original_63_subject_fit_status":"63/64 SCIENTIFIC NONPASS",
        "original_failure":{"traj.mu":4,"traj.muhat":4},
        "x0":START,"x0_hex":xhex(START),
        "min_steps":10,"max_steps":100,"init_h":1.0,"div":1.2,"tf":2.0,
        "ridders_source_sha256":digest(source),
        "hgfx_gradient":[float(z) for z in grad],
        "hgfx_error":[float(z) for z in err],
        "hgfx_nodes":nodes,
        "steps_per_coordinate":steps,
        "nodes_per_coordinate":[2*n for n in steps],
        "source_warning_count":len(notices),
        "environment":{"github_run_id":os.environ.get("GITHUB_RUN_ID",""),
                       "github_sha":os.environ.get("GITHUB_SHA",""),
                       "python":sys.version,"numpy":np.__version__,
                       "platform":platform.platform()},
        "independent_review":"NOT_RECEIVED","perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN","gpu":"NOT_RUN",
    }
    need(len(classified)==sum(steps),"Source initial node accounting changed")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"stage":"prepare","gradient":result["hgfx_gradient"],
                      "steps_per_coordinate":steps,"num_nodes":len(nodes),
                      "source_status":"63/64 SCIENTIFIC NONPASS"},sort_keys=True))


def verify(root,archive,source_path,matlab_path,output):
    p,original=base_problem(root,archive)
    py_bytes=source_path.read_bytes()
    hg=json.loads(py_bytes)
    need(hg["schema"]==SCHEMA and hg["status"]=="SOURCE_HGFX_INITIAL_RIDDERS_OWN_STENCIL"
         and hg["frozen_hgfx_sha"]==HGFX and hg["frozen_matlab_sha"]==MATLAB
         and hg["x0_hex"]==xhex(START) and hg["min_steps"]==10
         and hg["environment"]["github_run_id"]==os.environ.get("GITHUB_RUN_ID")
         and hg["environment"]["github_sha"]==os.environ.get("GITHUB_SHA")
         and hg["original_63_subject_fit_status"]=="63/64 SCIENTIFIC NONPASS"
         and hg["independent_review"]=="NOT_RECEIVED"
         and hg["perf01c"]=="NOT_FROZEN",
         "Exact source HGFX initial Ridders provenance changed")
    py_nodes=normalize_node(hg["hgfx_nodes"])
    hsteps,_=classify_stencil(py_nodes)
    mbytes=matlab_path.read_bytes()
    ma=json.loads(mbytes)
    need(ma["schema"]=="perf01d-real-private-matlab-first-ridders-stencil-v1"
         and ma["frozen_hgfx_sha"]==HGFX and ma["frozen_matlab_sha"]==MATLAB
         and ma["source_hgfx_stencil_sha256"]==sha256(py_bytes).hexdigest()
         and ma["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and ma["original_failure"]=={"traj.mu":4,"traj.muhat":4}
         and str(ma["github_run_id"])==os.environ.get("GITHUB_RUN_ID")
         and ma["tested_sha"]==os.environ.get("GITHUB_SHA")
         and ma["hook_count"]==1 and ma["original_optimizer_delegated"] is True
         and ma["native_wrapped_26_and_iter_exact"] is True
         and ma["independent_review"]=="NOT_RECEIVED"
         and ma["perf01c"]=="NOT_FROZEN"
         and ma["min_steps"]==10
         and ma["x0_hex"]==xhex(START),
         "Actual frozen MATLAB private initial stencil/neutrality provenance changed")
    mnodes=normalize_node(ma["matlab_nodes"])
    msteps,mclassified=classify_stencil(mnodes)
    need(len(ma["matlab_on_hgfx_nodes"])==len(py_nodes),
         "Real private MATLAB did not evaluate all original HGFX nodes")
    m_on_h=[]
    for i,(item,node) in enumerate(zip(ma["matlab_on_hgfx_nodes"],py_nodes)):
        need(item["ordinal"]==i and xhex(item["x"])==node["x_hex"],
             "Source Python coordinate was modified by MATLAB JSON transport")
        value=float(item["value"])
        need(math.isfinite(value),"Real private MATLAB returned nonfinite cross-grid value")
        m_on_h.append(value)
    h_on_m=[]
    for i,node in enumerate(mnodes):
        value=float(p.evaluate_free(np.asarray(node["x"],np.float64)))
        need(math.isfinite(value),"Frozen HGFX returned nonfinite MATLAB stencil cross-grid scalar")
        h_on_m.append(value)
    h_same_x_h=[fbits(node["value"])==fbits(m_on_h[i]) for i,node in enumerate(py_nodes)]
    h_same_x_m=[fbits(node["value"])==fbits(h_on_m[i]) for i,node in enumerate(mnodes)]
    paired=[]
    for coord in range(3):
        hgcoord=[row for row in classify_stencil(py_nodes)[1] if row["coord_zero_based"]==coord]
        macoord=[row for row in mclassified if row["coord_zero_based"]==coord]
        for step in range(max(len(hgcoord),len(macoord))):
            a=hgcoord[step] if step<len(hgcoord) else None
            b=macoord[step] if step<len(macoord) else None
            for sign in ("positive","negative"):
                aa=a[sign] if a else None
                bb=b[sign] if b else None
                paired.append({
                    "coord_zero_based":coord,"step_one_based":step+1,"sign":sign,
                    "both_present":aa is not None and bb is not None,
                    "same_stencil_x_binary64":
                        xbits(aa["x"])==xbits(bb["x"]) if aa and bb else None,
                    "hgfx_own_x":aa["x"] if aa else None,
                    "matlab_own_x":bb["x"] if bb else None,
                    "hgfx_own_objective":aa["value"] if aa else None,
                    "matlab_own_objective":bb["value"] if bb else None,
                })
    report={
        "schema":"perf01d-initial-ridders-same-x-both-objectives-v1",
        "status":"AUTHOR_SIDE_BOTH_REAL_RIDDERS_INITIAL_SOURCE_STENCILS_NOT_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "source_hgfx_sha256":sha256(py_bytes).hexdigest(),
        "source_matlab_sha256":sha256(mbytes).hexdigest(),
        "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
        "original_failure":{"traj.mu":4,"traj.muhat":4},
        "source_x0":START,"hgfx_step_counts":hsteps,"matlab_step_counts":msteps,
        "hgfx_objective_eval_count":len(py_nodes),
        "matlab_objective_eval_count":len(mnodes),
        "hgfx_original_gradient":hg["hgfx_gradient"],
        "matlab_actual_private_gradient":ma["matlab_gradient"],
        "hgfx_original_ridders_error":hg["hgfx_error"],
        "matlab_actual_private_ridders_error":ma["matlab_error"],
        "per_gradient_coordinate_abs_difference":[abs(a-b) for a,b in zip(hg["hgfx_gradient"],ma["matlab_gradient"])],
        "same_x_hgfx_own_stencil_objective_equal_binary64_count":sum(h_same_x_h),
        "same_x_hgfx_own_stencil_objective_unequal_binary64_count":len(py_nodes)-sum(h_same_x_h),
        "same_x_matlab_own_stencil_objective_equal_binary64_count":sum(h_same_x_m),
        "same_x_matlab_own_stencil_objective_unequal_binary64_count":len(mnodes)-sum(h_same_x_m),
        "original_own_stencil_pair_inventory":paired,
        "all_hgfx_own_stencil_nodes":[{"index":i,"x":z["x"],"hgfx_value":z["value"],
                                       "matlab_value_same_x":m_on_h[i],
                                       "same_objective_binary64":h_same_x_h[i]}
                                      for i,z in enumerate(py_nodes)],
        "all_matlab_own_stencil_nodes":[{"index":i,"x":z["x"],"matlab_value":z["value"],
                                        "hgfx_value_same_x":h_on_m[i],
                                        "same_objective_binary64":h_same_x_m[i]}
                                       for i,z in enumerate(mnodes)],
        "matlab_26_fields_plus_complete_iter_exact":"PRODUCER_TRUE_REQUIRES_SEPARATE_RAW_MAT_CHECK",
        "matlab_private_ridders_internal_if_branch_events":"NOT_CAPTURED",
        "hgfx_ridders_internal_if_branch_events":"NOT_CAPTURED",
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN",
        "performance_timing":"NOT_RUN","gpu":"NOT_RUN"
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({k:v for k,v in report.items()
                      if k not in ("original_own_stencil_pair_inventory",
                                   "all_hgfx_own_stencil_nodes","all_matlab_own_stencil_nodes")},
                     sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=("prepare","verify"),required=True)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--old-bfgs",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--hgfx-source",type=Path)
    p.add_argument("--matlab-source",type=Path)
    a=p.parse_args()
    if a.stage=="prepare":
        prepare(a.root,a.old_bfgs,a.output)
    else:
        need(a.hgfx_source is not None and a.matlab_source is not None,
             "Both real MATLAB/HGFX source archives required")
        verify(a.root,a.old_bfgs,a.hgfx_source,a.matlab_source,a.output)


if __name__=="__main__":main()
