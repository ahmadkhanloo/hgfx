# MATLAB Demo Model-Selection Matrix

## Purpose

This matrix turns the frozen HGF Toolbox 8.2.0 official demo into explicit v1.0 product acceptance cases.

Reference: `demo/hgf_demo.m` at HGF Toolbox commit `2437f4dc241541072722a2695ddeca7b44d83dd3`.

The governing rule is **reference-aware parity**: HGFX must reproduce the MATLAB toolbox's valid workflow and model choice. It is not required to make classic HGF succeed where the MATLAB demo itself switches to eHGF, uHGF, AR(1), or another model family.

## Cases

| ID | Official MATLAB demo case | Reference model/workflow | HGFX requirement | Status |
|---|---|---|---|---|
| D01 | Binary HGF fit/sim/recovery on `example_binary_input.txt` | `hgf_binary + unitsq_sgm` | fit/sim/trajectory/statistics parity | CORE PARITY PREVIOUSLY ESTABLISHED; DEMO WRAPPER OPEN |
| D02 | Parameter regime documented to fail in classic HGF but succeed in eHGF | classic `hgf_binary` must fail; `ehgf_binary + unitsq_sgm` must succeed | reproduce both the classic-HGF limitation and eHGF success on identical official input/parameters | CI GATE ADDED — RUN PENDING |
| D03 | uHGF binary comparison in a region where classic HGF can work | `uhgf_binary + unitsq_sgm` | reproduce uHGF trajectory/workflow | OPEN |
| D04 | Extreme binary regime followed by AR(1) regularisation | `uhgf_binary`, then `uhgf_ar1_binary` | reproduce the demo's model change; do not require base HGF to solve it | OPEN |
| D05 | Alternative learning model on the same binary responses | `rw_binary + unitsq_sgm` | fit and output compatibility | OPEN |
| D06 | Continuous USD/CHF classic HGF | `hgf + gaussian_obs` | Bayes-optimal fit, sim, fit-back, trajectory/statistics parity | OPEN |
| D07 | Continuous eHGF | `ehgf + gaussian_obs` | simulation/fitting/workflow parity | OPEN |
| D08 | Continuous uHGF | `uhgf + gaussian_obs` | simulation/fitting/workflow parity | OPEN |
| D09 | Prior predictive sampling | `sampleModel` on binary HGF configs | Python equivalent and result semantics | CORE M11 PARITY ESTABLISHED; DEMO WRAPPER OPEN |
| D10 | Posterior Corr/Sigma inspection | `fit_plotCorr`, `optim.Corr`, `optim.Sigma` | numerical Corr/Sigma parity and equivalent plotting/example surface | NUMERICAL CORE PASS; DEMO/PLOT SURFACE OPEN |
| D11 | Residual diagnostics | `fit_plotResidualDiagnostics` | equivalent residual outputs/diagnostic workflow | OPEN |
| D12 | Bayesian parameter averaging | `bayesian_parameter_average` | function/workflow parity if required by v1 exact-toolbox scope | OPEN |

## D02 frozen reference contract

The official demo states that the following native perceptual parameter vector leads to an error in classic HGF while eHGF can handle it:

```text
[NaN, 0, 1, NaN, 1, 1, NaN, 0, 0, 1, 1.5, NaN, -4, 3]
```

on the official 320-trial `demo/example_binary_input.txt` sequence.

D02 PASS therefore requires all of the following on the **same inputs and native parameters**:

1. frozen MATLAB classic `hgf_binary` fails;
2. HGFX classic `hgf_binary` fails correspondingly;
3. frozen MATLAB `ehgf_binary` succeeds;
4. HGFX `ehgf_binary` succeeds;
5. successful eHGF trajectories and inference states agree numerically within the established forward-parity tolerance.

A result where HGFX forces classic HGF to succeed is **not** considered better compatibility; it is a reference-behaviour mismatch unless explicitly introduced in a post-v1 extension mode.

## Product interpretation

The official demo itself documents why model-family awareness matters:

- eHGF supports a broader parameter region than classic HGF;
- uHGF is provided for parameter regions where classic HGF can fail;
- for binary time series with implausible large excursions, the demo introduces `uhgf_ar1_binary` and explicitly encourages AR(1) models as a default modelling choice.

These are part of the MATLAB toolbox's scientific workflow and therefore part of HGFX v1 compatibility, not exceptions to it.
