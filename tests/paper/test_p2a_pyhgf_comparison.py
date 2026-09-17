from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper" / "scripts" / "generate_p2a_pyhgf_comparison.py"
SPEC = ROOT / "paper" / "comparison" / "pyhgf_comparison_spec.json"
TABLE = ROOT / "paper" / "tables" / "pyhgf_feature_design_matrix.md"
SEMANTIC = ROOT / "paper" / "comparison" / "pyhgf_semantic_mapping.json"
MANIFEST = ROOT / "paper" / "comparison" / "p2a_manifest.json"

REQUIRED_DIMENSIONS = {
    "primary_design_goal",
    "matlab_toolbox_relation",
    "network_construction",
    "model_coverage_extensibility",
    "fitting_model_comparison",
    "differentiability_jax",
    "accelerator_support",
    "recovery_evidence",
    "reproducibility_provenance",
    "packaging_documentation",
}

REQUIRED_SEMANTIC_CHECKS = {
    "model_structure",
    "update_equations",
    "input_and_masking",
    "parameter_semantics",
    "initial_state_semantics",
    "observation_response_quantity",
    "precision_mode",
}


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p2a_pyhgf_comparison", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p2a_spec_pins_exact_pyhgf_release_and_primary_sources():
    payload = json.loads(SPEC.read_text(encoding="utf-8"))
    comparator = payload["comparator"]
    assert comparator["package"] == "pyhgf"
    assert comparator["version"] == "0.3.2"
    assert comparator["git_tag"] == "v0.3.2"
    assert comparator["git_commit"] == "ccd43db5ee5abe4a5a35077d098e53cce2c070c2"
    assert comparator["sdist_sha256"] == (
        "8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d"
    )
    assert payload["protocol_id"] == "hgfx-paper-protocol-1"
    assert payload["primary_sources"]
    assert all(source["url"].startswith("https://") for source in payload["primary_sources"])


def test_p2a_feature_matrix_and_semantic_gate_are_complete_and_neutral():
    generator = load_generator()
    outputs, manifest = generator.build_outputs(ROOT)

    assert set(outputs) == {
        "paper/tables/pyhgf_feature_design_matrix.md",
        "paper/comparison/pyhgf_semantic_mapping.json",
    }
    table = outputs["paper/tables/pyhgf_feature_design_matrix.md"]
    semantic = json.loads(outputs["paper/comparison/pyhgf_semantic_mapping.json"])

    assert REQUIRED_DIMENSIONS == set(manifest["feature_dimensions"])
    assert REQUIRED_SEMANTIC_CHECKS == set(semantic["checks"])
    assert semantic["classification"] in {
        "PASS_FOR_COMMON_SCOPE",
        "NOT_DIRECTLY_COMPARABLE",
    }
    assert semantic["candidate_surface"] == "fixed_parameter_three_level_binary_hgf_forward"
    assert semantic["empirical_comparison_permitted"] == (
        semantic["classification"] == "PASS_FOR_COMMON_SCOPE"
    )

    lower = table.lower()
    assert "first python" not in lower
    assert "only python" not in lower
    assert "generally superior" not in lower
    assert "generally faster" not in lower
    assert "evidence" in lower
    assert "not_directly_comparable" in outputs["paper/comparison/pyhgf_semantic_mapping.json"].lower()


def test_p2a_outputs_are_deterministic_and_match_committed_files():
    generator = load_generator()
    outputs_a, manifest_a = generator.build_outputs(ROOT)
    outputs_b, manifest_b = generator.build_outputs(ROOT)
    assert outputs_a == outputs_b
    assert json.dumps(manifest_a, sort_keys=True) == json.dumps(manifest_b, sort_keys=True)

    for relative, text in outputs_a.items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert path.read_text(encoding="utf-8") == text, relative

    assert MANIFEST.is_file()
    committed_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert committed_manifest == manifest_a
    assert all(item["sha256"] for item in committed_manifest["inputs"])
    assert all(item["sha256"] for item in committed_manifest["outputs"])
