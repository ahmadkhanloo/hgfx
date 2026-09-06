# Final Independent Review Checklist

The final reviewer must assume the implementation may contain subtle scientific errors.

## Review scope

### Source coverage
- [ ] Every frozen MATLAB source file classified
- [ ] No unexplained `TODO` in migration-critical paths
- [ ] Every model family accounted for
- [ ] Every observation family accounted for

### Mathematical fidelity
- [ ] Equations match reference semantics
- [ ] Parameter ordering verified
- [ ] Priors verified
- [ ] Transforms verified
- [ ] Fixed/free semantics verified
- [ ] Irregular trials verified
- [ ] Placeholder semantics verified

### Numerical validation
- [ ] Golden fixtures reproducible
- [ ] CPU x64 parity
- [ ] GPU x64 parity
- [ ] First-divergence tooling exists
- [ ] Tolerances scientifically justified
- [ ] No suspicious tolerance inflation

### Fitting
- [ ] Objective-at-fixed-theta parity
- [ ] Compatibility optimizer tested
- [ ] Fast optimizer scientifically equivalent
- [ ] Multi-start behavior tested
- [ ] Failure behavior tested

### Model evidence
- [ ] Parameter recovery
- [ ] Model recovery
- [ ] Edge-case sweeps
- [ ] Long-sequence stability

### GPU
- [ ] Data stays on device in hot loop
- [ ] Batch == repeated single
- [ ] Compilation behavior documented
- [ ] VRAM behavior documented
- [ ] Multi-GPU tested if claimed

### Publication evidence
- [ ] Benchmark protocol frozen before final runs
- [ ] Raw benchmark outputs archived
- [ ] Exact hardware/software recorded
- [ ] Statistical analysis reproducible
- [ ] Figures generated from scripts
- [ ] Manuscript claims trace to artifacts

### Licensing
- [ ] Third-party notices complete
- [ ] Copied/adapted code provenance complete
- [ ] No incompatible license contamination

## Reviewer output format

Each finding must be labeled:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFO
```

For each finding:
- file/path;
- issue;
- scientific/engineering impact;
- reproduction steps;
- proposed fix;
- whether it blocks release.
