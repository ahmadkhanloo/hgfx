"""Generate reader-facing arXiv figures from committed machine-readable evidence.

The canonical validation figures and frozen evidence are intentionally left unchanged.
This script only changes presentation: it uses reader-facing labels, quantitative
values and predeclared criteria, while preserving the original data and outcomes.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper" / "arxiv" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

MATLAB = "#0072B2"
HGFX = "#D55E00"
ACCENT = "#009E73"
SECONDARY = "#CC79A7"
DARK = "#333333"
GRID = "#D9D9D9"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.65)
    ax.set_axisbelow(True)


def save(fig, stem: str):
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(
        OUT / f"{stem}.pdf",
        bbox_inches="tight",
        facecolor="white",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


d02 = load("reference/validation/m18_d02_reference_limitation/decision.json")
d08 = load("reference/validation/m18_d08_reference_limitation/decision.json")
s7 = load("reference/validation/m18_s7_reference_limitation/decision.json")
gpu = load("gpu_validation_results/m18_s9_physical_gpu_revalidation.json")
pyhgf_raw = load("paper/reproducibility/p2a10_raw_numeric_result_35268575414.json")
pyhgf_cmp = load("paper/reproducibility/p2a10_comparison_35268575414.json")
p3 = load("paper/reproducibility/p3_m18c2_aggregate_35272347167.json")


# Figure 1 — why the two sensitive fitting cases are treated as reference limitations.
labels = ["Enhanced-HGF\nfitting stress case", "uHGF holdout\nfixed seed"]
records = [
    d02["matlab_self_sensitivity_evidence"],
    d08["matlab_self_sensitivity_evidence"],
]
fractions = [
    r["materially_different_endpoints"] / r["perturbations"] for r in records
]
counts = [
    f'{r["materially_different_endpoints"]}/{r["perturbations"]}' for r in records
]

fig, ax = plt.subplots(figsize=(7.2, 4.2))
bars = ax.bar(labels, fractions, width=0.58, color=[MATLAB, SECONDARY], alpha=0.9)
ax.set_ylim(0, 1.08)
ax.set_ylabel("Fraction of one-spacing start perturbations\nending outside the original endpoint tolerance")
ax.set_title("MATLAB reference sensitivity in the two numerically fragile fits", pad=12)
for bar, count, value in zip(bars, counts, fractions):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.025,
        f"{count} ({100*value:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax.text(
    0.01,
    0.02,
    "Same model, data, optimizer and tolerance; only a one-local-spacing start perturbation changes.",
    transform=ax.transAxes,
    fontsize=8.5,
)
style_axis(ax)
fig.tight_layout()
save(fig, "fig1_reference_sensitivity")


# Figure 2 — parameter recovery and model selection, with raw metrics against criteria.
models = ["hgf_binary", "ehgf_binary", "uhgf_binary"]
model_labels = ["classic HGF", "enhanced HGF", "unbounded HGF"]
criteria = s7["criteria_unchanged"]
metrics = [
    ("convergence_rate", criteria["convergence_rate_min"], "Convergence rate", "higher"),
    ("median_correlation", criteria["median_correlation_min"], "Median parameter correlation", "higher"),
    (
        "median_standardized_rmse",
        criteria["median_standardized_rmse_max"],
        "Median standardized RMSE",
        "lower",
    ),
]

fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0))
x = np.arange(len(models))
width = 0.34
for ax, (key, threshold, title, direction) in zip(axes.flat[:3], metrics):
    matlab_vals = np.array([s7["parameter_recovery"][m]["matlab"][key] for m in models])
    hgfx_vals = np.array([s7["parameter_recovery"][m]["hgfx"][key] for m in models])
    ax.bar(x - width / 2, matlab_vals, width, label="MATLAB 8.2.0", color=MATLAB)
    ax.bar(x + width / 2, hgfx_vals, width, label="HGFX 1.0.0", color=HGFX)
    ax.axhline(threshold, color=DARK, linestyle="--", linewidth=1.1)
    ax.text(
        0.99,
        0.96,
        f"predeclared criterion: {'≥' if direction == 'higher' else '≤'} {threshold:g}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
    )
    ax.set_xticks(x, model_labels, rotation=12)
    ax.set_title(title)
    style_axis(ax)

mr = s7["model_recovery"]
ax = axes.flat[3]
model_values = [
    mr["matlab_balanced_accuracy"],
    mr["hgfx_balanced_accuracy"],
    mr["winner_matches"] / mr["total_cases"],
]
model_names = ["MATLAB balanced\naccuracy", "HGFX balanced\naccuracy", "BIC winner\nagreement"]
bars = ax.bar(model_names, model_values, color=[MATLAB, HGFX, ACCENT], width=0.62)
ax.axhline(criteria["model_balanced_accuracy_min"], color=DARK, linestyle="--", linewidth=1.1)
ax.set_ylim(0, 1.06)
ax.set_title("Model selection")
for i, (bar, value) in enumerate(zip(bars, model_values)):
    label = f"{value:.3f}"
    if i == 2:
        label += f"\n({mr['winner_matches']}/{mr['total_cases']})"
    ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, label, ha="center", fontsize=8.5)
style_axis(ax)

handles, labels_legend = axes.flat[0].get_legend_handles_labels()
fig.legend(handles, labels_legend, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.995))
fig.suptitle(
    "Paired recovery reproduces the reference metrics; model-selection winners agree in all 36 datasets",
    y=1.035,
    fontsize=12,
)
fig.tight_layout(rect=(0, 0, 1, 0.95))
save(fig, "fig2_recovery_and_model_selection")


# Figure 3 — prospective trial-horizon diagnostic.
horizons = [128, 256, 512, 1024]
hidx = np.arange(len(horizons), dtype=float)
fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2), sharex=True)
horizon_metrics = [
    ("median_correlation", "Median parameter correlation", p3["criteria"]["median_correlation_min"]),
    (
        "median_standardized_rmse",
        "Median standardized RMSE",
        p3["criteria"]["median_standardized_rmse_max"],
    ),
]
model_colors = {"hgf_binary": MATLAB, "ehgf_binary": ACCENT, "uhgf_binary": SECONDARY}

for ax, (key, ylabel, threshold) in zip(axes, horizon_metrics):
    for model, model_label in zip(models, model_labels):
        vals_m = []
        vals_h = []
        for h in horizons:
            rec_m = p3["parameter_recovery"][model]["horizons"][str(h)]["matlab"]
            rec_h = p3["parameter_recovery"][model]["horizons"][str(h)]["hgfx"]
            vals_m.append(rec_m.get(key, np.nan) if rec_m.get("complete") else np.nan)
            vals_h.append(rec_h.get(key, np.nan) if rec_h.get("complete") else np.nan)
        ax.plot(
            hidx,
            vals_m,
            color=model_colors[model],
            marker="o",
            linewidth=1.7,
            label=f"{model_label} — MATLAB",
        )
        ax.plot(
            hidx,
            vals_h,
            color=model_colors[model],
            marker="x",
            linestyle="--",
            linewidth=1.1,
            alpha=0.8,
            label=f"{model_label} — HGFX",
        )
    ax.axhline(threshold, color=DARK, linestyle=":", linewidth=1.2)
    ax.set_xticks(hidx, [str(h) for h in horizons])
    ax.set_xlabel("Trial horizon")
    ax.set_ylabel(ylabel)
    style_axis(ax)

axes[0].set_title("Correlation")
axes[1].set_title("Standardized RMSE")
handles, leg = axes[0].get_legend_handles_labels()
fig.legend(handles, leg, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.06), fontsize=8)
fig.suptitle(
    "Prospective trial-horizon diagnostic; incomplete classic-HGF cells remain visible as gaps",
    y=1.16,
    fontsize=11.5,
)
fig.text(
    0.5,
    -0.01,
    "The predeclared paired-integrity requirement was not satisfied, so these trajectories are diagnostic rather than evidence for identifiability.",
    ha="center",
    fontsize=8.5,
)
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
save(fig, "fig3_horizon_diagnostics")


# Figure 4 — physical GPU numerical agreement.
cases = gpu["physical_gpu"]["cases"]
gaps = np.array([c["final_objective_gap"] for c in cases], dtype=float)
case_labels = [
    f'{c["trials"]} trials\n{c["regime"].replace("_", " ")}' for c in cases
]
threshold = gpu["criteria"]["jax_cpu_vs_physical_gpu_final_objective_gap_max"]

fig, ax = plt.subplots(figsize=(8.0, 4.3))
x = np.arange(len(cases))
ax.scatter(x, gaps, s=75, color=ACCENT, zorder=3)
ax.axhline(threshold, color=DARK, linestyle="--", linewidth=1.1, label=f"predeclared criterion = {threshold:g}")
ax.set_yscale("symlog", linthresh=1e-16)
ax.set_xticks(x, case_labels)
ax.set_ylabel("Absolute CPU–GPU final-objective difference")
ax.set_title("Physical GPU execution reproduces CPU fitting objectives in all four tested cells")
for i, gap in enumerate(gaps):
    ax.annotate("0" if gap == 0 else f"{gap:.2e}", (i, gap), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8)
ax.legend(frameon=False)
style_axis(ax)
fig.tight_layout()
save(fig, "fig4_gpu_numerical_agreement")


# Figure 5 — pyhgf common-scope trajectory comparison plus residual magnitude.
hgfx_p = np.asarray(pyhgf_raw["hgfx"]["fields"]["first_level_predicted_probability"], dtype=np.float64)
pyhgf_p = np.asarray(pyhgf_raw["pyhgf"]["fields"]["first_level_predicted_probability"], dtype=np.float64)
hgfx_mu = np.asarray(pyhgf_raw["hgfx"]["fields"]["level_2_posterior_mean"], dtype=np.float64)
pyhgf_mu = np.asarray(pyhgf_raw["pyhgf"]["fields"]["level_2_posterior_mean"], dtype=np.float64)
trials = np.arange(1, hgfx_p.size + 1)
p_resid = np.abs(hgfx_p - pyhgf_p)

fig, axes = plt.subplots(3, 1, figsize=(9.2, 7.0), sharex=True, gridspec_kw={"height_ratios": [1, 1, 0.65]})
axes[0].plot(trials, hgfx_p, color=MATLAB, lw=1.5, label="HGFX 1.0.0")
axes[0].plot(trials, pyhgf_p, color=HGFX, lw=1.0, linestyle="--", label="pyhgf 0.3.2")
axes[0].set_ylabel("Predicted p(u=1)")
axes[0].legend(frameon=False, ncol=2)
style_axis(axes[0])

axes[1].plot(trials, hgfx_mu, color=MATLAB, lw=1.5)
axes[1].plot(trials, pyhgf_mu, color=HGFX, lw=1.0, linestyle="--")
axes[1].set_ylabel("Level-2 posterior mean")
style_axis(axes[1])

axes[2].plot(trials, p_resid, color=ACCENT, lw=1.1)
axes[2].set_yscale("symlog", linthresh=1e-17)
axes[2].set_ylabel("|Δ predicted p|")
axes[2].set_xlabel("Trial")
style_axis(axes[2])

max_err = pyhgf_cmp["field_results"]["first_level_predicted_probability"]["max_abs_error"]
fig.suptitle(
    f"Common-scope perceptual trajectories overlap to binary64 scale (max |Δp| = {max_err:.2e})",
    y=0.995,
    fontsize=11.5,
)
fig.text(
    0.5,
    0.01,
    "Participant-response NLL is reported separately because the two implementations do not provide a defensible common numerical surface at the exact probability boundary.",
    ha="center",
    fontsize=8.3,
)
fig.tight_layout(rect=(0, 0.04, 1, 0.96))
save(fig, "fig5_pyhgf_common_scope")
