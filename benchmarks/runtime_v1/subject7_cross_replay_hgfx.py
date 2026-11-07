#!/usr/bin/env python3
"""PERF-01D subject-7 exact-vector cross-replay in frozen HGFX 1.0.0.

No timing, no re-optimization, no dataset edits, no threshold changes. This
compares MATLAB and HGFX at BOTH original optimizer final vectors.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np

from scientific_preflight import verify, CONFIG, FORWARD
from generate_inputs import digest, encode
from trialwise_hgfx_export import clean
from hgfx.compat.configs import unitsq_sgm_config
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

SUBJECT = 7
TRIALS = 128
HGF_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def read_sources(root, fitted):
    verify(root)
    if metadata.version("hgfx") != "1.0.0":
        raise RuntimeError("Subject 7 cross-replay requires hgfx==1.0.0")
    data = json.loads((root/"inputs"/"binary_128_s64.json").read_bytes())
    summary = json.loads((fitted/"summary-41863441006.json").read_bytes())
    if summary.get("hgfx_sha") != HGF_SHA or summary.get("matlab_sha") != MATLAB_SHA:
        raise RuntimeError("Wrong frozen fitting run/source identity")
    sources={}
    for label in ("hgfx", "matlab"):
        path=fitted/(label+"_raw.json")
        expected=summary["raw_evidence_sha256"][label+"_raw.json"]
        actual=digest(path.read_bytes())
        if actual!=expected:
            raise RuntimeError(f"{label} raw fitted outputs changed since evidence archival")
        raw=json.loads(path.read_bytes())
        candidates=[c for c in raw["cases"] if c["subject_index_zero_based"]==SUBJECT]
        if len(candidates)!=1 or candidates[0]["n_trials"] != TRIALS:
            raise RuntimeError(f"Missing canonical fitted subject in {label}")
        c=candidates[0]
        if (c["status"] != (
            "HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION" if label=="hgfx"
            else "MATLAB_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
        ) or not c["start_matches_frozen_snapshot"] or c["n_rand_init"] != 0):
            raise RuntimeError(f"{label} subject 7 did not match fit start/policy")
        sources[label]=np.asarray(c["optim"]["final"], dtype=np.float64)
    return data,summary,sources


def run(root, fitted):
    data,summary,sources=read_sources(root,fitted)
    u=np.asarray(data["u"][SUBJECT],dtype=np.float64)
    y=np.asarray(data["y"][SUBJECT],dtype=np.float64)
    prc=CONFIG["hgf_binary"]().resolve_placeholders(u)
    obs=unitsq_sgm_config()
    n_prc=len(prc.parameters)
    n_obs=len(obs.parameters)
    cases=[]
    for origin,full in sources.items():
        record={"endpoint_source":origin,"status":"NOT_RUN",
                "transformed_final_vector":clean(full)}
        try:
            if len(full)!=n_prc+n_obs:
                raise RuntimeError("Incorrect exact fitted-vector parameter dimension")
            traj,inf_states=FORWARD["hgf_binary"](
                u,full[:n_prc],transformed=True
            )
            logps,yhat,res=unitsq_sgm(
                y,inf_states,full[n_prc:],
                predorpost=int(obs.options.get("predorpost",1)),
            )
            record.update({
                "status":"HGFX_REPLAY_COMPLETED",
                "inf_states":clean(inf_states),
                "traj":clean(traj),
                "trial_log_likelihoods":clean(logps),
                "yhat":clean(yhat),
                "residuals":clean(res),
            })
        except Exception as exc:
            record["status"]="HGFX_REPLAY_ERROR"
            record["error"]=f"{type(exc).__name__}: {exc}"
        cases.append(record)
    # Frozen MATLAB-style full fit vectors may contain nonfinite fixed
    # placeholders. Restrict descriptive deltas to finite paired entries;
    # preserve a separate, fail-closed check of all nonfinite masks.
    ha, ma = sources["hgfx"], sources["matlab"]
    finite = np.isfinite(ha) & np.isfinite(ma)
    nonfinite_patterns_equal = bool(
        np.array_equal(np.isnan(ha), np.isnan(ma))
        and np.array_equal(np.isposinf(ha), np.isposinf(ma))
        and np.array_equal(np.isneginf(ha), np.isneginf(ma))
    )
    endpoint_max_abs_delta = (
        float(np.max(np.abs(ha[finite] - ma[finite])))
        if np.any(finite) else None
    )
    return {
        "schema":"perf01-subject7-hgfx-cross-replay-v1",
        "protocol":"hgfx-matlab-runtime-1",
        "status":"DIAGNOSTIC_UNFROZEN_NOT_TIMED",
        "product_sha":HGF_SHA,
        "oracle_sha":MATLAB_SHA,
        "subject_index_zero_based":SUBJECT,
        "trials":TRIALS,
        "source_run_id":"41863441006",
        "source_report_sha256":digest((fitted/"summary-41863441006.json").read_bytes()),
        "input_sha256":digest((root/"inputs"/"binary_128_s64.json").read_bytes()),
        "endpoint_max_abs_delta":endpoint_max_abs_delta,
        "endpoint_finite_parameter_count":int(np.sum(finite)),
        "endpoint_nonfinite_masks_equal":nonfinite_patterns_equal,
        "cases":cases,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--fitting",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=run(args.input,args.fitting)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(encode(out))
    print(json.dumps({"endpoint_max_abs_delta":out["endpoint_max_abs_delta"],
          "cases":[(c["endpoint_source"],c["status"]) for c in out["cases"]]}))


if __name__=="__main__":
    main()
