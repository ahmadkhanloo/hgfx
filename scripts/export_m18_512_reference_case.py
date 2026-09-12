#!/usr/bin/env python3
"""Freeze the M18B 512-trial HGF case for MATLAB reference comparison.

This script does not classify the failure. It exports the deterministic HGFX
case so MATLAB and Python can be run against identical inputs/configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from hgfx import enable_x64
from hgfx.compat.configs import unitsq_sgm_config
from hgfx.diagnostics.identifiability_validation import informative_binary_inputs
from hgfx.diagnostics.recovery import _truth_vector, _variant_components, simulate_binary_variant


def _jsonable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reference/generated/m18_512_hgf")
    parser.add_argument("--base-seed", type=int, default=181900)
    parser.add_argument("--replicate", type=int, default=0)
    parser.add_argument("--truth-scale", type=float, default=0.35)
    args = parser.parse_args()

    enable_x64()
    model = "hgf_binary"
    trial_count = 512
    # Same identity formula used by run_m18b_identifiability_validation.py.
    seed = args.base_seed + trial_count * 100 + args.replicate
    inputs = informative_binary_inputs(trial_count, seed)
    truth_full, truth_free, free_indices = _truth_vector(
        model, inputs, replicate=args.replicate, scale=args.truth_scale
    )
    responses, response_probabilities = simulate_binary_variant(
        model, inputs, truth_full, seed=seed + 100_000
    )

    config_factory, _ = _variant_components(model)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    n_prc = len(prc.parameters)

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    payloads = {
        "metadata.json": {
            "schema_version": 1,
            "purpose": "M18 issue #25 frozen 512-trial MATLAB comparison case",
            "model": model,
            "observation_model": "unitsq_sgm",
            "trial_count": trial_count,
            "base_seed": args.base_seed,
            "dataset_seed": seed,
            "simulation_seed": seed + 100_000,
            "replicate": args.replicate,
            "truth_scale": args.truth_scale,
            "classification": "INSUFFICIENT_REFERENCE_EVIDENCE",
        },
        "input.json": {"u": inputs},
        "responses.json": {
            "y": responses,
            "response_probabilities": response_probabilities,
        },
        "parameters.json": {
            "transformed_full": truth_full,
            "transformed_free": truth_free,
            "free_indices_zero_based": free_indices,
            "perceptual_transformed": truth_full[:n_prc],
            "observation_transformed": truth_full[n_prc:],
            "perceptual_native": prc.transformed_to_native(truth_full[:n_prc]),
            "observation_native": obs.transformed_to_native(truth_full[n_prc:]),
        },
    }
    for name, payload in payloads.items():
        text = json.dumps(_jsonable(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"
        (out / name).write_text(text, encoding="utf-8")

    manifest = {}
    for path in sorted(out.glob("*.json")):
        manifest[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / "sha256.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output_dir": str(out), "dataset_seed": seed, "files": manifest}, indent=2))


if __name__ == "__main__":
    main()
