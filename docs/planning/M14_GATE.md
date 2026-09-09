# M14 — GPU Engine Gate

Status: **PASS — PHYSICAL H100 GPU VALIDATED**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scientific scope

M14 owns the JAX fast execution engine, not GPU optimization. The formal milestone
gate is **CPU/GPU float64 forward and objective parity**. GPU fitting and
on-device optimizer state are M15; heterogeneous production batching is M16.

## Implemented fast path

- trial recursion uses `jax.lax.scan`;
- same-shape vectorization primitive uses `jax.vmap`;
- forward and objective callables are compiled with `jax.jit`;
- float64 is explicitly enabled;
- inputs/parameters can be explicitly placed on a selected JAX device;
- compile signatures include model, levels, observation model, dtype,
  trial-length bucket, and static options;
- power-of-two trial bucketing/padding is available for stable compilation shapes.

The first scientifically gated fast slice is the fitting-critical binary
HGF/eHGF/uHGF forward recursion plus the M8
`hgf_binary + unitsq_sgm` fixed-parameter objective.

## Compatibility boundary

The M4-M13 NumPy/MATLAB-compatible implementation is unchanged. Fast mode lives
under `hgfx.gpu`; it does not replace compatibility semantics.

## Validation requirements

CPU JAX x64 validation compares:

- HGF, eHGF, and uHGF trial trajectories;
- ignored-trial copy semantics;
- irregular-interval semantics;
- inference-state arrays;
- the M8 objective decomposition;
- `vmap` output against repeated single forward;
- JIT compile-cache reuse.

The physical-GPU test additionally requires:

- JAX reports a real `gpu` device;
- arrays remain on that GPU;
- CPU and GPU float64 forward results agree;
- CPU and GPU float64 objective results agree.

Setting `HGFX_REQUIRE_GPU=1` turns absence of a GPU into a test failure.

## Evidence

Hosted CPU/JAX workflow `34242409271`:

- frozen reference verification: PASS;
- M14 JAX CPU x64 parity suite: **9 passed**;
- hosted physical GPU test: skipped because no GPU device exists on the hosted runner;
- full regression: **80 passed, 1 GPU-only skipped**.

Physical GPU validation on 2026-09-09:

- validated stacked commit: `45139c07ec90a7558e3ace0d36fb7a56754539c1`;
- M14 implementation head: `695fd548a52375d01ae48c145afc933d0ad3d703`;
- GPU: **NVIDIA H100 80GB HBM3**, physical device 1;
- driver: 550.163.01;
- NVIDIA-SMI reported CUDA compatibility: 12.4;
- Python: 3.11.7;
- JAX/JAXLIB: 0.10.2 / 0.10.2;
- backend: `gpu`;
- strict M14 physical-GPU test: **1 passed in 4.95s**;
- combined M14-M16 strict suite: **20 passed in 112.97s**.

GitHub lineage comparison confirms no M14 engine/test files changed between the M14
head and the validated stacked commit.

No parity tolerance was relaxed to obtain these results.

See `docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## Gate conclusion

**M14 PASS.** Physical H100 CPU/GPU float64 forward/objective parity and GPU device
residency are established. M15 is therefore no longer blocked by M14 hardware
validation.
