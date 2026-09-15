# M18 D08 failed-holdout optimizer diagnostic

Status: **FROZEN DIAGNOSTIC / NOT AN ACCEPTANCE GATE**

Protocol: `m18-d08-holdout-optimizer-probe-1`

Frozen failing holdout seed: `314159265`

Reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Purpose

The prospective D08 Level-2 holdout failed for seed `314159265` while exact MATLAB-endpoint replay in HGFX had no same-vector mismatches. The failure therefore cannot be repaired or accepted by increasing a trajectory tolerance. This diagnostic localizes the earliest optimizer-path divergence on the exact failed holdout case.

This protocol is diagnostic only. It cannot turn D08 into PASS and it does not change the frozen holdout, its seeds, its tolerances, data, model family, starts, or optimizer settings.

## Frozen case

- input: official `demo/example_usdchf.txt`;
- simulation model: `uhgf`;
- observation model: `gaussian_obs`;
- native perceptual parameters: `[1.04 1 .0001 .1 0 0 1 -13 -2 1e4]`;
- native observation parameter: `.00002`;
- simulation seed: `314159265`;
- fit configs: default `uhgf_config`, `gaussian_obs_config`;
- optimizer: default `quasinewton_optim_config`.

The MATLAB-generated response vector is exported and reused by HGFX, so fitting compares the same observations rather than two separately simulated vectors.

## Why rows 38-44 are inspected

The frozen holdout result first reported an optimizer `iter.x` divergence at zero-based index `(41,4)`, i.e. MATLAB trace row 42 / transformed free parameter 5. Rows 38-44 are therefore a post-failure localization window around the first observed path split. Selecting this diagnostic window after observing the failure is allowed because this is **not** a prospective acceptance rule and cannot be used to declare PASS.

## Exported evidence

For MATLAB rows 38-44, export:

- exact optimizer `x`;
- objective value `val`;
- Ridders gradient and gradient error evaluated at that exact MATLAB `x`;
- inverse-Hessian state when available.

Also export the full MATLAB optimizer `x`, `val`, and reset traces so the checker can independently locate the first path divergence.

HGFX then:

1. fits the exact exported MATLAB response vector;
2. compares full optimizer traces using the existing default numerical tolerance only as a localization aid;
3. evaluates the HGFX objective and Ridders gradient at the **exact MATLAB shared states** in rows 38-44;
4. replays quasi-Newton step/BFGS algebra from exact MATLAB state where sufficient data are available;
5. reports raw absolute/relative differences and the earliest supported divergence mechanism.

## Diagnostic classifications

The checker may report one of:

- `SHARED_STATE_OBJECTIVE_OR_GRADIENT_DIVERGENCE` — HGFX differs at an exact MATLAB optimizer state before/at the path split; continue primitive/numerical localization there.
- `SHARED_STATE_NUMERICS_PASS_PATH_DIVERGES` — objective/gradient at the inspected shared states pass the existing localization tolerance while the fitted path diverges; investigate optimizer state/termination/finite-difference sensitivity rather than model equations.
- `INSUFFICIENT_REFERENCE_EVIDENCE` — required trace/gradient/Hessian evidence is unavailable.

These are diagnostic labels, not release outcomes.

## Integrity rule

Do not modify this diagnostic after observing its result in order to obtain a preferred classification. If additional localization is needed, create a new versioned diagnostic while preserving this result.
