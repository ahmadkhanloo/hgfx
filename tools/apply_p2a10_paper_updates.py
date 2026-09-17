#!/usr/bin/env python3
"""Synchronize paper-facing P2A text from the committed P2A.10 evidence.

This script does not recompute or alter the scientific result. It first validates the
committed comparison/provenance decision, then applies exact textual replacements.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARISON = ROOT / "paper/reproducibility/p2a10_comparison_35268575414.json"
PROVENANCE = ROOT / "paper/reproducibility/p2a10_workflow_provenance_35268575414.json"
MANUSCRIPT = ROOT / "paper/manuscript.md"
EVIDENCE_MAP = ROOT / "docs/research/PAPER_EVIDENCE_MAP.md"
EXECUTION_PLAN = ROOT / "docs/research/PAPER_EXECUTION_PLAN.md"

EXPECTED_RAW_HASH = "202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b"
EXPECTED_OVERALL = "PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES"
EXPECTED_RUN = 35268575414


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def validate_evidence() -> dict:
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if comparison.get("overall_classification") != EXPECTED_OVERALL:
        raise RuntimeError("unexpected P2A.10 overall classification")
    if comparison.get("raw_result_sha256") != EXPECTED_RAW_HASH:
        raise RuntimeError("unexpected raw-result hash")
    if comparison.get("raw_result_verified_before_interpretation") is not True:
        raise RuntimeError("raw result was not verified before interpretation")
    if comparison.get("post_result_changes_applied") is not False:
        raise RuntimeError("post-result scientific changes are recorded")
    if provenance.get("scientific_run_id") != EXPECTED_RUN:
        raise RuntimeError("unexpected scientific run id")
    if provenance.get("embedded_raw_result_sha256") != EXPECTED_RAW_HASH:
        raise RuntimeError("provenance/raw hash disagreement")
    if provenance.get("byte_for_byte_artifact_copy") is not True:
        raise RuntimeError("artifact was not preserved byte-for-byte")

    classes = [v["classification"] for v in comparison["field_results"].values()]
    if classes.count("PASS_FOR_EXECUTED_QUANTITY") != 11:
        raise RuntimeError("expected 11 directly passing common-scope quantities")
    if classes.count("NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY") != 2:
        raise RuntimeError("expected 2 response-NLL NDC quantities")
    return comparison


def update_manuscript() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")

    anchor = (
        "This classification scheme prevents product-compatibility acceptance from being confused with scientific identifiability or parameter-recovery success.\n\n"
        "## 3. Validation methodology"
    )
    replacement = (
        "This classification scheme prevents product-compatibility acceptance from being confused with scientific identifiability or parameter-recovery success.\n\n"
        "### 2.4 Relationship to pyhgf\n\n"
        "pyhgf is an established Python/JAX HGF-related library that represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference workflows [@legrand2026pyhgf]. HGFX and pyhgf therefore overlap scientifically, but their design centers are not identical. HGFX v1.0 is organized around behavioral compatibility with a frozen MATLAB HGF Toolbox 8.2.0 oracle and explicit cross-language validation/provenance, whereas pyhgf emphasizes generalized network construction and extensibility. We treat these as design differences rather than a ranking.\n\n"
        "For empirical positioning, `pyhgf==0.3.2` was pinned before execution and a direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. Quantities without a defensible common semantic/numerical surface are reported as not directly comparable rather than forced into a winner/loser comparison.\n\n"
        "## 3. Validation methodology"
    )
    text = replace_once(text, anchor, replacement, "manuscript related work")

    anchor = "### 3.7 Independent review and release freeze"
    replacement = (
        "### 3.7 Prospectively frozen pyhgf common-scope comparison\n\n"
        "The external-comparator cell used `hgfx==1.0.0` and `pyhgf==0.3.2` in an Ubuntu 24.04 CPU environment with Python 3.12.14, NumPy 2.3.3, JAX/JAXLIB 0.6.2, JAX x64 enabled, and float64 mapped arrays. The test case was a fixed-parameter three-level binary HGF with standard volatility updates, mean-field updates, unit value/volatility coupling, zero drift, fully observed binary input, and unit time. The explicit 128-trial input and response arrays, package identities, inverse temperature, output fields, guards, and tolerances were committed before any cross-tool numerical output was inspected.\n\n"
        "Trajectory and per-trial quantities used prospectively frozen `atol=1e-10` and `rtol=1e-8`; participant-response total NLL used `atol=1e-7` and `rtol=1e-8`. The raw per-implementation arrays and boundary diagnostics were written first, assigned a canonical SHA-256, reopened and verified, and only then interpreted. The protocol also prospectively specified that a derived surprise/response-NLL boundary nonfinite would be `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`, rather than triggering post-result clipping or tolerance changes.\n\n"
        "### 3.8 Independent review and release freeze"
    )
    text = replace_once(text, anchor, replacement, "manuscript comparator methods")

    anchor = "### 4.5 Reproducibility and provenance"
    replacement = (
        "### 4.5 Frozen common-scope comparison with pyhgf\n\n"
        "In the prospectively frozen 128-trial comparator case, all 11 mapped perceptual/inference quantities passed their predeclared tolerances. Maximum absolute differences were at binary64 rounding scale: `1.1102230246251565e-16` for first-level predicted probability, `4.440892098500626e-16` for level-2 means, `6.661338147750939e-16` for level-2 precisions, and `1.5543122344752192e-15` for level-3 precisions. Derived first-level prediction error and input surprise also passed, with maximum absolute differences of `1.1102230246251565e-16` and `4.440892098500626e-16`, respectively. Observed-input integrity was exact.\n\n"
        "The retained participant-response NLL surface was not directly comparable under the frozen numerical construction. With inverse temperature `ze=48`, the explicit power-ratio response transformation on the pyhgf side reached an exact probability boundary on 13 trials and the unclipped surprise became `+Inf`; the HGFX log-domain `unitsq_sgm` evaluation remained finite, with total NLL `1808.855415351429`. Because the pre-execution protocol had already classified response-NLL boundary nonfinites as `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`, no clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. The overall comparator classification is therefore `PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES`, not general tool equivalence.\n\n"
        "### 4.6 Reproducibility and provenance"
    )
    text = replace_once(text, anchor, replacement, "manuscript comparator results")

    anchor = (
        "The strongest current contribution is thus methodological: a Python/JAX reproduction process that makes the reference oracle, evidence classifications, numerical compatibility policy, historical failures, and release provenance explicit."
    )
    replacement = (
        "The external pyhgf comparison reinforces the value of quantity-specific compatibility claims. The mapped HGF belief trajectories agree to binary64 rounding scale in the single authorized common-scope case, while the response-NLL surface exposes a numerical-boundary difference despite sharing the same underlying predicted belief. Preserving the prospectively defined `NOT_DIRECTLY_COMPARABLE` outcome is more informative than changing clipping or reformulating the response computation after inspecting the result.\n\n"
        + anchor
    )
    text = replace_once(text, anchor, replacement, "manuscript discussion")

    anchor = (
        "Fifth, the current working manuscript still requires generated paper tables/figures, a complete paper-specific reproduction bundle, final author/affiliation metadata, target-journal formatting, and an independent pre-submission review."
    )
    replacement = (
        "Fifth, the direct pyhgf evidence is intentionally narrow: one fixed-parameter, fully observed, three-level binary-HGF case under an explicitly mapped standard/mean-field configuration. It supports the reported common-scope trajectory result but not general equivalence across model families, fitting workflows, missing-data semantics, observation models, or package capabilities. The participant-response NLL surface is explicitly retained as not directly comparable under the frozen numerical construction.\n\n"
        "Sixth, the current working manuscript still requires generated paper tables/figures, a complete paper-specific reproduction bundle, final author/affiliation metadata, target-journal formatting, and an independent pre-submission review."
    )
    text = replace_once(text, anchor, replacement, "manuscript limitations")

    anchor = (
        "Before submission, `paper/reproducibility/` will contain the frozen paper protocol, exact environment manifests, commands, evidence-input hashes, and table/figure regeneration instructions."
    )
    replacement = (
        "`paper/reproducibility/` now includes the frozen paper protocol and the P2A external-comparator case, authorization gate, byte-for-byte raw numerical result, post-hash comparison artifact, exact resolved environment, and workflow/artifact provenance. Before submission, the remaining selected paper outputs must receive the same input-hash and regeneration treatment, followed by the final `FROZEN_FOR_SUBMISSION` evidence manifest."
    )
    text = replace_once(text, anchor, replacement, "manuscript reproducibility")

    MANUSCRIPT.write_text(text, encoding="utf-8")


def update_evidence_map() -> None:
    text = EVIDENCE_MAP.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "Status: **ACTIVE / POST-M19 / v1.0.0 FROZEN / PAPER PROTOCOL FROZEN / P2 TABLES PASS / PAPER EVIDENCE OPEN**",
        "Status: **ACTIVE / POST-M19 / v1.0.0 FROZEN / PAPER PROTOCOL FROZEN / P2 TABLES PASS / P2A COMMON-SCOPE COMPLETE / PAPER EVIDENCE OPEN**",
        "evidence-map status",
    )
    text = replace_once(
        text,
        "| HGFX is generally more accurate/faster/better than pyhgf | **NOT SUPPORTED** | prohibited without direct prospectively frozen common-scope evidence; protocol 1 explicitly forbids a general superiority claim |",
        "| HGFX is generally more accurate/faster/better than pyhgf | **NOT SUPPORTED** | P2A supplies one prospectively frozen common-scope numerical result, but it does not support a general superiority, speed, or package-wide equivalence claim |",
        "evidence-map superiority row",
    )
    text = replace_once(
        text,
        "| A fair common-scope HGFX↔pyhgf comparison is complete | **OPEN / REQUIRED FOR POSITIONING** | PV1-02A / issue #33; comparator is pinned, but semantic overlap mapping and any valid common-scope result remain open; `NOT_DIRECTLY_COMPARABLE` is allowed |",
        "| A fair common-scope HGFX↔pyhgf comparison is complete | **READY / SCOPED** | P2A.2–P2A.10; frozen case `p2a9-binary-hgf-common-scope-001`; run `35268575414`; 11/11 mapped perceptual/inference quantities PASS; response-NLL per-trial/total retained as `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` |\n| The frozen common-scope perceptual trajectories establish general HGFX↔pyhgf equivalence | **REJECTED** | the observed binary64-scale agreement applies only to the authorized three-level binary-HGF cell; model families, fitting, masking/missingness, observation surfaces and broader capabilities remain outside this direct claim |\n| Participant-response NLL directly matches pyhgf under the frozen P2A case | **NOT SUPPORTED / NDC** | pyhgf-derived unclipped response NLL reaches `+Inf` on 13 trials under the frozen `ze=48` power-ratio transformation; HGFX remains finite; predeclared classification is `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` |",
        "evidence-map common-scope rows",
    )

    old = (
        "Paper protocol 1 freezes `pyhgf==0.3.2` as the comparator identity. The manuscript must compare the project goals neutrally. The feature matrix may include non-overlapping capabilities, but empirical numerical comparison is permitted only after a committed semantic mapping passes the protocol gate for the intended scientific quantity. `NOT_DIRECTLY_COMPARABLE` is an acceptable and scientifically preferable result to a forced ranking."
    )
    new = (
        "Paper protocol 1 freezes `pyhgf==0.3.2` as the comparator identity. The P2A semantic chain subsequently authorized exactly one fixed-parameter, fully observed three-level binary-HGF cell. Run `35268575414` preserved a canonical raw result before interpretation (`raw_result_sha256=202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b`). All 11 mapped perceptual/inference quantities pass their prospectively frozen tolerances with maximum absolute errors between approximately `1.1e-16` and `1.6e-15`. The two response-NLL quantities are retained as `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` because the frozen pyhgf-side response transformation reaches `+Inf` on 13 trials while the HGFX log-domain formulation remains finite. No post-result clipping, formula, dtype, parameter, input, version or tolerance change was made. This scoped result does not rank the packages or imply general equivalence."
    )
    text = replace_once(text, old, new, "evidence-map pyhgf interpretation")

    anchor = "- `paper/reproducibility/PAPER_PROTOCOL.md`\n"
    addition = (
        "- `docs/research/PYHGF_COMMON_SCOPE_NUMERICAL_RESULT.md`\n"
        "- `paper/reproducibility/p2a10_raw_numeric_result_35268575414.json`\n"
        "- `paper/reproducibility/p2a10_comparison_35268575414.json`\n"
        "- `paper/reproducibility/p2a10_workflow_provenance_35268575414.json`\n"
    )
    text = replace_once(text, anchor, anchor + addition, "evidence-map source list")

    text = replace_once(
        text,
        "- PV1-02A pyhgf semantic mapping and any valid common-scope empirical outputs;",
        "- generated P2A comparison table/figure only if selected for the final manuscript; semantic mapping and the valid common-scope empirical outputs are now committed;",
        "evidence-map remaining work",
    )
    EVIDENCE_MAP.write_text(text, encoding="utf-8")


def update_execution_plan() -> None:
    text = EXECUTION_PLAN.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "Status: **IN PROGRESS — P1/P2 DONE; P2A/P3 ACTIVE NEXT**",
        "Status: **IN PROGRESS — P1/P2/P2A DONE; P3 ACTIVE NEXT**",
        "execution-plan status",
    )
    text = replace_once(
        text,
        "**Status:** OPEN / HIGH PRIORITY FOR SUBMISSION POSITIONING.",
        "**Status:** DONE / PASS WITH SCOPED RESPONSE-NLL NDC.\n\nCompletion evidence:\n- P2A.1–P2A.9 froze the feature/design matrix, semantic mappings, numerical policy and exact common-scope case before execution;\n- P2A.10 scientific run `35268575414` executed `p2a9-binary-hgf-common-scope-001` without changing the frozen protocol;\n- 11/11 mapped perceptual/inference quantities are `PASS_FOR_EXECUTED_QUANTITY`;\n- participant-response NLL per-trial and total are `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` under the predeclared boundary-nonfinite policy;\n- raw result was hash-verified before interpretation and preserved byte-for-byte with exact environment/workflow provenance;\n- no general accuracy, performance or superiority conclusion is drawn.",
        "execution-plan P2A status",
    )
    anchor = (
        "Acceptance:\n- manuscript contains a neutral related-work section;\n- no first/only-Python-HGF claim remains;\n- no superiority claim appears without direct prospective evidence;\n- empirical comparison, if executed, follows the frozen paper protocol."
    )
    replacement = (
        anchor
        + "\n\nAcceptance result: **PASS**. The manuscript/evidence map now report the prospectively frozen scoped result, including the response-NLL NDC outcome without post-result retuning."
    )
    text = replace_once(text, anchor, replacement, "execution-plan P2A acceptance")
    EXECUTION_PLAN.write_text(text, encoding="utf-8")


def main() -> int:
    validate_evidence()
    update_manuscript()
    update_evidence_map()
    update_execution_plan()
    print("P2A.10 paper synchronization: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
