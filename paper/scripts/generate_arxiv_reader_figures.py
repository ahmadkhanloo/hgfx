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
style_axis(ax)
fig.tight_layout()
save(fig, "fig1_reference_sensitivity")


# Figure 2 — paired model-selection agreement as one clear reader-facing claim.
models = ["hgf_binary", "ehgf_binary", "uhgf_binary"]
model_labels = ["classic HGF", "enhanced HGF", "unbounded HGF"]
criteria = s7["criteria_unchanged"]
mr = s7["model_recovery"]

# Remove the superseded mixed recovery/model-selection rendering.
for suffix in ("png", "pdf"):
    (OUT / f"fig2_recovery_and_model_selection.{suffix}").unlink(missing_ok=True)

fig, ax = plt.subplots(figsize=(7.4, 4.5))
values = [mr["matlab_balanced_accuracy"], mr["hgfx_balanced_accuracy"]]
bars = ax.bar(
    ["MATLAB 8.2.0", "HGFX 1.0.0"],
    values,
    width=0.48,
    color=[MATLAB, HGFX],
    alpha=0.9,
)
threshold = criteria["model_balanced_accuracy_min"]
ax.axhline(
    threshold,
    color=DARK,
    linestyle="--",
    linewidth=1.1,
    label=f"predeclared balanced-accuracy criterion = {threshold:g}",
)
ax.set_ylim(0, 1.02)
ax.set_ylabel("Balanced accuracy")
ax.set_title("Paired model selection is identical across MATLAB and HGFX", pad=12)
for bar, value in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.025,
        f"{value:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )
ax.legend(frameon=False, loc="upper right")
style_axis(ax)
fig.text(
    0.5,
    0.02,
    f'{mr["winner_matches"]}/{mr["total_cases"]} paired BIC winner decisions agree exactly',
    ha="center",
    fontsize=10,
    weight="bold",
)
fig.tight_layout(rect=(0, 0.06, 1, 1))
save(fig, "fig2_model_selection_agreement")


# Figure 3 — prospective trial-horizon diagnostic.
horizons = [128, 256, 512, 1024]
hidx = np.arange(len(horizons), dtype=float)
fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4), sharex=True)
horizon_metrics = [
    (
        "median_correlation",
        f"Median parameter correlation  (target ≥ {p3['criteria']['median_correlation_min']:g})",
        p3["criteria"]["median_correlation_min"],
    ),
    (
        "median_standardized_rmse",
        f"Median standardized RMSE  (target ≤ {p3['criteria']['median_standardized_rmse_max']:g})",
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
            linewidth=1.8,
            markersize=5,
        )
        ax.plot(
            hidx,
            vals_h,
            color=model_colors[model],
            marker="x",
            linestyle="--",
            linewidth=1.15,
            markersize=5,
            alpha=0.9,
        )
    ax.axhline(threshold, color=DARK, linestyle=":", linewidth=1.2)
    ax.set_xticks(hidx, [str(h) for h in horizons])
    ax.set_xlabel("Trial horizon")
    ax.set_ylabel(ylabel)
    style_axis(ax)

axes[0].set_title("Correlation across trial horizons")
axes[1].set_title("Standardized error across trial horizons")

from matplotlib.lines import Line2D
model_handles = [
    Line2D([0], [0], color=model_colors[m], lw=2, label=lab)
    for m, lab in zip(models, model_labels)
]
engine_handles = [
    Line2D([0], [0], color=DARK, marker="o", lw=1.7, label="MATLAB 8.2.0"),
    Line2D([0], [0], color=DARK, marker="x", linestyle="--", lw=1.1, label="HGFX 1.0.0"),
]
legend_models = fig.legend(
    handles=model_handles,
    loc="upper center",
    ncol=3,
    frameon=False,
    bbox_to_anchor=(0.5, 1.07),
    fontsize=8.5,
)
fig.add_artist(legend_models)
fig.legend(
    handles=engine_handles,
    loc="upper center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.5, 1.005),
    fontsize=8.2,
)
fig.suptitle(
    "Prospective trial-horizon diagnostic; incomplete classic-HGF cells remain as gaps",
    y=1.17,
    fontsize=11.5,
)
fig.text(
    0.5,
    0.01,
    "The preregistered paired-integrity requirement was not satisfied; the curves are diagnostic rather than evidence for identifiability.",
    ha="center",
    fontsize=8.5,
)
fig.tight_layout(rect=(0, 0.05, 1, 0.91))
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
