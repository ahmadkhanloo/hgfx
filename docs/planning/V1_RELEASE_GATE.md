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
- D02 model selection: `PASS_MODEL_SELECTION_PARITY`.
- D04 uHGF→AR(1): PASS, run `34763542557`.
- Historical exact 512 case: `REFERENCE_LIMITATION_MATCH` for that exact case.
- D08: **BLOCKED** after failed prospective Level-2 holdout.

### D02 — accepted exact-scope reference limitation

Decision record: `../../reference/validation/m18_d02_reference_limitation/decision.json`.

Key frozen reference evidence is run `34837033370`, job `103953084600`, artifact `10344991786`, SHA-256 `9bb57f50b05d0fd2e6fb33badd265fec817c8c2308036d51d92e4f24a6e5e4ec`: the official MATLAB baseline replay is exact, while each of six independent one-local-spacing start perturbations moves the final endpoint outside the existing gate. Earlier same-vector, QN replay, optimizer-source, and source-likelihood diagnostics establish that the HGFX split occurs after shared semantics and at binary64-scale primitive/reduction residuals.

Release interpretation: D02 no longer counts as an unresolved HGFX-only mismatch in this exact official scope. It is not direct parity, not inferential PASS, and not generalizable.

### D08 — BLOCKED

The prospectively frozen Level-2 endpoint-sensitivity holdout failed. The failed seed/rules remain immutable. Focused optimizer evidence now classifies the failing path as `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`.

The previously observed USDCHF prior-input discrepancy has been repaired and independently validated exactly: run `34836421030`, job `103951169992`, artifact `10343484736`, SHA-256 `8e0028dbad33a007246e41bcf29bb54e91820b259ae9338641aa28412317c480`, classification `NO_PRIOR_DIVERGENCE`. The hard holdout still fails after that product repair, so D08 remains unresolved.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: a prospectively frozen Level-2 protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited.

Historical/direct and prospective failures remain immutable evidence.

## M18/v1 exit conditions

- [ ] All required model families/workflows accounted for
- [ ] Fit/simulation/trajectory/statistical outputs evidence-backed or exact-scope reference-limitation accounted
- [ ] Official required demos/workflows reproduced/accounted under policy
- [ ] Every non-direct-PASS case has supported classification
- [ ] Every accepted limitation has exact MATLAB evidence
- [ ] No unresolved required HGFX-only implementation/optimizer/model-selection mismatch
- [ ] Paired parameter/model recovery complete
- [ ] Robustness/backend/physical-GPU applicability matrix complete
- [ ] D09-D12 and other required output surfaces closed
- [ ] Aggregate evidence checker/report passes
- [ ] Clean install/examples/docs/API/licenses verified
- [ ] Zero MATLAB runtime dependency verified

After these: M19 evidence freeze, then M20 v1.0 Candidate.
