# M18 S8 — HGF R0 Ridders stencil localization

Status: **FROZEN DIAGNOSTIC / NO ACCEPTANCE EFFECT**

Protocol: `m18-s8-hgf-r0-ridders-stencil-1`

This is a child diagnostic of `m18-s8-hgf-r0-optimizer-probe-1`. The parent probe localized the first consequential mismatch to MATLAB optimizer row 10, free component 1, while the center-point objective still agreed within the unchanged numerical gate.

## Frozen scope

- exact immutable S7 case `PR-hgf_binary-T256-S0.35-R0`
- case SHA-256 `1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5`
- frozen MATLAB reference `2437f4dc241541072722a2695ddeca7b44d83dd3`
- optimizer row: MATLAB 1-based row `10`
- differentiated free component: MATLAB/Ridders component `1` (zero-based `0`)
- unchanged Ridders settings: `init_h=1`, `div=1.2`, `min_steps=10`, `max_steps=100`, `tf=2`
- no acceptance effect and no changes to seed/data/start/grid/model/optimizer/tolerances

## Exported stencil evidence

For each Ridders step actually visited before the frozen MATLAB termination rule fires, export both `x+h` and `x-h` evaluations with:

- exact free vector and `h`;
- negative log joint;
- negative log likelihood;
- perceptual and observation prior totals;
- trial log-likelihood vector;
- perceptual `infStates`;
- base centered-difference estimate;
- current Richardson best estimate/error.

HGFX evaluates exactly those exported free vectors. The checker reports the first and largest binary64 discrepancies separately for inference states, trial likelihoods, likelihood reduction, priors and joint objective. This diagnostic exists to select a regression/repair target; it cannot confer S7 acceptance.
