#!/usr/bin/env python3
"""Untimed original subject-7 frozen HGFX objective/Ridders probes.

All probe vectors come from original immutable paired public-fit trace; no
optimization, post-hoc selection, timing, seed/start/tolerance changes.
"""
from __future__ import annotations

import argparse
import json
from importlib import metadata
from pathlib import Path

import numpy as np
from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
from hgfx.optim.ridders import RiddersOptions, ridders_gradient

from generate_inputs import digest, encode
from scientific_preflight import verify
from trialwise_hgfx_export import clean

HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
TRACE_RUN = "42115887599"
TRACE_SHA = "b378fef6ff93f6efa041f4e8304dafba742ae4ab"
TRACE_HASHES = {
    "hgfx_raw.json": "6fe10be1dd1860612859e6efbe7bee13717e4787aed4a62f0e6b67a2072aac7a",
    "matlab_raw.json": "ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f",
}
ANCHOR_INDEX = (0, 1, 13, 14, 23)


def prepare(root: Path, archive: Path):
    verify(root)
    if metadata.version("hgfx") != "1.0.0":
        raise ValueError("Expected exact HGFX v1.0.0")
    prior = json.loads((archive / "summary.json").read_bytes())
    if (prior["github_run_id"] != TRACE_RUN or prior["candidate_sha"] != TRACE_SHA
            or prior["raw_evidence_sha256"] != TRACE_HASHES
            or prior["frozen_hgfx_sha"] != HGFX_SHA
            or prior["frozen_matlab_sha"] != MATLAB_SHA
            or prior["recorded_finite_slots"] != {"hgfx": 25, "matlab": 25}):
        raise ValueError("Original optimizer-trace identity not verified")
    traces = {}
    for origin, filename in (("hgfx","hgfx_raw.json"),("matlab","matlab_raw.json")):
        path = archive / filename
        if digest(path.read_bytes()) != TRACE_HASHES[filename]:
            raise ValueError(f"Archived {filename} checksum mismatch")
        obj = json.loads(path.read_bytes())
        if (obj["subject_index_zero_based"] != 7 or obj["trials"] != 128
                or obj["model"] != "hgf_binary"
                or obj["frozen_hgfx_sha"] != HGFX_SHA
                or obj["frozen_matlab_sha"] != MATLAB_SHA
                or obj["source_run_id"] != "41863441006"
                or not obj["frozen_start_matches"]
                or not obj["original_raw_fits_verified"]
                or obj["n_rand_init"] != 0):
            raise ValueError(f"Wrong original trace scientific identity: {origin}")
        traces[origin] = obj
    source = json.loads((root / "inputs" / "binary_128_s64.json").read_bytes())
    u = np.asarray(source["u"][7],dtype=np.float64)
    y = np.asarray(source["y"][7],dtype=np.float64)
    if u.shape != (128,) or y.shape != (128,):
        raise ValueError("Original 128-trial subject identity changed")
    problem = hgf_binary_unitsq_fit_problem(y,u)
    if list(problem.free_indices) != [12,13,14]:
        raise ValueError("Original free-index protocol changed")
    start = np.asarray([float(-3), float(-6), float(3.871201010907891)],dtype=np.float64)
    if not np.array_equal(problem.initial_free,start):
        raise ValueError("Original configured free starts changed")
    for origin, record in traces.items():
        if not np.array_equal(np.asarray(record["iter_x"][0],np.float64),start):
            raise ValueError(f"{origin}: original anchor-0 start differs")
        if (record["source_input_sha256"] != digest((root / "inputs" / "binary_128_s64.json").read_bytes())
            or record["source_config_sha256"] != digest((root / "configs" / "hgf_binary_128.json").read_bytes())):
            raise ValueError(f"{origin}: original input/config provenance mismatch")
    return problem,traces


def execute(root: Path, archive: Path):
    problem,traces = prepare(root,archive)
    rows=[]
    for origin in ("hgfx","matlab"):
        old=traces[origin]
        for index in ANCHOR_INDEX:
            x=np.asarray(old["iter_x"][index],dtype=np.float64)
            stored=float(old["iter_val"][index])
            if x.shape != (3,) or not np.all(np.isfinite(x)) or not np.isfinite(stored):
                raise ValueError(f"Missing finite original anchor {origin} {index}")
            row={"anchor_origin":origin,"record_index_zero_based":index,
                 "free_parameters":clean(x),"archived_iter_val":stored,
                 "status":"NOT_EVALUATED"}
            try:
                val=float(problem.evaluate_free(x))
                grad,err=ridders_gradient(problem.evaluate_free,x,RiddersOptions(min_steps=10))
                row.update({"status":"EVALUATED","objective":val,
                            "ridders_gradient":clean(grad),"ridders_error":clean(err),
                            "archived_objective_abs_diff":abs(val-stored)})
            except Exception as exc:
                row.update({"status":"ERROR","error":f"{type(exc).__name__}: {exc}"})
            rows.append(row)
    return {
        "schema":"perf01d-subject7-hgfx-same-vector-gradient-v1",
        "status":"AUTHOR_SIDE_DIAGNOSTIC_UNTIMED_NO_FIT_NO_GATE_PASS",
        "frozen_hgfx_sha":HGFX_SHA,"frozen_matlab_sha":MATLAB_SHA,
        "original_trace_run":TRACE_RUN,"original_trace_sha":TRACE_SHA,
        "original_trace_raw_sha256":TRACE_HASHES,
        "source_run_id":"41863441006","subject_index_zero_based":7,
        "trials":128,"model":"hgf_binary","observation":"unitsq_sgm",
        "free_indices_zero_based":[12,13,14],"gradient_method":"frozen_Ridders_min_steps_10",
        "anchor_indices_zero_based":list(ANCHOR_INDEX),
        "cases":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=execute(a.input,a.archive)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(encode(result))
    print(json.dumps({"statuses":[[r["anchor_origin"],r["record_index_zero_based"],
                                    r["status"]] for r in result["cases"]]},sort_keys=True))
    if any(x["status"]!="EVALUATED" for x in result["cases"]):
        raise SystemExit("A frozen HGFX gradient probe failed; raw evidence retained")


if __name__=="__main__":
    main()
