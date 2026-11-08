#!/usr/bin/env python3
"""REV-1.2: uncertainty audit of frozen S7 cases; no simulation or refitting."""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.stats import beta, binomtest

MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
PARAMS = ("omega2", "omega3", "log_zeta")
BOOTSTRAP_SEED = 20261109
N_BOOT = 2000
VALID_MIN = 1900


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def ensure(ok: bool, detail: str) -> None:
    if not ok:
        raise ValueError(detail)


def exact_ci(k: int, n: int, confidence: float = 0.95) -> list[float]:
    ensure(0 <= k <= n and n > 0, "invalid binomial count")
    a = 1 - confidence
    return [float(beta.ppf(a/2, k, n-k+1)) if k else 0.0,
            float(beta.ppf(1-a/2, k+1, n-k)) if k < n else 1.0]


def summaries(truth: np.ndarray, fitted: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ensure(truth.shape == fitted.shape and truth.shape[1] == 3, "recovery shape mismatch")
    std = np.std(truth, axis=0, ddof=0)
    ensure(bool(np.all(std > 0.0)), "undefined full-sample truth SD")
    correlation = np.array([np.corrcoef(truth[:, i], fitted[:, i])[0, 1] for i in range(3)])
    rmse = np.sqrt(np.mean((fitted-truth)**2, axis=0))
    return correlation, rmse/std


def bootstats(truth: np.ndarray, fitted: np.ndarray, indices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Resample 12 paired-horizon truth clusters, retaining both horizons in each draw."""
    ts = truth.reshape(12, 2, 3)[indices].reshape(N_BOOT, 24, 3)
    fs = fitted.reshape(12, 2, 3)[indices].reshape(N_BOOT, 24, 3)
    tc, fc = ts-ts.mean(axis=1, keepdims=True), fs-fs.mean(axis=1, keepdims=True)
    st = np.sqrt(np.mean(tc**2, axis=1))
    sf = np.sqrt(np.mean(fc**2, axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.mean(tc*fc, axis=1)/(st*sf)
        srmse = np.sqrt(np.mean((ts-fs)**2, axis=1))/st
    return corr, srmse


def ci_from_bootstrap(draws: np.ndarray) -> dict:
    finite = draws[np.isfinite(draws)]
    n = len(finite)
    return {"ci95": [float(x) for x in np.quantile(finite, (0.025, 0.975), method="linear")]
            if n >= VALID_MIN else None,
            "bootstrap_valid": n, "bootstrap_total": N_BOOT, "quality_ok": n >= VALID_MIN}


def read_archives(archive_dir: Path, audit: dict) -> list[dict]:
    pins = {item["artifact"]: item for item in audit["raw_artifacts"]}
    paths = sorted(archive_dir.glob("m18-s7-shard-*.zip"))
    ensure(len(paths) == 12 and {p.name for p in paths} == set(pins),
           "missing, extra or renamed original S7 shard ZIP")
    records = []
    for path in paths:
        pin = pins[path.name]
        ensure(digest(path) == pin["archive_sha256"], "ZIP SHA-256 mismatch "+path.name)
        with ZipFile(path) as z:
            members = z.namelist()
            cs = [x for x in members if x.endswith("-comparison.json")]
            ms = [x for x in members if x.endswith("-manifest.json")]
            ensure(len(cs) == len(ms) == 1, "incorrect ZIP member inventory")
            raw_comp, raw_man = z.read(cs[0]), z.read(ms[0])
            ensure(sha256(raw_comp).hexdigest() == pin["comparison_sha256"], "comparison digest drift")
            ensure(sha256(raw_man).hexdigest() == pin["manifest_sha256"], "manifest digest drift")
            comp, man = json.loads(raw_comp), json.loads(raw_man)
            ensure(comp["shard_contract_pass"] and comp["protocol"] == "m18-s7-paired-recovery-1",
                   "frozen shard contract failed")
            ensure(comp["input_shard_sha256"] == man["shard_sha256"], "paired input SHA drift")
            cases = {case["case_id"]: case for case in man["parameter_cases"]}
            ensure(len(cases) == len(comp["parameter_results"]) == 6, "missing parameter cases")
            for row in comp["parameter_results"]:
                case = cases.get(row["case_id"])
                ensure(case is not None and row["case_sha256"] == case["case_sha256"],
                       "parameter case-input identity mismatch")
                ensure(row["model"] == case["model"] and row["seed"] == case["seed"]
                       and row["replicate"] == case["replicate"]
                       and row["trial_count"] == case["trial_count"]
                       and row["truth_scale"] == case["truth_scale"]
                       and row["truth_free"] == case["truth_free"], "parameter record mismatch")
                for imp in ("matlab", "hgfx"):
                    fit = row[imp]
                    ensure(bool(fit["success"]) and fit["free_indices_zero_based"] == [12, 13, 14]
                           and len(fit["final_free"]) == 3,
                           "missing/invalid fit "+row["case_id"])
                records.append(row)
    ensure(len(records) == 72 and len({r["case_id"] for r in records}) == 72,
           "missing/duplicate recovery case")
    return records


def compute(archives: Path, audit_path: Path, decision_path: Path) -> dict:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    ensure(audit["paired_winners_match"] == 36, "historical selection not verified")
    rows = read_archives(archives, audit)
    out = {
        "task": "REV-1.2", "status": "EXPLAINED",
        "protocol": "evidence/revision/protocols/REV-1.2_PROTOCOL.md",
        "frozen_source_run": 34896442847, "no_refitting": True,
        "source_sha256": {"confusion_audit_json": digest(audit_path),
                          "s7_decision_json": digest(decision_path)},
        "ci_method": "95% Clopper-Pearson exact beta quantiles; 95% paired-horizon cluster percentile bootstrap",
        "confidence": 0.95, "bootstrap": {
            "B": N_BOOT, "seed": BOOTSTRAP_SEED, "generator": "NumPy default_rng PCG64",
            "clusters_per_model": 12,
            "sampling_unit": "(truth_scale,replicate) with both horizon cases retained",
            "quantile": "numpy linear [0.025,0.975]", "minimum_valid_draws": VALID_MIN},
        "parameters_order": list(PARAMS), "per_model": {}, "model_recovery": {},
        "unchanged_scientific_criteria": decision["criteria_unchanged"],
        "interpretation_limits": [
            "Deterministic, nonrandom S7 truth grid; binomial CIs/tests are conditional descriptives, not population coverage guarantees.",
            "There are 12 unique transformed truth vectors per model, reused at two horizons. Bootstrap resamples their 12 paired-horizon clusters.",
            "No historical recovery FAIL was reclassified and no thresholds, fits, seeds, or existing figures were modified."]}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    for model in MODELS:
        model_rows = [row for row in rows if row["model"] == model]
        ensure(len(model_rows) == 24, "incomplete model "+model)
        groups = defaultdict(dict)
        for row in model_rows:
            k = (row["truth_scale"], row["replicate"])
            ensure(row["trial_count"] not in groups[k], "duplicate horizon in cluster")
            groups[k][row["trial_count"]] = row
        ensure(len(groups) == 12 and all(set(g) == {128, 256} for g in groups.values()),
               "bad paired-horizon grouping")
        ordered = [row for k in sorted(groups) for h, row in sorted(groups[k].items())]
        truth = np.asarray([r["truth_free"] for r in ordered], dtype=np.float64)
        draws = rng.integers(0, 12, size=(N_BOOT, 12))
        mo = {"case_count": 24, "unique_truth_clusters": 12, "implementations": {}}
        for imp in ("matlab", "hgfx"):
            fitted = np.asarray([r[imp]["final_free"] for r in ordered], dtype=np.float64)
            ensure(fitted.shape == truth.shape == (24, 3), "array shape changed")
            corr, srmse = summaries(truth, fitted)
            boot_corr, boot_srmse = bootstats(truth, fitted, draws)
            n_converged = sum(bool(r[imp]["converged"]) for r in ordered)
            convergence = {"n": 24, "converged": n_converged, "rate": n_converged/24,
                           "ci95": exact_ci(n_converged, 24)}
            params = {}
            for i, pname in enumerate(PARAMS):
                params[pname] = {
                    "correlation": {"estimate": float(corr[i]),
                                    **ci_from_bootstrap(boot_corr[:, i])},
                    "srmse": {"estimate": float(srmse[i]),
                              **ci_from_bootstrap(boot_srmse[:, i])}}
            bc = np.where(np.all(np.isfinite(boot_corr), axis=1),
                          np.median(boot_corr, axis=1), np.nan)
            bs = np.where(np.all(np.isfinite(boot_srmse), axis=1),
                          np.median(boot_srmse, axis=1), np.nan)
            pooled = {
                "median_correlation": {"estimate": float(np.median(corr)),
                                       **ci_from_bootstrap(bc)},
                "median_srmse": {"estimate": float(np.median(srmse)),
                                 **ci_from_bootstrap(bs)}}
            expected = decision["parameter_recovery"][model][imp]
            for key, actual in (("convergence_rate", convergence["rate"]),
                                ("median_correlation", pooled["median_correlation"]["estimate"]),
                                ("median_standardized_rmse", pooled["median_srmse"]["estimate"])):
                ensure(np.isclose(actual, expected[key], rtol=0, atol=2e-12),
                       f"{model}/{imp} frozen metric changed: {key}: {actual} vs {expected[key]}")
            mo["implementations"][imp] = {
                "convergence": convergence, "parameters": params, "pooled_secondary": pooled}
        out["per_model"][model] = mo
    confusion = audit["confusion_matrix_counts"]
    model_recovery = decision["model_recovery"]
    per_model = {}
    for i, model in enumerate(MODELS):
        k = confusion[i][i]
        per_model[model] = {
            "correct": k, "n": 12, "fraction": k/12, "ci95": exact_ci(k, 12),
            "chance_fraction": 1/3,
            "p_greater_than_chance": float(binomtest(k, 12, 1/3, alternative="greater").pvalue),
            "p_two_sided": float(binomtest(k, 12, 1/3, alternative="two-sided").pvalue),
            "all_selected_counts": dict(zip(MODELS, confusion[i]))}
    out["model_recovery"] = {
        "per_generating_model": per_model,
        "balanced_accuracy": sum(per_model[m]["fraction"] for m in MODELS)/3,
        "matlab_balanced_accuracy": model_recovery["matlab_balanced_accuracy"],
        "hgfx_balanced_accuracy": model_recovery["hgfx_balanced_accuracy"],
        "chance_balanced_accuracy": 1/3,
        "paired_winner_agreement": {"same": 36, "total": 36, "rate": 1.0,
                                    "ci95": exact_ci(36, 36)}}
    ensure(np.isclose(out["model_recovery"]["balanced_accuracy"],
                      model_recovery["hgfx_balanced_accuracy"], rtol=0, atol=2e-15),
           "original balanced accuracy changed")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive-dir", type=Path, required=True)
    ap.add_argument("--audit", type=Path, default=Path("evidence/revision/confusion_audit.json"))
    ap.add_argument("--decision", type=Path,
                    default=Path("reference/validation/m18_s7_reference_limitation/decision.json"))
    ap.add_argument("--output", type=Path,
                    default=Path("evidence/revision/recovery_uncertainty.json"))
    args = ap.parse_args()
    result = compute(args.archive_dir, args.audit, args.decision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True,
                                      allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "source_run": result["frozen_source_run"],
                      "models": list(result["per_model"]),
                      "model_recovery": {k: {"correct": v["correct"], "ci95": v["ci95"],
                                             "p_greater": v["p_greater_than_chance"]}
                                         for k, v in result["model_recovery"]["per_generating_model"].items()},
                      "bootstrap": result["bootstrap"]}, indent=2))


if __name__ == "__main__":
    main()
