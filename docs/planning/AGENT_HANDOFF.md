# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M8 — Objective Parity`

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

P0/P1 observation families validated against frozen MATLAB trial-wise outputs and total log likelihood:

- `unitsq_sgm` (O17, P0)
- `softmax_binary` (O13, P0)
- `beta_obs` (O01, P1)
- `cdfgaussian_obs` (O02, P1)
- `gaussian_obs` (O06, P1)
- `gaussian_obs_offset` (O07, P1)
- `logrt_linear_binary` (O08, P1)
- `logrt_linear_binary_minimal` (O09, P1)
- `softmax` (O11, P1)
- `softmax_2beta` (O12, P1)
- `softmax_mu3` (O14, P1)
- `unitsq_sgm_mu3` (O18, P1)

For every case: `logp`, `yhat`, `res`, irregular-trial NaN semantics, transformed observation parameter use, and total regular-trial log likelihood match MATLAB.

- M7 workflow run: `34143177077`
- `python-observation-tests`: PASS
- `matlab-python-observation-parity`: PASS
- calibrated tolerance: `rtol=2e-11`, `atol=2e-13`

## Next tasks

1. Reconstruct the fixed-parameter objective used by `fitModel`.
2. Combine perceptual forward pass + observation likelihood + priors.
3. Match trial exclusion / irregular-response semantics in objective aggregation.
4. Export fixed-vector MATLAB objective decomposition.
5. Validate `negLL`, prior term, and `negLogJoint` before starting optimizer parity.

## Do not start with

- optimizer tuning
- GPU optimization
- Hessian/LME
- simulation
