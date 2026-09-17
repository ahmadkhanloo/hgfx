from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper" / "scripts" / "generate_p2_tables.py"
EXPECTED_TABLES = {
    "model_workflow_coverage.md",
    "matlab_demo_parity.md",
    "fitting_statistics_classification.md",
    "recovery_model_selection.md",
    "backend_gpu_applicability.md",
    "release_reproducibility_provenance.md",
}


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p2_tables", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_tables_preserves_negative_evidence_and_traceability():
    generator = load_generator()
    tables, manifest = generator.build_outputs(ROOT)

    assert set(tables) == EXPECTED_TABLES
    joined = "\n".join(tables.values())
    assert "REFERENCE_LIMITATION_MATCH" in joined
    assert "FAIL_PRESERVED" in joined
    assert "D02" in joined and "D08" in joined
    assert "36/36" in joined
    assert "Tesla T4" in joined

    for name, text in tables.items():
        assert "Evidence" in text, name
        assert "|" in text, name

    assert manifest["protocol_id"] == "hgfx-paper-protocol-1"
    assert manifest["hgfx_release_commit"] == "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
    assert manifest["matlab_reference_commit"] == "2437f4dc241541072722a2695ddeca7b44d83dd3"
    assert set(manifest["outputs"]) == EXPECTED_TABLES
    assert manifest["inputs"]
    assert all(item["sha256"] for item in manifest["inputs"])


def test_missing_required_input_fails_loudly(tmp_path: Path):
    generator = load_generator()
    (tmp_path / "reference" / "validation" / "v1_release").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        generator.build_outputs(tmp_path)


def test_output_is_deterministic():
    generator = load_generator()
    tables_a, manifest_a = generator.build_outputs(ROOT)
    tables_b, manifest_b = generator.build_outputs(ROOT)
    assert tables_a == tables_b
    assert json.dumps(manifest_a, sort_keys=True) == json.dumps(manifest_b, sort_keys=True)


def test_committed_tables_match_generator():
    generator = load_generator()
    tables, _ = generator.build_outputs(ROOT)
    for name, text in tables.items():
        path = ROOT / "paper" / "tables" / name
        assert path.is_file(), name
        assert path.read_text(encoding="utf-8") == text, name
