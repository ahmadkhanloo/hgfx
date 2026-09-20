#!/usr/bin/env python3
"""Validate the frozen P2A.9 comparator case without running scientific outputs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
import platform
import sys
from pathlib import Path
from typing import Any, Sequence


EXPECTED_CASE_ID = "p2a9-binary-hgf-common-scope-001"
EXPECTED_PROTOCOL = "hgfx-paper-protocol-1"
EXPECTED_ENVIRONMENT = {
    "os": "ubuntu-24.04",
    "backend": "cpu",
    "python": "3.12.14",
    "numpy": "2.3.3",
    "jax": "0.6.2",
    "jaxlib": "0.6.2",
    "environment_variables": {
        "JAX_ENABLE_X64": "1",
        "JAX_PLATFORMS": "cpu",
    },
    "required_dtype": "float64",
    "full_resolved_environment_must_be_captured": True,
}
EXPECTED_IDENTITIES = {
    "hgfx_package": "hgfx==1.0.0",
    "hgfx_source_sha": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
    "pyhgf_package": "pyhgf==0.3.2",
    "pyhgf_source_sha": "ccd43db5ee5abe4a5a35077d098e53cce2c070c2",
    "pyhgf_sdist_sha256": "8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d",
}
EXPECTED_TRAJECTORY_TOLERANCE = {"atol": 1e-10, "rtol": 1e-8}
EXPECTED_TOTAL_NLL_TOLERANCE = {"atol": 1e-7, "rtol": 1e-8}
EXPECTED_COMPARED_FIELDS = [
    "first_level_predicted_probability",
    "level_2_posterior_mean",
    "level_2_predicted_mean",
    "level_2_posterior_precision",
    "level_2_predicted_precision",
    "level_3_posterior_mean",
    "level_3_predicted_mean",
    "level_3_posterior_precision",
    "level_3_predicted_precision",
    "derived_first_level_prediction_error",
    "derived_first_level_input_surprise",
    "participant_response_nll_per_trial",
    "participant_response_nll_total",
]


def canonical_bit_hash(values: Sequence[int]) -> str:
    """Return SHA-256 of comma-separated ASCII binary values with no whitespace."""
    bits = list(values)
    if any(type(value) is not int or value not in (0, 1) for value in bits):
        raise ValueError("canonical bit hash accepts only integer 0/1 values")
    payload = ",".join(str(value) for value in bits).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_manifest(data: dict[str, Any]) -> None:
    """Validate all prospectively frozen pre-execution settings and hashes."""
    _require(data.get("schema_version") == 1, "schema_version changed")
    _require(data.get("protocol_id") == EXPECTED_PROTOCOL, "protocol_id changed")
    _require(data.get("microstep") == "P2A.9", "microstep changed")
    _require(data.get("case_id") == EXPECTED_CASE_ID, "case_id changed")
    _require(
        data.get("status") == "FROZEN_PENDING_ENVIRONMENT_PREFLIGHT",
        "case status changed before environment preflight",
    )
    _require(data.get("cross_tool_numerical_outputs_inspected") is False,
             "cross-tool numerical outputs must not be inspected before authorization")
    _require(data.get("benchmark_authorized") is False,
             "case manifest must remain pre-authorization evidence")
    _require(data.get("identities") == EXPECTED_IDENTITIES, "package/source identity changed")
    _require(data.get("environment") == EXPECTED_ENVIRONMENT, "frozen environment changed")

    trial = data.get("trial_contract", {})
    n_trials = trial.get("n_trials")
    inputs = data.get("inputs")
    responses = data.get("responses")
    _require(n_trials == 128, "n_trials changed")
    _require(isinstance(inputs, list) and isinstance(responses, list),
             "inputs/responses must be explicit lists")
    _require(len(inputs) == n_trials, "input length differs from n_trials")
    _require(len(responses) == n_trials, "response length differs from n_trials")
    _require(all(type(v) is int and v in (0, 1) for v in inputs), "inputs are not binary")
    _require(all(type(v) is int and v in (0, 1) for v in responses), "responses are not binary")
    _require(trial.get("fully_observed") is True, "fully-observed contract changed")
    _require(trial.get("hgfx_ignored_trials") == [], "ignored-trial contract changed")
    _require(trial.get("hgfx_irregular_intervals") is False, "time contract changed")
    _require(trial.get("pyhgf_observed_mask") == "all_ones", "pyhgf mask contract changed")
    _require(trial.get("pyhgf_time_steps") == "all_ones", "pyhgf time contract changed")

    input_hash = canonical_bit_hash(inputs)
    response_hash = canonical_bit_hash(responses)
    _require(data.get("inputs_sha256") == input_hash,
             f"inputs_sha256 mismatch: expected {data.get('inputs_sha256')} got {input_hash}")
    _require(data.get("responses_sha256") == response_hash,
             f"responses_sha256 mismatch: expected {data.get('responses_sha256')} got {response_hash}")

    hgfx_params = data.get("model", {}).get("hgfx_native_parameters")
    _require(
        hgfx_params == {
            "mu_0": [None, 0.0, 1.0],
            "sa_0": [None, 0.1, 1.0],
            "rho": [None, 0.0, 0.0],
            "ka": [1.0, 1.0],
            "om": [None, -3.0, -6.0],
        },
        "HGFX fixed parameter mapping changed",
    )
    py_net = data.get("model", {}).get("pyhgf_network", {})
    _require(py_net.get("volatility_updates") == "standard", "pyhgf update family changed")
    _require(py_net.get("mean_field_updates") is True, "pyhgf mean-field policy changed")
    _require(py_net.get("precision_clipping_value") == 0.0, "pyhgf clipping policy changed")
    _require(py_net.get("max_posterior_precision") == "inf", "pyhgf precision cap changed")
    _require(py_net.get("level_2", {}).get("tonic_drift") == 0.0, "level-2 drift changed")
    _require(py_net.get("level_3", {}).get("tonic_drift") == 0.0, "level-3 drift changed")
    _require(py_net.get("level_2", {}).get("value_coupling_strength") == 1.0,
             "binary value coupling changed")
    _require(py_net.get("level_3", {}).get("volatility_coupling_strength") == 1.0,
             "volatility coupling changed")

    response_contract = data.get("response_contract", {})
    _require(response_contract.get("retained") is True, "response-NLL surface changed")
    _require(response_contract.get("inverse_temperature_native_ze") == 48.0,
             "inverse temperature changed")
    _require(response_contract.get("hgfx_predorpost") == 1, "HGFX response belief choice changed")
    _require(response_contract.get("pyhgf_surprise_clipping") is False,
             "pyhgf surprise clipping changed")

    _require(data.get("compared_fields") == EXPECTED_COMPARED_FIELDS,
             "compared output field list changed")
    tolerances = data.get("tolerances", {})
    _require(tolerances.get("trajectory_and_per_trial_quantities") == EXPECTED_TRAJECTORY_TOLERANCE,
             "trajectory tolerance changed")
    _require(tolerances.get("participant_response_nll_total") == EXPECTED_TOTAL_NLL_TOLERANCE,
             "total NLL tolerance changed")
    _require(tolerances.get("integrity_observed_input") == {"exact": True},
             "integrity tolerance changed")

    raw_schema = data.get("raw_output_schema", {})
    _require(raw_schema.get("arrays_must_be_stored_per_implementation") is True,
             "raw array preservation policy changed")
    _require(raw_schema.get("manual_numeric_transcription_allowed") is False,
             "manual transcription policy changed")
    _require(raw_schema.get("raw_result_sha256_required") is True,
             "raw result hash policy changed")


def _package_version(name: str) -> str:
    return importlib.metadata.version(name)


def _module_path(module: Any) -> str:
    path = getattr(module, "__file__", None)
    return str(Path(path).resolve()) if path else "<no-file>"


def _cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _memory_kib() -> int | None:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    return None


def runtime_preflight(data: dict[str, Any]) -> dict[str, Any]:
    """Verify the environment/API contract without executing HGF scientific data."""
    validate_manifest(data)

    import jax
    import jax.numpy as jnp
    import jaxlib
    import numpy as np
    import hgfx
    import pyhgf
    from pyhgf.math import binary_surprise
    from pyhgf.model import Network

    env = data["environment"]
    actual = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "jaxlib": jaxlib.__version__,
        "hgfx": _package_version("hgfx"),
        "pyhgf": _package_version("pyhgf"),
    }
    expected = {
        "python": env["python"],
        "numpy": env["numpy"],
        "jax": env["jax"],
        "jaxlib": env["jaxlib"],
        "hgfx": "1.0.0",
        "pyhgf": "0.3.2",
    }
    _require(actual == expected, f"resolved version mismatch: expected {expected}, got {actual}")
    _require(os.environ.get("JAX_ENABLE_X64") == "1", "JAX_ENABLE_X64 is not exactly '1'")
    _require(os.environ.get("JAX_PLATFORMS") == "cpu", "JAX_PLATFORMS is not exactly 'cpu'")
    _require(jax.config.read("jax_enable_x64") is True, "jax x64 mode is disabled")
    _require(jax.default_backend() == "cpu", f"JAX backend is {jax.default_backend()}, not cpu")
    _require(str(jnp.asarray([0.0], dtype=jnp.float64).dtype) == "float64",
             "JAX float64 array did not remain float64")
    _require(str(np.asarray([0.0], dtype=np.float64).dtype) == "float64",
             "NumPy float64 array did not remain float64")

    # Construction checks public configuration only. Do not add nodes or call input_data.
    network = Network(
        volatility_updates="standard",
        mean_field_updates=True,
        precision_clipping_value=0.0,
        max_posterior_precision=float("inf"),
    )
    _require(network.volatility_updates == "standard", "Network volatility_updates mismatch")
    _require(network.mean_field_updates is True, "Network mean_field_updates mismatch")
    _require(network.precision_clipping_value == 0.0, "Network clipping guard mismatch")
    _require(math.isinf(network.max_posterior_precision) and network.max_posterior_precision > 0,
             "Network precision cap is not +inf")
    surprise_signature = inspect.signature(binary_surprise)
    _require("clipping" in surprise_signature.parameters,
             "pyhgf binary_surprise no longer exposes clipping parameter")

    distributions = {
        dist.metadata["Name"]: dist.version
        for dist in importlib.metadata.distributions()
        if dist.metadata.get("Name")
    }
    provenance = {
        "schema_version": 1,
        "protocol_id": data["protocol_id"],
        "case_id": data["case_id"],
        "scientific_execution_performed": False,
        "cross_tool_numerical_outputs_inspected": False,
        "versions": actual,
        "module_paths": {
            "hgfx": _module_path(hgfx),
            "pyhgf": _module_path(pyhgf),
            "jax": _module_path(jax),
            "jaxlib": _module_path(jaxlib),
            "numpy": _module_path(np),
        },
        "runtime": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "cpu_model": _cpu_model(),
            "memory_kib": _memory_kib(),
            "jax_backend": jax.default_backend(),
            "jax_enable_x64": bool(jax.config.read("jax_enable_x64")),
            "numpy_dtype_probe": str(np.asarray([0.0], dtype=np.float64).dtype),
            "jax_dtype_probe": str(jnp.asarray([0.0], dtype=jnp.float64).dtype),
        },
        "pyhgf_public_configuration": {
            "volatility_updates": network.volatility_updates,
            "mean_field_updates": network.mean_field_updates,
            "precision_clipping_value": network.precision_clipping_value,
            "max_posterior_precision": "inf",
            "binary_surprise_has_clipping_parameter": True,
        },
        "environment_variables": {
            "JAX_ENABLE_X64": os.environ.get("JAX_ENABLE_X64"),
            "JAX_PLATFORMS": os.environ.get("JAX_PLATFORMS"),
        },
        "github": {
            "sha": os.environ.get("GITHUB_SHA"),
            "ref": os.environ.get("GITHUB_REF"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "job": os.environ.get("GITHUB_JOB"),
        },
        "resolved_distributions": dict(sorted(distributions.items(), key=lambda item: item[0].lower())),
    }
    return provenance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="paper/reproducibility/pyhgf_common_scope_case.json",
        type=Path,
    )
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_manifest(data)
    result: dict[str, Any] = {
        "schema_version": 1,
        "protocol_id": data["protocol_id"],
        "case_id": data["case_id"],
        "manifest_validation": "PASS",
        "scientific_execution_performed": False,
    }
    if args.runtime:
        result["runtime_preflight"] = runtime_preflight(data)

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
