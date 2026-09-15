# M18 D02 optimizer source probe — frozen diagnostic protocol

Protocol: `m18-d02-optimizer-source-probe-1`
Status: **FROZEN / DIAGNOSTIC ONLY**
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

The preregistered D02 cross-endpoint basin diagnostic classifies D02 as `OPTIMIZER_NUMERICAL_BASIN_CANDIDATE`: all nine exact shared parameter vectors pass the unchanged objective tolerance while fitted inference remains materially different. The next question is therefore where the optimizer path first acquires the numerical perturbation that is later amplified.

This probe is diagnostic only. It does not change any release tolerance, seed, data, model, observation family, optimizer option, start point, endpoint, or acceptance rule, and it cannot confer PASS.

## Frozen workflow

Use the exact official D02 workflow:

- input: frozen MATLAB demo `example_binary_input.txt`;
- seed: `123456789`;
- simulation: `ehgf_binary` with native parameters `[NaN 0 1 NaN 1 1 NaN 0 0 1 1.5 NaN -4 3]`;
- simulation observation model: `unitsq_sgm`, native observation parameter `5`;
- fit: `ehgf_binary + unitsq_sgm`;
- observation prior variance: `0.5`;
- optimizer: frozen `quasinewton_optim_config`;
- Ridders gradient options: frozen optimizer setting `min_steps=10`, all other defaults unchanged.

Historical official evidence reports the first gate-level optimizer `x` divergence at zero-based row 7, component 0. This probe freezes the immediately preceding MATLAB source state:

- MATLAB `iter.x` row 7 (one-based), corresponding to zero-based optimizer row 6;
- all three free optimizer components are probed independently;
- every Ridders finite-difference `f(x+h)` and `f(x-h)` sample is exported through the actual stopping step;
- each sample is decomposed into log likelihood, perceptual prior, observation prior, and negative log joint.

The source row and components must not be changed after observing the result. If a later diagnostic needs a different row, it must be a separately named protocol and must preserve this result.

## Decision tree

1. If any HGFX objective sample at the exact MATLAB finite-difference vector differs from MATLAB, classify `OBJECTIVE_SAMPLE_DIVERGENCE`. Localize the first differing decomposition component before changing optimizer algebra.
2. If all objective samples are exact but replaying the MATLAB samples through the Python Ridders extrapolation differs, classify `RIDDERS_EXTRAPOLATION_ARITHMETIC_DIVERGENCE`.
3. If MATLAB samples replay exactly but HGFX samples yield a different selected derivative despite exact objective samples, classify `RIDDERS_REPLAY_UNEXPLAINED_DIVERGENCE` and retain all raw samples.
4. If all three components reproduce the MATLAB selected derivative/error exactly, classify `NO_RIDDERS_DIVERGENCE_AT_SOURCE`; the next diagnostic may inspect transition/state accumulation, but D02 remains BLOCKED.

No classification in this document is an acceptance result. D02 remains blocked until its frozen inference requirements are satisfied or a separately preregistered accepted-equivalence/reference-limitation rule genuinely applies.
