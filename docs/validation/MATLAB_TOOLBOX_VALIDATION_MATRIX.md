# MATLAB Toolbox Validation Matrix

Last synchronized: 2026-09-15
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
| V09 parameter recovery | M18/M18A/M18B/S7 paired | **REFERENCE_LIMITATION_MATCH — exact S7 frozen grid**; historical M18 scientific FAIL preserved |
| V10 model recovery/selection | S7 paired + demo evidence | **PASS_PAIRED_MODEL_SELECTION**; 36/36 BIC winners match, BA `0.5833333333333334` both implementations |
| V11 robustness | S9 | **NOW / IN PROGRESS** |
| V12 CPU/GPU agreement | M14-M17 + S9 audit | prior scopes PASS; final applicability OPEN |
| V13 official MATLAB workflows | M18 official/demo suites | release-acceptable in completed D01-D12 exact scopes; final S9/S10 release-surface audit still open |
| V14 MATLAB limitations | paired limitation registry | exact 512 case + exact D02 official case + exact D08 failed holdout seed + exact S7 paired recovery grid are `REFERENCE_LIMITATION_MATCH`; no generalization |

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

## D09-D12 workflow/output coverage

| Case | Surface | Status | Evidence |
|---|---|---|---|
| D09 | official sampleModel / prior-predictive workflow | PASS | run `34842943557`, artifact `10346184455` |
| D10 | Corr/Sigma analysis/plot data | PASS | run `34847266268`, artifact `10348099156` |
| D11 | residual diagnostics surface | PASS | run `34847266268`, artifact `10348099156` |
| D12 | Bayesian parameter averaging | PASS | run `34854238549`, artifact `10352486569` |

## S7 paired recovery evidence

Decision: `../../reference/validation/m18_s7_reference_limitation/decision.json` and `M18_S7_REFERENCE_LIMITATION.md`.

Official run `34896442847`; aggregate job `104163079125`; artifact `10370615292`; artifact SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92`.

- coverage: 12/12 shards, 72/72 parameter cases, 36/36 model-recovery datasets;
- HGF: MATLAB/HGFX convergence both `0.8333333333`; both fail median correlation and sRMSE;
- eHGF: MATLAB/HGFX convergence both `0.9166666667`; both fail median correlation and sRMSE;
- uHGF: MATLAB/HGFX convergence both `0.7916666667`; both fail convergence, median correlation and sRMSE;
- model recovery: 36/36 BIC winners match; MATLAB/HGFX balanced accuracy both `0.5833333333333334`.

The parameter-recovery result is an exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS. A demonstrated standard-HGF oracle defect was repaired in `0239f52f772825e0a4fc74cdf3559cafa18a603e`; final paired evidence contains no unresolved S7 implementation/optimizer/model-selection mismatch.

## Established reference-aware cases

- D02 exact official fit: `REFERENCE_LIMITATION_MATCH`, exact scope only.
- D08 exact failing holdout seed `314159265`: `REFERENCE_LIMITATION_MATCH`, exact scope only; holdout FAIL preserved.
- S7 complete paired parameter-recovery grid: `REFERENCE_LIMITATION_MATCH`, exact protocol scope only.
- S7 paired model selection: `PASS_PAIRED_MODEL_SELECTION`.
- D02 model-family behavior: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS on run `34763542557`.
- exact historical 512-trial case: `REFERENCE_LIMITATION_MATCH`, exact case only.

## Remaining release validation

The next unresolved gate is S9 robustness/backend/physical-GPU applicability closure. Then perform S10 aggregate evidence/provenance, clean install/examples/docs/API/licenses, and zero-MATLAB-runtime verification before M19 evidence freeze and M20 v1 candidate.
