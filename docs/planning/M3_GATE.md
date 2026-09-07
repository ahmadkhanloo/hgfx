# M3 — Scalar Numerical Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Validation workflow: `M3 Scalar Numerical Parity`
- Passing workflow run: `34114052778`

## Scope validated

- [x] `tapas_logit`: reference formula and domain-error semantics
- [x] `tapas_sgm`: reference sigmoid formula
- [x] `boltzmann`: beta parameter and reference overflow/NaN behavior
- [x] `lambert_w0`: negative-input NaN, small-z branch, reference initial guesses, exactly eight Halley iterations
- [x] `nearest_psd`: iterative symmetrize/eigenvalue-clip/reconstruct loop
- [x] `tapas_Cov2Corr`: validation order and covariance-to-correlation normalization
- [x] `riddersdiff`: first derivative
- [x] `riddersdiff2`: second derivative
- [x] `riddersdiffcross`: mixed derivative
- [x] `riddersgradient`: vector gradient
- [x] `riddershessian`: full Hessian
- [x] CPU float64 golden parity against frozen MATLAB reference

## Evidence

The MATLAB oracle exports deterministic reference outputs from the pinned HGF submodule. The Python checker independently evaluates HGFX implementations and compares each utility with calibrated float64 tolerances.

Passing jobs in workflow run `34114052778`:

- `python-scalar-tests`: PASS
- `matlab-python-scalar-parity`: PASS

Regression evidence on the corrected implementation:

- M1 Golden Harness run `34114052681`: PASS
- M2 Parameter/Config Parity run `34114052742`: reference export and MATLAB/Python comparison PASS

The first M3 CI attempt exposed a Python syntax-transfer defect in `covariance.py` (`||` instead of `or`). It was corrected before accepting the gate. The scientific comparison then passed without relaxing tolerances or changing the reference oracle to hide a mismatch.

## Compatibility decisions frozen by M3

Compatibility mode preserves the MATLAB algorithms where their numerical path can affect downstream fitting:

- no stabilized softmax substitution for `boltzmann`;
- fixed eight-iteration Halley implementation for `lambert_w0`;
- iterative PSD repair rather than a one-shot alternative;
- Ridders numerical differentiation retained for compatibility Hessian/LME work.

Fast/JAX-native alternatives may be introduced later only behind a separate native path and separate parity tests.

## Next milestone

`M4 — HGF Forward Parity`
