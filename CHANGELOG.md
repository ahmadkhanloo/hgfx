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
