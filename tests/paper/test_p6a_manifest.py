from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper" / "scripts" / "generate_p6a_manifest.py"
OUTPUT = ROOT / "paper" / "reproducibility" / "p6a_paper_evidence_manifest.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p6a_manifest", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p6a_draft_manifest_is_deterministic_and_not_frozen() -> None:
    generator = load_generator()
    first = generator.build(ROOT)
    second = generator.build(ROOT)
    assert first == second

    assert first["status"] == "DRAFT_NOT_FROZEN"
    assert first["submission_candidate_sha"] is None
    assert first["claim_audit_status"] == "PENDING_P6A_2"
    assert first["freeze_policy"]["separate_from_m19"] is True
    assert first["freeze_policy"]["requires_independent_p8_pass"] is True
    assert first["anchors"]["hgfx_v1_0_0_sha"] == "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
    assert first["anchors"]["matlab_hgf_toolbox_8_2_0_sha"] == "2437f4dc241541072722a2695ddeca7b44d83dd3"
    assert first["anchors"]["p3_aggregate_sha256"] == "83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4"

    classes = first["classifications"]
    assert classes["historical_m18_scientific_validation"] == "FAIL_PRESERVED"
    assert classes["d02_fitting"] == "REFERENCE_LIMITATION_MATCH"
    assert classes["d08_fitting_holdout"] == "REFERENCE_LIMITATION_MATCH"
    assert classes["s7_parameter_recovery"] == "REFERENCE_LIMITATION_MATCH"
    assert classes["pyhgf_participant_response_nll"] == "NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY"
    assert classes["p3_trial_horizon"] == "INSUFFICIENT_REFERENCE_EVIDENCE"
    assert classes["p3_gate_pass"] is False

    paths = {item["path"] for item in first["files"]}
    assert "paper/figures/fig_p3_horizon_diagnostics.png" in paths
    assert "paper/figures/fig_p3_horizon_diagnostics.pdf" in paths
    assert "paper/manuscript.md" in paths
    assert "paper/scripts/generate_p6a_manifest.py" in paths
    assert len([p for p in paths if p.startswith("paper/figures/") and p.endswith(".png")]) == 6
    assert len([p for p in paths if p.startswith("paper/figures/") and p.endswith(".pdf")]) == 6


def test_committed_p6a_manifest_matches_generator() -> None:
    generator = load_generator()
    expected = generator.build(ROOT)
    committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert committed == expected


def test_p6a_freeze_guard_rejects_unsigned_p8() -> None:
    generator = load_generator()
    with pytest.raises(RuntimeError, match="P6A freeze refused"):
        generator.build(
            ROOT,
            status="FROZEN_FOR_SUBMISSION",
            candidate_sha="0" * 40,
        )
