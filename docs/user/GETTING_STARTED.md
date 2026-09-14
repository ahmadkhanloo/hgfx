# Getting started with HGFX

HGFX v1 targets functional/scientific equivalence with the frozen MATLAB HGF Toolbox 8.2.0 reference while running as a Python package without MATLAB at user runtime.

## Requirements

- Python 3.11 or newer
- NumPy
- JAX
- MATLAB is **not** required for ordinary HGFX use

## Install from a source checkout

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

For development/testing:

```bash
python -m pip install -e '.[dev]'
pytest
```

## First fit

Run the maintained release smoke example:

```bash
python examples/quickstart.py
```

Equivalent minimal Python code:

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
