# M18 S9 Physical-GPU Hardware Eligibility Amendment

Date: 2026-09-15
Applies to protocol: `m18-s9-robustness-backend-1`
Status: **FROZEN BEFORE NEW PHYSICAL-GPU EVIDENCE**

## Decision

The S9 physical-GPU gate is **not H100-specific**. Any physical NVIDIA CUDA-capable GPU supported by the installed JAX/CUDA runtime is eligible for the v1.0 backend-applicability gate.

Examples include NVIDIA T4, L4, A10/A10G, A100, H100, H200 and compatible RTX/datacenter GPUs. The exact device model must be recorded in the evidence.

## Rationale

S9 validates backend numerical applicability, not H100-specific performance. The frozen acceptance question is whether the same repaired JAX numerical path executes on a real NVIDIA CUDA device, has actual GPU residency, and agrees with the JAX CPU result under the already-frozen final-objective criterion.

The prior wording inherited H100 from historical project hardware evidence. No current S9 physical-GPU result has been observed under the repaired numerical path, so this hardware-eligibility amendment is made before the new physical run and is not result-driven.

## Unchanged acceptance criteria

This amendment does **not** change:

- protocol data, trials, starts, model family or optimizer;
- compatibility-vs-JAX CPU criteria;
- JAX CPU-vs-physical-GPU final-objective gap `<= 1e-7`;
- requirement for actual device residency;
- requirement to record source commit, GPU model, driver/CUDA/JAX/JAXLIB/Python versions, exact command and environment limitations;
- prohibition on CPU or mocked-device evidence substituting for physical GPU evidence.

## Claim boundary

A passing run supports `PASS_PHYSICAL_GPU_APPLICABILITY` for the tested NVIDIA/JAX/CUDA path. It does not claim H100-specific validation unless the tested device is an H100, and it does not establish performance/scaling claims for untested GPU models.

Performance/scaling benchmarks remain separate from this numerical-applicability gate.
