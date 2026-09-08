# M14 — GPU Engine Gate

Status: **IMPLEMENTED — REAL GPU VALIDATION PENDING**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scientific scope

M14 owns the JAX fast execution engine, not GPU optimization. The formal milestone
gate remains: **CPU/GPU float64 forward and objective parity**. GPU fitting and
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

## Validation

CPU JAX x64 validation must compare:

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

Setting `HGFX_REQUIRE_GPU=1` turns absence of a GPU into a test failure. The CI
workflow exposes this through a manually dispatched self-hosted
`[self-hosted, linux, x64, gpu]` job.

## Infrastructure status

This repository is owned by a personal GitHub account. GitHub-hosted GPU larger
runners are not available as the standard `ubuntu-latest` runner here, and no
repository self-hosted GPU runner is currently configured.

Therefore M14 must **not** be marked PASS from CPU-only evidence. It becomes PASS only
after the real-GPU job completes successfully on physical GPU hardware.

## Current evidence

Branch workflow `34242409271`:

- frozen reference verification: PASS;
- M14 JAX CPU x64 parity suite: **9 passed**;
- real GPU test: **1 skipped** because no GPU device exists on the hosted runner;
- full regression: **80 passed, 1 GPU-only skipped**.

No CPU/JAX tolerance was relaxed to obtain these results.

Workflow: `.github/workflows/m14-gpu-engine.yml`.
