#!/usr/bin/env python3
"""Classify fresh S7 aggregate evidence for release accounting.

The raw S7 aggregator intentionally treats a paired MATLAB/HGFX scientific
limitation as REVIEW_REQUIRED. This tool applies the separately frozen review
decision without converting that limitation into a scientific PASS.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROTOCOL = "m18-s7-paired-recovery-1"
FROZEN_MATLAB_REFERENCE = "2437f4dc241541072722a2695ddeca7b44d83dd3"
MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")


def _failed_checks(summary: dict[str, Any]) -> list[str]:
    checks = summary.get("checks", {})
    return sorted(name for name, passed in checks.items() if passed is False)


def classify_release(aggregate: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []

    raw_gate_pass = aggregate.get("gate_pass") is True
    raw_classification = aggregate.get("s7_classification")

    # A genuine direct scientific PASS requires no limitation override.
    if raw_gate_pass and raw_classification == "PASS_PAIRED_RECOVERY":
        return {
            "protocol": aggregate.get("protocol"),
            "raw_gate_pass": True,
            "raw_classification": raw_classification,
            "release_gate_pass": True,
            "release_classification": "PASS_PAIRED_RECOVERY",
            "scientific_pass": True,
            "product_equivalence_closed": True,
            "failures": [],
        }

    if aggregate.get("protocol") != PROTOCOL:
        failures.append("aggregate protocol does not match frozen S7 protocol")
    if decision.get("protocol") != PROTOCOL:
        failures.append("decision protocol does not match frozen S7 protocol")
    if decision.get("reference_commit") != FROZEN_MATLAB_REFERENCE:
        failures.append("decision frozen MATLAB reference commit does not match")

    if raw_classification != "REFERENCE_LIMITATION_REVIEW_REQUIRED":
        failures.append(f"raw S7 classification is not reviewable: {raw_classification!r}")
    if aggregate.get("parameter_classification") != "PAIRED_REFERENCE_LIMITATION_REVIEW_REQUIRED":
        failures.append("raw parameter classification is not the frozen review-required class")
    if aggregate.get("coverage_pass") is not True:
        failures.append("fresh S7 coverage did not pass")

    if decision.get("decision") != "REFERENCE_LIMITATION_MATCH":
        failures.append("frozen decision is not REFERENCE_LIMITATION_MATCH")
    if decision.get("status") != "RELEASE_ACCEPTABLE_EXACT_PROTOCOL_SCOPE":
        failures.append("frozen decision is not release-acceptable in exact protocol scope")
    if decision.get("scientific_pass") is not False:
        failures.append("frozen limitation decision must preserve scientific_pass=false")
    if decision.get("product_equivalence_closed") is not True:
        failures.append("frozen decision does not close product equivalence")

    if aggregate.get("criteria") != decision.get("criteria_unchanged"):
        failures.append("fresh S7 criteria differ from frozen decision criteria")

    coverage = aggregate.get("coverage", {})
    frozen_coverage = decision.get("coverage", {})
    expected_coverage = {
        "shards": 12,
        "parameter_cases": 72,
        "model_cases": 36,
    }
    for key, expected in expected_coverage.items():
        if coverage.get(key) != expected:
            failures.append(f"fresh S7 coverage {key}={coverage.get(key)!r}, expected {expected}")
    if coverage.get("unique_parameter_cases") != 72 or coverage.get("unique_model_cases") != 36:
        failures.append("fresh S7 coverage contains missing or duplicate cases")
    if frozen_coverage.get("shards") != 12 or frozen_coverage.get("parameter_cases") != 72:
        failures.append("frozen decision coverage does not match 12-shard/72-case protocol")
    if frozen_coverage.get("model_recovery_datasets") != 36:
        failures.append("frozen decision model-recovery coverage does not match 36 datasets")
    if tuple(frozen_coverage.get("models", ())) != MODELS:
        failures.append("frozen decision model set differs from S7 protocol")

    current_parameters = aggregate.get("parameter_recovery", {})
    frozen_parameters = decision.get("parameter_recovery", {})
    for model in MODELS:
        current = current_parameters.get(model, {})
        frozen = frozen_parameters.get(model, {})
        if current.get("classification") != "PAIRED_REFERENCE_LIMITATION_CANDIDATE":
            failures.append(f"{model}: current parameter classification is not a limitation candidate")
        if frozen.get("classification") != "REFERENCE_LIMITATION_MATCH":
            failures.append(f"{model}: frozen parameter decision is not REFERENCE_LIMITATION_MATCH")

        matlab = current.get("matlab", {})
        hgfx = current.get("hgfx", {})
        if matlab.get("complete") is not True or hgfx.get("complete") is not True:
            failures.append(f"{model}: incomplete MATLAB/HGFX parameter evidence")
        if matlab.get("scientific_pass") is not False or hgfx.get("scientific_pass") is not False:
            failures.append(f"{model}: expected paired scientific limitation is no longer reproduced")
        if matlab.get("checks") != hgfx.get("checks"):
            failures.append(f"{model}: MATLAB/HGFX check pattern differs")

        current_failed = _failed_checks(matlab)
        frozen_failed = sorted(frozen.get("shared_failed_criteria", []))
        if current_failed != frozen_failed:
            failures.append(
                f"{model}: current failed criteria {current_failed!r} differ from frozen {frozen_failed!r}"
            )

    current_model = aggregate.get("model_recovery", {})
    frozen_model = decision.get("model_recovery", {})
    if current_model.get("classification") != "PASS_PAIRED_MODEL_SELECTION":
        failures.append("fresh model recovery is not PASS_PAIRED_MODEL_SELECTION")
    if frozen_model.get("classification") != "PASS_PAIRED_MODEL_SELECTION":
        failures.append("frozen model-recovery decision is not PASS_PAIRED_MODEL_SELECTION")
    if current_model.get("winner_matches") != 36 or current_model.get("total_cases") != 36:
        failures.append("fresh model recovery does not contain 36/36 winner matches")
    if current_model.get("all_winners_match") is not True or current_model.get("mismatched_cases") != []:
        failures.append("fresh model recovery contains model-selection mismatch")
    if frozen_model.get("winner_matches") != 36 or frozen_model.get("total_cases") != 36:
        failures.append("frozen model-recovery decision does not record 36/36 winner matches")
    if frozen_model.get("mismatched_cases") != []:
        failures.append("frozen model-recovery decision contains mismatched cases")
    if current_model.get("matlab_balanced_accuracy") != frozen_model.get("matlab_balanced_accuracy"):
        failures.append("fresh MATLAB model-recovery balanced accuracy differs from frozen decision")
    if current_model.get("hgfx_balanced_accuracy") != frozen_model.get("hgfx_balanced_accuracy"):
        failures.append("fresh HGFX model-recovery balanced accuracy differs from frozen decision")

    integrity = decision.get("evidence_integrity", {})
    for key in (
        "unresolved_required_scope_implementation_mismatch",
        "unresolved_required_scope_optimizer_mismatch",
        "unresolved_required_scope_model_selection_mismatch",
    ):
        if integrity.get(key) is not False:
            failures.append(f"frozen decision integrity does not close {key}")

    release_pass = not failures
    return {
        "protocol": aggregate.get("protocol"),
        "raw_gate_pass": raw_gate_pass,
        "raw_classification": raw_classification,
        "release_gate_pass": release_pass,
        "release_classification": "REFERENCE_LIMITATION_MATCH" if release_pass else "FAIL",
        "scientific_pass": False,
        "product_equivalence_closed": release_pass,
        "failures": failures,
    }


def main(aggregate_path: str, decision_path: str, output_path: str) -> int:
    aggregate = json.loads(Path(aggregate_path).read_text(encoding="utf-8"))
    decision = json.loads(Path(decision_path).read_text(encoding="utf-8"))
    result = classify_release(aggregate, decision)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["release_gate_pass"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("aggregate")
    parser.add_argument("decision")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.aggregate, args.decision, args.output))
