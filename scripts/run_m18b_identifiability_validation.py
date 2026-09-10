#!/usr/bin/env python3
"""Run M18B identifiability-aware recovery validation."""

from __future__ import annotations

import argparse
import json
import hashlib
import platform
import subprocess
from dataclasses import asdict

import jax
import numpy as np
from pathlib import Path

from hgfx import enable_x64
from hgfx.diagnostics.identifiability_validation import (
    evaluate_m18b_gate,
    informative_binary_inputs,
    records_from_diagnosis,
    records_payload,
    summarize_records,
    trial_count_trends,
)
from hgfx.diagnostics.parameter_recovery_diagnosis import diagnose_parameter_recovery_dataset
from hgfx.diagnostics.recovery import BINARY_VARIANTS
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

PRESETS = {
    "ci": {
        "trial_counts": (48, 64),
        "replicates": 1,
        "truth_scale": 0.35,
        "max_iter": 4,
        "profile_points": 7,
    },
    "gate": {
        "trial_counts": (64, 128, 256),
        "replicates": 3,
        "truth_scale": 0.35,
        "max_iter": 100,
        "profile_points": 31,
    },
}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=tuple(PRESETS), default="ci")
    parser.add_argument("--output", default="benchmarks/results/m18b_identifiability_validation.json")
    parser.add_argument("--seed", type=int, default=181900)
    args = parser.parse_args()

    enable_x64()
    cfg = PRESETS[args.preset]
    options = QuasiNewtonOptions(max_iter=cfg["max_iter"])
    records = []
    datasets = []
    failures = []
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    source_paths = (
        "scripts/run_m18b_identifiability_validation.py",
        "src/hgfx/diagnostics/identifiability_validation.py",
        "src/hgfx/diagnostics/parameter_recovery_diagnosis.py",
    )

    def git_value(*command):
        try:
            return subprocess.check_output(["git", *command], cwd=root, text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    environment = {
        "python": platform.python_version(), "numpy": np.__version__,
        "jax": jax.__version__, "jax_x64": bool(jax.config.jax_enable_x64),
        "devices": [str(d) for d in jax.devices()],
        "commit": git_value("rev-parse", "HEAD"),
        "working_tree_status": git_value("status", "--porcelain"),
        "source_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in source_paths},
    }
    if not environment["jax_x64"]:
        raise RuntimeError("M18B requires JAX float64")

    def json_value(value):
        # Boundary curvature is undefined; retain it explicitly as null.
        if isinstance(value, np.ndarray):
            return json_value(value.tolist())
        if isinstance(value, dict):
            return {k: json_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [json_value(v) for v in value]
        if isinstance(value, (float, np.floating)):
            return float(value) if np.isfinite(value) else None
        if isinstance(value, np.integer):
            return int(value)
        return value

    def checkpoint(complete=False):
        summary = summarize_records(records)
        gate = evaluate_m18b_gate(
            records=records, summary=summary,
            trial_counts=cfg["trial_counts"], replicates=cfg["replicates"],
        )
        gate["checks"]["execution_complete"] = complete and not failures
        gate["checks"]["final_gate_preset"] = args.preset == "gate"
        gate["pass"] = all(gate["checks"].values())
        payload = {
            "schema_version": 2, "milestone": "M18B", "preset": args.preset,
            "status": "completed" if complete else "incomplete",
            "purpose": "protocol integrity, not a claim of successful joint identifiability",
            "base_seed": args.seed, "protocol": cfg, "environment": environment,
            "stimulus_design": "balanced_bounded_run_v1",
            "frozen_m18": json.loads((root / "reference/validation/m18_provenance.json").read_text()),
            "records": records_payload(records), "datasets": datasets, "failures": failures,
            "summary": summary, "trial_count_trends": trial_count_trends(summary), "gate": gate,
        }
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(json_value(payload), indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
        temporary.replace(output)
        return payload

    checkpoint()
    for model_index, model in enumerate(BINARY_VARIANTS):
        for trial_count in cfg["trial_counts"]:
            for replicate in range(cfg["replicates"]):
                seed = args.seed + model_index * 1_000_000 + int(trial_count) * 100 + replicate
                identity = dict(model=model, trial_count=trial_count, replicate=replicate, seed=seed)
                print(json.dumps({"starting": identity}), flush=True)
                try:
                    inputs = informative_binary_inputs(int(trial_count), seed)
                    diagnosis = diagnose_parameter_recovery_dataset(
                        **identity, truth_scale=cfg["truth_scale"], options=options,
                        profile_points=cfg["profile_points"], inputs_override=inputs,
                    )
                    rows = records_from_diagnosis(diagnosis)
                    datasets.append({"inputs": inputs, "diagnosis": asdict(diagnosis)})
                    records.extend(rows)
                except Exception as exc:
                    # Preserve failed cells and continue the fixed grid without
                    # resampling, dropping cells, or silently reducing coverage.
                    failures.append({**identity, "error_type": type(exc).__name__, "message": str(exc)})
                checkpoint()

    payload = checkpoint(complete=True)
    print(json.dumps({"output": str(output), "preset": args.preset,
                      "gate_pass": payload["gate"]["pass"], "failures": len(failures)}, indent=2))
    if failures or (args.preset == "gate" and not payload["gate"]["pass"]):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
