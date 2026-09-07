# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M2 — Parameter/Config Parity`

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

1. Define canonical parameter/config schema.
2. Preserve MATLAB parameter ordering.
3. Implement transformed/native parameter semantics.
4. Implement prior and fixed/free semantics.
5. Add placeholder, irregular-trial-mask, and time-axis representations.
6. Create config/parameter golden fixtures before model equations are ported.

## Do not start with

- GPU optimization
- full repo translation
- plotting
- performance micro-optimizations
