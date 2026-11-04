#!/usr/bin/env python3
"""PERF-01B/D: all 64 subjects x 3 model families x 3 horizons, HGFX only.

Fixed vector validation of configurations, forward and objective. Not timing.
No input replacement, retries, fitting or gate promotion.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
import math
from pathlib import Path

import numpy as np

from generate_inputs import digest, encode
from scientific_preflight import CONFIG, FORWARD, decode_number, verify
from hgfx.compat.configs import unitsq_sgm_config
from hgfx.compat.objective import evaluate_objective
from hgfx.responses.unitsq_sigmoid import unitsq_sgm


MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
HORIZONS = (128, 512, 1024)
SUBJECTS = 64


def check_config(perceptual, observation, snapshot):
    prc=snapshot["perceptual"]
    obs=snapshot["observation"]
    if (perceptual.model != prc["name"] or observation.model != obs["name"]
        or len(perceptual.parameters) != len(prc["parameters"])
        or len(observation.parameters) != len(obs["parameters"])):
        return False
    for cfg,rows in ((perceptual,prc["parameters"]),(observation,obs["parameters"])):
        for p,s in zip(cfg.parameters,rows):
            if (p.name!=s["name"] or p.matlab_index!=s["matlab_index_1based"]
                or p.transform.kind.value!=s["transform"]):
                return False
            if not (np.isclose(p.prior_mean,decode_number(s["prior_mean"]),atol=0,rtol=0,equal_nan=True)
                and np.isclose(p.prior_variance,decode_number(s["prior_variance"]),atol=0,rtol=0,equal_nan=True)):
                return False
    return True


def run(root):
    manifest,config_manifest=verify(root)
    versions={"hgfx":metadata.version("hgfx"),"numpy":np.__version__}
    if versions["hgfx"]!="1.0.0":
        raise ValueError("Expected frozen HGFX 1.0.0")
    rows=[]
    for n in HORIZONS:
        source=root/"inputs"/f"binary_{n}_s64.json"
        contents=source.read_bytes()
        data=json.loads(contents)
        assert data["trial_count"]==n and data["subject_count"]==SUBJECTS
        for model in MODELS:
            snap_path=root/"configs"/f"{model}_{n}.json"
            snap=json.loads(snap_path.read_bytes())
            full=np.array([decode_number(v) for v in snap["transformed_start_full"]],dtype=np.float64)
            for idx in range(SUBJECTS):
                row={"model":model,"trials":n,"subject_index_zero_based":idx,
                     "source_sha256":digest(contents),"config_sha256":digest(snap_path.read_bytes()),
                     "config_matches_snapshot":False,
                     "forward_status":"NOT_RUN","objective_status":"NOT_RUN",
                     "negative_log_joint":None,"negative_log_likelihood":None}
                u=np.asarray(data["u"][idx],dtype=np.float64)
                y=np.asarray(data["y"][idx],dtype=np.float64)
                try:
                    prc=CONFIG[model]().resolve_placeholders(u)
                    obs=unitsq_sgm_config()
                    n_prc=len(prc.parameters)
                    valid=(check_config(prc,obs,snap)
                           and np.array_equal(full[:n_prc],prc.priormus,equal_nan=True)
                           and np.array_equal(full[n_prc:],obs.priormus,equal_nan=True))
                    row["config_matches_snapshot"]=bool(valid)
                    if not valid:
                        row["forward_status"]="BLOCKED_CONFIG_MISMATCH"
                        row["objective_status"]="BLOCKED_CONFIG_MISMATCH"
                        rows.append(row); continue
                    pp,po=full[:n_prc],full[n_prc:]
                    try:
                        _,states=FORWARD[model](u,pp,transformed=True)
                        if np.asarray(states).shape!=(n,3,4):
                            row["forward_status"]="INVALID_SHAPE"
                        else:
                            row["forward_status"]="COMPLETE"
                    except Exception as exc:
                        row["forward_status"]="INVALID_OR_ERROR"
                        row["forward_error"]=f"{type(exc).__name__}: {exc}"
                    result=evaluate_objective(
                        responses=y,inputs=u,
                        perceptual_parameters=pp,observation_parameters=po,
                        perceptual_config=prc,observation_config=obs,
                        perceptual_function=FORWARD[model],
                        observation_function=unitsq_sgm,
                    )
                    if result.rval == 0 and math.isfinite(result.neg_log_joint):
                        row["objective_status"]="COMPLETE"
                        row["negative_log_joint"]=float(result.neg_log_joint)
                        row["negative_log_likelihood"]=float(result.neg_log_likelihood)
                        row["valid_likelihood_trials"]=int(result.regular_mask.sum())
                    else:
                        row["objective_status"]="INVALID_OR_ERROR"
                        row["objective_rval"]=int(result.rval)
                except Exception as exc:
                    row["forward_status"]="ERROR"
                    row["objective_status"]="ERROR"
                    row["exception"]=f"{type(exc).__name__}: {exc}"
                rows.append(row)
    assert len(rows)==len(MODELS)*len(HORIZONS)*SUBJECTS
    return {"schema":"perf01-all-subject-hgfx-v1","protocol_id":"hgfx-matlab-runtime-1",
            "status":"DIAGNOSTIC_ONLY_NO_TIMING_NO_FITTING",
            "source_sha":"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
            "versions":versions,
            "input_manifest_sha256":digest((root/"inputs_manifest.json").read_bytes()),
            "config_manifest_sha256":digest((root/"resolved_configs_manifest.json").read_bytes()),
            "cases":rows}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    obj=run(a.input)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(obj))
    from collections import Counter
    print(json.dumps({"rows":len(obj["cases"]),
          "forward":dict(Counter(x["forward_status"] for x in obj["cases"])),
          "objective":dict(Counter(x["objective_status"] for x in obj["cases"]))},sort_keys=True))


if __name__=="__main__":
    main()
