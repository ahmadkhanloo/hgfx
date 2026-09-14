"""D08 diagnostic must separate input preparation from prior arithmetic."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture
def diagnostic(monkeypatch):
    monkeypatch.syspath_prepend(str(Path('tools').resolve()))
    spec = importlib.util.spec_from_file_location(
        'd08_prior_diagnostic', Path('tools/check_m18_d08_prior_terms.py')
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_real_prior_mismatch_is_first_an_input_mismatch(diagnostic, tmp_path):
    output = tmp_path / 'comparison.json'
    diagnostic.main(Path('reference/validation/m18_d08_prior/reference.json'), output)
    result = json.loads(output.read_text())
    assert result['classification'] == 'PRIOR_INPUT_DIVERGENCE'
    assert not result['inputs']['variances']['exact']
    assert result['matched_input_replay']['combined_terms']['exact']
    assert result['matched_input_replay']['total']['exact']


def test_diagnostic_does_not_broadcast_partial_arrays(diagnostic):
    with pytest.raises(ValueError, match='length'):
        diagnostic.array_cmp([1.0], [1.0, 1.0])


def test_missing_placeholder_trace_is_unavailable(diagnostic):
    assert diagnostic.compare_placeholder([1.0, 2.0], None) == {'status': 'UNAVAILABLE'}


def test_partial_placeholder_trace_is_rejected(diagnostic):
    with pytest.raises(KeyError):
        diagnostic.compare_placeholder([1.0, 2.0], {'window': [1.0, 2.0]})
