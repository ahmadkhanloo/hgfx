# Research Log

This log records paper-relevant scientific and engineering decisions. It is not a substitute for raw gate evidence. Historical failures are never rewritten.

## 2026-09-14 — D02 exact official workflow classified as REFERENCE_LIMITATION_MATCH

- **Question:** Is D02's material fitted-inference divergence an HGFX-only optimizer defect, or a numerical-basin limitation present in the frozen MATLAB reference itself?
- **Shared-state evidence:** corrected basin run `34829122057` passes all nine preregistered same-vector objectives; exact MATLAB endpoint replay and sampled MATLAB-path objectives pass; exact-state QN transition algebra agrees at machine level.
- **Source localization:** run `34835728961` has an exact source objective and localizes the first off-centre sample difference to `2.842170943040401e-14` in log-likelihood only; MATLAB-sample Ridders replay is exact. Run `34836421105` has exact inference states and trial-likelihood differences no larger than `8.881784197001252e-16`; MATLAB vector `sum` differs from its scalar-loop reduction by `1.1368683772161603e-13` on the frozen sample.
- **Frozen reference sensitivity test:** protocol `m18-d02-matlab-self-sensitivity-1`, run `34837033370`, job `103953084600`, artifact `10344991786`, SHA-256 `9bb57f50b05d0fd2e6fb33badd265fec817c8c2308036d51d92e4f24a6e5e4ec`.
- **Observed:** baseline replay reproduces the official MATLAB endpoint exactly. Each of six independent changes of one free starting coordinate by only `+/-eps(x)` (`4.440892098500626e-16`) terminates outside the existing endpoint gate; the largest observed free-parameter shift is about `1.5077`.
- **Decision:** preserve the direct D02 FAIL and historical `INFERENCE_EQUIVALENCE_FAIL`, but classify the exact official D02 workflow as `REFERENCE_LIMITATION_MATCH` for release accounting. This is not `PASS_INFERENTIAL_EQUIVALENCE` and cannot be generalized to other cases.
- **Scientific implication:** in this exact finite-difference quasi-Newton workflow, binary64-scale perturbations can select materially different basins in the MATLAB oracle itself. Chasing platform-specific ULP differences in `pow`/reduction is therefore not a sound product acceptance strategy once shared semantics have been established.

## 2026-09-14 — D08 prior semantics repaired but failed holdout remains

- The USDCHF placeholder variance/prior-input discrepancy was repaired and validated exactly.
- Run `34836421030`, job `103951169992`, artifact `10343484736`, SHA-256 `8e0028dbad33a007246e41bcf29bb54e91820b259ae9338641aa28412317c480`: `NO_PRIOR_DIVERGENCE`; parameters, means, variances, prior terms and totals are exact.
- The prospectively frozen hard holdout seed `314159265` still fails after the repair; therefore the prior mismatch was real but not the complete D08 cause.
- Failed-holdout optimizer diagnostic `34829121895` classifies `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`; D08 remains BLOCKED.

## 2026-09-14 — D08 prospective endpoint-sensitivity hypothesis did not generalize

- **Question:** Can D08's original direct-gate failure be accepted as a numerically immaterial endpoint-sensitivity effect under a prospectively frozen Level-2 rule?
- **Pre-registered evidence:** `matlab-equivalence-policy-1`; holdout seeds `271828182` and `314159265`; unchanged official USDCHF data, uHGF + gaussian_obs model/config, quasinewton optimizer and existing field tolerances.
- **Run:** `34826235671`, job `103918945542`, artifact `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1`.
- **Observed:** seed `271828182` passed; seed `314159265` failed inference-level requirements. Exact MATLAB-endpoint replay still had no mismatch.
- **Decision:** preserve the failed prospective experiment. D08 remains BLOCKED. Do not replace the failing seed, broaden tolerance, or reinterpret the frozen Level-2 protocol.

## 2026-09-14 — tiered equivalence replaces decimal-place thinking, not frozen evidence

- **Decision:** use exact contract, scale-aware numerical equivalence, prospectively validated endpoint-sensitivity equivalence, separately preregistered inferential equivalence, and exact paired reference-limit classifications. Decimal-place-only rules are rejected.
- **Integrity:** old direct failures remain failures; new protocols must be frozen before validation data are observed; FAIL outcomes are preserved equally with PASS outcomes.
- **Policy commit:** `3bea320ac6e9f0f7cef26e63ac18e50c422a834a`.

## 2026-09-13 — v1 paper objective aligned to MATLAB-equivalent product objective

HGFX v1/paper primarily targets a validated Python replacement for frozen MATLAB HGF Toolbox 8.2.0. GPU/differentiability/performance are secondary claims conditional on scientific behavior. Frozen reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## 2026-09-13 — historical M18 FAIL remains visible

M18B protocol evidence does not retroactively convert the historical M18 recovery experiment into PASS. Final product-level recovery requires paired MATLAB/HGFX evidence under a frozen protocol.

## 2026-09-13 — reference limitations may be matched, not silently repaired

`REFERENCE_LIMITATION_MATCH` is permitted only for exact paired MATLAB limitations with no earlier HGFX-only semantic divergence. Official MATLAB model-family choices should be mirrored rather than silently substituting another model.

## 2026-09-13 — physical GPU evidence required for GPU claims

CPU/mock execution cannot support GPU validation claims. Record physical hardware, runtime/driver, command, commit and result. Shared/contended systems are acceptable only with explicit caveat when peak uncontended performance is not the criterion.

## 2026-09-13 — paper results freeze deferred to M19

Manuscript structure/methods may evolve before M19, but final numerical tables/figures/results are frozen only after required v1 evidence closes, with exact code/reference SHAs, protocols, datasets, environments, run/job/artifact IDs, hashes and regeneration scripts.
