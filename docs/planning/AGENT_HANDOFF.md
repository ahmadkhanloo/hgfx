# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M10 — Hessian/LME Parity`

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

## M8 evidence

Fixed transformed-parameter objective decomposition for the standard vertical slice
`hgf_binary + unitsq_sgm` matches frozen `fitModel.m` semantics.

- M8 workflow run: `34152468348`
- `python-objective-tests`: PASS
- `matlab-python-objective-parity`: PASS
- calibrated tolerance: `rtol=2e-11`, `atol=2e-13`

## M9 evidence

The frozen compatibility optimizer and default single-start fitting path are now parity-gated.

Validated:

- `quasinewton_optim_config` defaults: PASS
- Ridders gradient with `min_steps=10`: preserved
- BFGS inverse-Hessian update: PASS
- `maxStep` clipping: PASS
- Armijo-like regularization loop: PASS
- reset semantics: preserved
- `tolArg` and `tolGrad` stopping formulas: preserved
- optimizer quadratic oracle `argMin/valMin/T`: PASS
- combined perceptual+observation free-index selection: PASS
- fixed/undefined parameters remain unchanged: PASS
- initialization from prior means: PASS
- M8 objective reused rather than duplicated in Python fitting path: PASS
- transformed MAP vector: PASS
- native perceptual MAP vector: PASS
- native observation MAP vector: PASS
- final `negLogJoint`: PASS
- final `negLogLl`: PASS
- frozen default `nRandInit=0`: confirmed
- M9 workflow run: `34161336607`
- `python-compat-fitting-tests`: PASS
- `matlab-python-compat-fitting`: PASS

M9 intentionally does not calculate the numerical Hessian, covariance, LME, AIC/BIC, or select random restarts by LME. Those belong to M10. The frozen default fitting path has `nRandInit=0`, so this does not leave the default compatibility fit incomplete.

## Next tasks

1. Port/freeze `riddershessian` use at the fitted MAP with `init_h=1`, `min_steps=10`.
2. Match positive-definite checks and optimizer-`T` fallback.
3. Match `nearest_psd`, Sigma, Corr, and determinant semantics.
4. Match Laplace LME and decomposed LME.
5. Match accuracy/complexity, AIC, and BIC.
6. Once LME parity is closed, add and validate seeded multi-start selection.

## Do not start with

- GPU optimization
- simulation
- performance tuning
- batch fitting
