"""Generate the three canonical reader-facing arXiv figures from frozen evidence.

This presentation follows the visual language of the revised preprint reviewed
by the author: compact multi-panel scientific figures, direct paired markers,
explicit criteria, incomplete cells shown rather than imputed, and residuals
shown separately when overlapping trajectories would hide numerical differences.

Scientific data, thresholds, seeds, classifications, and interpretations are
unchanged. Only vector PDF assets are retained in paper/arxiv/figures/.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper" / "arxiv" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

MATLAB = "#4C7899"
HGFX = "#C97855"
ACCENT = "#4F8F80"
DARK = "#333333"
GRID = "#E2E2E2"
INCOMPLETE = "#F2F3F4"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def style_axis(ax, *, axis: str = "x"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=axis, color=GRID, linewidth=0.7, alpha=0.85)
    ax.set_axisbelow(True)


def save(fig, stem: str):
    fig.savefig(
        OUT / f"{stem}.pdf",
        bbox_inches="tight",
        facecolor="white",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054):
    p = successes / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denom
    half = z * np.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n) / denom
    return center - half, center + half


s7 = load("reference/validation/m18_s7_reference_limitation/decision.json")
p3 = load("paper/reproducibility/p3_m18c2_aggregate_35272347167.json")
pyhgf_raw = load("paper/reproducibility/p2a10_raw_numeric_result_35268575414.json")

# Delete superseded arXiv figure assets. Historical paper/figures evidence is untouched.
for stem in (
    "fig1_reference_sensitivity",
    "fig2_model_selection_agreement",
    "fig3_horizon_diagnostics",
    "fig4_gpu_numerical_agreement",
    "fig5_pyhgf_common_scope",
    "fig2_recovery_and_model_selection",
):
    for suffix in ("pdf", "png"):
        (OUT / f"{stem}.{suffix}").unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Figure 1 — paired parameter-recovery summaries, in the visual form preferred
# in HGFX_revised_preprint.pdf. Agreement and scientific recovery quality are
# visible at the same time; model-selection is deliberately not mixed in.
# ---------------------------------------------------------------------------
models = ["hgf_binary", "ehgf_binary", "uhgf_binary"]
model_labels = ["Classic HGF", "Enhanced HGF", "Unbounded HGF"]
criteria = s7["criteria_unchanged"]
metrics = [
    (
        "convergence_rate",
        "Convergence",
        "Fraction; target ≥ 0.80",
        0.0,
        1.02,
        float(criteria["convergence_rate_min"]),
    ),
    (
        "median_correlation",
        "Correlation",
        "Median r; target ≥ 0.50",
        0.0,
        0.66,
        float(criteria["median_correlation_min"]),
    ),
    (
        "median_standardized_rmse",
        "Recovery error",
        "sRMSE; target ≤ 1.00",
        0.0,
        3.25,
        float(criteria["median_standardized_rmse_max"]),
    ),
]

fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.75), sharey=True)
y = np.arange(len(models))[::-1].astype(float)
dy = 0.075

for panel_idx, (ax, (key, title, xlabel, xmin, xmax, threshold)) in enumerate(zip(axes, metrics)):
    matlab_vals = np.array([s7["parameter_recovery"][m]["matlab"][key] for m in models], dtype=float)
    hgfx_vals = np.array([s7["parameter_recovery"][m]["hgfx"][key] for m in models], dtype=float)

    # Reorder arrays to match top-to-bottom display.
    matlab_vals = matlab_vals
    hgfx_vals = hgfx_vals

    for i, yy in enumerate(y):
        ax.plot(
            [matlab_vals[i], hgfx_vals[i]],
            [yy + dy, yy - dy],
            color="#B9B9B9",
            linewidth=1.0,
            zorder=1,
        )

    if key == "convergence_rate":
        # 24 cases per family in the frozen recovery grid.
        successes = [20, 22, 19]
        for i, (xval, k) in enumerate(zip(matlab_vals, successes)):
            lo, hi = wilson_interval(k, 24)
            ax.errorbar(
                xval,
                y[i] + dy,
                xerr=np.array([[xval - lo], [hi - xval]]),
                fmt="none",
                ecolor=MATLAB,
                elinewidth=1.2,
                capsize=2.5,
                alpha=0.78,
                zorder=2,
            )
        for i, (xval, k) in enumerate(zip(hgfx_vals, successes)):
            lo, hi = wilson_interval(k, 24)
            ax.errorbar(
                xval,
                y[i] - dy,
                xerr=np.array([[xval - lo], [hi - xval]]),
                fmt="none",
                ecolor=HGFX,
                elinewidth=1.05,
                capsize=2.5,
                alpha=0.72,
                zorder=2,
            )

    ax.scatter(matlab_vals, y + dy, s=38, facecolor="white", edgecolor=MATLAB, linewidth=1.35, marker="o", zorder=3)
    ax.scatter(hgfx_vals, y - dy, s=38, color=HGFX, marker="x", linewidth=1.35, zorder=4)

    ax.axvline(threshold, color="#777777", linestyle=":", linewidth=1.1)
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel(xlabel)
    ax.set_title(f"{chr(65 + panel_idx)}  {title}", loc="left", fontweight="bold", fontsize=10.2, pad=9)
    style_axis(ax, axis="x")

    # Direct labels show the HGFX point estimate; MATLAB rounds identically.
    label_offset = 0.018 * (xmax - xmin)
    for xval, yy in zip(hgfx_vals, y):
        ax.text(
            min(xval + label_offset, xmax - 0.055 * (xmax - xmin)),
            yy - dy,
            f"{xval:.3f}",
            va="center",
            ha="left",
            fontsize=7.7,
            color=DARK,
        )

axes[0].set_yticks(y, model_labels)
for ax in axes[1:]:
    ax.tick_params(labelleft=False)

legend_handles = [
    Line2D([0], [0], color=MATLAB, marker="o", markerfacecolor="white", lw=1.2, label="MATLAB 8.2.0"),
    Line2D([0], [0], color=HGFX, marker="x", lw=1.2, label="HGFX 1.0.0"),
]
fig.legend(handles=legend_handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.03), fontsize=8.7)
fig.tight_layout(rect=(0, 0, 1, 0.93), w_pad=2.2)
save(fig, "fig1_recovery_metrics")


# ---------------------------------------------------------------------------
# Figure 2 — prospective trial-horizon diagnostic as a 2 x 3 small-multiple
# grid. Incomplete classic-HGF 512/1024 summaries are explicit shaded regions.
# ---------------------------------------------------------------------------
horizons = [128, 256, 512, 1024]
x = np.arange(len(horizons), dtype=float)
fig, axes = plt.subplots(2, 3, figsize=(10.25, 6.2), sharex="col")
row_specs = [
    ("median_correlation", "Median parameter r", float(p3["criteria"]["median_correlation_min"]), (-0.30, 1.05)),
    ("median_standardized_rmse", "Median sRMSE", float(p3["criteria"]["median_standardized_rmse_max"]), (0.0, 3.45)),
]

for col, (model, model_label) in enumerate(zip(models, model_labels)):
    axes[0, col].set_title(model_label, fontweight="bold", fontsize=10.2, pad=9)
    for row, (key, ylabel, threshold, ylim) in enumerate(row_specs):
        ax = axes[row, col]
        vals_m, vals_h = [], []
        complete_mask = []
        for h in horizons:
            rec_m = p3["parameter_recovery"][model]["horizons"][str(h)]["matlab"]
            rec_h = p3["parameter_recovery"][model]["horizons"][str(h)]["hgfx"]
            complete = bool(rec_m.get("complete")) and bool(rec_h.get("complete"))
            complete_mask.append(complete)
            vals_m.append(rec_m.get(key, np.nan) if complete else np.nan)
            vals_h.append(rec_h.get(key, np.nan) if complete else np.nan)

        vals_m = np.asarray(vals_m, dtype=float)
        vals_h = np.asarray(vals_h, dtype=float)

        ax.plot(x, vals_m, color=MATLAB, marker="o", markerfacecolor="white", markersize=4.8, linewidth=1.35, zorder=3)
        ax.plot(x, vals_h, color=HGFX, marker="x", markersize=5.0, linewidth=1.0, linestyle="--", zorder=4)
        ax.axhline(threshold, color="#777777", linestyle=":", linewidth=1.0)
        ax.set_ylim(*ylim)
        ax.set_xticks(x, [str(h) for h in horizons])
        style_axis(ax, axis="y")

        if model == "hgf_binary":
            ax.axvspan(1.55, 3.45, color=INCOMPLETE, zorder=0)
            ax.text(2.5, ylim[0] + 0.70 * (ylim[1] - ylim[0]), "Incomplete", ha="center", va="center", fontsize=8.5, color="#777777")

        if col == 0:
            ax.set_ylabel(ylabel)
        else:
            ax.tick_params(labelleft=False)
        if row == 1:
            ax.set_xlabel("Trials")

legend_handles = [
    Line2D([0], [0], color=MATLAB, marker="o", markerfacecolor="white", lw=1.35, label="MATLAB 8.2.0"),
    Line2D([0], [0], color=HGFX, marker="x", linestyle="--", lw=1.0, label="HGFX 1.0.0"),
]
fig.legend(handles=legend_handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.01), fontsize=8.7)
fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=1.6, w_pad=1.5)
save(fig, "fig2_horizon_diagnostics")


# ---------------------------------------------------------------------------
# Figure 3 — pyhgf common-scope trajectories with a separate signed residual
# panel in units of 1e-16. The residual is linear, not symlog.
# ---------------------------------------------------------------------------
hgfx_p = np.asarray(pyhgf_raw["hgfx"]["fields"]["first_level_predicted_probability"], dtype=np.float64)
pyhgf_p = np.asarray(pyhgf_raw["pyhgf"]["fields"]["first_level_predicted_probability"], dtype=np.float64)
hgfx_mu = np.asarray(pyhgf_raw["hgfx"]["fields"]["level_2_posterior_mean"], dtype=np.float64)
pyhgf_mu = np.asarray(pyhgf_raw["pyhgf"]["fields"]["level_2_posterior_mean"], dtype=np.float64)
trials = np.arange(1, hgfx_p.size + 1)
signed_residual = (hgfx_p - pyhgf_p) * 1e16

fig, axes = plt.subplots(3, 1, figsize=(9.3, 6.0), sharex=True, gridspec_kw={"height_ratios": [1.0, 1.0, 0.72]})

axes[0].plot(trials, hgfx_p, color=MATLAB, linewidth=1.35, label="HGFX 1.0.0")
axes[0].plot(trials, pyhgf_p, color=HGFX, linewidth=1.0, linestyle="--", label="pyhgf 0.3.2")
axes[0].set_ylabel("Predicted P(u = 1)")
axes[0].set_ylim(0.0, 1.02)
style_axis(axes[0], axis="y")

axes[1].plot(trials, hgfx_mu, color=MATLAB, linewidth=1.35)
axes[1].plot(trials, pyhgf_mu, color=HGFX, linewidth=1.0, linestyle="--")
axes[1].set_ylabel(r"Posterior mean $\mu_2$")
style_axis(axes[1], axis="y")

axes[2].plot(trials, signed_residual, color=MATLAB, linewidth=0.95)
axes[2].axhline(0.0, color="#8A8A8A", linewidth=0.8)
axes[2].set_ylabel(r"$\Delta p$ ($\times 10^{-16}$)")
axes[2].set_xlabel("Trial")
style_axis(axes[2], axis="y")

for label, ax in zip(("A", "B", "C"), axes):
    ax.text(-0.075, 0.86, label, transform=ax.transAxes, fontweight="bold", fontsize=10)

fig.legend(
    handles=[
        Line2D([0], [0], color=MATLAB, lw=1.35, label="HGFX 1.0.0"),
        Line2D([0], [0], color=HGFX, lw=1.0, linestyle="--", label="pyhgf 0.3.2"),
    ],
    loc="upper center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.5, 1.015),
    fontsize=8.7,
)
fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=0.8)
save(fig, "fig3_pyhgf_common_scope")
