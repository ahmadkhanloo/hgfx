# Numerical Policy

## Scientific default

HGFX scientific validation uses:

```text
float64
```

with JAX x64 enabled.

## Validation hierarchy

```text
MATLAB reference float64
        ↓
JAX CPU float64
        ↓
JAX GPU float64
```

CPU parity is established before GPU performance work.

## Tolerance policy

There is no universal tolerance.

Tolerance classes are calibrated empirically for:
- scalar utilities;
- one-step updates;
- recursive trajectories;
- likelihoods;
- MAP parameters;
- Hessian;
- LME;
- CPU/GPU comparisons.

Any tolerance change requires:
1. failing example;
2. numerical explanation;
3. evidence that scientific conclusions are unchanged;
4. review.

## Optimization equivalence

Optimizers need not follow identical paths.

Acceptance is based on:
- final objective;
- resulting trajectories;
- parameter plausibility/recovery;
- repeatability;
- model comparison behavior.

## Forbidden shortcuts

- default float32 for validation;
- hiding divergence by clipping unless reference does so;
- silently changing parameter order;
- silently replacing numerical algorithms in compatibility mode.
