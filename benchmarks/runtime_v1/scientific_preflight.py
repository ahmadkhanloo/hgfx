#!/usr/bin/env python3
"""PERF-01 scientific *preflight* on HGFX only: no timing or MATLAB parity claim."""
from __future__ import annotations

import argparse
from importlib import metadata
import json
import math
from pathlib import Path
import traceback

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.simulation import ehgf_binary_config, uhgf_binary_config
from hgfx.compat.objective import evaluate_objective
from hgfx.models import hgf_binary, ehgf_binary, uhgf_binary
from hgfx.responses.unitsq_sigmoid import unitsq_sgm

from generate_inputs import digest, encode

FORWARD = {
    "hgf_binary": hgf_binary,
    "ehgf_binary": ehgf_binary,
    "uhgf_binary": uhgf_binary,
}
CONFIG = {
    "hgf_binary": hgf_binary_config,
    "ehgf_binary": ehgf_binary_config,
    "uhgf_binary": uhgf_binary_config,
}


def decode_number(value: dict) -> float:
    if "hex" in value:
        f = float.fromhex(value["hex"])
        if f.hex() != value["hex"] or repr(f) != value["decimal"]:
            raise ValueError("Inconsistent float64 encoding")
        return f
    if value.get("special") == "NaN":
        return float("nan")
    if value.get("special") == "Infinity":
        return float("inf")
    if value.get("special") == "-Infinity":
        return float("-inf")
    raise ValueError(f"Unknown numeric representation: {value}")


def verify(root: Path):
    if metadata.version("hgfx") != "1.0.0":
        raise RuntimeError("Preflight requires isolated hgfx==1.0.0")
    inp = root / "inputs_manifest.json"
    cfg = root / "resolved_configs_manifest.json"
    registry = json.loads(inp.read_bytes())
    config = json.loads(cfg.read_bytes())
    if config["input_manifest_sha256"] != digest(inp.read_bytes()):
        raise ValueError("Input manifest changed after config export")
    if len(registry["cases"]) != 28 or len(config["entries"]) != 9:
        raise ValueError("Incomplete preregistered matrix")
    for item in registry["cases"]:
        actual = digest((root / item["source_file"]).read_bytes())
        if actual != item["source_sha256"]:
            raise ValueError(f"Tampered source input: {item['id']}")
    for item in config["entries"]:
        if digest((root / item["config_file"]).read_bytes()) != item["config_sha256"]:
            raise ValueError(f"Tampered configuration: {item['config_file']}")
    return registry, config


def smoke_one(root: Path, case: dict) -> dict:
    """Validate HGFX-only fixed-vector forward/objective, never a speed test."""
    model = case["model"]
    n = case["n_trials"]
    src = json.loads((root / case["source_file"]).read_bytes())
    u = np.asarray(src["u"][0], dtype=np.float64)
    y = np.asarray(src["y"][0], dtype=np.float64)
    if n != len(u):
        raise ValueError("Input horizon mismatch")
    if case["tier"] == "robustness":
        mask = case["mask_indices_zero_based"]
        u[mask["ignored_input_and_response"]] = np.nan
        y[mask["ignored_input_and_response"]] = np.nan
        y[mask["irregular_response_only"]] = np.nan
    snap = json.loads((root / f"configs/{model}_{n}.json").read_bytes())
    config = CONFIG[model]().resolve_placeholders(u)
    obs_config = unitsq_sgm_config()
    theta = np.asarray(
        [decode_number(v) for v in snap["transformed_start_full"]],
        dtype=np.float64,
    )
    n_prc = len(config.parameters)
    p_prc, p_obs = theta[:n_prc], theta[n_prc:]
    if len(theta) != n_prc + len(obs_config.parameters):
        raise ValueError("Start vector length mismatch")
    if not np.array_equal(p_prc, config.priormus, equal_nan=True):
        raise ValueError("Prior/start mismatch (input-derived placeholders)")
    if not np.array_equal(p_obs, obs_config.priormus, equal_nan=True):
        raise ValueError("Observation prior/start mismatch")
    if case["stage"] == "forward":
        ignored = tuple(int(x) for x in np.flatnonzero(np.isnan(u)))
        traj, infstates = FORWARD[model](
            u, p_prc, transformed=True, ignored_trials=ignored,
        )
        if np.asarray(infstates).shape[0] != n:
            raise ValueError("Unexpected trajectory horizon")
        return {
            "status": "HGFX_ONLY_FORWARD_COMPLETED_MATLAB_UNVERIFIED",
            "trajectory_keys": sorted(traj),
            "inf_states_shape": list(np.asarray(infstates).shape),
        }
    result = evaluate_objective(
        responses=y,
        inputs=u,
        perceptual_parameters=p_prc,
        observation_parameters=p_obs,
        perceptual_config=config,
        observation_config=obs_config,
        perceptual_function=FORWARD[model],
        observation_function=unitsq_sgm,
    )
    if result.rval != 0 or not math.isfinite(result.neg_log_joint):
        raise ValueError(
            f"Invalid objective status={result.rval}, value={result.neg_log_joint}"
        )
    if len(result.trial_log_likelihoods) != n:
        raise ValueError("Trial likelihood length mismatch")
    if len(result.regular_trial_log_likelihoods) != n - int(np.isnan(u).sum()) - int(np.isnan(y).sum() - np.isnan(u).sum()):
        raise ValueError("Mask selection mismatch")
    return {
        "status": "HGFX_ONLY_OBJECTIVE_COMPLETED_MATLAB_UNVERIFIED",
        "neg_log_joint": result.neg_log_joint,
        "neg_log_likelihood": result.neg_log_likelihood,
        "regular_trial_count": len(result.regular_trial_log_likelihoods),
    }


def produce(root: Path) -> dict:
    registry, configs = verify(root)
    rows = []
    for case in registry["cases"]:
        row = {
            "case_id": case["id"],
            "tier": case["tier"],
            "model": case["model"],
            "stage": case["stage"],
            "n_trials": case["n_trials"],
            "input_sha256": case["source_sha256"],
        }
        if case["tier"] == "throughput" or case["stage"] == "fit_compat_full":
            row["status"] = "NOT_RUN_AWAITING_FULL_WORKFLOW_AND_MATLAB_GATE"
        else:
            try:
                row.update(smoke_one(root, case))
            except Exception as exc:
                row["status"] = "HGFX_ONLY_ERROR"
                row["error"] = f"{type(exc).__name__}: {exc}"
                row["traceback"] = traceback.format_exc(limit=4)
        rows.append(row)
    return {
        "schema": "hgfx-runtime-preflight-v1",
        "status": "DIAGNOSTIC_ONLY_MATLAB_UNVERIFIED_NO_TIMING",
        "protocol_id": "hgfx-matlab-runtime-1",
        "hgfx_installed": metadata.version("hgfx"),
        "numpy": np.__version__,
        "inputs_manifest_sha256": digest((root / "inputs_manifest.json").read_bytes()),
        "configs_manifest_sha256": digest((root / "resolved_configs_manifest.json").read_bytes()),
        "counts": {status: sum(item["status"] == status for item in rows) for status in sorted(set(item["status"] for item in rows))},
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = produce(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encode(result))
    print(json.dumps(result["counts"], sort_keys=True))
    # Keep all cell rows, even on failure. For this preflight, return an error
    # when any HGFX-only smoke cell cannot be evaluated.
    if result["counts"].get("HGFX_ONLY_ERROR", 0):
        raise SystemExit("HGFX-only scientific preflight has failures; full record retained")


if __name__ == "__main__":
    main()
