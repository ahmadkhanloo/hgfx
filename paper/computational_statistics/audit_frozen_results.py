"""Re-describe retained results without fitting or changing historical gates."""
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent


def classify_rows(parameter_rows, model_rows):
    invalid = [r for r in parameter_rows if r['hgfx'].get('error') == 'SIMULATION_INVALID_TRAJECTORY'
               and r['matlab'].get('error_message') == 'SIMULATION_INVALID_TRAJECTORY']
    contract = [r for r in parameter_rows if not r['diagnostic']['contract_free_indices_match']]
    absent = [r for r in model_rows if not r['matlab_selected_model'] and not r['hgfx_selected_model']]
    different = [r for r in model_rows if r['matlab_selected_model'] and r['hgfx_selected_model']
                 and r['matlab_selected_model'] != r['hgfx_selected_model']]
    asymmetric = [r for r in parameter_rows if r['matlab']['success'] != r['hgfx']['success']]
    return {
        'parameter_cases': len(parameter_rows), 'model_cases': len(model_rows),
        'shared_invalid_simulations': len(invalid), 'contract_flag_false': len(contract),
        'successful_pair_index_mismatches': sum(r['diagnostic']['both_success'] for r in contract),
        'both_winners_absent': len(absent), 'different_nonempty_winners': len(different),
        'matching_nonempty_winners': sum(bool(r['matlab_selected_model']) and r['matlab_selected_model'] == r['hgfx_selected_model'] for r in model_rows),
        'asymmetric_parameter_cases': [{
            'case_id': r['case_id'], 'matlab_success_flag': r['matlab']['success'],
            'matlab_negLj': str(r['matlab']['negLj']), 'hgfx_error': r['hgfx'].get('error'),
            'first_stage': 'initial objective admissibility, before optimizer',
            'first_divergent_trial_level_state': 'not recorded by historical runner',
        } for r in asymmetric],
        'historical_gate_changed': False,
    }


def main():
    evidence = HERE / 'evidence'
    inventory = json.loads((evidence / 'acquisition.json').read_text())
    parameter_rows, model_rows = [], []
    for record in inventory:
        path = evidence / record['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith('comparison.json'):
                    data = json.loads(archive.read(name))
                    parameter_rows.extend(data['parameter_results'])
                    model_rows.extend(data['model_results'])
    assert len({r['case_id'] for r in parameter_rows}) == len(parameter_rows) == 144
    assert len({r['case_id'] for r in model_rows}) == len(model_rows) == 72
    result = classify_rows(parameter_rows, model_rows)
    (evidence / 'p3_diagnostic_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    with zipfile.ZipFile(evidence / 's7_aggregate.zip') as archive:
        s7 = json.loads(archive.read('aggregate.json'))
    (evidence / 's7_aggregate.json').write_text(json.dumps(s7, indent=2)+'\n', encoding='utf-8', newline='\n')
    lines = ['| Model | Parameter | r MATLAB / HGFX | sRMSE MATLAB / HGFX |', '|---|---|---|---|']
    for model in ['hgf_binary', 'ehgf_binary', 'uhgf_binary']:
        for j, name in enumerate(['omega2', 'omega3', 'log zeta']):
            m, h = [s7['parameter_recovery'][model][key] for key in ['matlab', 'hgfx']]
            lines.append(f"| {model.replace('_binary', '')} | {name} | {m['correlation'][j]:.6f} / {h['correlation'][j]:.6f} | {m['standardized_rmse'][j]:.6f} / {h['standardized_rmse'][j]:.6f} |")
    (evidence / 's7_parameter_table.md').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
