# M18 S7 Paired Recovery Protocol

Protocol: **`m18-s7-paired-recovery-1`**
Status: **FROZEN BEFORE EXECUTION**
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`
HGFX protocol-freeze parent: `26b8b8db477a604acc6f623386675b9d91374b59`

## Objective

Determine whether HGFX reproduces the parameter-recovery and model-recovery behavior of the frozen MATLAB HGF Toolbox on the original M18 recovery grid. This is a product-equivalence protocol. It does **not** rewrite the historical M18 scientific experiment or its FAIL result.

The paired unit is the same exported dataset, truth vector, parameter semantics, starting point, model family, observation model and optimizer workflow evaluated by both implementations.

## Frozen grid

Perceptual models:

- `hgf_binary`
- `ehgf_binary`
- `uhgf_binary`

Observation model: `unitsq_sgm` with its default frozen config.

Trial counts: `[128, 256]`.

Truth perturbation scales: `[0.15, 0.35]` prior standard deviations.

Parameter-recovery replicates: **6 per model × trial-count × truth-scale stratum**.

Model-recovery replicates: **3 per generating-model × trial-count × truth-scale stratum**.

Candidate model set and order: `[hgf_binary, ehgf_binary, uhgf_binary]`.

Model-selection rule: minimum **BIC**. AIC is retained as a diagnostic only and cannot replace BIC after results are observed.

Workload:

- parameter recovery: `3 × 2 × 2 × 6 = 72` fits;
- model recovery: `3 × 2 × 2 × 3 = 36` generated datasets, each fit by 3 candidate models = `108` fits;
- total paired fitting workload per implementation = **180 fits**.

Execution may be sharded by `(generating/model, trial_count, truth_scale)`. Sharding may not remove, substitute, or resample cases.

## Frozen deterministic case generation

The case generator preserves the existing HGFX M18 deterministic protocol rather than inventing a new successful subset.

For parameter-recovery scale `s`, base seed is:

`18018 + round(10000*s)`.

For a trial count `T` and zero-based replicate `r`:

`run_seed = base_seed + 100*T + r`.

For model recovery, scale base seed is:

`18018 + 500000 + round(10000*s)`.

For zero-based generating-model index `g` in the frozen candidate order:

`run_seed = base_seed + 1000000*g + 100*T + r`.

Inputs, truth vectors and simulated responses are exported once by the case generator and become immutable paired inputs. Both MATLAB and HGFX must fit the exact exported `u` and `y`; cross-language RNG identity is never assumed.

Truth-vector construction is the existing M18 rule in transformed coordinates:

`theta_true_free = prior_mu_free + s * sqrt(prior_var_free) * sin((r+1) * phase * 1.61803398875)`

with `phase = [1, ..., n_free]` in the already-validated free-parameter order. Fixed parameters remain unchanged.

The exported case records native/transformed truth vectors, free indices, priors, input/response data, seeds, model/config identity and hashes.

## Frozen fitting contract

MATLAB:

- perceptual configs: `hgf_binary_config`, `ehgf_binary_config`, `uhgf_binary_config`;
- observation config: `unitsq_sgm_config`;
- fitting entry point: `fitModel(y, u, perceptual_config, observation_config, 'quasinewton_optim_config')`;
- default priors/default transformed start from the resolved configs; no restart/seed/start substitution after observing results.

HGFX:

- matching compatibility configs and parameter order;
- `fit_binary_variant` / validated compatibility objective;
- default `QuasiNewtonOptions(max_iter=100)` matching the historical gate budget;
- same exported `u`, `y` and default transformed start.

No candidate/model substitution is permitted to rescue a failed case.

## Historical scientific criteria retained

No new easier scientific thresholds are introduced. The original frozen M18 criteria remain:

- parameter convergence rate >= `0.80`;
- parameter median correlation >= `0.50`;
- parameter median standardized RMSE <= `1.00`;
- model-recovery balanced accuracy >= `0.50`.

These criteria are evaluated separately for MATLAB and HGFX on the same complete paired grid.

## Product-equivalence acceptance

### Parameter recovery

For each perceptual model, compute the same historical aggregate metrics and per-stratum diagnostics for both implementations.

Product-level parameter-recovery classification:

- `PASS_PAIRED_RECOVERY_BEHAVIOR` only if MATLAB and HGFX have the same PASS/FAIL outcome for every frozen historical parameter criterion and no case is missing/substituted;
- `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` if MATLAB satisfies a historical criterion that HGFX fails, or required fit execution differs due to an HGFX-only error;
- `REFERENCE_LIMITATION_MATCH` may be used only when both fail the same historical criterion on the same complete grid and the paired raw evidence supports comparable behavior with no earlier HGFX-only semantic divergence;
- `INSUFFICIENT_REFERENCE_EVIDENCE` when the comparison cannot support one of the above.

Per-fit endpoint, objective, Hessian and termination differences are always retained diagnostically; they are not silently ignored and may trigger S8 localization if they alter recovery behavior.

### Model recovery

For every one of the 36 frozen generated datasets, MATLAB and HGFX must fit the same three candidates and select the BIC minimum.

- all 36 BIC winners identical => `PASS_PAIRED_MODEL_SELECTION`;
- any BIC winner differs => `MODEL_SELECTION_MISMATCH` unless a separately frozen exact-case MATLAB limitation is established;
- balanced accuracy and confusion matrices are reported for both implementations using the frozen generating-model labels.

AIC cannot override a BIC disagreement.

## Failure handling

All fit failures, non-finite results, max-iteration terminations, candidate scores and raw outputs are retained. No failed replicate may be dropped or replaced.

Primary classifications remain:

- `IMPLEMENTATION_MISMATCH`
- `OPTIMIZER_MISMATCH`
- `MODEL_SELECTION_MISMATCH`
- `REFERENCE_LIMITATION_MATCH`
- `INSUFFICIENT_REFERENCE_EVIDENCE`

S8 repairs may start only from demonstrated required-scope mismatches and require a failing regression fixture before product-code repair.

## Separation from M18C.2

Issue #21 / M18C.2 (`128/256/512/1024` horizon analysis) is a separate preregistered experiment. Its results cannot change this protocol's grid, thresholds, replicates, seeds, candidates or classification rules.

## Evidence package

Each shard and the aggregate report must record:

- protocol ID and protocol file hash;
- MATLAB reference SHA and HGFX tested SHA;
- case IDs, seeds, data/truth/config hashes;
- environment/runtime versions;
- exact commands;
- raw MATLAB/HGFX fit outputs and failures;
- per-case BIC/AIC/final/objective/termination diagnostics;
- aggregate recovery metrics and confusion matrices;
- artifact IDs and SHA-256 digests;
- final supported classification.

No M18/v1 PASS follows from implementation of this protocol alone. Only completed evidence can close S7.
