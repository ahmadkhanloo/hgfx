# HGFX Architecture

## Two public modes

### Compatibility mode
Goal: scientific behavior as close as practical to frozen MATLAB HGF behavior.

```text
MATLAB-like configs
        ↓
compatibility adapters
        ↓
shared JAX mathematical core
        ↓
compat optimizer/statistics
```

### Fast mode
Goal: high-throughput GPU-native fitting.

```text
native Python config
        ↓
shared JAX mathematical core
        ↓
jit / scan / vmap
        ↓
GPU optimizer
        ↓
batch scheduler
```

## Shared core principle

Do not maintain two mathematical implementations unless absolutely necessary.

Preferred:

```text
one mathematical core
+ compatibility adapters
+ fast execution layer
```

## JAX mapping

- trial recurrence → `jax.lax.scan`
- subjects → `jax.vmap`
- restarts → `jax.vmap`
- gradients → `jax.grad`
- fast Hessian → `jax.hessian`
- compilation → `jax.jit`

## Extension points

A custom model should override only the equations it changes.

Target protocols:

```python
class PerceptualModel:
    def init_state(...): ...
    def step(...): ...

class ResponseModel:
    def log_prob(...): ...
    def simulate(...): ...

class Coupling:
    def predict(...): ...
    def update(...): ...
```
