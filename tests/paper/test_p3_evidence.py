from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGGREGATE = ROOT / "paper" / "reproducibility" / "p3_m18c2_aggregate_35272347167.json"
PROVENANCE = ROOT / "paper" / "reproducibility" / "p3_m18c2_provenance_35272347167.json"

EXPECTED_SHA256 = "83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4"
EXPECTED_PROTOCOL = "m18c2-trial-horizon-identifiability-1"


def test_p3_aggregate_is_hash_verified_and_classified() -> None:
    payload = AGGREGATE.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == EXPECTED_SHA256

    aggregate = json.loads(payload)
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))

    assert aggregate["protocol"] == EXPECTED_PROTOCOL
    assert aggregate["overall_classification"] == "INSUFFICIENT_REFERENCE_EVIDENCE"
    assert aggregate["gate_pass"] is False
    assert aggregate["historical_m18_unchanged"] is True
    assert aggregate["coverage"]["shards"] == aggregate["coverage"]["expected_shards"] == 24
    assert aggregate["coverage"]["model_cases"] == aggregate["coverage"]["expected_model_cases"] == 72
    assert aggregate["coverage"]["parameter_cases"] == aggregate["coverage"]["expected_parameter_cases"] == 144

    assert provenance["protocol_id"] == EXPECTED_PROTOCOL
    assert provenance["workflow_run"] == 35272347167
    assert provenance["artifact_id"] == 10521838356
    assert provenance["aggregate_sha256"] == EXPECTED_SHA256
    assert provenance["overall_classification"] == aggregate["overall_classification"]
    assert provenance["gate_pass"] is False
    assert provenance["historical_m18_unchanged"] is True
