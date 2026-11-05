"""Ensure absent winners cannot be reported as two different selected models."""
import importlib.util
from pathlib import Path


def test_absent_winners_and_failed_indices_are_distinct():
    path = Path(__file__).resolve().parents[2] / 'paper/computational_statistics/audit_frozen_results.py'
    spec = importlib.util.spec_from_file_location('audit', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pair = {'matlab': {'success': False, 'error_message': 'SIMULATION_INVALID_TRAJECTORY'},
            'hgfx': {'success': False, 'error': 'SIMULATION_INVALID_TRAJECTORY'},
            'diagnostic': {'contract_free_indices_match': False, 'both_success': False}}
    result = module.classify_rows([pair], [
        {'matlab_selected_model': '', 'hgfx_selected_model': ''},
        {'matlab_selected_model': 'hgf', 'hgfx_selected_model': 'ehgf'},
        {'matlab_selected_model': 'hgf', 'hgfx_selected_model': 'hgf'}])
    assert result['both_winners_absent'] == result['different_nonempty_winners'] == result['matching_nonempty_winners'] == 1
    assert result['contract_flag_false'] == 1
    assert result['successful_pair_index_mismatches'] == 0


def test_empirical_figure_uses_entire_recorded_series():
    import json
    import numpy as np
    root = Path(__file__).resolve().parents[2] / 'paper/computational_statistics'
    spec = importlib.util.spec_from_file_location('figures', root / 'generate_figures.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inputs = np.loadtxt(root / 'empirical_example/example_usdchf.txt')
    result = json.loads((root / 'empirical_example/result.json').read_text())
    figure = module.empirical_workflow(result, inputs)
    np.testing.assert_array_equal(figure.axes[0].lines[0].get_ydata(), inputs)
    np.testing.assert_array_equal(figure.axes[0].lines[1].get_ydata(), np.asarray(result['muhat'])[:, 0])
    assert len(inputs) == 614
