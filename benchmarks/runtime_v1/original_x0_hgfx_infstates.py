#!/usr/bin/env python3
"""SHA-locked genuine frozen HGFX HGF infStates + native unitsq LL at all real x0 Ridders nodes.

The original source HGFX objective and 128 trial LL values must be reproduced
bitwise. Original MATLAB private source node coordinates and all failed 63/64
scientific acceptance evidence must remain unchanged. No threshold or fitting.
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
from hgfx.models.hgf_binary import hgf_binary
from hgfx.responses.unitsq_sigmoid import unitsq_sgm
from hgfx.math.matlab_exp import matlab_exp_scalar
from hgfx.compat.configs import unitsq_sgm_config
from hgfx.core.trials import build_trial_masks

from subject7_first_ridders_stencil import base_problem, xbits, xhex, HGFX, MATLAB, START
from replay_initial_ridders_stencil_archive import MEMBERS, RUN, SOURCE_SHA, scientific_original

ORIGINAL_TERM_SHA={
 "original-hgfx-71-objective-terms.json":"eb085a07e633aa10979602d9f9fb5e9221e2a1132aecd9fb7b73953a4d2850df",
 "original-matlab-71-objective-terms.json":"4d9cd77d1187f203a0b467b602d6ab74b4283f2c76476c97d5c8b9e3dc95d0ea",
 "independent-71-node-likelihood-and-prior-source-audit.json":"4bfedca4318343bfa3422a5f85e150b039771e53a7a2823995309feac15e0d25",
}
FIELD_NAMES=("muhat","sahat","mu","sa")
SCHEMA="perf01d-frozen-hgfx-infstates-71-native-obs-v1"


def require(v,s):
    if not v:raise ValueError(s)


def same(a,b):
    return struct.pack(">d",float(a))==struct.pack(">d",float(b))


def floats(a,allow_nan=False):
    z=np.asarray(a,dtype=np.float64).reshape(-1)
    require(np.all(np.isfinite(z)|np.isnan(z)),"Inf in frozen original HGF infStates")
    if not allow_nan:
        require(np.isfinite(z).all(),"Nonfinite original observation predictor or logp")
    return [float(v) if np.isfinite(v) else None for v in z]


def serialize_states(states):
    arr=np.asarray(states,dtype=np.float64)
    require(arr.shape==(128,3,4),"Original 128x3x4 frozen binary HGF source infStates shape changed")
    return {
        name:[[float(v) if np.isfinite(v) else None for v in row]
              for row in arr[:,:,component]]
        for component,name in enumerate(FIELD_NAMES)
    }


def collect(root,bfgs,x0,original_terms,output):
    p,failed=base_problem(root,bfgs)
    scientific_original(failed)
    raw={}
    for fname in ("hgfx-first-ridders.json","matlab-first-private-ridders.json"):
        bb=(x0/fname).read_bytes()
        require(sha256(bb).hexdigest()==MEMBERS[fname],
                "Original 71 true MATLAB/HGFX node source digest changed")
        raw[fname]=json.loads(bb)
    src={}
    for fname,known in ORIGINAL_TERM_SHA.items():
        bb=(original_terms/fname).read_bytes()
        require(sha256(bb).hexdigest()==known,
                "Frozen original first gradient objective terms source SHA256 changed")
        src[fname]=json.loads(bb)
    hg=raw["hgfx-first-ridders.json"]
    ml=raw["matlab-first-private-ridders.json"]
    hterms=src["original-hgfx-71-objective-terms.json"]
    mterms=src["original-matlab-71-objective-terms.json"]
    audit=src["independent-71-node-likelihood-and-prior-source-audit.json"]
    require(hg["frozen_hgfx_sha"]==HGFX and hg["frozen_matlab_sha"]==MATLAB
            and hg["environment"]["github_run_id"]==RUN
            and hg["environment"]["github_sha"]==SOURCE_SHA
            and hterms["original_scientific_fit"]=="63/64 SCIENTIFIC NONPASS"
            and mterms["original_scientific_fit"]=="63/64 SCIENTIFIC NONPASS"
            and audit["first_gradient_same_x_joint_unequal_count"]==14
            and audit["all_71_original_joint_source_values_reconstructed_exact_each_engine"] is True
            and len(hg["hgfx_nodes"])==len(ml["matlab_nodes"])==
                len(hterms["nodes"])==len(mterms["nodes"])==71,
            "Genuine frozen 71-node objective algebra/source lineage is not authenticated")

    obs_config=unitsq_sgm_config()
    require(int(obs_config.options["predorpost"])==1,
            "Original frozen observation family is no longer default predictor")
    masks=build_trial_masks(p.responses,p.inputs)
    irreg=np.flatnonzero(masks.irregular).astype(int).tolist()
    ignored=np.flatnonzero(masks.ignored).astype(int).tolist()
    rows=[]
    for i in range(71):
        hh=hg["hgfx_nodes"][i];mm=ml["matlab_nodes"][i]
        rh=hterms["nodes"][i];rm=mterms["nodes"][i]
        x=hh["x"]
        require(i==hh["ordinal"]==mm["ordinal"]==
                rh["original_node_index"]==rm["original_node_index"]
                and xbits(x)==xbits(mm["x"])==xbits(rh["x"])==xbits(rm["x"])
                and xhex(x)==hh["x_hex"]==mm["x_hex"],
                "Original 71 source node order/coordinate bits changed")
        full=p.expand(x)
        prc=full[:p.n_perceptual]
        obs=full[p.n_perceptual:]
        traj,states=hgf_binary(p.inputs,prc,transformed=True,
                               ignored_trials=ignored)
        require(states.shape==(128,3,4),"Frozen original HGF returned wrong infStates dimensions")
        predicted=floats(states[:,0,0])
        posterior=floats(states[:,0,2])
        logp,_,_=unitsq_sgm(p.responses,states,obs,irregular_trials=irreg,predorpost=1)
        native_ll=floats(logp)
        term=rh["components"]
        require(len(term["full_trial_log_likelihood"])==len(native_ll)==128,
                "Frozen 128 trial original HGFX objective source terms missing")
        require(all(same(a,b) for a,b in zip(native_ll,term["full_trial_log_likelihood"])),
                "New frozen HGF+observation source output differs from previous original true HGFX trial LL at node "+str(i))
        total=float(p.evaluate_free(x))
        require(same(total,hh["value"]) and
                same(total,rh["original_hgfx_source_scalar"]) and
                same(mm["value"],rm["original_matlab_private_source_scalar"]),
                "Frozen source objective total no longer exact at node "+str(i))
        zeta=float(matlab_exp_scalar(obs[0]))
        require(math.isfinite(zeta),"Original native observation zeta invalid")
        rows.append({
            "ordinal":i,"x":x,"x_hex":xhex(x),
            "native_source_objective":total,
            "original_matlab_private_source_objective":mm["value"],
            "native_logp":native_ll,"native_prediction_level1":predicted,
            "native_posterior_level1":posterior,
            "native_zeta":zeta,"native_inf_states":serialize_states(states),
        })
    result={
        "schema":SCHEMA,
        "status":"ORIGINAL_FROZEN_HGFX_INFSTATES_AND_UNITSQ_SOURCE_EXACT_ALL_71",
        "frozen_hgfx_sha":HGFX,"frozen_matlab_sha":MATLAB,
        "original_true_private_ridders_run":RUN,
        "original_true_private_ridders_sha":SOURCE_SHA,
        "original_constituents_source_run":"42402421462",
        "original_constituents_source_sha":"3ae1ac5330bd1b6bc1ea8017f16f0f66be6b3b57",
        "original_scientific_fitting":"63/64 SCIENTIFIC NONPASS",
        "original_failures":{"traj.mu":4,"traj.muhat":4},
        "original_71_node_count":len(rows),"n_trials":128,
        "inf_states_shape_per_node":[128,3,4],
        "selected_source_infstate_component":"muhat",
        "predorpost":1,
        "original_irregular_trial_indices_zero_based":irreg,
        "nodes":rows,
        "original_source_term_sha256":ORIGINAL_TERM_SHA,
        "environment":{"run_id":os.environ.get("GITHUB_RUN_ID",""),
                       "tested_sha":os.environ.get("GITHUB_SHA",""),
                       "platform":platform.platform(),"numpy":np.__version__,
                       "python":sys.version},
        "independent_scientific_review":"NOT_RECEIVED",
        "perf01c":"NOT_FROZEN","paper_timing":"NOT_RUN","physical_gpu":"NOT_RUN",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,allow_nan=False,indent=2,sort_keys=True)+"\n")
    output.with_suffix(".sha256").write_text(sha256(output.read_bytes()).hexdigest()+"\n")
    print(json.dumps({"source":"HGFX","nodes":len(rows),"trials":128,
                      "old_real_hgfx_source_trial_ll_exact":"71x128",
                      "old_original_fitting":"63/64 SCIENTIFIC NONPASS"},sort_keys=True))


def main():
    parser=argparse.ArgumentParser()
    for f in ("root","old-bfgs","original-x0","original-terms","output"):
        parser.add_argument("--"+f,type=Path,required=True)
    a=parser.parse_args()
    collect(a.root,a.old_bfgs,a.original_x0,a.original_terms,a.output)


if __name__=="__main__":main()
