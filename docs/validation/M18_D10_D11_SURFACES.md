# M18 D10/D11 — Analysis and Residual Diagnostic Surfaces

Status: **IMPLEMENTED / VALIDATION PENDING**

Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.

D10 covers the `fit_plotCorr` surface and the corresponding `optim.Corr`/`optim.Sigma` data. D11 covers `fit_plotResidualDiagnostics`: residual time series, shifted residual autocorrelation with MATLAB lag indexing, and residuals against predictions.

## Frozen gate v2

The gate uses a deterministic **fit-like result fixture** containing exactly the fields consumed by the two frozen MATLAB plotting utilities. This deliberately isolates surface semantics from simulation/fitting behavior: optimized-parameter labels are derived from MATLAB struct field expansion and prior variances, while Corr/Sigma/res/resAC/yhat are copied directly from the fixture.

Acceptance compares:

- D10 optimized-parameter labels in MATLAB struct-field expansion order;
- D10 `Corr` and `Sigma`;
- D11 residuals;
- D11 `fftshift(resAC)` and lag vector;
- D11 predictions used for the residual scatter.

Numerical tolerance is `rtol=3e-8`, `atol=3e-10`. Plot pixels, GUI window positions, fonts, and backend-specific rendering are intentionally not scientific acceptance criteria. Public aliases `fit_plotCorr` and `fit_plotResidualDiagnostics` are provided, with matplotlib loaded lazily via the `plot` extra.

## Preserved harness history

Protocol v1 attempted to create the fixture through an HGF binary simulation. Run `34846788533` failed inside MATLAB `simModel` before any Python/MATLAB surface comparison because that simulation entered an invalid variational-approximation region. Unit surface tests had already passed. No scientific result was produced by v1. The v2 fixture removes this unrelated upstream dependency; no acceptance tolerance or plotted-surface algorithm was changed in response to a scientific result.
