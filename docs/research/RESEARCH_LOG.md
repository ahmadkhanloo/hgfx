# Research Log

This log records paper-relevant scientific and engineering decisions. It is not a substitute for raw gate evidence. Historical failures are never rewritten.

## 2026-09-14 — D08 prospective endpoint-sensitivity hypothesis did not generalize

- **Question:** Can D08's original direct-gate failure be accepted as a numerically immaterial endpoint-sensitivity effect under a prospectively frozen Level-2 rule?
- **Pre-registered evidence:** `matlab-equivalence-policy-1`; holdout seeds `271828182` and `314159265`; unchanged official USDCHF data, uHGF + gaussian_obs model/config, quasinewton optimizer and existing field tolerances.
- **Run:** `M18 D08 Equivalence Holdout` `34826235671`, job `103918945542`, tested head `57cd9216fde5b36dd3a6ef033df2b2369e96b022`.
- **Artifact:** `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1`.
- **Observed:** seed 271828182 passed; seed 314159265 failed inference-level requirements. Exact MATLAB-endpoint replay still had no mismatch, but the fitted optimizer path diverged and final/H/Sigma/Corr/yhat/res/resAC exceeded Level-2 conditions.
- **Decision:** Preserve the failed prospective experiment. D08 remains BLOCKED. Do not replace the failing seed, broaden tolerance, or reinterpret the frozen Level-2 protocol after seeing the result.
- **Scientific implication:** exact same-endpoint numerical agreement is not sufficient evidence that fitting-level inference is stable across cases; optimizer-path sensitivity itself can be consequential.
- **Next:** diagnostic-only localization around the first frozen failing optimizer path split, with no acceptance effect.

## 2026-09-14 — D02 basin diagnostic first execution was a harness failure, not scientific evidence

- **Question:** Did the first `m18-d02-basin-probe-1` run classify the D02 mismatch?
- **Run:** `34827198731`.
- **Observed:** MATLAB reference export succeeded, but Python preparer raised `Fixed transformed parameters differ between endpoints` before evaluating the frozen grid.
- **Cause:** structural fixed slots are NaN in both MATLAB/HGFX; `np.array_equal` without `equal_nan=True` treats NaN-vs-NaN as unequal.
- **Decision:** classify this run as **HARNESS EXECUTION FAILURE**, preserve it, and fix only NaN-aware contract checking. Commit `942ca86eea1fe52e8326c14f8fe175a5faa3db84` keeps seed, endpoints, alpha grid, model, optimizer and tolerances unchanged and interpolates only free coordinates.
- **Next:** corrected CI run `34829122057` is queued; its result may classify same-vector implementation mismatch vs optimizer numerical basin candidate, but cannot itself close D02.

## 2026-09-14 — tiered equivalence replaces decimal-place thinking, not frozen evidence

- **Decision:** use exact contract, scale-aware numerical equivalence, prospectively validated endpoint-sensitivity equivalence, and separately preregistered inferential equivalence. Decimal-place-only rules are rejected.
- **Integrity:** old direct failures remain failures; new protocols must be frozen before validation data are observed; FAIL outcomes are preserved equally with PASS outcomes.
- **Policy commit:** `3bea320ac6e9f0f7cef26e63ac18e50c422a834a`.

## 2026-09-13 — v1 paper objective aligned to MATLAB-equivalent product objective

HGFX v1/paper primarily targets a validated Python replacement for frozen MATLAB HGF Toolbox 8.2.0. GPU/differentiability/performance are secondary claims conditional on scientific behavior. Frozen reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## 2026-09-13 — historical M18 FAIL remains visible

M18B protocol evidence does not retroactively convert the historical M18 recovery experiment into PASS. Final product-level recovery requires paired MATLAB/HGFX evidence under a frozen protocol.

## 2026-09-13 — reference limitations may be matched, not silently repaired

`REFERENCE_LIMITATION_MATCH` is permitted only for exact paired MATLAB limitations with no earlier HGFX-only divergence. Official MATLAB model-family choices (eHGF/uHGF/specialized models) should be mirrored rather than silently substituting another model.

## 2026-09-13 — implementation parity and scientific identifiability are distinct

Recovery failure alone does not prove a porting defect. Required classifications separate implementation mismatch, optimizer/numerical mismatch, model-selection mismatch, scientific/reference limitation and insufficient evidence.

## 2026-09-13 — physical GPU evidence required for GPU claims

CPU/mock execution cannot support GPU validation claims. Record physical hardware, runtime/driver, command, commit and result. Shared/contended systems are acceptable only with explicit caveat when peak uncontended performance is not the criterion.

## 2026-09-13 — D02 is a numerical-reproducibility case study candidate, not a solved result

Earlier regression-first diagnostics found tiny cross-runtime numerical differences and demonstrated amplification through finite-difference/optimization paths. Subsequent evidence shows D02's fitted endpoint/statistical outputs remain materially different. Do not chase every last bit; use frozen same-vector/inference evidence to decide whether a micro-difference is consequential.

## 2026-09-13 — paper results freeze deferred to M19

Manuscript structure/methods may evolve before M19, but final numerical tables/figures/results are frozen only after required v1 evidence closes, with exact code/reference SHAs, protocols, datasets, environments, run/job/artifact IDs, hashes and regeneration scripts.