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

## M15

CPU/JAX fitting validation:

```bash
pytest tests/cpu_gpu/test_m15_gpu_fitting.py -q
```

Physical GPU fitting validation:

```bash
HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m15_gpu_fitting.py::test_real_gpu_fitting_parity_when_available \
  -q
```

When `HGFX_REQUIRE_GPU=1`, absence of a JAX GPU is a failure rather than a skip.

The workflows `.github/workflows/m14-gpu-engine.yml` and
`.github/workflows/m15-gpu-fitting.yml` expose strict jobs targeting a
`[self-hosted, linux, x64, gpu]` runner.
