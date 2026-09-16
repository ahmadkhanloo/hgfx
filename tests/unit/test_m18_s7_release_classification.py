import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "classify_m18_s7_release",
    ROOT / "tools" / "classify_m18_s7_release.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def _aggregate():
    checks = {
        "hgf_binary": {
            "convergence_rate": True,
            "median_correlation": False,
            "median_standardized_rmse": False,
        },
        "ehgf_binary": {
            "convergence_rate": True,
            "median_correlation": False,
            "median_standardized_rmse": False,
        },
        "uhgf_binary": {
            "convergence_rate": False,
            "median_correlation": False,
            "median_standardized_rmse": False,
        },
    }
    return {
        "protocol": "m18-s7-paired-recovery-1",
        "criteria": {
            "convergence_rate_min": 0.8,
            "median_correlation_min": 0.5,
            "median_standardized_rmse_max": 1.0,
            "model_balanced_accuracy_min": 0.5,
        },
        "coverage": {
            "shards": 12,
            "parameter_cases": 72,
            "unique_parameter_cases": 72,
            "model_cases": 36,
            "unique_model_cases": 36,
        },
        "coverage_pass": True,
        "parameter_classification": "PAIRED_REFERENCE_LIMITATION_REVIEW_REQUIRED",
        "parameter_recovery": {
            model: {
                "classification": "PAIRED_REFERENCE_LIMITATION_CANDIDATE",
                "matlab": {"complete": True, "scientific_pass": False, "checks": pattern.copy()},
                "hgfx": {"complete": True, "scientific_pass": False, "checks": pattern.copy()},
            }
            for model, pattern in checks.items()
        },
        "model_recovery": {
            "classification": "PASS_PAIRED_MODEL_SELECTION",
            "winner_matches": 36,
            "total_cases": 36,
            "all_winners_match": True,
            "matlab_balanced_accuracy": 0.5833333333333334,
            "hgfx_balanced_accuracy": 0.5833333333333334,
            "mismatched_cases": [],
        },
        "s7_classification": "REFERENCE_LIMITATION_REVIEW_REQUIRED",
        "gate_pass": False,
    }


def _decision():
    return {
        "protocol": "m18-s7-paired-recovery-1",
        "decision": "REFERENCE_LIMITATION_MATCH",
        "status": "RELEASE_ACCEPTABLE_EXACT_PROTOCOL_SCOPE",
        "scientific_pass": False,
        "product_equivalence_closed": True,
        "reference_commit": "2437f4dc241541072722a2695ddeca7b44d83dd3",
        "coverage": {
            "shards": 12,
            "parameter_cases": 72,
            "model_recovery_datasets": 36,
            "models": ["hgf_binary", "ehgf_binary", "uhgf_binary"],
        },
        "criteria_unchanged": {
            "convergence_rate_min": 0.8,
            "median_correlation_min": 0.5,
            "median_standardized_rmse_max": 1.0,
            "model_balanced_accuracy_min": 0.5,
        },
        "parameter_recovery": {
            "hgf_binary": {
                "classification": "REFERENCE_LIMITATION_MATCH",
                "shared_failed_criteria": ["median_correlation", "median_standardized_rmse"],
            },
            "ehgf_binary": {
                "classification": "REFERENCE_LIMITATION_MATCH",
                "shared_failed_criteria": ["median_correlation", "median_standardized_rmse"],
            },
            "uhgf_binary": {
                "classification": "REFERENCE_LIMITATION_MATCH",
                "shared_failed_criteria": [
                    "convergence_rate",
                    "median_correlation",
                    "median_standardized_rmse",
                ],
            },
        },
        "model_recovery": {
            "classification": "PASS_PAIRED_MODEL_SELECTION",
            "winner_matches": 36,
            "total_cases": 36,
            "matlab_balanced_accuracy": 0.5833333333333334,
            "hgfx_balanced_accuracy": 0.5833333333333334,
            "mismatched_cases": [],
        },
        "evidence_integrity": {
            "unresolved_required_scope_implementation_mismatch": False,
            "unresolved_required_scope_optimizer_mismatch": False,
            "unresolved_required_scope_model_selection_mismatch": False,
        },
    }


def test_accepts_frozen_reference_limitation_without_scientific_pass():
    result = MOD.classify_release(_aggregate(), _decision())
    assert result["release_gate_pass"] is True
    assert result["release_classification"] == "REFERENCE_LIMITATION_MATCH"
    assert result["scientific_pass"] is False
    assert result["raw_gate_pass"] is False
    assert result["failures"] == []


def test_rejects_changed_scientific_criteria():
    decision = _decision()
    decision["criteria_unchanged"]["median_correlation_min"] = 0.49
    result = MOD.classify_release(_aggregate(), decision)
    assert result["release_gate_pass"] is False
    assert any("criteria" in failure for failure in result["failures"])


def test_rejects_hgfx_only_check_pattern():
    aggregate = _aggregate()
    aggregate["parameter_recovery"]["hgf_binary"]["hgfx"]["checks"]["convergence_rate"] = False
    result = MOD.classify_release(aggregate, _decision())
    assert result["release_gate_pass"] is False
    assert any("check pattern" in failure for failure in result["failures"])


def test_rejects_model_selection_mismatch():
    aggregate = _aggregate()
    aggregate["model_recovery"]["winner_matches"] = 35
    aggregate["model_recovery"]["all_winners_match"] = False
    aggregate["model_recovery"]["mismatched_cases"] = ["case-x"]
    result = MOD.classify_release(aggregate, _decision())
    assert result["release_gate_pass"] is False
    assert any("model recovery" in failure for failure in result["failures"])
