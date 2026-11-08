# REV-1.2 audit protocol — existing S7 recovery uncertainty

Status: **FROZEN BEFORE REV-1.2 ANALYSIS EXECUTION** (2026-11-09).
Parent authority: `docs/planning/COMPSTAT_REVISION_PLAN.md` §REV-1.2, and the
already-frozen `m18-s7-paired-recovery-1` grid. This adds statistical summaries
only. It does not regenerate data, rerun fitting, or modify M18 results.

## Inputs and verification

- Original run: GitHub Actions `34896442847`, its **12 original shard ZIP
  artifacts**, each containing immutable `*-manifest.json` and
  `*-comparison.json`. Check all hashes against
  `evidence/revision/confusion_audit.json` before calculations.
- Exactly 72 parameter-recovery fits per implementation (24 per perceptual
  model) and 36 distinct generating datasets for model selection (12 per row).
- Require per-case success, identity, complete `truth_free` and `final_free`
  vectors, identical free-index order within each model, and no missing
  entries. If incomplete, record missing cases rather than exclude them.
- The three free transformed coordinates in each S7 binary-model configuration
  are `om_2` (omega2), `om_3` (omega3), `logze` (log zeta), as defined in
  `src/hgfx/compat/configs.py` and `src/hgfx/compat/simulation.py`.
  Free indices are [12,13,14] (zero-based); verify for every case.
- Do not pool MATLAB and HGFX observations as independent replicates; the data
  are paired by case ID.

## Statistical procedures (frozen now, before execution)

- Report **95%** two-sided Clopper–Pearson exact-binomial CIs for the
  model-specific convergence proportion (successes over 24) in each
  implementation and for correct model-recovery fraction per generating row
  (successes over 12). Also include exact CI for 36/36 cross-implementation
  winner agreement, clearly distinct from model-recovery accuracy.
- Chance benchmark for each generating row is **1/3**, with an exact binomial
  **one-sided greater-than-chance** p-value and two-sided p-value recorded.
  These are descriptive, conditional on independent and identically
  distributed binomial trials; the frozen grid is deterministic and stratified,
  so nominal inferential coverage/generalization is not established.
- Per-parameter central points: Pearson correlation of true vs fitted
  transformed coordinates over 24 cases and sRMSE = sqrt(mean((fit-truth)^2)) /
  population SD(truth, ddof=0). Reproduce existing central medians by taking
  the median across all three per-coordinate values. Retain all original
  central values; never substitute CI endpoints for point estimates.
- **Bootstrap:** B=2000, NumPy PCG64 generator `np.random.default_rng(20261109)`;
  95% percentile interval with `np.quantile(...,[0.025,0.975],method="linear")`.
  The 24 parameter-recovery observations per model contain only 12 unique
  truth vectors: the (truth-scale, replicate) pairs are reused at both
  horizons. Thus the resampling unit is the **12 paired-horizon clusters**
  (two scale values × six replicates), drawn with replacement, preserving
  both horizons and MATLAB/HGFX case pairing. Within each draw, recompute
  per-coordinate correlation, sRMSE and their 3-parameter median, preserving
  the same denominator formula. An undefined resampled SD/correlation is
  marked nonfinite; report valid-resample count, do not silently replace,
  drop historical cases, or redraw. If fewer than 1900/2000 bootstrap draws
  are valid for any statistic, mark its interval `null` and classify the
  limitation explicitly rather than relaxing this quality requirement.
- Report the per-coordinate estimates and intervals as **primary** results,
  the median-across-coordinates as secondary. Correlations cannot be
  interpreted as fit-level agreement merely because MATLAB/HGFX are close.
- Do not introduce a new scientific PASS criterion. Existing M18 thresholds:
  convergence >=0.80; median r >=0.50; median sRMSE <=1.00;
  balanced accuracy >=0.50. These remain unchanged.

## Outputs and stopping rule

- `evidence/revision/recovery_uncertainty.json`: hashes, protocol metadata,
  CIs, p-values, complete per-parameter and pooled summaries,
  model-recovery counts, cross-implementation agreement, bootstrap validity.
- `paper/computational_statistics/figures/`: **new revision-only** Figure 2
  (recovery and intervals) and Figure 3 (BIC/model-recovery accuracy with
  1/3 chance line and exact per-row intervals), PDF and PNG. Historical frozen
  `paper/figures/` remains unmodified. Existing central plotted values are
  preserved.
- One analysis on the archived records, one report, no optimizer runs.
  Any numerical/methodological discrepancy is reported and **not** corrected
  by changing evidence, seeds, thresholds, the frozen grid, or the protocol.
- Targeted tests and a single targeted CI workflow; stage the report as
  `IN PROGRESS` until results are verified and registered in the ledger.
