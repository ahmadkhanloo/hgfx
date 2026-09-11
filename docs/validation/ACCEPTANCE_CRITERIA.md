# Acceptance Criteria

## Component acceptance

A migrated mathematical component is accepted only if:

- [ ] Source file(s) identified
- [ ] Equations documented
- [ ] Inputs/outputs documented
- [ ] Branches documented
- [ ] Edge cases documented
- [ ] Golden fixture exists
- [ ] CPU x64 passes
- [ ] GPU x64 passes if GPU-critical
- [ ] No unexplained mismatch remains
- [ ] Migration Matrix status updated
- [ ] Provenance recorded

## Release acceptance

- [ ] 100% frozen source manifest classified
- [ ] P0/P1 perceptual models covered
- [ ] all targeted observation families covered
- [ ] config/transform/name parity
- [ ] fitModel compatibility
- [ ] sim/sample compatibility
- [ ] Hessian/covariance/correlation
- [ ] AIC/BIC/LME
- [ ] CPU x64
- [ ] GPU x64
- [ ] batch/single equivalence
- [ ] parameter recovery
- [ ] model recovery
- [ ] custom model API documented
- [ ] reproducible benchmarks
- [ ] runtime MATLAB dependency = 0
- [ ] third-party notices complete

## MATLAB-equivalence closure requirements — 2026-09-11

Follow [R0–R6](../planning/MATLAB_PARITY_RECOVERY_PLAN.md). These are additional evidence requirements, not a relaxation of the checklists above.

- [ ] Corrected M18B final artifact validated from complete raw records.
- [ ] Historical 512-trial failure reproduced against frozen MATLAB; first divergence or shared reference limitation documented.
- [ ] Failed M18 datasets compared in both runtimes using identical inputs, responses, parameters, priors and starts.
- [ ] Objective, trajectories, fit statistics and model decisions compared with preregistered field-specific tolerances.
- [ ] Scientific family/config/regime/backend claims mapped to evidence; coverage gaps remain open.
- [ ] Conditional/oracle diagnostics are not presented as joint identifiability.
- [ ] Changed scientific paths revalidated on physical GPU before GPU claims.
- [ ] Historical M18 FAIL and thresholds preserved; any successor protocol explicitly versioned and independently evaluated.

Shared MATLAB/Python recovery failure may establish a model/design limitation, but does not make the original M18 pass. Any change to release scientific criteria needs an explicit reviewed decision with paired evidence; this plan grants no exception.
