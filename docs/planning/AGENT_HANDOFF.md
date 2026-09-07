# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M5 — eHGF Forward Parity`

## Frozen reference

HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Completed gates

- M0 — Reference Frozen
- M1 — Golden Harness Operational
- M2 — Parameter/Config Parity
- M3 — Scalar Numerical Parity
- M4 — HGF Forward Parity

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

## Next tasks

1. Assemble eHGF binary and continuous forward paths using the shared B02–B10 core.
2. Export dedicated eHGF MATLAB trajectory fixtures.
3. Golden-test regular and irregular+ignored eHGF trajectories.
4. Validate eHGF safe precision-update semantics and edge cases.
5. Keep standard HGF M4 fixtures as regression gates.

## Do not start with

- GPU optimization
- full repo translation
- plotting
- performance micro-optimizations
