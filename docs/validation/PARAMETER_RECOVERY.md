# Parameter Recovery Protocol

M18 uses simulation-based parameter recovery rather than fixture replay.

For each selected binary HGF-family model:

```text
transformed theta_true
        |
        v
native transform -> simulate responses -> MAP fit -> transformed theta_hat
```

## Frozen axes

Final gate:

- models: HGF binary, eHGF binary, uHGF binary;
- trial counts: 128 and 256;
- parameter regimes: deterministic perturbations of 0.15 and 0.35 prior SD;
- six replicates per trial-count/regime/model;
- deterministic seeds;
- frozen default MAP start;
- frozen compatibility quasi-Newton optimizer.

Truth variation is applied only to parameters that are free under the frozen model config.
Fixed, undefined, and placeholder semantics are not altered.

## Metrics

Report by parameter and in aggregate:

- bias;
- RMSE;
- median absolute error;
- true-vs-estimated correlation;
- RMSE standardized by the empirical spread of simulated truth;
- convergence rate;
- trial-count and parameter-regime strata.

Failures remain in the denominator. They are not silently dropped.

## Minimum M18 criteria

For every generating model:

- convergence rate >= 0.80;
- median recoverability correlation >= 0.50;
- median standardized RMSE <= 1.00.

These thresholds are frozen before the gate run. Paper-level analyses may report richer
confidence intervals and larger grids, but may not retroactively change the M18 gate.

## Active correction requirements — 2026-09-11

Paired diagnosis must run the identical archived M18 datasets in MATLAB and Python, with shared responses/random drivers, transformed truths, priors and starts. Report parameter errors and inference differences separately. Conditional slices and truth-start/oracle fits are diagnostics, not proof of joint identifiability or replacement gate fits. A successor protocol must freeze design, numeric thresholds and holdout seeds before confirmation; it cannot overwrite historical M18.
