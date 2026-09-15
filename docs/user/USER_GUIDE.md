# HGFX v1 User Guide

HGFX is the Python/JAX implementation of the Hierarchical Gaussian Filter family validated against the frozen MATLAB HGF Toolbox 8.2.0 reference at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`.

The v1 product goal is practical MATLAB-toolbox-equivalent use without requiring MATLAB at runtime. MATLAB remains a development and validation oracle only.

## 1. Installation

HGFX requires Python 3.11 or newer.

### Current release candidate

Until the package is formally published to PyPI, install it from a source checkout:

```bash
git clone --recurse-submodules https://github.com/ahmadkhanloo/hgfx.git
cd hgfx
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

For development:

```bash
python -m pip install -e '.[dev]'
pytest
```

After a future PyPI publication, the intended installation form is simply:

```bash
python -m pip install hgfx
```

Do not assume that command is available until a PyPI release has actually been published.

## 2. The basic mental model

If you know the MATLAB HGF Toolbox, the HGFX workflow is deliberately familiar:

| Task | HGFX Python-first API | MATLAB-style HGFX alias |
| --- | --- | --- |
| Fit a model | `hgfx.fit_model(...)` | `hgfx.fitModel(...)` |
| Simulate from supplied parameters | `hgfx.sim_model(...)` | `hgfx.simModel(...)` |
| Sample from configured priors | `hgfx.sample_model(...)` | `hgfx.sampleModel(...)` |
| Bayesian parameter averaging | `hgfx.bayesian_parameter_average(...)` | — |

The aliases are compatibility conveniences. New Python projects should normally prefer snake_case names.

## 3. Enable 64-bit JAX numerics

The MATLAB reference is double precision. Enable JAX x64 near program startup when using JAX-backed fitting/GPU paths:

```python
import hgfx

hgfx.enable_x64()
```

The NumPy compatibility paths also use `float64` arrays.

## 4. First model fit

```python
import numpy as np
import hgfx

hgfx.enable_x64()

u = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)
y = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)

result = hgfx.fit_model(y, u)

print("LME:", result.optim.LME)
print("BIC:", result.optim.BIC)
print("AIC:", result.optim.AIC)
print("fitted perceptual parameters:", result.p_prc)
print("fitted observation parameters:", result.p_obs)
```

The default fit is the validated binary-HGF + unit-square sigmoid observation workflow.

The equivalent explicit call is:

```python
result = hgfx.fit_model(
    y,
    u,
    "hgf_binary_config",
    "unitsq_sgm_config",
    "quasinewton_optim_config",
)
```

The MATLAB-style alias is also available:

```python
result = hgfx.fitModel(
    y,
    u,
    "hgf_binary_config",
    "unitsq_sgm_config",
    "quasinewton_optim_config",
)
```

## 5. Reading the fit result

HGFX returns MATLAB-like result surfaces while still behaving naturally in Python.

Common fields include:

```python
result.traj          # perceptual trajectories
result.optim.LME     # log model evidence approximation
result.optim.AIC
result.optim.BIC
result.optim.negLl
result.optim.negLj
result.optim.H       # Hessian
result.optim.Sigma   # covariance estimate
result.optim.Corr    # parameter correlation matrix
result.yhat          # predicted responses
result.res           # residuals
result.p_prc         # fitted perceptual parameters
result.p_obs         # fitted observation parameters
```

To obtain a MATLAB-style nested dictionary:

```python
matlab_like = result.to_dict(matlab_style=True)
```

This is useful when migrating existing analysis code or comparing serialized results across MATLAB and Python.

## 6. Supplying project data

For binary workflows, `u` is normally a one-dimensional input sequence or a compatible array whose first column contains the observations supplied to the perceptual model.

`y` contains behavioral responses used by the observation model during fitting.

Use explicit floating-point arrays:

```python
u = np.asarray(my_inputs, dtype=np.float64)
y = np.asarray(my_responses, dtype=np.float64)
```

`NaN` trials retain the frozen MATLAB ignored-trial semantics in the validated compatibility paths. Irregular-interval behavior is model/config dependent; use the corresponding configuration and validation matrix rather than assuming every model treats timing identically.

## 7. Simulation with known parameters

`sim_model` mirrors the validated `simModel` orchestration for supported binary-HGF variants.

Example using a native-space eHGF parameter vector:

```python
import numpy as np
import hgfx

u = np.asarray([0, 1, 1, 0, 1, 0], dtype=np.float64)
p = np.asarray(
    [np.nan, 0, 1, np.nan, 1, 1, np.nan, 0, 0, 1, 1.5, np.nan, -4, 3],
    dtype=np.float64,
)

sim = hgfx.sim_model(u, "ehgf_binary", p)
print(sim.trajectory["mu"])
```

An observation model can also be supplied where supported so that simulated responses are returned together with the perceptual trajectory.

## 8. Prior-predictive sampling

Use `sample_model` when the workflow should draw parameters from model priors:

```python
import numpy as np
import hgfx

u = np.asarray([0, 1, 1, 0, 1, 0], dtype=np.float64)

sample = hgfx.sample_model(
    u,
    perceptual_config="ehgf_binary_config",
    observation_config="unitsq_sgm_config",
    seed=1234,
)

print(sample.perceptual_parameters)
print(sample.responses)
```

Random streams are reproducible within the HGFX seed contract, but NumPy and MATLAB random generators are not claimed to be byte-identical. Exact cross-language stochastic validation injects the same exported random draws when required.

## 9. Model comparison

Fit competing models to the same data and compare statistics from `result.optim`, especially BIC/LME when appropriate for the scientific design.

```python
fit_a = hgfx.fit_model(y, u, "hgf_binary_config", "unitsq_sgm_config")
fit_b = hgfx.fit_model(y, u, "ehgf_binary_config", "unitsq_sgm_config")

print(fit_a.optim.BIC, fit_b.optim.BIC)
```

Do not interpret a lower BIC or higher LME without considering the experimental design and the documented limitations of the candidate model family.

## 10. Bayesian parameter averaging

For release-supported compatible fit results:

```python
bpa = hgfx.bayesian_parameter_average(results)
```

See `docs/user/API.md` for the exact accepted input surface and returned fields.

## 11. Plotting and diagnostics

Install the plotting extra when needed:

```bash
python -m pip install '.[plot]'
```

HGFX exposes release-supported fit diagnostics, including residual and parameter-correlation plotting helpers. Keep numerical analysis separate from presentation code so that plots do not become part of scientific acceptance criteria.

## 12. GPU use

HGFX uses JAX for accelerated fitting paths. Install a JAX build appropriate for the target CUDA/runtime environment, then confirm the physical device rather than assuming GPU execution from a mocked backend.

A minimal device check is:

```python
import jax
import hgfx

hgfx.enable_x64()
print(jax.devices())
```

The v1 release evidence includes physical NVIDIA validation. Numerical applicability and multi-GPU performance are different claims; consult the validation evidence for the exact scope of each result.

## 13. How close is usage to the MATLAB toolbox?

The intended migration pattern is close:

1. choose a perceptual configuration;
2. choose an observation configuration;
3. fit, simulate, or sample;
4. inspect trajectories and fit statistics;
5. compare candidate models;
6. perform diagnostics.

The important differences are Python conventions:

- arrays are NumPy/JAX arrays rather than MATLAB matrices;
- Python uses zero-based indexing internally;
- snake_case APIs are preferred, with MATLAB-style aliases available;
- exceptions replace MATLAB error identifiers at the Python boundary;
- GPU execution is JAX based;
- MATLAB is not needed in a deployed HGFX project.

The compatibility layer intentionally keeps familiar field names such as `traj`, `optim`, `LME`, `AIC`, and `BIC` where that improves migration.

## 14. Official MATLAB demo reproductions

From a repository checkout with the frozen MATLAB toolbox submodule initialized:

```bash
git submodule update --init --recursive
python -m pip install .
python examples/matlab_demo_model_selection.py
python examples/matlab_demo_uhgf_ar1.py
```

These scripts use the exact official `demo/example_binary_input.txt` and native parameter vectors from the frozen `demo/hgf_demo.m` workflows covered by the v1 release gate.

For the side-by-side MATLAB/HGFX results, tolerances, workflow run IDs, and exact reproduction commands, see:

- `docs/user/MATLAB_DEMOS.md`

## 15. Validation scope and scientific limitations

HGFX v1 is not described as "every HGF model works scientifically for every parameter regime." The frozen MATLAB toolbox itself has regimes where the variational approximation fails or recovery is limited.

HGFX therefore distinguishes:

- direct numerical/behavioral parity;
- workflow parity;
- reference limitation matches;
- historical scientific failures;
- implementation failures.

For example, the official eHGF challenge intentionally uses a parameter region where classic HGF fails and eHGF succeeds. HGFX reproduces that behavior rather than modifying the algorithm until classic HGF passes.

Before relying on a specialized model in a publication, inspect:

- `docs/validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`
- `docs/validation/V1_EVIDENCE_INDEX.md`
- `docs/validation/MATLAB_EQUIVALENCE_POLICY.md`
- `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`

## 16. Recommended project pattern

A normal downstream project should depend on HGFX rather than copying its source:

```text
my-project/
├── pyproject.toml
├── src/
├── tests/
└── analyses/
```

Import HGFX in analysis/application code:

```python
import hgfx

hgfx.enable_x64()
result = hgfx.fit_model(y, u)
```

Pin a specific HGFX version for reproducible research. Once v1.0 is formally released, prefer a version constraint such as `hgfx==1.0.0` rather than tracking a moving branch.

## 17. What to cite and archive for reproducibility

For a scientific project, record at least:

- HGFX version;
- HGFX commit SHA when using an unreleased candidate;
- Python version;
- NumPy/JAX versions;
- CPU/GPU hardware when relevant;
- perceptual/observation configuration names;
- parameter vectors or priors;
- optimizer settings;
- random seeds/draws when stochastic paths are used;
- input dataset version/checksum.

That information is sufficient for another researcher or agent to reconstruct the exact analysis environment much more reliably than an unpinned source checkout.
