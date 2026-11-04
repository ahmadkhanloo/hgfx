#!/usr/bin/env python3
"""PERF-01D full fitModel output audit for all 64 unchanged 128-trial subjects.

NO performance timing, NO changed starts, NO retried/omitted subjects.
Frozen HGFX 1.0.0 code runs from an independently verified checkout.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np
from hgfx import fit_model

from generate_inputs import digest, encode
from scientific_preflight import decode_number, verify
from trialwise_hgfx_export import clean

FIT_FIELDS = (
    "init", "final", "H", "Sigma", "Corr", "trialLogLlsplit",
    "negLl", "negLj", "LME", "decompLME", "AIC", "BIC",
    "yhat", "res", "resAC",
)
SUBJECTS = 64
TRIALS = 128


def run(root: Path) -> dict:
    if metadata.version("hgfx") != "1.0.0":
        raise ValueError("Full-cohort fit requires hgfx==1.0.0")
    verify(root)
    data_file = root / "inputs" / "binary_128_s64.json"
    cfg_file = root / "configs" / "hgf_binary_128.json"
    source = json.loads(data_file.read_bytes())
    snap = json.loads(cfg_file.read_bytes())
    start = np.array(
        [decode_number(v) for v in snap["transformed_start_full"]],
        dtype=np.float64,
    )
    if len(source["u"]) != SUBJECTS or len(source["y"]) != SUBJECTS:
        raise ValueError("Unexpected canonical cohort size")
    rows = []
    for index in range(SUBJECTS):
        u = np.array(source["u"][index], dtype=np.float64)
        y = np.array(source["y"][index], dtype=np.float64)
        if u.shape != (TRIALS,) or y.shape != (TRIALS,):
            raise ValueError(f"Malformed subject {index}")
        record = {
            "model": "hgf_binary",
            "n_trials": TRIALS,
            "subject_index_zero_based": index,
            "status": "NOT_RUN",
            "start_matches_frozen_snapshot": False,
            "n_rand_init": None,
            "optimizer_iteration_count": None,
            "optim": None,
            "traj": None,
        }
        try:
            fit = fit_model(
                y, u, "hgf_binary_config", "unitsq_sgm_config",
                "quasinewton_optim_config",
            )
            result = fit.optim
            record["n_rand_init"] = int(fit.c_opt.nRandInit)
            record["start_matches_frozen_snapshot"] = bool(
                np.array_equal(np.asarray(result["init"]), start, equal_nan=True)
            )
            if record["n_rand_init"] or not record["start_matches_frozen_snapshot"]:
                record["status"] = "HGFX_UNEXPECTED_RESTART_OR_START"
            else:
                record["status"] = "HGFX_FULL_FIT_COMPLETED_NO_PARITY_DECISION"
            record["optim"] = {
                name: clean(
                    result[name].to_dict()
                    if hasattr(result[name], "to_dict") else result[name]
                )
                for name in FIT_FIELDS
            }
            record["traj"] = {
                name: clean(value) for name, value in fit.traj.items()
            }
            history = result.get("iter", [])
            if hasattr(history, "get"):
                values = np.asarray(history.get("val", []), dtype=np.float64)
                record["optimizer_iteration_count"] = int(values.size)
            else:
                record["optimizer_iteration_count"] = 0
        except Exception as exc:
            record["status"] = "HGFX_FULL_FIT_ERROR"
            record["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(record)
    assert len(rows) == SUBJECTS
    return {
        "schema": "perf01-hgfx-full-cohort-fit-v1",
        "status": "UNFROZEN_DIAGNOSTIC_ONLY_NO_TIMING",
        "hgfx_distribution": metadata.version("hgfx"),
        "release_expected_sha": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "model": "hgf_binary",
        "observation_model": "unitsq_sgm",
        "trials": TRIALS,
        "subjects": SUBJECTS,
        "input_sha256": digest(data_file.read_bytes()),
        "config_sha256": digest(cfg_file.read_bytes()),
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encode(result))
    from collections import Counter
    print(json.dumps({
        "subject_count": len(result["cases"]),
        "status": dict(Counter(x["status"] for x in result["cases"])),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
