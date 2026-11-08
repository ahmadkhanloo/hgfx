#!/usr/bin/env python3
"""PERF-01C: explicitly separated untimed forward-call boundary on original cases.

Research diagnostic only. This module does not create a timed benchmark or clear
the independent-review, hardware, or scientific eligibility gates.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path

import numpy as np

from generate_inputs import digest, encode
from scientific_preflight import CONFIG, FORWARD, decode_number, verify
from trialwise_hgfx_export import clean

EXPECTED = (
    ("primary_forward_128", "hgf_binary", 128),
    ("secondary_ehgf_binary_forward_128", "ehgf_binary", 128),
    ("secondary_ehgf_binary_forward_512", "ehgf_binary", 512),
    ("secondary_ehgf_binary_forward_1024", "ehgf_binary", 1024),
    ("secondary_uhgf_binary_forward_128", "uhgf_binary", 128),
    ("secondary_uhgf_binary_forward_512", "uhgf_binary", 512),
    ("secondary_uhgf_binary_forward_1024", "uhgf_binary", 1024),
)
TRAJ = ("mu", "sa", "muhat", "sahat", "v", "w", "da", "ud", "psi", "epsi", "wt")
SOURCE = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"


def forward_only_call(model: str, inputs: np.ndarray, parameters: np.ndarray):
    """Proposed CPU computation region ONLY: return all complete forward outputs.

    The caller must prepare inputs before, inspect and serialize results after.
    This function deliberately does not import or use clocks, timing, JIT or
    benchmarking. Unapproved candidate, not a prospective timed protocol.
    """
    return FORWARD[model](
        inputs, parameters, transformed=True, ignored_trials=()
    )


def produce(root: Path) -> dict:
    registry, _ = verify(root)  # Original 28 inputs and nine configs are hashed.
    if metadata.version("hgfx") != "1.0.0":
        raise RuntimeError("Must run frozen HGFX 1.0.0, not current main")
    indexed = {c["id"]: c for c in registry["cases"]}
    if len(indexed) != 28:
        raise ValueError("Duplicate or missing original case IDs")
    rows = []
    for case_id, model, n in EXPECTED:
        case = indexed[case_id]
        if (case["model"], case["n_trials"], case["stage"], case["tier"]) != (
            model, n, "forward", "primary" if model == "hgf_binary" else "secondary"
        ):
            raise ValueError("Original forward case contract changed: " + case_id)
        source = root / case["source_file"]
        snap = root / "configs" / f"{model}_{n}.json"
        data = json.loads(source.read_bytes())
        cfg = json.loads(snap.read_bytes())
        u = np.asarray(data["u"][0], dtype=np.float64)
        if len(u) != n or not np.isfinite(u).all():
            raise ValueError("Nonfinite or wrong-horizon unmasked input: " + case_id)
        full = np.asarray([decode_number(v) for v in cfg["transformed_start_full"]],
                          dtype=np.float64)
        prc = CONFIG[model]().resolve_placeholders(u)
        p = full[:len(prc.parameters)]
        if not np.array_equal(p, prc.priormus, equal_nan=True):
            raise ValueError("Original perceptual start mismatch: " + case_id)
        # Only the perceptual model is executed; no observation likelihood,
        # objective, fitting, seed resampling, time measurement or I/O in it.
        traj, states = forward_only_call(model, u, p)
        if np.asarray(states).shape != (n, 3, 4):
            raise ValueError("Invalid complete inference-state shape: " + case_id)
        if set(traj) != set(TRAJ):
            raise ValueError("Incomplete original forward trajectory: " + case_id)
        for field in TRAJ:
            if np.asarray(traj[field]).shape[0] != n:
                raise ValueError(f"Wrong trial axis for {case_id}.{field}")
        rows.append({
            "case_id": case_id, "model": model, "trials": n, "subject_index": 0,
            "source_sha256": digest(source.read_bytes()),
            "config_sha256": digest(snap.read_bytes()),
            "status": "HGFX_UNTIMED_FORWARD_COMPLETED_MATLAB_UNVERIFIED",
            "boundary_id": "PERCEPTUAL_FORWARD_FULL_OUTPUT_CALL_V1",
            "boundary_scope": "FORWARD_ONLY_NO_OBSERVATION_NO_OBJECTIVE_NO_FIT",
            "clock": "ABSENT",
            "inf_states": clean(states), "traj": clean(traj),
        })
    return {
        "schema": "perf01c-forward7-hgfx-boundary-untimed-v1",
        "candidate_boundary": "PERCEPTUAL_FORWARD_FULL_OUTPUT_CALL_V1",
        "input_preparation": "BEFORE_CALL_OUTSIDE_CANDIDATE_REGION",
        "output_shape_validation_and_serialization": "AFTER_CALL_OUTSIDE_CANDIDATE_REGION",
        "clock": "ABSENT",
        "status": "DIAGNOSTIC_ONLY_NOT_BENCHMARK_NOT_SCIENTIFIC_PASS",
        "hgfx_sha": SOURCE,
        "original_case_denominator": 28,
        "forward_case_count": len(rows),
        "cells": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = produce(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encode(result))
    print("HGFX 7 proposed forward-call boundary outputs (UNTIMED / NOT FROZEN)")


if __name__ == "__main__":
    main()
