# M18 D02 MATLAB optimizer self-sensitivity diagnostic

Status: **FROZEN FOR DIAGNOSTIC EXECUTION — NO ACCEPTANCE EFFECT**

Protocol: `m18-d02-matlab-self-sensitivity-1`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

The frozen D02 evidence now shows all of the following at once:

- the nine-point cross-endpoint same-vector objective grid passes the existing numerical gate;
- exact MATLAB optimizer-state quasi-Newton transition replay agrees at machine level;
- the first localized off-centre Ridders residual is in the observation likelihood, while the perceptual state is exact;
- at that frozen sample the residual primitive differences are binary64-scale (up to one or a few ULPs), including MATLAB-vs-Python power/log evaluation, and MATLAB's own vector `sum` differs from a scalar-loop reduction.

This diagnostic asks a narrower reference question before any further ULP-specific implementation changes: **is the frozen MATLAB optimizer itself materially sensitive to a one-local-spacing perturbation of its official starting point?**

A positive result is evidence of local optimizer/basin sensitivity in the reference implementation. It is not a D02 PASS and it does not prove that every HGFX endpoint difference is caused by the same perturbation mechanism. A negative result only means that this exact frozen perturbation set did not expose start-point sensitivity; it does not prove numerical stability to objective-evaluation perturbations.

## Frozen contract

Use the official D02 workflow unchanged:

- input: `demo/example_binary_input.txt`;
- simulation seed: `123456789`;
- simulator: `ehgf_binary + unitsq_sgm`;
- native simulation parameters: `[NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3]`;
- fit: `ehgf_binary + unitsq_sgm`;
- observation prior variance: `0.5`;
- optimizer: frozen `quasinewton_optim_config`;
- objective: the same restricted negative-log-joint used by `fitModel`;
- free-parameter ordering and fixed parameters: unchanged.

First replay the optimizer from the exact official free starting point. Then perform exactly six additional MATLAB optimization runs. For each of the three free coordinates independently, replace only that starting coordinate by:

- `x_k + eps(x_k)`; and
- `x_k - eps(x_k)`.

All other coordinates are unchanged. The actual binary64 delta is recorded. No larger perturbation grid is part of this protocol.

## Classification rule

The existing M18 numerical gate is reused only as a **diagnostic materiality yardstick**:

- `rtol = 3e-8`
- `atol = 3e-10`

Classify:

1. `INVALID_BASELINE_REPLAY` if the reconstructed baseline optimizer endpoint does not reproduce the official MATLAB endpoint under the existing gate.
2. `MATLAB_START_ULP_BASIN_SENSITIVE` if the baseline replay is valid and at least one of the six one-spacing starts terminates at a final free-parameter vector outside the existing gate relative to the baseline endpoint.
3. `NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED` if the baseline replay is valid and all six perturbed endpoints remain inside the existing gate.
4. `INSUFFICIENT_REFERENCE_EVIDENCE` if any frozen run is missing or non-finite.

No classification above closes D02. D02 remains **BLOCKED** until the release policy is satisfied by direct parity or a separately preregistered scientific/inferential gate with adequate reference evidence.

## Integrity constraints

- Preserve all historical D02 failures and artifacts.
- Do not change seed, data, model, priors, objective, optimizer settings, free-parameter ordering, acceptance tolerances, or the six-run perturbation set after execution.
- Do not use a favorable perturbation run as a replacement fitted result.
- Do not infer a general scientific limitation from a negative result.
