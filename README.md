# HGFX

**HGFX — A GPU-Native Python Toolbox for Hierarchical Gaussian Filters**

HGFX is a Python/JAX reimplementation and extension framework for the Hierarchical Gaussian Filter (HGF). The v1.0 target is functional/scientific equivalence with the frozen MATLAB HGF Toolbox 8.2.0 reference while requiring no MATLAB runtime for users.

## Current status

**HGFX v1.0.0 is released and published on PyPI.**

- PyPI: https://pypi.org/project/hgfx/1.0.0/
- Public install: `python -m pip install hgfx==1.0.0`
- Published release: https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0
- Release ID: `389966452`
- Immutable v1.0.0 source target: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- Git tag `v1.0.0` is verified to resolve directly to that exact commit.
- PyPI publication used Trusted Publishing / GitHub OIDC; publish workflow run `35207257208` passed.
- Independent public-PyPI clean-install verification run `35207903084` passed on Python 3.12.14.
- M0–M17 are completed in their documented scopes.
- Historical M18 scientific failures remain preserved rather than retuned away.
- Exact shared MATLAB/HGFX limitations are tracked explicitly as scoped `REFERENCE_LIMITATION_MATCH` results, not scientific PASS claims.
- S9 CPU/backend is `PASS_CPU_BACKEND_EQUIVALENCE`.
- S9 physical NVIDIA GPU applicability passed on 2x Tesla T4; archived H100 results retain their original scope.
- M19 evidence freeze is complete.
- M20 candidate finalization passed as `PASS_M20_CANDIDATE`.
- The independent frontier review completed; release-blocking H1/H2 findings were resolved without changing frozen scientific criteria.
- Final package and citation metadata are `1.0.0`.
- PR #30 head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b` passed all active promotion gates: S10 `35089882319`, M19/M20 preflight `35089882608`, D10/D11 `35089882668`, and HGFX Regression `35089882392`.
- PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; main HGFX Regression run `35090329868` passed on Ubuntu and Windows.

The v1.0.0 release gate is closed. The immutable release source and frozen evidence are `4dd8fbd8`.

`main` also carries the active additive **1.1.0** development line (`pyproject.toml`) for opt-in MAP, VKF, dual-stream AR1, and project softmax helpers. v1.1.0 preserves the frozen `fit_model` compatibility path but is **not yet released**: it is not on PyPI and has no GitHub release tag. Usage: `docs/user/V1_1.md`; release policy: `docs/planning/V1_1_RELEASE_PLAN.md`.

See `docs/planning/V1_RELEASE_GATE.md`, `docs/validation/V1_EVIDENCE_INDEX.md`, `docs/validation/V1_FINAL_RELEASE_PROVENANCE.md`, and `docs/planning/PYPI_PUBLISHING.md` for release and distribution evidence.

## Install

Python 3.11+ is required.

Install the released package from PyPI:

```bash
python -m pip install hgfx==1.0.0
```

For a source checkout or development install:

```bash
git clone https://github.com/ahmadkhanloo/hgfx.git
cd hgfx
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
```

MATLAB is a development-time reference oracle only; it is not a user runtime dependency.

## Quick start

```bash
python examples/quickstart.py
```

Or directly:

```python
import numpy as np
import hgfx

u = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)
y = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=float)

result = hgfx.fit_model(y, u)
print(result.optim.LME)
print(result.optim.BIC)
```

The public compatibility surface includes Python-first and MATLAB-style aliases such as `fit_model`/`fitModel`, `sim_model`/`simModel`, and `sample_model`/`sampleModel`.

User documentation:

- `docs/user/GETTING_STARTED.md` — minimal installation and first fit
- `docs/user/USER_GUIDE.md` — practical v1 guide for fitting, simulation, sampling, GPU use, migration from MATLAB, and reproducibility
- `docs/user/API.md` — public API surface
- `docs/user/V1_1.md` — additive 1.1.0 usage (MAP, VKF, dual-stream, project softmax)
- `docs/user/MATLAB_DEMOS.md` — exact official MATLAB demo reproductions and cross-language parity evidence
- `examples/README.md` — runnable examples

## Official MATLAB demo reproductions

With the frozen reference submodule initialized:

```bash
git submodule update --init --recursive
python examples/matlab_demo_model_selection.py
python examples/matlab_demo_uhgf_ar1.py
```

The corresponding CI workflows regenerate the real MATLAB outputs and compare them with HGFX at frozen tolerances. See `docs/user/MATLAB_DEMOS.md` for exact results and evidence IDs.

## Scope

HGFX provides:

- HGF/eHGF/uHGF and specialized model implementations covered by the migration plan;
- MATLAB-compatible fit, simulation, sampling and statistical output surfaces in documented validated scopes;
- JAX-based fast CPU/GPU paths;
- batch and multi-GPU infrastructure;
- parameter/model recovery and validation tooling;
- explicit provenance for direct PASS, numerical/inferential equivalence and reference limitations.

Bitwise identity across hardware is not a general requirement. Acceptance is governed by the frozen equivalence policies and release gate; thresholds, seeds, datasets, starts, grids, model families and optimizers are not changed post-hoc to manufacture PASS results.

## Reference implementation

The frozen MATLAB toolbox is retained only as a validation oracle. The product runtime goal is:

```text
MATLAB dependency = 0
```

## Core project documents

- `docs/planning/V1_RELEASE_GATE.md`
- `docs/planning/M18_COMPLETION_PLAN.md`
- `docs/planning/ROADMAP.md`
- `docs/planning/MILESTONES.md`
- `docs/validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`
- `docs/validation/MATLAB_EQUIVALENCE_POLICY.md`
- `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
- `docs/validation/V1_EVIDENCE_INDEX.md`
- `docs/validation/V1_FINAL_RELEASE_PROVENANCE.md`
- `docs/planning/PYPI_PUBLISHING.md`

## License

HGFX project code is MIT licensed. Third-party material must retain its own provenance and licensing; see `THIRD_PARTY_NOTICES.md`.
