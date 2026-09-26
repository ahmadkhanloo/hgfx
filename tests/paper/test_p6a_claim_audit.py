from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper" / "scripts" / "generate_p6a_claim_audit.py"
OUTPUT = ROOT / "paper" / "reproducibility" / "p6a_claim_audit.json"
MANIFEST = ROOT / "paper" / "reproducibility" / "p6a_paper_evidence_manifest.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p6a_claim_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p6a2_claim_audit_is_complete_and_deterministic() -> None:
    generator = load_generator()
    first = generator.build(ROOT)
    second = generator.build(ROOT)
    assert first == second
    assert first["status"] == "COMPLETE_P6A_2_NOT_FROZEN"
    assert first["claim_count"] == 46
    assert first["explicit_exemption_count"] == 10
    assert first["unmapped_numeric_lines"] == []
    assert set(first["machine_checks"].values()) == {"PASS"}


def test_claim_evidence_is_inside_p6a_manifest() -> None:
    audit = json.loads(OUTPUT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_paths = {item["path"] for item in manifest["files"]}
    for claim in audit["claims"]:
        assert claim["evidence"], claim["id"]
        assert set(claim["evidence"]) <= manifest_paths, claim["id"]


def test_committed_claim_audit_matches_generator() -> None:
    generator = load_generator()
    expected = generator.build(ROOT)
    committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert committed == expected
