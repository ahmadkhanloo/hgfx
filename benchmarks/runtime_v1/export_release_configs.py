#!/usr/bin/env python3
"""Export pre-freeze configuration/start snapshots from verified HGFX 1.0.0.

This is metadata preparation, NOT scientific parity or a speed benchmark.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from importlib import metadata
import json
import math
from pathlib import Path

import numpy as np

from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
from hgfx.compat.simulation import ehgf_binary_config, uhgf_binary_config
from hgfx.core.priors import optimization_indices
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

from generate_inputs import digest, encode

RELEASE = "1.0.0"
REFERENCE = "2437f4dc241541072722a2695ddeca7b44d83dd3"
MODEL_FACTORIES = {
    "hgf_binary": hgf_binary_config,
    "ehgf_binary": ehgf_binary_config,
    "uhgf_binary": uhgf_binary_config,
}
HORIZONS = (128, 512, 1024)


def number(value: object) -> dict[str, str]:
    """Preserve full binary64 representation, including undefined NaN sentinels."""
    f = float(value)
    if math.isnan(f):
        return {"special": "NaN"}
    if math.isinf(f):
        return {"special": "Infinity" if f > 0 else "-Infinity"}
    return {"decimal": repr(f), "hex": f.hex()}


def serialize_model(config) -> dict:
    return {
        "name": config.model,
        "options": dict(config.options),
        "source_files": list(config.source_files),
        "parameters": [
            {
                "name": p.name,
                "native_name": p.native_name,
                "matlab_index_1based": p.matlab_index,
                "component": p.component,
                "prior_mean": number(p.prior_mean),
                "prior_variance": number(p.prior_variance),
                "transform": p.transform.kind.value,
                "transform_upper": number(p.transform.upper),
                "status": p.status.value,
            }
            for p in config.parameters
        ],
        "free_indices_0based": list(config.free_indices),
        "free_indices_1based": list(config.matlab_free_indices),
        "fixed_indices_0based": list(config.fixed_indices),
        "undefined_indices_0based": list(config.undefined_indices),
    }


def snapshot(model: str, inputs: np.ndarray) -> dict:
    perceptual = MODEL_FACTORIES[model]().resolve_placeholders(inputs)
    observation = unitsq_sgm_config()
    priors = np.concatenate((perceptual.priormus, observation.priormus))
    variances = np.concatenate((perceptual.priorsas, observation.priorsas))
    free = tuple(optimization_indices(variances))
    expected = (
        tuple(perceptual.free_indices)
        + tuple(i + len(perceptual.parameters) for i in observation.free_indices)
    )
    if free != expected:
        raise AssertionError("Unmatched fitModel free parameter ordering")
    if len(free) < 1:
        raise AssertionError("Unexpected zero free parameters")
    return {
        "schema": "hgfx-runtime-config-v1",
        "status": "HGFX_EXPORTED_MATLAB_UNVERIFIED",
        "model": model,
        "observation_model": observation.model,
        "perceptual": serialize_model(perceptual),
        "observation": serialize_model(observation),
        "transformed_start_full": [number(v) for v in priors],
        "transformed_start_free": [number(priors[i]) for i in free],
        "fit_free_indices_0based": list(free),
        "fit_free_indices_1based": [i + 1 for i in free],
        "optimizer": {**asdict(QuasiNewtonOptions()), "n_rand_init": 0},
    }


def write_or_check(path: Path, content: bytes, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_bytes() != content:
            raise ValueError(f"Missing or noncanonical export: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise ValueError(f"Refusing to overwrite changed export: {path}")
    path.write_bytes(content)


def produce(root: Path, *, check: bool = False) -> dict:
    # A version match is necessary but not sufficient for provenance: the
    # workflow separately verifies tag checkout's exact commit before install.
    installed = metadata.version("hgfx")
    if installed != RELEASE:
        raise RuntimeError(f"Require independently installed hgfx=={RELEASE}; got {installed}")
    manifest_path = root / "inputs_manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    if manifest["protocol_id"] != "hgfx-matlab-runtime-1":
        raise ValueError("Incorrect runtime protocol")
    if manifest["product_source_sha"] != "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27":
        raise ValueError("HGFX source SHA does not match v1.0.0")
    if manifest["matlab_oracle_sha"] != REFERENCE:
        raise ValueError("Incorrect MATLAB oracle")
    entries: list[dict] = []
    for n in HORIZONS:
        rel_input = f"inputs/binary_{n}_s64.json"
        source = root / rel_input
        raw = source.read_bytes()
        item = json.loads(raw)
        matches = [c for c in manifest["cases"] if c["source_file"] == rel_input]
        if not matches or any(digest(raw) != c["source_sha256"] for c in matches):
            raise ValueError(f"Unverified source file: {rel_input}")
        u = np.asarray(item["u"], dtype=np.float64)
        y = np.asarray(item["y"], dtype=np.float64)
        if u.shape != (64, n) or y.shape != (64, n):
            raise ValueError(f"Unexpected source dimensions: {rel_input}")
        if not (np.all((u == 0) | (u == 1)) and np.all((y == 0) | (y == 1))):
            raise ValueError(f"Nonbinary source: {rel_input}")
        for model in MODEL_FACTORIES:
            ref = snapshot(model, u[0])
            ref_bytes = encode(ref)
            # Verify that the single exported parameter/start vector is
            # applicable to every predeclared subject, not just subject 0.
            for row in u[1:]:
                if encode(snapshot(model, row)) != ref_bytes:
                    raise ValueError(f"Subject-specific priors require individual export: {model}/{n}")
            rel = f"configs/{model}_{n}.json"
            write_or_check(root / rel, ref_bytes, check)
            entries.append({
                "model": model, "trial_count": n,
                "source_file": rel_input, "source_sha256": digest(raw),
                "config_file": rel, "config_sha256": digest(ref_bytes),
                "free_parameter_count": len(ref["fit_free_indices_0based"]),
                "subject_count_verified": 64,
            })
    document = {
        "schema": "hgfx-runtime-resolved-configs-v1",
        "protocol_id": "hgfx-matlab-runtime-1",
        "status": "HGFX_1_0_0_EXPORTED_PENDING_MATLAB_CROSSCHECK_NOT_FROZEN",
        "hgfx_distribution_version": installed,
        "hgfx_source_expected_sha": manifest["product_source_sha"],
        "matlab_reference_expected_sha": REFERENCE,
        "input_manifest_sha256": digest(manifest_path.read_bytes()),
        "entries": entries,
    }
    write_or_check(root / "resolved_configs_manifest.json", encode(document), check)
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = produce(args.output, check=args.check)
    print(f"Verified {len(result['entries'])} config cells; check={args.check}")


if __name__ == "__main__":
    main()
