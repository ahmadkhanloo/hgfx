#!/usr/bin/env python3
"""Generate the deterministic P6A paper-evidence manifest.

P6A is separate from the frozen v1/M19 release evidence. The default output is
DRAFT_NOT_FROZEN. FROZEN_FOR_SUBMISSION requires an independent P8 PASS recorded
for the exact submission-candidate SHA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

PROTOCOL_ID = "hgfx-paper-protocol-1"
MANIFEST_ID = "hgfx-paper-evidence-manifest-1"
HGFX_V1_SHA = "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
MATLAB_ORACLE_SHA = "2437f4dc241541072722a2695ddeca7b44d83dd3"
P2A_RUN = 35268575414
P3_RUN = 35272347167
P3_AGGREGATE_SHA256 = "83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4"

RAW_EVIDENCE = (
    "reference/validation/v1_release/evidence_manifest.json",
    "reference/validation/m18_d02_inference/decision.json",
    "reference/validation/m18_d02_reference_limitation/decision.json",
    "reference/validation/m18_d08_endpoint/decision.json",
    "reference/validation/m18_d08_holdout/decision.json",
    "reference/validation/m18_d08_reference_limitation/decision.json",
    "reference/validation/m18_s7_reference_limitation/decision.json",
    "paper/reproducibility/p2a10_raw_numeric_result_35268575414.json",
    "paper/reproducibility/p2a10_comparison_35268575414.json",
    "paper/reproducibility/p2a10_workflow_provenance_35268575414.json",
    "paper/reproducibility/p2a10_pip_freeze_35268575414.txt",
    "paper/reproducibility/p3_m18c2_aggregate_35272347167.json",
    "paper/reproducibility/p3_m18c2_provenance_35272347167.json",
    "paper/reproducibility/pyhgf_common_scope_case.json",
    "paper/reproducibility/pyhgf_final_semantic_gate.json",
    "paper/reproducibility/pyhgf_initial_state_mapping.json",
    "paper/reproducibility/pyhgf_input_masking_mapping.json",
    "paper/reproducibility/pyhgf_output_quantity_mapping.json",
    "paper/reproducibility/pyhgf_parameter_mapping.json",
    "paper/reproducibility/pyhgf_precision_numerical_policy.json",
    "paper/reproducibility/pyhgf_preflight_environment_35265386637.json",
    "docs/user/MATLAB_DEMOS.md",
    "gpu_validation_results/m18_s9_physical_gpu_revalidation.json",
    "docs/validation/V1_FINAL_RELEASE_PROVENANCE.md",
)

GENERATED_TABLES = (
    "paper/tables/model_workflow_coverage.md",
    "paper/tables/matlab_demo_parity.md",
    "paper/tables/fitting_statistics_classification.md",
    "paper/tables/recovery_model_selection.md",
    "paper/tables/backend_gpu_applicability.md",
    "paper/tables/release_reproducibility_provenance.md",
    "paper/tables/p3_horizon_summary.md",
    "paper/tables/p2_tables_manifest.json",
)

FIGURE_BASENAMES = (
    "fig_evidence_classes",
    "fig_recovery_metrics",
    "fig_model_selection",
    "fig_gpu_applicability",
    "fig_pyhgf_common_scope",
    "fig_p3_horizon_diagnostics",
)
GENERATED_FIGURES = tuple(
    f"paper/figures/{stem}.{suffix}"
    for stem in FIGURE_BASENAMES
    for suffix in ("png", "pdf")
) + ("paper/figures/p5_figures_manifest.json",)

GENERATORS = (
    "paper/scripts/generate_p2_tables.py",
    "paper/scripts/generate_p5_figures.py",
    "paper/scripts/generate_p6a_claim_audit.py",
    "paper/scripts/check_p7_submission.py",
    "paper/scripts/generate_p6a_manifest.py",
)

PROTOCOL_AND_REPRO = (
    "paper/reproducibility/PAPER_PROTOCOL.md",
    "paper/reproducibility/README.md",
    "docs/research/P3_M18C2_RESULT.md",
    "docs/research/PYHGF_COMMON_SCOPE_NUMERICAL_RESULT.md",
    "docs/research/P7_JNM_PREFLIGHT.md",
    "paper/reproducibility/p6a_claim_audit.json",
)

MANUSCRIPT_INPUTS = (
    "paper/manuscript.md",
    "paper/references.bib",
    "paper/highlights.txt",
)


def _canonical_bytes(repo: Path, rel: str) -> bytes:
    """Read the committed Git bytes, independent of checkout line-ending policy."""
    path = repo / rel
    if not path.is_file():
        raise FileNotFoundError(f"missing required P6A evidence file: {rel}")
    try:
        return subprocess.check_output(
            ["git", "show", f"HEAD:{rel}"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Supports first-generation/local use before a new artifact is committed.
        return path.read_bytes()


def _entry(repo: Path, rel: str, role: str) -> dict:
    payload = _canonical_bytes(repo, rel)
    return {
        "path": rel,
        "role": role,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _check_freeze_guard(repo: Path, status: str, candidate_sha: str | None) -> None:
    if status != "FROZEN_FOR_SUBMISSION":
        return
    if not candidate_sha or not re.fullmatch(r"[0-9a-f]{40}", candidate_sha):
        raise ValueError("FROZEN_FOR_SUBMISSION requires --candidate-sha <40-hex-sha>")

    checklist = (repo / "docs/research/PAPER_P8_REVIEW_CHECKLIST.md").read_text(encoding="utf-8")
    required_patterns = {
        "candidate": rf"^Candidate SHA: `{re.escape(candidate_sha)}`$",
        "reviewer": r"^Reviewer: \S.+$",
        "date": r"^Date: \d{4}-\d{2}-\d{2}$",
        "result": r"^Result: `PASS`$",
    }
    missing = [
        name
        for name, pattern in required_patterns.items()
        if re.search(pattern, checklist, flags=re.MULTILINE) is None
    ]
    if missing:
        raise RuntimeError(
            "P6A freeze refused: independent P8 PASS for the exact candidate is not recorded: "
            + "; ".join(missing)
        )


def build(
    repo: Path,
    *,
    status: str = "DRAFT_NOT_FROZEN",
    candidate_sha: str | None = None,
) -> dict:
    _check_freeze_guard(repo, status, candidate_sha)

    files = []
    for rel in RAW_EVIDENCE:
        files.append(_entry(repo, rel, "raw_evidence"))
    for rel in GENERATED_TABLES:
        files.append(_entry(repo, rel, "generated_table_or_table_manifest"))
    for rel in GENERATED_FIGURES:
        files.append(_entry(repo, rel, "generated_figure_or_figure_manifest"))
    for rel in GENERATORS:
        files.append(_entry(repo, rel, "generator"))
    for rel in PROTOCOL_AND_REPRO:
        files.append(_entry(repo, rel, "protocol_or_reproducibility"))
    for rel in MANUSCRIPT_INPUTS:
        files.append(_entry(repo, rel, "submission_working_source"))

    claim_audit = json.loads((repo / "paper/reproducibility/p6a_claim_audit.json").read_text(encoding="utf-8"))
    if claim_audit.get("status") != "COMPLETE_P6A_2_NOT_FROZEN":
        raise RuntimeError("P6A-2 claim audit is not complete")
    if claim_audit.get("unmapped_numeric_lines") != []:
        raise RuntimeError("P6A-2 claim audit has unmapped numerical manuscript lines")

    aggregate_entry = next(
        item for item in files
        if item["path"] == "paper/reproducibility/p3_m18c2_aggregate_35272347167.json"
    )
    if aggregate_entry["sha256"] != P3_AGGREGATE_SHA256:
        raise RuntimeError(
            "P3 aggregate hash mismatch: "
            f"expected {P3_AGGREGATE_SHA256}, got {aggregate_entry['sha256']}"
        )

    classifications = {
        "historical_m18_scientific_validation": "FAIL_PRESERVED",
        "d02_fitting": "REFERENCE_LIMITATION_MATCH",
        "d08_fitting_holdout": "REFERENCE_LIMITATION_MATCH",
        "s7_parameter_recovery": "REFERENCE_LIMITATION_MATCH",
        "s7_paired_model_selection": "PASS_PAIRED_MODEL_SELECTION_36_OF_36",
        "pyhgf_common_scope_perceptual_quantities": "PASS_11_OF_11_MAPPED_QUANTITIES",
        "pyhgf_participant_response_nll": "NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY",
        "p3_trial_horizon": "INSUFFICIENT_REFERENCE_EVIDENCE",
        "p3_gate_pass": False,
        "p3_historical_m18_unchanged": True,
        "gpu_evidence": "PASS_PHYSICAL_GPU_APPLICABILITY",
        "performance_scaling_headline_claim": "NOT_ACTIVATED_IN_PROTOCOL_1",
    }

    claim_groups = [
        {
            "id": "C1_matlab_compatibility",
            "status": "EVIDENCE_BOUND",
            "evidence": [
                "reference/validation/v1_release/evidence_manifest.json",
                "paper/tables/model_workflow_coverage.md",
                "paper/tables/matlab_demo_parity.md",
                "paper/tables/fitting_statistics_classification.md",
            ],
        },
        {
            "id": "C2_recovery_and_model_selection",
            "status": "EVIDENCE_BOUND_WITH_LIMITATIONS",
            "evidence": [
                "reference/validation/m18_s7_reference_limitation/decision.json",
                "paper/tables/recovery_model_selection.md",
                "paper/figures/fig_recovery_metrics.png",
                "paper/figures/fig_model_selection.png",
            ],
        },
        {
            "id": "C3_gpu_applicability_not_speed",
            "status": "EVIDENCE_BOUND",
            "evidence": [
                "paper/tables/backend_gpu_applicability.md",
                "paper/figures/fig_gpu_applicability.png",
            ],
        },
        {
            "id": "C4_pyhgf_common_scope",
            "status": "EVIDENCE_BOUND_WITH_NDC",
            "evidence": [
                "paper/reproducibility/p2a10_raw_numeric_result_35268575414.json",
                "paper/reproducibility/p2a10_comparison_35268575414.json",
                "paper/reproducibility/p2a10_workflow_provenance_35268575414.json",
                "paper/figures/fig_pyhgf_common_scope.png",
            ],
        },
        {
            "id": "C5_p3_trial_horizon",
            "status": "EVIDENCE_BOUND_INCONCLUSIVE",
            "evidence": [
                "paper/reproducibility/p3_m18c2_aggregate_35272347167.json",
                "paper/reproducibility/p3_m18c2_provenance_35272347167.json",
                "docs/research/P3_M18C2_RESULT.md",
                "paper/figures/fig_p3_horizon_diagnostics.png",
            ],
        },
    ]

    return {
        "schema_version": 1,
        "manifest_id": MANIFEST_ID,
        "status": status,
        "protocol_id": PROTOCOL_ID,
        "recorded_date": "2026-09-18",
        "submission_candidate_sha": candidate_sha,
        "claim_audit_status": (
            "COMPLETE_P6A_2_NOT_FROZEN" if status == "DRAFT_NOT_FROZEN" else "COMPLETE"
        ),
        "anchors": {
            "hgfx_v1_0_0_sha": HGFX_V1_SHA,
            "matlab_hgf_toolbox_8_2_0_sha": MATLAB_ORACLE_SHA,
            "pypi_stable": "hgfx==1.0.0",
            "p2a_workflow_run": P2A_RUN,
            "p3_workflow_run": P3_RUN,
            "p3_aggregate_sha256": P3_AGGREGATE_SHA256,
        },
        "freeze_policy": {
            "separate_from_m19": True,
            "m19_must_remain_unchanged": True,
            "requires_exact_submission_candidate_sha": True,
            "requires_independent_p8_pass": True,
            "draft_may_change_during_p7": True,
        },
        "regeneration_commands": [
            "python paper/scripts/generate_p2_tables.py",
            "python paper/scripts/generate_p5_figures.py",
            "python paper/scripts/generate_p6a_claim_audit.py",
            "python paper/scripts/generate_p6a_manifest.py",
            "pytest -q tests/paper/test_p2_tables.py tests/paper/test_p5_figures.py tests/paper/test_p3_evidence.py tests/paper/test_p6a_claim_audit.py tests/paper/test_p6a_manifest.py",
        ],
        "classifications": classifications,
        "claim_groups": claim_groups,
        "files": sorted(files, key=lambda item: item["path"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--status",
        choices=("DRAFT_NOT_FROZEN", "FROZEN_FOR_SUBMISSION"),
        default="DRAFT_NOT_FROZEN",
    )
    parser.add_argument("--candidate-sha")
    parser.add_argument(
        "--output",
        default="paper/reproducibility/p6a_paper_evidence_manifest.json",
    )
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    manifest = build(
        repo,
        status=args.status,
        candidate_sha=args.candidate_sha,
    )
    output = repo / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "manifest_id": manifest["manifest_id"],
                "status": manifest["status"],
                "file_count": len(manifest["files"]),
                "output": str(output.relative_to(repo)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
