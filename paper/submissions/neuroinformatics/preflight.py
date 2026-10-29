#!/usr/bin/env python3
"""Read-only editorial preflight for HGFX's Neuroinformatics derivative.

This gate checks formatting and intact scientific disclaimers, NOT new scientific validation.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FIGURES = [
    "fig_evidence_classes.png",
    "fig_recovery_metrics.png",
    "fig_model_selection.png",
    "fig_gpu_applicability.png",
    "fig_pyhgf_common_scope.png",
    "fig_p3_horizon_diagnostics.png",
]
HEADINGS = [
    "## Abstract",
    "## 1 Introduction",
    "## 2 Materials and methods",
    "## 3 Results",
    "## 4 Discussion",
    "## 5 Software availability and reproducibility",
    "## Figure captions",
    "## Information Sharing Statement",
    "## Acknowledgments",
    "## Statements and Declarations",
    "### Funding",
    "### Competing interests",
    "### Author contributions",
    "### Data availability",
    "### Code availability",
    "### Ethics approval",
    "### Use of generative AI tools",
    "## References",
]
FREEZE_IDENTITIES = [
    "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
    "2437f4dc241541072722a2695ddeca7b44d83dd3",
    "897aed804901f9f49ad1d73ecfab6fa714d50098",
]
SCIENTIFIC_QUALIFICATIONS = [
    "36 BIC winners",
    "INSUFFICIENT_REFERENCE_EVIDENCE",
    "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH",
    "not directly comparable",
    "not a post-remediation performance measurement",
]

def check() -> dict:
    doc = (HERE / "manuscript.md").read_text(encoding="utf-8")
    refs = (ROOT / "paper/references.bib").read_text(encoding="utf-8")
    notes = (HERE / "README.md").read_text(encoding="utf-8")
    errors = []
    for heading in HEADINGS:
        if heading not in doc:
            errors.append(f"MISSING_HEADING:{heading}")
    m = re.search(r"(?ms)^## Abstract\n(.*?)^## 1 Introduction", doc)
    abstract = m.group(1).strip() if m else ""
    words = len(re.findall(r"\b[\w'’-]+\b", abstract))
    if not 150 <= words <= 250:
        errors.append(f"ABSTRACT_WORD_COUNT:{words}")
    k = re.search(r"(?m)^\*\*Keywords:\*\* (.+)$", doc)
    keywords = [x.strip() for x in (k.group(1).split(";") if k else []) if x.strip()]
    if not 4 <= len(keywords) <= 6:
        errors.append(f"KEYWORD_COUNT:{len(keywords)}")
    for ident in FREEZE_IDENTITIES[:2]:
        if ident not in doc:
            errors.append(f"FROZEN_IDENTITY_ABSENT:{ident}")
    if FREEZE_IDENTITIES[2] not in notes:
        errors.append("INDEPENDENT_REVIEW_IDENTITY_NOT_RECORDED")
    for phrase in SCIENTIFIC_QUALIFICATIONS:
        if phrase not in doc:
            errors.append(f"QUALIFICATION_ABSENT:{phrase}")
    if "Journal of Neuroscience Methods" in doc or "**Target journal:**" in doc:
        errors.append("SUPERSEDED_JOURNAL_FRONT_MATTER")
    if doc.index("## Information Sharing Statement") > doc.index("## Acknowledgments"):
        errors.append("INFORMATION_SHARING_AFTER_ACKNOWLEDGMENTS")
    between = doc.split("## Information Sharing Statement", 1)[1].split("## Acknowledgments", 1)[0]
    if re.search(r"(?m)^## ", between):
        errors.append("INFORMATION_SHARING_NOT_IMMEDIATELY_BEFORE_ACKNOWLEDGMENTS")
    captions = re.findall(r"(?m)^\*\*Figure (\d+)\.\*\*", doc)
    if captions != ["1","2","3","4","5","6"]:
        errors.append(f"FIGURE_CAPTIONS:{captions}")
    for name in FIGURES:
        if not (ROOT / "paper/figures" / name).is_file():
            errors.append(f"FIGURE_FILE_MISSING:{name}")
    bibkeys = set(re.findall(r"(?m)^@\w+\{([^,]+),", refs))
    used = set(re.findall(r"\[@([a-zA-Z_0-9-]+)", doc))
    # Also capture additional keys inside multi-citation brackets.
    used |= set(re.findall(r";\s*@([a-zA-Z_0-9-]+)", doc))
    missing = sorted(used - bibkeys)
    if missing:
        errors.append("UNRESOLVED_CITATIONS:"+",".join(missing))
    if len(bibkeys) < 10:
        errors.append("BIBLIOGRAPHY_SUSPICIOUSLY_SMALL")
    return {
        "status": "PASS_JOURNAL_FORMAT_PREFLIGHT" if not errors else "FAIL_JOURNAL_FORMAT_PREFLIGHT",
        "errors": errors, "abstract_words": words, "keyword_count": len(keywords),
        "figure_count": len(captions), "used_citation_keys": len(used),
        "frozen_product_sha": FREEZE_IDENTITIES[0],
        "frozen_matlab_sha": FREEZE_IDENTITIES[1],
    }

if __name__ == "__main__":
    report = check()
    print(json.dumps(report, indent=2))
    if report["errors"]:
        sys.exit(1)
