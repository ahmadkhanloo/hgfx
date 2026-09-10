"""Adversarial evidence tests; a plausible summary must never override raw data."""
from dataclasses import replace
import pytest
from hgfx.diagnostics.identifiability_validation import (
    IdentifiabilityRecord, EXPECTED_PARAMETERS, evaluate_m18b_gate, summarize_records,
    classify_mechanism,
)
from hgfx.diagnostics.recovery import BINARY_VARIANTS


def good_records():
    return [IdentifiabilityRecord(
        model=m, trial_count=t, replicate=r, seed=1000+100*mi+t+r,
        parameter=p, role='observation' if p == 'logze' else 'perceptual',
        prior_sd=1., baseline_error_sd=.1, truth_start_error_sd=.1,
        oracle_error_sd=.1, perceptual_oracle_error_sd=None if p == "logze" else .1,
        likelihood_profile_offset_sd=.1, joint_profile_offset_sd=.1,
        likelihood_span=2., likelihood_curvature=1.,
        objective_improvement_from_truth_start=.01,
        baseline_termination='tol_grad', truth_start_termination='tol_grad',
        mechanism='low_error_recovery',
    ) for mi,m in enumerate(BINARY_VARIANTS) for t in (32,64)
      for r in range(3) for p in EXPECTED_PARAMETERS]


def gate(rows, **kwargs):
    return evaluate_m18b_gate(records=rows, summary=kwargs.pop('summary', summarize_records(rows)),
        trial_counts=kwargs.pop('trial_counts',(32,64)), replicates=3, **kwargs)


def test_complete_raw_evidence_passes():
    assert gate(good_records())['pass']


def test_empty_raw_records_cannot_pass_with_forged_summary():
    assert not gate([], summary=summarize_records(good_records()))['pass']


@pytest.mark.parametrize('mutation', [
    {'parameter':'wrong'}, {'model':'wrong'}, {'replicate':99},
    {'replicate':True}, {'trial_count':32.0}, {'seed':-1},
    {'baseline_error_sd':float('nan')}, {'baseline_error_sd':-.1},
    {'truth_start_error_sd':float('inf')}, {'oracle_error_sd':float('inf')},
    {'likelihood_span':float('inf')}, {'likelihood_span':-1.},
    {'prior_sd':0.}, {'perceptual_oracle_error_sd':float('nan')},
    {'perceptual_oracle_error_sd':None},
    {'likelihood_curvature':float('inf')}, {'baseline_termination':'invented'},
    {'role':'wrong'}, {'mechanism':'identifiable_recovery'},
])
def test_bad_single_row_is_not_hidden_by_medians(mutation):
    rows=good_records(); rows[0]=replace(rows[0], **mutation)
    assert not gate(rows)['pass']


def test_duplicate_replicate_cannot_replace_missing_evidence():
    rows=good_records(); rows[3:6]=rows[:3]
    assert not gate(rows)['pass']


def test_inconsistent_seeds_within_dataset_fail():
    rows=good_records(); rows[0]=replace(rows[0],seed=99999)
    assert not gate(rows)['pass']


def test_reused_seed_across_replicates_fails():
    rows=good_records()
    rows[3:6]=[replace(x,seed=rows[0].seed) for x in rows[3:6]]
    assert not gate(rows)['pass']


def test_supplied_summary_must_match_raw_records():
    rows=good_records(); summary=summarize_records(rows)
    next(iter(summary.values()))['median_baseline_error_sd']=0.
    assert not gate(rows,summary=summary)['pass']


@pytest.mark.parametrize('trials',[(),(32,32),(0,64),(32.0,64),(True,64)])
def test_invalid_protocol_fails(trials):
    assert not gate(good_records(),trial_counts=trials)['pass']


def test_missing_or_altered_frozen_result_fails(tmp_path):
    p=tmp_path/'m18.json'
    assert not gate(good_records(),frozen_m18_path=p)['pass']
    p.write_text('{"gate":{"pass":false}}')
    assert not gate(good_records(),frozen_m18_path=p)['pass']


def test_low_error_is_not_proof_of_identifiability():
    assert classify_mechanism(baseline_error_sd=.1,truth_start_error_sd=.1,
        oracle_error_sd=.1,likelihood_profile_offset_sd=0.,
        objective_improvement_from_truth_start=0.) == 'low_error_recovery'


def test_observation_cannot_claim_a_perceptual_only_oracle_fit():
    rows=good_records(); rows[2]=replace(rows[2],perceptual_oracle_error_sd=.1)
    assert not gate(rows)['pass']
