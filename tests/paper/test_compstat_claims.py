"""Targeted REV-0.4 claim-audit tests (no JAX or MATLAB required)."""

import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "check_manuscript_claims.py"


def _setup(tmp_path):
    (tmp_path / "paper" / "computational_statistics").mkdir(parents=True)
    (tmp_path / "docs" / "planning").mkdir(parents=True)
    (tmp_path / "evidence").mkdir()
    (tmp_path / "paper" / "computational_statistics" / "manuscript.md").write_text(
        "The trial recovered 36/36 and a rate of 0.583.\n", encoding="utf-8"
    )
    (tmp_path / "evidence" / "values.json").write_text(
        json.dumps({"matches": 36, "total": 36, "rate": 0.5833333333333334}),
        encoding="utf-8",
    )
    registry = {
        "claims": [
            {"id": "pair", "source": "paper/computational_statistics/manuscript.md",
             "phrase": "36/36", "evidence": "evidence/values.json",
             "values": [{"pointer": "/matches"}, {"pointer": "/total"}]},
            {"id": "rate", "source": "paper/computational_statistics/manuscript.md",
             "phrase": "0.583", "evidence": "evidence/values.json",
             "values": [{"pointer": "/rate", "decimal_places": 3}]},
        ]
    }
    (tmp_path / "docs" / "planning" / "COMPSTAT_CLAIM_MAP.json").write_text(
        json.dumps(registry), encoding="utf-8"
    )


def _run(tmp_path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path),
         "--source", "paper/computational_statistics/manuscript.md", *args],
        capture_output=True, text=True, check=False,
    )


def test_partial_inventory_and_strict_behavior(tmp_path):
    _setup(tmp_path)
    inventory = _run(tmp_path, "--allow-unmapped", "--json-out", str(tmp_path / "report.json"))
    assert inventory.returncode == 0, inventory.stderr
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["sources"]["paper/computational_statistics/manuscript.md"]["mapped"] == 3
    assert report["unmapped_count"] == 0
    assert report["status"] == "COVERED"
    assert _run(tmp_path).returncode == 0


def test_wrong_value_never_passes_even_in_inventory(tmp_path):
    _setup(tmp_path)
    path = tmp_path / "evidence" / "values.json"
    path.write_text(json.dumps({"matches": 35, "total": 36, "rate": 0.5833333333333334}))
    result = _run(tmp_path, "--allow-unmapped")
    assert result.returncode != 0
    assert "36 != evidence 35" in result.stderr


def test_unmapped_values_fail_strict_but_are_listed_in_inventory(tmp_path):
    _setup(tmp_path)
    path = tmp_path / "paper" / "computational_statistics" / "manuscript.md"
    path.write_text(path.read_text(encoding="utf-8") + "Unmapped 182 seconds.\n")
    assert _run(tmp_path).returncode != 0
    inventory = _run(tmp_path, "--allow-unmapped")
    assert inventory.returncode == 0
    assert "UNMAPPED" in inventory.stdout


def test_sha256_pin_detects_altered_evidence_even_when_values_match(tmp_path):
    import hashlib
    _setup(tmp_path)
    source = tmp_path / "evidence" / "values.json"
    registry_file = tmp_path / "docs" / "planning" / "COMPSTAT_CLAIM_MAP.json"
    registry = json.loads(registry_file.read_text(encoding="utf-8"))
    registry["claims"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    registry_file.write_text(json.dumps(registry), encoding="utf-8")
    source.write_bytes(source.read_bytes() + b"\n")
    result = _run(tmp_path, "--allow-unmapped")
    assert result.returncode != 0
    assert "evidence SHA-256 changed" in result.stderr
