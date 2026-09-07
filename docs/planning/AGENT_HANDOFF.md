# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M12 — Specialized Model Coverage`

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
- M9 — Compatibility Fitting
- M10 — Hessian/LME Parity
- M11 — Simulation Parity

## M11 evidence

Simulation and prior-predictive behavior for the standard compatibility slice now matches the frozen MATLAB reference at the deterministic scientific boundary.

Validated:

- `simModel.m` orchestration: PASS
- `sampleModel.m` prior draw → transform → trajectory path: PASS
- fixed native perceptual/observation parameters: PASS
- deterministic unit-square-sigmoid response probabilities: PASS
- ignored-trial index semantics: PASS
- frozen `simModel` row-deletion quirk for `traj.muhat/sahat`: PASS
- full `infStates` retained for observation sampling: PASS
- MATLAB-exported standard-normal prior drivers: PASS
- transformed/native sampled parameter vectors: PASS
- same-runtime seeded reproducibility: PASS
- Bernoulli/Gaussian distributional tests: PASS
- M11 workflow run: `34167613757`
- `python-simulation-tests`: PASS
- `matlab-python-simulation`: PASS

No MATLAB-vs-NumPy RNG stream identity is claimed. The MATLAB Actions runner lacks Statistics Toolbox, so M11 uses a test-only scoped Bernoulli shim only to exercise the frozen orchestration; deterministic probabilities and distributions remain the parity targets.

## Architecture decisions frozen through M11

1. M8 owns objective semantics.
2. M9 owns compatibility Ridders+BFGS MAP optimization.
3. M10 owns Hessian/covariance/Laplace evidence and LME-based restart selection.
4. M11 owns compatibility simulation and prior-predictive sampling semantics.
5. Cross-language stochastic parity is defined by shared deterministic drivers or distributional agreement, not RNG byte identity.
6. Native GPU simulation remains a later engine and must be cross-validated against compatibility mode.

## Next tasks

1. Inventory every frozen perceptual/observation family not yet covered by M4–M11.
2. Classify each frozen MATLAB model/file as PORT, WRAP, REUSE_PYHGF, REFERENCE_ONLY, PLOT_ONLY, DEPRECATED, or NOT_APPLICABLE.
3. Prioritize P1 specialized families: PU / PU-TBT, AR1, MAB, JGET, categorical.
4. Add forward/observation/simulation fixtures per family before expanding compatibility APIs.
5. Record the PyHGF dependency-vs-fork decision from empirical parity evidence.

## Do not start with

- GPU optimization
- performance tuning
- batch fitting
- multi-GPU
