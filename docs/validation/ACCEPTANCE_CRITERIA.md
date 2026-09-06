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
