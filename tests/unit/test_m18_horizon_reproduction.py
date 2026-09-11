"""Protect the historical failure and reject misleading paired evidence."""
import copy
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load('scripts/reproduce_m18_horizon.py')
checker = load('tools/check_m18_horizon.py')


def test_historical_512_prior_rejection_is_finite_precision_jump():
    rows = runner.build_cases((512,))
    assert len(rows) == 18
    first = rows[0]
    assert first['seed'] == 233100
    assert first['status'] == 'rejected'
    info = first['unchecked_python_diagnostic']
    assert info['mu']['all_finite'] and info['pi']['all_finite']
    assert info['mu']['max_jump_ratio'] < 16
    assert info['pi']['max_jump_ratio'] > 16
    assert info['pi']['destination_trial_1based'] == 2
    assert info['pi']['level_1based'] == 2
    assert all(r['status'] == 'valid' for r in rows if r['model'] != 'hgf_binary')


def test_checker_rejects_missing_cases_and_wrong_error():
    p = {'reference_commit': 'test', 'cases': [dict(model='hgf_binary', trials=512,
         replicate=0, seed=233100, point='prior', status='rejected')]}
    m = copy.deepcopy(p)
    m['cases'][0]['error_id'] = 'MATLAB:UndefinedFunction'
    assert checker.compare(p, m)['mismatches']
    m['cases'][0]['error_id'] = 'tapas:hgf:VarApproxInvalid'
    out = checker.compare(p, m)
    assert not out['mismatches'] and not out['complete_raw_parity']
    m['cases'] = []
    with pytest.raises(ValueError, match='Missing cases'):
        checker.compare(p, m)


def test_nonfinite_masks_and_first_divergence():
    a = runner.encode_array([[1., np.nan], [2., np.inf]])
    case = dict(model='hgf_binary', trials=2, replicate=0, seed=1,
                point='prior', status='valid', trajectory={'mu': a})
    p = {'reference_commit': 'test', 'cases': [case]}
    m = copy.deepcopy(p)
    assert checker.compare(p, m)['complete_raw_parity']
    m['cases'][0]['trajectory']['mu']['values'][1][0] += 1
    assert checker.compare(p, m)['mismatches'][0]['first_index_0based'] == [1, 0]
    m = copy.deepcopy(p)
    m['cases'][0]['trajectory']['mu']['posinf'][1][1] = False
    assert checker.compare(p, m)['mismatches']
