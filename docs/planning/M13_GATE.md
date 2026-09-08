# M13 — API Compatibility Gate

Status: **PASS**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scope

M13 is an interface/consumer-compatibility milestone. It does not introduce a new
scientific inference path. Numerical fit, statistics, simulation, and sampling are
delegated to the already-validated M8-M11 compatibility core.

## Public API

Python-first:

```python
import hgfx

est = hgfx.fit_model(responses, inputs, "hgf_binary_config", "unitsq_sgm_config")
sim = hgfx.sim_model(inputs, "hgf_binary", p_prc, "unitsq_sgm", p_obs)
sam = hgfx.sample_model(inputs, "hgf_binary_config", "unitsq_sgm_config")
```

Minimal-change MATLAB-style aliases are also public:

```python
hgfx.fitModel(...)
hgfx.simModel(...)
hgfx.sampleModel(...)
```

The lower-level M11 `hgfx.compat.sim_model` / `hgfx.compat.sample_model`
functions remain unchanged for parity tooling and existing internal consumers.

## Stable result surface

`CompatibilityResult` supports attribute and dictionary-style access. The fit surface
provides `u`, `y`, `irr`, `ign`, configs, `p_prc`, `p_obs`, `traj`,
`optim`, `yhat`, and `res`. Nested result structures are `MatlabStruct`
mappings, so both `est.optim.LME` and `est.optim["LME"]` work.

`p_prc` / `p_obs` expose named native fields plus `p` and `ptrans`.
Trial indices in `irr` and `ign` are 1-based, matching MATLAB.

## Export semantics

`est.to_dict(matlab_style=True)` mirrors frozen structure placement. For fit results,
predictions and residuals are exported under `optim.yhat` / `optim.res`, as in
`fitModel.m`, while direct `est.yhat` / `est.res` remain Python convenience aliases.

## Compatibility boundary

The public M13 `fit_model` wrapper exposes the fully validated M9/M10
`hgf_binary + unitsq_sgm + quasinewton_optim` fitting slice. It deliberately rejects
other fit combinations instead of implying unvalidated generic fit orchestration.
M12 model implementations remain available through their model/config APIs.

## Acceptance tests

- public snake_case and MATLAB-style entry points import from `hgfx`;
- representative downstream consumers access named parameters, trajectories,
  model-quality statistics, predictions, and residuals without an adapter;
- `irr`/`ign` use frozen 1-based semantics;
- sim/sample result structures preserve M11 output semantics;
- MATLAB-style export preserves nested fit `optim.yhat` / `optim.res`;
- M11 raw APIs remain source-compatible;
- full Python regression remains green.

CI workflow: `.github/workflows/m13-api-compatibility.yml`.\n\nGate evidence: workflow run `34234431858` — frozen reference guard PASS; M13/API consumer suite **13 passed**; full Python regression **71 passed**.

## Gate

M13 is PASS only after the M13 workflow is green on the implementation commit and the
full regression suite passes. After PASS, the next milestone is **M14 — GPU Engine**.
