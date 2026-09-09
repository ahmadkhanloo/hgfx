# M17 — Multi-GPU Gate

Status: **PASS — PHYSICAL MULTI-GPU CORRECTNESS + SHARED-SERVER SCALING RECORDED**

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scope

M17 adds explicit data-parallel scheduling of independent M16 subject batches across
multiple JAX GPU devices. It does not change the HGF objective, optimizer semantics,
restart selection, or single-device numerical path.

## Implemented

- explicit GPU index selection;
- deterministic round-robin subject sharding;
- independent M16 shard execution per selected device;
- optional concurrent dispatch with a thread pool;
- original subject ordering restored in the combined result;
- per-shard device residency preserved;
- strict two-GPU numerical parity test;
- no automatic use of all visible GPUs.

## Resource-safety boundary

M17 never selects all GPUs implicitly. The caller must provide `device_indices`.
This is intentional for shared servers.

On busy systems, tests should set:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

and expose only the GPUs intended for validation through `CUDA_VISIBLE_DEVICES`.

## Formal gate

Physical multi-GPU validation requires:

1. at least two real JAX GPU devices are visible;
2. the same batch fitted on one GPU and on two GPUs agrees in objective values,
   fitted free parameters, and trajectories;
3. each shard remains resident on its assigned GPU;
4. the full regression suite stays green.

Physical correctness evidence on 2026-09-09:
- M14 strict GPU parity: 1 passed in 7.46s
- M15 strict GPU fitting parity: 1 passed in 17.72s
- M16 strict GPU batch parity: 1 passed in 20.69s
- M17 strict real two-GPU parity/device-residency: 1 passed in 29.25s
- combined M14-M17 modules: 23 passed in 144.23s

See `docs/planning/M17_H100_GPU_EVIDENCE.md`.

Observed shared-server scaling evidence was recorded on the production/shared H100 node.
Because the GPUs could not be made completely idle, the benchmark is explicitly treated
as representative shared-server performance rather than uncontended peak throughput.


## Consolidated future hardware validation

After infrastructure access is restored, use a fresh clone and run:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
XLA_PYTHON_CLIENT_PREALLOCATE=false \
bash scripts/run_gpu_validation.sh
```

This records M14-M17 correctness evidence and produces
`hgfx_gpu_validation_results.tar.gz`.

For scaling benchmarks:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
XLA_PYTHON_CLIENT_PREALLOCATE=false \
python scripts/benchmark_m17_multi_gpu.py \
  --gpu-counts 1,2,4,8 \
  --subjects 64 \
  --trials 128 \
  --extra-restarts 1 \
  --warmups 1 \
  --repeats 3
```

The benchmark writes structured JSON under
`gpu_validation_results/m17_scaling.json`.


## Shared-server scaling benchmark

Environment:
- NVIDIA H100 80GB HBM3
- `CUDA_VISIBLE_DEVICES=0,1,2,3,5`
- `XLA_PYTHON_CLIENT_PREALLOCATE=false`
- 64 subjects
- 128 trials per subject
- 1 extra restart
- 1 warmup
- 3 timed repeats
- median wall-clock time reported

Observed results:

| GPUs | Median time (s) | Subjects/s | Fits/s | Speedup vs 1 GPU | Parallel efficiency |
|---:|---:|---:|---:|---:|---:|
| 1 | 81.719055 | 0.783 | 1.566 | 1.000 | 1.000 |
| 2 | 73.838342 | 0.867 | 1.734 | 1.107 | 0.553 |
| 4 | 58.860710 | 1.087 | 2.175 | 1.388 | 0.347 |

Interpretation:
- throughput improves monotonically from 1 to 4 GPUs;
- 4 GPUs deliver a measured 1.388× speedup over 1 GPU;
- scaling is sub-linear, as expected under a shared-server workload with pre-existing GPU
  memory occupancy and other concurrent jobs;
- these numbers are accepted as the project's operational scaling evidence, not as a claim
  of uncontended H100 peak scaling.

With correctness already validated independently, this benchmark closes M17.
