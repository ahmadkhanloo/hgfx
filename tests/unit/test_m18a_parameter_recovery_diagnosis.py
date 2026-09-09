from __future__ import annotations

import numpy as np

from hgfx.diagnostics.parameter_recovery_diagnosis import (
    diagnose_parameter_recovery_dataset,
    fit_restricted_binary_variant,
    profile_parameter_at_truth,
    recovery_parameter_metadata,
)
from hgfx.diagnostics.recovery import (
    _truth_vector,
    deterministic_binary_inputs,
    simulate_binary_variant,
)
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


def test_recovery_parameter_metadata_names_the_three_m18_parameters() -> None:
    inputs = deterministic_binary_inputs(32, 181801)
    metadata = recovery_parameter_metadata("hgf_binary", inputs)

    assert [item.role for item in metadata] == [
        "perceptual",
        "perceptual",
        "observation",
    ]
    assert [item.transformed_name for item in metadata] == [
        "om[1]",
        "om[2]",
        "logze",
    ]
    np.testing.assert_allclose(
        [item.prior_mean for item in metadata],
        [-3.0, -6.0, np.log(48.0)],
    )


def test_restricted_fit_keeps_nonselected_parameters_at_truth() -> None:
    inputs = deterministic_binary_inputs(32, 181802)
    truth_full, _, _ = _truth_vector(
        "hgf_binary",
        inputs,
        replicate=0,
        scale=0.35,
    )
    responses, _ = simulate_binary_variant(
        "hgf_binary",
        inputs,
        truth_full,
        seed=181803,
    )
    metadata = recovery_parameter_metadata("hgf_binary", inputs)
    target = metadata[0]

    fit = fit_restricted_binary_variant(
        responses,
        inputs,
        "hgf_binary",
        base_full=truth_full,
        optimized_full_indices=(target.full_index,),
        initial_values=(target.prior_mean,),
        options=QuasiNewtonOptions(max_iter=2),
    )

    mask = np.ones(truth_full.size, dtype=bool)
    mask[target.full_index] = False
    np.testing.assert_allclose(fit.final_full[mask], truth_full[mask], atol=0.0, rtol=0.0)
    assert np.isfinite(fit.objective.neg_log_joint)


def test_profile_reports_finite_likelihood_and_joint_curves() -> None:
    inputs = deterministic_binary_inputs(32, 181804)
    truth_full, _, _ = _truth_vector(
        "hgf_binary",
        inputs,
        replicate=1,
        scale=0.35,
    )
    responses, _ = simulate_binary_variant(
        "hgf_binary",
        inputs,
        truth_full,
        seed=181805,
    )
    parameter = recovery_parameter_metadata("hgf_binary", inputs)[0]

    profile = profile_parameter_at_truth(
        responses,
        inputs,
        "hgf_binary",
        truth_full,
        parameter,
        points=9,
    )

    assert profile.grid.shape == (9,)
    assert np.all(np.isfinite(profile.neg_log_likelihood))
    assert np.all(np.isfinite(profile.neg_log_joint))
    assert profile.likelihood_span >= 0.0
    assert profile.joint_span >= 0.0


def test_dataset_diagnosis_exposes_baseline_truth_start_oracle_and_profiles() -> None:
    result = diagnose_parameter_recovery_dataset(
        model="hgf_binary",
        trial_count=32,
        replicate=0,
        seed=181806,
        truth_scale=0.35,
        options=QuasiNewtonOptions(max_iter=2),
        profile_points=7,
    )

    assert result.truth_free.shape == (3,)
    assert result.baseline_free.shape == (3,)
    assert result.truth_start_free.shape == (3,)
    assert result.oracle_single_free.shape == (3,)
    assert result.perceptual_oracle_free.shape == (3,)
    assert len(result.profiles) == 3
    assert np.isfinite(result.baseline_neg_log_joint)
    assert np.isfinite(result.truth_start_neg_log_joint)
