from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

import pytest


def _horizon_module():
    spec = importlib.util.find_spec("hgfx.diagnostics.horizon")
    assert spec is not None, "M18C.2 horizon diagnostics module must exist"
    return importlib.import_module("hgfx.diagnostics.horizon")


def _script_module(filename: str, module_name: str):
    path = Path(__file__).resolve().parents[2] / "scripts" / filename
    assert path.exists(), f"required M18C.2 script is missing: {filename}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _checks(*, convergence: bool, correlation: bool, standardized_rmse: bool) -> dict[str, bool]:
    return {
        "convergence_rate": convergence,
        "median_correlation": correlation,
        "median_standardized_rmse": standardized_rmse,
    }


def test_m18c2_protocol_constants_are_frozen_before_execution() -> None:
    horizon = _horizon_module()

    assert horizon.PROTOCOL == "m18c2-trial-horizon-identifiability-1"
    assert horizon.TRIAL_HORIZONS == (128, 256, 512, 1024)
    assert horizon.TRUTH_SCALES == (0.15, 0.35)
    assert horizon.PARAM_REPLICATES == 6
    assert horizon.MODEL_REPLICATES == 3
    assert horizon.CRITERIA == {
        "convergence_rate_min": 0.80,
        "median_correlation_min": 0.50,
        "median_standardized_rmse_max": 1.00,
        "model_balanced_accuracy_min": 0.50,
    }


def test_m18c2_classifies_256_failure_resolved_at_1024_as_data_limited() -> None:
    horizon = _horizon_module()
    matlab = {
        "hgf_binary": {
            256: _checks(convergence=True, correlation=False, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=True, standardized_rmse=True),
        }
    }
    hgfx = {
        "hgf_binary": {
            256: _checks(convergence=True, correlation=False, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=True, standardized_rmse=True),
        }
    }

    result = horizon.classify_horizon_evidence(
        matlab_checks_by_model=matlab,
        hgfx_checks_by_model=hgfx,
        model_winner_match_by_horizon={256: True, 1024: True},
        complete=True,
    )

    assert result["by_model"]["hgf_binary"] == "DATA_HORIZON_LIMITATION_SUPPORTED"
    assert result["overall"] == "DATA_HORIZON_LIMITATION_SUPPORTED"


def test_m18c2_classifies_1024_failure_as_persistent_identifiability_limit() -> None:
    horizon = _horizon_module()
    matlab = {
        "ehgf_binary": {
            256: _checks(convergence=True, correlation=False, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=False, standardized_rmse=True),
        }
    }
    hgfx = {
        "ehgf_binary": {
            256: _checks(convergence=True, correlation=False, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=False, standardized_rmse=True),
        }
    }

    result = horizon.classify_horizon_evidence(
        matlab_checks_by_model=matlab,
        hgfx_checks_by_model=hgfx,
        model_winner_match_by_horizon={256: True, 1024: True},
        complete=True,
    )

    assert (
        result["by_model"]["ehgf_binary"]
        == "PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED"
    )
    assert result["overall"] == "PERSISTENT_IDENTIFIABILITY_LIMITATION_SUPPORTED"


def test_m18c2_withholds_scientific_interpretation_on_paired_criterion_mismatch() -> None:
    horizon = _horizon_module()
    matlab = {
        "uhgf_binary": {
            256: _checks(convergence=True, correlation=False, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=True, standardized_rmse=True),
        }
    }
    hgfx = {
        "uhgf_binary": {
            256: _checks(convergence=True, correlation=True, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=True, standardized_rmse=True),
        }
    }

    result = horizon.classify_horizon_evidence(
        matlab_checks_by_model=matlab,
        hgfx_checks_by_model=hgfx,
        model_winner_match_by_horizon={256: True, 1024: True},
        complete=True,
    )

    assert result["overall"] == "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"
    assert result["scientific_interpretation_allowed"] is False


def test_m18c2_reports_model_selection_mismatch_separately() -> None:
    horizon = _horizon_module()
    checks = {
        "hgf_binary": {
            256: _checks(convergence=True, correlation=False, standardized_rmse=False),
            1024: _checks(convergence=True, correlation=True, standardized_rmse=True),
        }
    }

    result = horizon.classify_horizon_evidence(
        matlab_checks_by_model=checks,
        hgfx_checks_by_model=checks,
        model_winner_match_by_horizon={256: True, 1024: False},
        complete=True,
    )

    assert result["overall"] == "MODEL_SELECTION_MISMATCH"
    assert result["scientific_interpretation_allowed"] is False


def test_m18c2_incomplete_evidence_is_not_interpreted() -> None:
    horizon = _horizon_module()

    result = horizon.classify_horizon_evidence(
        matlab_checks_by_model={},
        hgfx_checks_by_model={},
        model_winner_match_by_horizon={},
        complete=False,
    )

    assert result["overall"] == "INSUFFICIENT_REFERENCE_EVIDENCE"
    assert result["scientific_interpretation_allowed"] is False


def test_m18c2_shard_generator_preserves_frozen_seed_and_case_contract() -> None:
    generator = _script_module(
        "prepare_m18c2_horizon_shard.py", "prepare_m18c2_horizon_shard_test"
    )

    shard = generator.build_shard("hgf_binary", 512, 0.15)
    repeated = generator.build_shard("hgf_binary", 512, 0.15)

    assert shard["protocol"] == "m18c2-trial-horizon-identifiability-1"
    assert shard["shard"] == {"model": "hgf_binary", "trial_count": 512, "truth_scale": 0.15}
    assert len(shard["parameter_cases"]) == 6
    assert len(shard["model_cases"]) == 3
    assert shard["parameter_cases"][0]["seed"] == 70_718
    assert shard["model_cases"][0]["seed"] == 570_718
    assert shard["parameter_cases"][0]["case_id"] == "M18C2-PR-hgf_binary-T512-S0.15-R0"
    assert shard["model_cases"][0]["case_id"] == "M18C2-MR-hgf_binary-T512-S0.15-R0"
    assert len(shard["parameter_cases"][0]["case_sha256"]) == 64
    assert len(shard["shard_sha256"]) == 64
    assert shard["shard_sha256"] == repeated["shard_sha256"]

    # This exact frozen case is known from preflight to enter the HGF
    # trajectory-invalid region. It must remain in the shard unchanged rather
    # than being resampled, dropped, or assigned a replacement seed.
    first = shard["parameter_cases"][0]
    assert first["generation_success"] is False
    assert first["generation_error"]["error_type"] == "ValueError"
    assert "Variational approximation invalid" in first["generation_error"]["message"]
    assert first["y"] == []
    assert first["response_probabilities"] == []


def test_m18c2_shard_generator_rejects_non_frozen_horizon() -> None:
    generator = _script_module(
        "prepare_m18c2_horizon_shard.py", "prepare_m18c2_horizon_shard_invalid_test"
    )

    with pytest.raises(ValueError, match="trial count"):
        generator.build_shard("hgf_binary", 64, 0.15)
