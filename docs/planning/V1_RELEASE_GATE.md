# HGFX v1.0 Release Gate

Last synchronized: 2026-09-13
Status: **OPEN / IN PROGRESS**

## Product definition

HGFX v1.0 is a functional and scientific replacement for the frozen MATLAB HGF Toolbox 8.2.0.

The v1 target is not only numerical parity of individual algorithms. It is end-to-end workflow compatibility, including the MATLAB toolbox's model-family choices and demonstrated limitations.

A demonstrated MATLAB-equivalent limitation may be accepted as `REFERENCE_LIMITATION_MATCH`; HGFX is not required to make MATLAB-failing cases artificially succeed. An HGFX-only divergence where MATLAB provides valid comparable output remains blocking.

## Mandatory acceptance criteria

- [ ] Complete MATLAB HGF Toolbox model/workflow coverage required for v1
- [ ] Fit workflow parity
- [ ] Simulation workflow parity
- [ ] Trajectory output parity
- [ ] Hessian/LME/statistical output parity
- [ ] Parameter recovery validation against the same MATLAB oracle/workflow
- [ ] Model recovery/model-selection validation against the same MATLAB oracle/workflow
- [ ] CPU/GPU numerical agreement within defined tolerances on required supported paths
- [ ] Python reproduction of required MATLAB demo workflows
- [ ] Documentation and examples sufficient for independent usage
- [ ] Aggregate evidence/provenance closure with no unknown required row
- [ ] Zero MATLAB runtime dependency for HGFX users

## Current evidence snapshot

Current work is tracked in `V1_TODO.md`; ordered dependencies are in `M18_COMPLETION_PLAN.md`.

At tested implementation head `faf97bfdbef1333a6a756749a8ab9d6a5be102b3`:

- M0-M17 remain completed in their documented scopes.
- D02 model-selection behavior is `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF -> AR(1) workflow is PASS (run `34763542557`).
- Exact historical 512-trial case is `REFERENCE_LIMITATION_MATCH` in its frozen scope.
- Latest official fit/Bayes closure run `34763542525`, job `103740409700`: **7/9 PASS**; `D02_fit` and `D08_fit` remain blockers.
- Artifact `m18-official-workflows`, ID `10319853691`, ZIP SHA-256 `2cb5b01bce11b900261a0e309e80bf4220d63ac655417d86bf32539bf1cbf773`.
- Historical M18 scientific result remains FAIL; product M18/v1 closure remains OPEN.

This snapshot does not check off the top-level release criteria prematurely: each criterion is closed only when its full required surface and evidence package are complete.

## Execution and decision rule

Use, in order:

1. `V1_TODO.md` for the live operational checklist;
2. `M18_COMPLETION_PLAN.md` for S1-S10 dependency order;
3. `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` for non-PASS/reference-limitation classification;
4. relevant validation matrices and immutable evidence artifacts for each gate.

Required MATLAB functionality must be complete before the initial v1.0 release. “v1.x” is not permission to defer required replacement functionality past v1.0. Capabilities beyond MATLAB scope may move to v2.x.

Every required validation row needs raw, traceable evidence. Unresolved implementation, optimizer or model-selection mismatches, missing reference evidence, or incomplete required demo/output surfaces block release.

Do not change thresholds, seeds, datasets, starts, grids or model family after observing results to obtain a PASS.

## M18 release-validation exit conditions

- [ ] All required model families/workflows accounted for
- [ ] Required fit/simulation/trajectory/statistical outputs evidence-backed
- [ ] Required official demo/workflow surface reproduced in Python
- [ ] Every non-PASS required case has a supported primary classification
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
