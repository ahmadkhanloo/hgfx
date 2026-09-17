# HGFX Methods Paper Protocol

Protocol ID: **`hgfx-paper-protocol-1`**  
Status: **FROZEN_FOR_EXECUTION**  
Frozen on: **2026-09-17**  
Tracking: PV1-02 / GitHub issue #32  
HGFX product source: **`v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`**  
MATLAB compatibility oracle: **HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`**

This protocol freezes the paper-specific claim set, prospective research analyses, comparator policy, reporting rules, and provenance requirements before final paper-only experiments are executed. It does not reopen M18, M19, M20, or the v1.0.0 release gate.

## 1. Primary paper claim set

The primary contribution tested and reported by this paper is:

> HGFX v1.0.0 is a Python/JAX implementation designed to reproduce the documented scientific and workflow behavior of the frozen MATLAB HGF Toolbox 8.2.0 reference across explicitly validated scopes, while preserving and disclosing matched reference limitations instead of converting them into scientific PASS results.

The paper may additionally report:

1. prospective trial-horizon evidence about the preserved parameter-recovery limitations;
2. paired model-selection evidence;
3. neutral positioning relative to `pyhgf` on semantically overlapping and non-overlapping surfaces;
4. frozen v1 physical-GPU applicability/correctness evidence.

The initial submission protocol does **not** make general speedup or multi-GPU scaling a headline scientific claim. A new post-v1 performance benchmark is therefore **not activated in protocol version 1**. Any later decision to add a performance headline requires a new protocol revision frozen before those final runs.

## 2. Immutable historical evidence policy

The following records are immutable historical evidence and are not rerun or reclassified merely to improve the paper narrative:

- historical M18 scientific validation, including its preserved FAIL;
- D02 and D08 direct failures and their accepted scoped `REFERENCE_LIMITATION_MATCH` interpretation;
- S7 parameter-recovery and paired model-selection evidence;
- S8 repair evidence;
- S9 CPU/backend and physical-GPU applicability evidence;
- M19 `PASS/FROZEN` release evidence;
- M20 release-candidate evidence;
- v1.0.0 release and PyPI publication provenance.

`REFERENCE_LIMITATION_MATCH` is never reported as parameter-recovery PASS, direct fit parity, or proof of scientific correctness.

## 3. Paper evidence classes

Every numerical or categorical result used in the paper must be classified as one of:

- `PASS`
- `IMPLEMENTATION_MISMATCH`
- `OPTIMIZER_MISMATCH`
- `MODEL_SELECTION_MISMATCH`
- `REFERENCE_LIMITATION_MATCH`
- `NOT_DIRECTLY_COMPARABLE`
- `INSUFFICIENT_REFERENCE_EVIDENCE`
- historical `FAIL`

No result may be omitted because it is negative, inconvenient, or inconsistent with the preferred narrative.

## 4. Prospective recovery / identifiability experiment

The paper retains PV1-01 / issue #21 as a prospective analysis. Its settings are frozen here consistently with protocol `m18c2-trial-horizon-identifiability-1`.

### 4.1 Models and observation model

Perceptual model candidate order:

1. `hgf_binary`
2. `ehgf_binary`
3. `uhgf_binary`

Observation model: `unitsq_sgm` with the frozen default configuration.

### 4.2 Trial horizons and truth scales

Trial horizons:

```text
128, 256, 512, 1024
```

Truth perturbation scales:

```text
0.15, 0.35 prior standard deviations
```

### 4.3 Replicates

Parameter recovery:

```text
6 replicates per model × horizon × truth-scale stratum
```

Model recovery:

```text
3 replicates per generating-model × horizon × truth-scale stratum
```

Frozen workload per implementation:

- parameter recovery: 144 fits;
- model recovery: 72 generated datasets, each fit by 3 candidates = 216 fits;
- total: **360 fits per implementation**.

No failed shard, replicate, candidate, or model may be dropped or replaced.

### 4.4 Deterministic generation

For parameter recovery at truth scale `s`:

```text
base_seed = 18018 + round(10000*s)
run_seed  = base_seed + 100*T + r
```

For model recovery:

```text
base_seed = 18018 + 500000 + round(10000*s)
run_seed  = base_seed + 1000000*g + 100*T + r
```

where `T` is trial horizon, `r` is the zero-based replicate index, and `g` is the zero-based generating-model index in the frozen candidate order.

Truth-vector construction:

```text
theta_true_free = prior_mu_free + s * sqrt(prior_var_free) * sin((r+1) * phase * 1.61803398875)
phase = [1, ..., n_free]
```

Inputs, responses, truth vectors, free-parameter masks, starts, and candidate identities are exported once and become immutable paired inputs for MATLAB and HGFX. Cross-language RNG identity is not assumed.

Before any paired fit is interpreted, an input manifest must contain SHA-256 checksums for every exported shard. Regenerating a shard after viewing its fit result is prohibited.

### 4.5 Fitting contract

MATLAB:

- perceptual configs: `hgf_binary_config`, `ehgf_binary_config`, `uhgf_binary_config`;
- observation config: `unitsq_sgm_config`;
- entry point: `fitModel(y, u, perceptual_config, observation_config, 'quasinewton_optim_config')`;
- default transformed start;
- no restarts or alternative starts.

HGFX:

- matching compatibility configs and validated free-parameter order;
- `fit_binary_variant` using the compatibility objective;
- `QuasiNewtonOptions(max_iter=100)`;
- identical exported `u`, `y`, model identity, fixed/free mask, and transformed start.

### 4.6 Frozen scientific criteria

The historical M18 criteria remain unchanged and are evaluated separately at each horizon:

- parameter convergence rate >= `0.80`;
- parameter median correlation >= `0.50`;
- parameter median standardized RMSE <= `1.00`;
- model-recovery balanced accuracy >= `0.50`.

No threshold can be modified after results are inspected.

### 4.7 Required recovery outputs

For parameter recovery report at minimum:

- convergence fraction;
- bias per free parameter;
- RMSE per free parameter;
- standardized RMSE per free parameter;
- correlation per free parameter and median finite correlation;
- median absolute error;
- `negLj`, `negLl`, termination, iteration, and reset diagnostics;
- available curvature/inverse-Hessian diagnostics.

For model recovery report at minimum:

- selected BIC winner for every dataset in MATLAB and HGFX;
- BIC and AIC for every candidate;
- balanced accuracy by horizon;
- row-normalized confusion matrix by horizon;
- every winner disagreement.

### 4.8 Paired integrity gate

Scientific horizon interpretation is allowed only when all conditions hold:

1. all 24 model × horizon × truth-scale shards are present;
2. all 144 parameter cases and 72 model-recovery datasets are unique and complete;
3. MATLAB and HGFX use the same free-parameter indices for every paired case;
4. MATLAB and HGFX have the same PASS/FAIL outcome for each frozen parameter criterion at every model × horizon;
5. every paired model-recovery BIC winner agrees.

A failed paired-integrity gate blocks identifiability interpretation and is classified as implementation/optimizer mismatch or insufficient reference evidence, as appropriate.

### 4.9 Preregistered horizon interpretation

For each perceptual model, define the failing set at `T=256` from criteria that fail in both implementations after the paired-integrity gate passes.

Per-model labels:

- `NO_256_FAILURE_TO_EXPLAIN`
- `DATA_HORIZON_LIMITATION_SUPPORTED`
- `PERSISTENT_WEAK_OR_STRUCTURAL_IDENTIFIABILITY_SUPPORTED`
- `MIXED_HORIZON_EFFECT_INCONCLUSIVE`

The decisive comparison is 256 → 1024 trials. Horizons 128 and 512 are trajectory diagnostics and cannot replace the preregistered comparison.

Persistent failure at 1024 may support a weak/structural-identifiability interpretation but is not proof of mathematical structural non-identifiability.

## 5. Statistical summaries and uncertainty

The paper reports point estimates together with uncertainty where a meaningful sampling unit exists.

Frozen paper-summary policy:

- proportions such as convergence fraction: Wilson 95% confidence interval;
- recovery errors, bias, median absolute error, and finite parameter correlations: nonparametric percentile bootstrap 95% interval over the frozen replicate-level sampling units;
- model-recovery balanced accuracy: stratified bootstrap 95% interval over generated datasets, preserving generating-model strata;
- bootstrap resamples: `10_000`;
- bootstrap RNG seed: `20260917`;
- all descriptive summaries retain the raw replicate values in machine-readable evidence.

Confidence intervals are descriptive uncertainty summaries and do not replace the frozen PASS/FAIL criteria.

## 6. pyhgf comparator freeze

Comparator package:

```text
pyhgf==0.3.2
```

Frozen source-distribution identity:

```text
pyhgf-0.3.2.tar.gz
SHA256 8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d
release date 2026-09-11
```

The comparator is frozen because it is current at protocol freeze time, not because its outputs are presumed equivalent to HGFX or MATLAB.

### 6.1 Required qualitative comparison

The paper must compare HGFX and pyhgf neutrally on:

- primary design objective;
- relation to the MATLAB HGF Toolbox;
- frozen behavioral compatibility vs generalized/nodalized construction;
- binary/continuous HGF support and extensibility;
- fitting/model-comparison workflow;
- differentiability and JAX integration;
- CPU/GPU execution;
- arbitrary network construction/generalized filtering;
- recovery/validation evidence;
- evidence/provenance strategy;
- packaging, PyPI availability, and documentation.

### 6.2 Semantic gate for direct empirical comparison

A direct numerical HGFX↔pyhgf comparison is permitted only if a committed semantic mapping demonstrates, before the empirical run, that both tools can execute the same intended scientific quantity with matched:

- model structure;
- update equations relevant to the compared output;
- input sequence and masking;
- parameter meaning, transforms, and fixed values;
- initial-state semantics;
- observation/response quantity;
- precision mode.

The first candidate common surface is a fixed-parameter three-level binary HGF forward trajectory / surprise calculation. This is only a candidate surface, not an assumption of equivalence.

If the semantic mapping cannot satisfy the gate without altering one implementation's intended semantics, the paper records `NOT_DIRECTLY_COMPARABLE` and does not force a numerical ranking.

No general statement that HGFX is more accurate, faster, or better than pyhgf is allowed under this protocol.

## 7. GPU and performance claim policy

### 7.1 GPU correctness/applicability

The paper may report the already frozen v1 physical-GPU applicability result in its original scope only:

- physical NVIDIA evidence exists on 2× Tesla T4;
- final-objective agreement is a correctness/applicability result;
- it is not a general speed or scaling result.

The exact historical evidence source and environment provenance must be cited from the frozen v1 evidence index rather than reconstructed from memory.

### 7.2 Performance benchmark status

Prospective paper performance benchmark: **NOT ACTIVATED IN PROTOCOL 1**.

Therefore:

- historical H100/T4 throughput measurements may appear only as clearly labeled engineering context or supplement;
- no new general speedup/scaling conclusion is drawn from them;
- no cross-tool timing ranking is performed;
- no benchmark workload may be selected after inspecting comparative timing outcomes.

If a later manuscript decision makes performance a headline contribution, create `hgfx-paper-protocol-2` (or later), freeze its exact workload matrix, warmups, repeats, timing boundaries, hardware, and comparator rules, commit it, and only then execute final performance runs.

## 8. Paper environment and provenance requirements

Every new prospective paper result must record:

- protocol ID and protocol file SHA;
- HGFX source SHA/tag;
- MATLAB reference SHA where paired;
- pyhgf version and package hash where used;
- Python version;
- NumPy version;
- JAX and JAXLIB versions;
- MATLAB version where applicable;
- OS and kernel;
- CPU model and RAM;
- GPU model/count/VRAM where used;
- NVIDIA driver and CUDA/runtime versions where used;
- device-visibility settings such as `CUDA_VISIBLE_DEVICES`;
- JAX memory settings where relevant;
- command line;
- workload/case IDs;
- seeds and exported stochastic-driver hashes;
- start/restart/optimizer settings;
- run/workflow/job ID where applicable;
- raw artifact names and SHA-256 hashes;
- whether hardware was shared or contended.

HGFX's package requirements (`numpy>=2.0`, `jax>=0.4.30`, Python >=3.11) are not sufficient reproducibility metadata. Exact resolved versions must be captured for every new paper execution environment.

## 9. Data and input checksum policy

Historical paper tables must read existing frozen machine-readable evidence directly.

Prospective recovery/comparator experiments follow a two-stage freeze:

1. this protocol freezes how inputs are generated or selected;
2. before fitting/comparison, the generated/selected inputs are written to an immutable manifest containing file paths, case IDs, dimensions, and SHA-256 checksums.

The fit/comparison stage must abort if an expected input hash does not match the manifest.

## 10. Table and figure generation policy

Final paper tables and figures must be generated by committed scripts from committed machine-readable inputs.

Required behavior:

- deterministic output from identical inputs;
- fail loudly if required evidence is absent;
- include `REFERENCE_LIMITATION_MATCH`, historical FAIL, and `NOT_DIRECTLY_COMPARABLE` rows rather than silently dropping them;
- record source SHA and input hashes in a sidecar manifest or embedded metadata;
- do not manually transcribe final numerical cells from chat, prose notes, or screenshots.

## 11. Manuscript claim rules

The manuscript must not state or imply:

- that all parameter recovery passes;
- that D02/D08 are direct scientific PASS results;
- that historical M18 was converted to PASS;
- that HGFX is the first or only Python/JAX HGF package;
- that HGFX is generally superior to pyhgf;
- that physical GPU applicability proves speedup;
- that historical shared-H100 scaling is a general performance result;
- that equivalence extends beyond the explicitly validated model/workflow scopes.

Every numerical sentence in the final manuscript must map to an evidence item in the final paper evidence manifest.

## 12. Protocol deviations

After this file is frozen, no final paper-only setting may be changed merely because of observed outcomes.

A necessary deviation must:

1. be recorded explicitly with reason;
2. preserve the original failed/partial run;
3. create a new protocol version before rerunning;
4. avoid retroactively changing the interpretation of results produced under the prior protocol.

Bug fixes that correct a demonstrated implementation error require a regression test and unchanged scientific criteria before rerun.

## 13. Final paper-evidence freeze

After all submission-used evidence is complete, a separate machine-readable paper manifest will be created and marked `FROZEN_FOR_SUBMISSION` only when:

- all reported raw inputs/results are committed or immutably referenced;
- hashes and environments are complete;
- all tables/figures regenerate from committed scripts;
- every numerical claim has an evidence mapping;
- failures, reference limitations, and non-comparable cases remain visible;
- independent review has no unresolved CRITICAL/HIGH finding.

This final paper-evidence freeze is separate from historical M19 and does not modify v1.0.0 release evidence.
