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
| V09 | Parameter recovery | frozen M18 + M18A + corrected M18B protocol | IN PROGRESS — M18B PROTOCOL GATE PASS |
| V10 | Model recovery / model-selection behavior | M18 confusion matrix + reference workflow comparison | IN PROGRESS |
| V11 | Robustness sweeps | M18 robustness extension | TODO |
| V12 | CPU/GPU numerical agreement | M15/M17/M18 GPU validation | PASS WITH PHYSICAL-H100 EVIDENCE |
| V13 | MATLAB demo/workflow reproduction | v1 demo-parity suite | TODO |
| V14 | MATLAB-equivalent scientific limitations | reference-limitation evidence registry | IN PROGRESS — 512-TRIAL CASE CLASSIFIED |

## Recovery matrix

The recovery matrix is **model-family specific**. A failure of base HGF is not automatically a product failure when the frozen MATLAB toolbox itself requires a different model family for the scientific case.

| Generator | Primary same-model fit | Cross-family diagnostics | Trial counts | Parameter regimes | Metrics |
|---|---|---|---|---|---|
| hgf_binary | hgf_binary | eHGF/uHGF where scientifically relevant | 64, 128, 256 | preregistered perturbations | bias, RMSE, correlation, profile diagnostics |
| ehgf_binary | ehgf_binary | HGF/uHGF diagnostics | 64, 128, 256 | preregistered perturbations | bias, RMSE, correlation, profile diagnostics |
| uhgf_binary | uhgf_binary | HGF/eHGF diagnostics | 64, 128, 256 | preregistered perturbations | bias, RMSE, correlation, profile diagnostics |

The historical frozen M18 128/256 × 0.15/0.35-SD experiment remains immutable evidence. M18B adds an identifiability-aware 64/128/256 × 0.35-SD diagnostic protocol without retroactively changing historical M18 thresholds.

Corrected M18B protocol evidence: workflow run `34497399365`, job `102939240184`; frozen reference guard PASS; 39 M18B tests passed; full regression 136 passed / 4 physical-GPU-only skips; final 27-dataset gate `gate_pass=true`, failures=0; artifact `10160948325`, SHA-256 `5a997b3be06f12420a52086f42656ecd14ff132892d42bb69c20419de234f182`.

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

## 512-trial numerical-horizon case — CLASSIFIED

The exact historical HGF 512-trial case has now been compared against the frozen MATLAB reference and is classified **`REFERENCE_LIMITATION_MATCH`**.

Frozen case:

- model: `hgf_binary`
- observation model: `unitsq_sgm`
- trials: 512
- truth perturbation: 0.35 prior SD
- replicate: 0
- cell seed: `233100`
- response seed: `233101`
- MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

Evidence:

- workflow: `M18 512 MATLAB Reference Classification`
- run: `34683977567`
- HGFX head: `3a272c545ca2366deb57a0c9c0dbb2cf01ad0108`
- artifact: `m18-512-matlab-reference-evidence`, ID `10295261423`
- artifact SHA-256: `8a538a1bc8cae206e1014b72a4de8495d9951ad2934845db1704d83ee743092c`

Observed behavior on identical inputs/responses/configuration:

1. truth-parameter forward execution succeeds in both MATLAB and HGFX;
2. default-parameter forward execution fails in both with the same variational-approximation-invalid scientific condition;
3. MATLAB reports `tapas:hgf:VarApproxInvalid`; HGFX raises the corresponding `ValueError`;
4. the initial objective is unstable in both (`neg_log_joint` and `neg_log_likelihood` at the realmax failure sentinel, `rval=-1`);
5. fitting is therefore not entered in either implementation;
6. no MATLAB-vs-HGFX mismatch was observed.

Interpretation: for this frozen case the 512-trial horizon is not an HGFX-specific defect. It is acceptable as a matched MATLAB-reference limitation for v1.0. This does **not** constitute a scientific PASS and does not imply arbitrary 512-trial input/configuration regimes are supported.

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
