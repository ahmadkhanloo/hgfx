#!/usr/bin/env python3
"""REV-2.6A runner: forward-filter precision stability (float32 vs float64).

Executes the preregistered protocol `evidence/revision/protocols/
REV-2.6_PROTOCOL.md` exactly once: 200 prior-based parameter draws of the
released `hgf_binary` JAX forward filter, horizons {128, 4096, 65536},
float64 reference leg vs default-float32 treatment leg on CPU, paired
elementwise differences and failure classification. Descriptive only; no
acceptance threshold. Run from repository root with the venv that has the
released hgfx==1.0.0 wheel installed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DRAW_SEED = 2026111400
INPUT_SEED = 2026111401
N_DRAWS = 200
HORIZONS = (128, 4096, 65536)
WHEEL_SHA256 = "5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90"


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def classify(result) -> str:
    traj = result.trajectory
    sa = np.asarray(traj["sa"])
    finite_sa = sa[np.isfinite(sa)]
    if finite_sa.size and float(finite_sa.min()) < 0.0:
        return "negative_posterior_precision"
    if any(not np.isfinite(np.asarray(traj[k])).all() for k in ("mu", "sa")):
        return "nonfinite_output"
    return "ok"


def run_leg(inputs, theta, x64: bool):
    import jax

    jax.config.update("jax_enable_x64", x64)
    from hgfx.gpu.engine import fast_binary_hgf

    result = fast_binary_hgf(inputs, theta, update_type="hgf", transformed=True)
    expected = np.float64 if x64 else np.float32
    got = np.asarray(result.trajectory["mu"]).dtype
    if got != expected:
        raise AssertionError(f"leg dtype assertion failed: expected {expected}, got {got}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "evidence/revision/rev26_precision_stability.json"))
    ap.add_argument("--figure", default=str(ROOT / "evidence/revision/rev26_precision_error.png"))
    args = ap.parse_args()

    import jax
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from hgfx.compat.configs import hgf_binary_config
    from hgfx.core.priors import optimization_indices

    cfg = hgf_binary_config()
    mu0 = np.asarray(cfg.priormus, dtype=np.float64)
    sa0 = np.asarray(cfg.priorsas, dtype=np.float64)
    free = np.asarray(optimization_indices(sa0))

    rng = np.random.Generator(np.random.PCG64(DRAW_SEED))
    z = rng.standard_normal((N_DRAWS, free.size))
    thetas = np.repeat(mu0[None, :], N_DRAWS, axis=0)
    thetas[:, free] = mu0[free] + np.sqrt(sa0[free]) * z

    u_rng = np.random.Generator(np.random.PCG64(INPUT_SEED))
    u_full = u_rng.integers(0, 2, size=max(HORIZONS)).astype(np.float64)

    env = {
        "hgfx_version": importlib.metadata.version("hgfx"),
        "hgfx_wheel_sha256": WHEEL_SHA256,
        "jax_version": importlib.metadata.version("jax"),
        "jaxlib_version": importlib.metadata.version("jaxlib"),
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "devices": [str(d) for d in jax.devices()],
        "git_head": git_head(),
        "protocol": "evidence/revision/protocols/REV-2.6_PROTOCOL.md",
        "draw_seed": DRAW_SEED,
        "input_seed": INPUT_SEED,
        "n_draws": N_DRAWS,
        "horizons": list(HORIZONS),
        "free_indices_zero_based": [int(x) for x in free],
        "input_u_sha256": hashlib.sha256(u_full.tobytes()).hexdigest(),
        "draws_sha256": hashlib.sha256(thetas.tobytes()).hexdigest(),
    }

    per_draw = []
    aggregates: dict[str, dict] = {}
    started = time.time()
    suppressed_warnings = 0
    for T in HORIZONS:
        u = u_full[:T]
        rows = []
        for i in range(N_DRAWS):
            theta = thetas[i]
            record: dict = {"horizon": T, "draw": i, "z": [float(v) for v in z[i]]}
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    r64 = run_leg(u, theta, x64=True)
                    record["R"] = classify(r64)
                    mu64 = np.asarray(r64.trajectory["mu"], dtype=np.float64)
                    sa64 = np.asarray(r64.trajectory["sa"], dtype=np.float64)
                except Exception as exc:  # noqa: BLE001 - recorded per protocol
                    record["R"] = f"exception:{type(exc).__name__}"
                try:
                    r32 = run_leg(u, theta, x64=False)
                    record["F"] = classify(r32)
                    mu32 = np.asarray(r32.trajectory["mu"], dtype=np.float64)
                    sa32 = np.asarray(r32.trajectory["sa"], dtype=np.float64)
                except Exception as exc:  # noqa: BLE001
                    record["F"] = f"exception:{type(exc).__name__}"
            if caught:
                suppressed_warnings += len(caught)
            if record.get("R") == "ok" and record.get("F") == "ok":
                record["max_abs_mu_diff"] = float(np.max(np.abs(mu32 - mu64)))
                record["max_abs_sa_diff"] = float(np.max(np.abs(sa32 - sa64)))
            rows.append(record)
            if (i + 1) % 50 == 0:
                print(f"  T={T}: {i + 1}/{N_DRAWS} draws", flush=True)
        per_draw.extend(rows)

        for leg in ("R", "F"):
            classes: dict[str, int] = {}
            for row in rows:
                status = row.get(leg, "missing")
                key = status.split(":", 1)[0]
                classes[key] = classes.get(key, 0) + 1
            aggregates.setdefault(T, {})[leg] = classes
        for metric in ("max_abs_mu_diff", "max_abs_sa_diff"):
            values = np.asarray(
                [row[metric] for row in rows if metric in row], dtype=np.float64
            )
            if values.size:
                aggregates[T][metric] = {
                    "n_pairs": int(values.size),
                    "median": float(np.quantile(values, 0.5)),
                    "p90": float(np.quantile(values, 0.9)),
                    "p99": float(np.quantile(values, 0.99)),
                    "max": float(np.max(values)),
                }
        print(f"T={T} done in {time.time() - started:.1f}s cumulative", flush=True)

    # float64 failure region: which draws failed in the reference leg at the
    # longest horizon, with their free transformed values
    r_failures = [
        {"horizon": row["horizon"], "draw": row["draw"], "status": row["R"], "z": row["z"]}
        for row in per_draw if row["R"] != "ok"
    ]

    elapsed = time.time() - started
    payload = {
        "schema": "compstat-rev26-precision-stability-v1",
        "task": "REV-2.6A",
        "status": "EXECUTED_DESCRIPTIVE_NO_SCIENTIFIC_PASS",
        "protocol": "evidence/revision/protocols/REV-2.6_PROTOCOL.md",
        "protocol_commit": "87d5eb5",
        "environment": env,
        "runtime_seconds": elapsed,
        "suppressed_jax_truncation_warnings": suppressed_warnings,
        "aggregate": {str(k): v for k, v in aggregates.items()},
        "float64_reference_failures": r_failures,
        "per_draw": per_draw,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}")

    # figure: paired max |mu| difference quantiles vs horizon (log-log)
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    xs = sorted(aggregates.keys())
    for stat, marker in (("median", "o"), ("p90", "s"), ("max", "^")):
        ys = [aggregates[T].get("max_abs_mu_diff", {}).get(stat) for T in xs]
        if any(y is None for y in ys):
            continue
        ax.plot(xs, ys, marker=marker, color="#333333", label=stat)
    for T in xs:
        f_fail = aggregates[T]["F"].get("negative_posterior_precision", 0) / N_DRAWS
        f_nonf = aggregates[T]["F"].get("nonfinite_output", 0) / N_DRAWS
        ax.annotate(
            f"{f_fail + f_nonf:.0%} F failures",
            (T, aggregates[T].get("max_abs_mu_diff", {}).get("max", 0.0)),
            textcoords="offset points", xytext=(0, 8), ha="center", fontsize=7,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("trial horizon T")
    ax.set_ylabel("max |mu_float32 - mu_float64| (paired)")
    ax.set_title("REV-2.6A forward-filter precision stability (hgf_binary, CPU)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.figure, dpi=200)
    print(f"wrote {args.figure}")

    print(json.dumps({str(k): v for k, v in aggregates.items()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
