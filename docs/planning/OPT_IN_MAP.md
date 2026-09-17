# Opt-in MAP solver

Status: **additive / not a v1 compatibility change**
Recorded: 2026-09-18

`hgfx.fit_model` still uses the frozen MATLAB `quasinewton` path. That contract
is the methods-paper claim and must stay bit-stable.

This module exists because a TAPAS-compatible optimizer is not the same thing as
a good MAP optimizer. Use it from analysis code when the target is a tighter
point estimate on a known objective.

## API

```python
from hgfx.optim import MapOptions, minimize_map, multi_start_map

result = minimize_map(
    neg_log_joint,           # transformed-space objective
    x0,
    jac=None,                # optional exact gradient
    starts=None,             # extra deterministic restarts
    n_random_starts=4,
    options=MapOptions(gradient="finite"),  # or "ridders" / "jax"
)
```

`result.x` is the best free-parameter vector. `result.fun` is the minimized
value. This object is not a `QuasiNewtonResult` and must not be fed into frozen
LME-parity helpers unless you know they only need `arg_min`.

## Gradient rules

| `gradient` | When to use |
|---|---|
| `finite` | Default. Works with NumPy HGFX models (`hgf_ar1_binary`, dual-stream wrappers). |
| `ridders` | Same models, slower and closer to the TAPAS gradient estimator. |
| `jax` | Only if the objective is JAX-traceable end-to-end. Do not point this at NumPy forwards; the gradient will be wrong. |
| user `jac` | Best option when you have an analytic or JAX gradient of *your* wrapper. |

## What this is not

- Not a change to `fit_model` defaults.
- Not v2.
- Not a claim that recovery or LME improved for paper 1.
- Not a PyMC/NUTS path.
