#!/usr/bin/env python3
"""Execute the single P2A.9-authorized HGFX↔pyhgf numerical comparison.

The runner deliberately separates raw scientific execution from interpretation:
raw arrays are written and hash-verified before comparison metrics are computed.
Scientific imports are lazy so ordinary HGFX regression does not require pyhgf.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

EXPECTED_PROTOCOL = "hgfx-paper-protocol-1"
EXPECTED_CASE_ID = "p2a9-binary-hgf-common-scope-001"
EXPECTED_INPUT_SHA256 = "502c5ea2344d42d72a853a4a438a95c010c9c7a42a696815a03314b61ece0062"
EXPECTED_RESPONSE_SHA256 = "c2a910ff2ff4fd35cf3b4b7e8eb0cc69d41b80fd6239750812d5f56687d0bae2"
EXPECTED_ENV = {
    "python": "3.12.14",
    "numpy": "2.3.3",
    "jax": "0.6.2",
    "jaxlib": "0.6.2",
    "hgfx": "1.0.0",
    "pyhgf": "0.3.2",
}
EXPECTED_TRAJECTORY_TOLERANCE = {"atol": 1e-10, "rtol": 1e-8}
EXPECTED_TOTAL_NLL_TOLERANCE = {"atol": 1e-7, "rtol": 1e-8}
DERIVED_FIELDS = {
    "derived_first_level_prediction_error",
    "derived_first_level_input_surprise",
    "participant_response_nll_per_trial",
    "participant_response_nll_total",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_bit_hash(values: Sequence[int]) -> str:
    bits = list(values)
    _require(all(type(v) is int and v in (0, 1) for v in bits), "bit array is not binary")
    return hashlib.sha256(",".join(map(str, bits)).encode("ascii")).hexdigest()


def validate_authorization(case: Mapping[str, Any], gate: Mapping[str, Any]) -> None:
    """Validate the immutable case and the separate P2A.9 authorization record."""
    _require(case.get("protocol_id") == EXPECTED_PROTOCOL, "protocol mismatch")
    _require(gate.get("protocol_id") == EXPECTED_PROTOCOL, "gate protocol mismatch")
    _require(case.get("case_id") == EXPECTED_CASE_ID, "case id mismatch")
    _require(gate.get("benchmark_authorized") is True, "benchmark is not authorized")
    _require(
        gate.get("authorization_scope") == f"{EXPECTED_CASE_ID} only",
        "authorization scope does not match the frozen case",
    )
    frozen = gate.get("frozen_case", {})
    _require(frozen.get("case_id") == EXPECTED_CASE_ID, "authorization case mismatch")
    _require(case.get("benchmark_authorized") is False, "case manifest must remain pre-authorization evidence")
    _require(case.get("cross_tool_numerical_outputs_inspected") is False, "case manifest integrity changed")

    inputs = case.get("inputs")
    responses = case.get("responses")
    _require(isinstance(inputs, list) and isinstance(responses, list), "explicit input/response arrays required")
    _require(len(inputs) == 128 and len(responses) == 128, "frozen trial count changed")
    input_hash = canonical_bit_hash(inputs)
    response_hash = canonical_bit_hash(responses)
    _require(input_hash == EXPECTED_INPUT_SHA256 == case.get("inputs_sha256"), "input hash mismatch")
    _require(response_hash == EXPECTED_RESPONSE_SHA256 == case.get("responses_sha256"), "response hash mismatch")
    _require(frozen.get("inputs_sha256") == EXPECTED_INPUT_SHA256, "gate input hash mismatch")
    _require(frozen.get("responses_sha256") == EXPECTED_RESPONSE_SHA256, "gate response hash mismatch")

    _require(case["environment"]["python"] == EXPECTED_ENV["python"], "Python pin changed")
    _require(case["environment"]["numpy"] == EXPECTED_ENV["numpy"], "NumPy pin changed")
    _require(case["environment"]["jax"] == EXPECTED_ENV["jax"], "JAX pin changed")
    _require(case["environment"]["jaxlib"] == EXPECTED_ENV["jaxlib"], "JAXLIB pin changed")
    _require(case["identities"]["hgfx_package"] == "hgfx==1.0.0", "HGFX identity changed")
    _require(case["identities"]["pyhgf_package"] == "pyhgf==0.3.2", "pyhgf identity changed")
    _require(
        case["tolerances"]["trajectory_and_per_trial_quantities"] == EXPECTED_TRAJECTORY_TOLERANCE,
        "trajectory tolerance changed",
    )
    _require(
        case["tolerances"]["participant_response_nll_total"] == EXPECTED_TOTAL_NLL_TOLERANCE,
        "total NLL tolerance changed",
    )
    _require(case["response_contract"]["inverse_temperature_native_ze"] == 48.0, "inverse temperature changed")


def build_hgfx_native_parameters(case: Mapping[str, Any]) -> np.ndarray:
    """Construct the exact 14-element native HGFX vector from the frozen mapping."""
    p = case["model"]["hgfx_native_parameters"]

    def _n(value: Any) -> float:
        return np.nan if value is None else float(value)

    values = [*p["mu_0"], *p["sa_0"], *p["rho"], *p["ka"], *p["om"]]
    out = np.asarray([_n(v) for v in values], dtype=np.float64)
    _require(out.shape == (14,), "HGFX native parameter vector shape changed")
    return out


def canonical_raw_sha256(payload: Mapping[str, Any]) -> str:
    """Hash canonical raw JSON while excluding the hash field itself."""
    canonical = dict(payload)
    canonical.pop("raw_result_sha256", None)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _tolerance_for(field: str, case: Mapping[str, Any]) -> tuple[float, float]:
    key = (
        "participant_response_nll_total"
        if field == "participant_response_nll_total"
        else "trajectory_and_per_trial_quantities"
    )
    tol = case["tolerances"][key]
    return float(tol["atol"]), float(tol["rtol"])


def compare_field(
    field: str,
    hgfx_values: Any,
    pyhgf_values: Any,
    case: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare one frozen quantity using only the prospectively frozen tolerance."""
    a = np.asarray(hgfx_values, dtype=np.float64)
    b = np.asarray(pyhgf_values, dtype=np.float64)
    if a.shape != b.shape:
        return {
            "classification": "IMPLEMENTATION_MISMATCH",
            "shape_hgfx": list(a.shape),
            "shape_pyhgf": list(b.shape),
            "finite_mask_agreement": False,
            "all_finite_values_within_tolerance": False,
            "nonfinite_coordinates": [],
        }

    a_flat = a.reshape(-1)
    b_flat = b.reshape(-1)
    finite_a = np.isfinite(a_flat)
    finite_b = np.isfinite(b_flat)
    finite_mask_agreement = bool(np.array_equal(finite_a, finite_b))
    nonfinite_coordinates = np.flatnonzero(~(finite_a & finite_b)).astype(int).tolist()
    common = finite_a & finite_b
    atol, rtol = _tolerance_for(field, case)

    if np.any(common):
        av = a_flat[common]
        bv = b_flat[common]
        abs_error = np.abs(av - bv)
        denom = np.maximum(np.maximum(np.abs(av), np.abs(bv)), np.finfo(np.float64).tiny)
        rel_error = abs_error / denom
        max_abs_error = float(np.max(abs_error))
        max_rel_error = float(np.max(rel_error))
        within = bool(np.all(np.isclose(av, bv, atol=atol, rtol=rtol)))
    else:
        max_abs_error = None
        max_rel_error = None
        within = True

    any_nonfinite = bool(np.any(~finite_a) or np.any(~finite_b))
    if field in DERIVED_FIELDS and any_nonfinite:
        classification = "NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY"
    elif not finite_mask_agreement:
        classification = "IMPLEMENTATION_MISMATCH"
    elif not within:
        classification = "IMPLEMENTATION_MISMATCH"
    else:
        classification = "PASS_FOR_EXECUTED_QUANTITY"

    return {
        "classification": classification,
        "shape": list(a.shape),
        "atol": atol,
        "rtol": rtol,
        "finite_mask_agreement": finite_mask_agreement,
        "all_finite_values_within_tolerance": within,
        "nonfinite_coordinates": nonfinite_coordinates,
        "max_abs_error": max_abs_error,
        "max_rel_error": max_rel_error,
    }


def _json_safe_scalar(value: Any) -> Any:
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        f = float(value)
        if math.isnan(f):
            return "NaN"
        if math.isinf(f):
            return "+Inf" if f > 0 else "-Inf"
        return f
    return value


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return _json_safe_scalar(value)


def _nonfinite_summary(values: Any) -> dict[str, Any]:
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    nan_idx = np.flatnonzero(np.isnan(arr)).astype(int).tolist()
    pos_idx = np.flatnonzero(np.isposinf(arr)).astype(int).tolist()
    neg_idx = np.flatnonzero(np.isneginf(arr)).astype(int).tolist()
    return {
        "dtype": str(np.asarray(values).dtype),
        "nan_count": len(nan_idx),
        "nan_coordinates": nan_idx,
        "posinf_count": len(pos_idx),
        "posinf_coordinates": pos_idx,
        "neginf_count": len(neg_idx),
        "neginf_coordinates": neg_idx,
    }


def _boundary_diagnostics(fields: Mapping[str, Any]) -> dict[str, Any]:
    p = np.asarray(fields["first_level_predicted_probability"], dtype=np.float64).reshape(-1)
    l2 = np.asarray(fields["level_2_posterior_precision"], dtype=np.float64).reshape(-1)
    l3 = np.asarray(fields["level_3_posterior_precision"], dtype=np.float64).reshape(-1)

    def _max_finite(x: np.ndarray) -> float | None:
        finite = x[np.isfinite(x)]
        return float(np.max(finite)) if finite.size else None

    zero_or_one = np.flatnonzero((p == 0.0) | (p == 1.0)).astype(int).tolist()
    return {
        "first_level_predicted_probability": {
            "min_finite": float(np.min(p[np.isfinite(p)])) if np.any(np.isfinite(p)) else None,
            "max_finite": float(np.max(p[np.isfinite(p)])) if np.any(np.isfinite(p)) else None,
            "exact_zero_or_one_count": len(zero_or_one),
            "exact_zero_or_one_coordinates": zero_or_one,
        },
        "maximum_finite_level_2_posterior_precision": _max_finite(l2),
        "maximum_finite_level_3_posterior_precision": _max_finite(l3),
        "per_field_nonfinite_and_dtype": {
            name: _nonfinite_summary(values) for name, values in fields.items()
        },
    }


def _validate_runtime(case: Mapping[str, Any]) -> dict[str, Any]:
    """Verify the exact authorized runtime before scientific execution."""
    import jax
    import jax.numpy as jnp
    import jaxlib
    import hgfx
    import pyhgf

    actual = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "jaxlib": jaxlib.__version__,
        "hgfx": importlib.metadata.version("hgfx"),
        "pyhgf": importlib.metadata.version("pyhgf"),
    }
    _require(actual == EXPECTED_ENV, f"INVALID_RUN_DO_NOT_INTERPRET: version mismatch {actual}")
    _require(os.environ.get("JAX_ENABLE_X64") == "1", "INVALID_RUN_DO_NOT_INTERPRET: JAX_ENABLE_X64")
    _require(os.environ.get("JAX_PLATFORMS") == "cpu", "INVALID_RUN_DO_NOT_INTERPRET: JAX_PLATFORMS")
    _require(jax.config.read("jax_enable_x64") is True, "INVALID_RUN_DO_NOT_INTERPRET: x64 disabled")
    _require(jax.default_backend() == "cpu", "INVALID_RUN_DO_NOT_INTERPRET: backend is not CPU")
    _require(str(jnp.asarray([0.0], dtype=jnp.float64).dtype) == "float64", "JAX float64 probe failed")

    workspace = os.environ.get("GITHUB_WORKSPACE")
    module_paths = {
        "hgfx": str(Path(hgfx.__file__).resolve()),
        "pyhgf": str(Path(pyhgf.__file__).resolve()),
    }
    if workspace:
        root = Path(workspace).resolve()
        for name, module_path in module_paths.items():
            try:
                Path(module_path).resolve().relative_to(root)
            except ValueError:
                continue
            raise ValueError(f"INVALID_RUN_DO_NOT_INTERPRET: {name} imported from checkout")

    return {
        "versions": actual,
        "backend": jax.default_backend(),
        "jax_enable_x64": bool(jax.config.read("jax_enable_x64")),
        "numpy_dtype_probe": str(np.asarray([0.0], dtype=np.float64).dtype),
        "jax_dtype_probe": str(jnp.asarray([0.0], dtype=jnp.float64).dtype),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "module_paths": module_paths,
        "environment_variables": {
            "JAX_ENABLE_X64": os.environ.get("JAX_ENABLE_X64"),
            "JAX_PLATFORMS": os.environ.get("JAX_PLATFORMS"),
        },
        "github": {
            "sha": os.environ.get("GITHUB_SHA"),
            "ref": os.environ.get("GITHUB_REF"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "job": os.environ.get("GITHUB_JOB"),
        },
    }


def _execute_hgfx(case: Mapping[str, Any]) -> dict[str, Any]:
    from hgfx.models.hgf_binary import hgf_binary
    from hgfx.responses.unitsq_sigmoid import unitsq_sgm

    inputs = np.asarray(case["inputs"], dtype=np.float64)
    responses = np.asarray(case["responses"], dtype=np.float64)
    params = build_hgfx_native_parameters(case)
    traj, inf_states = hgf_binary(
        inputs,
        params,
        transformed=False,
        irregular_intervals=False,
        ignored_trials=[],
        validate=True,
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        fields: dict[str, Any] = {
            "observed_binary_input": np.asarray(traj["mu"][:, 0], dtype=np.float64),
            "first_level_predicted_probability": np.asarray(traj["muhat"][:, 0], dtype=np.float64),
            "level_2_posterior_mean": np.asarray(traj["mu"][:, 1], dtype=np.float64),
            "level_2_predicted_mean": np.asarray(traj["muhat"][:, 1], dtype=np.float64),
            "level_2_posterior_precision": np.asarray(1.0 / traj["sa"][:, 1], dtype=np.float64),
            "level_2_predicted_precision": np.asarray(1.0 / traj["sahat"][:, 1], dtype=np.float64),
            "level_3_posterior_mean": np.asarray(traj["mu"][:, 2], dtype=np.float64),
            "level_3_predicted_mean": np.asarray(traj["muhat"][:, 2], dtype=np.float64),
            "level_3_posterior_precision": np.asarray(1.0 / traj["sa"][:, 2], dtype=np.float64),
            "level_3_predicted_precision": np.asarray(1.0 / traj["sahat"][:, 2], dtype=np.float64),
        }
        p = fields["first_level_predicted_probability"]
        fields["derived_first_level_prediction_error"] = inputs - p
        fields["derived_first_level_input_surprise"] = np.where(
            inputs == 1.0, -np.log(p), -np.log1p(-p)
        )
        ze = float(case["response_contract"]["inverse_temperature_native_ze"])
        logp, _yhat, _res = unitsq_sgm(
            responses,
            inf_states,
            np.asarray([np.log(ze)], dtype=np.float64),
            predorpost=int(case["response_contract"]["hgfx_predorpost"]),
        )
        nll = -np.asarray(logp, dtype=np.float64)
        fields["participant_response_nll_per_trial"] = nll
        fields["participant_response_nll_total"] = np.asarray(np.sum(nll), dtype=np.float64)
    return fields


def _execute_pyhgf(case: Mapping[str, Any]) -> dict[str, Any]:
    import jax.numpy as jnp
    from pyhgf.math import binary_surprise
    from pyhgf.model import Network

    cfg = case["model"]["pyhgf_network"]
    level2 = cfg["level_2"]
    level3 = cfg["level_3"]
    network = Network(
        volatility_updates=cfg["volatility_updates"],
        mean_field_updates=bool(cfg["mean_field_updates"]),
        precision_clipping_value=float(cfg["precision_clipping_value"]),
        max_posterior_precision=float("inf"),
    )
    network.add_nodes(kind="binary-state")
    network.add_nodes(
        kind="continuous-state",
        mean=float(level2["mean"]),
        precision=float(level2["precision"]),
        tonic_drift=float(level2["tonic_drift"]),
        tonic_volatility=float(level2["tonic_volatility"]),
        autoconnection_strength=float(level2["autoconnection_strength"]),
        value_children=(
            [int(level2["value_child"])],
            [float(level2["value_coupling_strength"])],
        ),
    )
    network.add_nodes(
        kind="continuous-state",
        mean=float(level3["mean"]),
        precision=float(level3["precision"]),
        tonic_drift=float(level3["tonic_drift"]),
        tonic_volatility=float(level3["tonic_volatility"]),
        autoconnection_strength=float(level3["autoconnection_strength"]),
        volatility_children=(
            [int(level3["volatility_child"])],
            [float(level3["volatility_coupling_strength"])],
        ),
    )

    inputs = np.asarray(case["inputs"], dtype=np.float64)
    responses = np.asarray(case["responses"], dtype=np.float64)
    network.input_data(
        input_data=inputs,
        time_steps=np.ones(inputs.shape[0], dtype=np.float64),
        observed=np.ones(inputs.shape[0], dtype=int),
        record_trajectories=True,
    )
    trajectories = network.node_trajectories
    _require(trajectories is not None, "pyhgf did not record trajectories")

    def _node(idx: int, key: str) -> np.ndarray:
        return np.asarray(trajectories[idx][key], dtype=np.float64).reshape(-1)

    fields: dict[str, Any] = {
        "observed_binary_input": _node(0, "mean"),
        "first_level_predicted_probability": _node(0, "expected_mean"),
        "level_2_posterior_mean": _node(1, "mean"),
        "level_2_predicted_mean": _node(1, "expected_mean"),
        "level_2_posterior_precision": _node(1, "precision"),
        "level_2_predicted_precision": _node(1, "expected_precision"),
        "level_3_posterior_mean": _node(2, "mean"),
        "level_3_predicted_mean": _node(2, "expected_mean"),
        "level_3_posterior_precision": _node(2, "precision"),
        "level_3_predicted_precision": _node(2, "expected_precision"),
    }
    p = np.asarray(fields["first_level_predicted_probability"], dtype=np.float64)
    fields["derived_first_level_prediction_error"] = inputs - p
    fields["derived_first_level_input_surprise"] = np.asarray(
        binary_surprise(
            x=jnp.asarray(inputs, dtype=jnp.float64),
            expected_mean=jnp.asarray(p, dtype=jnp.float64),
            clipping=False,
        ),
        dtype=np.float64,
    )
    ze = float(case["response_contract"]["inverse_temperature_native_ze"])
    p_jax = jnp.asarray(p, dtype=jnp.float64)
    q = (p_jax**ze) / ((p_jax**ze) + ((1.0 - p_jax) ** ze))
    nll = np.asarray(
        binary_surprise(
            x=jnp.asarray(responses, dtype=jnp.float64),
            expected_mean=q,
            clipping=False,
        ),
        dtype=np.float64,
    )
    fields["participant_response_nll_per_trial"] = nll
    fields["participant_response_nll_total"] = np.asarray(np.sum(nll), dtype=np.float64)
    return fields


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def execute(case: Mapping[str, Any], gate: Mapping[str, Any], output_dir: Path) -> tuple[Path, Path]:
    validate_authorization(case, gate)
    runtime = _validate_runtime(case)
    hgfx_fields = _execute_hgfx(case)
    pyhgf_fields = _execute_pyhgf(case)

    _require(
        np.array_equal(np.asarray(hgfx_fields["observed_binary_input"]), np.asarray(case["inputs"], dtype=np.float64)),
        "HGFX observed-input integrity failure",
    )
    _require(
        np.array_equal(np.asarray(pyhgf_fields["observed_binary_input"]), np.asarray(case["inputs"], dtype=np.float64)),
        "pyhgf observed-input integrity failure",
    )

    raw_payload: dict[str, Any] = {
        "schema_version": 1,
        "protocol_id": case["protocol_id"],
        "case_id": case["case_id"],
        "environment": runtime,
        "identities": case["identities"],
        "input_hashes": {
            "inputs_sha256": case["inputs_sha256"],
            "responses_sha256": case["responses_sha256"],
        },
        "settings": {
            "hgfx_native_parameters": _json_safe(build_hgfx_native_parameters(case)),
            "pyhgf_network": case["model"]["pyhgf_network"],
            "response_contract": case["response_contract"],
            "compared_fields": case["compared_fields"],
            "tolerances": case["tolerances"],
        },
        "hgfx": {"fields": _json_safe(hgfx_fields)},
        "pyhgf": {"fields": _json_safe(pyhgf_fields)},
        "comparison": None,
        "boundary_diagnostics": {
            "hgfx": _json_safe(_boundary_diagnostics(hgfx_fields)),
            "pyhgf": _json_safe(_boundary_diagnostics(pyhgf_fields)),
        },
        "classification": "RAW_UNINTERPRETED",
        "nonfinite_json_encoding": {"nan": "NaN", "positive_infinity": "+Inf", "negative_infinity": "-Inf"},
    }
    raw_payload["raw_result_sha256"] = canonical_raw_sha256(raw_payload)
    raw_path = output_dir / "p2a10_raw_numeric_result.json"
    _write_json(raw_path, raw_payload)

    reopened = json.loads(raw_path.read_text(encoding="utf-8"))
    embedded_hash = reopened.get("raw_result_sha256")
    _require(embedded_hash == canonical_raw_sha256(reopened), "raw-result SHA-256 verification failed")

    results: dict[str, Any] = {}
    for field in case["compared_fields"]:
        results[field] = compare_field(field, hgfx_fields[field], pyhgf_fields[field], case)

    classifications = [r["classification"] for r in results.values()]
    if "IMPLEMENTATION_MISMATCH" in classifications:
        overall = "IMPLEMENTATION_MISMATCH"
    elif "NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY" in classifications:
        overall = "PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES"
    else:
        overall = "PASS_FOR_FROZEN_COMMON_SCOPE_NUMERICAL_EXECUTION"

    comparison_payload = {
        "schema_version": 1,
        "protocol_id": case["protocol_id"],
        "case_id": case["case_id"],
        "raw_result_sha256": embedded_hash,
        "raw_result_verified_before_interpretation": True,
        "comparison_formulae": {
            "max_abs_error": "max(abs(hgfx - pyhgf)) over coordinates finite in both",
            "max_rel_error": "max(abs(hgfx-pyhgf)/max(abs(hgfx),abs(pyhgf),float64_tiny)) over coordinates finite in both",
            "classification_test": "numpy.isclose using the prospectively frozen field tolerance",
        },
        "field_results": results,
        "observed_input_integrity": "PASS_EXACT",
        "overall_classification": overall,
        "post_result_changes_applied": False,
    }
    comparison_path = output_dir / "p2a10_comparison.json"
    _write_json(comparison_path, comparison_payload)
    return raw_path, comparison_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, default=Path("paper/reproducibility/pyhgf_common_scope_case.json"))
    parser.add_argument("--gate", type=Path, default=Path("paper/reproducibility/pyhgf_final_semantic_gate.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("p2a10-artifact"))
    args = parser.parse_args(argv)

    case = json.loads(args.case.read_text(encoding="utf-8"))
    gate = json.loads(args.gate.read_text(encoding="utf-8"))
    raw_path, comparison_path = execute(case, gate, args.output_dir)
    print(f"raw={raw_path}")
    print(f"comparison={comparison_path}")
    print(f"raw_result_sha256={json.loads(raw_path.read_text(encoding='utf-8'))['raw_result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
