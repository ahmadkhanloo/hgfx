from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper/scripts/check_p7_submission.py"


def load_preflight():
    spec = importlib.util.spec_from_file_location("check_p7_submission", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p7_jnm_preflight_has_only_author_email_blocker() -> None:
    module = load_preflight()
    report = module.build(ROOT)

    assert report["status"] == "BLOCKED_AUTHOR_INPUT"
    assert report["errors"] == []
    assert report["blockers"] == ["MISSING_CORRESPONDING_AUTHOR_EMAIL"]
    assert report["corresponding_author_email_present"] is False

    assert report["abstract_word_count"] <= 250
    assert report["keyword_count"] <= 6
    assert 3 <= report["highlight_count"] <= 5
    assert all(item["length"] <= 85 for item in report["highlights"])
    assert report["unresolved_bibliography_keys"] == []
