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
FIGURE_FILES = (
    "fig_evidence_classes.png",
    "fig_recovery_metrics.png",
    "fig_model_selection.png",
    "fig_gpu_applicability.png",
    "fig_pyhgf_common_scope.png",
    "fig_p3_horizon_diagnostics.png",
)
PLANNING_PREFIXES = (
    "**Target journal:**",
    "**Article type:**",
    "**Highlights:**",
    "**Word count",
    "**Figures:**",
    "**Abstract:**",
)


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def _strip_placeholder_reference_section(text: str) -> str:
    if REFERENCE_MARKER not in text:
        raise RuntimeError("paper/manuscript.md is missing the References section marker")
    body, _ = text.split(REFERENCE_MARKER, 1)
    return body.rstrip() + "\n"


def _submission_source(text: str) -> str:
    """Remove internal planning metadata and embed all referee-facing figures."""
    body = _strip_placeholder_reference_section(text)
    lines = [
        line for line in body.splitlines()
        if not any(line.startswith(prefix) for prefix in PLANNING_PREFIXES)
    ]
    body = "\n".join(lines).strip() + "\n"

    for index, filename in enumerate(FIGURE_FILES, start=1):
        marker = f"**Figure {index}.**"
        image = f"![Figure {index}](paper/figures/{filename})"
        if marker not in body:
            raise RuntimeError(f"missing Figure {index} caption")
        body = body.replace(marker, image + "\n\n" + marker, 1)
    return body


def _bib_titles(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    titles = re.findall(r"(?mi)^\s*title\s*=\s*\{(.+?)\}\s*,?\s*$", text)
    if not titles:
        raise RuntimeError("no bibliography titles found")
    return titles


def _normalize_text(value: str) -> str:
    value = re.sub(r"[{}]", "", value)
    value = re.sub(r"\\[A-Za-z]+\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.casefold().strip()


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def build(out_dir: Path) -> tuple[Path, Path]:
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc is required for the journal submission build")

    manuscript = (ROOT / "paper" / "manuscript.md").read_text(encoding="utf-8")
    source = _submission_source(manuscript)
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
    leak_markers = (
        "subscription track, no APC",
        "Word count (main text, approximate)",
        "this draft ~",
        "paper/highlights.txt",
    )
    leaked = [marker for marker in leak_markers if marker in rendered]
    if leaked:
        raise RuntimeError(
            "internal planning metadata leaked into journal DOCX: " + ", ".join(leaked)
        )

    titles = _bib_titles(refs)
    rendered_norm = _normalize_text(rendered)
    missing = [title for title in titles if _normalize_text(title) not in rendered_norm]
    if missing:
        raise RuntimeError(
            f"citeproc bibliography verification failed ({len(titles) - len(missing)}/{len(titles)}): "
            + ", ".join(missing)
        )

    with zipfile.ZipFile(docx) as zf:
        media = [name for name in zf.namelist() if name.startswith("word/media/")]
    if len(media) < len(FIGURE_FILES):
        raise RuntimeError(
            f"journal DOCX is figure-incomplete: {len(media)}/{len(FIGURE_FILES)} embedded media"
        )

    for tool in ("pdftotext", "pdfimages"):
        if shutil.which(tool) is None:
            raise RuntimeError(f"{tool} is required for journal submission verification")

    txt = out_dir / "_pdf_text.txt"
    run("pdftotext", str(pdf), str(txt))
    pdf_text = txt.read_text(encoding="utf-8", errors="replace")
    txt.unlink(missing_ok=True)
    pdf_norm = _normalize_text(pdf_text)
    missing_pdf = [title for title in titles if _normalize_text(title) not in pdf_norm]
    if missing_pdf:
        raise RuntimeError(
            f"PDF bibliography verification failed ({len(titles) - len(missing_pdf)}/{len(titles)}): "
            + ", ".join(missing_pdf)
        )

    image_list = subprocess.check_output(
        ("pdfimages", "-list", str(pdf)), text=True, errors="replace"
    )
    image_rows = [
        line for line in image_list.splitlines()
        if re.match(r"^\s*\d+\s+\d+\s+", line)
    ]
    if len(image_rows) < len(FIGURE_FILES):
        raise RuntimeError(
            f"journal PDF is figure-incomplete: {len(image_rows)}/{len(FIGURE_FILES)} image rows"
        )

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
