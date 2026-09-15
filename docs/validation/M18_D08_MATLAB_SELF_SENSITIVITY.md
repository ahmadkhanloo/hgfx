# M18 D08 MATLAB optimizer self-sensitivity diagnostic

Status: **FROZEN FOR DIAGNOSTIC EXECUTION — NO ACCEPTANCE EFFECT**

Protocol: `m18-d08-matlab-self-sensitivity-1`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

The prospective D08 Level-2 holdout is already an immutable failure as a set: seed `271828182` passed, while seed `314159265` produced `INFERENCE_EQUIVALENCE_FAIL`. For the failing seed, HGFX replay at the exact MATLAB endpoint passes, and the frozen optimizer diagnostic (`m18-d08-holdout-optimizer-probe-1`, run `34829121895`) classified the case as `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES`: objective and Ridders gradient at exact MATLAB states pass the existing numerical gate while the fitted optimizer paths eventually separate.

This diagnostic asks a narrower reference question before any further ULP-specific implementation changes: **is the frozen MATLAB optimizer itself materially sensitive to a one-local-spacing perturbation of its official starting point for the exact failing D08 holdout?**

A positive result is reference evidence of local numerical/basin sensitivity. It is not a D08 PASS, does not rewrite the failed prospective holdout, and does not by itself establish `REFERENCE_LIMITATION_MATCH`. Any release classification must additionally satisfy `MATLAB_REFERENCE_LIMITATIONS_POLICY.md` using the already-preserved paired evidence.

## Frozen contract

Use the exact failed prospective holdout case unchanged:

- input: `demo/example_usdchf.txt`;
- simulation seed: `314159265`;
- simulator: `uhgf + gaussian_obs`;
- native perceptual parameters: `[1.04 1 .0001 .1 0 0 1 -13 -2 1e4]`;
- native observation variance: `.00002`;
- fit: `uhgf + gaussian_obs`;
- default `uhgf_config` and `gaussian_obs_config` after normal placeholder resolution;
- optimizer: frozen `quasinewton_optim_config`;
- objective: the same restricted negative-log-joint used by `fitModel`;
- free full-parameter indices (MATLAB one-based): `[1, 3, 4, 8, 9, 10, 11]`;
- free-parameter ordering and all fixed parameters unchanged.

First replay the optimizer from the exact official free starting point. Then perform exactly fourteen additional MATLAB optimization runs. For each of the seven free coordinates independently, replace only that starting coordinate by:

- `x_k + eps(x_k)`; and
- `x_k - eps(x_k)`.

All other coordinates are unchanged. The actual binary64 delta is recorded. No larger perturbation grid is part of this protocol.

## Classification rule

The existing M18 numerical gate is reused only as a **diagnostic materiality yardstick**:

- `rtol = 3e-8`
- `atol = 3e-10`

Classify:

1. `INVALID_BASELINE_REPLAY` if the reconstructed baseline optimizer endpoint does not reproduce the official MATLAB endpoint under the existing gate.
2. `MATLAB_START_ULP_BASIN_SENSITIVE` if the baseline replay is valid and at least one of the fourteen one-spacing starts terminates at a final free-parameter vector outside the existing gate relative to the baseline endpoint.
3. `NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED` if the baseline replay is valid and all fourteen perturbed endpoints remain inside the existing gate.
4. `INSUFFICIENT_REFERENCE_EVIDENCE` if any frozen run is missing, malformed, or non-finite.

No classification above closes D08. A positive result may be used only as one component of an exact-scope reference-limitation assessment together with the preserved prospective holdout, exact MATLAB-endpoint replay, and shared-state optimizer diagnostic. The failed Level-2 holdout itself remains failed.

## Integrity constraints

- Preserve all historical D08 failures and the failed prospective holdout.
- Do not change seed, data, model, priors, objective, optimizer settings, free-parameter ordering, numerical gate, or the fourteen-run perturbation set after execution.
- Do not substitute a favorable perturbed MATLAB fit for the official reference fit.
- Do not generalize a positive result beyond this exact D08 workflow/seed.
- Do not infer numerical stability from a negative result beyond this exact start-perturbation experiment.
