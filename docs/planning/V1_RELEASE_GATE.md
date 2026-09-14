# HGFX v1.0 Release Gate

Last synchronized: 2026-09-14
Status: **OPEN / IN PROGRESS**

## Product definition

HGFX v1.0 is a functional and scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0. Bitwise identity is not generally required, but every accepted equivalence/limitation must follow the frozen policies and preserve failed evidence. No post-hoc threshold, seed, dataset, start, grid, model-family or optimizer change may obtain PASS.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md` and `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` as acceptance policy.

## Mandatory acceptance criteria

- [ ] Complete required MATLAB model/workflow coverage
- [ ] Fit workflow parity/equivalence/reference-limitation accounting under frozen policy
- [ ] Simulation workflow parity/equivalence
- [ ] Trajectory output parity/equivalence
- [ ] Hessian/LME/statistical output parity/equivalence or exact-scope reference limitation
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
- Official direct fit/Bayes gate remains **7/9 direct PASS**; D02_fit and D08_fit remain direct failures.
- D02 exact official workflow: **REFERENCE_LIMITATION_MATCH** for release accounting; direct/inference failures preserved.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265`: **REFERENCE_LIMITATION_MATCH** for release accounting only.
- D02 model selection: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS, run `34763542557`.
- Historical exact 512 case: `REFERENCE_LIMITATION_MATCH` for that exact case.
- D09 official sampleModel workflow: PASS, run `34842943557`.
- D10/D11 analysis/output surfaces: PASS, run `34847266268`.
- D12 Bayesian parameter averaging: PASS, run `34854238549`.

### D02 — accepted exact-scope reference limitation

Decision record: `../../reference/validation/m18_d02_reference_limitation/decision.json`.

D02 remains a direct/inferential failure. Shared-state and source-level localization plus frozen MATLAB one-spacing self-sensitivity evidence establish an exact-workflow numerical-basin reference limitation. This disposition is not generalizable.

### D08 — accepted exact failed-seed reference limitation, prospective FAIL preserved

Decision record: `../../reference/validation/m18_d08_reference_limitation/decision.json`.

The prospectively frozen Level-2 holdout remains failed as a set. The exact failing seed `314159265` is release-acceptable only as `REFERENCE_LIMITATION_MATCH` because:

- repaired-product holdout run `34842943696` still fails while exact MATLAB-endpoint replay has no mismatch;
- shared-state objective/gradient and exact-state quasi-Newton transition localization classify `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`;
- after the evidence-linked prior repair, the selected source-likelihood sample reproduces the relevant observation outputs/reduction exactly;
- frozen MATLAB self-sensitivity run `34846375826` reproduces baseline exactly, then 13/14 independent one-local-spacing start perturbations leave the unchanged endpoint gate.

This is not direct parity, not Level-2 PASS, not a replacement seed, and not a tolerance relaxation.

### D09-D12 — closed workflow/output surfaces

- D09: run `34842943557`, artifact `10346184455`, SHA-256 `6c754cc02ce621c66d67224884c5347c61468cdfb6f3de81dffb03898d02b85c`.
- D10/D11: run `34847266268`, artifact `10348099156`, SHA-256 `a69045cc4e1ad388c64dec7235f8c9d2ad42f6885c6210d31b979d2284b48317`.
- D12: run `34854238549`, job `104009543024`, artifact `10352486569`, SHA-256 `14ab041b2473a13496377f63d6d1897578d1785128406eadbc1d6d44ae119883`.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: a prospectively frozen Level-2 protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited.

Historical/direct and prospective failures remain immutable evidence.

## Current release blocker sequence

1. **S7 paired parameter/model recovery** on a new frozen same-oracle protocol.
2. S8 repairs only if S7 demonstrates a required-scope HGFX-only mismatch.
3. S9 robustness/backend/physical-GPU applicability closure.
4. S10 aggregate evidence, install/examples/docs/API/licenses and no-MATLAB-runtime verification.
5. M19 evidence freeze, then M20 v1.0 candidate.

## M18/v1 exit conditions

- [ ] All required model families/workflows accounted for
- [ ] Fit/simulation/trajectory/statistical outputs evidence-backed or exact-scope reference-limitation accounted
- [ ] Official required demos/workflows reproduced/accounted under policy
- [ ] Every non-direct-PASS case has supported classification
- [ ] Every accepted limitation has exact MATLAB evidence
- [ ] No unresolved required HGFX-only implementation/optimizer/model-selection mismatch
- [ ] Paired parameter/model recovery complete
- [ ] Robustness/backend/physical-GPU applicability matrix complete
- [x] D09-D12 required output surfaces closed
- [ ] Aggregate evidence checker/report passes
- [ ] Clean install/examples/docs/API/licenses verified
- [ ] Zero MATLAB runtime dependency verified

The release remains **OPEN**. Exact-scope D02/D08 dispositions and D09-D12 completion do not close paired recovery or backend/release gates.
