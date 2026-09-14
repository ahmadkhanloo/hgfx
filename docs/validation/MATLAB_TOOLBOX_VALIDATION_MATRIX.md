# MATLAB Toolbox Validation Matrix

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

Acceptance is scientific/functional equivalence under `MATLAB_EQUIVALENCE_POLICY.md`, not bitwise identity and not post-hoc tolerance relaxation.

## Validation layers

| ID | Capability | Status |
|---|---|---|
| V01 HGF forward | M4 | PASS |
| V02 eHGF forward | M5 | PASS |
| V03 uHGF forward | M6 | PASS |
| V04 observations | M7 | PASS |
| V05 objective | M8 | PASS |
| V06 fitting | M9 + M18 | core historical scope PASS; product workflow closure IN PROGRESS |
| V07 Hessian/covariance/LME | M10 + M18 | historical core scope PASS; final workflow surface open |
| V08 simulation | M11/M12 | historical core scope PASS; demo wrappers remain |
| V09 parameter recovery | M18/M18A/M18B/future paired | IN PROGRESS; historical M18 FAIL preserved |
| V10 model recovery/selection | paired recovery/demo evidence | IN PROGRESS; D02 model-selection parity PASS |
| V11 robustness | S9 | OPEN/TODO |
| V12 CPU/GPU agreement | M14-M17 + S9 audit | prior scopes PASS; final applicability OPEN |
| V13 official MATLAB workflows | M18 official/demo suites | **IN PROGRESS / BLOCKED by D02 and D08** |
| V14 MATLAB limitations | paired limitation registry | exact 512 case REFERENCE_LIMITATION_MATCH; others case-specific |

## Official fit/Bayes closure

Unchanged direct gate: run `34823572071`, job `103910417693`, head `648c3f84905eb7fe952c070e5ee858e48de4a3fa`, result **7/9 direct PASS**.

Artifact `m18-official-workflows`, ID `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.

| Case | Direct gate | Current status |
|---|---|---|
| D01_bayes | PASS | PASS |
| D01_fit | PASS | PASS |
| D02_fit | FAIL / optimizer mismatch | **BLOCKED / INFERENCE_EQUIVALENCE_FAIL** |
| D03_fit | PASS | PASS |
| D05_fit | PASS | PASS |
| D06_bayes | PASS | PASS |
| D06_fit | PASS | PASS |
| D07_fit | PASS | PASS |
| D08_fit | FAIL / optimizer mismatch | **BLOCKED; prospective Level-2 holdout failed** |

## D08 evidence

Calibration/focused endpoint evidence showed exact same-MATLAB-endpoint replay and motivated a prospectively frozen Level-2 holdout. That holdout is now completed and failed:

- run `34826235671`, job `103918945542`, tested head `57cd9216fde5b36dd3a6ef033df2b2369e96b022`;
- artifact `m18-d08-equivalence-holdout`, ID `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1`;
- seed 271828182: PASS;
- seed 314159265: `INFERENCE_EQUIVALENCE_FAIL`;
- exact MATLAB-endpoint replay: no mismatches;
- optimizer trace first x mismatch at `(41,4)` and later inference outputs exceed Level-2 requirements.

Decision record: `reference/validation/m18_d08_holdout/decision.json` => `FAIL_PRESERVED_D08_REMAINS_BLOCKED`.

Diagnostic-only next step: `m18-d08-holdout-optimizer-probe-1`, fixed seed 314159265, exact MATLAB rows 38-44 around the first path split. Current queued run: `34829121895`. Diagnostic results cannot close D08 by themselves.

## D02 evidence

Exact MATLAB endpoint replay, initial Ridders, sampled MATLAB-path objectives and quasi-Newton replay provide important agreement, but the actual fitted endpoint and H/Sigma/Corr/LME/predictions/residuals remain materially different. D02 therefore remains `INFERENCE_EQUIVALENCE_FAIL / BLOCKED`.

Frozen classifier `m18-d02-basin-probe-1` evaluates identical MATLAB/HGFX objectives at 9 preregistered transformed vectors with existing `rtol=3e-8`, `atol=3e-10`.

First run `34827198731` was not a scientific result: the preparer rejected structural NaN-vs-NaN fixed slots. Artifact/run remain preserved. Commit `942ca86eea1fe52e8326c14f8fe175a5faa3db84` repairs only NaN-aware contract checking and interpolates only free coordinates, without changing the frozen experiment. Corrected run `34829122057` is queued.

Possible diagnostic classifications are `SAME_VECTOR_IMPLEMENTATION_MISMATCH`, `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`, or `INSUFFICIENT_REFERENCE_EVIDENCE`; none is PASS.

## Established reference-aware cases

- D02 model-family behavior: `PASS_MODEL_SELECTION_PARITY` on exact paired MATLAB/HGFX behavior.
- D04 uHGF→AR(1): PASS on run `34763542557`.
- exact historical 512-trial case: `REFERENCE_LIMITATION_MATCH`, exact case only.

## Remaining release validation

Close D02/D08 under frozen policy; D09-D12 surfaces; paired parameter/model recovery; evidence-backed repairs; robustness/backend applicability including physical GPU where needed; aggregate evidence/provenance; release packaging/install/docs/no-MATLAB-runtime.

M18/v1 cannot close while D02 or D08 has an unresolved HGFX-only required-scope optimizer/inference mismatch.