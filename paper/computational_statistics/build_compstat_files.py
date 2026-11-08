"""Prepare flat, journal-instruction-adapted LaTeX packages; no official class claim.
Run after build_submission.py. Scientific authoring sources remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
OUT = HERE / 'journal_submission'
TITLE = 'HGFX: reference-compatible hierarchical Gaussian filtering in Python'

def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')

def run(args):
    p = subprocess.run(args, cwd=OUT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    if p.returncode:
        write(OUT / 'build_failure.log', p.stdout + p.stderr)
        raise RuntimeError((p.stdout + p.stderr)[-1800:])
    return p.stdout

def main():
    OUT.mkdir(exist_ok=True)
    for stem, target in [('HGFX_CompStat', 'Manuscript'), ('HGFX_Supplement', 'ESM_1')]:
        tex = (HERE / 'package' / (stem + '.tex')).read_text(encoding='utf-8')
        tex = tex.replace('Author-review draft, 8 November 2026', '9 November 2026')
        tex = tex.replace(r'\renewcommand{\figurename}{Fig.}', r'\renewcommand{\figurename}{Fig.}'+'\n'+r'\captionsetup[figure]{labelfont=bf,labelsep=space}')
        if target == 'ESM_1':
            tex = tex.replace(r'\title{HGFX supplementary evidence and provenance}', r'\title{Online Resource 1: '+TITLE+'}')
            tex = tex.replace(r'\maketitle', r'\maketitle'+'\n\nComputational Statistics\\\\\nMohammad Ahmadkhanloo\\\\\nInstitute for Research in Fundamental Sciences (IPM), Tehran, Iran\\\\\nCorrespondence: m.ahmadkhanloo@ipm.ir\n\n')
        else:
            # Journal asks for a descriptive caption and Online Resource naming.
            insert = r'\subsection{Electronic supplementary material}'+'\n\nOnline Resource 1 (ESM\\_1.pdf) contains frozen identities, numerical validation and recovery details, trial-horizon diagnostics, backend and comparator evidence, published-input source provenance, and the bounded warning and feasibility follow-up.\n\n'
            tex = tex.replace(r'\subsection{Statements and', insert+r'\subsection{Statements and')
        figures = re.findall(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}', tex)
        for index, filename in enumerate(figures, 1):
            new = f'Fig{index}.pdf' if target == 'Manuscript' else f'FigS{index}.pdf'
            shutil.copyfile(HERE / 'figures' / filename, OUT / new)
            tex = tex.replace('{'+filename+'}', '{'+new+'}')
        write(OUT / (target + '.tex'), tex)
        for _ in range(2):
            log = run(['pdflatex', '--disable-installer', '-interaction=nonstopmode', '-halt-on-error', target+'.tex'])
        write(OUT / (target + '_build.log'), log)
        run(['pdftotext', target+'.pdf', target+'.txt'])
        rendered = (OUT / (target+'.txt')).read_text(encoding='utf-8')
        if re.search(r'\[@|\?\?|\*\*Table|\|---', rendered):
            raise RuntimeError('Unresolved markup in '+target)
        if target == 'Manuscript':
            for token in ['324', '48', '0.583', '614', 'Statements and', 'Online Resource 1']:
                if token not in rendered: raise RuntimeError('Missing expected content: '+token)
        if 'Overfull' in log or 'Missing character:' in log:
            raise RuntimeError('Layout warning requires inspection: '+target)
    shutil.copyfile(HERE / 'references.bib', OUT / 'references.bib')
    shutil.copyfile(HERE / 'THIRD_PARTY_NOTICES.md', OUT / 'THIRD_PARTY_NOTICES.md')
    for p in OUT.glob('Fig*.pdf'):
        run(['pdftops', '-eps', p.name, p.with_suffix('.eps').name])
    letter = (HERE / 'cover_letter.md').read_text(encoding='utf-8').split('\n---')[0]
    letter = letter.replace('Authorship and declarations have been confirmed; final scientific approval\nand administrative clearance must be completed before this letter is sent.', 'Authorship and declarations have been confirmed. This letter accompanies the author-review package; final scientific and administrative approval remain pending.')
    write(OUT / 'Cover_letter.md', '# Computational Statistics\n\n9 November 2026\n\n'+letter)
    run(['pandoc', 'Cover_letter.md', '--standalone', '--no-highlight', '-V', 'geometry:margin=25mm', '-V', 'fontsize:11pt', '-o', 'Cover_letter.tex'])
    run(['pdflatex', '--disable-installer', '-interaction=nonstopmode', '-halt-on-error', 'Cover_letter.tex'])
    write(OUT / 'README.txt', 'Computational Statistics, initial software/package contribution.\nAuthor-review package; not submitted and not cleared for submission.\n\nUPLOAD MAP (confirm item types in the actual portal):\nManuscript.pdf: main manuscript preview.\nManuscript_source.zip: editable flat LaTeX source and main figures.\nESM_1.pdf: Online Resource 1, supplementary evidence.\nESM_1_source.zip: editable flat supplementary source (for reproducibility; upload only if requested).\nCover_letter.pdf: unsent letter for author review.\nFigures Fig1-Fig5.pdf and .eps: identical content, vector EPS alternatives supplied.\nDo not upload this entire author-review directory as one manuscript.\n\nBUILD: pdflatex Manuscript.tex twice; pdflatex ESM_1.tex twice.\nReferences are rendered inline with author-year citation hyperlinks; references.bib supplied for editing.\nNo BibTeX step or external image path is required.\nThe sources use the standard article class, adapted to current journal instructions.\nOfficial Springer ZIP retrieval returned HTTP 403; no official-class compliance is claimed.\nGuide checked 2026-11-09: https://link.springer.com/journal/180/submission-guidelines\nPending: final scientific approval, secondary-data reuse assessment, mandatory-fee/institutional/portal clearance.\nDo not infer those approvals from successful compilation.\n')
    for target, pattern in [('Manuscript','Fig[1-5].pdf'),('ESM_1','FigS*.pdf')]:
        names = [target+'.tex','references.bib','README.txt','THIRD_PARTY_NOTICES.md']+[p.name for p in OUT.glob(pattern)]
        with zipfile.ZipFile(OUT / (target+'_source.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for name in names: z.write(OUT/name,name)
        with zipfile.ZipFile(OUT / (target+'_source.zip')) as z:
            assert z.testzip() is None and all('/' not in n and '\\' not in n for n in z.namelist())
    # Keep textual source hashes stable across Windows and Linux Git checkouts.
    for path in OUT.iterdir():
        if path.suffix in {'.tex', '.eps', '.md', '.bib', '.txt'}:
            path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
    inputs = [HERE/'build_compstat_files.py', HERE/'package/HGFX_CompStat.tex', HERE/'package/HGFX_Supplement.tex', HERE/'cover_letter.md', HERE/'references.bib']+list((HERE/'figures').glob('*.pdf'))
    outputs = [p for p in OUT.iterdir() if p.suffix in {'.pdf','.tex','.zip','.eps','.md'} or p.name=='README.txt']
    manifest = {'date':'2026-11-09','venue':'Computational Statistics','type':'software/package contribution; exact portal category unverified','status':'AUTHOR_REVIEW_NOT_SUBMISSION_CLEARED','official_template':'Publisher ZIP HTTP403; standard LaTeX article allowed by journal instructions; no official class claimed','inputs':{p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs},'science_changed':False,'submitted':False}
    write(OUT/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'BUILT_JOURNAL_ADAPTED_PACKAGE','outputs':len(outputs)},indent=2))

if __name__ == '__main__':
    main()
