"""Inventory pinned study snapshots without executing or translating their code.

Run from the checkout root. Downloaded sources remain in ignored local_only.
The inventory covers external MATLAB symbols (tapas/VBA/spirl/combined models),
not a static proof of MATLAB dynamic-call closure. Unresolved means unresolved.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / 'paper/case_studies'
PAIN_SHA = '3f1d32aff73826a1385c359ca638ad0e11a7fda7'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_record(root, relative):
    path = root / relative
    return {'path': relative, 'status': 'PRESENT' if path.is_file() else 'MISSING',
            'sha256': digest(path) if path.is_file() else None}


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def audit():
    root = CASES / 'local_only/pain_2025'
    actual = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != PAIN_SHA:
        raise ValueError(f'Wrong Pain snapshot: {actual}')
    if subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip():
        raise ValueError('Pain source checkout is modified')
    paths = subprocess.check_output(['git', '-C', str(root), 'ls-files'], text=True).splitlines()
    out = CASES / 'pain_2025'
    out.mkdir(exist_ok=True)
    inputs = [input_record(root, x) for x in ['sourcedata/participants.csv', 'sourcedata/iasta.csv', 'sourcedata/pcs.csv', 'sourcedata/bdi.csv', 'participants.tsv']]
    trials = []
    for folder in sorted((root / 'sourcedata').glob('sub-*')):
        candidates = sorted(p for p in folder.iterdir() if 'PainUncertainty' in p.name and '.csv' in p.name)
        row = {'subject': folder.name[:7], 'folder': folder.name, 'task_files': len(candidates), 'retained_trials': None, 'source_excluded': folder.name[:7] in ['sub-055', 'sub-059']}
        if len(candidates) == 1:
            with candidates[0].open(encoding='utf-8-sig', newline='') as stream:
                task = list(csv.DictReader(stream))
            row['retained_trials'] = sum(bool(r.get('block_name')) and bool(r.get('stimulus_')) for r in task)
        trials.append(row)
    files = [{'path': p, 'sha256': digest(root / p), 'bytes': (root / p).stat().st_size, 'redistribute': False} for p in paths]
    manifest = {'schema_version': 1, 'checked_date': '2026-11-04', 'source_url': 'https://github.com/meganel-t/painuncertainty', 'commit': actual, 'decision': 'BLOCKED_UNLICENSED_CUSTOM_RESPONSE_AND_UNRESOLVED_ENVIRONMENT', 'original_environment': 'ORIGINAL_ENVIRONMENT_UNRESOLVED', 'input_checks': inputs, 'trial_inventory': trials, 'files': files}
    (out / 'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    # Map every external namespace symbol found in all MATLAB sources, including
    # quoted function handles and simulation names. Builtins are MATLAB runtime.
    oracle = {p.stem: p for p in (ROOT / 'external/hgf-toolbox').rglob('*.m') if '_original_models' not in p.parts}
    upstream = {p.stem: p for p in root.rglob('*.m')}
    declarations = {}
    for path in root.rglob('*.m'):
        first = path.read_text(encoding='utf-8').splitlines()[0]
        match = re.search(r'(?:=\s*|function\s+)([A-Za-z]\w*)\s*\(', first)
        if match:
            declarations[match.group(1)] = path
    symbols = {}
    for path in root.rglob('*.m'):
        content = '\n'.join(line.split('%', 1)[0] for line in path.read_text(encoding='utf-8').splitlines())
        for symbol in re.findall(r"\b(?:tapas_|VBA_)[A-Za-z0-9_]+(?=\s*\(|['\"])", content):
            symbols.setdefault(symbol, set()).add(path.relative_to(root).as_posix())
    rows = []
    for symbol, callers in sorted(symbols.items()):
        local = upstream.get(symbol) or declarations.get(symbol)
        candidate = oracle.get(symbol) or oracle.get(symbol.removeprefix('tapas_'))
        status = 'DECLARED_NAME_FILENAME_MISMATCH' if local and symbol != local.stem else 'LOCAL_SOURCE_LICENSE_REVIEW_REQUIRED' if local else 'UNPINNED_VBA' if symbol.startswith('VBA_') else 'ORACLE_CANDIDATE_NOT_HISTORICAL_EQUIVALENCE' if candidate else 'MISSING'
        rows.append({'symbol': symbol, 'callers': ';'.join(sorted(callers)), 'upstream_path': local.relative_to(root).as_posix() if local else '', 'oracle_8_2_candidate': candidate.relative_to(ROOT).as_posix() if candidate else '', 'status': status, 'historical_version': 'UNRESOLVED'})
    write_csv(out / 'dependency_inventory.csv', rows)
    print(json.dumps({'files': len(files), 'source_folders': len(trials), 'input_checks': inputs, 'external_symbols': len(rows)}, indent=2))


if __name__ == '__main__':
    audit()
