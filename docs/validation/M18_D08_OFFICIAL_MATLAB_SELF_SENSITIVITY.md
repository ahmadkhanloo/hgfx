# M18 D08 official MATLAB optimizer self-sensitivity diagnostic

Status: **FROZEN FOR DIAGNOSTIC EXECUTION — NO ACCEPTANCE EFFECT**

Protocol: `m18-d08-official-matlab-self-sensitivity-1`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

The official `official-demo-workflows-1` D08 case uses seed `123456789`, not the later prospective holdout seed `314159265`. On the current product implementation the official D08 direct gate remains a preserved `OPTIMIZER_MISMATCH`: exact MATLAB endpoint replay passes, the initial Ridders diagnostic passes, sampled MATLAB optimizer-path objectives pass, and the remaining direct mismatch is a fitted derived trajectory value. Separately, the failed prospective holdout seed `314159265` has now demonstrated strong MATLAB one-ULP start-point basin sensitivity under protocol `m18-d08-matlab-self-sensitivity-1`.

This protocol asks the exact release-scope reference question for the **official seed**: is the frozen MATLAB optimizer itself materially sensitive to a one-local-spacing perturbation of its official D08 starting point?

A positive result is exact-case reference numerical-sensitivity evidence. It is not direct parity, not a Level-2 PASS, and does not rewrite either the official direct failure or the failed prospective holdout.

## Frozen contract

Use the exact official D08 workflow from `reference/matlab/export_m18_workflows.m`:

- input: `demo/example_usdchf.txt`;
- simulation seed: `123456789`;
- simulator: `uhgf + gaussian_obs`;
- native perceptual parameters: `[1.04 1 .0001 .1 0 0 1 -13 -2 1e4]`;
- native observation variance: `.00002`;
- fit: `uhgf + gaussian_obs`;
- default `uhgf_config` and `gaussian_obs_config` after normal placeholder resolution;
- optimizer: frozen `quasinewton_optim_config`;
- objective: the same restricted negative-log-joint used by `fitModel`;
- free full-parameter indices (MATLAB one-based): `[1, 3, 4, 8, 9, 10, 11]`;
- free-parameter ordering and fixed parameters unchanged.

First replay the optimizer from the exact official free starting point. Then perform exactly fourteen additional MATLAB optimization runs. For each of the seven free coordinates independently, replace only that starting coordinate by `x_k - eps(x_k)` and `x_k + eps(x_k)`. Record the actual binary64 delta. No larger perturbation grid is part of this protocol.

## Classification rule

Reuse the existing M18 numerical gate only as a diagnostic materiality yardstick:

- `rtol = 3e-8`
- `atol = 3e-10`

Classify:

1. `INVALID_BASELINE_REPLAY` if the reconstructed baseline does not reproduce the official MATLAB endpoint under the existing gate.
2. `MATLAB_START_ULP_BASIN_SENSITIVE` if baseline replay is valid and at least one of the fourteen one-spacing starts terminates outside the existing gate relative to baseline.
3. `NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED` if baseline replay is valid and all fourteen endpoints remain inside the gate.
4. `INSUFFICIENT_REFERENCE_EVIDENCE` if evidence is incomplete or non-finite.

This diagnostic cannot independently close D08. A release `REFERENCE_LIMITATION_MATCH` decision requires the full exact-scope evidence chain: preserved official direct failure, exact MATLAB endpoint replay, optimizer/shared-state evidence, repaired prior/placeholder contract, and this frozen MATLAB reference-sensitivity result. The failed prospective Level-2 holdout remains failed regardless of outcome.

## Integrity constraints

- Preserve the official D08 direct failure and the prospective holdout failure.
- Do not change seed, dataset, model, priors, objective, optimizer, free-parameter ordering, gate, or fourteen-run perturbation set after execution.
- Do not substitute a favorable perturbed MATLAB endpoint for the official endpoint.
- Do not generalize any result beyond the exact official D08 workflow without separate evidence.
