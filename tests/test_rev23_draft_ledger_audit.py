"""Read-only draft 44-cell gate assertions: never infer scientific eligibility."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "rev23_draft_ledger_audit", ROOT / "tools/rev23_draft_ledger_audit.py")
assert SPEC is not None and SPEC.loader is not None
audit_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_tool)

DRAFT = ROOT / "evidence/revision/REV-2.3_ELIGIBILITY_MATRIX_DRAFT.json"


@pytest.fixture
def ledger():
    return json.loads(DRAFT.read_text(encoding="utf-8"))


def assert_blocked(ledger, expected: str):
    result = audit_tool.audit(ledger)
    assert result["status"] == "BLOCKED_DRAFT_LEDGER"
    assert result["timing_authorized"] is False
    assert any(expected in e for e in result["errors"]), result["errors"]


def test_repo_draft_44_cell_contract_is_structurally_intact(ledger):
    result = audit_tool.audit(ledger)
    assert result["status"] == "DRAFT_STRUCTURE_CHECK_PASS", result["errors"]
    assert result["workloads_seen"] == 11
    assert result["cells_seen"] == 44
    assert result["scientific_validation"] == "NOT_EVALUATED"
    assert result["timing_authorized"] is False


def test_no_silent_workload_drop(ledger):
    ledger["workloads"] = ledger["workloads"][:-1]
    assert_blocked(ledger, "11 workload IDs")


def test_no_duplicate_favorable_cell(ledger):
    ledger["cells"][-1] = copy.deepcopy(ledger["cells"][0])
    assert_blocked(ledger, "44-cell denominator")


def test_no_silent_trial_reduction(ledger):
    ledger["workloads"][3]["trials"] = 8192
    assert_blocked(ledger, "scope changed")


def test_no_unauthorized_model_switch(ledger):
    next(w for w in ledger["workloads"] if w["id"] == "S128")["model"] = "ehgf_binary"
    assert_blocked(ledger, "original fit model changed")


def test_unapproved_forward_model_not_frozen(ledger):
    next(w for w in ledger["workloads"] if w["id"] == "F128")["model"] = "hgf_binary"
    assert_blocked(ledger, "author choice inserted")


def test_d08_family_cannot_change(ledger):
    next(w for w in ledger["workloads"] if w["id"] == "D08")["observation"] = "unitsq_sgm"
    assert_blocked(ledger, "original family changed")


def test_no_unreviewed_eligibility_pass(ledger):
    ledger["cells"][0]["eligibility"] = "PASS"
    assert_blocked(ledger, "premature eligibility promotion")


def test_no_inserted_timing(ledger):
    ledger["cells"][0]["timed_values_seconds"] = [1.1, 1.2]
    assert_blocked(ledger, "draft timing values must be empty")


def test_no_pretend_gpu_proof(ledger):
    ledger["cells"][3]["host_id"] = "mock-gpu"
    assert_blocked(ledger, "unsupported host_id")


def test_no_gate_override(ledger):
    ledger["perf01c_gate"] = "PASS"
    assert_blocked(ledger, "PERF-01C gate changed")


def test_no_protocol_repeat_change(ledger):
    ledger["study_repetition_policy"]["timed_repeats"] = 20
    assert_blocked(ledger, "repetition/precision")


def test_no_fake_frozen_source(ledger):
    ledger["source_versions"]["matlab_toolbox_commit"] = "000000"
    assert_blocked(ledger, "frozen reference commit changed")


def test_root_must_be_json_object():
    assert_blocked([], "root must be object")
