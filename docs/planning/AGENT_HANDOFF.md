# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M14 — GPU Engine`

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

## M12 coverage details

See:

- `docs/planning/M12_GATE.md`
- `docs/planning/M12_COVERAGE.md`
- `tools/check_m12_inventory.py`

## Next tasks

1. Start M14 GPU engine without altering compatibility semantics.
2. Port trial recursions to `jax.lax.scan` behind a separate fast-mode boundary.
3. Add subject/restart vectorization only after single-sequence CPU/JAX equivalence is frozen.
4. Add JIT/compile-cache and device-residency tests.
5. Cross-validate fast-mode trajectories/objectives against the M4-M13 compatibility oracles.
6. Do not weaken MATLAB parity gates in the name of performance.

## M14 boundary

Start GPU implementation now, but keep batch fitting and multi-GPU scheduling out of the first M14 slice until single-model fast-mode equivalence is demonstrated.


## Corrected M12 requirement — completed

All frozen scientific perceptual and observation model families are implemented in HGFX with applicable config/transform/output/simulation semantics and MATLAB parity. Scientific REFERENCE_ONLY count is zero. M13 is complete; M14 is now unblocked.
