# M18 D08 failed-holdout Ridders source probe

Status: **FROZEN / DIAGNOSTIC ONLY**

Protocol: `m18-d08-holdout-source-probe-1`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

The frozen D08 Level-2 holdout remains failed for seed `314159265`. After the placeholder-variance repair, the failed-holdout optimizer diagnostic classifies the case as `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`: exact MATLAB-state objectives reproduce, quasi-Newton state transitions replay at machine precision, but tiny shared-state gradient differences accumulate into a material optimizer path split.

This probe localizes the numerical source inside the finite-difference gradient. It has **no acceptance effect** and cannot convert the failed prospective holdout into PASS.

## Frozen contract

Use exactly:

- input: `demo/example_usdchf.txt`;
- simulation seed: `314159265`;
- simulation and fit model: `uhgf + gaussian_obs`;
- native perceptual vector: `[1.04, 1, .0001, .1, 0, 0, 1, -13, -2, 1e4]`;
- native simulation observation variance: `.00002`;
- default `uhgf_config`, `gaussian_obs_config`, and `quasinewton_optim_config`;
- seven free optimizer coordinates in the reference ordering;
- Ridders `min_steps=10`, all other defaults unchanged;
- MATLAB optimizer trace row **38 one-based** as the source state.

Row 38 is frozen because the already-preserved optimizer diagnostic places it before the first gate-level `iter.x` split while showing a small non-zero exact-shared-state gradient residual. The row must not be changed after observing this probe.

For each of the seven free coordinates, export every `f(x+h)` and `f(x-h)` used through the actual Ridders stopping step, together with the exact finite-difference coordinate and a decomposition into log likelihood, perceptual prior, observation prior, and negative log joint.

## Classification

- `OBJECTIVE_SAMPLE_DIVERGENCE`: at least one HGFX objective evaluated at an exact MATLAB finite-difference vector is not bitwise equal to MATLAB. Localize the first differing decomposition component before changing optimizer algebra.
- `RIDDERS_EXTRAPOLATION_ARITHMETIC_DIVERGENCE`: all objective samples are exact but replaying the MATLAB samples through Python Ridders arithmetic differs from the MATLAB selected derivative/error.
- `RIDDERS_REPLAY_UNEXPLAINED_DIVERGENCE`: MATLAB sample replay is exact but HGFX-sample replay does not reproduce the selected derivative despite exact objective samples.
- `NO_RIDDERS_DIVERGENCE_AT_SOURCE`: all seven components reproduce the selected derivative/error exactly.

No classification above is an acceptance result. Do not change seed, row, model, data, priors, optimizer, Ridders settings, or release tolerances after execution.
