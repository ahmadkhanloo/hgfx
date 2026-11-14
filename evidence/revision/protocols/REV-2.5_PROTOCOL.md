# REV-2.5 protocol — redesigned parameter/model recovery study (HGFX)

Status: FROZEN_BEFORE_EXECUTION (committed before any run; the timing probe
below is reconnaissance, not the run).
Task: `COMPSTAT_REVISION_PLAN.md` REV-2.5. One run; infrastructure rerun cap 1;
incremental checkpoint files are infrastructure, not reruns. Terminal states
apply; results are reported whatever they are. No tolerance is invented or
relaxed; the four predeclared thresholds are unchanged.

## Declared limitation (frozen now)

The plan's paired MATLAB subset (first 30 datasets per generating model) is
**NOT RUN**: no local MATLAB oracle exists, and CI-triggered MATLAB is an
external action outside this task. The study is therefore **HGFX-only** and
its conclusions are scoped to released HGFX behavior
(`hgfx==1.0.0` wheel, SHA-256 `5c63c16d...88b90`); implementation-independence
across MATLAB/HGFX is a recorded DOCUMENTED_LIMITATION for this task.

## Amendment before execution (reconnaissance findings, 2026-11-14)

A pre-run reconnaissance probe found two behaviors that would break the
preregistered schedule if unhandled; this amendment is committed before the
single run:

1. **Simulation failures are real protocol data.** Prior-drawn truths place a
   substantial fraction of classic-HGF datasets in the documented
   negative-posterior-precision region (`ValueError: Negative posterior
   precision. Parameters are in a region where model assumptions are
   violated.`); these stay in denominators exactly as the protocol already
   requires.
2. **Pathological fits can exceed any reasonable wall-clock budget** (one
   `uhgf_binary` T=512 prior-draw fit ran > 6 minutes without returning;
   typical fits are ~5-10 ms). Each dataset task therefore runs in an
   isolated worker process with a **240-second wall-clock guard**; a task
   exceeding the guard is classified `timeout`, stays in the denominator as
   a failure, and is checkpointed so a resumed run never re-hangs. The guard
   is infrastructure, not a scientific criterion, and per-fit optimizer
   settings are untouched.

## Design

- Models: `hgf_binary`, `ehgf_binary`, `uhgf_binary`, each with
  `unitsq_sgm`; horizons `T in {128, 256, 512}`.
- **Parameter recovery**: full design `N = 100` datasets per model per T.
  Truth: transformed free parameters drawn from the resolved priors —
  `theta_free = prior_mean_free + sqrt(prior_variance_free) * z`,
  `z = PCG64(seed).standard_normal(n_free)`, only free entries replaced
  (fixed entries stay at resolved defaults; free-index set = released
  `optimization_indices` of the resolved config). Dataset seed =
  `2026111500 + model_idx*1_000_000 + T_idx*10_000 + d`; inputs
  `u = PCG64(2026111501 + model_idx*1_000_000 + T_idx*10_000 + d).
  integers(0, 2, size=T)`; responses simulated with the released
  `simulate_binary_variant` at `seed = dataset_seed + 1`. Invalid simulations
  (exception/nonfinite) are logged and counted in the denominator, never
  redrawn.
- **Model recovery**: full design `M = 60` datasets per generating model per
  T, generated exactly as above (separate seed space:
  `2026111500 + 3_000_000 + model_idx*1_000_000 + T_idx*10_000 + d`); each
  dataset is fit by **all three** candidate models; winner = minimum BIC from
  the released result fields; ties or all-invalid are class `no_winner`.
- **Fits**: three starts per (dataset, fitting model) — start 0 = resolved
  prior mean, starts 1-2 = prior-scheme random draws with seeds
  `2026111502 + model_idx*1_000_000 + T_idx*10_000 + d*10 + s`; the best
  objective (lowest negative log joint; ties by negative log likelihood)
  is retained; **all three runs are logged** (objective, termination,
  exception). Convergence uses the released fit's own definition:
  `optimizer.termination in {"tol_grad", "tol_arg"}`; `NOT_EXPORTED` is
  recorded if a field is absent.
- **Fallback (preregistered trigger):** a pre-execution timing probe of 20
  representative fits projects the total runtime; if it exceeds **6 hours**,
  the uniform 50% fallback applies (`N = 50`, `M = 30`) with all seeds,
  models, horizons and starts retained — never a selective reduction.

## Metrics and reporting (thresholds unchanged)

- Per-parameter Pearson correlation, standardized RMSE (population SD of
  truths, `ddof=0`), and bias, computed in **transformed space** over valid
  pairs; failures stay in the denominator and are reported separately.
- Convergence rate from the retained run's termination.
- Model-recovery confusion matrix (rows = generating model), balanced
  accuracy, exact binomial test vs chance `1/3` per generating row, and
  Clopper–Pearson 95% CIs for convergence rate, per-row correct-recovery and
  balanced accuracy.
- The four predeclared thresholds are applied as stated (convergence >= 0.80,
  median correlation >= 0.50, median standardized RMSE <= 1.00, balanced
  accuracy >= 0.50) and per-parameter/row compliance is reported; **no result
  is relabeled** to meet them.
- BIC-based identifiability note for omega3 is descriptive only.

## Outputs

- `evidence/revision/rev25_recovery_redesign.json` (dataset manifest hashes,
  per-fit logs, aggregated metrics, thresholds table),
  `evidence/revision/rev25_recovery_scatter.png` (per-parameter truth-vs-fit
  scatter for the primary family), `evidence/revision/rev25_model_recovery.png`
  (confusion matrices per horizon).
- Practical guidance sentence(s) for the article; manuscript integration is a
  later REV-3 editorial step requiring author review. This study makes no
  scientific PASS statement and changes no frozen result.
