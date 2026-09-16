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

## Release acceptance template (historical checklist)

The checkboxes below define the original checklist, not live milestone status.
Current v1 acceptance and scoped MATLAB limitations are recorded in
[the release gate](../planning/V1_RELEASE_GATE.md) and
[the evidence index](V1_EVIDENCE_INDEX.md). Historical recovery FAIL is not
converted into scientific PASS by product equivalence accounting.


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
