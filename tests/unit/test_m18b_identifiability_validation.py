from __future__ import annotations

import numpy as np

from hgfx.diagnostics.identifiability_validation import (
    classify_mechanism,
    evaluate_m18b_gate,
    informative_binary_inputs,
    records_from_diagnosis,
    summarize_records,
    trial_count_trends,
)
from hgfx.diagnostics.parameter_recovery_diagnosis import diagnose_parameter_recovery_dataset
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions


def test_classifier_separates_main_failure_mechanisms() -> None:
    assert classify_mechanism(
        baseline_error_sd=0.8,
        truth_start_error_sd=0.8,
        oracle_error_sd=0.8,
        likelihood_profile_offset_sd=0.7,
        objective_improvement_from_truth_start=0.0,
    ) == "finite_data_likelihood_identifiability"

    assert classify_mechanism(
        baseline_error_sd=0.8,
        truth_start_error_sd=0.8,
        oracle_error_sd=0.2,
        likelihood_profile_offset_sd=0.1,
        objective_improvement_from_truth_start=0.0,
    ) == "cross_parameter_confounding"

    assert classify_mechanism(
        baseline_error_sd=0.8,
        truth_start_error_sd=0.2,
        oracle_error_sd=0.8,
        likelihood_profile_offset_sd=0.1,
        objective_improvement_from_truth_start=0.2,
    ) == "optimizer_start_sensitivity"


def test_records_summary_and_trial_trends_are_structured() -> None:
    diagnoses = [
        diagnose_parameter_recovery_dataset(
            model="hgf_binary",
            trial_count=32,
            replicate=0,
            seed=181901,
            truth_scale=0.35,
            options=QuasiNewtonOptions(max_iter=2),
            profile_points=7,
        ),
        diagnose_parameter_recovery_dataset(
            model="hgf_binary",
            trial_count=48,
            replicate=0,
            seed=181902,
            truth_scale=0.35,
            options=QuasiNewtonOptions(max_iter=2),
            profile_points=7,
        ),
    ]
    records = []
    for diagnosis in diagnoses:
        records.extend(records_from_diagnosis(diagnosis))

    assert len(records) == 6
    assert {row.parameter for row in records} == {"om[1]", "om[2]", "logze"}
    assert all(np.isfinite(row.baseline_error_sd) for row in records)

    summary = summarize_records(records)
    assert len(summary) == 6

    trends = trial_count_trends(summary)
    assert set(trends) == {
        "hgf_binary:om[1]",
        "hgf_binary:om[2]",
        "hgf_binary:logze",
    }


def test_gate_preserves_frozen_m18_semantics() -> None:
    diagnosis = diagnose_parameter_recovery_dataset(
        model="hgf_binary",
        trial_count=32,
        replicate=0,
        seed=181903,
        truth_scale=0.35,
        options=QuasiNewtonOptions(max_iter=2),
        profile_points=7,
    )
    records = records_from_diagnosis(diagnosis)
    summary = summarize_records(records)

    result = evaluate_m18b_gate(
        records=records,
        summary=summary,
        trial_counts=(32,),
        replicates=1,
    )

    assert result["criteria"]["m18_thresholds_may_be_relaxed"] is False
    assert result["checks"]["frozen_m18_result_preserved"] is True


def test_informative_binary_inputs_are_balanced_and_bounded_run() -> None:
    values = informative_binary_inputs(256, 181904)
    assert set(np.unique(values)) == {0.0, 1.0}
    assert 0.40 <= float(np.mean(values)) <= 0.60
    longest = 1
    run = 1
    for i in range(1, values.size):
        run = run + 1 if values[i] == values[i - 1] else 1
        longest = max(longest, run)
    assert longest <= 3
