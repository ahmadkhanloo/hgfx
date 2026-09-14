# MATLAB Toolbox Validation Matrix

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

Acceptance is scientific/functional equivalence under `MATLAB_EQUIVALENCE_POLICY.md` plus exact-scope reference limitations under `MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.

## Validation layers

| ID | Capability | Status |
|---|---|---|
| V01 HGF forward | M4 | PASS |
| V02 eHGF forward | M5 | PASS |
| V03 uHGF forward | M6 | PASS |
| V04 observations | M7 | PASS |
| V05 objective | M8 | PASS |
| V06 fitting | M9 + M18 | direct gate has 2 failures; D02 exact scope accepted as reference limitation; D08 open |
| V07 Hessian/covariance/LME | M10 + M18 | historical core PASS; D02 exact limitation disclosed; D08 open |
| V08 simulation | M11/M12 | historical core PASS; demo wrappers remain |
| V09 parameter recovery | M18/M18A/M18B/future paired | IN PROGRESS; historical M18 FAIL preserved |
| V10 model recovery/selection | paired recovery/demo evidence | IN PROGRESS; D02 model-selection parity PASS |
| V11 robustness | S9 | OPEN/TODO |
| V12 CPU/GPU agreement | M14-M17 + S9 audit | prior scopes PASS; final applicability OPEN |
| V13 official MATLAB workflows | M18 official/demo suites | **IN PROGRESS / D08 BLOCKED**; D02 exact official scope = REFERENCE_LIMITATION_MATCH |
| V14 MATLAB limitations | paired limitation registry | exact 512 case + exact D02 official case are REFERENCE_LIMITATION_MATCH; no generalization |

## Official fit/Bayes closure

Direct gate remains **7/9 PASS**. Direct failures are retained for D02_fit and D08_fit.

| Case | Direct gate | Release disposition |
|---|---|---|
| D01_bayes | PASS | PASS |
| D01_fit | PASS | PASS |
| D02_fit | FAIL / optimizer mismatch | **REFERENCE_LIMITATION_MATCH — exact official scope; direct FAIL preserved** |
| D03_fit | PASS | PASS |
| D05_fit | PASS | PASS |
| D06_bayes | PASS | PASS |
| D06_fit | PASS | PASS |
| D07_fit | PASS | PASS |
| D08_fit | FAIL / optimizer mismatch | **BLOCKED; prospective Level-2 holdout failed** |

## D02 evidence and scope

Decision record: `../../reference/validation/m18_d02_reference_limitation/decision.json`.

- same-vector basin run `34829122057`: all 9 frozen objective points pass;
- optimizer-source run `34835728961`: exact source objective; first off-centre likelihood-only residual `2.842170943040401e-14`; MATLAB-sample Ridders replay exact;
- source-likelihood run `34836421105`: inference states exact; trial likelihood differences <= `8.881784197001252e-16`; binary64 primitive/reduction localization;
- MATLAB self-sensitivity run `34837033370`: baseline exact, 6/6 independent +/- one-spacing starts materially change fitted endpoint; classification `MATLAB_START_ULP_BASIN_SENSITIVE`.

This establishes an optimizer/numerical-basin limitation in the frozen reference for the exact D02 workflow. It does not erase the direct failure and does not cover other seeds/regimes.

## D08 evidence

The frozen prospective holdout remains failed: seed `271828182` PASS, seed `314159265` `INFERENCE_EQUIVALENCE_FAIL`.

Failed-holdout optimizer run `34829121895` classifies `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`: exact shared-state objectives pass, gradient residuals are tiny, and QN step/inverse-Hessian replays are machine-level around the first path split.

USDCHF placeholder/prior preparation is now exact after the evidence-linked repair: run `34836421030` => `NO_PRIOR_DIVERGENCE`, all compared prior inputs/terms/totals exact. The hard holdout still fails post-repair, so D08 remains **BLOCKED**.

## Established reference-aware cases

- D02 exact official fit: `REFERENCE_LIMITATION_MATCH`, exact scope only.
- D02 model-family behavior: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS on run `34763542557`.
- exact historical 512-trial case: `REFERENCE_LIMITATION_MATCH`, exact case only.

## Remaining release validation

Resolve D08 under frozen policy; close D09-D12 surfaces; paired parameter/model recovery; evidence-backed repairs; robustness/backend applicability including physical GPU where needed; aggregate evidence/provenance; release packaging/install/docs/no-MATLAB-runtime.
