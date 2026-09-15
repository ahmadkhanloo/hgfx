# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-15
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Release branch: `migration/m18-workflow-closure`

This index is the release-level provenance map. It preserves historical failures and distinguishes direct PASS, scoped reference limitations, preflight evidence and still-open hardware evidence.

## Milestone baseline

- M0-M17: completed in documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.

## M18/v1 closure evidence

| Surface | Classification | Evidence |
|---|---|---|
| D02 direct fit | FAIL preserved | historical/direct gate |
| D02 exact official scope | REFERENCE_LIMITATION_MATCH | `M18_D02_REFERENCE_LIMITATION.md` + decision JSON |
| D08 prospective holdout | FAIL preserved | frozen Level-2 holdout |
| D08 exact failed seed | REFERENCE_LIMITATION_MATCH | `M18_D08_REFERENCE_LIMITATION.md` + decision JSON |
| D04 uHGF -> AR1 | PASS | run `34763542557` |
| D09 sampleModel | PASS | run `34842943557` |
| D10/D11 analysis surfaces | PASS | run `34847266268` |
| D12 BPA | PASS | run `34854238549` |
| S7 paired parameter recovery | REFERENCE_LIMITATION_MATCH | run `34896442847`, artifact `10370615292`, SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92` |
| S7 paired model selection | PASS_PAIRED_MODEL_SELECTION | 36/36 BIC winners match |
| S8 required repair scope | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU robustness/backend | PASS_CPU_BACKEND_EQUIVALENCE | run `34901924475`, job `104169632034`, artifact `10371308067`, SHA-256 `875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826` |
| S9 physical GPU | BLOCKED / DEFERRED | fresh current-path H100 evidence required |
| S10 release readiness | PASS | latest rerun on `87e3b01fdbdbe5f157ba8dc7f1309335408a165a`: run `34934079865`, artifact `10383235791`, SHA-256 `8abf4488e91c6ae28983c318670f4a92dfab57c4acc8caad494be02fca47eb2b` |
| M19 evidence-freeze preflight | PASS_PREFLIGHT / FINAL BLOCKED BY H100 | run `34934079973`, job `104268154143` |
| M20 candidate preflight | PASS_PREFLIGHT / FINAL BLOCKED BY H100 + M19 | run `34934079973`, job `104268154143` |
| M19/M20 preflight artifact | PASS | artifact `10383425031`, SHA-256 `3f711a260f68ff0454d18b2b09b3645d28ab5b370384c8729d4fd431bee5e7cf` |

## Historical S8 diagnostic disposition

The negative-precision and raw-precheck localization workflows are historical/manual diagnostics. Their invalid-region behavior is preserved. Frozen MATLAB itself can raise `Negative posterior precision` in this region, so these probes are not treated as current release regressions and do not reopen completed S8 required-scope accounting.

## Active release blockers

1. Physical H100 S9 revalidation.
2. M19 final evidence freeze.
3. M20 v1.0 candidate finalization.

## Integrity rules

- Historical FAIL remains FAIL.
- `REFERENCE_LIMITATION_MATCH` is scope-limited product-equivalence evidence, not scientific PASS.
- `PASS_PREFLIGHT` is not final milestone PASS.
- CPU evidence never substitutes for physical-GPU evidence.
- No post-hoc threshold/seed/dataset/start/grid/model/optimizer changes may obtain PASS.
