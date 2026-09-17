from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "paper" / "scripts" / "generate_core_tables.py"
TABLE_DIR = ROOT / "paper" / "tables"
EXPECTED_STEMS = {
    "model_workflow_coverage",
    "official_demo_parity",
    "fitting_statistics_classification",
    "recovery_model_selection",
    "backend_gpu_applicability",
    "release_reproducibility_provenance",
}


def run_check() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_core_table_generator_check_passes() -> None:
    result = run_check()
    assert result.returncode == 0, result.stdout + result.stderr


def test_exactly_six_core_table_pairs_are_committed() -> None:
    markdown = {path.stem for path in TABLE_DIR.glob("*.md")}
    csv_files = {path.stem for path in TABLE_DIR.glob("*.csv")}
    assert markdown == EXPECTED_STEMS
    assert csv_files == EXPECTED_STEMS


def test_generated_tables_preserve_negative_and_reference_limitation_evidence() -> None:
    fitting = (TABLE_DIR / "fitting_statistics_classification.md").read_text(encoding="utf-8")
    recovery = (TABLE_DIR / "recovery_model_selection.md").read_text(encoding="utf-8")

    assert "D02_fit" in fitting
    assert "D08" in fitting
    assert "FAIL_PRESERVED" in fitting
    assert "REFERENCE_LIMITATION_MATCH" in fitting

    assert "M18_HISTORICAL_SCIENTIFIC" in recovery
    assert "FAIL_PRESERVED" in recovery
    assert "REFERENCE_LIMITATION_MATCH" in recovery
    assert "PASS_PAIRED_MODEL_SELECTION" in recovery
    assert "36/36" in recovery


def test_generated_manifest_tracks_all_table_outputs() -> None:
    manifest_path = TABLE_DIR / "core_tables_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "GENERATED_FROM_FROZEN_EVIDENCE"
    assert set(manifest["tables"]) == EXPECTED_STEMS
    for stem in EXPECTED_STEMS:
        outputs = manifest["tables"][stem]["outputs"]
        assert set(outputs) == {"markdown", "csv"}
        assert len(outputs["markdown"]["sha256"]) == 64
        assert len(outputs["csv"]["sha256"]) == 64
