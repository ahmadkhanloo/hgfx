# HGFX v1 public API

This page documents the release-facing public API exported by `hgfx`.

Additive 1.1 beta helpers (MAP, VKF, dual-stream, project softmax) are documented with copy-paste usage in `docs/user/V1_1.md`. They are not part of the frozen MATLAB compatibility contract.

## Configuration

### `hgfx.enable_x64()`

Enable JAX 64-bit mode for workflows that require the validated numerical precision policy.

## Fit, simulation and sampling

### `hgfx.fit_model(...)`

Python-first fitting API. The validated compatibility surface includes the frozen MATLAB-equivalent workflows documented in the repository validation matrix.

MATLAB-style alias: `hgfx.fitModel(...)`.

Opt-in MAP on the same objective, different optimizer: `hgfx.optim.fit_map` / `hgfx.optim.minimize_map`. See `docs/user/V1_1.md`.

### `hgfx.sim_model(...)`

Python-first simulation API returning a compatibility result object.

MATLAB-style alias: `hgfx.simModel(...)`.

### `hgfx.sample_model(...)`

Python-first prior-predictive/sample-model API.

MATLAB-style alias: `hgfx.sampleModel(...)`.

## Bayesian parameter averaging

### `hgfx.bayesian_parameter_average(...)`

Bayesian parameter averaging surface validated in D12.

## Analysis/plotting surfaces

- `hgfx.fit_plot_corr(...)`
- `hgfx.fit_plot_residual_diagnostics(...)`
- MATLAB-style aliases `fit_plotCorr(...)` and `fit_plotResidualDiagnostics(...)`

Plotting requires the optional `plot` dependency:

```bash
python -m pip install 'hgfx[plot]'
```

## Result objects

Public workflows return `hgfx.CompatibilityResult` objects. Their fields preserve the documented MATLAB-style structure while remaining Python-accessible. `MatlabStruct` supports both mapping and attribute access.

Use:

```python
result.to_dict(matlab_style=True)
```

when a MATLAB-shaped dictionary is required by downstream compatibility code.

## Stability and validation

Public availability does not imply that every arbitrary model/configuration combination has identical validation strength. The authoritative supported/release surface is the current `docs/validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md` plus the v1 release gate and scoped limitation records.
