# HGFX v1.0 Release Gate

Last synchronized: 2026-09-14
Status: **OPEN / IN PROGRESS**

## Product definition

HGFX v1.0 is a functional and scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0. Bitwise identity is not generally required, but every accepted equivalence must follow a rule frozen before its validation data are observed. No post-hoc threshold, seed, dataset, start, grid, model-family or optimizer change may obtain PASS.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md` and `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` as acceptance policy.

## Mandatory acceptance criteria

- [ ] Complete required MATLAB model/workflow coverage
- [ ] Fit workflow parity/equivalence under frozen policy
- [ ] Simulation workflow parity/equivalence
- [ ] Trajectory output parity/equivalence
- [ ] Hessian/LME/statistical output parity/equivalence
- [ ] Paired parameter recovery against same MATLAB oracle/workflow
- [ ] Paired model recovery/model-selection validation
- [ ] CPU/GPU numerical agreement on required supported paths
- [ ] Python reproduction of required MATLAB demo workflows
- [ ] Independent-use documentation/examples
- [ ] Aggregate evidence/provenance closure
- [ ] Zero MATLAB runtime dependency for users

## Current evidence snapshot

- M0-M17 completed in their documented scopes.
- Historical M18 scientific result: FAIL, preserved.
- D02 model selection: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS, run `34763542557`.
- Historical exact 512 case: `REFERENCE_LIMITATION_MATCH` for that exact case.
- Official fit/Bayes closure run `34823572071`, job `103910417693`: **7/9 direct PASS**; D02_fit and D08_fit failed.
- Official artifact ID `10339454535`, SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.

### D08 — BLOCKED

The prospectively frozen Level-2 endpoint-sensitivity holdout **failed**. Run `34826235671`, job `103918945542`, artifact `10340644941`, SHA-256 `5211ffa97880e674f7d9b2a4ab1edba0a29dde57a7127483fd4beeb88295fac1` used frozen seeds `271828182` and `314159265`. The first seed passed; the second produced `INFERENCE_EQUIVALENCE_FAIL` with optimizer-path and core inference differences. Same-MATLAB-endpoint replay still has no mismatch, but this is insufficient to satisfy the frozen Level-2 rule.

The failed protocol is preserved in `reference/validation/m18_d08_holdout/decision.json`. D08 may not be rescued by changing that protocol post hoc. A diagnostic-only optimizer localization is implemented and queued; it cannot itself confer PASS.

### D02 — BLOCKED

D02 fails inference-level equivalence because endpoint, H/Sigma/Corr/LME, predictions and residuals differ materially despite several shared-state/objective replays passing. Frozen `m18-d02-basin-probe-1` is a classification diagnostic only.

Its first run `34827198731` failed mechanically due NaN-unsafe checking of structural fixed slots. Commit `942ca86eea1fe52e8326c14f8fe175a5faa3db84` corrects only the harness; seed/grid/tolerance/model/optimizer remain frozen. Corrected run `34829122057` is queued.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: a prospectively frozen Level-2 protocol passes. D08's first such protocol did **not** pass.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation.

Historical/direct and prospective failures remain immutable evidence.

## M18/v1 exit conditions

- [ ] All required model families/workflows accounted for
- [ ] Fit/simulation/trajectory/statistical outputs evidence-backed
- [ ] Official required demos/workflows reproduced
- [ ] Every non-direct-PASS case has supported classification and any accepted-equivalence protocol actually passes
- [ ] Every accepted limitation has exact MATLAB evidence
- [ ] No unresolved required implementation/optimizer/model-selection mismatch
- [ ] Paired parameter/model recovery complete
- [ ] Robustness/backend/physical-GPU applicability matrix complete
- [ ] D10-D12 and other required output surfaces closed
- [ ] Aggregate evidence checker/report passes
- [ ] Clean install/examples/docs/API/licenses verified
- [ ] Zero MATLAB runtime dependency verified

After these: M19 evidence freeze, then M20 v1.0 Candidate.