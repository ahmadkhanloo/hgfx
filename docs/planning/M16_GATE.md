# M16 — Batch Engine Gate

Status: **IMPLEMENTED — CPU/JAX VALIDATION IN PROGRESS**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scope

M16 owns high-throughput batching on top of the M14 fast engine and M15 gradient
fitting path. It does not change compatibility semantics and does not own multi-GPU
scheduling.

The first gated slice is `hgf_binary + unitsq_sgm`.

## Implemented

- subject batching with `jax.vmap`;
- restart batching with nested `jax.vmap`;
- shape-homogeneous scheduler keyed by:
  - model,
  - observation model,
  - trial-length bucket,
  - restart count,
  - dtype;
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
semantics with minimum objective selection.

M16's acceptance criterion is numerical equivalence between repeated single M15 fits
and batched M16 fits.

## Formal gate

CPU/JAX must pass:

1. scheduler groups only shape-compatible subjects;
2. default-start subject batching matches repeated single M15 fits;
3. restart batching matches independent single-start optimization;
4. heterogeneous trial lengths preserve final objective and trajectory equivalence;
5. compile cache reuses group runners for repeated compatible workloads;
6. all returned arrays stay on the selected JAX device;
7. full regression remains green.

Physical GPU throughput benchmarking is intentionally deferred until M14/M15 hardware
validation is available. M16 may be software-complete and CPU-gated before that
hardware evidence.

## Boundary to M17

M17 owns actual multi-device scheduling, data-parallel partitioning, and multi-GPU
benchmarking. M16 is strictly single-device batching.
