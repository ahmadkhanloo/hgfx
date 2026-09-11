# MATLAB Toolbox Validation Matrix

## Purpose

This document defines the M18 validation traceability matrix between the MATLAB HGF Toolbox behavior and HGFX scientific validation.

The product-level acceptance target is **MATLAB Toolbox scientific equivalence**, not merely passing internal unit tests.

Reference:

- HGF Toolbox: 8.2.0
- Frozen reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Validation layers

| ID | MATLAB capability | HGFX validation artifact | Status |
|---|---|---|---|
| V01 | HGF forward trajectories | forward parity fixtures | PASS |
| V02 | eHGF forward trajectories | eHGF parity fixtures | PASS |
| V03 | uHGF forward trajectories | uHGF parity fixtures | PASS |
| V04 | Observation models | observation parity fixtures | PASS |
| V05 | Objective computation | objective parity fixtures | PASS |
| V06 | Model fitting compatibility | M9 compatibility fitting | PASS |
| V07 | Hessian/covariance/LME | M10 validation | PASS |
| V08 | Simulation compatibility | M11/M12 validation | IN PROGRESS |
| V09 | Parameter recovery | M18 recovery protocol | IN PROGRESS |
| V10 | Model recovery | M18 confusion matrix evaluation | IN PROGRESS |
| V11 | Robustness sweeps | M18 robustness extension | TODO |
| V12 | CPU/GPU numerical agreement | M17/M18 GPU validation | IN PROGRESS |

## Recovery matrix

| Generator | Fitted models | Trial counts | Parameter regimes | Metrics |
|---|---|---|---|---|
| hgf_binary | hgf_binary | 128, 256 | 0.15, 0.35 prior SD | bias, RMSE, correlation |
| ehgf_binary | ehgf_binary | 128, 256 | 0.15, 0.35 prior SD | bias, RMSE, correlation |
| uhgf_binary | uhgf_binary | 128, 256 | 0.15, 0.35 prior SD | bias, RMSE, correlation |

## Model recovery matrix

| Generating model | Candidate models | Selection rule | Output |
|---|---|---|---|
| hgf_binary | hgf/eHGF/uHGF | BIC primary, AIC secondary | confusion matrix |
| ehgf_binary | hgf/eHGF/uHGF | BIC primary, AIC secondary | confusion matrix |
| uhgf_binary | hgf/eHGF/uHGF | BIC primary, AIC secondary | confusion matrix |

## Important scientific rule

A recovery failure does not automatically indicate an HGFX implementation error. The MATLAB toolbox itself has identifiability limits. Validation must distinguish:

1. implementation mismatch;
2. optimizer failure;
3. parameter non-identifiability;
4. insufficient data regime;
5. intrinsic model ambiguity.

Therefore M18 reports diagnosis information rather than forcing all recoveries to PASS.

## Acceptance

M18 is complete when:

- all rows have reproducible evidence;
- failures are classified;
- MATLAB-equivalent limitations are documented;
- recovery claims are supported by frozen experiment outputs.
