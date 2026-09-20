# Getting started with HGFX

HGFX v1 targets functional/scientific equivalence with the frozen MATLAB HGF Toolbox 8.2.0 reference while running as a Python package without MATLAB at user runtime.

Additive 1.1 beta helpers (opt-in MAP, VKF, dual-stream AR1, social-gaze and 3PLR softmax) are documented in `docs/user/V1_1.md`.

## Requirements

- Python 3.11 or newer
- NumPy
- JAX
- MATLAB is **not** required for ordinary HGFX use

## Install from PyPI

HGFX `1.0.0` is published on the public Python Package Index:

```bash
python -m pip install hgfx==1.0.0
```

Stable `1.0.0` does **not** include the additive 1.1 helpers. The first planned public beta is `1.1.0b1`. Once published, ordinary `python -m pip install hgfx` continues to select stable 1.0.0; opt in with `python -m pip install --pre hgfx` or pin `python -m pip install hgfx==1.1.0b1`. Before publication, use `main` or an editable checkout (`python -m pip install -e '.[optim]'`). See `docs/user/V1_1.md`.

The publication provenance and public-index verification are recorded in `docs/planning/PYPI_PUBLISHING.md`.

## Source/development install

For development or repository-level validation:

```bash
git clone https://github.com/ahmadkhanloo/hgfx.git
cd hgfx
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
```

## First fit

From a source checkout, run the maintained release smoke example:

```bash
python examples/quickstart.py
```

Equivalent minimal Python code, which also works with the PyPI installation:

```python
import numpy as np
import hgfx

u = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)
y = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)

result = hgfx.fit_model(y, u)
print(result.optim.LME)
print(result.optim.BIC)
```

## MATLAB-style compatibility API

The public package exposes both Python-first names and MATLAB-style aliases where the compatibility surface is implemented. For example:

- `hgfx.fit_model` / `hgfx.fitModel`
- `hgfx.sim_model` / `hgfx.simModel`
- `hgfx.sample_model` / `hgfx.sampleModel`

Result objects support attribute-style access and MATLAB-style export through `to_dict(matlab_style=True)`.

## GPU use

JAX-backed accelerated paths are available for the supported fast-engine surface. GPU validation claims are tracked separately from CPU equivalence; a CPU installation does not imply physical-GPU validation.

## Validation scope

HGFX preserves failed historical experiments. A shared MATLAB/HGFX scientific limitation can be release-acceptable only when the repository contains exact paired reference evidence and a scoped `REFERENCE_LIMITATION_MATCH` decision. This does not convert the underlying scientific result into PASS.
