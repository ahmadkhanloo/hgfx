# M18 S7 Paired Recovery — Reference-Limitation Disposition

Status: **REFERENCE_LIMITATION_MATCH — release-acceptable in the frozen S7 protocol scope**

Frozen protocol: `m18-s7-paired-recovery-1`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
HGFX tested commit: `96daac8e8fe889deaf1c8c4b5f92f2c6f676262c`
Official paired run: `34896442847`
Aggregate job: `104163079125`
Aggregate artifact: `10370615292`
Artifact SHA-256: `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92`
Decision record: `../../reference/validation/m18_s7_reference_limitation/decision.json`

## Scope

This disposition covers only the complete frozen S7 paired-recovery grid:

- perceptual models: `hgf_binary`, `ehgf_binary`, `uhgf_binary`;
- observation model: `unitsq_sgm` default frozen configuration;
- trial counts: `128`, `256`;
- truth perturbation scales: `0.15`, `0.35` prior SD;
- six parameter-recovery replicates per model/trial-count/scale stratum;
- three model-recovery replicates per generating-model/trial-count/scale stratum;
- identical exported inputs, responses, truth vectors, parameter semantics and default starts in MATLAB and HGFX;
- identical candidate order `[hgf_binary, ehgf_binary, uhgf_binary]` and minimum-BIC winner rule;
- default compatibility quasinewton workflow.

Coverage is complete: 12 shards, 72 parameter-recovery cases and 36 model-recovery datasets, with three candidate fits per model-recovery dataset. No case was removed, replaced or resampled.

## Result

The official aggregate classification is `REFERENCE_LIMITATION_REVIEW_REQUIRED`, which is deliberately not an automatic PASS. Review under `MATLAB_REFERENCE_LIMITATIONS_POLICY.md` establishes `REFERENCE_LIMITATION_MATCH` for parameter recovery in this exact protocol scope.

### Parameter recovery

For every model, MATLAB and HGFX have the **same frozen criterion outcomes** and nearly identical aggregate metrics.

| Model | MATLAB convergence | HGFX convergence | MATLAB median corr | HGFX median corr | MATLAB median sRMSE | HGFX median sRMSE | Disposition |
|---|---:|---:|---:|---:|---:|---:|---|
| HGF | 0.8333333333 | 0.8333333333 | 0.2026845702 | 0.2026845701 | 2.6096628455 | 2.6096628455 | `REFERENCE_LIMITATION_MATCH` |
| eHGF | 0.9166666667 | 0.9166666667 | 0.4619183691 | 0.4619183691 | 2.3591268882 | 2.3591268887 | `REFERENCE_LIMITATION_MATCH` |
| uHGF | 0.7916666667 | 0.7916666667 | 0.3809683136 | 0.3809683136 | 2.9578866197 | 2.9578866181 | `REFERENCE_LIMITATION_MATCH` |

Frozen scientific thresholds were not changed:

- convergence rate >= `0.80`;
- median parameter correlation >= `0.50`;
- median standardized RMSE <= `1.00`.

HGF and eHGF meet the convergence threshold but both implementations fail correlation and sRMSE. uHGF fails all three criteria in both implementations. These remain scientific/model-identifiability limitations of the tested workflows, not scientific PASS claims.

The MATLAB/HGFX differences in median correlation are approximately `2.3e-11`, `1.7e-11`, and `8.3e-12` for eHGF/HGF/uHGF respectively. The largest MATLAB/HGFX difference in median standardized RMSE is approximately `1.6e-9`. Convergence rates are identical for all three models.

### Model recovery / selection

Model-selection behavior passes directly:

- `36/36` BIC winners match between MATLAB and HGFX;
- balanced accuracy is `0.5833333333333334` in both implementations;
- row-normalized confusion matrices are identical;
- classification: `PASS_PAIRED_MODEL_SELECTION`.

## Evidence integrity

The historical M18 scientific FAIL remains preserved and is not relabeled.

A real HGFX-only HGF semantic defect discovered while localizing S7/S8 was repaired before this final paired run: standard HGF level-1 prediction must follow the frozen `_original_models/hgf_binary.m` oracle without the clamp that belongs to other paths. Product repair commit: `0239f52f772825e0a4fc74cdf3559cafa18a603e`. Post-repair R0 fitting traces/endpoints returned inside the frozen numerical gate.

A separate S7 measurement defect was also corrected without changing any fit: the frozen MATLAB optimizer allows the tenth reset and may subsequently converge, so `reset_count == 10` is not itself a non-convergence condition. Commit `96daac8e8fe889deaf1c8c4b5f92f2c6f676262c` captures the frozen optimizer's own terminal warnings and uses those to infer termination. The same data, thresholds, starts, models and optimizer settings were retained.

The final paired aggregate therefore contains no unresolved required-scope implementation, optimizer, or model-selection mismatch. The shared parameter-recovery failures are scientifically/numerically comparable and satisfy the repository policy for `REFERENCE_LIMITATION_MATCH`.

## Release interpretation

For HGFX v1.0 MATLAB-equivalence accounting:

- paired parameter recovery: **REFERENCE_LIMITATION_MATCH** in this exact frozen protocol scope;
- paired model recovery/model selection: **PASS_PAIRED_MODEL_SELECTION**;
- S7 product-equivalence closure: **DONE / release-acceptable**;
- S8: no unresolved S7-derived HGFX-only repair remains; the evidence-linked HGF defect is repaired and regression-backed;
- next gate: **S9 robustness/backend/physical-GPU applicability closure**.

This disposition must not be generalized to other trial horizons, datasets, seeds, truth scales, starts, model families or observation models.