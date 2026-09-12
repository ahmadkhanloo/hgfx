# M18 — MATLAB Reference Validation Matrix

## Purpose

This matrix defines the product/scientific validation surface for HGFX v1.0.

The frozen reference is HGF Toolbox v8.2.0 at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`.

HGFX is not required to make base HGF succeed in cases where the MATLAB Toolbox itself uses eHGF, uHGF, a specialized family, or exposes a scientific/identifiability limitation. The compatibility target is the reference capability and workflow, including its limitations.

## Core matrix

| Workflow | MATLAB reference path | HGFX v1 requirement | M18 evidence |
|---|---|---|---|
| Binary HGF | HGF + unit-square sigmoid | Same fit/sim/trajectory/objective semantics | parameter recovery + model recovery + parity |
| Binary eHGF | eHGF + unit-square sigmoid | Same enhanced-update workflow | parameter recovery + model recovery + parity |
| Binary uHGF | uHGF + unit-square sigmoid | Same uncertainty-aware workflow | parameter recovery + model recovery + parity |
| Specialized perceptual families | MATLAB family-specific implementation | Equivalent supported family; do not force base HGF | frozen M12 parity + targeted scientific checks where meaningful |
| Observation families | MATLAB matching observation model | Preserve likelihood/prediction/residual semantics | frozen M7 parity + demo/workflow checks |
| Fitting/statistics | fitModel/quasi-Newton/Hessian/LME | MATLAB-compatible fitting/statistics | frozen M8–M10 parity + optimizer agreement |
| Simulation | simModel/sampleModel | MATLAB-compatible orchestration and transforms | frozen M11 parity + recovery simulations |
| CPU/GPU | MATLAB-equivalent math on HGFX backends | Numerically equivalent result across HGFX backends | CPU/GPU agreement |
| Demo workflows | official/frozen MATLAB example path | Python reproduction with equivalent scientific outputs | mandatory v1 demo gate |

## Specialized-family coverage inherited from M12

The following families already belong to the v1 compatibility surface and must not be collapsed into a requirement that base HGF solve their use cases:

- PU / PU-TBT across HGF/eHGF/uHGF
- AR1 continuous/binary variants
- MAB variants
- JGET
- categorical / categorical-normalized
- RW / dual-RW
- Pearce-Hall
- Sutton K1
- Kalman
- HMM / HHMM
- WhatWorld / WhichWorld
- Bayes-optimal auxiliary families
- response-speed / squared-PE auxiliary families
- conditional/world observation families

## Limitation policy

A validation case is **not** an HGFX failure when all of the following hold:

1. the same limitation exists in the frozen MATLAB reference or its documented workflow;
2. HGFX reproduces that limitation or follows the same alternative model path;
3. HGFX does not claim stronger identifiability/scientific validity than the reference;
4. the limitation and chosen model path are recorded in M18 evidence.

Conversely, it **is** an HGFX failure if MATLAB succeeds with an available reference workflow but HGFX cannot reproduce that workflow within the agreed numerical/scientific tolerances.

## Recovery gate

The first recovery gate intentionally covers the unified binary variants:

- `hgf_binary`
- `ehgf_binary`
- `uhgf_binary`

This is appropriate because the existing M18 diagnostic engine can simulate, fit, recover parameters, and perform candidate-model recovery for all three variants. Specialized families are added to recovery only when recovery is scientifically meaningful in the MATLAB reference; complete computational parity for those families remains inherited from M12.

## Remaining v1 release checks

- [ ] Gate-level parameter recovery executed and recorded
- [ ] Gate-level model recovery executed and recorded
- [ ] Optimizer agreement recorded
- [ ] CPU/GPU agreement recorded where a GPU runtime is available
- [ ] MATLAB limitation register completed
- [ ] MATLAB demo workflows mapped to Python reproductions
- [ ] Demo outputs validated

Machine-readable source: `benchmarks/m18_validation_matrix.json`.
