#!/usr/bin/env python3
"""Fresh, untimed frozen HGFX v1.0.0 PUBLIC fit trace for original subject 7.

Does not replace the archived first 64 fits, alter starts or decide scientific PASS.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np

from generate_inputs import digest, encode
from scientific_preflight import verify
from trialwise_hgfx_export import clean
from hgfx import fit_model
from hgfx.compat.fitting import hgf_binary_unitsq_fit_problem
from hgfx.optim.ridders import RiddersOptions, ridders_gradient

SUBJECT = 7
HGFX_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
RUN_ID = "41863441006"


def run(root: Path, original: Path) -> dict:
    if metadata.version("hgfx") != "1.0.0":
        raise ValueError("Expected frozen HGFX 1.0.0, not current main")
    verify(root)
    summary = json.loads((original/f"summary-{RUN_ID}.json").read_bytes())
    if summary["hgfx_sha"] != HGFX_SHA or summary["matlab_sha"] != MATLAB_SHA:
        raise ValueError("Frozen source or archived fitted evidence mismatch")
    for name, expected in summary["raw_evidence_sha256"].items():
        if digest((original/name).read_bytes()) != expected:
            raise ValueError(f"Original raw source checksum mismatch: {name}")
    input_path = root/"inputs"/"binary_128_s64.json"
    config_path = root/"configs"/"hgf_binary_128.json"
    input_sha, config_sha = digest(input_path.read_bytes()), digest(config_path.read_bytes())
    if input_sha != summary["hgfx_input_sha256"] or config_sha != summary["hgfx_config_sha256"]:
        raise ValueError("Original archived input/config changed")
    source = json.loads(input_path.read_bytes())
    old = json.loads((original/"hgfx_raw.json").read_bytes())["cases"][SUBJECT]
    if old["subject_index_zero_based"] != SUBJECT or old["n_trials"] != 128:
        raise ValueError("Wrong original fit subject")
    if old["status"] != "HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION":
        raise ValueError("Original HGFX public fit did not complete")
    u = np.asarray(source["u"][SUBJECT], dtype=np.float64)
    y = np.asarray(source["y"][SUBJECT], dtype=np.float64)
    fit = fit_model(y, u, "hgf_binary_config", "unitsq_sgm_config",
                    "quasinewton_optim_config")
    opt = fit.optim
    history = opt.get("iter")
    if history is None or not hasattr(history, "get"):
        raise ValueError("Frozen public HGFX optimizer did not return iter history")
    x = np.asarray(history["x"], dtype=np.float64)
    val = np.asarray(history["val"], dtype=np.float64)
    finite = np.isfinite(val)
    if (x.shape != (101, 3) or val.shape != (101,) or
            np.flatnonzero(finite).tolist() != list(range(25))):
        raise ValueError("Unexpected original trace buffer or finite-slot inventory")
    inverse_hessians = history.get("invH", ())
    matrices = [np.asarray(item["T"], dtype=np.float64) for item in inverse_hessians]
    if len(matrices) != 25 or any(m.shape != (3, 3) for m in matrices):
        raise ValueError("Expected exactly 25 original populated 3x3 BFGS matrices")
    reset_indices = np.asarray(history.get("rst", ()), dtype=np.int64).reshape(-1)
    problem = hgf_binary_unitsq_fit_problem(y, u)
    if tuple(problem.free_indices) != (12, 13, 14):
        raise ValueError("Original free-coordinate scientific policy changed")
    gradients = []
    for i in range(25):
        g, uncertainty = ridders_gradient(
            problem.evaluate_free, x[i], RiddersOptions(min_steps=10)
        )
        gradients.append({
            "record_index_zero_based": i,
            "free_parameters": clean(x[i]),
            "objective_recomputed": float(problem.evaluate_free(x[i])),
            "grad": clean(g),
            "ridders_error": clean(uncertainty),
        })
    start_matches = bool(
        np.array_equal(np.asarray(opt["init"], dtype=np.float64),
                       np.asarray(old["optim"]["init"], dtype=np.float64), equal_nan=True)
        and int(fit.c_opt.nRandInit) == 0
    )
    return {
        "schema": "perf01-subject7-bfgs-state-hgfx-v1",
        "status": "UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED",
        "model": "hgf_binary",
        "trials": 128,
        "subject_index_zero_based": SUBJECT,
        "source_run_id": RUN_ID,
        "frozen_hgfx_sha": HGFX_SHA,
        "frozen_matlab_sha": MATLAB_SHA,
        "source_input_sha256": input_sha,
        "source_config_sha256": config_sha,
        "original_raw_fits_verified": True,
        "frozen_start_matches": start_matches,
        "n_rand_init": int(fit.c_opt.nRandInit),
        "fit_neg_lj": float(opt["negLj"]),
        "original_final_full": old["optim"]["final"],
        "final_full": clean(opt["final"]),
        "iter_x": clean(x),
        "iter_val": clean(val),
        "iter_inverse_hessian": clean(matrices),
        "iter_resets_one_based": clean(reset_indices),
        "ridders_recomputed_history": gradients,
        "ridders_min_steps": 10,
        "finite_slots": 25,
        "note": "Frozen public fit with all BFGS inverse-Hessian matrices and separately recomputed Ridders gradients; no performance timing or reference-limitation decision.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    record = run(a.input, a.original)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(encode(record))
    print(json.dumps({"status": record["status"], "x_rows": len(record["iter_x"]),
                      "val_rows": len(record["iter_val"])}, sort_keys=True))


if __name__ == "__main__":
    main()
