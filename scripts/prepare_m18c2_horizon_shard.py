#!/usr/bin/env python3
"""Prepare one immutable M18C.2 paired trial-horizon recovery shard."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from hgfx.diagnostics.horizon import (
    MODEL_REPLICATES,
    PARAM_REPLICATES,
    PROTOCOL,
    TRIAL_HORIZONS,
    TRUTH_SCALES,
)
from hgfx.diagnostics.recovery import (
    BINARY_VARIANTS,
    _truth_vector,
    deterministic_binary_inputs,
    simulate_binary_variant,
)

REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"
PHI = 1.61803398875


def _canonical_hash(payload: dict) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _parameter_seed(trials: int, scale: float, replicate: int) -> int:
    return int(18018 + round(10_000 * scale) + 100 * trials + replicate)


def _model_seed(model_index: int, trials: int, scale: float, replicate: int) -> int:
    return int(
        18018
        + 500_000
        + round(10_000 * scale)
        + 1_000_000 * model_index
        + 100 * trials
        + replicate
    )


def _case_payload(
    *, kind: str, model: str, trials: int, scale: float, replicate: int, seed: int
) -> dict:
    inputs = deterministic_binary_inputs(trials, seed)
    truth_full, truth_free, free_indices = _truth_vector(
        model, inputs, replicate=replicate, scale=scale
    )
    responses, probabilities = simulate_binary_variant(
        model, inputs, truth_full, seed=seed + 1
    )
    case = {
        "kind": kind,
        "model": model,
        "trial_count": trials,
        "truth_scale": scale,
        "replicate": replicate,
        "seed": seed,
        "simulation_seed": seed + 1,
        "u": np.asarray(inputs, dtype=np.float64).reshape(-1).tolist(),
        "y": np.asarray(responses, dtype=np.float64).reshape(-1).tolist(),
        "response_probabilities": np.asarray(probabilities, dtype=np.float64).reshape(-1).tolist(),
        "truth_free": np.asarray(truth_free, dtype=np.float64).reshape(-1).tolist(),
        "free_indices_zero_based": [int(i) for i in free_indices],
    }
    case["case_sha256"] = _canonical_hash(case)
    return case


def build_shard(model: str, trials: int, scale: float) -> dict:
    """Build one deterministic M18C.2 model × horizon × truth-scale shard."""
    if model not in BINARY_VARIANTS:
        raise ValueError(f"unknown model {model!r}")
    if trials not in TRIAL_HORIZONS:
        raise ValueError(f"trial count must be one of {TRIAL_HORIZONS}")
    if scale not in TRUTH_SCALES:
        raise ValueError(f"truth scale must be one of {TRUTH_SCALES}")

    model_index = BINARY_VARIANTS.index(model)
    parameter_cases = []
    for replicate in range(PARAM_REPLICATES):
        seed = _parameter_seed(trials, scale, replicate)
        case = _case_payload(
            kind="parameter_recovery",
            model=model,
            trials=trials,
            scale=scale,
            replicate=replicate,
            seed=seed,
        )
        case["case_id"] = f"M18C2-PR-{model}-T{trials}-S{scale:.2f}-R{replicate}"
        parameter_cases.append(case)

    model_cases = []
    for replicate in range(MODEL_REPLICATES):
        seed = _model_seed(model_index, trials, scale, replicate)
        case = _case_payload(
            kind="model_recovery",
            model=model,
            trials=trials,
            scale=scale,
            replicate=replicate,
            seed=seed,
        )
        case["generating_model"] = model
        case["candidate_models"] = list(BINARY_VARIANTS)
        case["case_id"] = f"M18C2-MR-{model}-T{trials}-S{scale:.2f}-R{replicate}"
        model_cases.append(case)

    shard = {
        "protocol": PROTOCOL,
        "reference_commit": REFERENCE_COMMIT,
        "generator": {
            "historical_seed_scheme": True,
            "truth_phase_constant": PHI,
            "response_generator": "hgfx validated simulation; exported y is immutable paired data",
            "relationship_to_s7": "same generator semantics; trial horizon extended only",
        },
        "shard": {"model": model, "trial_count": trials, "truth_scale": scale},
        "parameter_cases": parameter_cases,
        "model_cases": model_cases,
    }
    shard["shard_sha256"] = _canonical_hash(shard)
    return shard


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=BINARY_VARIANTS, required=True)
    parser.add_argument("--trials", type=int, choices=TRIAL_HORIZONS, required=True)
    parser.add_argument("--scale", type=float, choices=TRUTH_SCALES, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = build_shard(args.model, args.trials, args.scale)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "protocol": PROTOCOL,
                "output": str(output),
                "shard": payload["shard"],
                "parameter_cases": len(payload["parameter_cases"]),
                "model_cases": len(payload["model_cases"]),
                "shard_sha256": payload["shard_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
