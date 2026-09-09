# M18B — Recovery Protocol Redesign / Identifiability-Aware Validation

Status: **IMPLEMENTED — CI GATE PENDING**

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

- strong recovery for the first perceptual volatility parameter om[1];
- finite-data likelihood identifiability limitations for om[2], especially HGF/uHGF;
- perceptual/observation confounding for logze, especially uHGF;
- negligible benefit from truth-start optimization in most cells.

A scientifically valid recovery benchmark must therefore distinguish estimator recovery,
likelihood identifiability as trial count increases, parameter confounding, and optimizer
start-point sensitivity.

## Final gate grid

- models: hgf_binary, ehgf_binary, uhgf_binary;
- trial counts: 128, 256, 512;
- truth perturbation: 0.35 prior SD;
- replicates: 3 per model/trial cell;
- profile points: 31;
- optimizer maximum iterations: 100.

The 0.15-SD regime from frozen M18 is not used as the M18B primary identifiability
experiment because its deliberately small generating spread makes correlation and
empirical-spread standardized RMSE unstable as identifiability metrics. The original
M18 result remains archived unchanged.

## Per-dataset evidence

For each free parameter M18B records baseline MAP error, truth-start error,
single-parameter oracle error, perceptual-only oracle error where applicable,
likelihood/joint profile displacement, profile span and curvature, optimizer
termination, and a dominant diagnostic mechanism.

## Mechanism classes

- identifiable_recovery
- finite_data_likelihood_identifiability
- cross_parameter_confounding
- optimizer_start_sensitivity
- mixed_or_weak_identifiability

Classification is diagnostic and never exempts failed observations.

## Gate criteria

M18B PASS means that the redesigned protocol itself is complete and scientifically
interpretable. It requires:

1. complete model × parameter × trial-count coverage;
2. finite profile diagnostics for every group;
3. absolute median truth-start objective improvement <= 0.10, confirming optimizer
   sensitivity is not the dominant global mechanism;
4. the known healthy control om[1] has median recovery error <= 0.50 prior SD at the
   highest trial count for all three models;
5. frozen M18 thresholds and FAIL evidence remain unchanged.

M18B PASS does not imply M18 PASS.

## Commands

CI/smoke:

    python scripts/run_m18b_identifiability_validation.py --preset ci

Final gate:

    python scripts/run_m18b_identifiability_validation.py --preset gate \
      --output benchmarks/results/m18b_identifiability_validation.json

## Completion condition

M18B can be closed only when unit tests pass, the final --preset gate run exits
successfully, the JSON result is archived as a CI artifact, and full regression
remains green.

Until then the correct status is:

**IMPLEMENTED / CI GATE NOT EXECUTED**
