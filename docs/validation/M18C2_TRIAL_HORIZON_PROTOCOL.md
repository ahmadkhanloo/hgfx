# M18C.2 Trial-Horizon / Identifiability Protocol

Protocol: **`m18c2-trial-horizon-identifiability-1`**  
Status: **FROZEN BEFORE EXECUTION**  
Tracking: GitHub issue #21 / PV1-01  
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`  
HGFX protocol parent: `f9d4b81acb7d7478882b6268497a1f5870374bd1`

## Objective

Determine whether the preserved M18 parameter-recovery limitations are primarily explained by the available trial horizon or persist at substantially longer horizons in a way consistent with weak/structural identifiability.

This is a post-v1 research experiment. It does **not** reopen or rewrite the historical M18 result, S7 classification, v1 release gate, thresholds, seeds, model family, optimizer, or reference oracle.

The experiment is paired: the same immutable generated `u`, `y`, truth vectors, candidate models, starting points, and fitting workflow are evaluated by the frozen MATLAB reference and HGFX. Scientific interpretation is withheld if the two implementations diverge at the criterion or BIC-winner level.

## Frozen grid

Perceptual models and candidate order:

1. `hgf_binary`
2. `ehgf_binary`
3. `uhgf_binary`

Observation model: `unitsq_sgm` with the frozen default configuration.

Trial horizons: `[128, 256, 512, 1024]`.

Truth perturbation scales: `[0.15, 0.35]` prior standard deviations.

Parameter-recovery replicates: **6 per model × horizon × truth-scale stratum**.

Model-recovery replicates: **3 per generating-model × horizon × truth-scale stratum**.

Model-selection rule: minimum **BIC**. AIC is retained only as a diagnostic.

Workload per implementation:

- parameter recovery: `3 × 4 × 2 × 6 = 144` fits;
- model recovery: `3 × 4 × 2 × 3 = 72` generated datasets, each fit by 3 candidates = `216` fits;
- total: **360 fits per implementation**.

Execution may be sharded by `(model, trial_horizon, truth_scale)`. No shard, failed case, replicate, or candidate may be dropped, substituted, or resampled.

## Frozen deterministic case generation

M18C.2 extends the S7 trial horizon only. It preserves the S7 deterministic generation policy exactly.

For parameter recovery at scale `s`:

`base_seed = 18018 + round(10000*s)`

For trial horizon `T` and zero-based replicate `r`:

`run_seed = base_seed + 100*T + r`

For model recovery:

`base_seed = 18018 + 500000 + round(10000*s)`

For zero-based generating-model index `g` in the frozen candidate order:

`run_seed = base_seed + 1000000*g + 100*T + r`

Inputs, truth vectors and simulated responses are exported once by the Python preparer and become immutable paired inputs for both implementations. Cross-language RNG identity is not assumed.

Truth-vector construction remains:

`theta_true_free = prior_mu_free + s * sqrt(prior_var_free) * sin((r+1) * phase * 1.61803398875)`

with `phase = [1, ..., n_free]` in the validated free-parameter order. Fixed parameters remain unchanged.

## Frozen fitting contract

MATLAB:

- perceptual configs: `hgf_binary_config`, `ehgf_binary_config`, `uhgf_binary_config`;
- observation config: `unitsq_sgm_config`;
- fitting entry point: `fitModel(y, u, perceptual_config, observation_config, 'quasinewton_optim_config')`;
- default transformed start from the resolved configs;
- no restarts, alternative starts, candidate substitution, or optimizer changes after observing outcomes.

HGFX:

- matching compatibility configs and validated parameter order;
- `fit_binary_variant` with the compatibility objective;
- `QuasiNewtonOptions(max_iter=100)`;
- the exact same exported `u`, `y`, model identity, and default transformed start.

## Frozen scientific criteria

The original M18 criteria are reused unchanged and evaluated separately at each horizon:

- parameter convergence rate >= `0.80`;
- parameter median correlation >= `0.50`;
- parameter median standardized RMSE <= `1.00`;
- model-recovery balanced accuracy >= `0.50`.

Parameter metrics are reported per model × horizon, aggregating both frozen truth scales. Scale-specific summaries are also retained as diagnostics.

Model-recovery accuracy is reported per horizon across the complete generating-model/truth-scale grid, with row-normalized confusion matrices.

No threshold may be relaxed after execution.

## Required metrics and diagnostics

For parameter recovery report, at minimum:

- convergence rate;
- bias per free parameter;
- RMSE per free parameter;
- standardized RMSE per free parameter;
- correlation per free parameter and median finite correlation;
- median absolute error;
- `negLj`, `negLl`, termination, iteration and reset diagnostics for every fit.

For model recovery report, at minimum:

- MATLAB and HGFX selected BIC winner for every dataset;
- BIC/AIC values for all candidates;
- balanced accuracy and confusion matrix per horizon;
- all winner disagreements, if any.

For likelihood/curvature diagnostics, retain the fitted objective values and optimizer curvature information available from HGFX. For each successful HGFX fit, symmetrize the final inverse-Hessian approximation and record its eigenvalue spectrum, finite rank, and condition number when defined. MATLAB LME and optimizer-trace fields are retained where the frozen reference exposes them. These curvature quantities are **diagnostic only**: no post-hoc numeric cutoff is used to turn them into a PASS.

## Paired integrity gate

Before any data-horizon interpretation:

1. all 24 shards must be present;
2. all 144 parameter cases and 72 model-recovery datasets must be unique and complete;
3. MATLAB and HGFX must use the same free-parameter indices for every fitted case;
4. MATLAB and HGFX must have the same PASS/FAIL outcome for each frozen parameter criterion at each model × horizon;
5. every model-recovery BIC winner must agree between MATLAB and HGFX.

If any item fails, the overall classification is `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` or `INSUFFICIENT_REFERENCE_EVIDENCE`, as appropriate, and no scientific identifiability conclusion is promoted.

## Preregistered horizon interpretation

For each perceptual model, define the **256-horizon failing set** as the frozen parameter criteria that fail at `T=256` in both implementations after the paired integrity gate passes.

Per-model interpretation:

- `NO_256_FAILURE_TO_EXPLAIN`: the 256-horizon failing set is empty.
- `DATA_HORIZON_LIMITATION_SUPPORTED`: the 256-horizon failing set is non-empty and every criterion in that set passes at `T=1024` in both implementations, with no criterion that passed at `T=256` regressing to FAIL at `T=1024`.
- `PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED`: at least one criterion in the 256-horizon failing set still fails at `T=1024` in both implementations.
- `MIXED_HORIZON_EFFECT_INCONCLUSIVE`: evidence is complete and paired, but the 256→1024 pattern does not satisfy either rule above.

The `128` and `512` horizons are used to show trajectory and detect non-monotonic behavior; they do not replace the preregistered 256→1024 comparison.

Overall interpretation:

- if any paired-integrity mismatch exists: `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`;
- otherwise, if one or more models are `PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED`: `PERSISTENT_IDENTIFIABILITY_LIMITATION_SUPPORTED`;
- otherwise, if one or more models are `DATA_HORIZON_LIMITATION_SUPPORTED` and none are persistent: `DATA_HORIZON_LIMITATION_SUPPORTED`;
- otherwise: `MIXED_OR_INCONCLUSIVE`.

These labels are evidential classifications, not proofs of mathematical identifiability. Persistent failure at 1024 supports a weak/structural-identifiability interpretation but does not by itself prove structural non-identifiability.

## Evidence package

Every shard and aggregate report must record:

- protocol ID;
- frozen MATLAB reference SHA;
- HGFX tested SHA;
- exact case IDs, seeds and immutable shard hashes;
- runtime and environment versions;
- exact commands/workflow run IDs;
- raw MATLAB and HGFX fit outputs, including failures;
- parameter metrics, likelihood/curvature diagnostics and model-selection evidence;
- aggregate horizon tables and preregistered classification;
- artifact names/IDs and SHA-256 digests where available.

## Historical evidence preservation

M18, D02/D08, S7, S8, S9, M19, M20 and v1.0.0 evidence remain immutable historical records. M18C.2 may explain the preserved scientific limitation, but it may not retroactively convert any historical FAIL into PASS or change the v1.0.0 compatibility claim.
