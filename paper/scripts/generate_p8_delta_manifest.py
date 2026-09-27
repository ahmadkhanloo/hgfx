#!/usr/bin/env python3
"""Generate the deterministic P8 paper/post-review delta manifest.

The independent v1 review/remediation is accepted as baseline. This script
classifies every file changed between the post-remediation validated source
and the exact P7 paper candidate so an independent reviewer can review only
the relevant delta rather than re-reviewing unchanged v1 implementation.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

BASELINE_SHA = "09c49031cda95b449f8115030a9d32dcba36098e"
V1_RELEASE_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"

PAPER_PREFIXES = (
    "paper/",
    "docs/research/",
    "gpu_validation_results/",
)
PAPER_WORKFLOWS = (
    ".github/workflows/p2-paper-tables.yml",
    ".github/workflows/p2a10-common-scope.yml",
    ".github/workflows/p2a10-evidence-ingest.yml",
    ".github/workflows/p2a10-paper-sync.yml",
    ".github/workflows/p2a9-preflight.yml",
    ".github/workflows/p5-paper-figures.yml",
    ".github/workflows/p6a-paper-evidence.yml",
    ".github/workflows/p7-paper-preflight.yml",
    ".github/workflows/p8-delta-scope.yml",
    ".github/workflows/p8-cpu-postfix-evidence.yml",
    ".github/workflows/arxiv-package.yml",
)
EVIDENCE_PROVENANCE_PATHS = (
    "docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md",
    "docs/validation/V1_EVIDENCE_INDEX.md",
    "docs/validation/V1_FINAL_RELEASE_PROVENANCE.md",
    "docs/planning/V1_RELEASE_GATE.md",
    "docs/planning/MILESTONES.md",
    "docs/planning/V1_TODO.md",
    "README.md",
    "CITATION.cff",
    ".github/workflows/m19-m20-release-preflight.yml",
)
PRODUCT_ONLY_PREFIXES = (
    "src/hgfx/",
    "tests/unit/",
    "docs/user/",
)
PRODUCT_ONLY_PATHS = (
    "pyproject.toml",
    "docs/planning/OPT_IN_MAP.md",
    "docs/planning/V1_1_RELEASE_PLAN.md",
    "docs/planning/VERSION_POLICY.md",
    ".github/workflows/release-pypi.yml",
    ".github/workflows/verify-pypi.yml",
)
MAINTENANCE_PATHS = (
    ".gitattributes",
    "docs/planning/AGENT_HANDOFF.md",
    "docs/planning/M18_VALIDATION_PLAN.md",
    "docs/planning/PYPI_PUBLISHING.md",
    "docs/planning/ROADMAP.md",
    "docs/planning/V1_PRODUCT_DEFINITION.md",
    "docs/research/BENCHMARK_PLAN.md",
    "docs/research/LEVEL2_PAPER_PLAN.md",
    "docs/superpowers/plans/2026-09-16-v1.0.0-final-promotion.md",
    "docs/superpowers/plans/2026-09-17-p2a10-execute-common-scope.md",
    "docs/superpowers/plans/2026-09-17-p2a9-final-semantic-gate.md",
)

def _run(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

def _classify(path: str) -> str:
    if path.startswith(PAPER_PREFIXES) or path in PAPER_WORKFLOWS:
        return "PAPER_REVIEW_REQUIRED"
    if path in EVIDENCE_PROVENANCE_PATHS:
        return "EVIDENCE_PROVENANCE_REVIEW_REQUIRED"
    if path.startswith(PRODUCT_ONLY_PREFIXES) or path in PRODUCT_ONLY_PATHS:
        return "PRODUCT_ONLY_CHECK_CLAIM_LEAKAGE"
    if path in MAINTENANCE_PATHS:
        return "MAINTENANCE_CONTEXT_ONLY"
    if path.startswith("tests/paper/") or path.startswith("tests/test_p2a"):
        return "PAPER_REVIEW_REQUIRED"
    if path.startswith("tools/apply_p2a") or path.startswith("tools/check_p2a") or path.startswith("tools/run_p2a"):
        return "PAPER_REVIEW_REQUIRED"
    return "UNCLASSIFIED"

def build(repo: Path, candidate_sha: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", candidate_sha):
        raise ValueError("candidate_sha must be a 40-character lowercase Git SHA")
    # Fail early if the exact immutable anchors are absent.
    for sha in (BASELINE_SHA, candidate_sha, V1_RELEASE_SHA):
        _run(repo, "cat-file", "-e", f"{sha}^{{commit}}")

    status_lines = _run(repo, "diff", "--name-status", BASELINE_SHA, candidate_sha).splitlines()
    numstat_lines = _run(repo, "diff", "--numstat", BASELINE_SHA, candidate_sha).splitlines()
    numstat = {}
    for line in numstat_lines:
        added, deleted, path = line.split("\t", 2)
        numstat[path] = {
            "additions": None if added == "-" else int(added),
            "deletions": None if deleted == "-" else int(deleted),
            "binary": added == "-" or deleted == "-",
        }

    files = []
    for line in status_lines:
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]
        entry = {
            "path": path,
            "git_status": status,
            "review_class": _classify(path),
        }
        entry.update(numstat.get(path, {"additions": None, "deletions": None, "binary": True}))
        files.append(entry)

    unclassified = [item["path"] for item in files if item["review_class"] == "UNCLASSIFIED"]
    if unclassified:
        raise RuntimeError("unclassified P8 delta paths: " + ", ".join(unclassified))

    counts = {}
    for item in files:
        counts[item["review_class"]] = counts.get(item["review_class"], 0) + 1

    changed_paths = {item["path"] for item in files}
    frozen_matlab_changed = sorted(path for path in changed_paths if path.startswith("reference/matlab/"))
    frozen_v1_evidence_changed = sorted(
        path for path in changed_paths if path.startswith("reference/validation/v1_release/")
    )

    return {
        "schema_version": 1,
        "manifest_id": "hgfx-p8-paper-delta-1",
        "status": "READY_FOR_INDEPENDENT_PAPER_DELTA_REVIEW",
        "baseline": {
            "kind": "post_independent_review_remediation_validated_source",
            "sha": BASELINE_SHA,
            "independent_review_report": "docs/validation/INDEPENDENT_REVIEW_REPORT.md",
            "remediation_record": "docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md",
        },
        "candidate": {
            "kind": "locked_p7_submission_candidate",
            "sha": candidate_sha,
        },
        "v1_release_anchor": V1_RELEASE_SHA,
        "ahead_commit_count": int(_run(repo, "rev-list", "--count", f"{BASELINE_SHA}..{candidate_sha}")),
        "changed_file_count": len(files),
        "review_class_counts": counts,
        "frozen_matlab_reference_changed": frozen_matlab_changed,
        "frozen_v1_release_evidence_changed": frozen_v1_evidence_changed,
        "review_policy": {
            "PAPER_REVIEW_REQUIRED": "Independent reviewer inspects scientific wording, paper-only evidence, tables/figures, reproducibility, and claim mapping.",
            "EVIDENCE_PROVENANCE_REVIEW_REQUIRED": "Reviewer checks provenance/release context only where it supports a manuscript claim.",
            "PRODUCT_ONLY_CHECK_CLAIM_LEAKAGE": "No repeat implementation review; verify additive post-v1 product work is not silently promoted into paper-1 claims.",
            "MAINTENANCE_CONTEXT_ONLY": "Context only unless reviewer finds a direct manuscript/evidence dependency.",
        },
        "files": sorted(files, key=lambda x: x["path"]),
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--output", default="docs/research/P8_DELTA_MANIFEST.json")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    payload = build(repo, args.candidate_sha)
    output = repo / args.output
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "ahead_commit_count": payload["ahead_commit_count"],
        "changed_file_count": payload["changed_file_count"],
        "review_class_counts": payload["review_class_counts"],
        "frozen_matlab_reference_changed": payload["frozen_matlab_reference_changed"],
        "frozen_v1_release_evidence_changed": payload["frozen_v1_release_evidence_changed"],
    }, indent=2))

if __name__ == "__main__":
    main()
