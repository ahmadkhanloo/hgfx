from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from hgfx.diagnostics.horizon import (
    PROTOCOL,
    TRIAL_HORIZONS,
    classify_horizon_evidence,
    parameter_check_flags,
)


REPO = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_frozen_grid() -> None:
    assert PROTOCOL == "m18c2-trial-horizon-identifiability-1"
    assert TRIAL_HORIZONS == (128, 256, 512, 1024)


def test_classification_rules() -> None:
    fail256 = {"convergence_rate": False, "median_correlation": True, "median_standardized_rmse": True}
    pass1024 = {"convergence_rate": True, "median_correlation": True, "median_standardized_rmse": True}
    fail1024 = dict(fail256)
    assert classify_horizon_evidence(
        paired_integrity_pass=True, checks_256=fail256, checks_1024=pass1024
    ) == "DATA_HORIZON_LIMITATION_SUPPORTED"
    assert classify_horizon_evidence(
        paired_integrity_pass=True, checks_256=fail256, checks_1024=fail1024
    ) == "PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED"
    assert classify_horizon_evidence(
        paired_integrity_pass=False, checks_256=fail256, checks_1024=pass1024
    ) == "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"
    assert classify_horizon_evidence(
        paired_integrity_pass=True, checks_256=pass1024, checks_1024=pass1024
    ) == "NO_256_FAILURE_TO_EXPLAIN"


def test_parameter_check_flags() -> None:
    flags = parameter_check_flags(
        {"convergence_rate": 0.9, "median_correlation": 0.6, "median_standardized_rmse": 0.4}
    )
    assert flags == {
        "convergence_rate": True,
        "median_correlation": True,
        "median_standardized_rmse": True,
    }


def test_build_shard_rejects_unfrozen_horizon() -> None:
    prepare = _load(REPO / "scripts" / "prepare_m18c2_horizon_shard.py", "prepare_m18c2")
    with pytest.raises(ValueError, match="trial count"):
        prepare.build_shard("hgf_binary", 64, 0.15)


def test_build_shard_frozen_512_contract() -> None:
    prepare = _load(REPO / "scripts" / "prepare_m18c2_horizon_shard.py", "prepare_m18c2")
    shard = prepare.build_shard("hgf_binary", 512, 0.15)
    assert shard["protocol"] == PROTOCOL
    assert len(shard["parameter_cases"]) == 6
    assert len(shard["model_cases"]) == 3
    assert shard["parameter_cases"][0]["seed"] == 18018 + 1500 + 100 * 512
    again = prepare.build_shard("hgf_binary", 512, 0.15)
    assert shard["shard_sha256"] == again["shard_sha256"]


def test_workflow_contains_full_matrix() -> None:
    text = (REPO / ".github" / "workflows" / "pv1-01-m18c2-horizon.yml").read_text(encoding="utf-8")
    for trials in (128, 256, 512, 1024):
        assert f"trials: {trials}" in text
    for model in ("hgf_binary", "ehgf_binary", "uhgf_binary"):
        assert model in text
    assert "workflow_dispatch" in text
    assert "matlab-actions/setup-matlab@v2" in text
