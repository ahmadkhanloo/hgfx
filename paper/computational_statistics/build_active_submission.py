#!/usr/bin/env python3
"""Build an evidence-preserving CompStat author-review preview (NOT submission approval)."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('paper/computational_statistics/manuscript.md')
ESM = Path('paper/SUPPLEMENTARY_APPENDICES.md')
BIB = Path('paper/references.bib')
CAPTION = re.compile(r'^\*\*Figure (\d+)\.\*\* (.*?) File: \x60paper/figures/([\w-]+)\.png\x60.*$', re.M)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd, log):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       errors='replace', timeout=300)
    with log.open('a', encoding='utf-8') as f:
        f.write('$ ' + ' '.join(args) + '\n' + p.stdout + '\n' + p.stderr + '\n')
    if p.returncode:
        raise RuntimeError(f'{args[0]} returned {p.returncode}; inspect {log}')
    return p.stdout


def build(root, out):
    root, out = root.resolve(), out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    log = out / 'build.log'
    log.write_text('AUTHOR-REVIEW PREVIEW; NO SCIENTIFIC VALIDATION\n', encoding='utf-8')
    main = (root / SOURCE).read_text(encoding='utf-8')
    esm = (root / ESM).read_text(encoding='utf-8')
    bib = (root / BIB).read_text(encoding='utf-8')
    title = main.splitlines()[0].removeprefix('# ').strip()
    abstract = main.split('## Abstract\n', 1)[1].split('## 1 Introduction', 1)[0]
    nwords = len(abstract.split())
    if not 150 <= nwords <= 250:
        raise ValueError(f'abstract outside journal range: {nwords}')
    keyword_matches = re.findall(r'^\*\*Keywords:\*\*\s*(.+?)\s*$', main, re.M)
    if len(keyword_matches) != 1:
        raise ValueError('exactly one manuscript Keywords line is required')
    keywords = [part.strip() for part in keyword_matches[0].split(';')]
    if not 4 <= len(keywords) <= 6 or any(not word for word in keywords):
        raise ValueError(f'journal requires 4-6 non-empty keywords; found {len(keywords)}')
    body = '## Abstract\n' + main.split('## Abstract\n', 1)[1].split('\n## References', 1)[0]
    if body.count('\n## 1 Introduction') != 1:
        raise ValueError('expected one Introduction boundary for keyword insertion')
    body = body.replace('\n## 1 Introduction',
                        '\n\n**Keywords:** ' + '; '.join(keywords) + '\n\n## 1 Introduction', 1)
    heads = [int(x) for x in re.findall(r'^\*\*Table (\d+)\.\*\*', body, re.M)]
    if heads != [1, 2, 3, 4, 5, 6]:
        raise ValueError('six current manuscript tables are required')
    chunk = body.split('\n## Figure captions\n', 1)[1].split('\n## Declaration of generative AI', 1)[0]
    figures = list(CAPTION.finditer(chunk))
    if [int(m[1]) for m in figures] != [1, 2, 3, 4, 5, 6]:
        raise ValueError('six current figure captions must parse in order')
    replacement = '\n\n' + '\n\n'.join(
        f'![{m[2]}](figures/{m[3]}.pdf){{width=82%}}' for m in figures) + '\n\n'
    body = body.replace('\n## Figure captions\n' + chunk, replacement)
    body = ('*Institute for Research in Fundamental Sciences (IPM), Tehran, Iran.*\n\n'
            '*Correspondence: m.ahmadkhanloo@ipm.ir*\n\n' + body)
    keys = set(re.findall(r'@\w+\s*\{([^,\s]+),', bib))
    refs = set(re.findall(r'(?<!\w)@([A-Za-z][\w-]+)', body + '\n' + esm)) - {'ipm'}
    if refs - keys:
        raise ValueError(f'missing bibliography keys: {sorted(refs - keys)}')
    stage = out / 'source'
    (stage / 'figures').mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / BIB, stage / 'references.bib')
    hashes = {str(p): sha(root / p) for p in (SOURCE, ESM, BIB)}
    for m in figures:
        p = Path('paper/figures') / (m[3] + '.pdf')
        hashes[str(p)] = sha(root / p)
        shutil.copy2(root / p, stage / 'figures' / p.name)
    (stage / 'HGFX_Main.md').write_text(body, encoding='utf-8')
    (stage / 'HGFX_ESM.md').write_text(esm.split('\n', 1)[1], encoding='utf-8')
    result = {}
    for stem, title_arg in [('HGFX_Main', title), ('HGFX_ESM', 'HGFX Supplementary Appendices')]:
        run(['pandoc', stem + '.md', '-f', 'markdown+tex_math_single_backslash+raw_tex',
             '-s', '--citeproc', '--bibliography=references.bib',
             '--metadata=title:' + title_arg, '--metadata=author:Mohammad Ahmadkhanloo',
             '--metadata=date:', '-V', 'geometry:margin=23mm', '-V', 'fontsize:10pt',
             '-o', stem + '.tex'], stage, log)
        if stem == 'HGFX_Main' and (stage / (stem + '.tex')).read_text().count('\\begin{longtable}') != 6:
            raise RuntimeError('Pandoc did not preserve all six tables')
        for _ in range(2):
            run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', stem + '.tex'], stage, log)
        info = run(['pdfinfo', stem + '.pdf'], stage, log)
        match = re.search(r'^Pages:\s*(\d+)\s*$', info, re.M)
        if not match:
            raise RuntimeError('pdfinfo page count missing')
        run(['pdftotext', stem + '.pdf', stem + '.txt'], stage, log)
        extracted = (stage / (stem + '.txt')).read_text(encoding='utf-8')
        if any(x in extracted for x in ('[@', '??', '**Table')):
            raise RuntimeError('unresolved rendered citation/table marker')
        result[stem] = {'pages': int(match[1]),
                        'pdf_sha256': sha(stage / (stem + '.pdf')),
                        'tex_sha256': sha(stage / (stem + '.tex'))}
    limits = {'HGFX_Main': 14, 'HGFX_ESM': 10}
    status = ('DRAFT_PAGE_LIMITS_MET' if all(result[n]['pages'] <= lim for n, lim in limits.items())
              else 'DRAFT_PAGE_LIMIT_BLOCKED')
    manifest = {'schema': 'compstat_active_preview_v1', 'status': status,
                'submission_authorized': False, 'scientific_validation': 'NOT_ASSESSED',
                'layout': 'generic author-review Pandoc/LaTeX (not official Springer class)',
                'abstract_words': nwords, 'input_sha256': hashes,
                'output': result, 'page_limits': limits}
    (out / 'build_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(out / 'HGFX_review_source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file() and p.suffix in {'.md', '.tex', '.bib', '.pdf'}:
                z.write(p, p.relative_to(stage))
    print(json.dumps(manifest, indent=2))
    return 0 if status == 'DRAFT_PAGE_LIMITS_MET' else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--outdir', type=Path, default=Path('paper/computational_statistics/active_preview'))
    args = parser.parse_args()
    try:
        return build(args.root, args.outdir)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'BUILD_BLOCKED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
