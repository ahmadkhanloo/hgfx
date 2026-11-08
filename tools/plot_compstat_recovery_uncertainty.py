#!/usr/bin/env python3
"""REV-1.2: revision-only Figures 2 and 3, preserving original point estimates."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MODELS = ("hgf_binary", "ehgf_binary", "uhgf_binary")
PARAMS = ("omega2", "omega3", "log_zeta")
COLORS = {"matlab": "#4c78a8", "hgfx": "#f58518"}
LABEL = {"hgf_binary": "HGF", "ehgf_binary": "eHGF", "uhgf_binary": "uHGF"}


def bounds(value: dict) -> tuple[float, float]:
    lo, hi = value["ci95"]
    pt = value.get("estimate", value.get("rate", value.get("fraction")))
    if not lo <= pt <= hi:
        raise ValueError("point estimate outside its interval")
    return pt-lo, hi-pt


def save(fig: plt.Figure, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight", facecolor="white",
                metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def figure2(data: dict, output: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5))
    models = np.arange(3)
    metrics = (("convergence", "Convergence rate", 0.80),
               ("median_correlation", "Median correlation (secondary)", 0.50),
               ("median_srmse", "Median sRMSE (secondary)", 1.00))
    for ax, (metric, title, threshold) in zip(axes[0], metrics):
        for impl, offset in (("matlab", -0.17), ("hgfx", 0.17)):
            values, lowers, uppers = [], [], []
            for model in MODELS:
                d = data["per_model"][model]["implementations"][impl]
                v = d["convergence"] if metric == "convergence" else d["pooled_secondary"][metric]
                values.append(v["rate"] if metric == "convergence" else v["estimate"])
                lo, hi = bounds(v)
                lowers.append(lo); uppers.append(hi)
            ax.bar(models+offset, values, width=0.32, color=COLORS[impl], alpha=0.90,
                   label="MATLAB 8.2.0" if impl == "matlab" else "HGFX 1.0.0")
            ax.errorbar(models+offset, values, yerr=[lowers, uppers], fmt="none",
                        ecolor="#262626", capsize=2, linewidth=0.9)
        ax.axhline(threshold, linestyle="--", linewidth=1, color="#444444")
        ax.set_xticks(models, [LABEL[m] for m in MODELS])
        ax.set_title(title, fontsize=11)
        if metric == "convergence":
            ax.set_ylim(0, 1.08)
        elif metric == "median_correlation":
            ax.set_ylim(-0.65, 1)
        else:
            ax.set_ylim(0, 6.2)
    for ax, (metric, title, threshold) in zip(
        axes[1],
        (("correlation", "Pearson r by transformed parameter", 0.50),
         ("srmse", "Standardized RMSE by parameter", 1.00)),
    ):
        xx = np.arange(9)
        for impl, dx in (("matlab", -0.16), ("hgfx", 0.16)):
            pts, lower, upper = [], [], []
            for model in MODELS:
                for p in PARAMS:
                    v = data["per_model"][model]["implementations"][impl]["parameters"][p][metric]
                    pts.append(v["estimate"])
                    lo, hi = bounds(v)
                    lower.append(lo); upper.append(hi)
            ax.errorbar(xx+dx, pts, yerr=[lower, upper], fmt="o", linestyle="none",
                        markersize=4, elinewidth=1.15, capsize=2, color=COLORS[impl])
        ax.axhline(threshold, color="#444444", linestyle="--", linewidth=0.9)
        ax.set_xticks(xx, [p.replace("log_zeta", "log ζ") for m in MODELS for p in PARAMS],
                      rotation=35, ha="right")
        ax.set_title(title, fontsize=11)
        for cut in (2.5, 5.5):
            ax.axvline(cut, color="#dddddd", linewidth=0.8)
        if metric == "correlation":
            ax.axhline(0, color="#999999", linewidth=0.7)
            ax.set_ylim(-1, 1)
        else:
            ax.set_ylim(0, 7.4)
    axes[1, 2].axis("off")
    axes[1, 2].text(
        0.02, 0.93,
        "Per-parameter results are primary.\n"
        "Top-row medians remain unchanged.\n\n"
        "Bootstrap: B=2000, seed=20261109\n"
        "Resampling unit: 12 paired-horizon\n"
        "truth-scale × replicate clusters/model.\n\n"
        "Thin error bars: 95% intervals.\n"
        "Dashed lines: original M18 thresholds.\n\n"
        "Original historical figures untouched.",
        va="top", ha="left", fontsize=10)
    fig.suptitle(
        "S7 recovery: point estimates retained, uncertainty added (not scientific PASS)",
        fontsize=13)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2,
               bbox_to_anchor=(0.5, 0.975), frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, output)


def figure3(data: dict, output: Path) -> None:
    mr = data["model_recovery"]
    fig, (ax0, ax1) = plt.subplots(
        1, 2, figsize=(11.7, 4.7), gridspec_kw={"width_ratios": [1.05, 1]})
    for i, model in enumerate(MODELS):
        v = mr["per_generating_model"][model]
        lo, hi = bounds(v)
        ax0.bar(i, v["fraction"], width=0.5, color="#4c78a8")
        ax0.errorbar([i], [v["fraction"]], yerr=[[lo], [hi]],
                     fmt="none", ecolor="#222222", capsize=4, linewidth=1)
        ax0.text(i, max(v["fraction"]+hi+0.02, 0.1),
                 f"{v['correct']}/{v['n']}", ha="center", fontsize=10)
    ax0.axhline(1/3, color="#444444", linestyle=":", linewidth=1.1, label="chance = 1/3")
    ax0.set_xticks(range(3), [LABEL[m] for m in MODELS])
    ax0.set_ylim(0, 1.1)
    ax0.set_ylabel("correct generating-model fraction")
    ax0.set_title("Model recovery: per-class exact 95% CI")
    ax0.legend(loc="upper left", frameon=False)
    original = [mr["matlab_balanced_accuracy"], mr["hgfx_balanced_accuracy"],
                mr["paired_winner_agreement"]["rate"]]
    ax1.bar(range(3), original,
            color=["#4c78a8", "#f58518", "#54a24b"], width=0.65)
    lo, hi = bounds(mr["paired_winner_agreement"])
    ax1.errorbar(2, 1, yerr=[[lo], [hi]], fmt="none",
                 ecolor="#222222", capsize=4, linewidth=1)
    ax1.axhline(0.50, color="#333333", linestyle="--", linewidth=1,
                label="frozen balanced-accuracy threshold")
    ax1.axhline(1/3, color="#888888", linestyle=":", linewidth=1,
                label="three-class chance baseline")
    ax1.set_xticks(range(3),
                   ["MATLAB balanced\naccuracy", "HGFX balanced\naccuracy",
                    "BIC winner\nagreement"])
    ax1.set_ylim(0, 1.12)
    ax1.set_ylabel("fraction")
    ax1.set_title("Original three aggregate values retained")
    ax1.legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle(
        "S7 model recovery: model-selection parity is not identification", fontsize=12)
    fig.text(0.5, 0.01,
             "Exact-binomial intervals are conditional/descriptive; deterministic S7 grid is not an i.i.d. population sample.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    save(fig, output)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path,
                    default=Path("evidence/revision/recovery_uncertainty.json"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("paper/computational_statistics/figures"))
    args = ap.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    if data["bootstrap"]["B"] != 2000 or data["bootstrap"]["seed"] != 20261109:
        raise ValueError("unapproved bootstrap protocol")
    fig2 = args.out_dir/"fig2_recovery_uncertainty.png"
    fig3 = args.out_dir/"fig3_model_recovery_uncertainty.png"
    figure2(data, fig2)
    figure3(data, fig3)
    result = {"source": str(args.source),
              "source_sha256": sha256(args.source.read_bytes()).hexdigest(),
              "figures": {p.name: sha256(p.read_bytes()).hexdigest() for p in
                          (fig2, fig2.with_suffix(".pdf"),
                           fig3, fig3.with_suffix(".pdf"))}}
    (args.out_dir/"revision_figures_manifest.json").write_text(
        json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
