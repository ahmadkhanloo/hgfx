#!/usr/bin/env python3
"""Static/release-readiness checks for HGFX v1 packaging and independent use."""

from __future__ import annotations

import ast
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CITATION.cff",
    "examples/quickstart.py",
    "docs/user/GETTING_STARTED.md",
    "docs/user/API.md",
    "docs/validation/V1_EVIDENCE_INDEX.md",
    "reference/validation/v1_release/evidence_index.json",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_required_files() -> None:
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"required release file missing or empty: {relative}")


def check_pyproject() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data.get("project", {})
    if project.get("name") != "hgfx":
        fail("pyproject project.name must be 'hgfx'")
    if not project.get("requires-python"):
        fail("pyproject requires-python is missing")
    dependencies = [str(item).lower() for item in project.get("dependencies", [])]
    if any("matlab" in item for item in dependencies):
        fail("MATLAB must not be a runtime dependency")


def iter_python_files() -> list[Path]:
    files = list((ROOT / "src" / "hgfx").rglob("*.py"))
    files.extend((ROOT / "examples").rglob("*.py"))
    return sorted(files)


def check_no_matlab_runtime_imports() -> None:
    forbidden_text = ("matlab.engine", "from matlab ", "import matlab")
    for path in iter_python_files():
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        for token in forbidden_text:
            if token in lower:
                fail(f"forbidden MATLAB runtime reference {token!r} in {path.relative_to(ROOT)}")
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".", 1)[0] == "matlab":
                        fail(f"MATLAB import in {path.relative_to(ROOT)}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".", 1)[0] == "matlab":
                    fail(f"MATLAB import in {path.relative_to(ROOT)}")


def check_evidence_index() -> None:
    path = ROOT / "reference" / "validation" / "v1_release" / "evidence_index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("frozen_matlab_reference") != "2437f4dc241541072722a2695ddeca7b44d83dd3":
        fail("evidence index points at the wrong frozen MATLAB reference")
    if not isinstance(data.get("evidence"), list) or not data["evidence"]:
        fail("evidence index has no evidence entries")
    blockers = data.get("active_blockers")
    if not isinstance(blockers, list):
        fail("evidence index active_blockers must be a list")


def main() -> None:
    check_required_files()
    check_pyproject()
    check_no_matlab_runtime_imports()
    check_evidence_index()
    print("PASS: HGFX v1 static release-readiness checks")


if __name__ == "__main__":
    main()
