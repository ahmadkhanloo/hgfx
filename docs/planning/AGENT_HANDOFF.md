# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M7 — Observation Parity`

## Frozen reference

HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Completed gates

- M0 — Reference Frozen
- M1 — Golden Harness Operational
- M2 — Parameter/Config Parity
- M3 — Scalar Numerical Parity
- M4 — HGF Forward Parity
- M5 — eHGF Forward Parity
- M6 — uHGF Forward Parity

M1 bootstrap path:

```text
frozen MATLAB tapas_logit
→ JSON export
→ canonical HGFX fixture (JSON + NPZ)
→ independent Python computation
→ first-divergence numerical diff
```

The automated gate is `.github/workflows/m1-golden-harness.yml`.

## M4 evidence

- Standard binary + continuous HGF forward parity: PASS
- Regular and irregular+ignored trajectory fixtures: PASS
- Shared B02–B10 building blocks: PASS
- M4 workflow run: `34120120732`
- Regression runs: M1 `34120120741`, M2 `34120120738`, M3 `34120120734`

## M5 evidence

- eHGF binary + continuous forward parity: PASS
- regular and irregular+ignored trajectory fixtures: PASS
- safe precision-update edge case: PASS
- M5 workflow run: `34123043904`
- standard HGF M4 regression on the unified core: PASS

## M6 evidence

- uHGF binary + continuous forward parity: PASS
- regular and irregular+ignored trajectory fixtures: PASS
- Lambert W0 mode-finding diagnostics: PASS
- dual quadratic approximations: PASS
- variational-energy softmax weighting: PASS
- Gaussian-mixture moment matching: PASS
- extreme log-space / non-finite second-expansion fallback: PASS
- HGF + eHGF + uHGF Python regression suite: PASS
- M6 workflow run: `34125217371`

## Next tasks

1. Port the P0/P1 observation families beginning with unit-square sigmoid.
2. Export trial-wise MATLAB likelihood fixtures and total likelihood.
3. Preserve response-model transformed/native parameter semantics.
4. Golden-test binary softmax, softmax, Gaussian, and priority response families.
5. Keep M4/M5/M6 forward gates as regressions while observation parity is added.

## Do not start with

- GPU optimization
- full repo translation
- plotting
- performance micro-optimizations
