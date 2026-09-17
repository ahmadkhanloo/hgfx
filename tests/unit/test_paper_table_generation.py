from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "paper" / "scripts" / "generate_core_tables.py"
TABLES = (
    "model_workflow_coverage.md",
    "official_matlab_demo_parity.md",
    "fitting_statistics_classification.md",
    "recovery_model_selection.md",
    "backend_gpu_applicability.md",
    "release_reproducibility_provenance.md",
)
MANIFEST = "core_tables_manifest.json"


def _load_generator():
    assert GENERATOR.exists(), f"missing P2 generator: {GENERATOR}"
    spec = importlib.util.spec_from_file_location("hgfx_paper_tables", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generator_fails_loudly_when_required_evidence_is_absent(tmp_path: Path) -> None:
    generator = _load_generator()
    with pytest.raises(FileNotFoundError):
        generator.generate_tables(tmp_path, tmp_path / "tables")


def test_generator_preserves_negative_and_scoped_evidence(tmp_path: Path) -> None:
    generator = _load_generator()
    out_dir = tmp_path / "tables"
    manifest = generator.generate_tables(ROOT, out_dir)

    assert set(manifest["outputs"]) == set(TABLES)
    assert manifest["integrity"]["historical_m18_fail_visible"] is True
    assert manifest["integrity"]["d02_direct_fail_visible"] is True
    assert manifest["integrity"]["d08_direct_fail_visible"] is True
    assert manifest["integrity"]["reference_limitation_visible"] is True

    fitting = (out_dir / "fitting_statistics_classification.md").read_text(encoding="utf-8")
    assert "D02" in fitting
    assert "D08" in fitting
    assert "FAIL_PRESERVED" in fitting
    assert "REFERENCE_LIMITATION_MATCH" in fitting

    recovery = (out_dir / "recovery_model_selection.md").read_text(encoding="utf-8")
    assert "M18 historical scientific gate" in recovery
    assert "FAIL_PRESERVED" in recovery
    assert "PASS_PAIRED_MODEL_SELECTION" in recovery
    assert "36/36" in recovery

    backend = (out_dir / "backend_gpu_applicability.md").read_text(encoding="utf-8")
    assert "2x Tesla T4" in backend
    assert "PASS_PHYSICAL_GPU_APPLICABILITY" in backend
    assert "correctness/applicability only" in backend
    assert "does not establish speed or scaling" in backend


def test_generator_emits_hash_manifest(tmp_path: Path) -> None:
    generator = _load_generator()
    out_dir = tmp_path / "tables"
    generator.generate_tables(ROOT, out_dir)

    payload = json.loads((out_dir / MANIFEST).read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["protocol_id"] == "hgfx-paper-protocol-1"
    assert payload["hgfx_product"]["tag"] == "v1.0.0"
    assert payload["hgfx_product"]["source_sha"] == "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
    assert payload["matlab_reference"]["source_sha"] == "2437f4dc241541072722a2695ddeca7b44d83dd3"
    assert payload["inputs"]
    assert all(len(item["sha256"]) == 64 for item in payload["inputs"])
    assert all(len(item["sha256"]) == 64 for item in payload["output_hashes"])


def test_committed_tables_match_deterministic_regeneration(tmp_path: Path) -> None:
    generator = _load_generator()
    out_dir = tmp_path / "tables"
    generator.generate_tables(ROOT, out_dir)

    committed = ROOT / "paper" / "tables"
    for name in (*TABLES, MANIFEST):
        assert (out_dir / name).read_bytes() == (committed / name).read_bytes(), name
