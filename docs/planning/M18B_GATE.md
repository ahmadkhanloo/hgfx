# M18B — Recovery Protocol Redesign / Identifiability-Aware Validation

Status: **PASS — CORRECTED EVIDENCE-INTEGRITY GATE VALIDATED**

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

- `low_error_recovery`
- `finite_data_likelihood_identifiability`
- `cross_parameter_confounding`
- `optimizer_start_sensitivity`
- `mixed_or_weak_identifiability`

Classification is descriptive and never exempts failed observations.
`low_error_recovery` does not establish likelihood concentration or joint
identifiability. Conditional slices hold other parameters at truth. Undefined
boundary curvature is recorded explicitly as null.

## Gate criteria

M18B PASS means that the redesigned protocol itself is complete and scientifically
interpretable. The gate requires:

1. exact model × parameter × trial-count × replicate coverage and consistent unique dataset seeds;
2. valid finite required metrics in every raw record, and a summary recomputed from those records;
3. absolute median truth-start objective improvement <= 0.10, confirming optimizer
   sensitivity is not the dominant global mechanism;
4. the known healthy control `om[1]` has median recovery error <= 0.50 prior SD at the
   highest trial count for all three models;
5. frozen M18 thresholds and FAIL evidence remain unchanged.

M18B PASS **does not imply M18 PASS**.

## Historical pre-repair gate evidence

The first M18B implementation executed successfully on branch
`feat/m18b-identifiability-aware-validation` and produced a green gate, but the gate could
trust caller-supplied summary values without validating raw records. That historical green
run is retained as provenance, not accepted as final corrected evidence.

- historical commit: `db4662dc459de67124ab08e91082a4f362758f08`;
- historical run: `34411993098`;
- historical artifact: `10127986651`;
- historical artifact SHA-256: `239433f7951635f33543912d04fa812c1a18620884590acc390e6cbb2f429605`.

## Corrected evidence-integrity gate — PASS

The corrected implementation was validated on PR #20 (`Fix M18B false-positive validation
and archive auditable evidence`). It recomputes gate decisions from raw records, verifies
exact coverage and seeds, validates finite required fields, freezes original M18 FAIL
evidence, records auditable diagnostic profiles, checkpoints execution, and prevents a
partial/smoke run from claiming final PASS.

Validated evidence:

- repair head: `e5b55b61d4f114b429e17c49eb8deb0e053214a6`;
- PR #20 merged; merge commit: `78fd894785292cd33c408a45921d31e7fda82dfb`;
- workflow: `M18B Identifiability-Aware Validation`;
- workflow run: `34497399365`;
- job: `102939240184`;
- frozen reference guard: PASS, HGF Toolbox 8.2.0 commit
  `2437f4dc241541072722a2695ddeca7b44d83dd3`, 334 MATLAB files;
- corrected M18B unit tests: **39 passed**;
- full regression: **136 passed, 4 skipped**;
- all four skips are physical-GPU-only M14–M17 tests because the hosted runner exposes no
  qualifying physical GPU; physical H100 evidence remains archived in those milestones;
- full gate grid: 27 datasets = 3 models × 3 trial counts × 3 replicates;
- final gate result: **PASS**, `gate_pass=true`, `failures=0`;
- artifact: `m18b-identifiability-validation`, ID `10160948325`;
- artifact SHA-256: `5a997b3be06f12420a52086f42656ecd14ff132892d42bb69c20419de234f182`.

The corrected M18B protocol-integrity repair is therefore closed.

## 512-trial numerical-horizon classification

A 512-trial extension had previously exposed an unstable initial HGF recovery point. This
case has now been compared directly with frozen MATLAB HGF Toolbox 8.2.0 rather than being
assumed to be an HGFX defect.

Frozen case:

- `hgf_binary + unitsq_sgm`;
- 512 trials;
- truth scale 0.35 prior SD;
- replicate 0;
- cell seed `233100`;
- response seed `233101`.

Evidence:

- workflow: `M18 512 MATLAB Reference Classification`;
- run: `34683977567`;
- HGFX head: `3a272c545ca2366deb57a0c9c0dbb2cf01ad0108`;
- artifact: `m18-512-matlab-reference-evidence`, ID `10295261423`;
- artifact SHA-256: `8a538a1bc8cae206e1014b72a4de8495d9951ad2934845db1704d83ee743092c`;
- classification: **`REFERENCE_LIMITATION_MATCH`**.

On identical inputs/responses/configuration, truth-parameter forward execution succeeds in
both MATLAB and HGFX. Default-parameter forward execution fails in both with the same
variational-approximation-invalid condition. MATLAB reports
`tapas:hgf:VarApproxInvalid`; HGFX raises the corresponding validation error. Both initial
objectives return the realmax failure sentinel and `rval=-1`, so fitting is not entered in
either implementation. No MATLAB-vs-HGFX mismatch was observed.

This is acceptable for MATLAB-equivalence v1.0 as a documented matched reference
limitation. It is **not** a scientific PASS and does not establish arbitrary 512-trial
support.

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

M18B is now **PASS** as a corrected, auditable identifiability-aware validation protocol.
The original M18 scientific-validation result remains **FAIL** and is preserved unchanged;
M18B does not retroactively weaken or replace that evidence.

The historical 512-trial case is resolved as `REFERENCE_LIMITATION_MATCH`, not an
HGFX-specific implementation defect.

Remaining v1 MATLAB-equivalence work is separate:

1. reference-aware model-family/model-selection validation across required scientific
   workflows;
2. MATLAB demo/workflow reproduction in Python;
3. closure of any remaining `IMPLEMENTATION_MISMATCH`, `MODEL_SELECTION_MISMATCH`, or
   `INSUFFICIENT_REFERENCE_EVIDENCE` cases.
