"""Build this candidate only, with a flat editable LaTeX source archive.

The generic Pandoc article layout is an author-review format, not an official
Springer class. No historical manuscript/default builder is modified.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    if result.returncode:
        failure = HERE / 'package/last_build_failure.log'
        failure.write_text(result.stdout + result.stderr, encoding='utf-8', newline='\n')
        print((result.stdout + result.stderr)[-2500:])
        result.check_returncode()
    return result


def source_text(name):
    text = (HERE / name).read_text(encoding='utf-8')
    if name == 'manuscript.md':
        text = text[text.index('## Abstract'):]
        text = text.split('\n## References')[0]
    else:
        text = text.split('\n', 1)[1]
    text = re.sub(r'\]\(figures/([^)]*)\)', r'](\1)', text)
    # Keep each full caption with its image; Pandoc implicit-image captions
    # otherwise duplicate the label and can float away from the real caption.
    def figure(match):
        filename, caption = match.group(1), match.group(3)
        caption = ' '.join(caption.split()).replace('&', r'\&').replace('%', r'\%').replace('_', r'\_')
        return '\n'.join([r'\begin{center}', r'\begin{minipage}{\linewidth}', r'\centering', rf'\includegraphics[width=\linewidth]{{{filename}}}', rf'\captionof{{figure}}{{{caption}}}', r'\end{minipage}', r'\end{center}'])
    text = re.sub(r'!\[[^\]]*\]\(([^)]+)\)\{width=[^}]+\}\s+\*\*Fig\. ([^*]+)\*\* (.*?)(?=\n\n|\Z)', figure, text, flags=re.S)
    if name == 'manuscript.md':
        text = 'Institute for Research in Fundamental Sciences (IPM), Tehran, Iran\n\nCorrespondence: m.ahmadkhanloo@ipm.ir\n\nKeywords: statistical computing; Bayesian learning; numerical reproducibility; model selection; research software; uncertainty\n\n' + text
    return text


def main():
    out = HERE / 'package'
    out.mkdir(exist_ok=True)
    versions = {}
    for tool in ['pandoc', 'pdflatex', 'pdftotext', 'pdfinfo']:
        report = run([tool, '--version' if tool in ['pandoc', 'pdflatex'] else '-v'], HERE)
        versions[tool] = (report.stdout or report.stderr).splitlines()[:2]
    with tempfile.TemporaryDirectory(prefix='hgfx-compstat-build-') as temporary:
        work = Path(temporary)
        shutil.copyfile(HERE / 'references.bib', work / 'references.bib')
        shutil.copyfile(HERE / 'THIRD_PARTY_NOTICES.md', work / 'THIRD_PARTY_NOTICES.md')
        (work / 'README.txt').write_text('Author-review source, not cleared for submission.\nCompile each .tex with pdfLaTeX twice in this flat directory.\nThe bibliography is rendered inline by citeproc; references.bib is supplied for editing.\nGeneric Pandoc article layout; no official Springer class is claimed.\nSource and evidence documentation: paper/computational_statistics/ in the HGFX repository.\n', encoding='utf-8', newline='\n')
        for image in (HERE / 'figures').glob('*.pdf'):
            shutil.copyfile(image, work / image.name)
        for stem, name, title in [('HGFX_CompStat', 'manuscript.md', 'HGFX: reference-compatible hierarchical Gaussian filtering in Python'), ('HGFX_Supplement', 'supplement.md', 'HGFX supplementary evidence and provenance')]:
            (work / f'{stem}.md').write_text(source_text(name), encoding='utf-8', newline='\n')
            command = ['pandoc', f'{stem}.md', '--standalone', '--no-highlight', '--citeproc', '--bibliography=references.bib', '--metadata=reference-section-title:References', f'--metadata=title:{title}', '--metadata=author:Mohammad Ahmadkhanloo', '--metadata=date:Author-review draft, 8 November 2026', '-V', 'geometry:margin=25mm', '-V', 'fontsize:11pt', '-V', 'colorlinks:true', '-o', f'{stem}.tex']
            if (HERE / 'springer-basic-author-date.csl').exists():
                command.insert(2, f'--csl={HERE / "springer-basic-author-date.csl"}')
            run(command, work)
            # Preserve code and monospace names without overflowing long identifiers.
            tex_path = work / f'{stem}.tex'
            tex = tex_path.read_text(encoding='utf-8').replace('\\begin{document}', '\\setlength{\\emergencystretch}{3em}\n\\begin{document}')
            if stem == 'HGFX_CompStat':
                if tex.count('\\begin{longtable}') != 3:
                    raise RuntimeError('Candidate tables failed Markdown conversion')
                # These three compact tables fit on one page. Convert Pandoc's
                # multipage environment after parsing Markdown, then bind each
                # caption and table in an unbreakable box.
                tex = tex.replace('\\begin{longtable}[]', '\\begin{tabular}')
                tex = re.sub(r'\\bottomrule\\noalign\{\}\s*\\endlastfoot', '', tex)
                tex = tex.replace('\\endhead', '').replace('\\end{longtable}', '\\bottomrule\n\\end{tabular}')
                tex = re.sub(r'(\\textbf\{Table \d+\.\}.*?\\end\{tabular\}\s*\})', lambda m: '\\begin{minipage}{\\linewidth}\n' + m.group(1) + '\n\\end{minipage}\n', tex, flags=re.S)
            else:
                # All six supplementary tables are short; keep complete rows
                # together rather than leaving one continuation row on a page.
                tex = tex.replace('\\begin{longtable}[]', '\\begin{tabular}')
                tex = re.sub(r'\\bottomrule\\noalign\{\}\s*\\endlastfoot', '', tex)
                tex = tex.replace('\\endhead', '').replace('\\end{longtable}', '\\bottomrule\n\\end{tabular}')
                tex = re.sub(r'(\\begin\{tabular\}.*?\\end\{tabular\})', lambda m: '\\begin{minipage}{\\linewidth}\n' + m.group(1) + '\n\\end{minipage}\n', tex, flags=re.S)
            tex = re.sub(r'(\\begin\{CSLReferences\}\{\d+\}\{\d+\})', lambda m: m.group(1)+'\n\\interlinepenalty=10000', tex)
            tex = tex.replace('\\begin{document}', '\\usepackage{graphicx,caption}\n\\renewcommand{\\figurename}{Fig.}\n' + ('\\renewcommand{\\thefigure}{S\\arabic{figure}}\n' if stem == 'HGFX_Supplement' else '') + '\\begin{document}')
            tex_path.write_text(tex, encoding='utf-8', newline='\n')
            logs = []
            for _ in range(2):
                command = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', f'{stem}.tex']
                if 'MiKTeX' in '\n'.join(versions['pdflatex']):
                    command.insert(1, '--disable-installer')
                logs.append(run(command, work).stdout)
            (out / f'{stem}_build.log').write_text('\n'.join(logs), encoding='utf-8', newline='\n')
            run(['pdftotext', f'{stem}.pdf', f'{stem}.txt'], work)
            rendered = (work / f'{stem}.txt').read_text(encoding='utf-8')
            if re.search(r'\[@|\?\?|References are rendered|\*\*Table|\|---', rendered):
                raise RuntimeError('Unresolved reference or draft placeholder in PDF')
            if stem == 'HGFX_CompStat' and ('reference-compatible' not in rendered or 'paired-integrity' not in rendered):
                raise RuntimeError('Candidate title or preserved failure missing')
            for suffix in ['pdf', 'tex']:
                shutil.copyfile(work / f'{stem}.{suffix}', out / f'{stem}.{suffix}')
        with zipfile.ZipFile(out / 'HGFX_CompStat_source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in work.iterdir():
                if path.suffix in ['.tex', '.bib', '.pdf', '.md', '.txt']:
                    archive.write(path, path.name)
    manifest = {'layout': 'generic Pandoc article; official template download HTTP 403', 'status': 'AUTHOR_REVIEW_NOT_SUBMISSION_READY', 'hash_convention': 'source text written LF; binaries exact', 'tool_versions': versions, 'inputs': {}, 'outputs': {}}
    input_names = ['manuscript.md', 'supplement.md', 'references.bib', 'build_submission.py', 'THIRD_PARTY_NOTICES.md']
    input_names += [path.relative_to(HERE).as_posix() for path in (HERE / 'figures').glob('*.pdf')]
    if (HERE / 'springer-basic-author-date.csl').exists():
        input_names.append('springer-basic-author-date.csl')
    for name in input_names:
        manifest['inputs'][name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    for path in out.iterdir():
        if path.suffix in ['.pdf', '.tex', '.zip']:
            manifest['outputs'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / 'build_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(out)


if __name__ == '__main__':
    main()
