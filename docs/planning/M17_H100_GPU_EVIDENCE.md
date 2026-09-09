# M17 — Physical H100 Multi-GPU Evidence

Date: 2026-09-09

Status: **PASS — CORRECTNESS VALIDATED + SHARED-SERVER SCALING RECORDED**

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

A shared-server scaling benchmark was subsequently completed and is accepted as the
project's operational performance evidence. It is not interpreted as uncontended peak
H100 scaling.


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


## Shared-server scaling benchmark

Benchmark configuration:
- `CUDA_VISIBLE_DEVICES=0,1,2,3,5`
- GPU counts: 1, 2, 4
- subjects: 64
- trials: 128
- extra restarts: 1
- warmups: 1
- repeats: 3
- statistic: median wall time

Results:

| GPUs | Median time (s) | Subjects/s | Fits/s | Speedup | Efficiency |
|---:|---:|---:|---:|---:|---:|
| 1 | 81.719055 | 0.783 | 1.566 | 1.000 | 1.000 |
| 2 | 73.838342 | 0.867 | 1.734 | 1.107 | 0.553 |
| 4 | 58.860710 | 1.087 | 2.175 | 1.388 | 0.347 |

The server could not provide fully idle GPUs. Therefore these measurements intentionally
characterize HGFX under realistic shared-node contention. The observed trend is still
monotonic: 4 GPUs increase throughput from 0.783 to 1.087 subjects/s and reduce median
wall time from 81.719 s to 58.861 s.

No claim of ideal linear scaling or uncontended peak H100 performance is made.

**M17 is closed as PASS.**
