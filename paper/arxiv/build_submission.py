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
        "fig1_reference_sensitivity.pdf",
        "Sensitivity of the frozen MATLAB reference in the two numerically fragile fitting workflows. "
        "Bars show the fraction of one-local-spacing perturbations of the official start that move the MATLAB "
        "optimizer endpoint outside the original endpoint tolerance: 6/6 for the enhanced-HGF fitting stress case "
        "and 13/14 for the fixed-seed uHGF holdout. This supports an exact-scope reference-limitation interpretation "
        "without converting either endpoint mismatch into direct fitting parity.",
    ),
    (
        "fig2_model_selection_agreement.pdf",
        "Paired model-selection agreement on the frozen three-model grid. MATLAB 8.2.0 and HGFX 1.0.0 have the same "
        "balanced accuracy (0.583) and identical BIC winner decisions in all 36/36 paired datasets. The dashed line "
        "marks the predeclared balanced-accuracy criterion of 0.50. Parameter-recovery metrics are reported separately "
        "in Table 4 and Supplementary Appendix S3.",
    ),
    (
        "fig3_horizon_diagnostics.pdf",
        "Prospective trial-horizon diagnostic at 128, 256, 512 and 1024 trials. MATLAB and HGFX trajectories are shown "
        "together for complete cells; incomplete classic-HGF cells remain as gaps. Because the paired-integrity "
        "requirement was not satisfied, the figure is diagnostic and does not establish a stronger identifiability conclusion.",
    ),
    (
        "fig4_gpu_numerical_agreement.pdf",
        "Absolute CPU-versus-physical-GPU final-objective differences for all four preregistered fitting cells on two "
        "Tesla T4 devices. The dashed line is the predeclared 1e-7 criterion; three cells are exactly equal at the "
        "reported precision and the maximum observed difference is 1.42e-14. This is numerical applicability evidence, "
        "not a speed claim.",
    ),
    (
        "fig5_pyhgf_common_scope.pdf",
        "HGFX versus pyhgf 0.3.2 on the authorized common-scope 128-trial binary-HGF cell. Predicted probability and "
        "level-2 posterior mean overlap at plotting scale, while the residual panel shows the remaining binary64-scale "
        "difference directly. Participant-response NLL is reported separately as not directly comparable at the exact "
        "probability boundary.",
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
                r"\\begin{figure}[H]",
                r"\\centering",
                rf"\\includegraphics[width=0.92\\linewidth]{{figures/{filename}}}",
                rf"\\caption{{{latex_escape_caption(caption)}}}",
                rf"\\label{{fig:reader{index}}}",
                r"\\end{figure}",
            ]
        )

    # Place every figure next to the result it supports instead of collecting
    # detached full-page figures at the end of the manuscript.
    placements = [
        ("### 3.3 Parameter recovery versus model selection", 1),
        ("The trial-horizon study (section 2.6)", 2),
        ("### 3.4 Backend and physical-GPU applicability", 3),
        ("### 3.5 Common-scope comparison with pyhgf", 4),
        ("### 3.6 Examples of use and current limitations", 5),
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
    supplementary = re.sub(r"^# Supplementary Appendices\\s*", "", supplementary, count=1)
    combined = (
        front
        + main_body
        + "\n\n\\\\clearpage\n\n"
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

    readme = """HGFX arXiv source bundle
========================

Entry point: main.tex
Compile: latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

The bibliography has been resolved into main.tex by Pandoc/citeproc for robust
arXiv compilation. references.bib and combined_source.md are included for
traceability. Vector PDF figures are under figures/.

Source repository: https://github.com/ahmadkhanloo/hgfx
HGFX release: v1.0.0
"""
    (BUILD / "README.txt").write_text(readme, encoding="utf-8")

    zip_base = DIST / "HGFX_arXiv_source"
    archive_root = BUILD / "submission"
    archive_root.mkdir()
    for name in ("main.tex", "references.bib", "combined_source.md", "README.txt"):
        shutil.copy2(BUILD / name, archive_root / name)
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
