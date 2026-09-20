#!/usr/bin/env python3
"""Build the reader-facing HGFX arXiv PDF and source bundle.

The arXiv package is generated from the committed reader-facing manuscript,
supplementary appendices, bibliography, and vector figures. Scientific values
are not modified by this script.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARXIV = ROOT / "paper" / "arxiv"
DIST = ARXIV / "dist"
BUILD = ARXIV / "_build"
FIG_SRC = ARXIV / "figures"

TITLE = "HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox"
AUTHOR = "Mohammad Ahmadkhanloo"

FIGURES = [
    (
        "fig1_recovery_metrics.pdf",
        "Close paired agreement coexists with weak recovery. Original-scale parameter-recovery summaries are shown for classic, enhanced, and unbounded HGF. Circles denote MATLAB 8.2.0 and crosses denote HGFX 1.0.0; dotted lines mark the unchanged targets. The convergence panel includes descriptive Wilson 95% intervals for 24 cases per family. Correlation and standardized-RMSE panels show point summaries because replicate-level bootstrap inputs are not available in the archived aggregate.",
    ),
    (
        "fig2_horizon_diagnostics.pdf",
        "Trial-horizon diagnostics with incomplete cells retained. Columns separate classic, enhanced, and unbounded HGF; rows show median parameter correlation and median standardized RMSE at 128, 256, 512, and 1024 trials. Dotted lines mark the original targets. Shaded regions denote incomplete classic-HGF summaries at 512 and 1024 trials and are not zeros or interpolated estimates. The whole-study paired-integrity requirement was not satisfied, so these trends do not establish identifiability.",
    ),
    (
        "fig3_pyhgf_common_scope.pdf",
        "Perceptual trajectories agree at binary64 rounding scale, with residuals shown separately. HGFX 1.0.0 and pyhgf 0.3.2 are compared on the frozen 128-trial three-level binary-HGF cell. Panels show predicted input probability, level-2 posterior mean, and the signed HGFX-minus-pyhgf probability residual in units of 1e-16. Participant-response NLL is a separate quantity and remains not directly comparable in this cell.",
    ),
]

def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def latex_escape_caption(text: str) -> str:
    # Captions above contain no intentional LaTeX markup.
    repl = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
    }
    for src, dst in repl.items():
        text = text.replace(src, dst)
    return text


def build_combined_markdown() -> str:
    manuscript = (ARXIV / "manuscript.md").read_text(encoding="utf-8")
    supplementary = (ROOT / "paper" / "SUPPLEMENTARY_APPENDICES.md").read_text(encoding="utf-8")

    abstract_pos = manuscript.index("## Abstract")
    figure_pos = manuscript.index("## Figure captions")
    main_body = manuscript[abstract_pos:figure_pos].rstrip()

    # The source bibliography is processed by Pandoc/citeproc, so the internal
    # placeholder reference section from manuscript.md is deliberately omitted.
    front = """---
title: "{title}"
author:
  - "{author}"
date: ""
bibliography: references.bib
link-citations: true
reference-section-title: References
geometry: margin=1in
fontsize: 10pt
documentclass: article
header-includes:
  - \\usepackage{{graphicx}}
  - \\usepackage{{float}}
---

\\begin{{center}}
\\small Institute for Research in Fundamental Sciences (IPM), Tehran, Iran\\\\
Correspondence: Mohammad Ahmadkhanloo, m.ahmadkhanloo@ipm.ir\\\\
Software: \\url{{https://github.com/ahmadkhanloo/hgfx}}
\\end{{center}}

**Keywords:** Hierarchical Gaussian Filter; computational neuroscience; Bayesian learning; Python; reproducibility; model validation

""".format(title=TITLE, author=AUTHOR)

    def figure_block(index: int) -> str:
        filename, caption = FIGURES[index - 1]
        return "\n".join(
            [
                r"\begin{figure}[H]",
                r"\centering",
                rf"\includegraphics[width=0.92\linewidth]{{figures/{filename}}}",
                rf"\caption{{{latex_escape_caption(caption)}}}",
                rf"\label{{fig:reader{index}}}",
                r"\end{figure}",
            ]
        )

    # Place every figure next to the result it supports instead of collecting
    # detached full-page figures at the end of the manuscript.
    placements = [
        ("The trial-horizon study (section 2.6)", 1),
        ("**Table 4.** Paired parameter recovery", 2),
        ("Participant-response NLL was not directly comparable.", 3),
    ]
    for anchor, index in placements:
        if anchor not in main_body:
            raise RuntimeError(f"Figure placement anchor not found: {anchor}")
        main_body = main_body.replace(
            anchor,
            figure_block(index) + "\n\n" + anchor,
            1,
        )

    # Keep the supplementary title/overview, but normalize it as a continuation
    # of the same preprint rather than as a separate Markdown document.
    supplementary = re.sub(r"^# Supplementary Appendices\s*", "", supplementary, count=1)
    combined = (
        front
        + main_body
        + "\n\n\\clearpage\n\n"
        + "# Supplementary Appendices\n\n"
        + supplementary.strip()
        + "\n"
    )
    return combined


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    if DIST.exists():
        shutil.rmtree(DIST)
    BUILD.mkdir(parents=True)
    DIST.mkdir(parents=True)

    figures_dir = BUILD / "figures"
    figures_dir.mkdir()
    for filename, _ in FIGURES:
        src = FIG_SRC / filename
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, figures_dir / filename)

    shutil.copy2(ROOT / "paper" / "references.bib", BUILD / "references.bib")
    combined = build_combined_markdown()
    (BUILD / "combined_source.md").write_text(combined, encoding="utf-8")

    run(
        "pandoc",
        "combined_source.md",
        "--from=markdown+raw_tex",
        "--standalone",
        "--citeproc",
        "--bibliography=references.bib",
        "--metadata=reference-section-title:References",
        "-o",
        "main.tex",
        cwd=BUILD,
    )

    tex = (BUILD / "main.tex").read_text(encoding="utf-8")
    if "Bibliography entries are in" in tex or "paper/arxiv/figures/" in tex:
        raise RuntimeError("Internal source placeholder/path leaked into arXiv TeX")

    run("latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex", cwd=BUILD)

    pdf_out = DIST / "HGFX_arXiv_preprint.pdf"
    shutil.copy2(BUILD / "main.pdf", pdf_out)

    zip_base = DIST / "HGFX_arXiv_source"
    archive_root = BUILD / "submission"
    archive_root.mkdir()

    # Keep the arXiv upload minimal: only files required to compile the paper.
    # Citeproc has already rendered the bibliography into main.tex.
    shutil.copy2(BUILD / "main.tex", archive_root / "main.tex")
    shutil.copytree(figures_dir, archive_root / "figures")

    shutil.make_archive(str(zip_base), "zip", root_dir=archive_root)

    # Smoke-test the exact source bundle in a clean directory.
    smoke = BUILD / "smoke"
    smoke.mkdir()
    shutil.unpack_archive(str(zip_base) + ".zip", smoke)
    run("latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex", cwd=smoke)

    print(pdf_out)
    print(str(zip_base) + ".zip")


if __name__ == "__main__":
    main()
