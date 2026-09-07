from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from hgfx.golden import (
    FixtureValidationError,
    compare_mappings,
    import_matlab_json_fixture,
    load_fixture,
)


def _write_raw_fixture(path: Path) -> None:
    path.mkdir()
    metadata = {
        "hgf_version": "8.2.0",
        "hgf_commit_sha": "2437f4dc241541072722a2695ddeca7b44d83dd3",
        "matlab_version": "test-matlab",
        "fixture_schema_version": 1,
        "model_name": "utility:tapas_logit",
        "response_model_name": "N/A",
        "optimizer_name": "N/A",
        "rng_seed": 0,
    }
    values = {
        "metadata.json": metadata,
        "config.json": {"a": 1.0, "function": "tapas_logit"},
        "input.json": {"x": [0.1, 0.2, 0.5]},
        "expected.json": {"y": [-2.1972245773362196, -1.3862943611198906, 0.0]},
    }
    for name, value in values.items():
        (path / name).write_text(json.dumps(value), encoding="utf-8")


def test_matlab_json_import_and_load_roundtrip(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    canonical = tmp_path / "canonical"
    _write_raw_fixture(raw)
    import_matlab_json_fixture(raw, canonical)
    loaded = load_fixture(canonical)
    np.testing.assert_array_equal(loaded.inputs["x"], np.array([0.1, 0.2, 0.5]))
    np.testing.assert_allclose(
        loaded.expected["y"],
        np.array([-2.1972245773362196, -1.3862943611198906, 0.0]),
        rtol=0,
        atol=0,
    )


def test_diff_reports_first_divergent_trial_and_level() -> None:
    expected = {"traj/mu": np.array([[1.0, 2.0], [3.0, 4.0]])}
    actual = {"traj/mu": np.array([[1.0, 2.0], [3.001, 4.0]])}
    report = compare_mappings(expected, actual, rtol=1e-12, atol=1e-12)
    assert not report.passed
    assert report.first_failure is not None
    assert report.first_failure.field == "traj/mu"
    assert report.first_failure.trial == 2
    assert report.first_failure.level == 1


def test_diff_passes_identical_arrays() -> None:
    report = compare_mappings(
        {"y": np.array([0.0, 1.0, np.nan])},
        {"y": np.array([0.0, 1.0, np.nan])},
        rtol=1e-12,
        atol=1e-12,
    )
    assert report.passed


def test_schema_rejects_missing_provenance(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "metadata.json").write_text(
        json.dumps({"fixture_schema_version": 1}), encoding="utf-8"
    )
    for name in ("config.json", "input.json", "expected.json"):
        (raw / name).write_text("{}", encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="missing required fields"):
        import_matlab_json_fixture(raw, tmp_path / "canonical")
