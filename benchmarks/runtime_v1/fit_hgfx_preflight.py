#!/usr/bin/env python3
"""Diagnostic full fitModel boundary on one eligible prospective HGF case.

No timing: fitting eligibility and inference parity must precede benchmark.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import traceback

import numpy as np
from importlib import metadata
from hgfx import fit_model

from scientific_preflight import verify
from trialwise_hgfx_export import clean
from generate_inputs import digest, encode


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    verify(a.input)
    if metadata.version("hgfx")!="1.0.0":
        raise RuntimeError("Requires immutable HGFX 1.0.0")
    out={
      "schema":"perf01-hgfx-full-fitting-diagnostic-v1",
      "status":"EXPLORATORY_UNFROZEN_NOT_TIMING",
      "hgfx_version":metadata.version("hgfx"),
      "release_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
      "cases":[],
    }
    for n in (128,512,1024):
        f=a.input/"inputs"/f"binary_{n}_s64.json"
        data=json.loads(f.read_bytes())
        record={
            "case_id":f"primary_fit_compat_full_{n}",
            "n_trials":n,"input_sha256":digest(f.read_bytes()),
            "status":"NOT_RUN",
        }
        if n in (512,1024):
            record["status"]="BLOCKED_UNSTABLE_DEFAULT_START_MATLAB_RESAMPLES_HGFX_REJECTS"
        else:
            try:
                y=np.asarray(data["y"][0],dtype=np.float64)
                u=np.asarray(data["u"][0],dtype=np.float64)
                fit=fit_model(y,u,"hgf_binary_config","unitsq_sgm_config",
                              "quasinewton_optim_config")
                result=fit.optim
                selected=("init","final","H","Sigma","Corr","trialLogLlsplit",
                          "negLl","negLj","LME","decompLME","AIC","BIC",
                          "yhat","res","resAC")
                record["status"]="HGFX_FULL_FIT_COMPLETED_PARITY_NOT_ASSESSED"
                record["optim"]={k:clean(result[k]) for k in selected}
                record["traj"]={k:clean(v) for k,v in fit.traj.items()}
                record["n_rand_init"]=int(fit.c_opt.nRandInit)
            except Exception as exc:
                record["status"]="HGFX_FULL_FIT_ERROR"
                record["error"]=f"{type(exc).__name__}: {exc}"
                record["traceback"]=traceback.format_exc(limit=5)
        out["cases"].append(record)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(out))
    print(json.dumps({x["case_id"]:x["status"] for x in out["cases"]},sort_keys=True))


if __name__=="__main__":
    main()
