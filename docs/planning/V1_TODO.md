# HGFX v1.0 Live TODO

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

Use this file with `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, and `../validation/M18_D02_REFERENCE_LIMITATION.md`.

HGFX v1.0 targets scientific/functional equivalence with the frozen MATLAB toolbox, not bitwise identity. Never change thresholds, seeds, datasets, starts, validation grids, model family, or optimizer settings after seeing results to obtain PASS. Historical failures remain immutable evidence.

## Current validated baseline

- M0-M17: completed in their documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.
- D02 direct fit parity: **FAIL preserved**; exact official D02 release disposition: **REFERENCE_LIMITATION_MATCH**.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY**.
- D04 uHGF -> AR(1): **PASS**, run `34763542557`.
- Exact historical 512-trial case: **REFERENCE_LIMITATION_MATCH** in that exact paired scope.
- Official fit/Bayes direct gate remains **7/9 direct PASS**; direct failures are D02_fit and D08_fit.
- D02 is no longer an unresolved HGFX-only release blocker in its exact official scope; D08 remains the active fit-workflow blocker.
- M18/v1 product closure: **OPEN**. PR #26 remains draft/unmerged.

## DONE — D02 exact-scope disposition

`D02_fit` is accepted for v1 only as **REFERENCE_LIMITATION_MATCH**, not direct parity or inferential PASS.

Evidence chain:

- cross-endpoint basin run `34829122057`, job `103928016949`, artifact `10342907205`, SHA-256 `ee53fe25cd12ff8f6d47b3172218bec92cb881a6017c6d7f170b4925a561284d`: `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`, all 9 shared-vector objective points pass;
- optimizer-source run `34835728961`, job `103948983708`, artifact `10344290559`, SHA-256 `2ceb51c72898d6f61314313f877f810503613b0a45c555b235916564d0a36126`: source objective exact; first off-centre residual `2.842170943040401e-14`, log-likelihood only; MATLAB-sample Ridders replay exact;
- source-likelihood run `34836421105`, job `103951170207`, artifact `10344591868`, SHA-256 `90bbda77cfe88d3d9f79c64c06b61d738f6df2e5d34691296edfdcc4c33f86bb`: inference states exact; trial-likelihood differences <= `8.881784197001252e-16`; MATLAB vector-vs-scalar reduction differs by `1.1368683772161603e-13`;
- MATLAB self-sensitivity run `34837033370`, job `103953084600`, artifact `10344991786`, SHA-256 `9bb57f50b05d0fd2e6fb33badd265fec817c8c2308036d51d92e4f24a6e5e4ec`: `MATLAB_START_ULP_BASIN_SENSITIVE`; baseline replay exact and all 6 independent +/- one-spacing starts (`4.440892098500626e-16`) leave the existing endpoint gate, with shifts up to about `1.5077`.

Decision: `reference/validation/m18_d02_reference_limitation/decision.json`.

Do not erase the direct D02 FAIL or generalize this exact-case limitation to other seeds/regimes.

## NOW — D08 failed prospective holdout

### D08_fit — BLOCKED

The prospective Level-2 endpoint-sensitivity experiment remains **FAILED** under its frozen rules. Seed `271828182` passed; seed `314159265` failed inference-level requirements. The failed protocol remains immutable.

Additional localization now established:

- failed-holdout optimizer diagnostic `34829121895`, job `103928015484`, artifact `10343726427`, SHA-256 `d55f08120dd079717b7ff082566108bc7f91fbab9fa334b99656fec1faa07d63`: `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- placeholder/prior repair is independently validated: run `34836421030`, job `103951169992`, artifact `10343484736`, SHA-256 `8e0028dbad33a007246e41bcf29bb54e91820b259ae9338641aa28412317c480`, classification `NO_PRIOR_DIVERGENCE` with exact parameters/means/variances/prior terms;
- despite that repair, the frozen hard holdout seed still fails, so prior preparation was real but not the complete cause.

Next:

- [ ] Establish whether the frozen MATLAB reference itself is materially optimizer/basin-sensitive for failing seed `314159265`, using a preregistered reference-only perturbation diagnostic; diagnostic evidence cannot rewrite the failed Level-2 holdout.
- [ ] If MATLAB reference sensitivity is established, compare the failure mechanism against HGFX under the reference-limitations policy before any classification.
- [ ] If not established, continue localization of the first path-sensitive numerical primitive/state without widening tolerance.
- [ ] Keep D08 BLOCKED until a release-acceptable classification is evidence-backed.

## Official workflow closure exit gate

- [ ] D01/D03/D05/D06/D07 remain healthy on affected code paths.
- [x] D02 has a release-acceptable exact-scope disposition: `REFERENCE_LIMITATION_MATCH`; direct FAIL preserved.
- [ ] D08 reaches a release-acceptable outcome; failed prospective Level-2 holdout remains visible.
- [ ] All accepted non-direct outcomes have immutable evidence.
- [ ] PR #26 reviewed only after evidence closure.

## NEXT — remaining v1 work

- [ ] D09 prior-predictive sampling demo wrapper and remaining source-to-workflow mapping.
- [ ] D10 Corr/Sigma/plot surface.
- [ ] D11 residual diagnostic workflow/output parity.
- [ ] D12 Bayesian parameter averaging workflow parity.
- [ ] Paired MATLAB/HGFX parameter recovery under frozen product protocol.
- [ ] Paired model recovery under frozen candidate set/selection rule.
- [ ] Repair only demonstrated HGFX-only required-scope mismatches, regression first.
- [ ] Robustness matrix and CPU/JAX/physical-GPU applicability closure.
- [ ] Aggregate evidence checker/provenance index, clean install, examples, docs/API/licenses, zero MATLAB runtime dependency.
- [ ] M19 — Methods Paper Dataset Frozen.
- [ ] M20 — v1.0 Candidate only after release gate passes.

## Status vocabulary

Use only evidence-backed **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**.
