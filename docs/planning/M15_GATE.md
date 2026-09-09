# M15 — GPU Fitting Gate

Status: **PASS — PHYSICAL H100 GPU VALIDATED**

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

CPU/JAX requires:

1. fast scalar objective equals the M8/M9 compatibility objective;
2. JAX gradient agrees with an independent numerical derivative of compatibility mode;
3. device-resident BFGS improves the MAP objective;
4. recomputing the final objective returns the optimizer value;
5. final JAX trajectories agree with compatibility trajectories;
6. the full regression suite remains green.

Physical GPU additionally requires:

1. JAX reports a real GPU;
2. optimizer state remains on that GPU;
3. CPU and GPU final objective values agree;
4. CPU and GPU fitted free parameters agree;
5. CPU and GPU final trajectories agree.

## Evidence

Hosted CPU/JAX M15 workflow: PASS on the stacked M15 implementation lineage.

Physical GPU validation on 2026-09-09:

- validated stacked commit: `45139c07ec90a7558e3ace0d36fb7a56754539c1`;
- M15 implementation head: `cbb5ba2142b7018e2884b9fd3c608054b236bcab`;
- prerequisite M14 physical gate: PASS;
- GPU: **NVIDIA H100 80GB HBM3**, physical device 1;
- driver: 550.163.01;
- NVIDIA-SMI reported CUDA compatibility: 12.4;
- Python: 3.11.7;
- JAX/JAXLIB: 0.10.2 / 0.10.2;
- backend: `gpu`;
- strict M15 physical-GPU fitting test: **1 passed in 14.43s**;
- combined M14-M16 strict suite: **20 passed in 112.97s**.

GitHub lineage comparison confirms that `src/hgfx/gpu/fitting.py` and
`tests/cpu_gpu/test_m15_gpu_fitting.py` did not change between the M15 head and
the validated stacked commit.

See `docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## Gate conclusion

**M15 PASS.** Physical H100 objective, fitted-parameter, final-trajectory, and
device-residency parity are established.

## Boundary to M16

M16 owns subject batching, restart batching, heterogeneous scheduling, and
single-vs-batch equivalence. M15 validates a single fit on one selected device.
