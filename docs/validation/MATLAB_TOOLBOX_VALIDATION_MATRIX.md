# MATLAB Toolbox Validation Matrix

## Purpose

This document defines the M18 validation traceability matrix between the MATLAB HGF Toolbox behavior and HGFX scientific validation.

The product-level acceptance target is **MATLAB Toolbox scientific and workflow equivalence**, not merely passing internal unit tests and not forcing one model family to solve every scientific case.

Reference:

- HGF Toolbox: 8.2.0
- Frozen reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Limitation policy: `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`

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
| V08 | Simulation compatibility | M11/M12 validation | PASS |
| V09 | Parameter recovery | M18/M18A/M18B recovery protocol | IN PROGRESS |
| V10 | Model recovery / model-selection behavior | M18 confusion matrix + reference workflow comparison | IN PROGRESS |
| V11 | Robustness sweeps | M18 robustness extension | TODO |
| V12 | CPU/GPU numerical agreement | M15/M17/M18 GPU validation | PASS WITH PHYSICAL-H100 EVIDENCE |
| V13 | MATLAB demo/workflow reproduction | v1 demo-parity suite | TODO |
| V14 | MATLAB-equivalent scientific limitations | reference-limitation evidence registry | IN PROGRESS |

## Recovery matrix

The recovery matrix is **model-family specific**. A failure of base HGF is not automatically a product failure when the frozen MATLAB toolbox itself requires a different model family for the scientific case.

| Generator | Primary same-model fit | Cross-family diagnostics | Trial counts | Parameter regimes | Metrics |
|---|---|---|---|---|---|
| hgf_binary | hgf_binary | eHGF/uHGF where scientifically relevant | 64, 128, 256 | preregistered perturbations | bias, RMSE, correlation, profile diagnostics |
| ehgf_binary | ehgf_binary | HGF/uHGF diagnostics | 64, 128, 256 | preregistered perturbations | bias, RMSE, correlation, profile diagnostics |
| uhgf_binary | uhgf_binary | HGF/eHGF diagnostics | 64, 128, 256 | preregistered perturbations | bias, RMSE, correlation, profile diagnostics |

The historical frozen M18 128/256 × 0.15/0.35-SD experiment remains immutable evidence. M18B adds an identifiability-aware 64/128/256 × 0.35-SD diagnostic protocol without retroactively changing historical M18 thresholds.

## Model recovery matrix

| Generating model | Candidate models | Selection rule | Product interpretation |
|---|---|---|---|
| hgf_binary | hgf/eHGF/uHGF | BIC primary, AIC secondary | compare selected model and ambiguity with MATLAB reference behavior |
| ehgf_binary | hgf/eHGF/uHGF | BIC primary, AIC secondary | compare selected model and ambiguity with MATLAB reference behavior |
| uhgf_binary | hgf/eHGF/uHGF | BIC primary, AIC secondary | compare selected model and ambiguity with MATLAB reference behavior |

Balanced accuracy remains a scientific diagnostic. It is not by itself sufficient to declare an implementation failure when MATLAB exhibits the same model ambiguity.

## Required non-PASS classification

Every non-PASS scientific result must be assigned one primary class from `MATLAB_REFERENCE_LIMITATIONS_POLICY.md`:

- `IMPLEMENTATION_MISMATCH`
- `OPTIMIZER_MISMATCH`
- `REFERENCE_LIMITATION_MATCH`
- `MODEL_SELECTION_MISMATCH`
- `INSUFFICIENT_REFERENCE_EVIDENCE`

A `REFERENCE_LIMITATION_MATCH` is acceptable for **MATLAB-equivalence v1.0**, but is not a claim that the underlying model scientifically passes that case.

## Important scientific rule

A recovery failure does not automatically indicate an HGFX implementation error. Validation must distinguish:

1. implementation mismatch;
2. optimizer mismatch;
3. parameter non-identifiability;
4. insufficient data regime;
5. intrinsic model ambiguity;
6. MATLAB-reference limitation;
7. use of a different MATLAB model family (HGF/eHGF/uHGF/specialized family) for the scientific case.

Therefore M18 reports diagnosis information rather than forcing all recoveries to PASS.

## 512-trial numerical-horizon case

The current HGFX compatibility path has shown instability in a 512-trial extension. This is **not yet an accepted MATLAB-equivalent limitation**.

Required next evidence:

1. reproduce the exact deterministic 512-trial dataset and seed;
2. run the same model/configuration against frozen MATLAB HGF Toolbox 8.2.0;
3. identify whether MATLAB remains valid or fails comparably;
4. compare the first divergent trial/state if MATLAB remains valid;
5. classify as `IMPLEMENTATION_MISMATCH`, `REFERENCE_LIMITATION_MATCH`, or `INSUFFICIENT_REFERENCE_EVIDENCE`.

No seed substitution, grid shrinking, or threshold relaxation is allowed after observing the result.

## Acceptance

M18/v1 validation is complete when:

- all required MATLAB workflows have reproducible HGFX evidence;
- all matrix rows have explicit evidence and status;
- all non-PASS cases are classified;
- accepted limitations have frozen MATLAB-reference evidence;
- no unresolved implementation/model-selection mismatch remains in required MATLAB workflows;
- MATLAB demo/workflow parity is demonstrated;
- historical failed experiments remain preserved rather than rewritten;
- recovery and model-selection claims are supported by frozen experiment outputs.
