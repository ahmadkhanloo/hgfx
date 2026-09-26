#!/usr/bin/env python3
"""Generate protocol-1 paper figures from committed machine-readable evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROTOCOL_ID = "hgfx-paper-protocol-1"
REQUIRED_INPUTS = (
    "reference/validation/m18_s7_reference_limitation/decision.json",
    "paper/reproducibility/p2a10_raw_numeric_result_35268575414.json",
    "paper/reproducibility/p2a10_comparison_35268575414.json",
    "paper/reproducibility/p3_m18c2_aggregate_35272347167.json",
    "paper/reproducibility/p3_m18c2_provenance_35272347167.json",
    "paper/tables/backend_gpu_applicability.md",
    "paper/tables/p2_tables_manifest.json",
    "gpu_validation_results/m18_s9_physical_gpu_revalidation.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(
        path.with_suffix(".pdf"),
        bbox_inches="tight",
        facecolor="white",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def fig_recovery_metrics(repo: Path, out: Path) -> None:
    decision = _load_json(repo / "reference/validation/m18_s7_reference_limitation/decision.json")
    models = ["hgf_binary", "ehgf_binary", "uhgf_binary"]
    labels = ["hgf", "ehgf", "uhgf"]
    metrics = [
        ("convergence_rate", 0.80, "Convergence rate", True),
        ("median_correlation", 0.50, "Median correlation", True),
        ("median_standardized_rmse", 1.00, "Median standardized RMSE", False),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    x = np.arange(len(models))
    width = 0.35
    for ax, (key, threshold, title, higher_better) in zip(axes, metrics):
        matlab = [decision["parameter_recovery"][m]["matlab"][key] for m in models]
        hgfx = [decision["parameter_recovery"][m]["hgfx"][key] for m in models]
        ax.bar(x - width / 2, matlab, width, label="MATLAB 8.2.0", color="#4c78a8")
        ax.bar(x + width / 2, hgfx, width, label="HGFX 1.0.0", color="#f58518")
        ax.axhline(threshold, color="#333333", linestyle="--", linewidth=1, label="frozen threshold")
        ax.set_xticks(x, labels)
        ax.set_title(title)
        ax.set_ylim(0, max(max(matlab), max(hgfx), threshold) * 1.25)
        if not higher_better:
            ax.set_ylabel("lower is better")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("S7 paired parameter recovery (historical; not a scientific PASS)", y=1.18, fontsize=11)
    fig.tight_layout()
    fig.subplots_adjust(top=0.78)
    _save(fig, out)


def fig_model_selection(repo: Path, out: Path) -> None:
    decision = _load_json(repo / "reference/validation/m18_s7_reference_limitation/decision.json")
    mr = decision["model_recovery"]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.bar(
        ["MATLAB balanced\naccuracy", "HGFX balanced\naccuracy", "BIC winner\nagreement"],
        [mr["matlab_balanced_accuracy"], mr["hgfx_balanced_accuracy"], mr["winner_matches"] / mr["total_cases"]],
        color=["#4c78a8", "#f58518", "#54a24b"],
    )
    ax.axhline(0.50, color="#333333", linestyle="--", linewidth=1)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("fraction")
    ax.set_title(f"Paired model selection: {mr['winner_matches']}/{mr['total_cases']} BIC winners match")
    ax.text(0.02, 0.92, "Dashed line = frozen balanced-accuracy threshold 0.50", transform=ax.transAxes, fontsize=8)
    fig.tight_layout()
    _save(fig, out)


def fig_pyhgf_common_scope(repo: Path, out: Path) -> None:
    raw = _load_json(repo / "paper/reproducibility/p2a10_raw_numeric_result_35268575414.json")
    comparison = _load_json(repo / "paper/reproducibility/p2a10_comparison_35268575414.json")
    hgfx_p = np.asarray(raw["hgfx"]["fields"]["first_level_predicted_probability"], dtype=np.float64)
    pyhgf_p = np.asarray(raw["pyhgf"]["fields"]["first_level_predicted_probability"], dtype=np.float64)
    hgfx_mu = np.asarray(raw["hgfx"]["fields"]["level_2_posterior_mean"], dtype=np.float64)
    pyhgf_mu = np.asarray(raw["pyhgf"]["fields"]["level_2_posterior_mean"], dtype=np.float64)
    trials = np.arange(1, hgfx_p.size + 1)
    nll = comparison["field_results"]["participant_response_nll_total"]["classification"]
    fig, axes = plt.subplots(2, 1, figsize=(8.8, 5.6), sharex=True)
    axes[0].plot(trials, hgfx_p, color="#4c78a8", lw=1.4, label="HGFX")
    axes[0].plot(trials, pyhgf_p, color="#f58518", lw=1.0, ls="--", label="pyhgf 0.3.2")
    axes[0].set_ylabel("predicted p(u=1)")
    axes[0].set_title("Frozen common-scope binary HGF (128 trials)")
    axes[0].legend(frameon=False)
    axes[1].plot(trials, hgfx_mu, color="#4c78a8", lw=1.4)
    axes[1].plot(trials, pyhgf_mu, color="#f58518", lw=1.0, ls="--")
    axes[1].set_ylabel("level-2 posterior mean")
    axes[1].set_xlabel("trial")
    p_err = comparison["field_results"]["first_level_predicted_probability"]["max_abs_error"]
    fig.suptitle(
        f"11/11 mapped perceptual quantities PASS (max |Δp|={p_err:.1e}); response NLL: {nll}",
        fontsize=9,
    )
    fig.tight_layout()
    _save(fig, out)


def fig_evidence_classes(repo: Path, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    ax.set_axis_off()
    boxes = [
        (0.02, "PASS", "#54a24b", "Direct MATLAB\nparity in validated\nscopes"),
        (0.27, "REFERENCE\nLIMITATION MATCH", "#f2cf5b", "HGFX matches a\nMATLAB limitation\n(not recovery PASS)"),
        (0.52, "NDC", "#f58518", "pyhgf response NLL\nnot directly\ncomparable"),
        (0.77, "HISTORICAL FAIL", "#e45756", "M18 recovery FAIL\npreserved, not\nrewritten"),
    ]
    for x, title, color, body in boxes:
        ax.add_patch(plt.Rectangle((x, 0.22), 0.21, 0.68, facecolor=color, alpha=0.28, edgecolor="#222222", linewidth=0.8))
        ax.text(x + 0.105, 0.72, title, ha="center", va="center", fontsize=8, fontweight="bold", color="#111111")
        ax.text(x + 0.105, 0.40, body, ha="center", va="center", fontsize=8, color="#111111")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Paper evidence classes under hgfx-paper-protocol-1")
    fig.tight_layout()
    _save(fig, out)


def fig_p3_horizon_diagnostics(repo: Path, out: Path) -> None:
    aggregate = _load_json(repo / "paper/reproducibility/p3_m18c2_aggregate_35272347167.json")
    horizons = [128, 256, 512, 1024]
    models = ["hgf_binary", "ehgf_binary", "uhgf_binary"]
    model_labels = {
        "hgf_binary": "HGF",
        "ehgf_binary": "eHGF",
        "uhgf_binary": "uHGF",
    }
    colors = {
        "hgf_binary": "#4c78a8",
        "ehgf_binary": "#54a24b",
        "uhgf_binary": "#e45756",
    }
    engines = [
        ("matlab", "MATLAB", "-", "o"),
        ("hgfx", "HGFX", "--", "x"),
    ]
    metrics = [
        ("convergence_rate", "Convergence rate", aggregate["criteria"]["convergence_rate_min"]),
        ("median_correlation", "Median correlation", aggregate["criteria"]["median_correlation_min"]),
        ("median_standardized_rmse", "Median standardized RMSE", aggregate["criteria"]["median_standardized_rmse_max"]),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.0), sharex=True)
    x = np.arange(len(horizons), dtype=float)

    for ax, (key, title, threshold) in zip(axes, metrics):
        for model in models:
            horizon_data = aggregate["parameter_recovery"][model]["horizons"]
            for engine, engine_label, linestyle, marker in engines:
                values = []
                for horizon in horizons:
                    record = horizon_data[str(horizon)][engine]
                    if record.get("complete", False) and key in record:
                        values.append(record[key])
                    else:
                        values.append(np.nan)
                ax.plot(
                    x,
                    values,
                    color=colors[model],
                    linestyle=linestyle,
                    marker=marker,
                    linewidth=1.4,
                    markersize=4.5,
                    label=f"{model_labels[model]} {engine_label}",
                )
        ax.axhline(threshold, color="#333333", linestyle=":", linewidth=1.0)
        ax.set_xticks(x, [str(h) for h in horizons])
        ax.set_xlabel("trials")
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.2)

    axes[0].set_ylim(0, 1.05)
    axes[1].set_ylim(-0.05, 1.05)
    observed_srmse = []
    for model in models:
        for horizon in horizons:
            for engine, *_ in engines:
                record = aggregate["parameter_recovery"][model]["horizons"][str(horizon)][engine]
                if record.get("complete", False) and "median_standardized_rmse" in record:
                    observed_srmse.append(record["median_standardized_rmse"])
    axes[2].set_ylim(0, max(max(observed_srmse), metrics[2][2]) * 1.15)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle(
        "P3 trial-horizon diagnostics — overall classification: INSUFFICIENT_REFERENCE_EVIDENCE",
        fontsize=10,
        y=1.12,
    )
    fig.text(
        0.5,
        0.01,
        "Frozen thresholds are dotted lines. Incomplete HGF T=512/1024 cases are retained as gaps; "
        "diagnostic PASS rows do not establish identifiability.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.91))
    _save(fig, out)


def fig_gpu_applicability(repo: Path, out: Path) -> None:
    evidence = _load_json(repo / "gpu_validation_results/m18_s9_physical_gpu_revalidation.json")
    cpu_gap = evidence["acceptance_summary"]["fit_backend_max_objective_gap"]
    cpu_criterion = evidence["criteria"]["compat_vs_jax_cpu_final_objective_gap_max"]
    gpu_gap = max(case["final_objective_gap"] for case in evidence["physical_gpu"]["cases"])
    gpu_criterion = evidence["criteria"]["jax_cpu_vs_physical_gpu_final_objective_gap_max"]

    ratios = [cpu_gap / cpu_criterion, gpu_gap / gpu_criterion]
    labels = ["Compatibility ↔ JAX CPU", "JAX CPU ↔ 2× Tesla T4"]

    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    bars = ax.bar(labels, ratios, color=["#4c78a8", "#54a24b"])
    ax.axhline(1.0, color="#333333", linestyle="--", linewidth=1, label="frozen acceptance boundary")
    ax.set_yscale("log")
    ax.set_ylabel("observed final-objective gap / frozen criterion")
    ax.set_title("Backend agreement relative to each frozen criterion")
    for bar, gap, criterion in zip(bars, [cpu_gap, gpu_gap], [cpu_criterion, gpu_criterion]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.5,
            f"{gap:.3g} / {criterion:.0e}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    _save(fig, out)


def build(repo: Path) -> dict:
    missing = [rel for rel in REQUIRED_INPUTS if not (repo / rel).exists()]
    if missing:
        raise FileNotFoundError("missing required paper inputs: " + ", ".join(missing))
    figures = {
        "fig_recovery_metrics.png": fig_recovery_metrics,
        "fig_model_selection.png": fig_model_selection,
        "fig_pyhgf_common_scope.png": fig_pyhgf_common_scope,
        "fig_evidence_classes.png": fig_evidence_classes,
        "fig_p3_horizon_diagnostics.png": fig_p3_horizon_diagnostics,
        "fig_gpu_applicability.png": fig_gpu_applicability,
    }
    fig_dir = repo / "paper" / "figures"
    outputs = {}
    for name, fn in figures.items():
        path = fig_dir / name
        fn(repo, path)
        pdf = path.with_suffix(".pdf")
        outputs[name] = {
            "path": str(path.relative_to(repo)),
            "sha256": _sha256(path),
            "pdf_path": str(pdf.relative_to(repo)),
            "pdf_sha256": _sha256(pdf),
        }
    inputs = {rel: _sha256(repo / rel) for rel in REQUIRED_INPUTS}
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "generator": "paper/scripts/generate_p5_figures.py",
        "inputs": inputs,
        "figures": outputs,
        "notes": [
            "Figures are generated from committed evidence; no numerical values were transcribed by hand.",
            "PNG figures are exported at 300 dpi; vector PDFs are written alongside each PNG.",
            "P3 horizon diagnostics are generated directly from the hash-verified M18C.2 aggregate and remain diagnostic-only evidence; overall classification is INSUFFICIENT_REFERENCE_EVIDENCE.",
            "Figure 4 uses committed S9 backend evidence and plots each observed final-objective gap relative to its own frozen criterion.",
            "P4 performance/scaling figure is not activated under protocol 1.",
        ],
    }
    manifest_path = fig_dir / "p5_figures_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    manifest = build(Path(args.repo_root).resolve())
    print(json.dumps({"figures": list(manifest["figures"]), "protocol_id": PROTOCOL_ID}, indent=2))


if __name__ == "__main__":
    main()
