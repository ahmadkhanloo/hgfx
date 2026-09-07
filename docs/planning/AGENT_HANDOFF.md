# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M3 — Scalar Numerical Parity`

## Frozen reference

HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Completed gates

- M0 — Reference Frozen
- M1 — Golden Harness Operational

M1 bootstrap path:

```text
frozen MATLAB tapas_logit
→ JSON export
→ canonical HGFX fixture (JSON + NPZ)
→ independent Python computation
→ first-divergence numerical diff
```

The automated gate is `.github/workflows/m1-golden-harness.yml`.

## Next tasks

1. Port and golden-test `tapas_logit`.
2. Port and golden-test `tapas_sgm`.
3. Port and golden-test `boltzmann`.
4. Port and validate `lambert_w0`.
5. Port and validate `nearest_psd` and `tapas_Cov2Corr`.
6. Port Ridders numerical derivatives only after scalar utility parity is established.

## Do not start with

- GPU optimization
- full repo translation
- plotting
- performance micro-optimizations
