"""Checks for source-only auditing and separate agreement/accuracy displays."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'paper/computational_statistics' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inventory_does_not_resolve_missing_input_by_basename(tmp_path):
    audit = load_script('audit_case_sources')
    (tmp_path / 'participants.tsv').write_text('id\n1\n')
    assert audit.input_record(tmp_path, 'sourcedata/participants.csv')['status'] == 'MISSING'
    assert audit.input_record(tmp_path, 'participants.tsv')['status'] == 'PRESENT'


def test_agreement_and_accuracy_have_distinct_panels():
    figures = load_script('generate_figures')
    decision = json.loads((ROOT / 'reference/validation/m18_s7_reference_limitation/decision.json').read_text())
    fig = figures.model_selection(decision)
    assert len(fig.axes) == 2
    assert fig.axes[0].patches[0].get_height() == 1
    assert len(fig.axes[0].lines) == 0
    assert [p.get_height() for p in fig.axes[1].patches] == [decision['model_recovery'][k] for k in ['matlab_balanced_accuracy', 'hgfx_balanced_accuracy']]
    assert fig.axes[1].lines[0].get_ydata()[0] == decision['criteria_unchanged']['model_balanced_accuracy_min']


def test_pyhgf_residual_uses_all_frozen_trials():
    import numpy as np
    figures = load_script('generate_figures')
    raw = json.loads((ROOT / 'paper/reproducibility/p2a10_raw_numeric_result_35268575414.json').read_text())
    fig = figures.pyhgf_trajectories(raw)
    expected = np.asarray(raw['hgfx']['fields']['level_2_posterior_mean']) - np.asarray(raw['pyhgf']['fields']['level_2_posterior_mean'])
    np.testing.assert_array_equal(fig.axes[2].lines[0].get_ydata(), expected)
    np.testing.assert_array_equal(fig.axes[2].lines[0].get_xdata(), np.arange(1, 129))


def test_candidate_builder_binds_caption_to_image():
    builder = load_script('build_submission')
    source = builder.source_text('manuscript.md')
    assert source.count('\\begin{minipage}') == 4
    assert source.count('\\captionof{figure}') == 4
    assert 'Figure 1](figures/' not in source
    assert 'Bibliography entries are in' not in source
