# MATLAB Toolbox Validation Matrix

## Purpose

This document defines the M18 validation traceability matrix between the MATLAB HGF Toolbox behavior and HGFX scientific validation.

The product-level acceptance target is **MATLAB Toolbox scientific and workflow equivalence**, not merely passing internal unit tests and not forcing one model family to solve every scientific case.

Reference:

- HGF Toolbox: 8.2.0
- Frozen reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Limitation policy: `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
- Demo/model-selection matrix: `docs/validation/MATLAB_DEMO_MODEL_SELECTION_MATRIX.md`

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
| V10 | Model recovery / model-selection behavior | M18 confusion matrix + official demo reference workflows | IN PROGRESS — D02 MODEL-SELECTION PARITY PASS |
| V11 | Robustness sweeps | M18 robustness extension | TODO |
| V12 | CPU/GPU numerical agreement | M15/M17/M18 GPU validation | PASS WITH PHYSICAL-H100 EVIDENCE |
| V13 | MATLAB demo/workflow reproduction | v1 demo-parity suite | IN PROGRESS — D02 PASS |
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

### Official model-selection evidence D02 — PASS

The frozen official `hgf_demo.m` contains a parameter regime in which classic HGF is invalid and eHGF is the supported solution. HGFX reproduces that exact behavior on the official 320-trial binary input and native parameter vector.

- run `34684401843`, job `103528739680`, SUCCESS
- classification: `PASS_MODEL_SELECTION_PARITY`
- classic HGF: MATLAB FAIL (`tapas:hgf:NegPostPrec`), HGFX corresponding FAIL
- eHGF: MATLAB SUCCESS, HGFX SUCCESS
- eHGF trajectories/inference states: numerical parity, `mismatches=[]`
- artifact `10294714175`
- artifact SHA-256 `2aa62628d16198f8f335b56fca0f015303439406bb278a329b4cae09b9e69afd`

This establishes the first product-level proof that HGFX v1 follows MATLAB's model-family solution rather than forcing base HGF to pass an unsupported regime.

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

The exact historical HGF 512-trial case has been compared against the frozen MATLAB reference and is classified **`REFERENCE_LIMITATION_MATCH`**.

Frozen case: `hgf_binary + unitsq_sgm`, 512 trials, truth perturbation 0.35 prior SD, replicate 0, cell seed `233100`, response seed `233101`.

Evidence: workflow run `34683977567`; artifact `m18-512-matlab-reference-evidence`, ID `10295261423`; artifact SHA-256 `8a538a1bc8cae206e1014b72a4de8495d9951ad2934845db1704d83ee743092c`.

On identical inputs/responses/configuration, truth-parameter forward execution succeeds in both MATLAB and HGFX; default-parameter forward execution fails in both with the corresponding variational-approximation-invalid condition; the initial objective is unstable in both and fitting is not entered. No MATLAB-vs-HGFX mismatch was observed.

Interpretation: acceptable as a matched MATLAB-reference limitation for v1.0, but not a scientific PASS and not a claim of arbitrary 512-trial support.

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
