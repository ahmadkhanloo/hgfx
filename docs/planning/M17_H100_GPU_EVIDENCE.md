# M17 — Physical H100 Multi-GPU Evidence

Date: 2026-09-09

Status: **CORRECTNESS VALIDATED — SCALING BENCHMARK PENDING**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Source under test

The validation was executed from a GitHub source archive corresponding to:

`e6f1740ec6cacc55323c6a4d4ca521430c9f3dbf`

The archive had no `.git` metadata. The validation harness was locally adjusted only
to record `HGFX_SOURCE_REVISION`; no scientific or GPU implementation code was changed.

## Hardware / runtime

- GPU: NVIDIA H100 80GB HBM3
- driver: 550.163.01
- CUDA reported by NVIDIA-SMI: 12.4
- Python: 3.11.7
- JAX: 0.10.2
- JAXLIB: 0.10.2
- backend: GPU
- physical GPUs exposed through `CUDA_VISIBLE_DEVICES=0,1,2,3,5,6`
- JAX visible logical devices: six CUDA devices, logical ids 0..5
- `XLA_PYTHON_CLIENT_PREALLOCATE=false`

## Physical validation results

Strict hardware tests:

- M14 forward/objective GPU parity: **1 passed in 7.46s**
- M15 GPU fitting parity: **1 passed in 17.72s**
- M16 GPU batch parity/device residency: **1 passed in 20.69s**
- M17 real two-GPU multi-device parity/device residency: **1 passed in 29.25s**
- combined M14-M17 CPU/GPU modules: **23 passed in 144.23s**

The M17 strict test used the first two JAX-visible devices, which map to physical GPUs
0 and 1 under the selected `CUDA_VISIBLE_DEVICES` list.

The M17 test compares single-GPU and two-GPU results for objective values, fitted free
parameters, and inference trajectories, and verifies per-shard device residency.

## Runtime warning

During the M17 strict test JAX emitted:

`cuda_timer.cc:88 Delay kernel timed out: measured time has sub-optimal accuracy`

The test itself passed. NVIDIA-SMI captured at the start of validation showed substantial
concurrent load on some GPUs, including physical GPU 1, so this warning is treated as a
timing-quality warning rather than numerical correctness evidence.

## Interpretation

This run closes the physical correctness gate for M14-M17. It does **not** constitute a
valid throughput or strong-scaling benchmark because several GPUs were concurrently busy.

A controlled scaling run (1/2/4/6 or 1/2/4/8 GPUs) remains required for performance
claims and the Methods-paper reproducibility package.


## Repeat validation run

A second physical validation run was executed from the same source archive with:

`CUDA_VISIBLE_DEVICES=0,1,2,3,5`

JAX exposed five logical CUDA devices.

Results:
- M14 strict GPU parity: **1 passed in 6.42s**
- M15 strict GPU fitting parity: **1 passed in 16.16s**
- M16 strict GPU batch parity/device residency: **1 passed in 20.15s**
- M17 strict real two-GPU parity/device residency: **1 passed in 28.59s**
- combined M14-M17 modules: **23 passed in 138.37s**

No `cuda_timer` timing warning was emitted in this repeat run.

This repeat independently confirms the M14-M17 physical correctness result.
