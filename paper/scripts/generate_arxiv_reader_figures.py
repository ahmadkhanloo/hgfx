"""Generate reader-facing arXiv figures from committed machine-readable evidence.

These figures avoid internal validation IDs in the main narrative while preserving
exact repository traceability in the appendices. They do not change any scientific
threshold, classification, seed, dataset, optimizer, or validation grid.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper" / "arxiv_figures"
OUT.mkdir(parents=True, exist_ok=True)


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


s7 = load("reference/validation/m18_s7_reference_limitation/decision.json")
gpu = load("gpu_validation_results/m18_s9_physical_gpu_revalidation.json")
pyhgf = load("paper/reproducibility/p2a10_comparison_35268575414.json")
p3 = load("paper/reproducibility/p3_m18c2_aggregate_35272347167.json")

# Figure 1: evidence classes.
fig = plt.figure(figsize=(8.2, 3.6))
ax = fig.add_axes([0.04, 0.08, 0.92, 0.84])
ax.axis("off")
labels = [
    ("Direct parity", "Reference and HGFX agree\nunder frozen protocol/tolerance"),
    ("Matched reference limitation", "Reference exhibits the same\nnumerical/workflow limitation"),
    ("Preserved failure", "Scientific criterion not met;\nnegative result remains visible"),
    ("Not directly comparable", "No defensible common numerical\nsurface for that quantity"),
]
xs = [0.13, 0.38, 0.63, 0.88]
for x, (title, desc) in zip(xs, labels):
    ax.text(x, 0.66, title, ha="center", va="center", fontsize=11, fontweight="bold")
    ax.text(x, 0.43, desc, ha="center", va="center", fontsize=9)
for a, b in zip(xs[:-1], xs[1:]):
    ax.annotate("", xy=(b - 0.09, 0.82), xytext=(a + 0.09, 0.82),
                arrowprops=dict(arrowstyle="->", lw=1.1))
ax.text(0.5, 0.08,
        "Negative and limited results are not promoted to scientific PASS.",
        ha="center", va="center", fontsize=9)
fig.savefig(OUT / "fig1_evidence_classes.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 2: paired recovery criteria, normalized to pass-oriented threshold ratios.
models = ["hgf_binary", "ehgf_binary", "uhgf_binary"]
display = ["classic HGF", "enhanced HGF", "unbounded HGF"]
conv = np.array([s7["parameter_recovery"][m]["matlab"]["convergence_rate"] for m in models])
corr = np.array([s7["parameter_recovery"][m]["matlab"]["median_correlation"] for m in models])
srmse = np.array([s7["parameter_recovery"][m]["matlab"]["median_standardized_rmse"] for m in models])
criteria = s7["criteria_unchanged"]
ratios = np.vstack([
    conv / criteria["convergence_rate_min"],
    corr / criteria["median_correlation_min"],
    criteria["median_standardized_rmse_max"] / srmse,
]).T

fig = plt.figure(figsize=(8.2, 4.4))
ax = fig.add_axes([0.12, 0.22, 0.84, 0.70])
x = np.arange(len(models))
for j, (offset, name) in enumerate(zip([-0.22, 0, 0.22],
                                        ["Convergence", "Median correlation", "Standardized RMSE"])):
    ax.scatter(x + offset, ratios[:, j], s=55, label=name)
ax.axhline(1.0, linestyle="--", linewidth=1)
ax.set_xticks(x, display, rotation=12)
ax.set_ylabel("Pass-oriented criterion ratio (>=1 passes)")
ax.set_title("Paired parameter-recovery criteria on the frozen grid")
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.15))
ax.grid(axis="y", alpha=0.25)
fig.savefig(OUT / "fig2_recovery_metrics.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 3: model-selection agreement.
mr = s7["model_recovery"]
vals = [mr["winner_matches"] / mr["total_cases"],
        mr["matlab_balanced_accuracy"], mr["hgfx_balanced_accuracy"]]
fig = plt.figure(figsize=(7.6, 4.2))
ax = fig.add_axes([0.12, 0.20, 0.84, 0.70])
labels3 = ["BIC winner agreement", "MATLAB balanced accuracy", "HGFX balanced accuracy"]
ax.bar(np.arange(3), vals)
ax.set_xticks(np.arange(3), labels3, rotation=12)
ax.set_ylim(0, 1.08)
ax.set_ylabel("Fraction")
ax.set_title("Paired model-selection result")
for i, value in enumerate(vals):
    ax.text(i, value + 0.025, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
ax.grid(axis="y", alpha=0.25)
fig.savefig(OUT / "fig3_model_selection.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 4: physical GPU applicability.
cases = gpu["physical_gpu"]["cases"]
gaps = np.array([c["final_objective_gap"] for c in cases], dtype=float)
plot_gaps = np.where(gaps == 0, 1e-18, gaps)
labels4 = [f'{c["trials"]} {c["regime"].replace("_", " ")}' for c in cases]
fig = plt.figure(figsize=(7.8, 4.2))
ax = fig.add_axes([0.12, 0.23, 0.84, 0.68])
ax.scatter(np.arange(len(cases)), plot_gaps, s=60)
ax.axhline(gpu["criteria"]["jax_cpu_vs_physical_gpu_final_objective_gap_max"],
           linestyle="--", linewidth=1, label="Frozen criterion")
ax.set_yscale("log")
ax.set_xticks(np.arange(len(cases)), labels4, rotation=12)
ax.set_ylabel("Absolute CPU-GPU final-objective gap")
ax.set_title("Physical Tesla T4 applicability")
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
fig.savefig(OUT / "fig4_gpu_applicability.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 5: pyhgf common-scope mapped perceptual errors (exclude NDC response quantities).
ordered = [
    ("derived_first_level_input_surprise", "Input surprise"),
    ("derived_first_level_prediction_error", "Prediction error"),
    ("first_level_predicted_probability", "Predicted p"),
    ("level_2_posterior_mean", "L2 post. mean"),
    ("level_2_posterior_precision", "L2 post. precision"),
    ("level_2_predicted_mean", "L2 pred. mean"),
    ("level_2_predicted_precision", "L2 pred. precision"),
    ("level_3_posterior_mean", "L3 post. mean"),
    ("level_3_posterior_precision", "L3 post. precision"),
    ("level_3_predicted_mean", "L3 pred. mean"),
    ("level_3_predicted_precision", "L3 pred. precision"),
]
errs = [pyhgf["field_results"][k]["max_abs_error"] for k, _ in ordered]
fig = plt.figure(figsize=(8.2, 4.7))
ax = fig.add_axes([0.12, 0.32, 0.84, 0.60])
ax.scatter(np.arange(len(ordered)), errs, s=48)
ax.set_yscale("log")
ax.set_xticks(np.arange(len(ordered)), [v for _, v in ordered], rotation=52, ha="right")
ax.set_ylabel("Maximum absolute difference")
ax.set_title("HGFX vs pyhgf 0.3.2 mapped perceptual quantities")
ax.grid(axis="y", alpha=0.25)
fig.savefig(OUT / "fig5_pyhgf_common_scope.pdf", bbox_inches="tight")
plt.close(fig)

# Figure 6: horizon diagnostic, MATLAB values; paired HGFX values are numerically coincident
# at the plotted scale for complete cells.
horizons = np.array([128, 256, 512, 1024])
fig = plt.figure(figsize=(7.8, 4.4))
ax = fig.add_axes([0.12, 0.18, 0.84, 0.74])
for model, label in zip(models, display):
    vals = []
    for h in horizons:
        cell = p3["parameter_recovery"][model]["horizons"][str(h)]["matlab"]
        vals.append(cell.get("median_correlation", np.nan) if cell.get("complete") else np.nan)
    ax.plot(horizons, vals, marker="o", label=label)
ax.axhline(p3["criteria"]["median_correlation_min"], linestyle="--", linewidth=1,
           label="Frozen correlation criterion")
ax.set_xscale("log", base=2)
ax.set_xticks(horizons, [str(x) for x in horizons])
ax.set_xlabel("Trial horizon")
ax.set_ylabel("Median parameter correlation")
ax.set_title("Prospective trial-horizon diagnostic")
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
fig.savefig(OUT / "fig6_horizon_diagnostics.pdf", bbox_inches="tight")
plt.close(fig)
