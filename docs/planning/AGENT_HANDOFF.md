# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M9 — Compatibility Fitting`

## Frozen reference

HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Completed gates

- M0 — Reference Frozen
- M1 — Golden Harness Operational
- M2 — Parameter/Config Parity
- M3 — Scalar Numerical Parity
- M4 — HGF Forward Parity
- M5 — eHGF Forward Parity
- M6 — uHGF Forward Parity
- M7 — Observation Parity
- M8 — Objective Parity

## M4 evidence

- Standard binary + continuous HGF forward parity: PASS
- M4 workflow run: `34120120732`

## M5 evidence

- eHGF binary + continuous forward parity: PASS
- safe precision-update edge case: PASS
- M5 workflow run: `34123043904`

## M6 evidence

- uHGF binary + continuous forward parity: PASS
- Lambert W0 / dual approximation / variational weighting / mixture moments: PASS
- M6 workflow run: `34125217371`

## M7 evidence

P0/P1 observation families validated against frozen MATLAB trial-wise outputs and total log likelihood.

- M7 workflow run: `34143177077`
- `python-observation-tests`: PASS
- `matlab-python-observation-parity`: PASS
- calibrated tolerance: `rtol=2e-11`, `atol=2e-13`

## M8 evidence

Fixed transformed-parameter objective decomposition for the standard vertical slice
`hgf_binary + unitsq_sgm` matches frozen `fitModel.m` semantics.

Validated:

- regular fixed-vector objective: PASS
- ignored-input + irregular-response objective: PASS
- trial-wise log likelihoods: PASS
- exact irregular-trial exclusion before aggregation: PASS
- ordinary `sum` semantics rather than `nansum`: PASS
- `logLl` / `negLogLl`: PASS
- perceptual Gaussian prior indices, terms, and total: PASS
- observation Gaussian prior indices, terms, and total: PASS
- fixed/NaN prior variances excluded exactly as MATLAB: PASS
- full `negLogJoint`: PASS
- perceptual failure sentinel `realmax` + `rval=-1`: PASS
- M7 observation + M4 HGF regressions included in Python M8 gate: PASS
- M8 workflow run: `34152468348`
- `python-objective-tests`: PASS
- `matlab-python-objective-parity`: PASS
- calibrated tolerance unchanged: `rtol=2e-11`, `atol=2e-13`

The first two M8 workflow attempts exposed only MATLAB JSON scalar-vs-singleton-array serialization differences in the checker. No scientific equation or tolerance was changed.

## Next tasks

1. Add the compatibility free-parameter vector wrapper around the frozen M8 objective.
2. Port/freeze `quasinewton_optim` and its config/termination semantics.
3. Match deterministic initialization from prior means before adding random starts.
4. Compare MAP objective and transformed/native MAP parameters against MATLAB.
5. Add multi-start behavior only after single-start compatibility fitting passes.

## Do not start with

- Hessian/LME
- GPU optimization
- simulation
- performance tuning
