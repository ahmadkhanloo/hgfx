# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-15
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Release branch: `migration/m18-workflow-closure`

This index preserves historical failures and distinguishes direct PASS, scoped reference limitations, preflight evidence and still-open physical-GPU evidence.

## M18/v1 closure evidence

| Surface | Classification | Evidence |
|---|---|---|
| M0-M17 | PASS_IN_DOCUMENTED_SCOPES | milestone evidence |
| Historical M18 scientific experiment | FAIL_PRESERVED | historical evidence |
| D02 exact official scope | REFERENCE_LIMITATION_MATCH | decision JSON |
| D08 exact failed seed | REFERENCE_LIMITATION_MATCH | decision JSON |
| D04 uHGF -> AR1 | PASS | run `34763542557` |
| D09 sampleModel | PASS | run `34842943557` |
| D10/D11 analysis surfaces | PASS | run `34847266268` |
| D12 BPA | PASS | run `34854238549` |
| S7 paired parameter recovery | REFERENCE_LIMITATION_MATCH | run `34896442847`, artifact `10370615292` |
| S7 paired model selection | PASS_PAIRED_MODEL_SELECTION | 36/36 BIC winners match |
| S8 required repair scope | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU robustness/backend | PASS_CPU_BACKEND_EQUIVALENCE | run `34901924475`, job `104169632034`, artifact `10371308067` |
| S9 physical GPU | BLOCKED / DEFERRED | fresh current-path physical NVIDIA GPU evidence required; GPU model unconstrained |
| S10 release readiness | PASS | latest rerun `34934079865`, artifact `10383235791` |
| M19 evidence-freeze preflight | PASS_PREFLIGHT / FINAL BLOCKED BY GPU | run `34934079973`, job `104268154143` |
| M20 candidate preflight | PASS_PREFLIGHT / FINAL BLOCKED BY GPU + M19 | same run/job |

## Physical-GPU hardware policy

`M18_S9_PHYSICAL_GPU_AMENDMENT.md` was frozen before new repaired-path physical-GPU evidence. Any physical NVIDIA CUDA-capable GPU supported by JAX is eligible. The GPU model is recorded but is not itself an acceptance threshold.

Unchanged gate: actual GPU residency plus JAX CPU-vs-GPU final-objective gap `<= 1e-7`, with complete hardware/runtime/command/source provenance. CPU/mock evidence cannot substitute.

## Historical S8 diagnostic disposition

Negative-precision/raw-precheck localization workflows remain historical/manual diagnostics and do not reopen completed S8 required-scope accounting.

## Active release blockers

1. Physical NVIDIA GPU S9 revalidation.
2. M19 final evidence freeze.
3. M20 v1.0 candidate finalization.

## Integrity rules

- Historical FAIL remains FAIL.
- `REFERENCE_LIMITATION_MATCH` is scope-limited product-equivalence evidence, not scientific PASS.
- `PASS_PREFLIGHT` is not final milestone PASS.
- No post-hoc threshold/seed/dataset/start/grid/model/optimizer changes may obtain PASS.
