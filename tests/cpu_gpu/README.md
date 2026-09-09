# CPU/GPU Parity Tests

These tests compare JAX CPU float64 and JAX GPU float64 after CPU/reference parity is established.

## M14

CPU/JAX validation:

```bash
pytest tests/cpu_gpu/test_m14_fast_engine.py -q
```

Physical GPU validation must be strict:

```bash
HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m14_fast_engine.py::test_real_gpu_forward_and_objective_parity_when_available \
  -q
```

When `HGFX_REQUIRE_GPU=1`, absence of a JAX GPU is a failure rather than a skip.

The GitHub workflow `.github/workflows/m14-gpu-engine.yml` exposes the same check
through a manually dispatched job targeting `[self-hosted, linux, x64, gpu]`.
