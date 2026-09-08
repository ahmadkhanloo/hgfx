# M16 — Batch Engine Gate

Status: **CPU/JAX PASS — PHYSICAL GPU PERFORMANCE EVIDENCE DEFERRED**

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
- heterogeneous-length scheduler/cache reuse tests.

## Scientific boundary

M10 remains the compatibility specification for LME-based restart selection. M16
returns every independent restart result and does not silently replace M10 selection
semantics with minimum-objective selection.

M16's acceptance criterion is numerical equivalence between repeated single M15 fits
and batched M16 fits.

## Gate evidence

Workflow `34253080856` on commit
`42b6478827b75d11ae4b08a81d32d8e054705bb5`:

- frozen reference verification: **PASS**;
- M16 targeted CPU/JAX batch suite: **5 passed**;
- full regression: **88 passed, 2 GPU-only skipped**;
- workflow conclusion: **SUCCESS**.

This establishes the software/CPU-JAX M16 gate. Physical GPU throughput benchmarking
is intentionally deferred until M14/M15 hardware validation is available.

## Boundary to M17

M17 owns actual multi-device scheduling, data-parallel partitioning, and multi-GPU
benchmarking. M16 is strictly single-device batching.
