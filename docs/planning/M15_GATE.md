# M15 — GPU Fitting Gate

Status: **IMPLEMENTED — REAL GPU VALIDATION PENDING**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scope

M15 adds gradient-based fitting to the M14 JAX fast path. It does not replace the
M9 compatibility optimizer and does not own heterogeneous batching or multi-GPU
scheduling.

The first fitting-critical slice remains the validated
`hgf_binary + unitsq_sgm` MAP objective.

## Implemented

- exact M9 free/fixed transformed-parameter vector reused for the JAX fit problem;
- differentiable M14 objective with `jax.value_and_grad`;
- optimizer abstraction through `DeviceOptimizer`;
- JAX BFGS backend;
- optimizer position, gradient, inverse Hessian, status, and scalar objective kept
  as JAX arrays on the selected device;
- final transformed parameter vector reconstruction;
- final fast objective recomputation;
- final fast forward trajectory recomputation;
- CPU x64 gradient comparison against finite differences of the compatibility
  objective;
- CPU x64 final objective/trajectory comparison against the validated compatibility
  implementation;
- strict CPU/GPU fitting parity test.

## Compatibility boundary

M9 remains the frozen MATLAB-compatible optimizer behavior. M15 is a separate
high-throughput optimizer path under `hgfx.gpu`. Its acceptance criterion is
scientific equivalence of the objective and final trajectory, not iteration-by-
iteration identity with MATLAB BFGS.

## Formal gate

CPU/JAX must pass:

1. fast scalar objective equals the M8/M9 compatibility objective;
2. JAX gradient agrees with an independent numerical derivative of compatibility mode;
3. device-resident BFGS improves the MAP objective;
4. recomputing the final objective returns the optimizer value;
5. final JAX trajectories agree with compatibility trajectories;
6. the full regression suite remains green.

Physical GPU must additionally pass:

1. JAX reports a real GPU;
2. optimizer state remains on that GPU;
3. CPU and GPU final objective values agree;
4. CPU and GPU fitted free parameters agree;
5. CPU and GPU final trajectories agree.

Setting `HGFX_REQUIRE_GPU=1` makes absence of a GPU a test failure.

## Hardware dependency

M15 is not formally PASS until both M14 physical forward/objective parity and M15
physical fitting parity have run successfully on a real JAX-capable NVIDIA GPU.

Required M15 command:

```bash
HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m15_gpu_fitting.py::test_real_gpu_fitting_parity_when_available \
  -q
```

The repository workflow `.github/workflows/m15-gpu-fitting.yml` also exposes a
manual self-hosted GPU gate.

## Boundary to M16

M16 owns subject batching, restart batching, heterogeneous scheduling, and
single-vs-batch equivalence. M15 intentionally validates a single fit on one device.
