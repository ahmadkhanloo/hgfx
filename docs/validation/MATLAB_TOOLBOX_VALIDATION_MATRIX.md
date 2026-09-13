# MATLAB Toolbox Validation Matrix

Last synchronized: 2026-09-13
Status: **IN PROGRESS**

## Purpose

This matrix tracks HGFX v1.0 against the frozen MATLAB HGF Toolbox 8.2.0 behavior. The acceptance target is toolbox workflow/scientific equivalence, not merely internal unit-test success and not forcing one model family to solve every scientific case.

Reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

Operational ordering: `docs/planning/V1_TODO.md` and `docs/planning/M18_COMPLETION_PLAN.md`.
Reference-limitation policy: `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.

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
| V13 | MATLAB demo/workflow reproduction | official demo/workflow suites | **IN PROGRESS** — D04 PASS; current fit/Bayes closure 7/9 PASS; D02_fit/D08_fit blocking; D09-D12 surfaces remain open |
| V14 | MATLAB-equivalent scientific limitations | reference-limitation evidence registry | **IN PROGRESS** — exact historical 512-trial case classified REFERENCE_LIMITATION_MATCH; additional limitations require exact paired evidence |

## Current official workflow evidence

Latest tested implementation head: `faf97bfdbef1333a6a756749a8ab9d6a5be102b3`.

`M18 Official Workflow Closure` run `34763542525`, job `103740409700`:

| Case | Status |
|---|---|
| D01_bayes | PASS |
| D01_fit | PASS |
| D02_fit | **OPTIMIZER_MISMATCH / BLOCKING** |
| D03_fit | PASS |
| D05_fit | PASS |
| D06_bayes | PASS |
| D06_fit | PASS |
| D07_fit | PASS |
| D08_fit | **OPTIMIZER_MISMATCH / BLOCKING** |

Artifact: `m18-official-workflows`, ID `10319853691`, ZIP SHA-256 `2cb5b01bce11b900261a0e309e80bf4220d63ac655417d86bf32539bf1cbf773`.

The workflow intentionally fails until all required cases in that gate satisfy the unchanged acceptance criteria.

### D02_fit current diagnosis

- Exact MATLAB reference solution replay in HGFX: PASS at the existing gate tolerance.
- Initial Ridders gradient: PASS at the existing acceptance tolerance.
- MATLAB optimizer-path objective replay: PASS at the existing gate tolerance.
- Quasi-Newton step/BFGS replay from exact MATLAB state matches to machine precision.
- Exact MATLAB Ridders finite-difference coordinates expose raw cross-runtime objective differences around `1e-12`, amplified by later optimization.

Therefore the next evidence task is objective decomposition at those exact finite-difference coordinates; do not alter optimizer/tolerance/seed/data/model settings to force convergence to the MATLAB endpoint.

### D08_fit current diagnosis

The only frozen-gate mismatch is `fit.traj.epsi` near trial index 178 (~`3e-6`); reference-point, initial-Ridders, optimizer-trace and MATLAB-path-objective diagnostics otherwise pass. Full-precision final-vector and local state decomposition is required before classification/repair.

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

Current-head workflow `M18 Demo uHGF AR1 Workflow Parity`, run `34763542557`, completed successfully at `faf97bf...`.

Older planning statements that call D04 “IMPLEMENTED BUT NOT VALIDATED” are superseded by this evidence.

## Exact 512-trial case — REFERENCE_LIMITATION_MATCH

The exact historical HGF 512-trial case has paired frozen-reference evidence showing the same instability/invalid variational regime in MATLAB and HGFX before fitting. It is accepted as `REFERENCE_LIMITATION_MATCH` for that exact case only.

This is not a general claim of arbitrary 512-trial support and not a scientific PASS.

## Required classification for every non-PASS case

Use exactly one primary class:

- `IMPLEMENTATION_MISMATCH`
- `OPTIMIZER_MISMATCH`
- `REFERENCE_LIMITATION_MATCH`
- `MODEL_SELECTION_MISMATCH`
- `INSUFFICIENT_REFERENCE_EVIDENCE`

`REFERENCE_LIMITATION_MATCH` is acceptable for MATLAB-equivalence v1.0 only when the same limitation is demonstrated on the exact paired MATLAB workflow/regime and there is no earlier HGFX-only divergence.

## Remaining release-validation work

See `V1_TODO.md` for checkboxes. In summary:

- close D02_fit and D08_fit without changing the frozen gate;
- finish remaining required demo contract/wrapper coverage including D09;
- close D10 Corr/Sigma/plot surface, D11 residual diagnostics and D12 Bayesian parameter averaging;
- execute paired parameter and model recovery;
- repair only demonstrated HGFX-only mismatches;
- complete robustness and backend applicability/physical-GPU closure;
- implement aggregate evidence checker/report and complete release packaging/docs/install checks.

## Acceptance

M18/v1 validation is complete only when every required MATLAB workflow/surface has reproducible evidence, every non-PASS case is supported by a valid classification, accepted limitations have exact frozen-reference evidence, and no unresolved HGFX-only implementation/optimizer/model-selection mismatch remains in required scope.

Historical failed experiments must remain preserved rather than rewritten.
