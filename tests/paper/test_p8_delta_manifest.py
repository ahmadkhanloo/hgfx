from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "paper/scripts/generate_p8_delta_manifest.py"

def load_generator():
    spec = importlib.util.spec_from_file_location("generate_p8_delta_manifest", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_p8_delta_manifest_is_complete_and_scoped() -> None:
    module = load_generator()
    candidate_sha = json.loads(
        (ROOT / "docs/research/P8_DELTA_MANIFEST.json").read_text(encoding="utf-8")
    )["candidate"]["sha"]
    history = subprocess.run(
        ["git", "cat-file", "-e", f"{module.BASELINE_SHA}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if history.returncode != 0:
        pytest.skip(
            "full git history required; enforced non-skipped by P8 Delta Scope workflow (fetch-depth: 0)"
        )
    head_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", candidate_sha, head_sha],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    assert ancestry.returncode == 0, "P8 manifest candidate must be an ancestor of HEAD"

    if candidate_sha != head_sha:
        changed = set(
            subprocess.check_output(
                ["git", "diff", "--name-only", candidate_sha, head_sha],
                cwd=ROOT,
                text=True,
            ).splitlines()
        )
        allowed_lock_paths = {
            "docs/research/P8_DELTA_MANIFEST.json",
            "docs/research/P8_REVIEW_PACKET.md",
            "docs/research/PAPER_P8_REVIEW_CHECKLIST.md",
        }
        assert changed <= allowed_lock_paths, (
            "P8 manifest may point behind HEAD only across the documented docs-only "
            f"lock chain; unexpected paths: {sorted(changed - allowed_lock_paths)}"
        )

    payload = module.build(ROOT, candidate_sha)

    assert payload["status"] == "READY_FOR_INDEPENDENT_PAPER_DELTA_REVIEW"
    assert payload["baseline"]["sha"] == "09c49031cda95b449f8115030a9d32dcba36098e"
    assert payload["candidate"]["sha"] == candidate_sha
    assert payload["v1_release_anchor"] == "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
    assert payload["ahead_commit_count"] >= 109
    assert payload["changed_file_count"] > 100
    assert payload["frozen_matlab_reference_changed"] == []
    assert payload["frozen_v1_release_evidence_changed"] == []

    by_path = {item["path"]: item for item in payload["files"]}
    assert by_path["paper/manuscript.md"]["review_class"] == "PAPER_REVIEW_REQUIRED"
    assert by_path["paper/reproducibility/p3_m18c2_aggregate_35272347167.json"]["review_class"] == "PAPER_REVIEW_REQUIRED"
    assert by_path["paper/reproducibility/p2a10_comparison_35268575414.json"]["review_class"] == "PAPER_REVIEW_REQUIRED"
    assert by_path["docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md"]["review_class"] == "EVIDENCE_PROVENANCE_REVIEW_REQUIRED"
    assert by_path["src/hgfx/models/vkf.py"]["review_class"] == "PRODUCT_ONLY_CHECK_CLAIM_LEAKAGE"
    assert by_path["src/hgfx/optim/fit_map.py"]["review_class"] == "PRODUCT_ONLY_CHECK_CLAIM_LEAKAGE"
    assert all(item["review_class"] != "UNCLASSIFIED" for item in payload["files"])


def test_p8_candidate_sha_is_explicit_and_validated() -> None:
    module = load_generator()
    with pytest.raises(ValueError, match="40-character lowercase Git SHA"):
        module.build(ROOT, "HEAD")
