#!/usr/bin/env python3
"""PERF-01D: same-vector full HGF forward trajectories at BOTH archived fit endpoints.

NO optimization, timing or new scientific case. Three vectors are declared
before observing new results: original HGFX endpoint, original MATLAB endpoint,
and frozen initial start. MATLAB reference is evaluated at exactly the same
transformed full 15-vector, not separately optimized.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np

from generate_inputs import digest, encode
from scientific_preflight import FORWARD, decode_number, verify
from trialwise_hgfx_export import clean

HGFX_SHA="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA="2437f4dc241541072722a2695ddeca7b44d83dd3"
ORIGINAL_RUN="41863441006"
SUBJECT=7
ANCHORS=("original_hgfx_fitted_endpoint","original_matlab_fitted_endpoint",
         "original_frozen_start")
FIELDS={"mu","muhat","sa","sahat","da","epsi","psi","ud","v","w","wt"}


def run(root:Path,original:Path)->dict:
    if metadata.version("hgfx")!="1.0.0":
        raise ValueError("Original model must run from frozen release v1.0.0")
    verify(root)
    summary=json.loads((original/f"summary-{ORIGINAL_RUN}.json").read_bytes())
    if (summary.get("github_run_id")!=ORIGINAL_RUN
            or summary.get("hgfx_sha")!=HGFX_SHA
            or summary.get("matlab_sha")!=MATLAB_SHA
            or summary["cases"][SUBJECT]["mismatched_fields"]!=["traj.mu","traj.muhat"]
            or summary["classification_counts"]!={"FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1,
                   "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63}):
        raise ValueError("Immutable 63/64 source gate was modified")
    cases={}
    for engine in ("hgfx","matlab"):
        filename=engine+"_raw.json"
        if digest((original/filename).read_bytes())!=summary["raw_evidence_sha256"][filename]:
            raise ValueError(f"Original {engine} full-fit raw SHA changed")
        raw=json.loads((original/filename).read_bytes())
        if len(raw["cases"])!=64:
            raise ValueError("Original full fitting subject inventory incomplete")
        case=raw["cases"][SUBJECT]
        if (case["subject_index_zero_based"]!=SUBJECT
                or not case["start_matches_frozen_snapshot"]
                or case["n_rand_init"]!=0
                or case["status"]!=engine.upper()+"_FULL_FIT_COMPLETED_NO_PARITY_DECISION"):
            raise ValueError(f"Original {engine} fitting source identity wrong")
        cases[engine]=case
    source=root/"inputs"/"binary_128_s64.json"
    config=root/"configs"/"hgf_binary_128.json"
    if (digest(source.read_bytes())!=summary["hgfx_input_sha256"]
            or digest(config.read_bytes())!=summary["hgfx_config_sha256"]):
        raise ValueError("Original input/config SHA differs")
    d=json.loads(source.read_bytes())
    c=json.loads(config.read_bytes())
    u=np.asarray(d["u"][SUBJECT],dtype=np.float64)
    y=np.asarray(d["y"][SUBJECT],dtype=np.float64)
    if u.shape!=(128,) or y.shape!=(128,):
        raise ValueError("Original subject shape mismatch")
    nprc=len(c["perceptual"]["parameters"])
    nobs=len(c["observation"]["parameters"])
    start=np.asarray([decode_number(p) for p in c["transformed_start_full"]],
                     dtype=np.float64)
    if nprc!=14 or nobs!=1 or start.shape!=(15,):
        raise ValueError("Original perceptual/observation parameter split altered")
    endpoints={
        "original_hgfx_fitted_endpoint":np.asarray(cases["hgfx"]["optim"]["final"],float),
        "original_matlab_fitted_endpoint":np.asarray(cases["matlab"]["optim"]["final"],float),
        "original_frozen_start":start,
    }
    if (not np.array_equal(np.asarray(cases["hgfx"]["optim"]["init"],float),start,equal_nan=True)
            or not np.array_equal(np.asarray(cases["matlab"]["optim"]["init"],float),start,equal_nan=True)
            or c["fit_free_indices_0based"]!=[12,13,14]):
        raise ValueError("Fitted endpoints and original start/free-coordinate identity invalid")
    rows=[]
    for name in ANCHORS:
        params=endpoints[name]
        if params.shape!=(15,) or not np.array_equal(np.isnan(params),np.isnan(start)):
            raise ValueError(f"Frozen 15-component transformed vector malformed: {name}")
        traj,states=FORWARD["hgf_binary"](
            u,params[:nprc],transformed=True,
            ignored_trials=np.flatnonzero(np.isnan(u)).tolist())
        if set(traj)!=FIELDS or np.asarray(states).shape!=(128,3,4):
            raise ValueError("Frozen HGF forward schema or 128x3x4 states changed")
        for field in FIELDS:
            if np.asarray(traj[field]).shape!=((128,2) if field=="w" else (128,3)):
                raise ValueError(f"Malformed frozen forward trajectory {field}")
        rows.append({
            "origin":name,
            "status":"EVALUATED_IDENTICAL_FROZEN_VECTOR_HGFX",
            "full_transformed_vector":clean(params),
            "traj":clean(traj),
            "inf_states":clean(states),
        })
    return {
        "schema":"perf01d-subject7-crossed-forward-hgfx-v1",
        "status":"SAME_VECTOR_FORWARD_DIAGNOSTIC_NO_FULL_FIT_NO_TIMING_NO_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "source_run_id":ORIGINAL_RUN,
        "original_raw_sha256":summary["raw_evidence_sha256"],
        "source_input_sha256":digest(source.read_bytes()),
        "source_config_sha256":digest(config.read_bytes()),
        "subject_index_zero_based":SUBJECT,
        "trials":128,
        "model":"hgf_binary",
        "perceptual_parameter_count":nprc,
        "observation_parameter_count":nobs,
        "free_indices_zero_based":[12,13,14],
        "anchor_origins":list(ANCHORS),
        "original_endpoints_unmodified":True,
        "cases":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=run(a.input,a.original)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(result))
    print(json.dumps({"cases":len(result["cases"]),"anchors":result["anchor_origins"],
                      "status":result["status"]},sort_keys=True))


if __name__=="__main__":
    main()
