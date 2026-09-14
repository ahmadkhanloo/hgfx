# HGFX v1.0 Live TODO

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

Use this file with `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, `../validation/M18_D02_REFERENCE_LIMITATION.md`, and `../validation/M18_D08_REFERENCE_LIMITATION.md`.

HGFX v1.0 targets scientific/functional equivalence with the frozen MATLAB toolbox, not bitwise identity. Never change thresholds, seeds, datasets, starts, validation grids, model family, or optimizer settings after seeing results to obtain PASS. Historical and prospective failures remain immutable evidence.

## Current validated baseline

- M0-M17: completed in their documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.
- D02 direct fit parity: **FAIL preserved**; exact official D02 release disposition: **REFERENCE_LIMITATION_MATCH**.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265` release disposition: **REFERENCE_LIMITATION_MATCH**.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY**.
- D04 uHGF -> AR(1): **PASS**, run `34763542557`.
- Exact historical 512-trial case: **REFERENCE_LIMITATION_MATCH** in that exact paired scope.
- D09 official sampleModel workflow: **PASS**, run `34842943557`, artifact `10346184455`, SHA-256 `6c754cc02ce621c66d67224884c5347c61468cdfb6f3de81dffb03898d02b85c`.
- D10/D11 analysis surfaces: **PASS**, run `34847266268`, artifact `10348099156`, SHA-256 `a69045cc4e1ad388c64dec7235f8c9d2ad42f6885c6210d31b979d2284b48317`.
- D12 Bayesian parameter averaging: **PASS**, run `34854238549`, job `104009543024`, artifact `10352486569`, SHA-256 `14ab041b2473a13496377f63d6d1897578d1785128406eadbc1d6d44ae119883`.
- M18/v1 product closure: **OPEN**. PR #26 remains draft/unmerged.

## DONE — D02 exact-scope disposition

`D02_fit` is accepted for v1 only as **REFERENCE_LIMITATION_MATCH**, not direct parity or inferential PASS. Decision: `reference/validation/m18_d02_reference_limitation/decision.json`. Direct/historical failures remain visible and the classification does not generalize.

## DONE — D08 exact failed-seed disposition

The prospective Level-2 holdout remains **FAILED** as a set. Seed `271828182` passed; seed `314159265` failed inference-level requirements. That failed protocol is immutable.

For release accounting only, exact seed `314159265` in the frozen USDCHF uHGF + gaussian_obs/default-quasinewton workflow is accepted as **REFERENCE_LIMITATION_MATCH**.

Evidence chain:

- repaired-product holdout run `34842943696`, job `103971934494`, artifact `10347616859`, SHA-256 `8cbb16de519204710662d8bf0b94c2510df8c2e53f9427897b9f55d7d0b499f1`: holdout remains FAIL, exact MATLAB-endpoint replay has no mismatch;
- optimizer localization run `34842943657`, job `103971934637`, artifact `10347682339`, SHA-256 `3d94f74c71e5bf6bcdd8971d647ddba31f5a087cb4f3cb9a933c6a6e3c33518a`: `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- source-likelihood run `34842943607`, artifact `10346549885`, SHA-256 `4e763e9978cb409eca5c7b468d5798b3a832aa023e382731284b9af47fb61275`: selected observation inputs/output likelihood/reduction exact after the evidence-linked prior repair;
- MATLAB failed-seed self-sensitivity run `34846375826`, job `103983208684`, artifact `10348900752`, SHA-256 `42874a324ef408205452516f0abe7497b60d5f12b9f9bf2972df105845f907f6`: baseline endpoint exact; 13/14 independent one-local-spacing start perturbations leave the unchanged endpoint gate.

Decision: `reference/validation/m18_d08_reference_limitation/decision.json`.

Do not relabel the failed Level-2 holdout as PASS, widen its tolerances, replace seed `314159265`, or generalize this exact-case limitation.

## DONE — remaining D09-D12 workflow/output surfaces

- [x] D09 official sampleModel / prior-predictive workflow.
- [x] D10 Corr/Sigma analysis surface.
- [x] D11 residual diagnostic surface.
- [x] D12 Bayesian parameter averaging, including scalar-vs-singleton MATLAB prior-vector compatibility regression.

## NOW — S7 paired MATLAB/HGFX recovery

The next unresolved product gate is paired recovery against the same oracle. The old historical M18 scientific FAIL is preserved and is not sufficient as product-equivalence evidence.

Freeze a new paired protocol **before execution** with:

- models: `hgf_binary`, `ehgf_binary`, `uhgf_binary`;
- trial counts: `128`, `256`;
- truth perturbations: `0.15`, `0.35` prior SD;
- parameter-recovery replicates: 6 per stratum, matching the original frozen gate grid;
- model-recovery replicates: 3 per stratum;
- same simulated inputs/responses/truth vectors across MATLAB and HGFX using exported deterministic drivers/data rather than assuming RNG identity;
- same perceptual/observation model configs, free/fixed parameter ordering, priors, transformed/native semantics, starts and default quasinewton workflow;
- same candidate set and BIC winner rule for model recovery; AIC retained as diagnostic;
- all failures/raw fits preserved.

Expected original-grid workload: 72 parameter-recovery fits plus 108 candidate fits for model recovery = 180 fits. Use sharding for execution efficiency, **not grid reduction**.

Issue #21 / M18C.2 remains a separate preregistered 128/256/512/1024 horizon extension and must not retroactively alter the original S7 grid.

## After S7

- [ ] S8: repair only demonstrated required-scope HGFX-only implementation/optimizer/model-selection mismatches, regression first.
- [ ] S9: robustness matrix and CPU/JAX/physical-GPU applicability closure.
- [ ] S10: aggregate evidence checker/provenance index, clean install, examples, docs/API/licenses, zero MATLAB runtime dependency.
- [ ] M19 — Methods Paper Dataset Frozen.
- [ ] M20 — v1.0 Candidate only after release gate passes.

## Status vocabulary

Use only evidence-backed **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**.
