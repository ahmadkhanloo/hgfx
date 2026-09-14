# HGFX v1.0 Live TODO

Last synchronized: 2026-09-15
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

Use this file with `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, and the exact-scope limitation decision records under `reference/validation/`.

HGFX v1.0 targets scientific/functional equivalence with the frozen MATLAB toolbox, not bitwise identity. Never change thresholds, seeds, datasets, starts, validation grids, model family, or optimizer settings after seeing results to obtain PASS. Historical and prospective failures remain immutable evidence.

## Current validated baseline

- M0-M17: completed in their documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.
- D02 direct fit parity: **FAIL preserved**; exact official D02 release disposition: **REFERENCE_LIMITATION_MATCH**.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265` release disposition: **REFERENCE_LIMITATION_MATCH**.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY**.
- D04 uHGF -> AR(1): **PASS**, run `34763542557`.
- D09 official sampleModel workflow: **PASS**, run `34842943557`.
- D10/D11 analysis surfaces: **PASS**, run `34847266268`.
- D12 Bayesian parameter averaging: **PASS**, run `34854238549`.
- S7 paired recovery: **DONE / release-acceptable** under the frozen protocol. Parameter recovery is `REFERENCE_LIMITATION_MATCH`; model selection is `PASS_PAIRED_MODEL_SELECTION` (36/36 winners match). Official run `34896442847`, aggregate artifact `10370615292`, SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92`.
- S8 required-scope repair: **DONE for current S7 evidence**. Standard-HGF unclamped level-1 oracle defect repaired in `0239f52f772825e0a4fc74cdf3559cafa18a603e`; final S7 has no unresolved implementation/optimizer/model-selection mismatch.
- M18/v1 product closure: **OPEN**. PR #26 remains draft/unmerged.

## DONE — D02 exact-scope disposition

`D02_fit` is accepted for v1 only as **REFERENCE_LIMITATION_MATCH**, not direct parity or inferential PASS. Decision: `reference/validation/m18_d02_reference_limitation/decision.json`. Direct/historical failures remain visible and the classification does not generalize.

## DONE — D08 exact failed-seed disposition

The prospective Level-2 holdout remains **FAILED** as a set. Seed `271828182` passed; seed `314159265` failed inference-level requirements. For release accounting only, exact seed `314159265` in the frozen USDCHF uHGF + gaussian_obs/default-quasinewton workflow is accepted as **REFERENCE_LIMITATION_MATCH**. Decision: `reference/validation/m18_d08_reference_limitation/decision.json`.

## DONE — D09-D12 workflow/output surfaces

- [x] D09 official sampleModel / prior-predictive workflow.
- [x] D10 Corr/Sigma analysis surface.
- [x] D11 residual diagnostic surface.
- [x] D12 Bayesian parameter averaging.

## DONE — S7 paired recovery / S8 evidence-backed repair

Frozen protocol: `m18-s7-paired-recovery-1`.

Final evidence:

- complete 12-shard grid: 72 paired parameter-recovery cases and 36 paired model-recovery datasets;
- HGF/eHGF/uHGF parameter-recovery criterion outcomes match between MATLAB and HGFX;
- those shared parameter-recovery failures are accepted as **REFERENCE_LIMITATION_MATCH** in this exact grid, not scientific PASS;
- all 36 BIC winners match; balanced accuracy is `0.5833333333333334` in both implementations;
- no unresolved current-head implementation, optimizer or model-selection mismatch remains from S7;
- decision: `reference/validation/m18_s7_reference_limitation/decision.json` and `docs/validation/M18_S7_REFERENCE_LIMITATION.md`.

Historical pre-repair mismatch evidence remains preserved. The HGF semantic defect was repaired rather than hidden or tolerated.

## NOW — S9 robustness/backend closure

Freeze and execute the required robustness/backend applicability matrix without reusing scientific recovery thresholds as a way to obtain PASS. Required work:

- robustness across required trial horizons/regimes, missing/ignored trials, and initialization perturbations;
- compatibility-vs-JAX CPU agreement on supported product paths;
- CPU-vs-physical-GPU agreement where the same validated code/data path is supported;
- reuse prior H100 evidence only when unchanged code/data-path applicability is explicitly demonstrated; otherwise obtain new physical-GPU evidence;
- record hardware/runtime/command/commit/evidence and leave unsupported or untested cells OPEN rather than inferring coverage.

## After S9

- [ ] S10: aggregate evidence checker/provenance index, clean install, examples, docs/API/licenses, zero MATLAB runtime dependency.
- [ ] M19 — Methods Paper Dataset Frozen.
- [ ] M20 — v1.0 Candidate only after release gate passes.

## Status vocabulary

Use only evidence-backed **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**.
