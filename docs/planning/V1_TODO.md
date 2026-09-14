# HGFX v1.0 Live TODO

Last synchronized: 2026-09-14
Status: **IN PROGRESS**
Branch: `migration/m18-workflow-closure`
Current head before this sync: `942ca86eea1fe52e8326c14f8fe175a5faa3db84`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

Use this file with `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`, and `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`.

HGFX v1.0 targets scientific/functional equivalence with the frozen MATLAB toolbox, not bitwise identity. Never change thresholds, seeds, datasets, starts, validation grids, model family, or optimizer settings after seeing results to obtain PASS. Historical failures remain immutable evidence.

## Current validated baseline

- M0-M17: completed in their documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.
- D02 model-selection behavior: **PASS_MODEL_SELECTION_PARITY**.
- D04 uHGF -> AR(1): **PASS**, run `34763542557`.
- Exact historical 512-trial case: **REFERENCE_LIMITATION_MATCH** in that exact paired scope.
- Latest unchanged official fit/Bayes closure: run `34823572071`, job `103910417693`, **7/9 direct PASS** at head `648c3f84905eb7fe952c070e5ee858e48de4a3fa`.
- Official artifact `m18-official-workflows`, ID `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.
- Direct blockers remain `D02_fit` and `D08_fit`.
- M18/v1 product closure: **OPEN**. PR #26 remains draft/unmerged.

## NOW — D08 failed prospective holdout

### D08_fit — BLOCKED

The prospective Level-2 endpoint-sensitivity experiment is complete and **FAILED** under its frozen rules.

Evidence:

- workflow: `M18 D08 Equivalence Holdout`
- run: `34826235671`
- job: `103918945542`
- tested head: `57cd9216fde5b36dd3a6ef033df2b2369e96b022`
- artifact: `m18-d08-equivalence-holdout`, ID `10340644941`
- artifact SHA-256: `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1`
- frozen seeds: `271828182`, `314159265`

Results:

- seed `271828182`: PASS.
- seed `314159265`: **INFERENCE_EQUIVALENCE_FAIL**.
- exact MATLAB-endpoint replay has `same_endpoint_mismatches=[]`.
- first frozen-tolerance optimizer `iter.x` split: zero-based `(41,4)`, HGFX `-1.8442792255639227`, MATLAB `-1.844279150958309`.
- first `iter.val` split: zero-based `(56,)`, HGFX `-2253.9650998741404`, MATLAB `-2253.968334805428`.
- seed 314159265 also differs outside the Level-2 requirements in final parameters, Hessian, covariance, correlation, predictions, residuals and residual autocorrelation.

The failed prospective experiment is preserved in `reference/validation/m18_d08_holdout/decision.json`. Do not replace the failed seed, broaden tolerance, or relabel D08 as endpoint-equivalent.

Completed:

- [x] Freeze `matlab-equivalence-policy-1` before prospective validation.
- [x] Freeze holdout seeds before execution.
- [x] Execute the frozen holdout unchanged.
- [x] Preserve both PASS and FAIL outcomes with run/job/artifact/hash.
- [x] Freeze a diagnostic-only optimizer localization protocol for the failed seed in `../validation/M18_D08_HOLDOUT_OPTIMIZER_DIAGNOSTIC.md`.
- [x] Implement MATLAB exporter, HGFX checker and workflow for that diagnostic.

Next:

- [ ] Execute `M18 D08 Holdout Optimizer Diagnostic` on frozen seed `314159265`. Current queued run at this sync: `34829121895`.
- [ ] If exact shared MATLAB states show objective/gradient divergence, localize the responsible primitive/arithmetic path regression-first.
- [ ] If shared-state objective/gradient pass while fitted paths diverge, investigate finite-difference/optimizer state/path/termination sensitivity rather than model equations.
- [ ] Keep D08 BLOCKED until the direct gate passes or a new separately preregistered scientifically sufficient protocol is justified prospectively. Do not redefine the failed Level-2 protocol post hoc.

## NOW — D02 inference blocker

### D02_fit — BLOCKED / INFERENCE_EQUIVALENCE_FAIL

Established evidence:

- exact MATLAB endpoint replay in HGFX: PASS;
- initial Ridders gradient: PASS under existing tolerance;
- sampled MATLAB optimizer-path objectives: PASS;
- quasi-Newton step/BFGS algebra from exact MATLAB state: machine-level agreement;
- fitted endpoint, H, Sigma, Corr, LME, predictions and residuals differ materially.

Therefore D02 is not eligible for a trajectory-only tolerance exception.

Frozen classifier `m18-d02-basin-probe-1` uses exactly 9 line points `alpha=[0,0.125,...,1]` and unchanged `rtol=3e-8`, `atol=3e-10`.

First execution `34827198731` stopped because the harness treated structural MATLAB/HGFX `NaN` slots as unequal. This is a **HARNESS EXECUTION FAILURE**, not a scientific result. The failed run/artifact is preserved. Commit `942ca86eea1fe52e8326c14f8fe175a5faa3db84` fixes only NaN-aware contract checking and continues to interpolate only frozen free coordinates; seed/grid/tolerance/model/optimizer/endpoints are unchanged.

Next:

- [ ] Execute corrected `M18 D02 Basin Diagnostic` unchanged. Current queued run at this sync: `34829122057`.
- [ ] Shared-vector failure => `SAME_VECTOR_IMPLEMENTATION_MISMATCH`; localize exact point before optimizer changes.
- [ ] All shared-vector objectives pass => `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`; investigate conditioning/gradient amplification/path/termination.
- [ ] Neither diagnostic classification closes D02; keep BLOCKED until inference-level acceptance is genuinely satisfied.

## Official workflow closure exit gate

- [ ] D01/D03/D05/D06/D07 remain healthy on affected code paths.
- [ ] D02 reaches a release-acceptable outcome under frozen policy.
- [ ] D08 reaches a release-acceptable outcome under frozen policy; failed Level-2 holdout remains visible.
- [ ] All accepted non-direct outcomes have immutable prospective evidence.
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