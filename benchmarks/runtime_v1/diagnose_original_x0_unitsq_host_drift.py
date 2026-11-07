#!/usr/bin/env python3
"""Four-run SHA-frozen original 71×128 unitsq same-raw-HGF-input host diagnostics.

A mismatch is NEVER tolerated or reclassified; source files are byte locked.
Collects precise first/all mismatched original node/trial bits and CPU/NumPy
runtime diagnostics; strict exit nonzero on any original-source numeric mismatch.
Scientific full fitting remains 63/64 NONPASS; not a release gate or GPU test.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys

import numpy as np
from hgfx.core.trials import build_trial_masks
from hgfx.math.matlab_exp import matlab_exp_scalar
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

from compare_original_x0_infstates_observation import states_check
from replay_initial_ridders_stencil_archive import MEMBERS, scientific_original, ulps, RUN, SOURCE_SHA
from subject7_first_ridders_stencil import base_problem, xbits, xhex, HGFX, MATLAB

REAL_RUN="42404444341"
REAL_SHA="a6168bb2b1be07a0f084abc07599e9ffda61b22b"
H_SOURCE_SHA="53c998070dbbfc8b8a5c5ce7e8d962b44f9820635f60c567fd2012bf48fcd415"
M_SOURCE_SHA="15c2f3e50d3ff257d333e412b881053cd6bc0240137ddbae448b3ce7d1647006"
INDEPENDENT_SHA="5d1d03f200bb8be7bf058fe54d64e63ab8909a29857a6750014bad83db029af0"
OLD_H_TERMS_SHA="eb085a07e633aa10979602d9f9fb5e9221e2a1132aecd9fb7b73953a4d2850df"


def need(v,why):
    if not v:raise ValueError(why)


def identical(x,y):
    if type(x) not in (float,int) or type(y) not in (float,int) or not math.isfinite(x) or not math.isfinite(y):
        raise ValueError("Original genuine or freshly computed trial observation scalar nonfinite")
    return struct.pack(">d",float(x))==struct.pack(">d",float(y))


def compare_bits(expected,actual):
    need(type(expected) is list and type(actual) is list and
         len(expected)==len(actual)==128,
         "Original/host rerun 128-trial observation vector incomplete")
    rows=[]
    for i,(a,b) in enumerate(zip(expected,actual)):
        if not identical(a,b):
            rows.append({
                "trial_index_zero_based":i,
                "original_native_logp":a,
                "replayed_native_logp":b,
                "original_hex":float(a).hex(),
                "replay_hex":float(b).hex(),
                "original_binary64_big_endian":struct.pack(">d",float(a)).hex(),
                "replayed_binary64_big_endian":struct.pack(">d",float(b)).hex(),
                "absolute_difference":abs(float(a)-float(b)),
                "binary64_ordered_ulp_distance":ulps(float(a),float(b)),
            })
    return rows


def runtime_fingerprint():
    cpu={}
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if ":" not in line:continue
            k,v=(x.strip() for x in line.split(":",1))
            if k in ("vendor_id","model name","flags","cpu family","model","stepping","microcode"):
                if k=="flags":
                    cpu[k]=v.split()
                else:cpu[k]=v
            if "flags" in cpu:break
    except OSError:
        cpu["status"]="not available"
    runtime=io.StringIO()
    with redirect_stdout(runtime):
        np.show_runtime()
    return {
        "python":sys.version,
        "numpy":np.__version__,
        "numpy_runtime":runtime.getvalue(),
        "platform":platform.platform(),
        "machine":platform.machine(),
        "libc":list(platform.libc_ver()),
        "kernel":platform.release(),
        "cpuinfo_first_core":cpu,
        "available_cpu_count":os.cpu_count(),
        "thread_env":{k:os.environ.get(k,"") for k in (
            "OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS",
            "NPY_DISABLE_CPU_FEATURES","JAX_PLATFORMS")},
    }


def audited_sample(h,old_h,old_x,problem):
    need(h["schema"]=="perf01d-frozen-hgfx-infstates-71-native-obs-v1"
         and h["status"]=="ORIGINAL_FROZEN_HGFX_INFSTATES_AND_UNITSQ_SOURCE_EXACT_ALL_71"
         and h["frozen_hgfx_sha"]==HGFX and h["frozen_matlab_sha"]==MATLAB
         and h["original_true_private_ridders_run"]==RUN
         and h["original_true_private_ridders_sha"]==SOURCE_SHA
         and h["original_constituents_source_run"]=="42402421462"
         and h["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS"
         and h["original_failures"]=={"traj.mu":4,"traj.muhat":4}
         and h["original_71_node_count"]==len(h["nodes"])==71
         and h["inf_states_shape_per_node"]==[128,3,4]
         and h["predorpost"]==1
         and h["selected_source_infstate_component"]=="muhat"
         and h["independent_scientific_review"]=="NOT_RECEIVED"
         and h["perf01c"]=="NOT_FROZEN"
         and h["environment"]["run_id"]==REAL_RUN
         and h["environment"]["tested_sha"]==REAL_SHA,
         "Frozen genuine first-gradient HGF input source/science metadata was modified")
    need(len(old_h["nodes"])==len(old_x["hgfx_nodes"])==71,
         "Old frozen source x0 or original source terms not 71")
    masks=build_trial_masks(problem.responses,problem.inputs)
    irregular=np.flatnonzero(masks.irregular).astype(int).tolist()
    need(h["original_irregular_trial_indices_zero_based"]==irregular,
         "Original irregular-response mask changed")
    details=[];pertrial=[0]*128;nodecounts=[]
    for i,(z,prev,original_x) in enumerate(zip(h["nodes"],old_h["nodes"],old_x["hgfx_nodes"])):
        x=z["x"]
        need(z["ordinal"]==prev["original_node_index"]==original_x["ordinal"]==i
             and xbits(x)==xbits(prev["x"])==xbits(original_x["x"])
             and xhex(x)==z["x_hex"]==original_x["x_hex"],
             "Original HGF source x coordinate/order changed in numerical source host replay")
        saved=z["native_logp"]
        old=prev["components"]["full_trial_log_likelihood"]
        need(not compare_bits(saved,old),"Previous verified original 128 trial LL source no longer equals raw HGF stage")
        state=states_check(z["native_inf_states"],"genuine HGFX HGF source")
        need(all(identical(z["native_prediction_level1"][j],float(state[j,0,0]))
                 for j in range(128)),
             "Original saved level-1 HGF predictor differs from real source state")
        obs=problem.expand(x)[problem.n_perceptual:]
        native_zeta=float(matlab_exp_scalar(obs[0]))
        need(identical(native_zeta,z["native_zeta"]),
             "Original frozen native HGFX observation zeta source changed")
        fresh=unitsq_sgm(problem.responses,state,obs,
                         irregular_trials=irregular,predorpost=1)[0]
        fresh=[float(v) for v in np.asarray(fresh,np.float64).reshape(-1)]
        diffs=compare_bits(saved,fresh)
        nodecounts.append(len(diffs))
        for d in diffs:
            pertrial[d["trial_index_zero_based"]]+=1
        if diffs:
            details.append({
                "original_node_index_zero_based":i,
                "original_true_source_x":x,
                "difference_count":len(diffs),
                "first_difference":diffs[0],
                "every_difference":diffs,
            })
    return {
       "original_node_count":71,
       "original_trials_per_node":128,
       "original_source_trial_scalar_comparisons":71*128,
       "original_source_nodes_with_numerical_mismatch":len(details),
       "total_original_source_trial_scalar_mismatches":sum(nodecounts),
       "first_original_source_numeric_mismatch":
           details[0]["first_difference"]|{"node_index_zero_based":details[0]["original_node_index_zero_based"]}
           if details else None,
       "every_node_with_original_scalar_mismatch":details,
       "all_71_node_mismatch_counts":nodecounts,
       "all_128_trial_position_mismatch_counts":pertrial,
       "all_original_source_equal_this_runner":not bool(details),
    }


def main():
    p=argparse.ArgumentParser()
    for f in ("real-stage","old-terms","old-x","original-fit-root","old-bfgs","output"):
        p.add_argument("--"+f,type=Path,required=True)
    p.add_argument("--replica",type=int,choices=(1,2,3,4),required=True)
    a=p.parse_args()
    expected={
      "original-hgfx-71-infstates-and-native-ll.json":H_SOURCE_SHA,
      "original-matlab-71-infstates-and-cross-ll.json":M_SOURCE_SHA,
      "independent-hgf-infstates-unitsq-71-source-stage.json":INDEPENDENT_SHA,
    }
    raws={}
    for f,sha in expected.items():
        raw=(a.real_stage/f).read_bytes()
        need(sha256(raw).hexdigest()==sha,"Real original 71-node HGF source SHA changed: "+f)
        raws[f]=json.loads(raw)
    original_h=raws["original-hgfx-71-infstates-and-native-ll.json"]
    old_raw=(a.old_terms/"original-hgfx-71-objective-terms.json").read_bytes()
    need(sha256(old_raw).hexdigest()==OLD_H_TERMS_SHA,
         "Previous original HGFX 71 likelihood source SHA changed")
    old_h=json.loads(old_raw)
    old_x_raw=(a.old_x/"hgfx-first-ridders.json").read_bytes()
    need(sha256(old_x_raw).hexdigest()==MEMBERS["hgfx-first-ridders.json"],
         "Original genuine 71 Ridders x source SHA changed")
    old_x=json.loads(old_x_raw)
    problem,failed=base_problem(a.original_fit_root,a.old_bfgs)
    scientific_original(failed)
    capture=audited_sample(original_h,old_h,old_x,problem)
    outcome={
       "schema":"perf01d-frozen-unitsq-observation-fresh-CPU-runner-replay-v1",
       "status":("EXACT_SOURCE_REPLAY" if capture["all_original_source_equal_this_runner"]
                 else "NONEXACT_SOURCE_REPLAY"),
       "original_science":"63/64 SCIENTIFIC NONPASS",
       "original_subject7_failed_traj_mu":4,
       "original_subject7_failed_traj_muhat":4,
       "original_frozen_hgfx":HGFX,
       "original_frozen_matlab":MATLAB,
       "original_real_run":REAL_RUN,
       "original_real_source_sha":REAL_SHA,
       "original_real_source_member_sha256":expected,
       "original_previous_objective_source_sha256":OLD_H_TERMS_SHA,
       "github_run_id":os.environ.get("GITHUB_RUN_ID",""),
       "github_tested_commit":os.environ.get("GITHUB_SHA",""),
       "matrix_replica_one_based":a.replica,
       "environment":runtime_fingerprint(),
       "numerical_observations":capture,
       "cross_host_root_cause":"NOT_CLASSIFIED",
       "independent_scientific_review":"NOT_RECEIVED",
       "perf01c":"NOT_FROZEN",
       "paper_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(outcome,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
       "status":outcome["status"],
       "replica":a.replica,
       "source_mismatched_nodes":capture["original_source_nodes_with_numerical_mismatch"],
       "source_mismatched_trial_scalars":capture["total_original_source_trial_scalar_mismatches"],
       "first_mismatch":capture["first_original_source_numeric_mismatch"],
       "platform":outcome["environment"]["machine"],
       "cpu_model":outcome["environment"]["cpuinfo_first_core"].get("model name","unknown"),
       "science":outcome["original_science"],
    },sort_keys=True))
    need(capture["all_original_source_equal_this_runner"],
         "Source observation replay numerical NONMATCH: raw evidence archived; not a scientific PASS")


if __name__=="__main__":main()
