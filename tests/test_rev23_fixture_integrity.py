"""Source-only negative/positive controls for REV-2.3 fixture preflight.

All data are synthetic parser-test bytes created in tmp_path, NOT benchmark
fixtures or MATLAB/HGFX scientific validation; no model function is imported.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "rev23_fixture_integrity.py"
SPEC = importlib.util.spec_from_file_location("rev23_fixture_integrity", MODULE)
assert SPEC and SPEC.loader
rev23 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rev23)


def _file_entry(path: Path, root: Path) -> dict[str, str]:
    return {
        "path": str(path.relative_to(root)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


@pytest.fixture
def manifest(tmp_path: Path) -> tuple[Path, dict]:
    """Create dummy arrays solely to exercise a file-validation contract."""
    rows = {}
    for ident, (trials, subjects) in rev23.ROWS.items():
        directory = tmp_path / ident
        directory.mkdir()
        shape = (trials,) if subjects == 1 else (subjects, trials)
        inputs = directory / "inputs.npy"
        responses = directory / "responses.npy"
        config = directory / "config.json"
        start = directory / "start.npy"
        np.save(inputs, np.zeros(shape, dtype="<f8"))
        np.save(responses, np.ones(shape, dtype="<f8"))
        config.write_text('{"synthetic":true}', encoding="utf-8")
        np.save(start, np.zeros((2,), dtype="<f8"))
        rows[ident] = {
            "trials": trials,
            "subjects": subjects,
            "model": "uhgf" if ident == "D08" else "hgf_binary",
            "observation": "gaussian_obs" if ident == "D08" else "unitsq_sgm",
            "provenance": "synthetic test data, NOT scientific input",
            "selection_policy": "unit test only",
            **{field: _file_entry(path, tmp_path) for field, path in (
                ("inputs", inputs), ("responses", responses),
                ("config", config), ("start", start)
            )},
        }
    doc = {
        "protocol_id": "compstat-rev23-performance-1",
        "hgfx_source_commit": rev23.EXPECTED_RELEASE,
        "matlab_source_commit": rev23.EXPECTED_ORACLE,
        "workloads": rows,
    }
    file = tmp_path / "manifest.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    return file, doc


def _write(file: Path, doc: dict) -> None:
    file.write_text(json.dumps(doc), encoding="utf-8")


def _blocked(file: Path, expected: str) -> None:
    out = rev23.check(file)
    assert out["status"] == "BLOCKED_FIXTURE_INTEGRITY"
    assert out["benchmark_authorized"] is False
    assert out["scientific_parity"] == "NOT_EVALUATED"
    assert any(expected in error for error in out["errors"]), out["errors"]


def test_all_eleven_synthetic_files_only_pass_integrity(manifest):
    file, _ = manifest
    out = rev23.check(file)
    assert out["status"] == "SOURCE_ONLY_CHECK_PASS"
    assert out["rows_checked"] == 11
    assert out["errors"] == []
    assert out["benchmark_authorized"] is False
    assert out["scientific_parity"] == "NOT_EVALUATED"


def test_missing_workload_cannot_shrink_grid(manifest):
    file, doc = manifest
    del doc["workloads"]["B1024"]
    _write(file, doc)
    _blocked(file, "workload IDs mismatch")


def test_additional_workload_cannot_expand_grid_silently(manifest):
    file, doc = manifest
    doc["workloads"]["B2048"] = copy.deepcopy(doc["workloads"]["B1024"])
    _write(file, doc)
    _blocked(file, "workload IDs mismatch")


def test_changed_trails_and_subject_count_rejected(manifest):
    file, doc = manifest
    doc["workloads"]["F128"]["trials"] = 127
    doc["workloads"]["B256"]["subjects"] = 32
    _write(file, doc)
    _blocked(file, "immutable dimensions changed")


def test_corrupted_file_hash_rejected(manifest):
    file, doc = manifest
    doc["workloads"]["F128"]["inputs"]["sha256"] = "0" * 64
    _write(file, doc)
    _blocked(file, "sha256 mismatch")


def test_wrong_numpy_shape_rejected_even_with_correct_hash(manifest):
    file, doc = manifest
    path = file.parent / doc["workloads"]["S128"]["inputs"]["path"]
    np.save(path, np.zeros((127,), dtype="<f8"))
    doc["workloads"]["S128"]["inputs"] = _file_entry(path, file.parent)
    _write(file, doc)
    _blocked(file, "shape/dtype invalid")


def test_wrong_numpy_dtype_rejected_even_with_correct_hash(manifest):
    file, doc = manifest
    path = file.parent / doc["workloads"]["B32"]["responses"]["path"]
    np.save(path, np.zeros((32, 256), dtype="<f4"))
    doc["workloads"]["B32"]["responses"] = _file_entry(path, file.parent)
    _write(file, doc)
    _blocked(file, "shape/dtype invalid")


def test_path_traversal_rejected(manifest):
    file, doc = manifest
    doc["workloads"]["F128"]["inputs"]["path"] = "../outside.npy"
    _write(file, doc)
    _blocked(file, "escapes manifest directory")


def test_absolute_path_rejected(manifest):
    file, doc = manifest
    doc["workloads"]["F128"]["inputs"]["path"] = "/tmp/fixture.npy"
    _write(file, doc)
    _blocked(file, "relative path")


def test_matlab_oracle_and_hgfx_release_identity_rejected(manifest):
    file, doc = manifest
    doc["hgfx_source_commit"] = "unknown"
    doc["matlab_source_commit"] = "unknown"
    _write(file, doc)
    _blocked(file, "released HGFX source commit")
    _blocked(file, "frozen MATLAB source commit")


def test_default_matlab_ehgf_vs_hgfx_hgf_mismatch_prevented(manifest):
    file, doc = manifest
    doc["workloads"]["S128"]["model"] = "ehgf_binary"
    _write(file, doc)
    _blocked(file, "original binary HGF/unitsq fit scope")


def test_d08_model_swapping_rejected(manifest):
    file, doc = manifest
    doc["workloads"]["D08"]["model"] = "hgf_binary"
    _write(file, doc)
    _blocked(file, "original model/observation changed")


def test_missing_provenance_rejected(manifest):
    file, doc = manifest
    doc["workloads"]["B32"]["provenance"] = None
    _write(file, doc)
    _blocked(file, "source provenance/selection policy missing")


def test_start_bytes_must_match_real_hash(manifest):
    file, doc = manifest
    path = file.parent / doc["workloads"]["F128"]["start"]["path"]
    with path.open("ab") as stream:
        stream.write(b"extra")
    _write(file, doc)
    _blocked(file, "sha256 mismatch")


def test_invalid_json_config_rejected_even_with_matching_hash(manifest):
    file, doc = manifest
    path = file.parent / doc["workloads"]["F128"]["config"]["path"]
    path.write_text("not JSON", encoding="utf-8")
    doc["workloads"]["F128"]["config"] = _file_entry(path, file.parent)
    _write(file, doc)
    _blocked(file, "invalid JSON config")


def test_invalid_numpy_start_rejected_even_with_matching_hash(manifest):
    file, doc = manifest
    path = file.parent / doc["workloads"]["F128"]["start"]["path"]
    path.write_bytes(b"invalid NPY")
    doc["workloads"]["F128"]["start"] = _file_entry(path, file.parent)
    _write(file, doc)
    _blocked(file, "invalid start .npy")


def test_empty_manifest_fails_closed(tmp_path: Path):
    file = tmp_path / "bad.json"
    file.write_text("{}", encoding="utf-8")
    result = rev23.check(file)
    assert result["status"] == "BLOCKED_FIXTURE_INTEGRITY"
    assert result["benchmark_authorized"] is False
