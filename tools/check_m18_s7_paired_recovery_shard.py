#!/usr/bin/env python3
"""Run HGFX on one frozen S7 shard and compare to MATLAB raw fits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hgfx.diagnostics.recovery import BINARY_VARIANTS, fit_binary_variant
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

PROTOCOL = "m18-s7-paired-recovery-1"


def _normalise(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def _array(value: Any) -> np.ndarray:
    if isinstance(value, dict) and value.get("hgfx_numeric") == "ieee-strings-v1":
        shape = value["shape"]
        return np.asarray(_normalise(value["data"]), dtype=np.float64).reshape(shape, order="F")
    if value is None:
        return np.asarray(np.nan, dtype=np.float64)
    return np.asarray(_normalise(value), dtype=np.float64)


def _scalar(value: Any) -> float:
    arr = _array(value).reshape(-1)
    return float(arr[0]) if arr.size else float("nan")


def _fit(model: str, y, u) -> dict[str, Any]:
    try:
        fit = fit_binary_variant(
            np.asarray(y, dtype=np.float64),
            np.asarray(u, dtype=np.float64),
            model,
            options=QuasiNewtonOptions(max_iter=100),
        )
        return {
            "model": model,
            "success": True,
            "error": None,
            "final_free": fit.final_free.tolist(),
            "initial_free": fit.initial_full[np.asarray(fit.free_indices, dtype=np.int64)].tolist(),
            "free_indices_zero_based": list(fit.free_indices),
            "negLj": float(fit.objective.neg_log_joint),
            "negLl": float(fit.objective.neg_log_likelihood),
            "AIC": float(fit.aic),
            "BIC": float(fit.bic),
            "termination": fit.optimizer.termination,
            "converged": fit.optimizer.termination in {"tol_arg", "tol_grad"},
        }
    except Exception as exc:
        return {
            "model": model,
            "success": False,
            "error": f"{type(exc).__name__}: {exc}",
            "final_free": [],
            "initial_free": [],
            "free_indices_zero_based": [],
            "negLj": None,
            "negLl": None,
            "AIC": None,
            "BIC": None,
            "termination": "error",
            "converged": False,
        }


def _matlab_fit(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": raw["model"],
        "success": bool(raw["success"]),
        "error_identifier": raw.get("error_identifier", ""),
        "error_message": raw.get("error_message", ""),
        "final_free": _array(raw.get("final_free", [])).reshape(-1).tolist(),
        "initial_free": _array(raw.get("initial_free", [])).reshape(-1).tolist(),
        "free_indices_zero_based": [int(x) for x in _array(raw.get("free_indices_zero_based", [])).reshape(-1)],
        "negLj": _scalar(raw.get("negLj")),
        "negLl": _scalar(raw.get("negLl")),
        "AIC": _scalar(raw.get("AIC")),
        "BIC": _scalar(raw.get("BIC")),
        "LME": _scalar(raw.get("LME")),
        "trace_last_finite_row": int(round(_scalar(raw.get("trace_last_finite_row", 0)))),
        "reset_count": int(round(_scalar(raw.get("reset_count", 0)))),
        "converged": bool(raw.get("converged_inferred", False)),
    }


def _fit_diagnostic(matlab: dict[str, Any], hgfx: dict[str, Any], expected_free: list[int]) -> dict[str, Any]:
    contract_match = (
        matlab["free_indices_zero_based"] == expected_free
        and hgfx["free_indices_zero_based"] == expected_free
    )
    diag: dict[str, Any] = {
        "contract_free_indices_match": contract_match,
        "both_success": bool(matlab["success"] and hgfx["success"]),
        "convergence_match": bool(matlab["converged"] == hgfx["converged"]),
        "max_abs_final_free_diff": None,
        "abs_negLj_diff": None,
        "abs_BIC_diff": None,
    }
    if diag["both_success"]:
        ma = np.asarray(matlab["final_free"], dtype=np.float64)
        ha = np.asarray(hgfx["final_free"], dtype=np.float64)
        if ma.shape == ha.shape and ma.size:
            diag["max_abs_final_free_diff"] = float(np.max(np.abs(ma - ha)))
        diag["abs_negLj_diff"] = abs(float(matlab["negLj"]) - float(hgfx["negLj"]))
        diag["abs_BIC_diff"] = abs(float(matlab["BIC"]) - float(hgfx["BIC"]))
    return diag


def main(input_path: str, matlab_path: str, output_path: str) -> int:
    manifest = json.loads(Path(input_path).read_text(encoding="utf-8"))
    matlab_raw = json.loads(Path(matlab_path).read_text(encoding="utf-8"))
    if manifest["protocol"] != PROTOCOL or matlab_raw["protocol"] != PROTOCOL:
        raise ValueError("S7 protocol mismatch")
    if matlab_raw["input_shard_sha256"] != manifest["shard_sha256"]:
        raise ValueError("MATLAB result does not correspond to this immutable shard")

    parameter_results = []
    for case, mraw in zip(manifest["parameter_cases"], matlab_raw["parameter_results"], strict=True):
        matlab = _matlab_fit(mraw)
        hgfx = _fit(case["model"], case["y"], case["u"])
        expected = [int(i) for i in case["free_indices_zero_based"]]
        parameter_results.append({
            "case_id": case["case_id"],
            "case_sha256": case["case_sha256"],
            "model": case["model"],
            "trial_count": case["trial_count"],
            "truth_scale": case["truth_scale"],
            "replicate": case["replicate"],
            "seed": case["seed"],
            "truth_free": case["truth_free"],
            "matlab": matlab,
            "hgfx": hgfx,
            "diagnostic": _fit_diagnostic(matlab, hgfx, expected),
        })

    model_results = []
    for case, mraw in zip(manifest["model_cases"], matlab_raw["model_results"], strict=True):
        matlab_candidates = {
            candidate: _matlab_fit(raw)
            for candidate, raw in zip(BINARY_VARIANTS, mraw["candidates"], strict=True)
        }
        hgfx_candidates = {candidate: _fit(candidate, case["y"], case["u"]) for candidate in BINARY_VARIANTS}

        valid = {name: row for name, row in hgfx_candidates.items() if row["success"] and row["BIC"] is not None and np.isfinite(row["BIC"])}
        hgfx_selected = min(valid, key=lambda name: valid[name]["BIC"]) if valid else ""
        matlab_selected = str(mraw.get("selected_model", ""))
        candidate_diagnostics = {}
        for candidate in BINARY_VARIANTS:
            expected = matlab_candidates[candidate]["free_indices_zero_based"]
            candidate_diagnostics[candidate] = _fit_diagnostic(
                matlab_candidates[candidate], hgfx_candidates[candidate], expected
            )

        model_results.append({
            "case_id": case["case_id"],
            "case_sha256": case["case_sha256"],
            "generating_model": case["generating_model"],
            "trial_count": case["trial_count"],
            "truth_scale": case["truth_scale"],
            "replicate": case["replicate"],
            "seed": case["seed"],
            "matlab_selected_model": matlab_selected,
            "hgfx_selected_model": hgfx_selected,
            "winner_match": matlab_selected == hgfx_selected and matlab_selected != "",
            "matlab_candidates": matlab_candidates,
            "hgfx_candidates": hgfx_candidates,
            "candidate_diagnostics": candidate_diagnostics,
        })

    payload = {
        "protocol": PROTOCOL,
        "shard": manifest["shard"],
        "input_shard_sha256": manifest["shard_sha256"],
        "parameter_results": parameter_results,
        "model_results": model_results,
        "shard_contract_pass": all(r["diagnostic"]["contract_free_indices_match"] for r in parameter_results),
        "model_winner_matches": sum(int(r["winner_match"]) for r in model_results),
        "model_cases": len(model_results),
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "protocol": PROTOCOL,
        "shard": payload["shard"],
        "shard_contract_pass": payload["shard_contract_pass"],
        "model_winner_matches": payload["model_winner_matches"],
        "model_cases": payload["model_cases"],
    }, indent=2))
    # A shard comparison is evidence capture. Aggregate protocol classification
    # decides S7; do not fail early merely because a scientific result differs.
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("matlab")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.input, args.matlab, args.output))
