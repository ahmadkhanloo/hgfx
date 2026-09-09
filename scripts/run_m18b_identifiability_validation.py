#!/usr/bin/env python3
"""Run M18B identifiability-aware recovery validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hgfx.diagnostics.identifiability_validation import (
    evaluate_m18b_gate,
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
        "trial_counts": (128, 256, 512),
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

    cfg = PRESETS[args.preset]
    options = QuasiNewtonOptions(max_iter=cfg["max_iter"])
    records = []

    for model_index, model in enumerate(BINARY_VARIANTS):
        for trial_count in cfg["trial_counts"]:
            for replicate in range(cfg["replicates"]):
                seed = args.seed + model_index * 1_000_000 + int(trial_count) * 100 + replicate
                diagnosis = diagnose_parameter_recovery_dataset(
                    model=model,
                    trial_count=int(trial_count),
                    replicate=replicate,
                    seed=seed,
                    truth_scale=cfg["truth_scale"],
                    options=options,
                    profile_points=cfg["profile_points"],
                )
                records.extend(records_from_diagnosis(diagnosis))

    summary = summarize_records(records)
    payload = {
        "schema_version": 1,
        "milestone": "M18B",
        "preset": args.preset,
        "purpose": "identifiability-aware recovery validation without modifying frozen M18 thresholds or result",
        "protocol": cfg,
        "records": records_payload(records),
        "summary": summary,
        "trial_count_trends": trial_count_trends(summary),
    }
    payload["gate"] = evaluate_m18b_gate(
        records=records,
        summary=summary,
        trial_counts=cfg["trial_counts"],
        replicates=cfg["replicates"],
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "preset": args.preset,
        "gate_pass": payload["gate"]["pass"],
        "groups": len(summary),
    }, indent=2))
    if args.preset == "gate" and not payload["gate"]["pass"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
