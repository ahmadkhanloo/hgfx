# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M15 — GPU Fitting`

## Frozen reference

HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Completed gates

- M0 — Reference Frozen
- M1 — Golden Harness Operational
- M2 — Parameter/Config Parity
- M3 — Scalar Numerical Parity
- M4 — HGF Forward Parity
- M5 — eHGF Forward Parity
- M6 — uHGF Forward Parity
- M7 — Observation Parity
- M8 — Objective Parity
- M9 — Compatibility Fitting
- M10 — Hessian/LME Parity
- M11 — Simulation Parity
- M12 — Complete Model Coverage
- M13 — API Compatibility

## M12 evidence

Corrected M12 is PASS.

- M12A continuous AR1: `34224773192`
- M12B/C MAB + JGET: `34224773186`
- M12D/E categorical/world + HHMM: `34225650007`
- M12F/G auxiliary + remaining observations/simulations: `34225649883`
- config/prior parity: `34224773097`
- exhaustive closure/full regression: `34225650015`
- DONE files: 259
- REFERENCE_ONLY files: 0
- DONE families: 53
- REFERENCE_ONLY families: 0
- full Python regression: PASS

Frozen source quirks/defects and minimal compatibility repairs are documented in `docs/planning/M12_SOURCE_DEFECTS.md`.

## M13 evidence

M13 is PASS.

- compatibility result/API workflow: `34234431858`
- frozen reference guard: PASS
- M13 public API + downstream consumer tests: 13 passed
- full Python regression: 71 passed
- public aliases: `fit_model/sim_model/sample_model` and `fitModel/simModel/sampleModel`
- MATLAB-style result export: `to_dict(matlab_style=True)`
- one-based `irr`/`ign` compatibility metadata
- raw M11 `hgfx.compat.sim_model/sample_model` APIs preserved

See `docs/planning/M13_GATE.md`.

## Architecture decisions frozen through M13

1. M8 owns objective semantics.
2. M9 owns compatibility Ridders+BFGS MAP optimization.
3. M10 owns Hessian/covariance/Laplace evidence and LME-based restart selection.
4. M11 owns compatibility simulation and prior-predictive sampling semantics.
5. M12 owns final family-level migration classification for the frozen perceptual/observation source inventory.
6. `DONE` means compatibility implementation + parity evidence; scientific `REFERENCE_ONLY` is forbidden and the final M12 inventory contains zero such families.
7. HGF Toolbox 8.2.0 remains the compatibility specification.
8. PyHGF is optional for interoperability/comparison; do not fork it and do not place it under the compatibility core.
9. Native GPU/fast-mode work remains separate and must be cross-validated against compatibility mode.
10. M13 public result objects are interface adapters over validated compatibility numerics; they must not silently introduce alternate scientific semantics.
11. Root-level `hgfx.sim_model/sample_model` return M13 compatibility results; lower-level `hgfx.compat.sim_model/sample_model` remain the frozen M11 raw orchestration API.
12. MATLAB-style fit export keeps `optim.yhat` and `optim.res`; direct `est.yhat`/`est.res` are Python convenience aliases.
13. M14 fast mode lives under `hgfx.gpu` and must never silently replace compatibility mode.
14. M14 compile signatures are explicit HGFX metadata layered over JAX's internal executable cache.
15. Absence of physical GPU hardware cannot be counted as CPU/GPU parity evidence.

## M14 implementation status

M14 software implementation is complete on `work/m14-gpu-engine`, but the formal
milestone gate is still **PENDING physical GPU validation**.

CPU/JAX evidence:

- workflow: `34242409271`
- frozen reference guard: PASS
- JAX CPU x64 M14 parity: 9 passed
- full regression: 80 passed
- GPU-only parity test: 1 skipped because the hosted runner has no GPU

Implemented:

- `jax.lax.scan` trial recursion for binary HGF/eHGF/uHGF
- `jax.jit` forward/objective execution
- subject/same-shape forward `jax.vmap`
- restart/parameter-candidate objective `jax.vmap`
- explicit JAX device selection/placement
- float64 enforcement
- compile signatures + process-local callable cache
- trial-length bucketing/padding
- strict physical-GPU test that fails when `HGFX_REQUIRE_GPU=1` and no GPU exists

M14 is not PASS until the real-GPU job succeeds. M15 software was implemented on top of the M14 head, but both milestones remain formally gated on physical GPU evidence.

See `docs/planning/M14_GATE.md`.

## M12 coverage details

See:

- `docs/planning/M12_GATE.md`
- `docs/planning/M12_COVERAGE.md`
- `tools/check_m12_inventory.py`

### Owner action before closing M14

The repository owner must run the M14 strict parity test on their own physical GPU:

```bash
HGFX_REQUIRE_GPU=1 pytest \
  tests/cpu_gpu/test_m14_fast_engine.py::test_real_gpu_forward_and_objective_parity_when_available \
  -q
```

Record the GPU model, JAX/JAXLIB versions, CUDA version, test output, and commit SHA.
Only after this passes may M14 be marked PASS and M15 begin.

## M15 implementation status

M15 software implementation is complete on `work/m15-gpu-fitting`.

Implemented:
- exact M9 free/fixed fit-vector reuse;
- differentiable M14 objective through `jax.value_and_grad`;
- `DeviceOptimizer` abstraction;
- JAX BFGS backend;
- device-resident optimizer arrays;
- final objective and trajectory recomputation;
- CPU gradient and final-fit parity tests;
- strict physical CPU/GPU fitting parity harness.

M15 is not formal PASS until the physical GPU fitting test succeeds. See
`docs/planning/M15_GATE.md`.

## Next tasks

1. Provide a physical JAX-capable NVIDIA GPU runner.
2. Run the strict M14 physical forward/objective parity job.
3. Run the strict M15 physical fitting parity job.
4. Record GPU model, CUDA, JAX/JAXLIB, commit SHA, and outputs.
5. Mark M14 and M15 PASS only after their respective physical GPU gates are green.
6. Then begin M16 — Batch Engine.

## M14 boundary

Compatibility mode remains untouched. M14 owns fast forward/objective execution and
physical CPU/GPU parity; optimizer validation belongs to M15.


## Corrected M12 requirement — completed

All frozen scientific perceptual and observation model families are implemented in HGFX with applicable config/transform/output/simulation semantics and MATLAB parity. Scientific REFERENCE_ONLY count is zero. M13 is complete; M14 is now unblocked.
