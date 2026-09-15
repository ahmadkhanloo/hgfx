# HGFX v1.0 Release Gate

Last synchronized: 2026-09-15
Status: **OPEN / IN PROGRESS**

## Product definition

HGFX v1.0 is a functional and scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0. Bitwise identity is not generally required, but every accepted equivalence/limitation must follow the frozen policies and preserve failed evidence. No post-hoc threshold, seed, dataset, start, grid, model-family or optimizer change may obtain PASS.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md` and `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md` as acceptance policy.

## Mandatory acceptance criteria

- [ ] Complete required MATLAB model/workflow coverage
- [x] Fit workflow parity/equivalence/reference-limitation accounting under frozen policy
- [x] Simulation workflow parity/equivalence in documented required scopes
- [x] Trajectory output parity/equivalence in documented required scopes
- [x] Hessian/LME/statistical output parity/equivalence or exact-scope reference limitation in documented required scopes
- [x] Paired parameter recovery against same MATLAB oracle/workflow — exact frozen S7 grid is `REFERENCE_LIMITATION_MATCH`, not scientific PASS
- [x] Paired model recovery/model-selection validation — `PASS_PAIRED_MODEL_SELECTION`, 36/36 winners match
- [ ] CPU/GPU numerical agreement on required supported paths
- [ ] Python reproduction of all required MATLAB demo workflows accepted for release surface
- [x] Independent-use documentation/examples
- [ ] Aggregate evidence/provenance closure
- [x] Zero MATLAB runtime dependency for users

## Current evidence snapshot

- M0-M17 completed in their documented scopes.
- Historical M18 scientific result: FAIL, preserved.
- Official direct fit/Bayes gate remains **7/9 direct PASS**; D02_fit and D08_fit remain direct failures.
- D02 exact official workflow: **REFERENCE_LIMITATION_MATCH** for release accounting; direct/inference failures preserved.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265`: **REFERENCE_LIMITATION_MATCH** for release accounting only.
- D09 official sampleModel workflow: PASS, run `34842943557`.
- D10/D11 analysis/output surfaces: PASS, run `34847266268`.
- D12 Bayesian parameter averaging: PASS, run `34854238549`.
- S7 paired recovery: official run `34896442847`, aggregate artifact `10370615292`, SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92`.
  - parameter recovery: **REFERENCE_LIMITATION_MATCH** in the exact frozen protocol grid;
  - model selection: **PASS_PAIRED_MODEL_SELECTION**, 36/36 BIC winners match, balanced accuracy `0.5833333333333334` in both implementations.
- S8: standard-HGF oracle defect repaired in `0239f52f772825e0a4fc74cdf3559cafa18a603e`; final S7 evidence has no unresolved required-scope implementation/optimizer/model-selection mismatch.
- S9 CPU robustness/backend: **PASS_CPU_BACKEND_EQUIVALENCE**, run `34901924475`, job `104169632034`, artifact `10371308067`, SHA-256 `875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826`.
- S9 physical GPU: **BLOCKED** pending fresh H100 revalidation of the repaired current numerical path.
- S10 release readiness: **PASS** on commit `9387017eebd104b12817075eb07a07e067baaf67`; run `34933146678`, job `104265387068`, wheel artifact `10382605498`, SHA-256 `1d6f3650ae1d48751094f9c2e0305575988661114248143fde60719215437840`.
  - static release/provenance checks PASS;
  - clean wheel build and install PASS;
  - wheel contains no MATLAB/reference runtime payload PASS;
  - public API import outside source checkout PASS;
  - maintained quickstart PASS;
  - runtime/examples compile PASS.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: a prospectively frozen Level-2 protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited. It is acceptable for v1 MATLAB-equivalence but is **not** a scientific PASS claim.

Historical/direct and prospective failures remain immutable evidence.

## S7 — accepted exact protocol reference limitation

Decision record: `../../reference/validation/m18_s7_reference_limitation/decision.json`.

The complete 12-shard paired grid contains 72 parameter-recovery cases and 36 model-recovery datasets. MATLAB and HGFX have identical criterion outcomes for HGF/eHGF/uHGF and nearly identical aggregate recovery metrics. Shared recovery failures are therefore accepted as `REFERENCE_LIMITATION_MATCH` for the exact protocol scope. All 36 BIC model-selection winners match directly.

This disposition does not change the frozen recovery thresholds and does not claim that the underlying models have passed scientific parameter-recovery criteria.

## Current release blocker sequence

1. **S9 physical-H100 applicability closure**.
2. M19 evidence freeze.
3. M20 v1.0 candidate gate.

S10 release-readiness is closed and is no longer an active blocker.

## M18/v1 exit conditions

- [ ] All required model families/workflows accounted for
- [x] Fit/simulation/trajectory/statistical outputs evidence-backed or exact-scope reference-limitation accounted in completed required scopes
- [ ] Official required demos/workflows reproduced/accounted across the final release surface
- [x] Every current non-direct-PASS fit/recovery case has a supported release classification
- [x] Every currently accepted limitation has exact MATLAB evidence
- [x] No unresolved required HGFX-only implementation/optimizer/model-selection mismatch from S7
- [x] Paired parameter/model recovery complete
- [ ] Robustness/backend/physical-GPU applicability matrix complete
- [x] D09-D12 required output surfaces closed
- [ ] Aggregate evidence checker/report passes
- [x] Clean install/examples/docs/API/licenses verified
- [x] Zero MATLAB runtime dependency verified

The release remains **OPEN**. The active blockers are fresh physical-H100 evidence, M19 evidence freeze, and M20 v1.0 candidate closure.
