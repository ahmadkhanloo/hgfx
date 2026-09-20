#!/usr/bin/env python3
"""Preflight the HGFX manuscript for the P7 Journal of Neuroscience Methods lock."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_HEADINGS = (
    "## Abstract",
    "## 1 Introduction",
    "## 2 Materials and methods",
    "## 3 Results",
    "## 4 Discussion",
    "## 5 Data and code availability",
    "## Declaration of competing interest",
    "## CRediT authorship contribution statement",
    "## Funding",
    "## Acknowledgments",
    "## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process",
    "## References",
)

STALE_PHRASES = (
    "Technology and Code article",
    "FRONTIERS TECHNOLOGY-AND-CODE",
)

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
APPROVED_CORRESPONDING_EMAIL = "m.ahmadkhanloo@ipm.ir"
BIB_KEY_RE = re.compile(r"@[A-Za-z]+\{([^,]+),")
CITE_BLOCK_RE = re.compile(r"\[([^\]]*@[A-Za-z0-9_:-]+[^\]]*)\]")
CITE_KEY_RE = re.compile(r"@([A-Za-z0-9_:-]+)")
UPPER_ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")


def _section(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        raise RuntimeError(f"missing section boundary: {start!r} / {end!r}")
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def build(repo: Path) -> dict:
    manuscript_path = repo / "paper/manuscript.md"
    highlights_path = repo / "paper/highlights.txt"
    refs_path = repo / "paper/references.bib"
    arxiv_path = repo / "paper/arxiv/manuscript.md"

    manuscript = manuscript_path.read_text(encoding="utf-8")
    highlights = [line.strip() for line in highlights_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    refs = refs_path.read_text(encoding="utf-8")
    arxiv = arxiv_path.read_text(encoding="utf-8")

    errors: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if "*Journal of Neuroscience Methods*" not in manuscript:
        errors.append("TARGET_JOURNAL_MISSING")

    missing_headings = [heading for heading in REQUIRED_HEADINGS if heading not in manuscript]
    if missing_headings:
        errors.extend(f"MISSING_HEADING:{heading}" for heading in missing_headings)

    abstract = _section(manuscript, "## Abstract", "## 1 Introduction")
    abstract_words = _word_count(abstract)
    if abstract_words > 250:
        errors.append(f"ABSTRACT_OVER_250_WORDS:{abstract_words}")

    keyword_match = re.search(r"^\*\*Keywords:\*\*\s*(.+)$", manuscript, flags=re.M)
    if not keyword_match:
        errors.append("KEYWORDS_LINE_MISSING")
        keywords: list[str] = []
    else:
        keywords = [item.strip() for item in keyword_match.group(1).split(";") if item.strip()]
        if len(keywords) > 6:
            errors.append(f"TOO_MANY_KEYWORDS:{len(keywords)}")

    if not 3 <= len(highlights) <= 5:
        errors.append(f"HIGHLIGHT_COUNT_OUT_OF_RANGE:{len(highlights)}")
    long_highlights = [{"text": item, "length": len(item)} for item in highlights if len(item) > 85]
    if long_highlights:
        errors.append("HIGHLIGHT_OVER_85_CHARACTERS")
    acronym_highlights = [
        {"text": item, "tokens": UPPER_ACRONYM_RE.findall(item)}
        for item in highlights
        if UPPER_ACRONYM_RE.search(item)
    ]
    if acronym_highlights:
        errors.append("HIGHLIGHT_ACRONYM_OR_ABBREVIATION_PRESENT")

    stale = [phrase for phrase in STALE_PHRASES if phrase in manuscript]
    if stale:
        errors.extend(f"STALE_PHRASE:{phrase}" for phrase in stale)

    if "OpenAI ChatGPT was used during software development" not in manuscript:
        errors.append("AI_RESEARCH_PROCESS_DISCLOSURE_MISSING")
    if "During the preparation of this work, the author used OpenAI ChatGPT" not in manuscript:
        errors.append("AI_MANUSCRIPT_DECLARATION_MISSING")
    if "OpenAI ChatGPT was used during software development" not in arxiv:
        errors.append("ARXIV_AI_RESEARCH_PROCESS_DISCLOSURE_MISSING")
    if "During the preparation of this work, the author used OpenAI ChatGPT" not in arxiv:
        errors.append("ARXIV_AI_MANUSCRIPT_DECLARATION_MISSING")

    if "neuroscience methodology" not in manuscript.lower():
        errors.append("NEUROSCIENCE_METHOD_RELEVANCE_NOT_EXPLICIT")

    correspondence = re.search(r"^\*\*Correspondence:\*\*(.+)$", manuscript, flags=re.M)
    correspondence_text = correspondence.group(1).strip() if correspondence else ""
    correspondence_emails = EMAIL_RE.findall(correspondence_text)
    if not correspondence_emails:
        blockers.append("MISSING_CORRESPONDING_AUTHOR_EMAIL")
    elif APPROVED_CORRESPONDING_EMAIL not in [email.lower() for email in correspondence_emails]:
        errors.append("CORRESPONDING_AUTHOR_EMAIL_NOT_APPROVED")

    bib_keys = set(BIB_KEY_RE.findall(refs))
    cited_keys: set[str] = set()
    for block in CITE_BLOCK_RE.findall(manuscript):
        cited_keys.update(CITE_KEY_RE.findall(block))
    unresolved = sorted(cited_keys - bib_keys)
    if unresolved:
        errors.extend(f"UNRESOLVED_BIB_KEY:{key}" for key in unresolved)

    if "Institutional email to be inserted before submission" in manuscript:
        warnings.append("CORRESPONDENCE_PLACEHOLDER_PRESENT")

    status = "PASS_P7_PREFLIGHT" if not errors and not blockers else (
        "BLOCKED_AUTHOR_INPUT" if not errors and blockers else "FAIL"
    )

    return {
        "schema_version": 1,
        "status": status,
        "errors": errors,
        "blockers": blockers,
        "warnings": warnings,
        "abstract_word_count": abstract_words,
        "keyword_count": len(keywords),
        "keywords": keywords,
        "highlight_count": len(highlights),
        "highlights": [{"text": item, "length": len(item)} for item in highlights],
        "unresolved_bibliography_keys": unresolved,
        "corresponding_author_email_present": bool(correspondence_emails),
        "approved_corresponding_author_email": APPROVED_CORRESPONDING_EMAIL,
        "corresponding_author_email_matches_approved": (
            APPROVED_CORRESPONDING_EMAIL in [email.lower() for email in correspondence_emails]
        ),
        "arxiv_ai_disclosures_present": (
            "OpenAI ChatGPT was used during software development" in arxiv
            and "During the preparation of this work, the author used OpenAI ChatGPT" in arxiv
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    report = build(Path(args.repo_root).resolve())
    payload = json.dumps(report, indent=2, sort_keys=True)
    print(payload)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    if report["errors"] or (args.strict and report["blockers"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
