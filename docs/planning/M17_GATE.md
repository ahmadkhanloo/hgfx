# M17 — Multi-GPU Gate

Status: **IMPLEMENTED — PHYSICAL MULTI-GPU VALIDATION PENDING**

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

Scaling benchmarks for 1/2/4/8 GPUs are separate evidence. They should only be run
when selected GPUs are sufficiently idle to make throughput numbers interpretable.


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
