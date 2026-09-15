#!/usr/bin/env python3
"""Aggregate all 12 frozen M18 S7 paired-recovery shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

PROTOCOL = "m18-s7-paired-recovery-1"
MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
CRITERIA = {
    "convergence_rate_min": 0.80,
    "median_correlation_min": 0.50,
    "median_standardized_rmse_max": 1.00,
    "model_balanced_accuracy_min": 0.50,
}


def _corr(truth: np.ndarray, fitted: np.ndarray) -> np.ndarray:
    result = np.full(truth.shape[1], np.nan, dtype=np.float64)
    for j in range(truth.shape[1]):
        x, y = truth[:, j], fitted[:, j]
        if x.size >= 2 and np.std(x) > 0.0 and np.std(y) > 0.0:
            result[j] = float(np.corrcoef(x, y)[0, 1])
    return result


def _summary(rows: list[dict], implementation: str) -> dict:
    expected = 24
    if len(rows) != expected or any(not row[implementation]["success"] for row in rows):
        return {
            "complete": False,
            "n": len(rows),
            "expected": expected,
            "failed_cases": [row["case_id"] for row in rows if not row[implementation]["success"]],
            "checks": {},
        }
    truth = np.asarray([row["truth_free"] for row in rows], dtype=np.float64)
    fitted = np.asarray([row[implementation]["final_free"] for row in rows], dtype=np.float64)
    if truth.shape != fitted.shape:
        return {"complete": False, "n": len(rows), "expected": expected, "shape_mismatch": True, "checks": {}}
    error = fitted - truth
    rmse = np.sqrt(np.mean(error**2, axis=0))
    scales = np.std(truth, axis=0, ddof=0)
    standardized = rmse / np.where(scales > 1e-12, scales, 1.0)
    corr = _corr(truth, fitted)
    finite_corr = corr[np.isfinite(corr)]
    convergence = float(np.mean([bool(row[implementation]["converged"]) for row in rows]))
    median_corr = float(np.median(finite_corr)) if finite_corr.size else None
    median_srmse = float(np.median(standardized))
    checks = {
        "convergence_rate": convergence >= CRITERIA["convergence_rate_min"],
        "median_correlation": median_corr is not None and median_corr >= CRITERIA["median_correlation_min"],
        "median_standardized_rmse": median_srmse <= CRITERIA["median_standardized_rmse_max"],
    }
    return {
        "complete": True,
        "n": len(rows),
        "bias": np.mean(error, axis=0).tolist(),
        "rmse": rmse.tolist(),
        "correlation": corr.tolist(),
        "median_absolute_error": np.median(np.abs(error), axis=0).tolist(),
        "standardized_rmse": standardized.tolist(),
        "convergence_rate": convergence,
        "median_correlation": median_corr,
        "median_standardized_rmse": median_srmse,
        "checks": checks,
        "scientific_pass": bool(all(checks.values())),
    }


def _balanced_accuracy(rows: list[dict], selected_key: str) -> tuple[float, list[list[float]]]:
    matrix = np.zeros((3, 3), dtype=np.float64)
    index = {name: i for i, name in enumerate(MODELS)}
    for row in rows:
        generator = row["generating_model"]
        selected = row[selected_key]
        if generator in index and selected in index:
            matrix[index[generator], index[selected]] += 1.0
    for i in range(3):
        total = float(np.sum(matrix[i]))
        if total:
            matrix[i] /= total
    return float(np.mean(np.diag(matrix))), matrix.tolist()


def main(input_dir: str, output_path: str) -> int:
    paths = sorted(Path(input_dir).rglob("*comparison*.json"))
    if not paths:
        raise ValueError("No S7 comparison JSON files found")
    shards = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if any(shard.get("protocol") != PROTOCOL for shard in shards):
        raise ValueError("mixed/non-S7 protocol artifacts")

    parameter_rows = [row for shard in shards for row in shard["parameter_results"]]
    model_rows = [row for shard in shards for row in shard["model_results"]]
    unique_parameter = {row["case_id"] for row in parameter_rows}
    unique_model = {row["case_id"] for row in model_rows}
    coverage = {
        "shards": len(shards),
        "expected_shards": 12,
        "parameter_cases": len(parameter_rows),
        "unique_parameter_cases": len(unique_parameter),
        "expected_parameter_cases": 72,
        "model_cases": len(model_rows),
        "unique_model_cases": len(unique_model),
        "expected_model_cases": 36,
    }
    coverage_pass = (
        len(shards) == 12
        and len(parameter_rows) == len(unique_parameter) == 72
        and len(model_rows) == len(unique_model) == 36
    )

    parameter_by_model = {}
    parameter_classifications = []
    for model in MODELS:
        rows = [row for row in parameter_rows if row["model"] == model]
        matlab = _summary(rows, "matlab")
        hgfx = _summary(rows, "hgfx")
        if not matlab.get("complete") or not hgfx.get("complete"):
            classification = "INSUFFICIENT_REFERENCE_EVIDENCE"
        elif matlab["checks"] != hgfx["checks"]:
            classification = "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"
        elif matlab["scientific_pass"] and hgfx["scientific_pass"]:
            classification = "PASS_PAIRED_RECOVERY_BEHAVIOR"
        else:
            classification = "PAIRED_REFERENCE_LIMITATION_CANDIDATE"
        parameter_classifications.append(classification)
        parameter_by_model[model] = {
            "matlab": matlab,
            "hgfx": hgfx,
            "classification": classification,
        }

    if all(c == "PASS_PAIRED_RECOVERY_BEHAVIOR" for c in parameter_classifications):
        parameter_overall = "PASS_PAIRED_RECOVERY_BEHAVIOR"
    elif all(c in {"PASS_PAIRED_RECOVERY_BEHAVIOR", "PAIRED_REFERENCE_LIMITATION_CANDIDATE"} for c in parameter_classifications):
        parameter_overall = "PAIRED_REFERENCE_LIMITATION_REVIEW_REQUIRED"
    elif "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH" in parameter_classifications:
        parameter_overall = "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"
    else:
        parameter_overall = "INSUFFICIENT_REFERENCE_EVIDENCE"

    winners_match = [bool(row["winner_match"]) for row in model_rows]
    matlab_bacc, matlab_matrix = _balanced_accuracy(model_rows, "matlab_selected_model")
    hgfx_bacc, hgfx_matrix = _balanced_accuracy(model_rows, "hgfx_selected_model")
    model_complete = len(model_rows) == 36 and all(
        row["matlab_selected_model"] and row["hgfx_selected_model"] for row in model_rows
    )
    if not model_complete:
        model_classification = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif all(winners_match):
        model_classification = "PASS_PAIRED_MODEL_SELECTION"
    else:
        model_classification = "MODEL_SELECTION_MISMATCH"

    if (
        coverage_pass
        and parameter_overall == "PASS_PAIRED_RECOVERY_BEHAVIOR"
        and model_classification == "PASS_PAIRED_MODEL_SELECTION"
    ):
        s7_classification = "PASS_PAIRED_RECOVERY"
    elif (
        coverage_pass
        and parameter_overall == "PAIRED_REFERENCE_LIMITATION_REVIEW_REQUIRED"
        and model_classification == "PASS_PAIRED_MODEL_SELECTION"
    ):
        s7_classification = "REFERENCE_LIMITATION_REVIEW_REQUIRED"
    elif not coverage_pass:
        s7_classification = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif model_classification == "MODEL_SELECTION_MISMATCH":
        s7_classification = "MODEL_SELECTION_MISMATCH"
    else:
        s7_classification = "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"

    payload = {
        "protocol": PROTOCOL,
        "criteria": CRITERIA,
        "coverage": coverage,
        "coverage_pass": coverage_pass,
        "parameter_recovery": parameter_by_model,
        "parameter_classification": parameter_overall,
        "model_recovery": {
            "winner_matches": int(sum(winners_match)),
            "total_cases": len(model_rows),
            "all_winners_match": bool(model_rows and all(winners_match)),
            "matlab_balanced_accuracy": matlab_bacc,
            "hgfx_balanced_accuracy": hgfx_bacc,
            "matlab_confusion_matrix": matlab_matrix,
            "hgfx_confusion_matrix": hgfx_matrix,
            "matlab_scientific_pass": matlab_bacc >= CRITERIA["model_balanced_accuracy_min"],
            "hgfx_scientific_pass": hgfx_bacc >= CRITERIA["model_balanced_accuracy_min"],
            "mismatched_cases": [row["case_id"] for row in model_rows if not row["winner_match"]],
            "classification": model_classification,
        },
        "s7_classification": s7_classification,
        "gate_pass": s7_classification == "PASS_PAIRED_RECOVERY",
        "integrity_note": "REFERENCE_LIMITATION_REVIEW_REQUIRED is not an automatic accepted limitation; exact paired raw evidence must be reviewed under the frozen reference-limitations policy before release accounting.",
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "coverage_pass": coverage_pass,
        "parameter_classification": parameter_overall,
        "model_classification": model_classification,
        "s7_classification": s7_classification,
        "gate_pass": payload["gate_pass"],
    }, indent=2))
    return 0 if payload["gate_pass"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.input_dir, args.output))
