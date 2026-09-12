from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from hgfx.diagnostics.recovery import (
    BINARY_VARIANTS,
    ModelRecoveryRecord,
    ParameterRecoveryRecord,
    deterministic_binary_inputs,
    fit_binary_variant,
    model_recovery_matrix,
    simulate_binary_variant,
    summarize_parameter_recovery,
)
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


def test_m18_validation_matrix_tracks_all_unified_binary_recovery_variants() -> None:
    matrix_path = Path(__file__).resolve().parents[2] / "benchmarks" / "m18_validation_matrix.json"
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))

    gate = payload["m18_gate"]
    assert tuple(gate["parameter_recovery_models"]) == BINARY_VARIANTS
    assert tuple(gate["model_recovery_candidates"]) == BINARY_VARIANTS
    assert gate["demo_parity_required"] is True
    assert gate["matlab_limitation_register_required"] is True

    policy = payload["limitation_policy"]
    assert policy["matlab_limitations_are_acceptable"] is True
    assert policy["must_document_equivalent_hgfx_behavior"] is True
    assert policy["must_not_claim_stronger_scientific_identifiability_than_reference"] is True
    assert policy["model_substitution_must_follow_reference_workflow"] is True


def test_parameter_recovery_summary_reports_bias_rmse_correlation_and_failures() -> None:
    records = [
        ParameterRecoveryRecord(
            model="hgf_binary",
            trial_count=64,
            truth_scale=0.2,
            replicate=i,
            seed=i,
            true_free=np.array([float(i), float(2 * i)]),
            fitted_free=np.array([float(i) + 0.1, float(2 * i) - 0.2]),
            error=np.array([0.1, -0.2]),
            neg_log_joint=1.0,
            converged=i != 2,
            termination="tol_arg" if i != 2 else "max_iter",
        )
        for i in range(4)
    ]
    summary = summarize_parameter_recovery(records)

    np.testing.assert_allclose(summary.bias, [0.1, -0.2], atol=1e-12)
    np.testing.assert_allclose(summary.rmse, [0.1, 0.2], atol=1e-12)
    np.testing.assert_allclose(summary.median_absolute_error, [0.1, 0.2], atol=1e-12)
    np.testing.assert_allclose(summary.correlation, [1.0, 1.0], atol=1e-12)
    assert summary.convergence_rate == 0.75


def test_model_recovery_matrix_is_row_normalized() -> None:
    rows = [
        ModelRecoveryRecord(
            generating_model="hgf_binary",
            selected_model="hgf_binary",
            trial_count=64,
            truth_scale=0.2,
            replicate=0,
            seed=1,
            bic_by_model={},
            aic_by_model={},
        ),
        ModelRecoveryRecord(
            generating_model="hgf_binary",
            selected_model="ehgf_binary",
            trial_count=64,
            truth_scale=0.2,
            replicate=1,
            seed=2,
            bic_by_model={},
            aic_by_model={},
        ),
        ModelRecoveryRecord(
            generating_model="ehgf_binary",
            selected_model="ehgf_binary",
            trial_count=64,
            truth_scale=0.2,
            replicate=0,
            seed=3,
            bic_by_model={},
            aic_by_model={},
        ),
    ]
    matrix = model_recovery_matrix(
        rows,
        models=("hgf_binary", "ehgf_binary", "uhgf_binary"),
    )
    np.testing.assert_allclose(matrix[0], [0.5, 0.5, 0.0])
    np.testing.assert_allclose(matrix[1], [0.0, 1.0, 0.0])
    np.testing.assert_allclose(matrix[2], [0.0, 0.0, 0.0])


def test_recovery_fitter_can_fit_a_simulated_hgf_dataset() -> None:
    inputs = deterministic_binary_inputs(32, 1818)
    # Fit once to obtain the exact resolved default full vector, then use it
    # as a valid simulation point. This keeps the smoke test deterministic
    # without duplicating placeholder semantics.
    seed_responses = np.tile(np.array([0.0, 1.0]), 16)
    seed_fit = fit_binary_variant(
        seed_responses,
        inputs,
        "hgf_binary",
        options=QuasiNewtonOptions(max_iter=1),
    )
    responses, probabilities = simulate_binary_variant(
        "hgf_binary",
        inputs,
        seed_fit.initial_full,
        seed=1819,
    )
    assert responses.shape == (32,)
    assert probabilities.shape == (32,)
    assert np.all(np.isfinite(probabilities))

    result = fit_binary_variant(
        responses,
        inputs,
        "hgf_binary",
        options=QuasiNewtonOptions(max_iter=2),
    )
    assert np.isfinite(result.objective.neg_log_joint)
    assert np.isfinite(result.aic)
    assert np.isfinite(result.bic)
    assert result.final_free.shape == (len(result.free_indices),)
