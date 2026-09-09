#!/usr/bin/env python3
"""Reproducible single-node M17 1/2/4/8-GPU scaling benchmark."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import subprocess
import time
from pathlib import Path

import jax
import numpy as np

from hgfx.gpu import BFGSOptions, fit_hgf_binary_unitsq_multi_device


def parse_counts(raw: str) -> list[int]:
    counts = [int(value) for value in raw.split(",") if value.strip()]
    if not counts or any(value <= 0 for value in counts):
        raise argparse.ArgumentTypeError("gpu counts must be positive comma-separated integers")
    if counts != sorted(set(counts)):
        raise argparse.ArgumentTypeError("gpu counts must be unique and increasing")
    return counts


def make_dataset(n_subjects: int, n_trials: int, seed: int):
    rng = np.random.default_rng(seed)
    inputs = []
    responses = []
    for index in range(n_subjects):
        x = rng.integers(0, 2, size=n_trials, dtype=np.int8).astype(np.float64)
        noise = rng.random(n_trials) < (0.08 + 0.01 * (index % 5))
        y = np.where(noise, 1.0 - x, x).astype(np.float64)
        inputs.append(x)
        responses.append(y)
    return responses, inputs


def make_restarts(n_subjects: int, extra_restarts: int):
    if extra_restarts <= 0:
        return None
    base = np.array([-2.8, -5.7, math.log(42.0)], dtype=np.float64)
    offsets = np.linspace(-0.15, 0.15, extra_restarts, dtype=np.float64)
    starts = np.stack(
        [base + np.array([offset, -offset, 0.5 * offset]) for offset in offsets],
        axis=0,
    )
    return [starts.copy() for _ in range(n_subjects)]


def block_result(result) -> None:
    for shard in result.shard_results:
        for subject in shard.subjects:
            subject.objective_values.block_until_ready()


def run_once(responses, inputs, restarts, count: int, options: BFGSOptions) -> float:
    start = time.perf_counter()
    result = fit_hgf_binary_unitsq_multi_device(
        responses,
        inputs,
        device_indices=list(range(count)),
        restart_free_parameters=restarts,
        options=options,
        parallel=True,
    )
    block_result(result)
    return time.perf_counter() - start


def git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu-counts", type=parse_counts, default=parse_counts("1,2,4,8"))
    parser.add_argument("--subjects", type=int, default=64)
    parser.add_argument("--trials", type=int, default=128)
    parser.add_argument("--extra-restarts", type=int, default=1)
    parser.add_argument("--max-iter", type=int, default=40)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--output", type=Path, default=Path("gpu_validation_results/m17_scaling.json"))
    args = parser.parse_args()

    visible = tuple(jax.devices("gpu"))
    if not visible:
        raise SystemExit("No JAX GPU devices are visible")
    if max(args.gpu_counts) > len(visible):
        raise SystemExit(
            f"Requested up to {max(args.gpu_counts)} GPUs but only {len(visible)} are visible"
        )

    responses, inputs = make_dataset(args.subjects, args.trials, args.seed)
    restarts = make_restarts(args.subjects, args.extra_restarts)
    options = BFGSOptions(max_iter=args.max_iter)
    total_fits = args.subjects * (1 + args.extra_restarts)

    rows = []
    baseline = None
    for count in args.gpu_counts:
        for _ in range(args.warmups):
            run_once(responses, inputs, restarts, count, options)

        durations = [
            run_once(responses, inputs, restarts, count, options)
            for _ in range(args.repeats)
        ]
        median = float(np.median(durations))
        if baseline is None:
            baseline = median

        speedup = baseline / median
        rows.append(
            {
                "gpu_count": count,
                "durations_s": durations,
                "median_s": median,
                "subjects_per_s": args.subjects / median,
                "fits_per_s": total_fits / median,
                "speedup_vs_1gpu": speedup,
                "parallel_efficiency": speedup / count,
            }
        )
        print(
            f"{count} GPU: median={median:.6f}s "
            f"subjects/s={args.subjects / median:.3f} "
            f"fits/s={total_fits / median:.3f} "
            f"speedup={speedup:.3f} efficiency={speedup / count:.3f}"
        )

    payload = {
        "schema": "hgfx.m17.scaling.v1",
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "jax": jax.__version__,
        "jaxlib": getattr(jax.lib, "__version__", None),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "devices": [str(device) for device in visible],
        "config": {
            "gpu_counts": args.gpu_counts,
            "subjects": args.subjects,
            "trials": args.trials,
            "extra_restarts": args.extra_restarts,
            "max_iter": args.max_iter,
            "warmups": args.warmups,
            "repeats": args.repeats,
            "seed": args.seed,
        },
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
