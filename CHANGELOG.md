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

## 1.0.0 — 2026-09-16

### Released
- First stable HGFX release on PyPI with Python 3.11+ support.
- MATLAB-compatible fitting, simulation, sampling, statistical outputs, and public Python/MATLAB-style aliases in the documented v1 scope.
- Classic HGF, eHGF, uHGF, and specialized validated workflows covered by the frozen v1 migration/evidence matrix.
- JAX CPU/GPU execution paths, batch infrastructure, and explicit device-placement support.
- Frozen MATLAB HGF Toolbox 8.2.0 compatibility oracle and machine-readable validation evidence.
- Historical recovery failures and matched reference limitations retained explicitly rather than reclassified.
- Release source: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; tag: `v1.0.0`.

## M18B evidence integrity

- Reject incomplete/duplicate/nonfinite raw recovery records and inconsistent summaries.
- Verify archived M18 FAIL bytes and unchanged protocol source hashes.
- Rename the unsupported identifiable-recovery label to low-error recovery.
- Archive per-dataset profiles, inputs, failures and reproducibility metadata;
  checkpoint incomplete runs and distinguish smoke execution from final PASS.
