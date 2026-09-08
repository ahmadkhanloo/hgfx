# M12 — Complete Model Coverage Gate

Status: **PASS**

## Why M12 was reopened

The previous M12 accepted `REFERENCE_ONLY` for scientific model families. That is not the project goal.

The corrected project requirement is:

> Every computational/scientific model family in the frozen HGF Toolbox 8.2.0 must be implemented inside HGFX and validated against MATLAB. A scientific model may not remain REFERENCE_ONLY.

Only files that are not scientific models may finish as:

- `PLOT_ONLY`
- `DEPRECATED`
- `NOT_APPLICABLE`

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- MATLAB files in frozen manifest: `334`
- Numerical compatibility mode: CPU float64

## Definition of "implemented"

A model family is `DONE` only when all applicable compatibility pieces exist:

1. Python/JAX-visible model implementation in HGFX.
2. MATLAB-compatible parameter/config semantics.
3. MATLAB-compatible transformed/native parameter mapping.
4. Forward/likelihood/simulation behavior as applicable.
5. Ignored/irregular trial semantics where the MATLAB source supports them.
6. MATLAB-compatible trajectory / inferred-state layout.
7. Frozen MATLAB golden fixture.
8. Automated MATLAB ↔ Python parity checker.
9. Public package export.
10. Regression test proving previously completed families remain unchanged.

A wrapper that merely points at MATLAB or PyHGF is **not** a completed port.

## Corrected M12 sub-gates

### M12A — Continuous AR1
- [x] `hgf_ar1`
- [x] config / transform / name semantics
- [x] regular + ignored/irregular golden parity

### M12B — Multi-Armed Bandit families
- [x] `hgf_binary_mab`
- [x] `hgf_ar1_mab`
- [x] `hgf_ar1_binary_mab`
- [x] `ehgf_ar1_binary_mab`
- [x] `uhgf_ar1_binary_mab`
- [x] reward/input tensor semantics
- [x] configs / transforms / outputs
- [x] MATLAB parity

### M12C — JGET
- [x] `hgf_jget`
- [x] `ehgf_jget`
- [x] `uhgf_jget`
- [x] configs / transforms / outputs
- [x] MATLAB parity

### M12D — Categorical and world models
- [x] `hgf_categorical`
- [x] `hgf_categorical_norm`
- [x] `hgf_whatworld`
- [x] `hgf_whichworld`
- [x] configs / transforms / tensor layouts
- [x] MATLAB parity

### M12E — Discrete-state models
- [x] `tapas_hmm`
- [x] `tapas_hhmm`
- [x] tree/flattening compatibility
- [x] MATLAB parity

### M12F — Classical / auxiliary perceptual families
Already completed:
- [x] RW
- [x] dual-RW
- [x] Pearce-Hall
- [x] Sutton K1
- [x] Kalman

Remaining:
- [x] Bayes-optimal continuous
- [x] Bayes-optimal binary
- [x] Bayes-optimal categorical
- [x] Bayes-optimal WhatWorld
- [x] Bayes-optimal WhichWorld
- [x] response-surprise belief
- [x] response-surprise precision
- [x] response-surprise precision WhatWorld
- [x] response-surprise surprise
- [x] squared prediction error
- [x] configs / transforms where applicable
- [x] MATLAB parity

### M12G — Remaining observation families
Already completed through M7:
- [x] all former P0/P1 observation models

Remaining:
- [x] conditional hallucination observation 1
- [x] conditional hallucination observation 2
- [x] conditional hallucination observation 3
- [x] WhatWorld logRT
- [x] world softmax
- [x] world mu3 softmax
- [x] transforms / simulation functions where present
- [x] MATLAB parity

### M12H — Exhaustive closure
- [x] every scientific perceptual family = DONE
- [x] every scientific observation family = DONE
- [x] zero scientific `REFERENCE_ONLY` families
- [x] public API exports complete
- [x] config/transform inventory complete
- [x] exhaustive frozen-source classification gate
- [x] full regression suite
- [x] final M12 MATLAB/Python CI PASS

## Existing M12 work retained

The previous implementation remains valid and is not discarded:

- binary PU / PU-TBT HGF/eHGF/uHGF
- AR1 binary HGF/eHGF/uHGF
- RW / dual-RW
- Pearce-Hall
- Sutton K1
- Kalman
- HMM

Previous passing evidence: workflow `34188815550`.

## PyHGF decision

Unchanged:

```text
HGF Toolbox 8.2.0 = compatibility specification
HGFX               = compatibility implementation
PyHGF              = optional comparison/interoperability target
```

PyHGF will not be used as a substitute for implementing a frozen MATLAB model family.

## Final M12 pass condition

```text
M12 PASS
  iff
    every scientific frozen model family is implemented in HGFX
    AND every implemented family has frozen MATLAB parity evidence
    AND no scientific family is REFERENCE_ONLY
    AND the complete regression suite passes
```

## Next milestone

M13 must not start until this corrected M12 gate is PASS.


## Frozen-source defects

Known reference defects and the exact compatibility repairs are tracked in `docs/planning/M12_SOURCE_DEFECTS.md`. A source defect never permits a scientific family to remain REFERENCE_ONLY.


## Final evidence

Corrected M12 complete-model gate passed against the frozen HGF Toolbox 8.2.0 reference.

- M12A continuous AR1: workflow `34224773192` — PASS
- M12B/C MAB + JGET: workflow `34224773186` — PASS
- M12D/E categorical/world + HHMM: workflow `34225650007` — PASS
- M12F/G auxiliary + remaining observations, including deterministic simulation semantics: workflow `34225649883` — PASS
- specialized config/prior parity: workflow `34224773097` — PASS
- exhaustive closure: workflow `34225650015` — PASS
  - frozen reference verification: PASS
  - scientific REFERENCE_ONLY files: 0
  - scientific REFERENCE_ONLY families: 0
  - DONE files: 259
  - DONE families: 53
  - full Python regression suite: PASS
- M1 golden/regression revalidation: workflow `34224773168` — PASS

**M12 PASS. M13 is unblocked.**
