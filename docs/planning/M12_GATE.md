# M12 — Specialized Model Coverage Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Passing workflow run: `34188815550`
- Numerical mode: CPU float64

## Gate definition

M12 passes when every frozen perceptual/observation family has an explicit final migration status and the specialized families ported into HGFX are validated against canonical frozen MATLAB sources.

Accepted final family states for this gate:

- `DONE`: a compatibility implementation exists and is parity-gated.
- `REFERENCE_ONLY`: the family is explicitly inventoried, intentionally not claimed compatible, and has a concrete scientific/architectural reason.

No frozen perceptual or observation file may remain unclassified.

## Exhaustive inventory

Machine gate:

`tools/check_m12_inventory.py`

Passing result:

- DONE files: **146**
- REFERENCE_ONLY files: **113**
- DONE families: **32**
- REFERENCE_ONLY families: **21**
- unclassified frozen perceptual/observation files: **0**

Detailed family-level reasoning is recorded in:

`docs/planning/M12_COVERAGE.md`

## Specialized families implemented and parity-gated in M12

### Unified HGF variants

- [x] binary PU HGF
- [x] binary PU eHGF
- [x] binary PU uHGF
- [x] binary PU-TBT HGF
- [x] binary PU-TBT eHGF
- [x] binary PU-TBT uHGF
- [x] AR1 binary HGF
- [x] AR1 binary eHGF
- [x] AR1 binary uHGF

### Legacy / independent perceptual models

- [x] Rescorla-Wagner binary
- [x] dual Rescorla-Wagner
- [x] Pearce-Hall binary
- [x] Sutton K1 binary
- [x] scalar Kalman filter
- [x] HMM

The Python public surface is exported through `hgfx.models`.

## Explicit REFERENCE_ONLY families

The following remain available as frozen scientific references but HGFX v1 compatibility does not claim implementations for them:

- continuous AR1 HGF
- binary/continuous MAB variants
- AR1 binary MAB HGF/eHGF/uHGF
- JGET HGF/eHGF/uHGF
- categorical / categorical-normalized HGF
- WhatWorld / WhichWorld
- HHMM
- Bayes-optimal auxiliary families
- response-surprise auxiliary families
- squared prediction-error auxiliary
- conditional-hallucination observation families
- world-specific logRT / softmax observation families

Every one has an explicit reason in `M12_COVERAGE.md`.

## MATLAB/Python golden validation

The M12 oracle compares:

- `infStates`
- every exported trajectory field
- regular and ignored-trial state-copy behavior
- native fixed parameter recursion

Validated cases:

- HGF/eHGF/uHGF binary PU
- HGF/eHGF/uHGF binary PU-TBT
- HGF/eHGF/uHGF AR1 binary
- RW
- dual RW
- Pearce-Hall
- Sutton K1
- Kalman
- HMM

Numerical checker:

- `rtol=5e-10`
- `atol=5e-12`

No tolerance was widened to close a mismatch.

## Source issues caught by M12

### Canonical path shadowing

The first MATLAB comparison exposed the same class of reference-path hazard seen in M4: `genpath` could resolve frozen `_original_models/hgf_binary_pu.m` before the canonical unified implementation.

The oracle was fixed by explicitly adding only canonical directories:

- `core/`
- `building_blocks/`
- `perceptual/`
- `observation/`
- `utilities/`

No Python scientific equation or numerical tolerance was changed.

### Sutton K1 cleanup quirk

Frozen `sutton_k1_binary.m` executes `be(end)=[]` twice during result cleanup. HGFX preserves the resulting shorter `traj.be` rather than silently normalizing it.

## PyHGF decision gate

**PASS — do not fork PyHGF, and do not make PyHGF a required compatibility-core runtime dependency.**

Evidence through M12 shows that HGFX now owns a directly MATLAB-gated compatibility core, including source-specific semantics that would otherwise require another adapter boundary.

Frozen decision:

```text
HGF Toolbox 8.2.0 = compatibility specification
HGFX               = compatibility runtime
PyHGF              = optional interoperability / comparison target
```

A native API may integrate with PyHGF later, but compatibility claims remain judged against frozen MATLAB golden tests.

## Evidence

Workflow run `34188815550`:

- `python-specialized-tests`: PASS
  - exhaustive inventory classification: PASS
  - specialized unit tests: PASS
  - M4/M5/M6/M7 regressions: PASS
- `matlab-python-specialized`: PASS
  - frozen reference verification: PASS
  - MATLAB specialized oracle export: PASS
  - MATLAB/Python specialized parity checker: PASS

Earlier failed comparisons identified reference-path and frozen-output quirks and were corrected without relaxing scientific acceptance criteria.

## Next milestone

`M13 — API Compatibility`
