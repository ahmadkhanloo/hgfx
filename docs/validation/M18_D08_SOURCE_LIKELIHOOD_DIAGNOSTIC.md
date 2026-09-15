# M18 D08 failed-holdout source likelihood diagnostic

Status: **FROZEN / DIAGNOSTIC ONLY**

Protocol: `m18-d08-source-likelihood-probe-1`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

`m18-d08-holdout-source-probe-1` localized the first exact-state Ridders residual for the failed D08 holdout to one off-centre objective sample. The exact source objective is equal; Ridders extrapolation of the MATLAB samples is exact; perceptual and observation prior totals are exact. The first residual is `3.637978807091713e-12` in the log-likelihood only.

This diagnostic freezes and decomposes that exact sample before any product repair.

## Frozen sample

- official input: `demo/example_usdchf.txt`;
- simulation seed: `314159265`;
- model: `uhgf + gaussian_obs` for simulation and fitting;
- native simulation parameters: `[1.04, 1, .0001, .1, 0, 0, 1, -13, -2, 1e4]`;
- simulation observation variance: `.00002`;
- default configs and quasinewton optimizer;
- MATLAB optimizer source row: **38 one-based**;
- free component: **1 one-based** (full transformed component 1 one-based);
- Ridders step: **1 one-based**;
- side: **plus**;
- `h = 1.0`.

Thus the diagnostic vector is exactly the row-38 free vector with only free component 1 replaced by `x_1 + 1.0`.

## Evidence exported

For the frozen vector record:

- full transformed vector and perceptual/observation partitions;
- full inference-state tensor;
- Gaussian observation state `x = infStates(:,1,1)`;
- transformed observation parameter and `ze = exp(ptrans_obs)`;
- trial log likelihood, prediction and residual arrays;
- MATLAB vector likelihood sum and explicit scalar-loop sum;
- per-trial Gaussian primitives: normalizer, residual, squared residual, denominator, quadratic term and reconstructed log likelihood.

HGFX evaluates the exact same transformed vector and records its trial values plus NumPy sum, scalar-loop sum, and the compatibility `_matlab_sum` reduction.

## Classification

1. `FORWARD_STATE_DIVERGENCE` if inference states differ before the observation model.
2. `GAUSSIAN_OBSERVATION_PRIMITIVE_DIVERGENCE` if inference states are exact but trial likelihood/primitives differ.
3. `LIKELIHOOD_REDUCTION_DIVERGENCE` if all trial likelihoods are exact but the objective likelihood total differs.
4. `NO_LOCAL_DIVERGENCE` if all localized values and objective total are exact.
5. `INSUFFICIENT_REFERENCE_EVIDENCE` if the frozen sample cannot be reconstructed exactly.

This diagnostic cannot confer PASS and cannot change the failed prospective D08 holdout. Any repair must be general, regression-backed, and then re-tested against the unchanged holdout and existing regression gates.
