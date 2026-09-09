# M16 — Batch Engine Gate

Status: **PASS — PHYSICAL H100 GPU VALIDATED**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scope

M16 owns high-throughput batching on top of the M14 fast engine and M15 gradient
fitting path. It does not change compatibility semantics and does not own multi-GPU
scheduling.

The first gated slice is `hgf_binary + unitsq_sgm`.

## Implemented

- subject batching with `jax.vmap`;
- restart batching with nested `jax.vmap`;
- shape-homogeneous scheduler keyed by model, observation model, trial-length bucket,
  restart count, and dtype;
- explicit power-of-two trial buckets;
- safe zero padding plus ignored/regular masks for heterogeneous subject lengths;
- compiled group runners cached with HGFX compile signatures;
- batched BFGS over independent subject/restart fits;
- final objective recomputation for every restart;
- final trajectory recomputation for every restart;
- device-resident batch result arrays;
- single-vs-batch equivalence tests;
- restart-batch-vs-independent-fit equivalence tests;
- heterogeneous-length scheduler/cache reuse tests;
- strict physical CPU/GPU batch parity test.

## Scientific boundary

M10 remains the compatibility specification for LME-based restart selection. M16
returns every independent restart result and does not silently replace M10 selection
semantics with minimum-objective selection.

M16's acceptance criterion is numerical equivalence between repeated single M15 fits
and batched M16 fits. Throughput/scaling benchmarking is separate from this numerical
gate.

## CPU/JAX evidence

Workflow `34253080856` on commit
`42b6478827b75d11ae48c145afc933d0ad3d703`:

- frozen reference verification: **PASS**;
- M16 targeted CPU/JAX batch suite: **5 passed**;
- full regression: **88 passed, 2 GPU-only skipped**;
- workflow conclusion: **SUCCESS**.

The final strict-GPU-test head `45139c07ec90a7558e3ace0d36fb7a56754539c1`
also has successful GitHub Actions workflows, including M16 Batch Engine.

## Physical GPU evidence

Validation on 2026-09-09:

- commit: `45139c07ec90a7558e3ace0d36fb7a56754539c1`;
- GPU: **NVIDIA H100 80GB HBM3**, physical device 1;
- driver: 550.163.01;
- NVIDIA-SMI reported CUDA compatibility: 12.4;
- Python: 3.11.7;
- JAX/JAXLIB: 0.10.2 / 0.10.2;
- backend: `gpu`;
- strict M16 CPU/GPU batch parity/device-residency test: **1 passed in 21.87s**;
- combined M14-M16 strict suite: **20 passed in 112.97s**.

See `docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## Gate conclusion

**M16 PASS / GPU VALIDATED.** Numerical single-device batch parity and physical-GPU
device residency are established.

Physical throughput, memory-scaling, and multi-GPU benchmark measurements remain
future benchmark work; they are not inferred from the parity gate.

## Boundary to M17

M17 owns actual multi-device scheduling, data-parallel partitioning, multi-GPU
benchmarking, and scaling evidence. M16 is strictly single-device batching.
