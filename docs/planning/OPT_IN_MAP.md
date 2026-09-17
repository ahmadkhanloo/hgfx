# Opt-in MAP solver

Status: **additive / not a v1 compatibility change**
Recorded: 2026-09-18

`hgfx.fit_model` still uses the frozen MATLAB `quasinewton` path. That contract
is the methods-paper claim and must stay bit-stable.

The production opt-in engine is SciPy `L-BFGS-B`:

```bash
pip install 'hgfx[optim]'
```

If SciPy is missing, HGFX falls back to the internal L-BFGS. Install SciPy for
analysis work.

## API

```python
from hgfx.optim import MapOptions, fit_map, minimize_map, multi_start_map

# Same objective as fit_model, better optimizer:
fit = fit_map(y, u, n_random_starts=8)

# Custom objective (dual-stream wrapper, etc.):
result = multi_start_map(
    neg_log_joint,
    x0,
    n_random_starts=8,
    options=MapOptions(solver="scipy", method="L-BFGS-B", gradient="finite"),
)
```

`fit_model` remains the MATLAB-parity path. `fit_map` / `minimize_map` are the
tighter MAP path.

## Gradient rules

| `gradient` | When to use |
|---|---|
| `finite` | Default with SciPy. Works with NumPy HGFX models. |
| `ridders` | Same models, slower, closer to the TAPAS gradient estimator. |
| `jax` | Only if the objective is JAX-traceable end-to-end. |
| user `jac` | Best option when you have an analytic or JAX gradient of *your* wrapper. |

## What this is not

- Not a change to `fit_model` defaults.
- Not v2.
- Not a claim that recovery or LME improved for paper 1.
- Not a PyMC/NUTS path.
