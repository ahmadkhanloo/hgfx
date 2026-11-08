"""REV-1.3 unit tests; no source-data download, simulation or fitting."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[2] / "tools" / "audit_compstat_warnings.py"
spec = importlib.util.spec_from_file_location("compstat_warning_audit", PATH)
assert spec is not None and spec.loader is not None
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_grouping_separates_events_and_warning_blocks():
    rows = [
        {"study": "reed_2020", "arm": "804020", "ignored_trials": 1, "warnings": 3},
        {"study": "reed_2020", "arm": "804020", "ignored_trials": 1, "warnings": 1},
        {"study": "reed_2020", "arm": "905010", "ignored_trials": 0, "warnings": 0},
    ]
    grouped = audit.table(rows, ("arm",))
    assert len(grouped) == 2
    x = next(r for r in grouped if r["arm"] == "804020")
    assert x == {"arm": "804020", "blocks": 2, "warning_blocks": 2,
                 "warning_events": 4, "ignored_trials_total": 2}
    assert sum(r["blocks"] for r in grouped) == 3


def test_first_missing_index_none_is_not_zero():
    rows = [
        {"first_ignored_index_zero_based": None, "ignored_trials": 0, "warnings": 0},
        {"first_ignored_index_zero_based": 0, "ignored_trials": 1, "warnings": 1},
        {"first_ignored_index_zero_based": 0, "ignored_trials": 2, "warnings": 3},
    ]
    grouped = audit.table(rows, ("first_ignored_index_zero_based",))
    assert len(grouped) == 2
    assert {r["first_ignored_index_zero_based"]: r["warning_events"] for r in grouped} == {
        None: 0, 0: 4
    }


def test_archived_statuses_reject_invalid_hash(tmp_path):
    path = tmp_path / "historical.zip"
    path.write_bytes(b"not historical original bytes")
    with pytest.raises(ValueError, match="historical Actions ZIP SHA-256 mismatch"):
        audit.archived_statuses(path)


def test_reed_masks_reject_unpinned_input(tmp_path):
    path = tmp_path / "IRL_Data.mat"
    path.write_bytes(b"not Reed pinned MAT")
    with pytest.raises(ValueError, match="original Reed source bytes differ"):
        audit.reed_masks(path, [])


def test_negative_warning_count_rejected_in_ledger_group():
    rows = [{"study": "reed_2020", "ignored_trials": 1, "warnings": 1},
            {"study": "suthaharan_2021", "ignored_trials": 0, "warnings": 0}]
    result = audit.table(rows, ("study",))
    assert sum(x["warning_events"] for x in result) == 1
    assert sum(x["warning_blocks"] for x in result) == 1
