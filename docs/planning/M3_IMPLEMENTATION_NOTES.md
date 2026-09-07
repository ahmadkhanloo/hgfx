# M3 — Scalar Numerical Parity implementation notes

Target gate: utility-level golden tests pass in CPU float64 against frozen HGF Toolbox 8.2.0 (`2437f4dc241541072722a2695ddeca7b44d83dd3`).

Implemented utility families:

- `tapas_logit` / `tapas_sgm`
- `boltzmann`
- `lambert_w0`
- `nearest_psd`
- `tapas_Cov2Corr`
- `riddersdiff`, `riddersdiff2`, `riddersdiffcross`, `riddersgradient`, `riddershessian`

Compatibility mode deliberately preserves reference algorithm choices including logit domain errors, Boltzmann overflow behavior, Lambert W0's fixed eight Halley iterations, iterative PSD projection, covariance validation order, and Ridders stopping/error semantics.

Validation assets:

- `tests/unit/test_scalar_math.py`
- `reference/matlab/export_m3_scalar_parity.m`
- `tools/check_m3_parity.py`
- `.github/workflows/m3-scalar-numerical-parity.yml`

Local pre-CI validation:

- Python scalar utility tests: 9/9 PASS

Do **not** mark M3 complete until the MATLAB-to-Python workflow passes on the frozen submodule.
