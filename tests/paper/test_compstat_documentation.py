"""Static checks for HGFX publication documentation only; not scientific validation."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper" / "computational_statistics"


def test_review_text_is_readable():
    for relative_path in (
        "docs/superpowers/plans/2026-11-03-published-case-studies.md",
        "paper/computational_statistics/EDITORIAL_REVIEW_FA.md",
        "docs/submissions/2026-11-03_publication_revision_status.md",
    ):
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        assert not re.search(r"\?{4,}", content), relative_path


def test_p3_current_interpretation_does_not_override_historical_gate():
    audit = json.loads((PAPER / "evidence/p3_diagnostic_audit.json").read_text())
    assert audit["both_winners_absent"] == 10
    assert audit["different_nonempty_winners"] == 0
    assert audit["matching_nonempty_winners"] == 62
    assert audit["historical_gate_changed"] is False


def test_manifest_editorial_review_checksum():
    manifest = json.loads((PAPER / "REVISION_MANIFEST.json").read_text())
    file_data = (PAPER / "EDITORIAL_REVIEW_FA.md").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(file_data).hexdigest() == manifest["files"]["EDITORIAL_REVIEW_FA.md"]
