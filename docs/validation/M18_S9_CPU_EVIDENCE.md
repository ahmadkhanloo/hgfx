# M18 S9 CPU backend evidence

Date: 2026-09-15
Protocol: `m18-s9-robustness-backend-1`
Numerical source commit: `9c53af707a60d27ee3d9d37e5122e7a0ba7d5460`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Result

**CPU backend classification: `PASS_CPU_BACKEND_EQUIVALENCE`.**

The post-repair GitHub Actions execution completed successfully on the frozen S9 CPU matrix:

- workflow run: `34901924475`
- job: `104169632034`
- artifact: `10371308067`
- artifact digest: `sha256:875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826`
- runner: `ubuntu-24.04`

The job executed the semantic-boundary regression, M14/M15 CPU backend regressions, and the frozen S9 robustness/backend matrix. Current numerical code therefore has no unresolved required CPU backend implementation mismatch under this protocol.

## Physical GPU disposition

S9 is **not fully closed yet**. The numerical repair at `9c53af707a60d27ee3d9d37e5122e7a0ba7d5460` changed the GPU fast path, so older physical-GPU evidence cannot close current applicability.

Current physical-GPU classification remains:

**`PHYSICAL_GPU_REVALIDATION_REQUIRED`**

The required revalidation is **not H100-specific**. Under `M18_S9_PHYSICAL_GPU_AMENDMENT.md`, any physical NVIDIA CUDA-capable GPU supported by JAX is eligible. The same S9 code/data path must satisfy the unchanged CPU-vs-GPU final-objective gap `<= 1e-7`, with actual device residency and hardware/runtime/command/source evidence recorded.

A CPU-only or mocked-device run cannot infer GPU PASS. Passing on a T4 validates the tested NVIDIA/JAX/CUDA numerical path but does not make H100-specific performance claims.

## Integrity statement

No threshold, seed, dataset, start, model family, optimizer or validation grid was changed to obtain the CPU result or to amend GPU hardware eligibility. The hardware-model amendment was recorded before observing new physical-GPU evidence on the repaired path.
