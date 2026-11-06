#!/usr/bin/env python3
"""Issue 89 / PERF-01D: archive exact full fitModel trajectory of subject 7.

Runs the untouched public HGFX v1.0.0 fitting workflow with original 64-case
input/config/start. A new author-side diagnostic only; does not revise the
original 63/64 scientific classification or authorize a runtime comparison.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
import os
from pathlib import Path

import numpy as np
from hgfx import fit_model

from fit_cohort_hgfx import FIT_FIELDS
from generate_inputs import digest, encode
from scientific_preflight import decode_number, verify
from trialwise_hgfx_export import clean

SUBJECT = 7
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
BASE_RUN = "41863441006"


def execute(root: Path, original: Path) -> dict:
    if metadata.version("hgfx") != "1.0.0":
        raise ValueError("Not frozen hgfx==1.0.0")
    verify(root)
    summary_path = original / f"summary-{BASE_RUN}.json"
    summary = json.loads(summary_path.read_bytes())
    if (summary.get("github_run_id") != BASE_RUN
            or summary.get("hgfx_sha") != HGFX_SHA
            or summary.get("matlab_sha") != MATLAB_SHA
            or summary.get("classification_counts") != {
                "FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH": 1,
                "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES": 63,
            }
            or summary.get("cases", [])[SUBJECT].get("mismatched_fields")
                 != ["traj.mu", "traj.muhat"]):
        raise ValueError("Original 64-fit scientific NON-PASS was altered")
    for filename, checksum in summary["raw_evidence_sha256"].items():
        if digest((original/filename).read_bytes()) != checksum:
            raise ValueError(f"Original raw full-fit bytes changed: {filename}")
    old = json.loads((original/"hgfx_raw.json").read_bytes())["cases"][SUBJECT]
    if (old["subject_index_zero_based"] != SUBJECT
            or old["status"] != "HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            or old["n_rand_init"] != 0
            or not old["start_matches_frozen_snapshot"]):
        raise ValueError("Original HGFX fitted subject-7 status changed")
    inp = root/"inputs"/"binary_128_s64.json"
    cfg = root/"configs"/"hgf_binary_128.json"
    if (digest(inp.read_bytes()) != summary["hgfx_input_sha256"]
            or digest(cfg.read_bytes()) != summary["hgfx_config_sha256"]):
        raise ValueError("Original 128-trial input/config source changed")
    data = json.loads(inp.read_bytes())
    config = json.loads(cfg.read_bytes())
    u=np.asarray(data["u"][SUBJECT],dtype=np.float64)
    y=np.asarray(data["y"][SUBJECT],dtype=np.float64)
    start=np.asarray([decode_number(v) for v in config["transformed_start_full"]],
                     dtype=np.float64)
    if u.shape!=(128,) or y.shape!=(128,) or len(start)!=15:
        raise ValueError("Original binary subject/config shape changed")
    fit=fit_model(y,u,"hgf_binary_config","unitsq_sgm_config",
                  "quasinewton_optim_config")
    opt=fit.optim
    saved_start=np.asarray(opt["init"],dtype=np.float64)
    if (not np.array_equal(saved_start,start,equal_nan=True)
            or int(fit.c_opt.nRandInit)!=0
            or not np.array_equal(saved_start,
                 np.asarray(old["optim"]["init"],np.float64),equal_nan=True)):
        raise ValueError("Frozen optimizer start/restart policy changed")
    vals=np.asarray(opt["iter"]["val"],np.float64)
    history=np.asarray(opt["iter"]["x"],np.float64)
    if (vals.shape!=(101,) or history.shape!=(101,3)
            or not np.array_equal(np.flatnonzero(np.isfinite(vals)),np.arange(25))):
        raise ValueError("Original subject-7 optimizer history shape/finite slots changed")
    traj={k:clean(v) for k,v in fit.traj.items()}
    if set(traj)!=set(old["traj"]):
        raise ValueError("Public full-fitting trajectory field schema changed")
    for name in ("mu","muhat"):
        if np.asarray(traj[name],dtype=np.float64).shape!=(128,3):
            raise ValueError(f"Unexpected full fitted trajectory {name} shape")
    optim={
        name:clean(opt[name].to_dict() if hasattr(opt[name],"to_dict") else opt[name])
        for name in FIT_FIELDS
    }
    return {
        "schema":"perf01d-subject7-full-fit-traj-hgfx-v1",
        "status":"AUTHOR_SIDE_UNTIMED_COMPLETE_PUBLIC_FIT_NO_PARITY_DECISION",
        "subject_index_zero_based":SUBJECT,
        "trials":128,
        "model":"hgf_binary",
        "observation":"unitsq_sgm",
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run_id":BASE_RUN,
        "original_64_raw_sha256":summary["raw_evidence_sha256"],
        "source_input_sha256":digest(inp.read_bytes()),
        "source_config_sha256":digest(cfg.read_bytes()),
        "frozen_start_matches":True,
        "n_rand_init":int(fit.c_opt.nRandInit),
        "history_buffer_slots":int(vals.size),
        "finite_history_slots":int(np.isfinite(vals).sum()),
        "blas_mode_requested":os.environ.get("OPENBLAS_CORETYPE"),
        "optim":optim,
        "traj":traj,
        "limitations":[
            "New HGFX v1.0.0 public refit on exact original subject/data, not the original 64-subject evidence.",
            "Original MATLAB has NOT been rerun on this host.",
            "This is not an independent oracle classification or an approved scientific exception.",
            "No timing, GPU validation, case selection, threshold relaxation, or benchmark freeze.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    obj=execute(a.input,a.original)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(obj))
    print(json.dumps({
        "status":obj["status"],"mode":obj["blas_mode_requested"],
        "trajectory_fields":sorted(obj["traj"]),
        "mu_shape":list(np.asarray(obj["traj"]["mu"]).shape),
        "original_scientific_result":"63/64 NONPASS",
    },sort_keys=True))


if __name__=="__main__":
    main()
