#!/usr/bin/env python3
"""Aggregate 24 frozen M18C.2 paired-horizon shards and classify 256→1024."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from hgfx.diagnostics.horizon import (
    CRITERIA,
    MODELS,
    PROTOCOL,
    TRIAL_HORIZONS,
    classify_horizon_evidence,
    parameter_check_flags,
)

EXPECTED_SHARDS = 24
EXPECTED_PARAMETER = 144
EXPECTED_MODEL = 72
ROWS_PER_MODEL_HORIZON = 12  # 2 scales × 6 replicates


def _corr(truth: np.ndarray, fitted: np.ndarray) -> np.ndarray:
    result = np.full(truth.shape[1], np.nan, dtype=np.float64)
    for j in range(truth.shape[1]):
        x, y = truth[:, j], fitted[:, j]
        if x.size >= 2 and np.std(x) > 0.0 and np.std(y) > 0.0:
            result[j] = float(np.corrcoef(x, y)[0, 1])
    return result


def _summary(rows: list[dict], implementation: str, expected: int) -> dict:
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
    numeric = {
        "convergence_rate": convergence,
        "median_correlation": median_corr,
        "median_standardized_rmse": median_srmse,
    }
    checks = parameter_check_flags(numeric)
    return {
        "complete": True,
        "n": len(rows),
        "bias": np.mean(error, axis=0).tolist(),
        "rmse": rmse.tolist(),
        "correlation": corr.tolist(),
        "median_absolute_error": np.median(np.abs(error), axis=0).tolist(),
        "standardized_rmse": standardized.tolist(),
        **numeric,
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
        raise ValueError("No M18C.2 comparison JSON files found")
    shards = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if any(shard.get("protocol") != PROTOCOL for shard in shards):
        raise ValueError("mixed/non-M18C.2 protocol artifacts")

    parameter_rows = [row for shard in shards for row in shard["parameter_results"]]
    model_rows = [row for shard in shards for row in shard["model_results"]]
    unique_parameter = {row["case_id"] for row in parameter_rows}
    unique_model = {row["case_id"] for row in model_rows}
    contract_ok = all(row["diagnostic"]["contract_free_indices_match"] for row in parameter_rows)
    winners_match = [bool(row["winner_match"]) for row in model_rows]
    coverage = {
        "shards": len(shards),
        "expected_shards": EXPECTED_SHARDS,
        "parameter_cases": len(parameter_rows),
        "unique_parameter_cases": len(unique_parameter),
        "expected_parameter_cases": EXPECTED_PARAMETER,
        "model_cases": len(model_rows),
        "unique_model_cases": len(unique_model),
        "expected_model_cases": EXPECTED_MODEL,
        "contract_free_indices_match": contract_ok,
        "all_winners_match": bool(model_rows and all(winners_match)),
    }
    coverage_pass = (
        len(shards) == EXPECTED_SHARDS
        and len(parameter_rows) == len(unique_parameter) == EXPECTED_PARAMETER
        and len(model_rows) == len(unique_model) == EXPECTED_MODEL
        and contract_ok
    )

    by_model: dict[str, dict] = {}
    classifications: dict[str, str] = {}
    criterion_mismatch = False
    for model in MODELS:
        horizons: dict[str, dict] = {}
        for trials in TRIAL_HORIZONS:
            rows = [
                row
                for row in parameter_rows
                if row["model"] == model and int(row["trial_count"]) == trials
            ]
            matlab = _summary(rows, "matlab", ROWS_PER_MODEL_HORIZON)
            hgfx = _summary(rows, "hgfx", ROWS_PER_MODEL_HORIZON)
            if matlab.get("complete") and hgfx.get("complete") and matlab["checks"] != hgfx["checks"]:
                criterion_mismatch = True
            horizons[str(trials)] = {"matlab": matlab, "hgfx": hgfx}
        paired_ok = (
            coverage_pass
            and not criterion_mismatch
            and bool(model_rows and all(winners_match))
        )
        checks_256 = horizons["256"]["matlab"].get("checks") or None
        checks_1024 = horizons["1024"]["matlab"].get("checks") or None
        if checks_256 == {}:
            checks_256 = None
        if checks_1024 == {}:
            checks_1024 = None
        label = classify_horizon_evidence(
            paired_integrity_pass=paired_ok,
            checks_256=checks_256,
            checks_1024=checks_1024,
        )
        classifications[model] = label
        by_model[model] = {"horizons": horizons, "classification": label}

    matlab_bacc_by_h = {}
    hgfx_bacc_by_h = {}
    for trials in TRIAL_HORIZONS:
        rows = [row for row in model_rows if int(row["trial_count"]) == trials]
        matlab_bacc, matlab_matrix = _balanced_accuracy(rows, "matlab_selected_model")
        hgfx_bacc, hgfx_matrix = _balanced_accuracy(rows, "hgfx_selected_model")
        matlab_bacc_by_h[str(trials)] = {
            "balanced_accuracy": matlab_bacc,
            "confusion_matrix": matlab_matrix,
            "scientific_pass": matlab_bacc >= CRITERIA["model_balanced_accuracy_min"],
        }
        hgfx_bacc_by_h[str(trials)] = {
            "balanced_accuracy": hgfx_bacc,
            "confusion_matrix": hgfx_matrix,
            "scientific_pass": hgfx_bacc >= CRITERIA["model_balanced_accuracy_min"],
        }

    if not coverage_pass:
        overall = "INSUFFICIENT_REFERENCE_EVIDENCE"
    elif criterion_mismatch or not all(winners_match):
        overall = "IMPLEMENTATION_OR_OPTIMIZER_MISMATCH"
    else:
        labels = set(classifications.values())
        if labels == {"NO_256_FAILURE_TO_EXPLAIN"}:
            overall = "NO_256_FAILURE_TO_EXPLAIN"
        elif labels == {"DATA_HORIZON_LIMITATION_SUPPORTED"}:
            overall = "DATA_HORIZON_LIMITATION_SUPPORTED"
        elif labels == {"PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED"}:
            overall = "PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED"
        else:
            overall = "MIXED_HORIZON_EFFECT_INCONCLUSIVE"

    payload = {
        "protocol": PROTOCOL,
        "criteria": CRITERIA,
        "coverage": coverage,
        "coverage_pass": coverage_pass,
        "parameter_recovery": by_model,
        "model_recovery": {
            "winner_matches": int(sum(winners_match)),
            "total_cases": len(model_rows),
            "all_winners_match": bool(model_rows and all(winners_match)),
            "matlab_by_horizon": matlab_bacc_by_h,
            "hgfx_by_horizon": hgfx_bacc_by_h,
            "mismatched_cases": [row["case_id"] for row in model_rows if not row["winner_match"]],
        },
        "per_model_classification": classifications,
        "overall_classification": overall,
        "historical_m18_unchanged": True,
        "gate_pass": coverage_pass,  # completeness, not scientific PASS
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "coverage_pass": coverage_pass,
        "overall_classification": overall,
        "per_model_classification": classifications,
    }, indent=2))
    return 0 if coverage_pass else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.input_dir, args.output))
