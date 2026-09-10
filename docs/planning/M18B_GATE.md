# M18B — Recovery Protocol Redesign / Identifiability-Aware Validation

Status: **PASS — IMPLEMENTED, GATE EXECUTED, MERGED**

Parent: M18 Scientific Validation  
Predecessor: M18A Parameter Recovery Diagnosis

## Purpose

M18B redesigns the recovery-validation protocol after M18A showed that the original M18
parameter-recovery failure was heterogeneous and was not primarily caused by an optimizer
or implementation defect.

The redesign preserves the original M18 result and thresholds. M18B is a new validation
milestone, not a retroactive redefinition of M18.

## Scientific rationale

M18A established:

- strong recovery for the first perceptual volatility parameter `om[1]`;
- finite-data likelihood identifiability limitations for `om[2]`, especially HGF/uHGF;
- perceptual/observation confounding for `logze`, especially uHGF;
- negligible benefit from truth-start optimization in most cells.

A scientifically valid recovery benchmark must therefore distinguish estimator recovery,
likelihood identifiability as trial count increases, parameter confounding, and optimizer
start-point sensitivity. M18B also uses deterministic balanced binary stimuli with bounded
run length so that the benchmark measures parameter recoverability rather than accidental
pathological stimulus sequences.

## Final gate grid

- models: `hgf_binary`, `ehgf_binary`, `uhgf_binary`;
- trial counts: 64, 128, 256;
- truth perturbation: 0.35 prior SD;
- replicates: 3 per model/trial cell;
- profile points: 31;
- optimizer maximum iterations: 100.

A 512-trial extension was explicitly attempted during CI and exposed numerical overflow
in the current compatibility forward path before fitting could begin. It is therefore
recorded as a separate numerical-horizon limitation rather than misclassified as a
parameter-identifiability result. M18B remains within the validated 64–256 trial range.

The 0.15-SD regime from frozen M18 is not used as the M18B primary identifiability
experiment because its deliberately small generating spread makes correlation and
empirical-spread standardized RMSE unstable as identifiability metrics. The original
M18 result remains archived unchanged.

## Per-dataset evidence

For each free parameter M18B records:

- baseline MAP recovery error in prior-SD units;
- truth-start recovery error;
- single-parameter oracle recovery error;
- perceptual-only oracle recovery error where applicable;
- likelihood-profile minimum offset from truth;
- joint-profile minimum offset from truth;
- likelihood span and curvature;
- objective improvement from truth-start initialization;
- optimizer termination;
- dominant diagnostic mechanism.

## Mechanism classes

- `identifiable_recovery`
- `finite_data_likelihood_identifiability`
- `cross_parameter_confounding`
- `optimizer_start_sensitivity`
- `mixed_or_weak_identifiability`

Classification is diagnostic and never exempts failed observations.

## Gate criteria

M18B PASS means that the redesigned protocol itself is complete and scientifically
interpretable. The gate requires:

1. complete model × parameter × trial-count coverage;
2. finite profile diagnostics for every group;
3. absolute median truth-start objective improvement <= 0.10, confirming optimizer
   sensitivity is not the dominant global mechanism;
4. the known healthy control `om[1]` has median recovery error <= 0.50 prior SD at the
   highest trial count for all three models;
5. frozen M18 thresholds and FAIL evidence remain unchanged.

M18B PASS **does not imply M18 PASS**.

## Executed gate evidence

Final validated head before merge:

- branch: `feat/m18b-identifiability-aware-validation`;
- commit: `db4662dc459de67124ab08e91082a4f362758f08`;
- GitHub Actions workflow: `M18B Identifiability-Aware Validation`;
- workflow run ID: `34411993098`;
- workflow run number: 16;
- final gate: **PASS**;
- output groups: 27 = 3 models × 3 parameters × 3 trial-count strata;
- artifact: `m18b-identifiability-validation`, artifact ID `10127986651`;
- artifact SHA256: `239433f7951635f33543912d04fa812c1a18620884590acc390e6cbb2f429605`;
- M18B unit tests: **4 passed**;
- full regression: **101 passed, 4 skipped**;
- skipped tests are physical-GPU-only M14–M17 tests because the hosted runner exposes no
  real JAX GPU; their physical GPU evidence remains archived in the earlier milestones;
- frozen reference guard: **PASS**, HGF Toolbox commit
  `2437f4dc241541072722a2695ddeca7b44d83dd3`.

The validated PR was merged as:

- PR: #19;
- merge commit: `9ebf00e0c892cdf661ead5d072ec04e5824c1698`.

## Numerical-horizon observation

The attempted 512-trial extension produced overflow warnings in the compatibility
forward/numerical differentiation path and eventually an unstable initial recovery point
for HGF. This is not treated as a parameter-recovery failure because the fit never entered
a valid comparable estimation regime. It should be tracked separately as a future
long-sequence numerical-stability milestone.

The successful 64–256 gate still emitted isolated overflow warnings from Ridders
extrapolation / HGF exponentiation, but all required diagnostics completed, all M18B gate
checks passed, and the full regression suite remained green. These warnings should remain
visible as numerical-stability evidence rather than being suppressed.

## Commands

CI/smoke:

```bash
python scripts/run_m18b_identifiability_validation.py --preset ci
```

Final gate:

```bash
python scripts/run_m18b_identifiability_validation.py \
  --preset gate \
  --output benchmarks/results/m18b_identifiability_validation.json
```

## Conclusion

M18B is **PASS / CLOSED**.

The milestone demonstrates that HGFX now has an identifiability-aware recovery-validation
protocol that separates recoverability, finite-data likelihood identifiability, parameter
confounding, and optimizer sensitivity without weakening or rewriting the frozen M18
acceptance criteria.

The original M18 scientific-validation result remains **FAIL** and must remain preserved as
historical evidence. Any future attempt to close the parent M18 milestone must address the
scientific meaning of the original recovery thresholds rather than retroactively replacing
them with M18B criteria.
