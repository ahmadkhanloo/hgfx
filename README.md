# HGFX

**HGFX — A GPU-Native Python Toolbox for Hierarchical Gaussian Filters**

HGFX is a Python/JAX reimplementation and extension framework for the Hierarchical Gaussian Filter (HGF). The v1.0 target is functional/scientific equivalence with the frozen MATLAB HGF Toolbox 8.2.0 reference while requiring no MATLAB runtime for users.

## Current status

The `1.0.0rc1` release-candidate gate is **PASS**.

- M0–M17 are completed in their documented scopes.
- Historical M18 scientific failures remain preserved rather than retuned away.
- Exact shared MATLAB/HGFX limitations are tracked explicitly as scoped `REFERENCE_LIMITATION_MATCH` results, not scientific PASS claims.
- S9 CPU/backend is `PASS_CPU_BACKEND_EQUIVALENCE`.
- S9 physical NVIDIA GPU applicability passed on 2x Tesla T4; archived H100 results retain their original scope.
- M19 evidence freeze is complete.
- Candidate metadata is `1.0.0rc1`.
- M20 candidate finalization has passed; live evidence is recorded in `docs/planning/M20_GATE.md` and `docs/validation/V1_EVIDENCE_INDEX.md`.
- Final `1.0.0` promotion remains subject to the independent final review defined by `docs/planning/CHAT_WORKFLOW.md` and `docs/planning/FINAL_REVIEW_CHECKLIST.md` after the release candidate is frozen.

See `docs/planning/V1_RELEASE_GATE.md` and `docs/validation/V1_EVIDENCE_INDEX.md` for the live release state.

## Install

Python 3.11+ is required.

HGFX has not yet been formally published to PyPI as part of the v1 release process. Install the current release candidate from a source checkout:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

Development install:

```bash
python -m pip install -e '.[dev]'
pytest
```

After a future PyPI publication, the intended install command is `python -m pip install hgfx`.

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

## License

HGFX project code is MIT licensed. Third-party material must retain its own provenance and licensing; see `THIRD_PARTY_NOTICES.md`.
