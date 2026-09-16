# Full MATLAB `hgf_demo.m` Coverage in HGFX

This document maps the frozen HGF Toolbox 8.2.0 demo at commit `2437f4dc241541072722a2695ddeca7b44d83dd3` to the Python v1 release candidate.

The user-facing Python companion is:

```bash
python examples/hgf_demo_full.py
```

It follows the computational sequence of the official MATLAB `demo/hgf_demo.m`. Plotting is optional (`--plots`) because release parity is judged on numerical data surfaces, trajectories, parameters and fit diagnostics rather than pixel identity.

## Coverage matrix

| MATLAB demo section | HGFX Python surface | Cross-language evidence | v1 disposition |
| --- | --- | --- | --- |
| load `example_binary_input.txt` | NumPy load in `hgf_demo_full.py` | same frozen file/submodule | COVERED |
| Bayes-optimal binary HGF | `fit_model(None, ..., hgf_binary_config, bayes_optimal_binary_config)` | official direct gate `D01_bayes` | PASS |
| binary `hgf_binary + unitsq_sgm` simulation | `sim_model(...)` | M11 simulation parity + official workflow evidence | PASS |
| recover binary HGF parameters | `fit_model(sim.y, sim.u, ...)` | official fit/recovery gates; historical recovery limitations remain separately disclosed | COVERED / reference-aware |
| parameter Corr/Sigma | `optim.Corr`, `optim.Sigma`, `prepare_fit_correlation_surface` | D10 | PASS |
| posterior parameter vectors | `p_prc`, `p_obs` | compatibility/API and official fit gates | PASS in validated scopes |
| inferred trajectories | `traj` | HGF forward + official fit gates | PASS in validated scopes |
| edit observation prior + `align_priors` | immutable `ModelConfig`/`ParameterSpec` replacement; `priorsas` is computed immediately | M2 config parity | PYTHON-EQUIVALENT API |
| `sampleModel` prior-predictive examples | `sample_model(...)` | D09 official sampleModel | PASS |
| enhanced HGF challenge | `ehgf_binary` simulation + fit | current `M18 Demo Model Selection Parity` | `PASS_MODEL_SELECTION_PARITY` |
| unbounded HGF binary | `uhgf_binary` simulation + fit | M6 + official workflow evidence | PASS in validated scopes |
| high-volatility uHGF | `uhgf_binary` with official parameter vector | official demo workflow evidence | PASS |
| uHGF-AR(1) regularization | `uhgf_ar1_binary` validated forward path | current `M18 Demo uHGF AR1 Workflow Parity` | `PASS_UHGF_AR1_WORKFLOW_PARITY` |
| Rescorla-Wagner fit | `rw_binary_config` through `fit_model` | specialized model / official workflow coverage | PASS in documented scope |
| load USD/CHF continuous input | NumPy load of frozen `example_usdchf.txt` | same frozen file/submodule | COVERED |
| Bayes-optimal continuous HGF | `fit_model(None, ..., hgf_config, bayes_optimal_config)` | official direct gate `D06_bayes` | PASS |
| continuous two-level HGF simulation | `sim_model(..., hgf, gaussian_obs, ...)` | continuous model/observation parity gates | PASS in documented scope |
| add third HGF level | direct validated `hgf(...)` forward with official 15-parameter vector | HGF forward parity / specialized coverage | COVERED |
| continuous HGF parameter recovery | `fit_model(... hgf_config, gaussian_obs_config)` | official direct fit matrix | reference-aware disposition |
| continuous eHGF | `sim_model` + `fit_model` | eHGF forward / official workflow coverage | PASS in documented scope |
| continuous uHGF | `sim_model` + `fit_model` | uHGF forward / official workflow coverage | PASS in documented scope |
| residual diagnostics | `prepare_residual_diagnostics` / `fit_plot_residual_diagnostics` | D11 | PASS |
| second fictive continuous agent | `sim_model` + `fit_model` | same validated continuous surfaces | COVERED |
| Bayesian parameter averaging | `bayesian_parameter_average(est2, est2b)` | D12 | PASS |

## Exact current demo comparisons

### Enhanced-HGF challenge

Validated HGFX revision before the full-demo wrapper was added: `a16d81f7472a0d2d185ef2d70e0ba37b9149dd85`.

GitHub Actions run `35031481382` returned:

```text
PASS_MODEL_SELECTION_PARITY
mismatches=[]
```

Observed behavior:

| Implementation | classic HGF | eHGF |
| --- | --- | --- |
| MATLAB 8.2.0 | negative-posterior-precision failure | success |
| HGFX | negative-posterior-precision failure | success |

The Python user-facing example reported 320 trials and eHGF trajectory shape `(320, 3)`.

### uHGF to uHGF-AR(1)

GitHub Actions run `35031481302` returned:

```text
PASS_UHGF_AR1_WORKFLOW_PARITY
mismatches=[]
```

Descriptive trajectory values were identical in both implementations:

| Quantity | MATLAB 8.2.0 | HGFX |
| --- | ---: | ---: |
| uHGF max absolute level-3 posterior mean | `16.99162398501939` | `16.99162398501939` |
| uHGF-AR(1) max absolute level-3 posterior mean | `4.0927117005012175` | `4.0927117005012175` |

The actual checker compares the complete release-relevant trajectories/inference states at the frozen tolerances `rtol=5e-11`, `atol=5e-13`; the two values above are only readable summary values.

## Why the full demo uses composite evidence

The MATLAB demo intentionally combines many different capabilities in one educational script. Re-running a second monolithic parity oracle would duplicate several expensive gates and make failures harder to classify.

HGFX instead uses one user-facing Python companion plus the already-frozen specialized gates for each numerical surface. This preserves diagnostic separation:

- config parity is not confused with optimizer parity;
- simulation parity is not confused with stochastic RNG identity;
- plotting parity is checked on data surfaces, not pixels;
- historical recovery failures remain visible;
- exact MATLAB limitations remain `REFERENCE_LIMITATION_MATCH` rather than being rewritten as scientific PASS.

## Stochastic sections

MATLAB and NumPy/JAX do not use the same random stream implementation. A matching numeric seed therefore does not imply byte-identical simulated responses.

For exact cross-language validation, HGFX supports injected/exported uniform or standard-normal draws. The official gates use that mechanism where exact stochastic comparison is required. In the standalone educational demo, seeds are retained to make the Python run locally reproducible, but response samples should not be compared element-by-element with MATLAB solely on the basis of the integer seed.

## Running the full Python demo

```bash
git submodule update --init --recursive
python -m pip install .
python examples/hgf_demo_full.py --output hgf_demo_python_summary.json
```

Optional figures:

```bash
python -m pip install '.[plot]'
python examples/hgf_demo_full.py --plots
```

The script prints section progress and a machine-readable summary. The summary is intended for reproducibility and regression review; authoritative MATLAB equivalence remains the frozen validation evidence indexed in `docs/validation/V1_EVIDENCE_INDEX.md`.

## Release interpretation

Successful execution of the full Python demo means that the v1 public/validated surfaces compose into the same educational workflow as the MATLAB toolbox. It does **not** mean that every parameter-recovery case is scientifically identifiable. The historical M18 scientific FAIL and exact-scope reference limitations remain part of the v1 record.
