from __future__ import annotations

import importlib.util
from pathlib import Path

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
    payload = module.build(ROOT)

    assert payload["status"] == "READY_FOR_INDEPENDENT_PAPER_DELTA_REVIEW"
    assert payload["baseline"]["sha"] == "09c49031cda95b449f8115030a9d32dcba36098e"
    assert payload["candidate"]["sha"] == "8750bfe5c78a6ece7e3985cb8c182adf231c1bb8"
    assert payload["v1_release_anchor"] == "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
    assert payload["ahead_commit_count"] == 109
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
