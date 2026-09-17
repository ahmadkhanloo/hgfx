from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_p2a10_common_scope.py"
CASE_PATH = ROOT / "paper" / "reproducibility" / "pyhgf_common_scope_case.json"
GATE_PATH = ROOT / "paper" / "reproducibility" / "pyhgf_final_semantic_gate.json"


def _load_runner():
    assert RUNNER_PATH.is_file(), "P2A.10 runner has not been implemented yet"
    spec = importlib.util.spec_from_file_location("run_p2a10_common_scope", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_frozen_gate_authorizes_only_the_frozen_case():
    runner = _load_runner()
    case = _load_json(CASE_PATH)
    gate = _load_json(GATE_PATH)

    runner.validate_authorization(case, gate)

    bad_gate = dict(gate)
    bad_gate["authorization_scope"] = "different-case only"
    with pytest.raises(ValueError, match="authorization"):
        runner.validate_authorization(case, bad_gate)


def test_hgfx_native_parameter_vector_is_exactly_the_frozen_mapping():
    runner = _load_runner()
    case = _load_json(CASE_PATH)
    p = runner.build_hgfx_native_parameters(case)

    assert p.dtype == np.float64
    assert p.shape == (14,)
    assert np.isnan(p[[0, 3, 6, 11]]).all()
    np.testing.assert_array_equal(
        p[[1, 2, 4, 5, 7, 8, 9, 10, 12, 13]],
        np.asarray([0.0, 1.0, 0.1, 1.0, 0.0, 0.0, 1.0, 1.0, -3.0, -6.0]),
    )


def test_raw_payload_hash_is_canonical_and_not_self_referential():
    runner = _load_runner()
    payload = {"z": [1.0, "NaN"], "a": {"x": 2}, "raw_result_sha256": "old"}
    digest = runner.canonical_raw_sha256(payload)

    expected_payload = {"a": {"x": 2}, "z": [1.0, "NaN"]}
    expected_bytes = json.dumps(
        expected_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert digest == hashlib.sha256(expected_bytes).hexdigest()


def test_compare_field_uses_frozen_tolerance_and_reports_pass():
    runner = _load_runner()
    case = _load_json(CASE_PATH)
    a = np.asarray([0.1, 0.2, 0.3], dtype=np.float64)
    b = a + np.asarray([0.0, 1e-12, -1e-12], dtype=np.float64)

    result = runner.compare_field("level_2_posterior_mean", a, b, case)
    assert result["classification"] == "PASS_FOR_EXECUTED_QUANTITY"
    assert result["all_finite_values_within_tolerance"] is True
    assert result["finite_mask_agreement"] is True


def test_compare_field_reports_implementation_mismatch_for_finite_state_error():
    runner = _load_runner()
    case = _load_json(CASE_PATH)
    a = np.asarray([0.1, 0.2], dtype=np.float64)
    b = np.asarray([0.1, 0.25], dtype=np.float64)

    result = runner.compare_field("level_2_posterior_mean", a, b, case)
    assert result["classification"] == "IMPLEMENTATION_MISMATCH"
    assert result["all_finite_values_within_tolerance"] is False


def test_compare_field_marks_nonfinite_derived_nll_as_not_directly_comparable():
    runner = _load_runner()
    case = _load_json(CASE_PATH)
    a = np.asarray([0.2, np.inf], dtype=np.float64)
    b = np.asarray([0.2, np.inf], dtype=np.float64)

    result = runner.compare_field("participant_response_nll_per_trial", a, b, case)
    assert result["classification"] == "NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY"
    assert result["nonfinite_coordinates"] == [1]
