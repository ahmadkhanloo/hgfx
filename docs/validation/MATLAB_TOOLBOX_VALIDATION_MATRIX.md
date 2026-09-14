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
| V06 fitting | M9 + M18 | direct gate has 2 preserved failures; D02 exact official scope and D08 exact failed-seed scope are release-acceptable reference limitations |
| V07 Hessian/covariance/LME | M10 + M18 | historical core PASS; D02/D08 exact limitations disclosed where direct fit paths diverge |
| V08 simulation | M11/M12 + D09 | historical core PASS; official D09 sampleModel workflow PASS |
| V09 parameter recovery | M18/M18A/M18B/S7 paired | **IN PROGRESS**; historical M18 FAIL preserved, paired same-oracle protocol next |
| V10 model recovery/selection | S7 paired + demo evidence | **IN PROGRESS**; D02 model-selection parity PASS, full paired recovery next |
| V11 robustness | S9 | OPEN/TODO |
| V12 CPU/GPU agreement | M14-M17 + S9 audit | prior scopes PASS; final applicability OPEN |
| V13 official MATLAB workflows | M18 official/demo suites | **release-acceptable in completed D01-D12 exact scopes; paired recovery still open** |
| V14 MATLAB limitations | paired limitation registry | exact 512 case + exact D02 official case + exact D08 failed holdout seed are REFERENCE_LIMITATION_MATCH; no generalization |

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
| D08_fit | FAIL / optimizer mismatch | **REFERENCE_LIMITATION_MATCH — exact failed seed `314159265`; prospective Level-2 FAIL preserved** |

## D02 evidence and scope

Decision record: `../../reference/validation/m18_d02_reference_limitation/decision.json`.

The exact official D02 workflow is accepted as a reference numerical-basin limitation. Direct/inference failures remain visible. This disposition does not cover other seeds/regimes.

## D08 evidence and scope

Decision record: `../../reference/validation/m18_d08_reference_limitation/decision.json`.

The frozen prospective holdout remains failed: seed `271828182` PASS, seed `314159265` `INFERENCE_EQUIVALENCE_FAIL`.

For seed `314159265` only:

- repaired-product holdout run `34842943696`, artifact `10347616859`, SHA-256 `8cbb16de519204710662d8bf0b94c2510df8c2e53f9427897b9f55d7d0b499f1` preserves the failure and has exact MATLAB-endpoint replay;
- optimizer localization run `34842943657`, artifact `10347682339`, SHA-256 `3d94f74c71e5bf6bcdd8971d647ddba31f5a087cb4f3cb9a933c6a6e3c33518a` => `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- MATLAB self-sensitivity run `34846375826`, artifact `10348900752`, SHA-256 `42874a324ef408205452516f0abe7497b60d5f12b9f9bf2972df105845f907f6`: baseline exact; 13/14 independent one-spacing starts leave the unchanged gate.

Release classification: **REFERENCE_LIMITATION_MATCH**, exact failing-seed scope only. This does not turn the prospective holdout into PASS.

## D09-D12 workflow/output coverage

| Case | Surface | Status | Evidence |
|---|---|---|---|
| D09 | official sampleModel / prior-predictive workflow | PASS | run `34842943557`, artifact `10346184455`, SHA `6c754cc02ce621c66d67224884c5347c61468cdfb6f3de81dffb03898d02b85c` |
| D10 | Corr/Sigma analysis/plot data | PASS | run `34847266268`, artifact `10348099156`, shared D10/D11 SHA `a69045cc4e1ad388c64dec7235f8c9d2ad42f6885c6210d31b979d2284b48317` |
| D11 | residual diagnostics surface | PASS | run `34847266268`, artifact `10348099156`, shared D10/D11 SHA `a69045cc4e1ad388c64dec7235f8c9d2ad42f6885c6210d31b979d2284b48317` |
| D12 | Bayesian parameter averaging | PASS | run `34854238549`, job `104009543024`, artifact `10352486569`, SHA `14ab041b2473a13496377f63d6d1897578d1785128406eadbc1d6d44ae119883` |

## Established reference-aware cases

- D02 exact official fit: `REFERENCE_LIMITATION_MATCH`, exact scope only.
- D08 exact failing holdout seed `314159265`: `REFERENCE_LIMITATION_MATCH`, exact scope only; holdout FAIL preserved.
- D02 model-family behavior: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS on run `34763542557`.
- exact historical 512-trial case: `REFERENCE_LIMITATION_MATCH`, exact case only.

## Remaining release validation

The next unresolved gate is S7 paired parameter/model recovery on the frozen original grid and same MATLAB/HGFX oracle inputs. Then perform evidence-backed repairs if needed, robustness/backend applicability including physical GPU where required, aggregate evidence/provenance, and release packaging/install/docs/no-MATLAB-runtime verification.
