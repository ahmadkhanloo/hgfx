#!/usr/bin/env python3
"""REV-2.4 Panel-G HGFX evaluator: frozen 1.0.0 wheel, NO optimizer.

Consumes the single precommitted 600-vector manifest; creates one complete
source-labelled evaluation record with every failed/nonfinite case retained.
This is one-sided science only. A genuine frozen MATLAB run and the independent
comparator are required before ANY parity conclusion.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

import numpy as np

from tools.compstat_rev24_manifest import (
    FROZEN_RELEASE, MATLAB_REFERENCE, MODELS, NUMPY_VERSION,
    PROTOCOL, REPLICATES, ieee, release_config_vectors,
    require_released_runtime, validate_manifest,
)


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def f64(values) -> np.ndarray:
    return np.asarray([
        float("nan") if value == "NaN" else float(value)
        for value in values
    ], dtype=np.float64)


def evaluate_one(model: str, row: dict, group: dict, inputs: np.ndarray,
                 responses: np.ndarray, objective_function) -> dict:
    result = {
        "case_id": row["case_id"],
        "case_sha256": row["case_sha256"],
        "model": model,
        "config_sha256": group["config_sha256"],
        "valid": False,
        "rval": -1,
        "neg_log_likelihood": "NaN",
        "neg_log_joint": "NaN",
        "log_likelihood": "NaN",
        "trial_log_likelihoods": [],
        "perceptual_prior_total": "NaN",
        "observation_prior_total": "NaN",
        "error_type": "",
        "error_message": "",
    }
    try:
        full = f64(row["full_transformed"])
        free = np.asarray(group["free_indices_zero_based"], dtype=np.int64)
        check(np.array_equal(full[free], np.asarray(row["free_transformed"],
                                                   dtype=np.float64)),
              "Frozen transformed free-vector values do not match source")
        objective = objective_function(
            model=model, inputs=inputs, responses=responses,
            full_parameters=full,
        )
        result["rval"] = int(objective.rval)
        result["neg_log_likelihood"] = ieee(objective.neg_log_likelihood)
        result["neg_log_joint"] = ieee(objective.neg_log_joint)
        result["log_likelihood"] = ieee(objective.log_likelihood)
        ll = np.asarray(objective.trial_log_likelihoods,
                        dtype=np.float64).reshape(-1)
        result["trial_log_likelihoods"] = [ieee(v) for v in ll]
        result["perceptual_prior_total"] = ieee(objective.perceptual_prior.total)
        result["observation_prior_total"] = ieee(objective.observation_prior.total)
        result["valid"] = (
            objective.rval == 0
            and ll.shape == (128,)
            and np.all(np.isfinite(ll))
            and np.isfinite(objective.neg_log_likelihood)
            and np.isfinite(objective.neg_log_joint)
            and np.isfinite(objective.log_likelihood)
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error_message"] = str(exc)[:1000]
    return result


def evaluate_manifest(manifest: dict, configs, objective_function,
                      *, wheel_sha256: str, runtime: dict) -> dict:
    validate_manifest(manifest)
    check(manifest["release_wheel_sha256"] == wheel_sha256,
          "Frozen wheel SHA-256 does not match manifest creator")
    inputs = np.asarray(manifest["inputs"], dtype=np.float64)
    responses = np.asarray(manifest["responses"], dtype=np.float64)
    cases = []
    for model, group in zip(MODELS, manifest["strata"], strict=True):
        means, variances = configs[model]
        check(group["prior_means_full"] == [ieee(v) for v in means],
              f"{model}: version/config prior means differ from frozen input")
        check(group["prior_variances_full_ieee"] == [ieee(v) for v in variances],
              f"{model}: version/config prior variances differ from frozen input")
        check(group["observation_model"] == "unitsq_sgm", "Wrong observation model")
        for row in group["rows"]:
            cases.append(evaluate_one(model, row, group, inputs, responses,
                                      objective_function))
    check(len(cases) == REPLICATES * len(MODELS), "Any dropped result is invalid")
    return {
        "protocol": PROTOCOL,
        "source": "hgfx",
        "release_source_commit": FROZEN_RELEASE,
        "matlab_reference_commit": MATLAB_REFERENCE,
        "manifest_sha256": manifest["manifest_sha256"],
        "inputs_binary64_le_sha256": manifest["inputs_binary64_le_sha256"],
        "responses_binary64_le_sha256": manifest["responses_binary64_le_sha256"],
        "release_wheel_sha256": wheel_sha256,
        "runtime": runtime,
        "cases": cases,
        "scientific_parity_status": "NOT_ASSESSED_NO_MATLAB_PAIR",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--release-wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists(), "Refusing to overwrite the original evaluation")
    wheel_hash = require_released_runtime(args.release_wheel)
    check(np.__version__ == NUMPY_VERSION, "Wrong frozen NumPy runtime")
    # Import the scientific release only AFTER verifying its Wheel/runtime.
    import hgfx
    import jax
    import jaxlib
    from hgfx.diagnostics.recovery import _objective_for_variant
    check(bool(jax.config.read("jax_enable_x64")), "JAX float64 must be enabled")
    check(jax.default_backend() == "cpu", "Use original CPU x64 validation order")
    check(
        Path(hgfx.__file__).resolve()
        == Path(importlib.metadata.distribution("hgfx").locate_file(
            "hgfx/__init__.py")).resolve(),
        "HGFX import resolved to working branch instead of installed 1.0.0 wheel",
    )
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = evaluate_manifest(
        manifest, release_config_vectors(), _objective_for_variant,
        wheel_sha256=wheel_hash,
        runtime={
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "jax": jax.__version__,
            "jaxlib": jaxlib.__version__,
            "jax_x64": True,
            "jax_backend": jax.default_backend(),
            "hgfx_distribution": importlib.metadata.version("hgfx"),
            "hgfx_source_path": str(Path(hgfx.__file__).resolve()),
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["scientific_parity_status"],
        "source": result["source"],
        "case_count": len(result["cases"]),
        "valid": sum(bool(row["valid"]) for row in result["cases"]),
        "invalid": sum(not row["valid"] for row in result["cases"]),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
