# M18 D02 cross-endpoint numerical diagnostic

Status: **FROZEN FOR DIAGNOSTIC EXECUTION**
Protocol: `m18-d02-basin-probe-1`
Frozen on: 2026-09-14
Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Related decision policy: `MATLAB_EQUIVALENCE_POLICY.md`

## Purpose

D02 currently fails inferential equivalence: the fitted endpoint, Hessian, covariance, correlation, model evidence, predictions and residuals differ materially even though the exact MATLAB endpoint and sampled MATLAB optimizer-path objectives replay in HGFX within the frozen numerical gate.

This diagnostic is **classification-only**. It cannot turn D02 into PASS and it cannot relax an acceptance threshold. Its purpose is to distinguish a remaining same-vector implementation mismatch from optimizer/numerical basin or conditioning amplification.

## Frozen experiment

Use the official D02 workflow unchanged:

- `example_binary_input.txt`;
- simulation seed `123456789`;
- simulator `ehgf_binary + unitsq_sgm`;
- native simulation parameters `[NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3]`;
- fit `ehgf_binary + unitsq_sgm`;
- `unitsq_sgm.logzesa = 0.5` with the existing aligned prior semantics;
- `quasinewton_optim_config`;
- frozen MATLAB reference commit above.

First generate MATLAB and HGFX fitted endpoints under that exact contract. Then evaluate **both objective implementations at exactly the same full transformed parameter vectors** on the line

`theta(alpha) = (1-alpha) * theta_MATLAB + alpha * theta_HGFX`

using the preregistered grid

`alpha = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1]`.

The grid is frozen before its first execution and must not be densified, shifted, or selectively reduced after seeing the result. A later finer probe requires a new protocol version and must preserve this one.

## Decision rule

For every point compare MATLAB and HGFX negative log joint with the existing M18 default scale-aware numerical gate:

- `rtol = 3e-8`
- `atol = 3e-10`

No D02-specific acceptance tolerance is introduced.

Classify the diagnostic as:

1. `SAME_VECTOR_IMPLEMENTATION_MISMATCH` if any preregistered line point fails the unchanged objective tolerance. D02 remains **BLOCKED** and the earliest failing point becomes the next implementation diagnostic target.
2. `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE` if all same-vector line points pass but MATLAB and HGFX fitting still terminate at materially different inferential endpoints. D02 remains **BLOCKED**; this result only localizes the problem to optimization/numerical path/conditioning rather than the objective contract at the sampled points.
3. `INSUFFICIENT_REFERENCE_EVIDENCE` if MATLAB cannot produce the frozen experiment or the evidence set is incomplete.

`OPTIMIZER_NUMERICAL_BASIN_CANDIDATE` is not `PASS_INFERENTIAL_EQUIVALENCE`. D02 can close only if the frozen direct gate passes, a separately preregistered Level-3 inferential-equivalence protocol passes all required inference quantities, or an exact paired MATLAB reference limitation is established.

## Integrity constraints

- Preserve current D02 official failure and `reference/validation/m18_d02_inference/decision.json`.
- Do not change seed, data, model family, priors, optimizer, starts, alpha grid, or tolerance after execution.
- Record both successful and failed diagnostic runs.
- Generated cross-endpoint points are diagnostic inputs, not replacement release fixtures.
