# HGFX v1.0 Release Gate

Last synchronized: 2026-09-14
Status: **OPEN / IN PROGRESS**

## Product definition

HGFX v1.0 is a functional and scientific replacement for the frozen MATLAB HGF Toolbox 8.2.0.

The v1 target is end-to-end workflow and scientific equivalence. It does not require bit-for-bit identity where floating-point/optimizer endpoint sensitivity is scientifically immaterial, but it also does not allow thresholds to be relaxed after observing a failure merely to obtain PASS.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md` for the frozen tiered equivalence rules and `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` for exact paired MATLAB limitations.

A demonstrated MATLAB-equivalent limitation may be accepted as `REFERENCE_LIMITATION_MATCH`; HGFX is not required to make MATLAB-failing cases artificially succeed. An HGFX-only divergence where MATLAB provides valid comparable output remains blocking unless a prospectively frozen accepted-equivalence protocol is satisfied.

## Mandatory acceptance criteria

- [ ] Complete MATLAB HGF Toolbox model/workflow coverage required for v1
- [ ] Fit workflow parity/equivalence under frozen policy
- [ ] Simulation workflow parity/equivalence under frozen policy
- [ ] Trajectory output parity/equivalence under frozen policy
- [ ] Hessian/LME/statistical output parity/equivalence under frozen policy
- [ ] Parameter recovery validation against the same MATLAB oracle/workflow
- [ ] Model recovery/model-selection validation against the same MATLAB oracle/workflow
- [ ] CPU/GPU numerical agreement within defined tolerances on required supported paths
- [ ] Python reproduction of required MATLAB demo workflows
- [ ] Documentation and examples sufficient for independent usage
- [ ] Aggregate evidence/provenance closure with no unknown required row
- [ ] Zero MATLAB runtime dependency for HGFX users

## Current evidence snapshot

Current work is tracked in `V1_TODO.md`; ordered dependencies are in `M18_COMPLETION_PLAN.md`; detailed current cases are in `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`.

Latest unchanged official closure evidence at implementation head `648c3f84905eb7fe952c070e5ee858e48de4a3fa`:

- M0-M17 remain completed in their documented scopes.
- D02 model-selection behavior is `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF -> AR(1) workflow is PASS (run `34763542557`).
- Exact historical 512-trial case is `REFERENCE_LIMITATION_MATCH` in its frozen scope.
- Official fit/Bayes closure run `34823572071`, job `103910417693`: **7/9 direct PASS**; `D02_fit` and `D08_fit` failed the unchanged direct gate.
- Artifact `m18-official-workflows`, ID `10339454535`, ZIP SHA-256 `78bc7ea18fc55d02d4db8738f2f805d66d4b00a21e2a5b6ad4458b4ce3e9e77b`.
- Historical M18 scientific result remains FAIL; product M18/v1 closure remains OPEN.

Current post-diagnostic interpretation:

- **D08 — IMPLEMENTED BUT NOT VALIDATED under the new acceptance path.** Focused endpoint evidence shows exact same-vector replay at the MATLAB endpoint while a tiny endpoint perturbation is amplified in derived `epsi`. It is therefore a candidate for `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`, not a reason to increase global tolerance. The prospective holdout seeds `271828182` and `314159265` were frozen before execution; workflow `M18 D08 Equivalence Holdout` is implemented and was queued as run `34826235671` at the latest synchronization.
- **D02 — BLOCKED.** It currently fails inferential equivalence: endpoint, Hessian/covariance/correlation, model evidence, predictions and residuals differ materially. A frozen cross-endpoint same-vector diagnostic (`m18-d02-basin-probe-1`) is implemented to distinguish remaining objective implementation mismatch from optimizer/numerical basin or conditioning effects. That diagnostic cannot itself close D02.

This snapshot does not check off top-level release criteria prematurely. Historical failures remain immutable evidence even if a later prospectively defined equivalence classification becomes accepted.

## Execution and decision rule

Use, in order:

1. `V1_TODO.md` for the live operational checklist;
2. `M18_COMPLETION_PLAN.md` for S1-S10 dependency order;
3. `../validation/MATLAB_EQUIVALENCE_POLICY.md` for exact/numerical/endpoint-sensitivity/inferential equivalence;
4. `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` for paired reference limitations;
5. relevant validation matrices and immutable evidence artifacts for each gate.

Required MATLAB functionality must be complete before the initial v1.0 release. “v1.x” is not permission to defer required replacement functionality past v1.0. Capabilities beyond MATLAB scope may move to v2.x.

Every required validation row needs raw, traceable evidence. Unresolved implementation, optimizer or model-selection mismatches, missing reference evidence, incomplete required demo/output surfaces, or unexecuted prospective equivalence gates block release.

### Frozen anti-post-hoc rule

Do not change thresholds, seeds, datasets, starts, grids, model family or optimizer settings after observing results to obtain PASS.

For a new equivalence rule:

1. preserve the original failed evidence;
2. diagnose and document the mechanism;
3. freeze the rule and prospective validation data/seeds before execution;
4. execute unchanged;
5. preserve PASS and FAIL outcomes alike.

Existing M18 field tolerances remain unchanged. A decimal-place-only rule is not an accepted substitute for scale-aware absolute/relative comparison.

## Accepted result semantics

- `PASS` — existing frozen direct numerical gate passed.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY` — exact contract/core inference passes and a prospectively frozen endpoint-sensitivity protocol passes without broadening the direct field tolerances.
- `PASS_INFERENTIAL_EQUIVALENCE` — a separately preregistered inferential protocol passes fit quality, parameters/identifiability, uncertainty, predictive behavior and model-comparison conclusions as applicable.
- `REFERENCE_LIMITATION_MATCH` — exact paired MATLAB limitation under the reference-limitations policy.

The latter three are explicit classifications and must not be described as bitwise equality or silently collapsed into historical direct PASS evidence.

## M18 release-validation exit conditions

- [ ] All required model families/workflows accounted for
- [ ] Required fit/simulation/trajectory/statistical outputs evidence-backed under the frozen decision policy
- [ ] Required official demo/workflow surface reproduced in Python
- [ ] Every non-direct-PASS required case has a supported primary classification and any accepted-equivalence protocol is prospectively validated
- [ ] Every accepted limitation has exact frozen MATLAB-reference evidence
- [ ] No unresolved HGFX-only implementation/optimizer/model-selection mismatch in required scope
- [ ] Paired parameter/model recovery validation completed without rewriting historical experiments
- [ ] Required robustness/backend matrix completed, including physical GPU evidence where applicable
- [ ] D10-D12 and remaining required analysis/output surfaces closed
- [ ] Aggregate evidence checker/report implemented and passing
- [ ] Clean install, examples, docs, API behavior and licenses verified
- [ ] MATLAB runtime dependency verified as zero for end users

After these conditions pass: complete M19 evidence/dataset freeze, then M20 v1.0 Candidate.

## Versioning rule

Any capability required to reproduce MATLAB HGF Toolbox workflows remains in v1.x. Scientific/performance improvements beyond the frozen MATLAB reference may be introduced separately, provided compatibility mode remains reference-faithful.