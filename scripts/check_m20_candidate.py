#!/usr/bin/env python3
"""Preflight/finalize checks for the HGFX M20 v1.0 candidate gate."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "reference" / "validation" / "v1_release" / "evidence_index.json"
DEFAULT_MANIFEST = ROOT / "reference" / "validation" / "v1_release" / "evidence_manifest.json"

REQUIRED_RELEASE_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CITATION.cff",
    "docs/user/GETTING_STARTED.md",
    "docs/user/API.md",
    "docs/planning/M19_GATE.md",
    "docs/planning/M20_GATE.md",
    "docs/planning/V1_RELEASE_GATE.md",
    "docs/validation/V1_EVIDENCE_INDEX.md",
    "reference/validation/v1_release/evidence_index.json",
)


def parse_citation_version(text: str) -> str | None:
    match = re.search(r'^version:\s*["\']?([^"\'\n]+)', text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def main(mode: str, manifest_path: str) -> int:
    failures: list[str] = []

    for relative in REQUIRED_RELEASE_FILES:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing/empty release file: {relative}")

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = str(pyproject.get("project", {}).get("version", ""))
    if not version.startswith("1.0.0"):
        failures.append(f"package version is not on the v1.0.0 line: {version!r}")
    if mode == "finalize" and version not in {"1.0.0rc1", "1.0.0"}:
        failures.append(f"final M20 requires 1.0.0rc1 or 1.0.0, found {version!r}")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if "TBD" in citation:
        failures.append("CITATION.cff still contains TBD placeholders")
    if "https://github.com/ahmadkhanloo/hgfx" not in citation:
        failures.append("CITATION.cff repository-code is not the HGFX repository")
    citation_version = parse_citation_version(citation)
    if citation_version != version:
        failures.append(
            f"CITATION.cff version {citation_version!r} does not match pyproject {version!r}"
        )

    if not INDEX_PATH.is_file():
        failures.append("release evidence index is missing")
        index = {}
    else:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    evidence = {item.get("id"): item for item in index.get("evidence", [])}
    if evidence.get("S10_RELEASE_READINESS", {}).get("classification") != "PASS":
        failures.append("S10 is not PASS in release evidence index")
    if evidence.get("S9_CPU_BACKEND", {}).get("classification") != "PASS_CPU_BACKEND_EQUIVALENCE":
        failures.append("S9 CPU backend is not PASS in release evidence index")

    manifest = Path(manifest_path)
    if not manifest.is_absolute():
        manifest = ROOT / manifest
    if not manifest.is_file():
        failures.append(f"M19 manifest missing: {manifest}")
        manifest_data = {}
    else:
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))

    if mode == "preflight":
        if manifest_data.get("status") not in {
            "PREPARED_BLOCKED_H100",
            "PREPARED",
            "FROZEN",
        }:
            failures.append(f"unexpected M19 preflight status: {manifest_data.get('status')!r}")
        allowed = {
            "S9 physical H100 revalidation",
            "M19 evidence freeze",
            "M20 v1.0 candidate gate",
        }
        unexpected = sorted(set(index.get("active_blockers", [])) - allowed)
        if unexpected:
            failures.append(f"unexpected release blockers: {unexpected}")
    else:
        if manifest_data.get("status") != "FROZEN":
            failures.append("M19 manifest is not FROZEN")
        h100 = manifest_data.get("physical_h100", {})
        if h100.get("pass") is not True:
            failures.append("M19 manifest does not contain PASS physical-H100 evidence")
        blockers = set(index.get("active_blockers", []))
        if blockers - {"M20 v1.0 candidate gate"}:
            failures.append(f"earlier release blockers remain active: {sorted(blockers)}")

    status = "PASS_PREFLIGHT" if not failures and mode == "preflight" else (
        "PASS_M20_CANDIDATE" if not failures else "FAIL"
    )
    print(json.dumps({"mode": mode, "status": status, "version": version, "failures": failures}, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "finalize"), default="preflight")
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST.relative_to(ROOT)),
    )
    args = parser.parse_args()
    raise SystemExit(main(args.mode, args.manifest))
