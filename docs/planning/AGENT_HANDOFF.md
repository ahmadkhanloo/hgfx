# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M17 — Multi-GPU correctness validated; scaling benchmark pending`

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
- M14 — Native GPU Engine (physical H100 validated)
- M15 — GPU Fitting (physical H100 validated)
- M16 — Batch Engine (physical H100 validated)
- M17 — Multi-GPU correctness (physical H100 validated; scaling benchmark pending)

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

## M14 status

M14 is **PASS**.

Physical validation was completed on 2026-09-09 on NVIDIA H100 80GB HBM3
(physical GPU 1) using Python 3.11.7 and JAX/JAXLIB 0.10.2.

- validated stacked commit: `45139c07ec90a7558e3ace0d36fb7a56754539c1`
- strict M14 physical GPU test: 1 passed in 4.95s
- combined M14-M16 strict suite: 20 passed in 112.97s

See `docs/planning/M14_GATE.md` and
`docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## M12 coverage details

See:

- `docs/planning/M12_GATE.md`
- `docs/planning/M12_COVERAGE.md`
- `tools/check_m12_inventory.py`

### Physical GPU validation — completed

The owner-side H100 validation has been completed and recorded. No M14 hardware
action remains pending.


## M15 status

M15 is **PASS**.

- prerequisite M14 physical gate: PASS
- strict M15 physical GPU fitting test: 1 passed in 14.43s
- fitted objective/parameters/trajectory and device residency validated on H100
- combined M14-M16 strict suite: 20 passed in 112.97s

See `docs/planning/M15_GATE.md` and
`docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## Next tasks

1. Run controlled M17 scaling benchmarks on sufficiently idle H100s.
2. Record 1/2/4/6 or 1/2/4/8 GPU throughput, speedup, parallel efficiency, compile overhead, and peak memory.
3. Begin M18 scientific validation: parameter recovery, model recovery, robustness, CPU/GPU agreement, optimizer agreement.
4. Preserve M14-M17 numerical parity as the regression baseline.
5. Feed validation and benchmark results into the Methods-paper reproducibility package.

## M14 boundary

Compatibility mode remains untouched. M14 owns fast forward/objective execution and
physical CPU/GPU parity; optimizer validation belongs to M15.


## Corrected M12 requirement — completed

All frozen scientific perceptual and observation model families are implemented in HGFX with applicable config/transform/output/simulation semantics and MATLAB parity. Scientific REFERENCE_ONLY count is zero. M13 is complete; M14 is now unblocked.

## M16 status

M16 is **PASS / GPU VALIDATED**.

Implemented:
- subject batching with `jax.vmap`;
- restart batching with nested `jax.vmap`;
- scheduler by trial bucket and restart count;
- safe heterogeneous-length masks;
- compiled group-runner cache;
- final objective/trajectory recomputation;
- single-vs-batch and restart-vs-independent-fit tests;
- strict physical GPU batch parity/device-residency validation.

CPU/JAX evidence: workflow `34253080856`; 5 targeted tests passed; full regression
88 passed with 2 GPU-only skips.

Physical H100 evidence on 2026-09-09:
- strict M16 test: 1 passed in 21.87s;
- combined M14-M16 strict suite: 20 passed in 112.97s;
- validated commit: `45139c07ec90a7558e3ace0d36fb7a56754539c1`.

Throughput and multi-GPU scaling are M17/Methods work, not M16 parity claims.

See `docs/planning/M16_GATE.md` and
`docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.


## M17 status

M17 physical correctness is **PASS** as of 2026-09-09.

Validation environment:
- NVIDIA H100 80GB HBM3
- Python 3.11.7
- JAX/JAXLIB 0.10.2
- six JAX-visible GPUs from physical `CUDA_VISIBLE_DEVICES=0,1,2,3,5,6`

Evidence:
- M14 strict: 1 passed in 7.46s
- M15 strict: 1 passed in 17.72s
- M16 strict: 1 passed in 20.69s
- M17 real two-GPU strict parity/residency: 1 passed in 29.25s
- combined M14-M17 modules: 23 passed in 144.23s

The run was not accepted as a performance benchmark because several GPUs were concurrently
busy. Controlled scaling remains pending.

See `docs/planning/M17_H100_GPU_EVIDENCE.md`.
