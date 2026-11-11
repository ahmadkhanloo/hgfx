#!/usr/bin/env python3
"""Deterministic PERF-01 input producer. No inference, timing, or HGFX import."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

SEED = 20261104
HORIZONS = (128, 512, 1024)
SUBJECTS = 64
SCHEMA = "hgfx-runtime-input-v1"


def encode(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_data(n_trials: int) -> dict:
    """Independent PCG64 stream per horizon; rows are ordered subject IDs."""
    rng = np.random.Generator(np.random.PCG64(SEED + n_trials))
    u = rng.integers(0, 2, size=(SUBJECTS, n_trials), dtype=np.uint8)
    flip_rate = 0.08 + 0.01 * (np.arange(SUBJECTS) % 5)
    flipped = rng.random((SUBJECTS, n_trials)) < flip_rate[:, None]
    y = np.where(flipped, 1 - u.astype(np.int16), u).astype(np.uint8)
    return {
        "schema": SCHEMA,
        "seed": SEED + n_trials,
        "dtype": "float64-on-load",
        "trial_count": n_trials,
        "subject_count": SUBJECTS,
        "subject_indices_zero_based": list(range(SUBJECTS)),
        "u": u.tolist(),
        "y": y.tolist(),
    }


def cases(digests: dict[int, str]) -> list[dict]:
    out: list[dict] = []
    for n in HORIZONS:
        for stage in ("forward", "objective", "fit_compat_full"):
            out.append({"id": f"primary_{stage}_{n}", "tier": "primary", "model": "hgf_binary", "obs": "unitsq_sgm", "stage": stage, "n_trials": n, "subjects": 1, "source_file": f"inputs/binary_{n}_s64.json", "source_sha256": digests[n]})
    for model in ("ehgf_binary", "uhgf_binary"):
        for n in HORIZONS:
            for stage in ("forward", "objective"):
                out.append({"id": f"secondary_{model}_{stage}_{n}", "tier": "secondary", "model": model, "obs": "unitsq_sgm", "stage": stage, "n_trials": n, "subjects": 1, "source_file": f"inputs/binary_{n}_s64.json", "source_sha256": digests[n]})
    for n in (128, 512):
        for n_subjects in (1, 16, 64):
            out.append({"id": f"throughput_fit_{n_subjects}x{n}", "tier": "throughput", "model": "hgf_binary", "obs": "unitsq_sgm", "stage": "fit_compat_full_or_clearly_labeled_fast", "n_trials": n, "subjects": n_subjects, "source_file": f"inputs/binary_{n}_s64.json", "source_sha256": digests[n]})
    out.append({"id": "robustness_masked_512", "tier": "robustness", "model": "hgf_binary", "obs": "unitsq_sgm", "stage": "forward_objective", "n_trials": 512, "subjects": 1, "source_file": "inputs/binary_512_s64.json", "source_sha256": digests[512], "mask_indices_zero_based": {"ignored_input_and_response": [31, 127], "irregular_response_only": [63, 255]}})
    return out


def produce(root: Path, check: bool = False) -> dict:
    digests: dict[int, str] = {}
    for n in HORIZONS:
        rel = Path("inputs") / f"binary_{n}_s64.json"
        content = encode(make_data(n))
        digests[n] = digest(content)
        dest = root / rel
        if check:
            if not dest.is_file() or dest.read_bytes() != content:
                raise ValueError(f"Missing or noncanonical fixture: {dest}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.read_bytes() != content:
                raise ValueError(f"Refusing to overwrite changed input: {dest}")
            dest.write_bytes(content)
    manifest = {
        "schema": "hgfx-runtime-manifest-v1",
        "protocol_id": "hgfx-matlab-runtime-1",
        "status": "INPUT_DATA_GENERATED_CONFIGS_PENDING_NOT_FROZEN",
        "seed": SEED,
        "rng": "numpy.random.Generator(PCG64(seed + trial_count))",
        "product_source_sha": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
        "matlab_oracle_sha": "2437f4dc241541072722a2695ddeca7b44d83dd3",
        "configs_and_starts": "PENDING_VERIFIED_HGFX_1_0_0_EXPORT_AND_MATLAB_REVIEW",
        "case_count": 28,
        "cases": cases(digests),
    }
    if len(manifest["cases"]) != manifest["case_count"]:
        raise AssertionError("Workload registry changed")
    dest = root / "inputs_manifest.json"
    content = encode(manifest)
    if check:
        if not dest.is_file() or dest.read_bytes() != content:
            raise ValueError(f"Missing or noncanonical manifest: {dest}")
    else:
        if dest.exists() and dest.read_bytes() != content:
            raise ValueError(f"Refusing to overwrite changed manifest: {dest}")
        dest.write_bytes(content)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = produce(args.output, check=args.check)
    print(f"{len(manifest['cases'])} cases; hashes validated; check={args.check}")


if __name__ == "__main__":
    main()
