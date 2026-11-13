#!/usr/bin/env python3
"""Audit manuscript numbers against pinned JSON evidence (REV-0.4).

Strict mode fails on unmapped numbers or evidence mismatches. During REV-0,
--allow-unmapped prints an incomplete coverage report without treating missing
future mappings as a scientific PASS. No tolerance is used for comparison.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = "docs/planning/COMPSTAT_CLAIM_MAP.json"
NUM_RE = re.compile(r"(?<![\w.])[-+]?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][-+]?\d+)?(?!\w)")
TEXT_SUFFIXES = {".json", ".md", ".txt", ".log", ".bib", ".py", ".csv", ".csl",
                 ".tex", ".tsv", ".m", ".xml", ".yml", ".yaml"}


def evidence_sha256(path: Path) -> str:
    """Hash evidence bytes; text files are CRLF-normalized so pins recorded
    from LF blobs stay valid on Windows checkouts (binary files stay exact)."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def numeric_spans(text: str) -> list[tuple[int, int, str]]:
    return [(m.start(), m.end(), m.group()) for m in NUM_RE.finditer(text)]


def get_pointer(value: object, pointer: str) -> object:
    if not pointer.startswith("/"):
        raise ValueError("JSON pointer must begin with '/'")
    for component in pointer[1:].split("/"):
        component = component.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            value = value[int(component)]
        elif isinstance(value, dict):
            value = value[component]
        else:
            raise ValueError(f"cannot descend into {type(value).__name__}")
    return value


def expected_number(raw: object, specification: dict) -> Decimal:
    if specification.get("operation", "value") == "length":
        raw = len(raw)
    if isinstance(raw, bool) or not isinstance(raw, (int, float, Decimal)):
        raise ValueError("evidence JSON pointer is not numeric")
    precision = specification.get("decimal_places")
    sig = specification.get("significant_digits")
    if precision is not None and sig is not None:
        raise ValueError("choose one numeric presentation format")
    result = Decimal(str(raw))
    if precision is not None:
        result = result.quantize(Decimal(1).scaleb(-int(precision)), rounding=ROUND_HALF_EVEN)
    if sig is not None:
        result = Decimal(format(float(raw), f".{int(sig)}g"))
    return result


def scan(root: Path, sources: list[str], registry: dict) -> dict:
    errors: list[str] = []
    source_contents: dict[str, str] = {}
    for source in sources:
        candidate = (root / source).resolve()
        if not candidate.is_relative_to(root.resolve()) or not candidate.is_file():
            errors.append(f"source missing or outside repository: {source}")
            continue
        source_contents[source] = candidate.read_text(encoding="utf-8")

    evidence_cache: dict[str, tuple[object, str]] = {}
    matches: dict[str, set[tuple[int, int]]] = {name: set() for name in source_contents}
    covered: list[dict] = []
    labels: list[dict] = []
    labelled: dict[str, int] = {}
    seen_ids: set[str] = set()
    for claim in registry.get("claims", []):
        identifier = claim["id"]
        if identifier in seen_ids:
            errors.append(f"{identifier}: duplicate registry id")
            continue
        seen_ids.add(identifier)
        source = claim["source"]
        phrase = claim["phrase"]
        specs = claim["values"]
        if source not in source_contents:
            # This can happen when auditing a different submission source.
            continue
        phrase_spans = numeric_spans(phrase)
        if len(specs) != len(phrase_spans) or not phrase_spans:
            errors.append(f"{identifier}: one evidence pointer required per numeric token in phrase")
            continue
        evidence_path = claim["evidence"]
        try:
            evidence_file = (root / evidence_path).resolve()
            if not evidence_file.is_relative_to(root.resolve()):
                raise ValueError("evidence outside repository")
            if evidence_path not in evidence_cache:
                evidence_cache[evidence_path] = (
                    json.loads(evidence_file.read_bytes().decode("utf-8")),
                    evidence_sha256(evidence_file),
                )
            evidence, sha256 = evidence_cache[evidence_path]
            pinned = claim.get("sha256")
            if pinned and pinned != sha256:
                raise ValueError(f"evidence SHA-256 changed: {sha256} != {pinned}")
            for ((_, _, literal), specification) in zip(phrase_spans, specs):
                observed = Decimal(literal.replace(",", ""))
                expected = expected_number(get_pointer(evidence, specification["pointer"]), specification)
                if observed != expected:
                    raise ValueError(f"number {literal} != evidence {expected} at {specification['pointer']}")
        except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            errors.append(f"{identifier}: {exc}")
            continue
        text = source_contents[source]
        positions = list(re.finditer(re.escape(phrase), text))
        if not positions:
            errors.append(f"{identifier}: exact phrase not present in {source}")
            continue
        for position in positions:
            for start, end, _ in phrase_spans:
                matches[source].add((position.start() + start, position.start() + end))
        covered.append({
            "id": identifier, "source": source, "occurrences": len(positions),
            "evidence": evidence_path, "pointers": [s["pointer"] for s in specs],
            "evidence_sha256": sha256,
        })

    # Non-claim label entries: structural tokens (headings, table labels,
    # version identifiers, run IDs, citation DOIs) covered by an exact phrase
    # with a documented class and rationale. No evidence pointer is required,
    # and a label never validates a scientific value.
    for label in registry.get("labels", []):
        identifier = label.get("id")
        if not identifier or identifier in seen_ids:
            errors.append(f"{identifier}: duplicate registry id")
            continue
        seen_ids.add(identifier)
        source = label.get("source")
        if source not in source_contents:
            continue
        phrase = label.get("phrase") or ""
        phrase_spans = numeric_spans(phrase)
        if not phrase_spans:
            errors.append(f"{identifier}: label phrase contains no numeric token")
            continue
        text = source_contents[source]
        positions = list(re.finditer(re.escape(phrase), text))
        if not positions:
            errors.append(f"{identifier}: exact label phrase not present in {source}")
            continue
        for position in positions:
            for start, end, _ in phrase_spans:
                matches[source].add((position.start() + start, position.start() + end))
        labelled[source] = labelled.get(source, 0) + len(phrase_spans) * len(positions)
        labels.append({
            "id": identifier, "source": source, "occurrences": len(positions),
            "class": label.get("class", "unclassified"),
            "rationale": label.get("rationale", ""),
        })

    unmapped: list[dict] = []
    counts: dict[str, dict[str, int]] = {}
    for source, text in source_contents.items():
        all_numbers = numeric_spans(text)
        covered_spans = matches[source]
        counts[source] = {"mapped": sum((a, b) in covered_spans for a, b, _ in all_numbers),
                          "total": len(all_numbers)}
        for start, end, number in all_numbers:
            if (start, end) in covered_spans:
                continue
            line_number = text.count("\n", 0, start) + 1
            line_start = text.rfind("\n", 0, start) + 1
            line_end = text.find("\n", end)
            if line_end == -1:
                line_end = len(text)
            unmapped.append({
                "source": source, "line": line_number, "number": number,
                "context": text[line_start:line_end].strip()[:180],
            })
    return {
        "status": "ERROR" if errors else ("INCOMPLETE" if unmapped else "COVERED"),
        "sources": counts, "mapped_claims": covered, "labels": labels,
        "labelled": labelled,
        "unmapped_count": len(unmapped), "unmapped": unmapped, "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--source", action="append", help="repository-relative MD/TeX source; repeatable")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY, help="repository-relative mapping JSON")
    ap.add_argument("--json-out", type=Path, help="write machine-readable coverage report")
    ap.add_argument("--allow-unmapped", action="store_true", help="REV-0 inventory only; never PASS")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    registry = json.loads((root / args.registry).read_text(encoding="utf-8"))
    if args.source:
        sources = args.source
    else:
        tex_sources = ["paper/computational_statistics/Manuscript.tex",
                       "paper/computational_statistics/ESM_1.tex"]
        sources = ([p for p in tex_sources if (root / p).is_file()]
                   or ["paper/computational_statistics/manuscript.md",
                       "paper/SUPPLEMENTARY_APPENDICES.md"])
    result = scan(root, sources, registry)
    print("REV-0.4 numeric claims coverage (no scientific tolerance)")
    for source, count in result["sources"].items():
        print(f"  {source}: {count['mapped']}/{count['total']} numeric tokens "
              f"mapped, {result['labelled'].get(source, 0)} labelled non-claim")
    for claim in result["mapped_claims"]:
        print(f"  MAP {claim['id']}: {claim['evidence']}#{','.join(claim['pointers'])} "
              f"sha256={claim['evidence_sha256']}")
    print(f"Unmapped numeric tokens: {result['unmapped_count']}; "
          f"evidence errors: {len(result['errors'])}")
    for error in result["errors"]:
        print(f"  ERROR {error}", file=sys.stderr)
    for item in result["unmapped"][:30]:
        print(f"  UNMAPPED {item['source']}:{item['line']}: {item['number']} | {item['context']}")
    if result["unmapped_count"] > 30:
        print("  ... remaining unmapped records available in --json-out")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if result["errors"] or (result["unmapped_count"] and not args.allow_unmapped) else 0


if __name__ == "__main__":
    raise SystemExit(main())
