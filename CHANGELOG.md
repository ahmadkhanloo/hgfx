# Changelog

All notable changes to HGFX should be documented here.

## Unreleased

### Added
- Initial repository scaffold.
- Migration planning documents.
- Numerical validation policy.
- Golden test specification.
- Methods-paper research plan.
- M13 MATLAB-compatible public result API with `CompatibilityResult` / `MatlabStruct`.
- Root-level `fit_model`, `sim_model`, `sample_model` plus `fitModel`, `simModel`, `sampleModel` aliases.
- Stable MATLAB-style `to_dict(matlab_style=True)` export with named parameters, trajectories, optimizer statistics, predictions/residuals, and 1-based trial metadata.
- M13 downstream-consumer and full-regression CI gate.
- M14 JAX fast engine with `lax.scan`, `jit`, subject/restart `vmap`, explicit device placement, compile signatures/cache, and trial bucketing.
- M14 CPU x64 parity tests against compatibility HGF/eHGF/uHGF forward trajectories and the binary-HGF + unit-square objective.
- Strict physical-GPU parity harness; M14 remains pending until that hardware test runs successfully.
- M15 differentiable MAP fitting over the fast binary-HGF + unit-square objective.
- M15 optimizer abstraction and JAX BFGS backend with device-resident optimizer arrays.
- M15 CPU gradient/final-objective/trajectory parity tests and strict physical-GPU fitting parity harness.
- M16 subject/restart batch engine with shape scheduler, nested vmap fitting, heterogeneous-length masking, compile-cache reuse, and single-vs-batch equivalence gates.
