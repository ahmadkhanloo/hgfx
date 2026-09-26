#!/usr/bin/env python3
"""Build journal-facing DOCX/PDF with citations and bibliography rendered by citeproc."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "paper" / "dist" / "journal"
REFERENCE_MARKER = "\n## References\n"
KNOWN_REFERENCE_TEXT = (
    "A Bayesian Foundation for Individual Learning Under Uncertainty",
    "pyhgf: A neural network library for predictive coding",
)


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def _strip_placeholder_reference_section(text: str) -> str:
    if REFERENCE_MARKER not in text:
        raise RuntimeError("paper/manuscript.md is missing the References section marker")
    body, _ = text.split(REFERENCE_MARKER, 1)
    return body.rstrip() + "\n"


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def build(out_dir: Path) -> tuple[Path, Path]:
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc is required for the journal submission build")

    manuscript = (ROOT / "paper" / "manuscript.md").read_text(encoding="utf-8")
    source = _strip_placeholder_reference_section(manuscript)
    refs = ROOT / "paper" / "references.bib"
    out_dir.mkdir(parents=True, exist_ok=True)
    docx = out_dir / "HGFX_JNM_submission.docx"
    pdf = out_dir / "HGFX_JNM_submission.pdf"

    with tempfile.TemporaryDirectory(prefix="hgfx-jnm-") as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "journal_source.md"
        src.write_text(source, encoding="utf-8")

        common = (
            "pandoc",
            str(src),
            "--from=markdown",
            "--citeproc",
            f"--bibliography={refs}",
            "--metadata=reference-section-title:References",
            f"--resource-path={ROOT}",
        )
        run(*common, "-o", str(docx))
        run(*common, "--pdf-engine=pdflatex", "-o", str(pdf))

    rendered = _docx_text(docx)
    if "Bibliography entries are in" in rendered:
        raise RuntimeError("bibliography placeholder leaked into journal DOCX")
    missing = [item for item in KNOWN_REFERENCE_TEXT if item not in rendered]
    if missing:
        raise RuntimeError("citeproc bibliography verification failed: " + ", ".join(missing))

    if shutil.which("pdftotext"):
        txt = out_dir / "_pdf_text.txt"
        run("pdftotext", str(pdf), str(txt))
        pdf_text = txt.read_text(encoding="utf-8", errors="replace")
        txt.unlink(missing_ok=True)
        missing_pdf = [item for item in KNOWN_REFERENCE_TEXT if item not in pdf_text]
        if missing_pdf:
            raise RuntimeError("PDF bibliography verification failed: " + ", ".join(missing_pdf))

    return docx, pdf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    docx, pdf = build(args.output_dir.resolve())
    print(docx)
    print(pdf)


if __name__ == "__main__":
    main()
