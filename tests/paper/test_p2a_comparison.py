from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper" / "scripts" / "generate_p2a_comparison.py"
INPUT = ROOT / "paper" / "evidence" / "p2a" / "common_scope_input.json"
INPUT_MANIFEST = ROOT / "paper" / "reproducibility" / "p2a_input_manifest.json"

EXPECTED_GATE_CRITERIA = {
    "model_structure",
    "update_equations",
    "input_and_masking",
    "parameter_semantics",
    "initial_state_semantics",
    "observation_quantity",
    "precision_mode",
}


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p2a_comparison", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_input_was_frozen_before_comparison():
    manifest = json.loads(INPUT_MANIFEST.read_text(encoding="utf-8"))
    payload = INPUT.read_bytes()

    assert manifest["freeze_status"] == "FROZEN_BEFORE_EXECUTION"
    assert manifest["protocol_id"] == "hgfx-paper-protocol-1"
    assert manifest["comparator"]["package"] == "pyhgf"
    assert manifest["comparator"]["version"] == "0.3.2"
    assert (
        manifest["comparator"]["sdist_sha256"]
        == "8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d"
    )
    assert (
        manifest["comparator"]["git_commit"]
        == "ccd43db5ee5abe4a5a35077d098e53cce2c070c2"
    )
    assert manifest["inputs"][0]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert manifest["tolerance"] == {"absolute": 1e-8, "relative": 1e-7}


def test_semantic_gate_is_explicit_and_complete():
    generator = load_generator()
    mapping = generator.build_semantic_mapping(ROOT)

    assert mapping["protocol_id"] == "hgfx-paper-protocol-1"
    assert mapping["comparator"]["version"] == "0.3.2"
    assert set(mapping["criteria"]) == EXPECTED_GATE_CRITERIA
    assert all(mapping["criteria"][name]["status"] == "PASS" for name in EXPECTED_GATE_CRITERIA)
    assert all(mapping["criteria"][name]["evidence"] for name in EXPECTED_GATE_CRITERIA)
    assert mapping["semantic_gate"] == "PASS"


def test_common_scope_comparison_is_executed_after_gate():
    generator = load_generator()
    outputs = generator.build_outputs(ROOT)
    result = outputs["result"]

    assert result["semantic_gate"] == "PASS"
    assert result["executed"] is True
    assert result["classification"] in {"PASS", "NUMERICAL_MISMATCH"}
    assert result["case_id"] == "P2A-BINARY3-FORWARD-001"
    assert result["n_trials"] == 64
    assert result["precision"] == "float64"
    assert set(result["metrics"]) >= {
        "binary_expected_mean",
        "level2_expected_mean",
        "level2_posterior_mean",
        "level3_expected_mean",
        "level3_posterior_mean",
        "binary_surprise",
    }
    for metric in result["metrics"].values():
        assert set(metric) >= {"max_abs_error", "max_rel_error", "allclose"}


def test_generated_matrix_is_neutral_and_traceable():
    generator = load_generator()
    outputs = generator.build_outputs(ROOT)
    matrix = outputs["matrix"]

    required_axes = [
        "Primary design goal",
        "Relation to MATLAB HGF Toolbox",
        "Model representation / extensibility",
        "Fitting / model-comparison workflow",
        "Differentiability / JAX integration",
        "CPU / GPU execution",
        "Recovery / validation evidence",
        "Reproducibility / provenance",
        "Packaging / documentation",
    ]
    for axis in required_axes:
        assert axis in matrix

    assert "first/only" not in matrix.lower()
    assert "generally superior" not in matrix.lower()
    assert "NOT_DIRECTLY_COMPARABLE" in matrix
    assert "Evidence" in matrix


def test_committed_outputs_match_generator():
    generator = load_generator()
    outputs = generator.build_outputs(ROOT)

    expected = {
        ROOT / "paper" / "tables" / "pyhgf_common_scope_comparison.md": outputs["matrix"],
        ROOT / "paper" / "evidence" / "p2a" / "pyhgf_common_scope_result.json": (
            json.dumps(outputs["result"], indent=2, sort_keys=True) + "\n"
        ),
        ROOT / "paper" / "reproducibility" / "pyhgf_semantic_mapping.json": (
            json.dumps(outputs["semantic_mapping"], indent=2, sort_keys=True) + "\n"
        ),
        ROOT / "paper" / "reproducibility" / "p2a_output_manifest.json": (
            json.dumps(outputs["manifest"], indent=2, sort_keys=True) + "\n"
        ),
    }

    for path, expected_text in expected.items():
        assert path.is_file(), str(path)
        assert path.read_text(encoding="utf-8") == expected_text, str(path)
