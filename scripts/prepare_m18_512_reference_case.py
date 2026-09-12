#!/usr/bin/env python3
"""Freeze the first historical M18B 512-trial cell for MATLAB/HGFX comparison."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from hgfx.compat.configs import unitsq_sgm_config
from hgfx.diagnostics.identifiability_validation import informative_binary_inputs
from hgfx.diagnostics.recovery import _truth_vector, _variant_components, simulate_binary_variant

BASE_SEED = 181900
MODEL = "hgf_binary"
MODEL_INDEX = 0
TRIAL_COUNT = 512
REPLICATE = 0
TRUTH_SCALE = 0.35
SEED = BASE_SEED + MODEL_INDEX * 1_000_000 + TRIAL_COUNT * 100 + REPLICATE
RESPONSE_SEED = SEED + 1
REFERENCE_COMMIT = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def _json_value(value):
    if isinstance(value, np.ndarray):
        return _json_value(value.tolist())
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _json_value(v) for k, v in value.items()}
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def _git_head(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="reference/generated/m18_512_reference_case_input.json",
    )
    args = parser.parse_args()

    inputs = informative_binary_inputs(TRIAL_COUNT, SEED)
    truth_full, truth_free, free_indices = _truth_vector(
        MODEL, inputs, replicate=REPLICATE, scale=TRUTH_SCALE
    )
    config_factory, _ = _variant_components(MODEL)
    prc = config_factory().resolve_placeholders(inputs)
    obs = unitsq_sgm_config()
    n_prc = len(prc.parameters)
    initial_full = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)

    # Freeze responses in Python so MATLAB and HGFX fit exactly the same dataset;
    # cross-language RNG identity is intentionally not assumed.
    responses, probabilities = simulate_binary_variant(
        MODEL, inputs, truth_full, seed=RESPONSE_SEED
    )

    root = Path(__file__).resolve().parents[1]
    payload = {
        "schema_version": 1,
        "purpose": "M18 512-trial frozen MATLAB-reference classification",
        "reference": {
            "toolbox": "HGF Toolbox",
            "version": "8.2.0",
            "commit": REFERENCE_COMMIT,
        },
        "hgfx_commit": _git_head(root),
        "historical_cell": {
            "base_seed": BASE_SEED,
            "model": MODEL,
            "model_index": MODEL_INDEX,
            "trial_count": TRIAL_COUNT,
            "replicate": REPLICATE,
            "truth_scale": TRUTH_SCALE,
            "seed": SEED,
            "response_seed": RESPONSE_SEED,
            "seed_formula": "base_seed + model_index*1000000 + trial_count*100 + replicate",
        },
        "inputs": inputs,
        "responses": responses,
        "response_probabilities": probabilities,
        "truth_full_transformed": truth_full,
        "truth_free_transformed": truth_free,
        "free_zero_based_indices": list(free_indices),
        "n_perceptual_parameters": n_prc,
        "truth_perceptual_transformed": truth_full[:n_prc],
        "truth_observation_transformed": truth_full[n_prc:],
        "default_full_transformed": initial_full,
        "default_perceptual_transformed": initial_full[:n_prc],
        "default_observation_transformed": initial_full[n_prc:],
        "stimulus_design": "balanced_bounded_run_v1",
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(_json_value(payload), indent=2, sort_keys=True, allow_nan=False),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(output), "seed": SEED, "trials": TRIAL_COUNT}, indent=2))


if __name__ == "__main__":
    main()
