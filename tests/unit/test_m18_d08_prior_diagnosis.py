"""D08 diagnostic must separate input preparation from prior arithmetic."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from hgfx.core.placeholders import compute_placeholder_values


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


def test_usdchf_placeholder_variance_matches_frozen_matlab_exactly():
    # First 20 values of frozen demo/example_usdchf.txt.  MATLAB fitModel uses
    # var(u(1:20,1),1), whose scalar squared-deviation reduction is one ULP
    # above NumPy's vectorized np.var result for this exact window.
    window = np.asarray(
        [
            1.0357,
            1.0319,
            1.0359,
            1.0343,
            1.0303,
            1.0328,
            1.0311,
            1.0326,
            1.0247,
            1.0245,
            1.0175,
            1.0178,
            1.0184,
            1.0189,
            1.0241,
            1.0259,
            1.0262,
            1.0265,
            1.0286,
            1.0398,
        ],
        dtype=np.float64,
    )
    placeholders = compute_placeholder_values(window)
    assert placeholders.var_first_20 == np.float64(4.0624875000000105e-05)
    assert placeholders.log_var_first_20 == np.float64(-10.11112999424218)


def test_diagnostic_does_not_broadcast_partial_arrays(diagnostic):
    with pytest.raises(ValueError, match='length'):
        diagnostic.array_cmp([1.0], [1.0, 1.0])


def test_missing_placeholder_trace_is_unavailable(diagnostic):
    assert diagnostic.compare_placeholder([1.0, 2.0], None) == {'status': 'UNAVAILABLE'}


def test_partial_placeholder_trace_is_rejected(diagnostic):
    with pytest.raises(KeyError):
        diagnostic.compare_placeholder([1.0, 2.0], {'window': [1.0, 2.0]})
