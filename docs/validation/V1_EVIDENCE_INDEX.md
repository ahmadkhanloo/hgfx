# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-15
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Release branch: `migration/m18-workflow-closure`

This index preserves historical failures and distinguishes direct PASS, scoped reference limitations, preflight evidence, physical-GPU applicability, and final release gates.

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
| S9 physical GPU | PASS_PHYSICAL_GPU_APPLICABILITY | source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`; 2x Tesla T4; repository record `7179484ce782c25d6edde34cc56a0d689831e1cc`; raw JSON SHA-256 `6cd35c82be1e542830c06f6b7b7e444fda0ff4fe93773f080e6c13725212dfdf` |
| S10 release readiness | PASS | latest rerun `34934079865`, artifact `10383235791` |
| M19 evidence-freeze preflight | PASS_PREFLIGHT / READY_TO_FINALIZE | run `34934079973`, job `104268154143` |
| M20 candidate preflight | PASS_PREFLIGHT / BLOCKED BY M19 | same run/job |

## Physical-GPU result

`M18_S9_PHYSICAL_GPU_AMENDMENT.md` was frozen before this repaired-path physical run. The eligible hardware policy permits any physical NVIDIA CUDA-capable GPU supported by JAX; the GPU model is recorded but is not itself an acceptance threshold.

The uploaded evidence satisfies the unchanged S9 gate: JAX backend `gpu`, actual device residency, four required CPU-vs-GPU fitting cells passing the `<= 1e-7` final-objective criterion, and complete source/hardware/runtime/command/environment provenance. Maximum observed CPU-vs-GPU final-objective gap is `1.4210854715202004e-14`.

The run used 2x Tesla T4 under a hosted/shared Kaggle environment. This establishes numerical backend applicability for the tested NVIDIA/JAX/CUDA path; it does not establish uncontended performance/scaling or H100-specific performance.

The wrapper-created `gpu_validation_results/` directory appears as untracked in the captured git status because the wrapper creates the output directory before recording provenance. The recorded source HEAD is exactly `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`; no numerical source modification is indicated by that status entry.

## Historical S8 diagnostic disposition

Negative-precision/raw-precheck localization workflows remain historical/manual diagnostics and do not reopen completed S8 required-scope accounting.

## Active release blockers

1. M19 final evidence freeze.
2. M20 v1.0 candidate finalization.

## Integrity rules

- Historical FAIL remains FAIL.
- `REFERENCE_LIMITATION_MATCH` is scope-limited product-equivalence evidence, not scientific PASS.
- `PASS_PREFLIGHT` is not final milestone PASS.
- No post-hoc threshold/seed/dataset/start/grid/model/optimizer changes may obtain PASS.
