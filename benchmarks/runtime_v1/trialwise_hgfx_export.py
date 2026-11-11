#!/usr/bin/env python3
"""PERF-01-D raw trialwise HGFX output at frozen inputs, no timing."""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np
from hgfx.compat.configs import unitsq_sgm_config
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

from scientific_preflight import CONFIG, FORWARD, decode_number, verify
from generate_inputs import digest, encode

MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
HORIZONS = (128, 512, 1024)


def clean(value):
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        f = float(value)
        if np.isnan(f):
            return None
        if np.isposinf(f):
            return "Infinity"
        if np.isneginf(f):
            return "-Infinity"
        return f
    return value


def prefix_probe(model, u, p):
    """Sequential prefix checks: MATLAB validator uses horizon-dependent RMS.

    A prefix that fails can recover for longer horizons, so no bisection.
    This scans every prefix from trial 2 upward, halting on first invalid.
    """
    check = FORWARD[model]
    for trial_count in range(2, len(u) + 1):
        z = u[:trial_count]
        ignored = np.flatnonzero(np.isnan(z)).tolist()
        try:
            check(z, p, transformed=True, ignored_trials=ignored)
        except Exception as exc:
            return {
                "first_invalid_prefix_length": trial_count,
                "last_valid_prefix_length": trial_count - 1,
                "error": f"{type(exc).__name__}: {exc}",
                "scan_policy": "sequential_all_prefixes_from_2",
            }
    return {"first_invalid_prefix_length": None, "last_valid_prefix_length": len(u)}


def run_cell(root: Path, model: str, n: int, *, masked: bool = False):
    data_path = root / "inputs" / f"binary_{n}_s64.json"
    data = json.loads(data_path.read_bytes())
    u = np.asarray(data["u"][0], dtype=np.float64)
    y = np.asarray(data["y"][0], dtype=np.float64)
    if masked:
        u[[31, 127]] = np.nan
        y[[31, 127, 63, 255]] = np.nan
    snap_path = root / "configs" / f"{model}_{n}.json"
    snap = json.loads(snap_path.read_bytes())
    full = np.asarray([decode_number(x) for x in snap["transformed_start_full"]], np.float64)
    prc = CONFIG[model]().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    n_prc = len(prc.parameters)
    p_prc = full[:n_prc]
    p_obs = full[n_prc:]
    row = {
        "id": "robustness_masked_512" if masked else f"{model}_{n}",
        "model": model, "trials": n, "masked": masked,
        "source_sha256": digest(data_path.read_bytes()),
        "config_sha256": digest(snap_path.read_bytes()),
        "start_matches_resolved_prior": bool(
            np.array_equal(p_prc, prc.priormus, equal_nan=True)
            and np.array_equal(p_obs, obs.priormus, equal_nan=True)
        ),
        "ignored_trial_ids_one_based": (np.flatnonzero(np.isnan(u)) + 1).tolist(),
        "irregular_trial_ids_one_based": (
            np.flatnonzero(np.isnan(u) | np.isnan(y)) + 1
        ).tolist(),
        "status": "NOT_RUN",
    }
    if not row["start_matches_resolved_prior"]:
        row["status"] = "START_MISMATCH"
        return row
    try:
        traj, inf_states = FORWARD[model](
            u, p_prc, transformed=True,
            ignored_trials=np.flatnonzero(np.isnan(u)).tolist(),
        )
        trial_ll, yhat, residual = unitsq_sgm(
            y, inf_states, p_obs,
            irregular_trials=np.flatnonzero(np.isnan(u) | np.isnan(y)).tolist(),
            predorpost=int(obs.options.get("predorpost", 1)),
        )
        assert np.asarray(inf_states).shape == (n, 3, 4)
        assert len(trial_ll) == n
        row.update({
            "status": "HGFX_COMPLETED_REFERENCE_UNVERIFIED",
            "inf_states": clean(inf_states),
            "traj": clean(traj),
            "trial_log_likelihoods": clean(trial_ll),
            "yhat": clean(yhat),
            "residuals": clean(residual),
        })
    except Exception as exc:
        row["status"] = "HGFX_ERROR"
        row["error"] = f"{type(exc).__name__}: {exc}"
        if model == "hgf_binary":
            row["prefix_diagnostic"] = prefix_probe(model, u, p_prc)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify(args.input)
    if metadata.version("hgfx") != "1.0.0":
        raise RuntimeError("Not hgfx==1.0.0")
    rows = [run_cell(args.input, model, n) for n in HORIZONS for model in MODELS]
    rows.append(run_cell(args.input, "hgf_binary", 512, masked=True))
    out = {
        "schema": "hgfx-perf01-trialwise-hgfx-v1",
        "protocol": "hgfx-matlab-runtime-1",
        "source": "hgfx==1.0.0 @ 4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "input_manifest_sha256": digest((args.input / "inputs_manifest.json").read_bytes()),
        "config_manifest_sha256": digest((args.input / "resolved_configs_manifest.json").read_bytes()),
        "status": "EXPLORATORY_UNFROZEN_NO_PERFORMANCE",
        "cells": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encode(out))
    print(json.dumps({
        "total": len(rows),
        "completed": sum(x["status"] == "HGFX_COMPLETED_REFERENCE_UNVERIFIED" for x in rows),
        "errors": sum(x["status"] == "HGFX_ERROR" for x in rows),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
