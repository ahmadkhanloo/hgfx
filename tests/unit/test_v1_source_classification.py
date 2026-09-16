from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "check_v1_source_classification.py"
MANIFEST = ROOT / "reference" / "matlab_manifest.tsv"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_v1_source_classification", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_frozen_matlab_sources_have_release_classification() -> None:
    checker = _load_checker()
    records = checker.classify_manifest(MANIFEST)

    assert len(records) == 334
    assert {record.status for record in records} <= {
        "DONE",
        "PLOT_ONLY",
        "DEPRECATED",
        "NOT_APPLICABLE",
    }
    assert all(record.evidence for record in records)
    assert not [record.path for record in records if record.status == "REFERENCE_ONLY"]


def test_scientific_model_sources_remain_done() -> None:
    checker = _load_checker()
    records = checker.classify_manifest(MANIFEST)
    scientific = [
        record
        for record in records
        if record.path.startswith(("perceptual/", "observation/"))
    ]

    assert scientific
    assert all(record.status == "DONE" for record in scientific)
