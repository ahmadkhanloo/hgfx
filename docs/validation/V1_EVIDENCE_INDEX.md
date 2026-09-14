# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-15
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Release branch: `migration/m18-workflow-closure`

This index is the release-level provenance map. It does not rewrite historical evidence; it points to the authoritative records used by the v1 gate.

## Milestone baseline

- M0-M17: completed in their documented scopes; see planning/milestone documents and milestone-specific validation records.
- Historical M18 scientific experiment: **FAIL, preserved**.

## M18/v1 closure evidence

| Surface | Classification | Evidence |
|---|---|---|
| D02 direct fit | FAIL preserved | historical/direct gate |
| D02 exact official scope | REFERENCE_LIMITATION_MATCH | `M18_D02_REFERENCE_LIMITATION.md` + decision JSON |
| D08 prospective holdout | FAIL preserved | frozen Level-2 holdout |
| D08 exact failed seed | REFERENCE_LIMITATION_MATCH | `M18_D08_REFERENCE_LIMITATION.md` + decision JSON |
| D04 uHGF -> AR1 | PASS | workflow run `34763542557` |
| D09 sampleModel | PASS | workflow run `34842943557` |
| D10/D11 analysis surfaces | PASS | workflow run `34847266268` |
| D12 BPA | PASS | workflow run `34854238549` |
| S7 paired parameter recovery | REFERENCE_LIMITATION_MATCH | run `34896442847`, artifact `10370615292`, SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92` |
| S7 paired model selection | PASS_PAIRED_MODEL_SELECTION | 36/36 BIC winners match |
| S8 required repair scope | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU robustness/backend | PASS_CPU_BACKEND_EQUIVALENCE | run `34901924475`, job `104169632034`, artifact `10371308067`, SHA-256 `875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826` |
| S9 physical GPU | BLOCKED | current numerical path requires fresh H100 revalidation |

## Active release blockers

1. Physical H100 S9 revalidation on the repaired standard-HGF fast path.
2. S10 clean-wheel/install/example/docs/licenses/zero-MATLAB-runtime CI must pass on the closure branch.
3. After the above: M19 evidence freeze and M20 v1.0 candidate gate.

## Integrity rules

- A historical FAIL remains FAIL.
- `REFERENCE_LIMITATION_MATCH` is scope-limited product-equivalence evidence, not a scientific PASS.
- CPU evidence never substitutes for physical-GPU evidence.
- No post-hoc threshold/seed/dataset/start/grid/model/optimizer changes may obtain PASS.
