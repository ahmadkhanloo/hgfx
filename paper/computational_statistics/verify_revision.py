"""Local provenance checks; does not confer scientific or author approval."""
from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    baseline = json.loads((HERE / 'baseline_hashes.json').read_text())
    changed = [p for p, expected in baseline['files'].items() if sha(ROOT / p) != expected]
    if changed:
        raise RuntimeError(f'Protected artifacts changed: {changed}')
    text = (HERE / 'manuscript.md').read_text(encoding='utf-8')
    abstract = text.split('## Abstract')[1].split('## 1 Introduction')[0]
    if not 150 <= len(abstract.split()) <= 250:
        raise RuntimeError('Abstract outside checked journal range')
    bibliography = (HERE / 'references.bib').read_text(encoding='utf-8')
    cited = set(re.findall(r'(?<![\w.])@([A-Za-z][\w-]+)', text))
    keys = set(re.findall(r'@\w+\{([^,]+),', bibliography))
    if cited - keys:
        raise RuntimeError(f'Missing citation keys: {cited - keys}')
    ledger = list(csv.DictReader((HERE / 'CLAIM_EVIDENCE.csv').open(encoding='utf-8', newline='')))
    for row in ledger:
        for path, expected in zip(row['artifact/source'].split(';'), row['SHA/run'].split(';'), strict=True):
            if sha(ROOT / path) != expected:
                raise RuntimeError(f'Stale claim source: {row["claim_id"]}: {path}')
        if row['claim'] not in text:
            raise RuntimeError(f'Stale claim text: {row["claim_id"]}')
    paragraphs = [p for p in text.split('\n\n') if len(p.split()) >= 12 and not p.startswith(('##', '```', '$$', '!['))]
    if set(paragraphs) - {row['claim'] for row in ledger}:
        raise RuntimeError('Manuscript paragraphs missing from ledger')
    for name in ['manuscript.md', 'supplement.md', 'references.bib', 'CLAIM_EVIDENCE.csv', 'JOURNAL_POLICY_CHECK.md', 'VENUE_FIT.md', 'EDITORIAL_REVIEW_FA.md', 'cover_letter.md', 'SUBMISSION_CHECKLIST.md', 'EXECUTION_LOG.md', 'package/HGFX_CompStat.pdf', 'package/HGFX_Supplement.pdf', 'package/HGFX_CompStat_source.zip']:
        if not (HERE / name).is_file() or not (HERE / name).stat().st_size:
            raise RuntimeError(f'Missing deliverable: {name}')
    build = json.loads((HERE / 'package/build_manifest.json').read_text())
    for path, expected in build['inputs'].items():
        if sha(HERE / path) != expected:
            raise RuntimeError(f'Stale build input: {path}')
    for path, expected in build['outputs'].items():
        if sha(HERE / 'package' / path) != expected:
            raise RuntimeError(f'Stale package output: {path}')
    rendered_source = (HERE / 'package/HGFX_CompStat.tex').read_text(encoding='utf-8')
    if rendered_source.count('\\begin{tabular}') != 3 or '**Table' in rendered_source:
        raise RuntimeError('Tables missing or unconverted in final editable source')
    figures = json.loads((HERE / 'figures/manifest.json').read_text())
    for path, expected in figures['inputs'].items():
        if sha(ROOT / path) != expected:
            raise RuntimeError(f'Stale figure input: {path}')
    for record in figures['outputs']:
        if sha(ROOT / record['path']) != record['sha256']:
            raise RuntimeError(f'Stale figure output: {record["path"]}')
    with zipfile.ZipFile(HERE / 'package/HGFX_CompStat_source.zip') as archive:
        if archive.testzip() or any('/' in name or '\\' in name for name in archive.namelist()):
            raise RuntimeError('Invalid or non-flat source archive')
    smoke = json.loads((HERE / 'worked_example/result.json').read_text())
    if smoke['hgfx'] != '1.0.0' or not smoke['x64'] or smoke['trials'] != 24 or smoke['status'] != 'PASS_WORKFLOW_ONLY':
        raise RuntimeError('Wrong smoke identity/scope')
    result = {'status': 'PASS_LOCAL_ARTIFACT_CHECKS_ONLY', 'protected_files_unchanged': len(baseline['files']), 'claim_paragraphs': len(ledger), 'abstract_words': len(abstract.split()), 'manuscript_words_including_tables': len(text.split()), 'citation_keys_resolved': len(cited), 'human_verification': 'PENDING', 'real_data_replication': 'BLOCKED', 'zero_fee_clearance': 'OPEN'}
    (HERE / 'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
