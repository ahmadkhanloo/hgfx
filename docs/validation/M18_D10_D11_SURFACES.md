# M18 D10/D11 — Analysis and Residual Diagnostic Surfaces

Status: **IMPLEMENTED / VALIDATION PENDING**

Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.

D10 covers the `fit_plotCorr` surface and the corresponding `optim.Corr`/`optim.Sigma` data. D11 covers `fit_plotResidualDiagnostics`: residual time series, shifted residual autocorrelation with MATLAB lag indexing, and residuals against predictions.

The frozen gate uses one deterministic binary-demo-family fit (`hgf_binary + unitsq_sgm`, simulation seed `123`). The MATLAB result is imported directly into the Python surface preparation functions. This isolates analysis/plot surface semantics from fitting parity.

Acceptance compares:

- D10 optimized-parameter labels in MATLAB struct-field expansion order;
- D10 `Corr` and `Sigma`;
- D11 residuals;
- D11 `fftshift(resAC)` and lag vector;
- D11 predictions used for the residual scatter.

Numerical tolerance is `rtol=3e-8`, `atol=3e-10`. Plot pixels, GUI window positions, fonts, and backend-specific rendering are intentionally not scientific acceptance criteria. Public aliases `fit_plotCorr` and `fit_plotResidualDiagnostics` are provided, with matplotlib loaded lazily via the `plot` extra.
