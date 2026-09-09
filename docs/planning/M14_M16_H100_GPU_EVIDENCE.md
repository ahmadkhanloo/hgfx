# Physical H100 GPU Validation — M14/M15/M16

Date: 2026-09-09

Validated commit: `45139c07ec90a7558e3ace0d36fb7a56754539c1`  
Branch: `work/m16-batch-engine`  
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Hardware / software

- Physical GPU selected with `CUDA_VISIBLE_DEVICES=1`: NVIDIA H100 80GB HBM3
- NVIDIA-SMI driver: 550.163.01
- NVIDIA-SMI reported CUDA compatibility: 12.4
- Python: 3.11.7
- JAX: 0.10.2
- JAXLIB: 0.10.2
- JAX backend: `gpu`
- JAX-visible device: `CudaDevice(id=0)`

The JAX device is numbered 0 inside the process because only physical GPU 1 was exposed through `CUDA_VISIBLE_DEVICES=1`.

## Strict physical-GPU results

M14 forward/objective parity:

```text
1 passed in 4.95s
```

M15 fitting parity:

```text
1 passed in 14.43s
```

M16 batch parity:

```text
1 passed in 21.87s
```

Combined M14-M16 CPU/GPU test modules with `HGFX_REQUIRE_GPU=1`:

```text
20 passed in 112.97s (0:01:52)
```

## Commands

```bash
CUDA_VISIBLE_DEVICES=1 HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m14_fast_engine.py::test_real_gpu_forward_and_objective_parity_when_available \
  -q -s

CUDA_VISIBLE_DEVICES=1 HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m15_gpu_fitting.py::test_real_gpu_fitting_parity_when_available \
  -q -s

CUDA_VISIBLE_DEVICES=1 HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m16_batch_engine.py::test_real_gpu_batch_parity_when_available \
  -q -s

CUDA_VISIBLE_DEVICES=1 HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m14_fast_engine.py \
  tests/cpu_gpu/test_m15_gpu_fitting.py \
  tests/cpu_gpu/test_m16_batch_engine.py \
  -q -s
```

## Lineage validation

The physical validation was executed on the stacked M16 head.

- M14 PR head: `695fd548a52375d01ae48c145afc933d0ad3d703`
- M15 PR head: `cbb5ba2142b7018e2884b9fd3c608054b236bcab`
- validated M16 head: `45139c07ec90a7558e3ace0d36fb7a56754539c1`

GitHub compare confirms that no M14 engine/test files changed between the M14 head and the validated M16 head, and no M15 fitting/test files changed between the M15 head and the validated M16 head. The physical run therefore validates the corresponding M14 and M15 implementations in the stacked lineage.

## Gate conclusion

- **M14: PASS** — physical H100 CPU/GPU float64 forward/objective parity established.
- **M15: PASS** — physical H100 fitting/objective/parameter/trajectory/device-residency parity established.
- **M16: PASS / GPU VALIDATED** — strict physical-GPU batch parity and device-residency gate established.

Throughput, scaling, and multi-GPU performance benchmarking are not inferred from these parity tests. Those measurements belong to M17 and the Methods benchmark program.
