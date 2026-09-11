#!/usr/bin/env python3
"""M18C.2 Trial Horizon Analysis.

Runs the frozen M18 recovery protocol over increasing trial horizons to
separate data-limited from structural identifiability failures.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hgfx.diagnostics.recovery import (
    BINARY_VARIANTS,
    run_parameter_recovery,
    summarize_parameter_recovery,
)
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


TRIAL_HORIZONS = (128, 256, 512, 1024)


def summarize(records):
    result = summarize_parameter_recovery(records)
    return {
        "n": result.n,
        "convergence_rate": float(result.convergence_rate),
        "rmse": result.rmse.tolist(),
        "bias": result.bias.tolist(),
        "correlation": result.correlation.tolist(),
        "median_absolute_error": result.median_absolute_error.tolist(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="benchmarks/results/m18c_horizon_analysis.json")
    parser.add_argument("--seed", type=int, default=18018)
    parser.add_argument("--replicates", type=int, default=6)
    args = parser.parse_args()

    options = QuasiNewtonOptions(max_iter=100)
    payload = {
        "milestone": "M18C.2",
        "trial_horizons": list(TRIAL_HORIZONS),
        "models": list(BINARY_VARIANTS),
        "results": {},
    }

    for model in BINARY_VARIANTS:
        payload["results"][model] = {}
        for trials in TRIAL_HORIZONS:
            records = run_parameter_recovery(
                model=model,
                trial_counts=(trials,),
                replicates=args.replicates,
                seed=args.seed + trials,
                truth_scale=0.15,
                options=options,
            )
            payload["results"][model][str(trials)] = summarize(records)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "status": "complete"}, indent=2))


if __name__ == "__main__":
    main()
