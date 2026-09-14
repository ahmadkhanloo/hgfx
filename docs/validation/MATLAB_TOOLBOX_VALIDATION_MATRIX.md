# MATLAB Toolbox Validation Matrix

Last synchronized: 2026-09-14
Status: **IN PROGRESS**

## Purpose

This matrix tracks HGFX v1.0 against the frozen MATLAB HGF Toolbox 8.2.0 behavior. The acceptance target is toolbox workflow/scientific equivalence, not bit-for-bit identity, internal-unit-test success alone, or forcing one model family to solve every scientific case.

Reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

Operational ordering: `docs/planning/V1_TODO.md` and `docs/planning/M18_COMPLETION_PLAN.md`.
Reference-limitation policy: `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.
Numerical/inferential equivalence policy: `docs/validation/MATLAB_EQUIVALENCE_POLICY.md` (`matlab-equivalence-policy-1`).

The equivalence policy preserves historical failures and existing field tolerances. It does not introduce a generic tolerance increase. It distinguishes exact contract equality, scale-aware numerical equivalence, endpoint-sensitivity numerical equivalence, and separately preregistered inferential equivalence.

## Validation layers

| ID | MATLAB capability | HGFX validation artifact | Current status |
|---|---|---|---|
| V01 | HGF forward trajectories | M4 / forward parity fixtures | **PASS** |
| V02 | eHGF forward trajectories | M5 parity fixtures | **PASS** |
| V03 | uHGF forward trajectories | M6 parity fixtures | **PASS** |
| V04 | Observation models | M7 observation parity | **PASS** |
| V05 | Objective computation | M8 objective parity | **PASS** |
| V06 | Model fitting compatibility | M9 compatibility fitting | **PASS in established core scope; official workflow closure still IN PROGRESS** |
| V07 | Hessian/covariance/LME | M10 validation | **PASS in established core scope; release-surface evidence still aggregated under M18** |
| V08 | Simulation compatibility | M11/M12 validation | **PASS in established core scope; remaining demo-wrapper coverage tracked in V13** |
| V09 | Parameter recovery | historical M18 + M18A/M18B + future paired product protocol | **IN PROGRESS** — historical M18 FAIL preserved; M18B protocol evidence does not alone close v1 recovery |
| V10 | Model recovery / model-selection behavior | paired recovery + official demo reference workflows | **IN PROGRESS** — D02 model-selection parity PASS; full model-recovery gate open |
| V11 | Robustness sweeps | M18/S9 robustness matrix | **OPEN/TODO** |
| V12 | CPU/GPU numerical agreement | M14-M17 physical-H100 evidence + M18 applicability audit | **PASS in prior validated paths; M18 applicability/remaining-path audit OPEN** |
| V13 | MATLAB demo/workflow reproduction | official demo/workflow suites | **IN PROGRESS** — historical official closure is 7/9 PASS; D02 remains blocking; D08 has a prospective equivalence holdout pending; D09-D12 surfaces remain open |
| V14 | MATLAB-equivalent scientific limitations | reference-limitation evidence registry | **IN PROGRESS** — exact historical 512-trial case classified REFERENCE_LIMITATION_MATCH; additional limitations require exact paired evidence |

## Current official workflow evidence

Latest unchanged official gate evidence was produced at implementation head `648c3f84905eb7fe952c070e5ee858e48de4a3fa`.

`M18 Official Workflow Closure` run `34823572071`, job `103910417693`:

| Case | Historical official-gate status | Current interpretation |
|---|---|---|
| D01_bayes | PASS | PASS |
| D01_fit | PASS | PASS |
| D02_fit | **OPTIMIZER_MISMATCH / BLOCKING** | **INFERENCE_EQUIVALENCE_FAIL / BLOCKING**; new basin diagnostic preregistered |
| D03_fit | PASS | PASS |
| D05_fit | PASS | PASS |
| D06_bayes | PASS | PASS |
| D06_fit | PASS | PASS |
| D07_fit | PASS | PASS |
| D08_fit | **OPTIMIZER_MISMATCH / BLOCKING** | endpoint-sensitivity candidate; prospective holdout required before acceptance |

Artifact: `m18-official-workflows`, ID `10339454535`, ZIP SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.

The historical workflow remains failed. A later endpoint-sensitivity classification, if prospectively validated, does not rewrite this artifact as a direct numerical PASS.

## D08_fit — endpoint-sensitivity candidate

Focused endpoint diagnostic run `34823572192`, artifact `10339403480`, ZIP SHA-256 `c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de` established:

- the official residual mismatch is `fit.traj.epsi`, first zero-based index `(175,1)`, HGFX `138.87836008346915` versus MATLAB `138.8783558587791`, absolute difference `4.224690043130642e-6`;
- the largest fitted transformed-parameter endpoint difference is only `2.5768804867709605e-9` at zero-based parameter index 8;
- HGFX replay at the exact MATLAB endpoint reproduces the focused MATLAB `epsi` value exactly (`138.8783558587791`);
- HGFX replay at the exact MATLAB endpoint also reproduces MATLAB `negLj` (`-2323.459762013518`);
- replacing parameter 8 alone reduces the focused `epsi` discrepancy from `4.713810909606764e-6` to `4.3272243033243285e-7`;
- the optimizer trace and MATLAB-path objective diagnostics pass the frozen tolerance.

Therefore D08 is **not accepted merely by loosening `rtol`**. It is a candidate for `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` under `matlab-equivalence-policy-1`.

The prospective holdout was frozen before execution with seeds `271828182` and `314159265`, unchanged official data/model/config/optimizer, and unchanged existing field tolerances. Workflow `M18 D08 Equivalence Holdout` is implemented; run `34826235671` was queued at the last synchronization. Until both frozen holdouts pass unchanged, D08 is **IMPLEMENTED BUT NOT VALIDATED** under the new acceptance path.

Calibration evidence is preserved in `reference/validation/m18_d08_endpoint/decision.json` and remains explicitly diagnostic-only.

## D02_fit — inference-level blocker

D02 is not eligible for the D08 endpoint-sensitivity exception. Current evidence includes:

- exact MATLAB reference-point replay: PASS;
- initial Ridders gradient: PASS at the existing acceptance tolerance;
- MATLAB optimizer-path objective replay: PASS over 22 sampled points;
- quasi-Newton step/BFGS replay from exact MATLAB state: machine-level agreement;
- optimizer trace first material path split at zero-based `(7,0)`: HGFX `0.33948935870343205` versus MATLAB `0.33948938811282225`;
- materially different fitted endpoint and inference outputs, including `H`, `Sigma`, `Corr`, `LME`, predictions and residuals.

Representative differences from the latest official evidence include `H[0,0]` `0.30808977632407525` versus `0.9998054857037648`, `Sigma[0,0]` `10.242002825962189` versus `1.0001982837227512`, `Corr[0,1]` `-0.8242120336850707` versus `0.0015029079855196361`, and LME `-78.28285368561887` versus `-77.62115775483699`.

Accordingly `reference/validation/m18_d02_inference/decision.json` records **INFERENCE_EQUIVALENCE_FAIL / BLOCKING**. Small objective differences alone cannot override these inference-level differences.

A classification-only cross-endpoint diagnostic is frozen in `docs/validation/M18_D02_BASIN_DIAGNOSTIC.md` (`m18-d02-basin-probe-1`). It evaluates both MATLAB and HGFX objectives at the same preregistered 9-point line between their fitted endpoints using the unchanged default M18 tolerance (`rtol=3e-8`, `atol=3e-10`). It can distinguish `SAME_VECTOR_IMPLEMENTATION_MISMATCH` from `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`, but **neither result closes D02**. The diagnostic implementation/workflow is present but has not yet produced validated CI evidence at this synchronization.

## Reference-aware model-family evidence

### D02 model-selection behavior — PASS

The official MATLAB demo documents a regime where classic HGF is invalid and eHGF is the supported solution. On the exact official input/parameters:

- MATLAB classic HGF: FAIL with negative-posterior-precision condition;
- HGFX classic HGF: corresponding FAIL;
- MATLAB eHGF: SUCCESS;
- HGFX eHGF: SUCCESS;
- successful eHGF states/trajectories: parity PASS.

Workflow run `34684401843`, job `103528739680`; classification `PASS_MODEL_SELECTION_PARITY`; artifact `10294714175`, SHA-256 `2aa62628d16198f8f335b56fca0f015303439406bb278a329b4cae09b9e69afd`.

This proves that v1 compatibility follows MATLAB model-family behavior rather than requiring base HGF to pass unsupported regimes.

### D04 uHGF -> AR(1) — PASS

Workflow `M18 Demo uHGF AR1 Workflow Parity`, run `34763542557`, completed successfully at `faf97bf...`.

Older planning statements that call D04 “IMPLEMENTED BUT NOT VALIDATED” are superseded by this evidence.

## Exact 512-trial case — REFERENCE_LIMITATION_MATCH

The exact historical HGF 512-trial case has paired frozen-reference evidence showing the same instability/invalid variational regime in MATLAB and HGFX before fitting. It is accepted as `REFERENCE_LIMITATION_MATCH` for that exact case only.

This is not a general claim of arbitrary 512-trial support and not a scientific PASS.

## Required classification for every non-direct-PASS case

Primary diagnostic/problem classes remain:

- `IMPLEMENTATION_MISMATCH`
- `OPTIMIZER_MISMATCH`
- `MODEL_SELECTION_MISMATCH`
- `INSUFFICIENT_REFERENCE_EVIDENCE`
- `REFERENCE_LIMITATION_MATCH`

Prospective accepted-equivalence outcomes defined by `MATLAB_EQUIVALENCE_POLICY.md` are:

- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`
- `PASS_INFERENTIAL_EQUIVALENCE`

These accepted-equivalence outcomes require their own frozen evidence and must never be reported as bitwise equality. `REFERENCE_LIMITATION_MATCH` is acceptable only when the same limitation is demonstrated on the exact paired MATLAB workflow/regime and there is no earlier HGFX-only divergence.

## Remaining release-validation work

See `V1_TODO.md` for checkboxes. In summary:

- execute and record the frozen D08 prospective holdout without changing its seeds/rules;
- execute the frozen D02 basin diagnostic, then continue evidence-backed optimizer/conditioning or implementation work according to its classification;
- finish remaining required demo contract/wrapper coverage including D09;
- close D10 Corr/Sigma/plot surface, D11 residual diagnostics and D12 Bayesian parameter averaging;
- execute paired parameter and model recovery;
- repair only demonstrated HGFX-only mismatches;
- complete robustness and backend applicability/physical-GPU closure;
- implement aggregate evidence checker/report and complete release packaging/docs/install checks.

## Acceptance

M18/v1 validation is complete only when every required MATLAB workflow/surface has reproducible evidence, every non-PASS case has a supported classification, accepted limitations/equivalences have exact frozen evidence, and no unresolved HGFX-only implementation/optimizer/model-selection mismatch remains in required scope.

Historical failed experiments must remain preserved rather than rewritten.