# M12 — Complete Model Coverage Gate

Status: **REOPENED / IN PROGRESS**

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
- [ ] `hgf_ar1`
- [ ] config / transform / name semantics
- [ ] regular + ignored/irregular golden parity

### M12B — Multi-Armed Bandit families
- [ ] `hgf_binary_mab`
- [ ] `hgf_ar1_mab`
- [ ] `hgf_ar1_binary_mab`
- [ ] `ehgf_ar1_binary_mab`
- [ ] `uhgf_ar1_binary_mab`
- [ ] reward/input tensor semantics
- [ ] configs / transforms / outputs
- [ ] MATLAB parity

### M12C — JGET
- [ ] `hgf_jget`
- [ ] `ehgf_jget`
- [ ] `uhgf_jget`
- [ ] configs / transforms / outputs
- [ ] MATLAB parity

### M12D — Categorical and world models
- [ ] `hgf_categorical`
- [ ] `hgf_categorical_norm`
- [ ] `hgf_whatworld`
- [ ] `hgf_whichworld`
- [ ] configs / transforms / tensor layouts
- [ ] MATLAB parity

### M12E — Discrete-state models
- [x] `tapas_hmm`
- [ ] `tapas_hhmm`
- [ ] tree/flattening compatibility
- [ ] MATLAB parity

### M12F — Classical / auxiliary perceptual families
Already completed:
- [x] RW
- [x] dual-RW
- [x] Pearce-Hall
- [x] Sutton K1
- [x] Kalman

Remaining:
- [ ] Bayes-optimal continuous
- [ ] Bayes-optimal binary
- [ ] Bayes-optimal categorical
- [ ] Bayes-optimal WhatWorld
- [ ] Bayes-optimal WhichWorld
- [ ] response-surprise belief
- [ ] response-surprise precision
- [ ] response-surprise precision WhatWorld
- [ ] response-surprise surprise
- [ ] squared prediction error
- [ ] configs / transforms where applicable
- [ ] MATLAB parity

### M12G — Remaining observation families
Already completed through M7:
- [x] all former P0/P1 observation models

Remaining:
- [ ] conditional hallucination observation 1
- [ ] conditional hallucination observation 2
- [ ] conditional hallucination observation 3
- [ ] WhatWorld logRT
- [ ] world softmax
- [ ] world mu3 softmax
- [ ] transforms / simulation functions where present
- [ ] MATLAB parity

### M12H — Exhaustive closure
- [ ] every scientific perceptual family = DONE
- [ ] every scientific observation family = DONE
- [ ] zero scientific `REFERENCE_ONLY` families
- [ ] public API exports complete
- [ ] config/transform inventory complete
- [ ] exhaustive frozen-source classification gate
- [ ] full regression suite
- [ ] final M12 MATLAB/Python CI PASS

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
