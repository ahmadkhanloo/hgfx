#!/usr/bin/env python3
"""Frozen HGFX 71 real-source Ridders nodes objective constituent replay.

Only original 71 source x coordinates from run 42389292284 are used.
Every computed original objective scalar MUST be exactly equal in binary64
to the originally recorded frozen HGFX source scalar. No free thresholds.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys
import numpy as np

from subject7_first_ridders_stencil import base_problem, HGFX, MATLAB, START, xbits, xhex
from replay_initial_ridders_stencil_archive import MEMBERS, scientific_original, RUN, SOURCE_SHA

SCHEMA="perf01d-objective-term-decomp-genuine-source-71-v1"


def need(ok, why):
    if not ok:raise ValueError(why)


def b64(value):
    need(isinstance(value,(float,int,np.floating)) and math.isfinite(float(value)),
         "Nonfinite original source scalar")
    return struct.pack(">d",float(value))


def raw_list(a):
    arr=np.asarray(a,dtype=np.float64).reshape(-1)
    need(bool(np.isfinite(arr).all()),"Nonfinite original trial/gaussian source term")
    return [float(z) for z in arr]


def objective_terms(p,x):
    xarray=np.asarray(x,np.float64)
    result=p.evaluate_full(p.expand(xarray))
    need(result.rval==0 and math.isfinite(result.neg_log_joint),
         "Genuine frozen HGFX source objective returned invalid")
    need(len(result.trial_log_likelihoods)==128,
         "Genuine HGFX all 128 trial log-likelihoods required")
    need(len(result.irregular_mask)==128 and len(result.regular_mask)==128,
         "Original HGFX masks changed")
    trial=raw_list(result.trial_log_likelihoods)
    return {
        "full_trial_log_likelihood":trial,
        "regular_trial_mask":[bool(z) for z in result.regular_mask.tolist()],
        "log_likelihood":float(result.log_likelihood),
        "negative_log_likelihood":float(result.neg_log_likelihood),
        "perceptual_prior_terms":raw_list(result.perceptual_prior.terms),
        "perceptual_prior_log_total":float(result.perceptual_prior.total),
        "observation_prior_terms":raw_list(result.observation_prior.terms),
        "observation_prior_log_total":float(result.observation_prior.total),
        "negative_log_joint":float(result.neg_log_joint),
    }


def prepare(root,old,archive,output):
    p,original=base_problem(root,old)
    scientific_original(original)
    records=[]
    raw={}
    for fn in ("hgfx-first-ridders.json","matlab-first-private-ridders.json",
               "true-x0-both-stencils-cross-objective-audit.json"):
        bb=(archive/fn).read_bytes()
        need(sha256(bb).hexdigest()==MEMBERS[fn],
             "Immutable 71 actual MATLAB/HGFX source SHA changed: "+fn)
        raw[fn]=json.loads(bb)
    source=raw["hgfx-first-ridders.json"]
    matlab=raw["matlab-first-private-ridders.json"]
    audit=raw["true-x0-both-stencils-cross-objective-audit.json"]
    need(source["schema"]=="perf01d-initial-real-ridders-3coord-v1"
         and source["frozen_hgfx_sha"]==HGFX and source["frozen_matlab_sha"]==MATLAB
         and source["original_63_subject_fit_status"]=="63/64 SCIENTIFIC NONPASS"
         and source["environment"]["github_run_id"]==RUN
         and source["environment"]["github_sha"]==SOURCE_SHA
         and matlab["source_hgfx_stencil_sha256"]==MEMBERS["hgfx-first-ridders.json"]
         and matlab["original_science"]=="63/64 SCIENTIFIC NONPASS"
         and audit["original_scientific_fitting"]=="63/64 SCIENTIFIC NONPASS",
         "Frozen original 71 source run scientific identity changed")
    need(len(source["hgfx_nodes"])==len(matlab["matlab_nodes"])==71
         and len(audit["all_hgfx_own_stencil_nodes"])==71
         and len(audit["all_matlab_own_stencil_nodes"])==71,
         "Original first-gradient 71 source node inventory altered")
    for i,(h,m,cv,cm) in enumerate(zip(source["hgfx_nodes"],matlab["matlab_nodes"],
                                      audit["all_hgfx_own_stencil_nodes"],
                                      audit["all_matlab_own_stencil_nodes"])):
        x=h["x"]
        need(i==h["ordinal"]==m["ordinal"]==cv["index"]==cm["index"]
             and xbits(x)==xbits(m["x"])==xbits(cv["x"])==xbits(cm["x"])
             and xhex(x)==h["x_hex"]==m["x_hex"],
             "Genuine original MATLAB and HGFX first-gradient source x mismatch")
        term=objective_terms(p,x)
        need(b64(term["negative_log_joint"])==b64(h["value"])
             and b64(term["negative_log_joint"])==b64(cm["hgfx_value_same_x"])
             and b64(m["value"])==b64(cv["matlab_value_same_x"]),
             "Frozen HGFX original scalar source not bitwise reproduced: node "+str(i))
        records.append({"original_node_index":i,"x":x,"x_hex":xhex(x),
                        "original_hgfx_source_scalar":h["value"],
                        "original_matlab_private_source_scalar":m["value"],
                        "components":term})
    result={
        "schema":SCHEMA,"status":"AUTHOR_SIDE_FROZEN_HGFX_71_SOURCE_TERM_DECOMPOSITION",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "original_real_source_run":RUN,"original_real_source_sha":SOURCE_SHA,
        "original_hgfx_source_member_sha256":MEMBERS["hgfx-first-ridders.json"],
        "original_matlab_source_member_sha256":MEMBERS["matlab-first-private-ridders.json"],
        "original_cross_source_member_sha256":MEMBERS["true-x0-both-stencils-cross-objective-audit.json"],
        "original_scientific_fit":"63/64 SCIENTIFIC NONPASS",
        "original_failed_fields":{"traj.mu":4,"traj.muhat":4},
        "original_71_source_node_count":len(records),
        "nodes":records,
        "environment":{"run_id":os.getenv("GITHUB_RUN_ID",""),
                       "tested_sha":os.getenv("GITHUB_SHA",""),
                       "python":sys.version,"numpy":np.__version__,
                       "platform":platform.platform()},
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","paper_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    output.with_suffix(".sha256").write_text(sha256(output.read_bytes()).hexdigest()+"\n")
    print(json.dumps({"state":result["status"],"original_nodes":len(records),
                      "genuine_hgfx_scalar_reproduction":"71/71 BINARY64 EXACT",
                      "original_scientific_fit":"63/64 NONPASS"},sort_keys=True))


def main():
    parser=argparse.ArgumentParser()
    for k in ("root","old-bfgs","archive","output"):
        parser.add_argument("--"+k,required=True,type=Path)
    a=parser.parse_args()
    prepare(a.root,a.old_bfgs,a.archive,a.output)


if __name__=="__main__":main()
