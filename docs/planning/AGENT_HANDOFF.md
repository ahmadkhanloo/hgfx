# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M4 — HGF Forward Parity`

## Frozen reference

HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Completed gates

- M0 — Reference Frozen
- M1 — Golden Harness Operational
- M2 — Parameter/Config Parity
- M3 — Scalar Numerical Parity

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

1. Port and golden-test `hgf_prediction`.
2. Port and golden-test `hgf_pihat` / `hgf_pihat_last`.
3. Port binary level-1 and level-2 update blocks.
4. Port continuous level-1 update.
5. Port volatility prediction-error and update blocks.
6. Add trajectory validation and assemble standard HGF forward parity fixtures.

## Do not start with

- GPU optimization
- full repo translation
- plotting
- performance micro-optimizations
