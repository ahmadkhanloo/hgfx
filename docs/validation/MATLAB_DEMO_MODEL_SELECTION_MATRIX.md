# MATLAB Demo Model-Selection Matrix

## Purpose

This matrix turns the frozen HGF Toolbox 8.2.0 official demo into explicit v1.0 product acceptance cases.

Reference: `demo/hgf_demo.m` at HGF Toolbox commit `2437f4dc241541072722a2695ddeca7b44d83dd3`.

The governing rule is **reference-aware parity**: HGFX must reproduce the MATLAB toolbox's valid workflow and model choice. It is not required to make classic HGF succeed where the MATLAB demo itself switches to eHGF, uHGF, AR(1), or another model family.

## Cases

| ID | Official MATLAB demo case | Reference model/workflow | HGFX requirement | Status |
|---|---|---|---|---|
| D01 | Binary HGF fit/sim/recovery on `example_binary_input.txt` | `hgf_binary + unitsq_sgm` | fit/sim/trajectory/statistics parity | CORE PARITY PREVIOUSLY ESTABLISHED; DEMO WRAPPER OPEN |
| D02 | Parameter regime documented to fail in classic HGF but succeed in eHGF | classic `hgf_binary` must fail; `ehgf_binary + unitsq_sgm` must succeed | reproduce both the classic-HGF limitation and eHGF success on identical official input/parameters | **PASS — MODEL-SELECTION PARITY** |
| D03 | uHGF binary comparison in a region where classic HGF can work | `uhgf_binary + unitsq_sgm` | reproduce uHGF trajectory/workflow | OPEN |
| D04 | Extreme binary regime followed by AR(1) regularisation | `uhgf_binary`, then `uhgf_ar1_binary` | reproduce the demo's model change; do not require base HGF to solve it | IMPLEMENTED BUT NOT VALIDATED — exporter/checker at 3bff98b; no run returned for 81fd65a on 2026-09-12 |
| D05 | Alternative learning model on the same binary responses | `rw_binary + unitsq_sgm` | fit and output compatibility | OPEN |
| D06 | Continuous USD/CHF classic HGF | `hgf + gaussian_obs` | Bayes-optimal fit, sim, fit-back, trajectory/statistics parity | OPEN |
| D07 | Continuous eHGF | `ehgf + gaussian_obs` | simulation/fitting/workflow parity | OPEN |
| D08 | Continuous uHGF | `uhgf + gaussian_obs` | simulation/fitting/workflow parity | OPEN |
| D09 | Prior predictive sampling | `sampleModel` on binary HGF configs | Python equivalent and result semantics | CORE M11 PARITY ESTABLISHED; DEMO WRAPPER OPEN |
| D10 | Posterior Corr/Sigma inspection | `fit_plotCorr`, `optim.Corr`, `optim.Sigma` | numerical Corr/Sigma parity and equivalent plotting/example surface | NUMERICAL CORE PASS; DEMO/PLOT SURFACE OPEN |
| D11 | Residual diagnostics | `fit_plotResidualDiagnostics` | equivalent residual outputs/diagnostic workflow | OPEN |
| D12 | Bayesian parameter averaging | `bayesian_parameter_average` | function/workflow parity as part of v1 exact-toolbox scope | OPEN |

## D02 frozen reference contract — PASS

The official demo states that the following native perceptual parameter vector leads to an error in classic HGF while eHGF can handle it:

```text
[NaN, 0, 1, NaN, 1, 1, NaN, 0, 0, 1, 1.5, NaN, -4, 3]
```

on the official 320-trial `demo/example_binary_input.txt` sequence.

D02 PASS requires all of the following on the **same inputs and native parameters**:

1. frozen MATLAB classic `hgf_binary` fails;
2. HGFX classic `hgf_binary` fails correspondingly;
3. frozen MATLAB `ehgf_binary` succeeds;
4. HGFX `ehgf_binary` succeeds;
5. successful eHGF trajectories and inference states agree numerically within the established forward-parity tolerance.

All five conditions passed.

### D02 evidence

- HGFX head: `a074263b7139d4441caeb7a0d837d688626c5f58`
- workflow: `M18 Demo Model Selection Parity`
- run: `34684401843`
- job: `103528739680`
- conclusion: **SUCCESS**
- reference-freeze guard: PASS, exact HGF 8.2.0 commit, 334 MATLAB files
- classification: `PASS_MODEL_SELECTION_PARITY`
- MATLAB classic HGF: FAIL, `tapas:hgf:NegPostPrec`, `Negative posterior precision. Parameters are in a region where model assumptions are violated.`
- HGFX classic HGF: FAIL with the corresponding negative-posterior-precision validation error
- MATLAB eHGF: SUCCESS
- HGFX eHGF: SUCCESS
- eHGF trajectory/inference-state comparison: PASS; `mismatches=[]`
- artifact: `m18-demo-model-selection-evidence`, ID `10294714175`
- artifact ZIP SHA-256: `2aa62628d16198f8f335b56fca0f015303439406bb278a329b4cae09b9e69afd`

A result where HGFX forced classic HGF to succeed would **not** be considered better compatibility; it would be a reference-behaviour mismatch unless explicitly introduced in a post-v1 extension mode.

## Product interpretation

The official demo itself documents why model-family awareness matters:

- eHGF supports a broader parameter region than classic HGF;
- uHGF is provided for parameter regions where classic HGF can fail;
- for binary time series with implausible large excursions, the demo introduces `uhgf_ar1_binary` and explicitly encourages AR(1) models as a default modelling choice.

These are part of the MATLAB toolbox's scientific workflow and therefore part of HGFX v1 compatibility, not exceptions to it.

Execution order and acceptance dependencies: [M18 completion plan](../planning/M18_COMPLETION_PLAN.md). D02/D04 forward checks do not by themselves close fit/sim/plot workflows.
