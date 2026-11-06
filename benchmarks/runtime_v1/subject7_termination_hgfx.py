#!/usr/bin/env python3
"""PERF-01D: read source-native frozen HGFX public BFGS termination (untimed).

Execute original public fit and independently the exact *frozen* exposed
optimizer on the same 3-free-coordinate objective and start. Require exact
same-session public-versus-direct optimizer output before claiming a reason.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np

from hgfx import fit_model
from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions, quasinewton_optim

from scientific_preflight import verify
from trialwise_hgfx_export import clean
from generate_inputs import digest, encode

HGFX_SHA="4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA="2437f4dc241541072722a2695ddeca7b44d83dd3"
RUN="41863441006"
SUBJECT=7


def execute(root:Path,original:Path)->dict:
    if metadata.version("hgfx")!="1.0.0":
        raise ValueError("Not original frozen HGFX release")
    verify(root)
    s=json.loads((original/f"summary-{RUN}.json").read_bytes())
    if (s.get("github_run_id")!=RUN or s.get("hgfx_sha")!=HGFX_SHA
            or s.get("matlab_sha")!=MATLAB_SHA
            or s.get("classification_counts")!={"FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH":1,
                    "FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES":63}
            or s["cases"][SUBJECT]["mismatched_fields"]!=["traj.mu","traj.muhat"]):
        raise ValueError("Original 63/64 scientific non-PASS identity changed")
    for name,sha in s["raw_evidence_sha256"].items():
        if digest((original/name).read_bytes())!=sha:
            raise ValueError("Original raw full fitting SHA256 changed: "+name)
    source=json.loads((original/"hgfx_raw.json").read_bytes())["cases"][SUBJECT]
    if (source["status"]!="HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            or source["subject_index_zero_based"]!=SUBJECT
            or not source["start_matches_frozen_snapshot"] or source["n_rand_init"]!=0):
        raise ValueError("Original full public fit identity changed")
    inp=root/"inputs"/"binary_128_s64.json"
    cfg=root/"configs"/"hgf_binary_128.json"
    if (digest(inp.read_bytes())!=s["hgfx_input_sha256"]
            or digest(cfg.read_bytes())!=s["hgfx_config_sha256"]):
        raise ValueError("Original frozen binary inputs/config changed")
    data=json.loads(inp.read_bytes())
    u=np.asarray(data["u"][SUBJECT],np.float64)
    y=np.asarray(data["y"][SUBJECT],np.float64)
    if u.shape!=(128,) or y.shape!=(128,):
        raise ValueError("Original trial horizon changed")
    fit=fit_model(y,u,"hgf_binary_config","unitsq_sgm_config",
                  "quasinewton_optim_config")
    if not np.array_equal(np.asarray(fit.optim["init"],float),
                          np.asarray(source["optim"]["init"],float),equal_nan=True):
        raise ValueError("Public source optimizer initial full 15-vector altered")
    problem=hgf_binary_unitsq_fit_problem(y,u)
    if tuple(problem.free_indices)!=(12,13,14):
        raise ValueError("Original 3 transformed free coordinates changed")
    c=QuasiNewtonOptions()
    if (c.tol_arg!=1e-3 or c.tol_grad!=1e-3 or c.max_step!=1.0
            or c.max_iter!=100 or c.max_regu!=16 or c.max_rst!=10 or not c.opt_iter):
        raise ValueError("Original BFGS source options changed")
    expected=np.asarray(fit.optim["init"],float)[list(problem.free_indices)]
    direct=quasinewton_optim(problem.evaluate_free,expected,c)
    public_x=np.asarray(fit.optim["iter"]["x"],float)
    public_val=np.asarray(fit.optim["iter"]["val"],float)
    public_final=np.asarray(fit.optim["final"],float)[list(problem.free_indices)]
    comparable={
        "arg_min":bool(np.array_equal(direct.arg_min,public_final,equal_nan=True)),
        "iter_x":bool(np.array_equal(direct.iter_x,public_x,equal_nan=True)),
        "iter_val":bool(np.array_equal(direct.iter_val,public_val,equal_nan=True)),
    }
    if not all(comparable.values()):
        raise ValueError("Direct source-native optimizer does not exactly reproduce public fit; cannot infer termination")
    if (len(public_val)!=101 or
            np.flatnonzero(np.isfinite(public_val)).tolist()!=list(range(25))):
        raise ValueError("Original expected 101/25 fit buffer source not reproduced")
    return {
        "schema":"perf01d-subject7-source-native-termination-hgfx-v1",
        "status":"AUTHOR_SIDE_DIRECT_FROZEN_OPTIMIZER_TERMINATION_NOT_SCIENTIFIC_PASS",
        "frozen_hgfx_sha":HGFX_SHA,
        "frozen_matlab_sha":MATLAB_SHA,
        "original_64_fit_run_id":RUN,
        "original_raw_sha256":s["raw_evidence_sha256"],
        "source_input_sha256":s["hgfx_input_sha256"],
        "source_config_sha256":s["hgfx_config_sha256"],
        "subject_index_zero_based":SUBJECT,
        "trials":128,
        "model":"hgf_binary",
        "observation_model":"unitsq_sgm",
        "free_indices_zero_based":[12,13,14],
        "original_n_rand_init":0,
        "public_vs_same_source_direct_exact":comparable,
        "source_native_termination":direct.termination,
        "source_native_iterations":int(direct.iterations),
        "source_native_reset_count":int(direct.resets),
        "history_allocated_slots":int(len(public_val)),
        "history_finite_slots":int(np.isfinite(public_val).sum()),
        "public_fitted_full":clean(fit.optim["final"]),
        "direct_fitted_free":clean(direct.arg_min),
        "direct_iter_x":clean(direct.iter_x),
        "direct_iter_val":clean(direct.iter_val),
        "public_traj":clean(fit.traj),
        "note":"No MATLAB reference classification: source-native HGFX optimization stop is not an external scientific parity PASS",
        "limitations":[
            "Only original frozen HGFX v1.0.0 source; direct source replay independently matches same-host public fit",
            "No changed data, start, optimiser settings, restart, seed, threshold or model family",
            "Original complete MATLAB/HGFX 63/64 fitting non-PASS still binding",
            "No timed benchmark, physical GPU or independent scientific adjudication",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--original",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    result=execute(a.input,a.original)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(result))
    print(json.dumps({
        "status":result["status"],
        "termination":result["source_native_termination"],
        "iterations":result["source_native_iterations"],
        "resets":result["source_native_reset_count"],
        "verified":result["public_vs_same_source_direct_exact"],
        "original_science":"63/64 NON-PASS; NO TIMING",
    },sort_keys=True))


if __name__=="__main__":
    main()
