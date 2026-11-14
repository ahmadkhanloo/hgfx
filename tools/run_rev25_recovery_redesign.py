#!/usr/bin/env python3
"""REV-2.5 runner: redesigned parameter/model recovery study (HGFX).

Executes the preregistered protocol `evidence/revision/protocols/
REV-2.5_PROTOCOL.md` exactly once using the released hgfx==1.0.0 wheel:
prior-draw truths, horizons {128, 256, 512}, three starts per fit with the
released termination-based convergence, per-parameter correlation/sRMSE/bias,
and a model-recovery confusion matrix with exact statistics. Descriptive; no
acceptance relabeling. Dataset tasks run in isolated worker processes with a
240 s wall-clock guard (protocol amendment); chunk files are checkpoint
infrastructure and make the run resumable without re-hanging.

Modes: probe | run | aggregate
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.metadata
import json
import multiprocessing as mp
import os
import platform
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence" / "revision"
CHUNKS = EVID / "rev25_chunks"
MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
HORIZONS = (128, 256, 512)
N_RECOVERY = 100
N_MODELREC = 60
BASE_SEED = 2026111500
TASK_TIMEOUT_S = 240
WHEEL_SHA256 = "5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90"
THRESHOLDS = {
    "convergence_rate_min": 0.80,
    "median_correlation_min": 0.50,
    "median_standardized_rmse_max": 1.00,
    "balanced_accuracy_min": 0.50,
}
PARAM_NAMES = ("omega2", "omega3", "logze")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def dataset_seed(kind: str, model_idx: int, t_idx: int, d: int) -> int:
    base = BASE_SEED + (3_000_000 if kind == "model" else 0)
    return base + model_idx * 1_000_000 + t_idx * 10_000 + d


def _sha(a: np.ndarray) -> str:
    a = np.ascontiguousarray(a, dtype="<f8")
    return hashlib.sha256(a.tobytes()).hexdigest()


def _dataset_task(payload: dict) -> dict:
    """Worker: regenerate one dataset deterministically and run its fits.

    Isolated process per protocol amendment; returns a picklable record
    without arrays. All exceptions are captured as statuses.
    """
    import warnings

    kind = payload["kind"]
    model = payload["model"]
    model_idx = payload["model_idx"]
    t_idx = payload["t_idx"]
    T = payload["T"]
    d = payload["d"]
    seed = dataset_seed(kind, model_idx, t_idx, d)

    from hgfx.compat.configs import unitsq_sgm_config
    from hgfx.core.priors import optimization_indices
    from hgfx.diagnostics.recovery import simulate_binary_variant

    u = np.random.Generator(np.random.PCG64(BASE_SEED + 1 + (3_000_000 if kind == "model" else 0)
                                            + model_idx * 1_000_000 + t_idx * 10_000 + d)
                            ).integers(0, 2, size=T).astype(np.float64)
    prc = _config_for(model)().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    mu0 = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    sa0 = np.concatenate((prc.priorsas, obs.priorsas)).astype(np.float64)
    free = np.asarray(optimization_indices(sa0))
    z = np.random.Generator(np.random.PCG64(seed)).standard_normal(free.size)
    truth = mu0.copy()
    truth[free] = mu0[free] + np.sqrt(sa0[free]) * z

    row: dict = {"kind": kind, "model": model, "model_idx": model_idx, "T": T,
                 "d": d, "seed": seed, "free": [int(x) for x in free],
                 "z": [float(x) for x in z],
                 "truth": [float(x) for x in truth[free]],
                 "u_sha256": _sha(u)}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y, _ = simulate_binary_variant(model, u, truth, seed=seed + 1)
        if not np.isfinite(y).all():
            row["dataset_status"] = "simulation_nonfinite"
            return row
        row["dataset_status"] = "ok"
        row["y_sha256"] = _sha(y.astype(np.float64))
    except Exception as exc:  # noqa: BLE001 - recorded per protocol
        row["dataset_status"] = f"simulation_exception:{type(exc).__name__}:{exc}"
        return row

    if kind == "recovery":
        row["runs"], row["retained"] = _fit_record(y, u, model, model_idx, t_idx, d)
        return row

    candidates = {}
    for c_idx, cand in enumerate(MODELS):
        runs, retained = _fit_record(y, u, cand, c_idx, t_idx, d)
        candidates[cand] = {"runs": runs, "retained": retained}
    winners = {c: v["retained"] for c, v in candidates.items() if v["retained"]}
    if winners:
        best = min(winners, key=lambda c: (winners[c]["bic"]
                                           if winners[c]["bic"] is not None else np.inf))
        bics = [winners[c]["bic"] for c in winners]
        row["winner"] = best if len(set(bics)) > 1 else "tie_or_single"
        row["candidate_bics"] = {c: winners[c]["bic"] for c in winners}
    else:
        row["winner"] = "no_winner"
    row["candidates"] = candidates
    return row


def _fit_record(y, u, model: str, model_idx: int, t_idx: int, d: int):
    from hgfx.diagnostics.recovery import fit_binary_variant

    runs = []
    for s in range(3):
        seed = None if s == 0 else (BASE_SEED + 2 + model_idx * 1_000_000
                                    + t_idx * 10_000 + d * 10 + s)
        rec: dict = {"start": s, "seed": seed}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                initial = _start_vector(model, u, seed)
                fit = fit_binary_variant(y, u, model, initial_free=initial)
                opt = fit.optimizer
                rec.update({
                    "status": "ok",
                    "termination": str(getattr(opt, "termination", "NOT_EXPORTED")),
                    "neg_log_joint": float(fit.objective.neg_log_joint),
                    "neg_log_likelihood": float(fit.objective.neg_log_likelihood),
                    "aic": None if fit.aic is None else float(fit.aic),
                    "bic": None if fit.bic is None else float(fit.bic),
                    "final_free": [float(x) for x in fit.final_free],
                })
            except Exception as exc:  # noqa: BLE001
                rec["status"] = f"exception:{type(exc).__name__}:{exc}"
        runs.append(rec)
    ok = [r for r in runs if r["status"] == "ok"]
    retained = None
    if ok:
        retained = dict(min(ok, key=lambda r: (r["neg_log_joint"], r["neg_log_likelihood"])))
    return runs, retained


def _start_vector(model: str, u: np.ndarray, kind_seed: int | None):
    from hgfx.compat.configs import unitsq_sgm_config
    from hgfx.core.priors import optimization_indices

    prc = _config_for(model)().resolve_placeholders(u)
    obs = unitsq_sgm_config()
    mu0 = np.concatenate((prc.priormus, obs.priormus)).astype(np.float64)
    sa0 = np.concatenate((prc.priorsas, obs.priorsas)).astype(np.float64)
    free = np.asarray(optimization_indices(sa0))
    v = mu0.copy()
    if kind_seed is not None:
        z = np.random.Generator(np.random.PCG64(kind_seed)).standard_normal(free.size)
        v[free] = mu0[free] + np.sqrt(sa0[free]) * z
    return v


def _config_for(model: str):
    from hgfx.diagnostics.recovery import _CONFIGS
    return _CONFIGS[model]


def iter_plan(kind: str, n_per: int):
    for m_idx, model in enumerate(MODELS):
        for t_idx, T in enumerate(HORIZONS):
            for d in range(n_per):
                yield kind, m_idx, model, t_idx, T, d


def environment_record() -> dict:
    import jax

    return {
        "hgfx_version": importlib.metadata.version("hgfx"),
        "hgfx_wheel_sha256": WHEEL_SHA256,
        "jax_version": importlib.metadata.version("jax"),
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "devices": [str(d) for d in jax.devices()],
        "git_head": git_head(),
        "protocol": "evidence/revision/protocols/REV-2.5_PROTOCOL.md",
        "base_seed": BASE_SEED,
        "task_timeout_s": TASK_TIMEOUT_S,
    }


def _execute(plan, tag: str):
    """Submit dataset tasks to the worker pool with per-task deadlines."""
    CHUNKS.mkdir(parents=True, exist_ok=True)
    started = time.time()
    futures = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        for payload in plan:
            fut = ex.submit(_dataset_task, payload)
            futures[fut] = (payload, time.time() + TASK_TIMEOUT_S)
        pending = set(futures)
        done_count = 0
        while pending:
            finished, pending = concurrent.futures.wait(
                pending, timeout=10, return_when=concurrent.futures.FIRST_COMPLETED)
            now = time.time()
            for fut in finished:
                payload, meta = futures[fut]
                try:
                    row = fut.result()
                except Exception as exc:  # noqa: BLE001
                    row = {"kind": payload["kind"], "model": payload["model"],
                           "model_idx": payload["model_idx"], "T": payload["T"],
                           "d": payload["d"], "dataset_status": f"worker_exception:{exc}"}
                _checkpoint(row, meta)
                done_count += 1
            for fut in list(pending):
                payload, deadline = futures[fut]
                if now > deadline:
                    row = {"kind": payload["kind"], "model": payload["model"],
                           "model_idx": payload["model_idx"], "T": payload["T"],
                           "d": payload["d"], "dataset_status": "timeout",
                           "timeout_s": TASK_TIMEOUT_S}
                    _checkpoint(row, meta=None)
                    pending.discard(fut)
                    done_count += 1
            if done_count and done_count % 50 == 0:
                print(f"  [{tag}] {done_count} datasets done "
                      f"({time.time() - started:.0f}s)", flush=True)
    print(f"[{tag}] complete: {done_count} datasets in {time.time() - started:.0f}s",
          flush=True)


def _checkpoint(row: dict, meta=None):
    kind = row["kind"]
    model = row["model"]
    T = row["T"]
    chunk = CHUNKS / f"{kind}_{model}_{T}.json"
    data = json.loads(chunk.read_text()) if chunk.exists() else {"done": {}}
    key = str(row["d"])
    existing = data["done"].get(key)
    if existing is not None and existing.get("dataset_status") not in (None, "timeout"):
        return  # never overwrite a real result with a timeout
    data["done"][key] = row
    chunk.write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")


def mode_probe(args):
    plan = []
    for i, payload in enumerate(_all_plan("recovery", N_RECOVERY)):
        if i % 45 == 0:
            plan.append(payload)
        if len(plan) >= 20:
            break
    _execute(plan, "probe")


def _all_plan(kind: str, n_per: int):
    for kind2, m_idx, model, t_idx, T, d in iter_plan(kind, n_per):
        yield {"kind": kind, "model": model, "model_idx": m_idx,
               "t_idx": t_idx, "T": T, "d": d}


def mode_run(args):
    n_rec, n_mod = (N_RECOVERY, N_MODELREC) if not args.fallback else (50, 30)
    plan = list(_all_plan("recovery", n_rec)) + list(_all_plan("model", n_mod))
    _execute(plan, f"run{'_fallback' if args.fallback else ''}")


def clopper_pearson(k: int, n: int, alpha: float = 0.05):
    from scipy.stats import beta

    lo = float(beta.ppf(alpha / 2, k, n - k + 1)) if k else 0.0
    hi = float(beta.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.0
    return [lo, hi]


def _load_rows(kind: str):
    rows = []
    for chunk in sorted(CHUNKS.glob(f"{kind}_*.json")):
        data = json.loads(chunk.read_text())
        rows.extend(data["done"].values())
    return rows


def mode_aggregate(args):
    from scipy.stats import binom

    summary = {"parameter_recovery": {}, "model_recovery": {}}
    rec_rows = _load_rows("recovery")
    for model in MODELS:
        for T in HORIZONS:
            rows = [r for r in rec_rows if r["model"] == model and r["T"] == T]
            n = len(rows)
            sim_ok = [r for r in rows if r.get("dataset_status") == "ok"]
            valid = [r for r in sim_ok if r.get("retained")]
            conv = sum(1 for r in valid
                       if r["retained"]["termination"] in ("tol_grad", "tol_arg"))
            truths = np.asarray([r["truth"] for r in valid], dtype=np.float64) if valid else np.zeros((0, 3))
            fitsA = np.asarray([r["retained"]["final_free"] for r in valid], dtype=np.float64) if valid else np.zeros((0, 3))
            per_param = []
            for j, name in enumerate(PARAM_NAMES):
                if valid:
                    x, yv = truths[:, j], fitsA[:, j]
                    corr = (float(np.corrcoef(x, yv)[0, 1])
                            if len(x) > 1 and np.std(x) > 0 and np.std(yv) > 0 else None)
                    rmse = float(np.sqrt(np.mean((yv - x) ** 2)))
                    srmse = rmse / float(np.std(x, ddof=0)) if np.std(x, ddof=0) > 0 else None
                else:
                    corr, srmse = None, None
                per_param.append({
                    "parameter": name, "n_pairs": int(len(valid)),
                    "correlation": corr, "standardized_rmse": srmse,
                    "bias": (float(np.mean(yv - x)) if valid else None),
                })
            summary["parameter_recovery"][f"{model}_T{T}"] = {
                "n_datasets": n,
                "n_simulation_invalid": n - len(sim_ok),
                "n_fit_failed": len(sim_ok) - len(valid),
                "convergence_rate": (conv / len(valid)) if valid else None,
                "converged": conv,
                "per_parameter": per_param,
                "clopper_pearson_convergence_95": (clopper_pearson(conv, len(valid))
                                                   if valid else None),
            }

    mod_rows = _load_rows("model")
    for T in HORIZONS:
        rows = [r for r in mod_rows if r["T"] == T]
        matrix = np.zeros((3, 3), dtype=np.int64)
        no_winner = 0
        for r in rows:
            w = r.get("winner", "no_winner")
            if w in MODELS:
                matrix[MODELS.index(r["model"]), MODELS.index(w)] += 1
            else:
                no_winner += 1
        row_stats = []
        diag = []
        for i, g in enumerate(MODELS):
            n_row = int(matrix[i].sum())
            correct = int(matrix[i, i])
            diag.append(correct / n_row if n_row else None)
            p_greater = (float(1 - binom.cdf(correct - 1, n_row, 1 / 3))
                         if n_row else None)
            row_stats.append({
                "generating": g, "n": n_row, "correct": correct,
                "counts": matrix[i].tolist(),
                "clopper_pearson_95": clopper_pearson(correct, n_row) if n_row else None,
                "binomial_greater_p_vs_chance": p_greater,
            })
        diags = [x for x in diag if x is not None]
        bacc = float(np.mean(diags)) if diags else None
        summary["model_recovery"][str(T)] = {
            "n_datasets": len(rows), "no_winner": no_winner,
            "confusion_counts": matrix.tolist(),
            "per_row": row_stats, "balanced_accuracy": bacc,
        }

    payload = {
        "schema": "compstat-rev25-recovery-redesign-v1",
        "task": "REV-2.5",
        "status": "EXECUTED_DESCRIPTIVE_NO_SCIENTIFIC_PASS",
        "protocol": "evidence/revision/protocols/REV-2.5_PROTOCOL.md",
        "protocol_commit": "cd0c285",
        "environment": environment_record(),
        "design": {"n_recovery": N_RECOVERY, "n_model_recovery": N_MODELREC,
                   "fallback_applied": args.fallback, "thresholds": THRESHOLDS},
        "results": summary,
        "threshold_compliance": threshold_compliance(summary),
    }
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    make_figures(payload, args)
    return 0


def threshold_compliance(summary: dict) -> dict:
    out = {}
    for key, res in summary["parameter_recovery"].items():
        corrs = [p["correlation"] for p in res["per_parameter"] if p["correlation"] is not None]
        srmses = [p["standardized_rmse"] for p in res["per_parameter"] if p["standardized_rmse"] is not None]
        corr_med = float(np.median(corrs)) if corrs else None
        srmse_med = float(np.median(srmses)) if srmses else None
        conv = res["convergence_rate"]
        out[key] = {
            "convergence_ge_0.80": None if conv is None else bool(conv >= 0.80),
            "median_correlation_ge_0.50": None if corr_med is None else bool(corr_med >= 0.50),
            "median_srmse_le_1.00": None if srmse_med is None else bool(srmse_med <= 1.00),
            "median_correlation": corr_med, "median_srmse": srmse_med,
        }
    for T, res in summary["model_recovery"].items():
        b = res["balanced_accuracy"]
        out[f"model_recovery_T{T}"] = {
            "balanced_accuracy_ge_0.50": None if b is None else bool(b >= 0.50),
            "balanced_accuracy": b,
        }
    return out


def make_figures(payload: dict, args):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, T in zip(axes, HORIZONS):
        rows = [r for r in _load_rows("recovery")
                if r["model"] == "hgf_binary" and r["T"] == T
                and r.get("retained") and r.get("dataset_status") == "ok"]
        for j, name in enumerate(PARAM_NAMES):
            xs = [r["truth"][j] for r in rows]
            ys = [r["retained"]["final_free"][j] for r in rows]
            ax.scatter(xs, ys, s=8, alpha=0.6, label=name)
        ax.set_title(f"hgf_binary T={T}", fontsize=9)
        ax.set_xlabel("truth (transformed)")
        ax.set_ylabel("fit (transformed)")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(Path(args.figure).parent / "rev25_recovery_scatter.png"), dpi=200)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, T in zip(axes, HORIZONS):
        res = payload["results"]["model_recovery"][str(T)]
        m = np.asarray(res["confusion_counts"], dtype=float)
        m = m / np.maximum(m.sum(axis=1, keepdims=True), 1)
        ax.imshow(m, vmin=0, vmax=1, cmap="Greys")
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=8)
        ax.set_xticks(range(3), [s.replace("_binary", "") for s in MODELS], fontsize=7)
        ax.set_yticks(range(3), [s.replace("_binary", "") for s in MODELS], fontsize=7)
        b = res["balanced_accuracy"]
        ax.set_title(f"T={T}  bacc={'n/a' if b is None else f'{b:.3f}'}", fontsize=9)
    fig.tight_layout()
    fig.savefig(args.figure, dpi=200)
    print(f"wrote figures {args.figure}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["probe", "run", "aggregate"])
    ap.add_argument("--fallback", action="store_true",
                    help="preregistered uniform 50% reduction (50/30)")
    ap.add_argument("--out", default=str(EVID / "rev25_recovery_redesign.json"))
    ap.add_argument("--figure", default=str(EVID / "rev25_model_recovery.png"))
    args = ap.parse_args()
    if args.mode == "probe":
        mode_probe(args)
        return 0
    if args.mode == "run":
        mode_run(args)
        return 0
    return mode_aggregate(args)


if __name__ == "__main__":
    sys.exit(main())
