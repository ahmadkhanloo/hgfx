#!/usr/bin/env python3
"""REV-2.4 frozen 600-vector input manifest (NOT an objective parity result).

Release-only executable: NumPy 2.0.2, non-editable HGFX 1.0.0 wheel, CPU x64.
The pure helper functions are unit-testable without installing HGFX; they
do not perform fitting, objective evaluations, or MATLAB reference calls.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from zipfile import ZipFile

import numpy as np

PROTOCOL = "compstat-rev2-4-objective-cross-eval-v1"
FROZEN_RELEASE = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_REFERENCE = "2437f4dc241541072722a2695ddeca7b44d83dd3"
NUMPY_VERSION = "2.0.2"
MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
REPLICATES = 200
TRIALS = 128
BASE_SEED = 2026111000


def demand(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def content_sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        .encode("utf-8")
    ).hexdigest()


def ieee(value: float) -> float | str:
    x = float(value)
    return x if math.isfinite(x) else (
        "NaN" if math.isnan(x) else ("+Inf" if x > 0 else "-Inf")
    )


def binary_data() -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(TRIALS, dtype=np.int64)
    u = (((37 * t + 11) % 101) < 51).astype(np.float64)
    y = (((29 * t + 3) % 97) < 47).astype(np.float64)
    return u, y


def f64_hash(values: np.ndarray) -> str:
    # Explicit little-endian binary64, independent of the host native endian.
    return hashlib.sha256(
        np.asarray(values, dtype="<f8").reshape(-1).tobytes(order="C")
    ).hexdigest()


def make_cases(
    model: str, seed: int, full_prior_means: np.ndarray,
    full_prior_variances: np.ndarray, count: int = REPLICATES,
) -> dict:
    """Generate *all* requested prior draws, without rejection or clipping."""
    demand(model in MODELS, "Model not in frozen three-family grid")
    means = np.asarray(full_prior_means, dtype=np.float64).reshape(-1)
    variances = np.asarray(full_prior_variances, dtype=np.float64).reshape(-1)
    demand(means.shape == variances.shape and means.size > 0,
           "Invalid resolved full prior vector lengths")
    demand(np.all(np.isfinite(means)), "Resolved prior means must be finite")
    demand(count > 0, "Grid size must be positive")
    free = np.flatnonzero(np.isfinite(variances) & (variances > 0))
    demand(free.size > 0, "Model has no valid free parameters")
    demand(np.all((~np.isfinite(variances)) | (variances >= 0)),
           "Negative prior variance in release config")
    rng = np.random.Generator(np.random.PCG64(seed))
    rows = []
    for i in range(count):
        z = rng.standard_normal(free.size)
        sample = means.copy()
        sample[free] = means[free] + np.sqrt(variances[free]) * z
        demand(np.all(np.isfinite(sample)), f"Nonfinite drawn vector at index {i}")
        row = {
            "case_id": f"REV24-G-{model}-{i:03d}",
            "replicate_zero_based": i,
            "seed": seed,
            "model": model,
            "observation_model": "unitsq_sgm",
            "full_transformed": sample.tolist(),
            "free_transformed": sample[free].tolist(),
        }
        row["case_sha256"] = content_sha256(row)
        rows.append(row)
    return {
        "model": model,
        "observation_model": "unitsq_sgm",
        "seed": seed,
        "free_indices_zero_based": free.tolist(),
        "prior_means_full": means.tolist(),
        "prior_variances_full_ieee": [ieee(x) for x in variances],
        "rows": rows,
    }


def build_manifest(configs: dict[str, tuple[np.ndarray, np.ndarray]],
                   wheel_sha256: str, numpy_version: str) -> dict:
    demand(tuple(configs) == MODELS, "Frozen model ordering must not change")
    demand(numpy_version == NUMPY_VERSION,
           f"Requires exact NumPy {NUMPY_VERSION} to freeze PCG64 draws")
    demand(len(wheel_sha256) == 64 and
           all(c in "0123456789abcdef" for c in wheel_sha256),
           "Unverified HGFX release-wheel SHA256")
    u, y = binary_data()
    strata = [
        make_cases(model, BASE_SEED + i, *configs[model])
        for i, model in enumerate(MODELS)
    ]
    payload = {
        "protocol": PROTOCOL,
        "scope": "SYNTHETIC_FIXED_VECTOR_ONLY_NOT_FITTING_OR_INFERENCE",
        "release_version": "1.0.0",
        "release_source_commit_declared": FROZEN_RELEASE,
        "release_wheel_sha256": wheel_sha256,
        "matlab_reference_commit": MATLAB_REFERENCE,
        "numpy_version": numpy_version,
        "rng": "numpy.Generator(numpy.PCG64(seed)).standard_normal",
        "n_per_model": REPLICATES,
        "trials": TRIALS,
        "inputs_binary64_le_sha256": f64_hash(u),
        "responses_binary64_le_sha256": f64_hash(y),
        "inputs": u.tolist(),
        "responses": y.tolist(),
        "strata": strata,
    }
    payload["manifest_sha256"] = content_sha256(payload)
    validate_manifest(payload)
    return payload


def validate_manifest(payload: dict) -> None:
    """Independent schema/hash checks, NOT a MATLAB/HGFX science verdict."""
    demand(payload.get("protocol") == PROTOCOL, "Wrong protocol")
    demand(payload.get("release_source_commit_declared") == FROZEN_RELEASE,
           "Wrong released source")
    demand(payload.get("matlab_reference_commit") == MATLAB_REFERENCE,
           "Wrong original MATLAB reference")
    demand(payload.get("numpy_version") == NUMPY_VERSION,
           "Wrong frozen RNG runtime")
    demand(payload.get("n_per_model") == REPLICATES and
           payload.get("trials") == TRIALS, "Original grid size changed")
    u, y = binary_data()
    demand(payload["inputs"] == u.tolist() and
           payload["responses"] == y.tolist(), "Frozen input/response data changed")
    demand(payload["inputs_binary64_le_sha256"] == f64_hash(u) and
           payload["responses_binary64_le_sha256"] == f64_hash(y),
           "Frozen binary64 array digest mismatch")
    strata = payload["strata"]
    demand(len(strata) == len(MODELS), "Model family disappeared")
    for index, (model, group) in enumerate(zip(MODELS, strata, strict=True)):
        demand(group["model"] == model and group["seed"] == BASE_SEED + index,
               "Grid model/seed identity changed")
        rows = group["rows"]
        demand(len(rows) == REPLICATES, "Model grid denominator changed")
        priors = np.asarray(group["prior_means_full"], dtype=np.float64)
        variances = np.asarray([
            float("nan") if x == "NaN" else float(x)
            for x in group["prior_variances_full_ieee"]
        ], dtype=np.float64)
        free = np.flatnonzero(np.isfinite(variances) & (variances > 0))
        demand(group["free_indices_zero_based"] == free.tolist(),
               "Free parameters changed")
        for i, item in enumerate(rows):
            demand(item["case_id"] == f"REV24-G-{model}-{i:03d}" and
                   item["replicate_zero_based"] == i and
                   item["model"] == model and
                   item["seed"] == BASE_SEED + index, "Case identity drift")
            demand(item["case_sha256"] ==
                   content_sha256({k: v for k, v in item.items()
                                   if k != "case_sha256"}), "Case hash mismatch")
            full = np.asarray(item["full_transformed"], dtype=np.float64)
            demand(full.shape == priors.shape and np.all(np.isfinite(full)),
                   "Invalid frozen full vector")
            fixed = np.ones(len(priors), dtype=bool)
            fixed[free] = False
            demand(np.array_equal(full[fixed], priors[fixed]),
                   "A fixed parameter was changed")
            demand(item["free_transformed"] == full[free].tolist(),
                   "Free/full transform mismatch")
    demand(payload["manifest_sha256"] ==
           content_sha256({k: v for k, v in payload.items()
                           if k != "manifest_sha256"}), "Manifest hash mismatch")


def release_config_vectors() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    # Lazy imports allow independent arithmetic/unit-test validation without
    # importing an unavailable or unintended HGFX science runtime.
    from hgfx.compat.configs import hgf_binary_config, unitsq_sgm_config
    from hgfx.compat.simulation import ehgf_binary_config, uhgf_binary_config
    factories = (hgf_binary_config, ehgf_binary_config, uhgf_binary_config)
    u, _ = binary_data()
    observation = unitsq_sgm_config()
    result = {}
    for model, factory in zip(MODELS, factories, strict=True):
        perceptual = factory().resolve_placeholders(u)
        result[model] = (
            np.concatenate([perceptual.priormus, observation.priormus]),
            np.concatenate([perceptual.priorsas, observation.priorsas]),
        )
    return result


def verify_installed_wheel_files(wheel: Path, dist: object) -> int:
    """Verify the *installed* HGFX Python sources match the supplied wheel."""
    with ZipFile(wheel) as archive:
        source_members = [
            name for name in archive.namelist()
            if name.startswith("hgfx/") and name.endswith(".py")
        ]
        demand(bool(source_members), "Released wheel has no HGFX Python modules")
        for name in source_members:
            installed = Path(dist.locate_file(name))
            demand(installed.is_file(), f"Installed release source absent: {name}")
            demand(
                hashlib.sha256(installed.read_bytes()).digest()
                == hashlib.sha256(archive.read(name)).digest(),
                f"Installed HGFX source differs from supplied release wheel: {name}",
            )
    return len(source_members)


def require_released_runtime(wheel: Path) -> str:
    demand(np.__version__ == NUMPY_VERSION,
           f"Do not generate scientific input on NumPy {np.__version__}; required {NUMPY_VERSION}")
    demand(importlib.metadata.version("hgfx") == "1.0.0",
           "Use installed released HGFX 1.0.0 wheel; never use the 1.1.0b1 worktree")
    dist = importlib.metadata.distribution("hgfx")
    direct = dist.read_text("direct_url.json") or ""
    demand('"editable": true' not in direct.lower() and
           '"editable":true' not in direct.lower(),
           "Editable HGFX install forbidden for release scientific grid")
    demand(wheel.is_file() and
           wheel.name.startswith("hgfx-1.0.0-") and
           wheel.suffix.lower() == ".whl", "Require archived original 1.0.0 wheel")
    verify_installed_wheel_files(wheel, dist)
    return hashlib.sha256(wheel.read_bytes()).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release-wheel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    wheel_sha = require_released_runtime(args.release_wheel)
    payload = build_manifest(release_config_vectors(), wheel_sha, np.__version__)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # No implicit regeneration over an earlier frozen paired input.
    demand(not args.output.exists(), "Frozen manifest exists: refusal to overwrite")
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True,
                                      allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "INPUT_MANIFEST_GENERATED_NO_MATLAB_EXECUTED",
        "protocol": PROTOCOL,
        "cases": sum(len(s["rows"]) for s in payload["strata"]),
        "manifest_sha256": payload["manifest_sha256"],
        "release_wheel_sha256": wheel_sha,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
