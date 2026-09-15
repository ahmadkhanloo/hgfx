# M18 completion plan — MATLAB-equivalent v1.0

Last synchronized: 2026-09-15
Status: **IN PROGRESS — ONLY PHYSICAL NVIDIA GPU + FINAL FREEZE/CANDIDATE REMAIN**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Objective

Deliver HGFX v1.0 as a functional/scientific Python replacement for MATLAB HGF Toolbox 8.2.0, with no MATLAB runtime dependency for users. Compatibility is judged under frozen equivalence/reference-limitation policies. Historical and prospective failures remain immutable.

## Current baseline

| Item | Status | Evidence |
|---|---|---|
| Historical M18 scientific experiment | FAIL, preserved | immutable historical gate |
| M0-M17 | PASS in documented scopes | milestone evidence |
| D02 direct fit | FAIL, preserved | historical/direct evidence |
| D02 exact official release disposition | `REFERENCE_LIMITATION_MATCH` | exact paired evidence |
| D08 prospective Level-2 holdout | FAIL, preserved | repaired-product evidence |
| D08 exact failed-seed disposition | `REFERENCE_LIMITATION_MATCH` | exact paired evidence |
| D09/D10-D11/D12 | PASS | recorded workflow runs |
| S7 paired parameter recovery | `REFERENCE_LIMITATION_MATCH` | frozen paired grid |
| S7 paired model selection | `PASS_PAIRED_MODEL_SELECTION` | 36/36 BIC winners match |
| S8 evidence-backed repair | DONE | `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU/backend | `PASS_CPU_BACKEND_EQUIVALENCE` | run `34901924475` |
| S9 physical GPU | BLOCKED / DEFERRED | fresh physical NVIDIA GPU evidence required |
| S10 release readiness | PASS | run `34934079865` |
| M19 evidence freeze | PREPARED / BLOCKED BY PHYSICAL GPU | preflight `34934079973` |
| M20 v1 candidate | PREPARED / BLOCKED BY PHYSICAL GPU + M19 | preflight `34934079973` |

## Ordered closure

S1-S8 and S10 are closed in their documented scopes. S9 CPU/backend is closed. The only unexecuted S9 cell is physical GPU applicability.

Per `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`, the physical gate is **not H100-specific**. Any physical NVIDIA CUDA-capable GPU supported by the installed JAX/CUDA runtime is eligible. This hardware amendment was frozen before observing new physical-GPU evidence on the repaired path.

The numerical gate remains unchanged:

- same repaired S9 code/data path;
- actual GPU residency;
- JAX CPU-vs-physical-GPU final-objective gap `<= 1e-7`;
- exact hardware/runtime/command/source/environment provenance;
- no CPU/mock substitution.

This validates backend numerical applicability, not device-specific performance. A T4 PASS is a valid S9 physical-backend PASS but does not imply H100 performance or cross-GPU scaling claims.

## Anti-endless-patching rule

Do not chase floating-point micro-differences merely because they exist. Repair only when frozen evidence links a difference to a required semantic mismatch. Never widen tolerances or change seed/start/dataset/grid/model/optimizer after results to obtain PASS.

## M19/M20 preparation

M19/M20 preflight passed on `87e3b01fdbdbe5f157ba8dc7f1309335408a165a`: run `34934079973`, job `104268154143`, artifact `10383425031`, SHA-256 `3f711a260f68ff0454d18b2b09b3645d28ab5b370384c8729d4fd431bee5e7cf`.

This is **preflight only**. M19 becomes PASS only after physical NVIDIA GPU evidence passes and `scripts/build_v1_evidence_manifest.py --mode finalize` creates a `FROZEN` manifest. M20 becomes PASS only after M19 freeze, version promotion and `scripts/check_m20_candidate.py --mode finalize` succeeds.

## Next action

Run `scripts/run_m18_s9_physical_gpu_revalidation.py` on any eligible physical NVIDIA CUDA GPU. If it passes without changing frozen criteria, record the evidence, finalize M19, promote release metadata, finalize M20, then make PR #26 ready/merge/tag only if all final gates pass.
