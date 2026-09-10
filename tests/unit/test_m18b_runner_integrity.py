"""Verify durable failure evidence and that interrupted runs cannot claim PASS."""
import importlib.util
import json
from pathlib import Path
import pytest


def runner():
    path = Path(__file__).resolve().parents[2] / 'scripts/run_m18b_identifiability_validation.py'
    spec = importlib.util.spec_from_file_location('m18b_runner', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failed_cells_are_archived_without_resampling(monkeypatch, tmp_path):
    m = runner()
    out = tmp_path / 'failure.json'
    monkeypatch.setattr('sys.argv', ['runner', '--preset', 'ci', '--output', str(out)])
    def fail(**kwargs):
        raise FloatingPointError('synthetic forward failure')
    monkeypatch.setattr(m, 'diagnose_parameter_recovery_dataset', fail)
    with pytest.raises(SystemExit) as exc:
        m.main()
    assert exc.value.code == 2
    result = json.loads(out.read_text())
    assert result['status'] == 'completed'
    assert len(result['failures']) == 6
    assert result['records'] == []
    assert result['gate']['pass'] is False
    assert result['gate']['checks']['execution_complete'] is False
    assert result['gate']['checks']['final_gate_preset'] is False
    assert len({(r['model'],r['trial_count'],r['replicate']) for r in result['failures']}) == 6


def test_interrupt_leaves_an_incomplete_nonpassing_artifact(monkeypatch, tmp_path):
    m = runner()
    out = tmp_path / 'interrupted.json'
    monkeypatch.setattr('sys.argv', ['runner', '--preset', 'gate', '--output', str(out)])
    def interrupt(**kwargs):
        raise KeyboardInterrupt
    monkeypatch.setattr(m, 'diagnose_parameter_recovery_dataset', interrupt)
    with pytest.raises(KeyboardInterrupt):
        m.main()
    result = json.loads(out.read_text())
    assert result['status'] == 'incomplete'
    assert result['gate']['pass'] is False
