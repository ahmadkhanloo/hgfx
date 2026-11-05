#!/usr/bin/env python3
"""Reproducible journal presentation build; never edits paper/manuscript.md or frozen data."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from preflight import check, ROOT, HERE, FIGURES

DEFAULT_OUT = ROOT / "paper/dist/neuroinformatics"
CAPTION_MARKER = "\n## Figure captions\n"
REFERENCE_MARKER = "\n## References\n"

def run(*args: str) -> None:
    subprocess.run(args, check=True, cwd=ROOT)

def pandoc(input_path: Path, output_path: Path, *, bibliography: bool = False) -> None:
    command = [
        "pandoc", str(input_path), "--from=markdown", "--standalone",
        f"--resource-path={ROOT}",
    ]
    if bibliography:
        command += [
            "--citeproc", f"--bibliography={ROOT / 'paper/references.bib'}",
            "--metadata=reference-section-title:References",
        ]
    if output_path.suffix == ".pdf":
        command.append("--pdf-engine=pdflatex")
    command += ["-o", str(output_path)]
    run(*command)

def manuscript_with_embedded_figures() -> str:
    raw = (HERE / "manuscript.md").read_text(encoding="utf-8")
    if REFERENCE_MARKER not in raw:
        raise RuntimeError("missing explicit References marker")
    body = raw.split(REFERENCE_MARKER, 1)[0].rstrip() + "\n"
    if CAPTION_MARKER not in body:
        raise RuntimeError("missing caption section")
    for i, filename in enumerate(FIGURES, 1):
        marker = f"**Figure {i}.**"
        if body.count(marker) != 1:
            raise RuntimeError(f"expected exactly one caption: {marker}")
        # Place each graphic immediately before its caption in the article body.
        body = body.replace(
            marker, f"![Figure {i}](paper/figures/{filename})\n\n{marker}", 1
        )
    return body

def get_docx_text(docx: Path) -> str:
    with zipfile.ZipFile(docx) as archive:
        xml = archive.read("word/document.xml").decode("utf-8")
        images = [x for x in archive.namelist() if x.startswith("word/media/")]
    if len(images) < 6 and "Manuscript" in docx.name:
        raise RuntimeError(f"Word manuscript embeds {len(images)} of six figures")
    return html.unescape(re.sub(r"<[^>]+>", "", xml))

def inspect_outputs(docx: Path, pdf: Path) -> None:
    rendered = get_docx_text(docx)
    if "Bibliography entries are in" in rendered:
        raise RuntimeError("placeholder bibliography leaked")
    if "Journal of Neuroscience Methods" in rendered:
        raise RuntimeError("prior journal name leaked")
    if "Information Sharing Statement" not in rendered:
        raise RuntimeError("information sharing statement missing")
    bib = (ROOT / "paper/references.bib").read_text(encoding="utf-8")
    titles = re.findall(r"(?mi)^\s*title\s*=\s*\{(.+?)\}\s*,?\s*$", bib)
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"\\[A-Za-z]+|[{}]", "", s)).casefold().strip()
    missing = [title for title in titles if norm(title) not in norm(rendered)]
    if missing:
        raise RuntimeError("Word bibliography incomplete: " + repr(missing))
    if shutil.which("pdfinfo"):
        run("pdfinfo", str(pdf))
    if shutil.which("pdftotext"):
        with tempfile.TemporaryDirectory(prefix="hgfx-ni-verify-") as temp:
            target = Path(temp) / "manuscript.txt"
            run("pdftotext", str(pdf), str(target))
            pdf_text = target.read_text(encoding="utf-8")
            if "Information Sharing Statement" not in pdf_text:
                raise RuntimeError("PDF missing information sharing section")
    if shutil.which("pdfimages"):
        output = subprocess.check_output(
            ["pdfimages", "-list", str(pdf)], text=True, cwd=ROOT
        )
        count = sum(bool(re.match(r"^\s*\d+\s+\d+\s+", x)) for x in output.splitlines())
        if count < 6:
            raise RuntimeError(f"PDF contains only {count} figure image rows")

def build(dest: Path) -> list[Path]:
    report = check()
    if report["errors"]:
        raise RuntimeError("editorial preflight failed: " + repr(report["errors"]))
    for name in ["pandoc", "pdflatex"]:
        if not shutil.which(name):
            raise RuntimeError(f"{name} is required to build journal sources")
    dest.mkdir(parents=True, exist_ok=True)
    docx = dest / "HGFX_Neuroinformatics_Manuscript.docx"
    pdf = dest / "HGFX_Neuroinformatics_Manuscript.pdf"
    supp_docx = dest / "HGFX_Neuroinformatics_Supplementary_Appendices.docx"
    supp_pdf = dest / "HGFX_Neuroinformatics_Supplementary_Appendices.pdf"
    title = dest / "HGFX_Neuroinformatics_Title_Page.docx"
    cover = dest / "HGFX_Neuroinformatics_Cover_Letter.docx"
    with tempfile.TemporaryDirectory(prefix="hgfx-neuroinformatics-") as tmp:
        doc_source = Path(tmp) / "submission_manuscript.md"
        doc_source.write_text(manuscript_with_embedded_figures(), encoding="utf-8")
        pandoc(doc_source, docx, bibliography=True)
        pandoc(doc_source, pdf, bibliography=True)
    pandoc(HERE / "title_page.md", title)
    pandoc(HERE / "cover_letter.md", cover)
    pandoc(ROOT / "paper/SUPPLEMENTARY_APPENDICES.md", supp_docx)
    pandoc(ROOT / "paper/SUPPLEMENTARY_APPENDICES.md", supp_pdf)
    inspect_outputs(docx, pdf)
    source_zip = dest / "HGFX_Neuroinformatics_Source_Figures.zip"
    with zipfile.ZipFile(source_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in [HERE/"manuscript.md",HERE/"title_page.md",
                     HERE/"cover_letter.md",HERE/"README.md",
                     ROOT/"paper/references.bib",
                     ROOT/"paper/SUPPLEMENTARY_APPENDICES.md"]:
            zf.write(path, path.relative_to(ROOT).as_posix())
        for filename in FIGURES:
            path = ROOT/"paper/figures"/filename
            zf.write(path,path.relative_to(ROOT).as_posix())
    return [docx, pdf, supp_docx, supp_pdf, title, cover, source_zip]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    for output in build(args.output_dir.resolve()):
        print(output)
