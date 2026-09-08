# Agent Handoff

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## Current milestone

`M12 — Complete Model Coverage (REOPENED)`

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
- M12 — Specialized Model Coverage (previous partial gate; reopened for full coverage)

## M12 evidence

Specialized/legacy model coverage is now frozen at the family level and all frozen perceptual/observation source files have an explicit final migration status.

Validated:

- binary PU HGF/eHGF/uHGF: PASS
- binary PU-TBT HGF/eHGF/uHGF: PASS
- AR1 binary HGF/eHGF/uHGF: PASS
- Rescorla-Wagner binary: PASS
- dual Rescorla-Wagner: PASS
- Pearce-Hall binary: PASS
- Sutton K1 binary: PASS
- scalar Kalman filter: PASS
- HMM: PASS
- exhaustive frozen inventory: PASS
- unclassified perceptual/observation files: 0
- DONE files: 146
- REFERENCE_ONLY files: 113
- DONE families: 32
- REFERENCE_ONLY families: 21
- M12 workflow run: `34188815550`
- `python-specialized-tests`: PASS
- `matlab-python-specialized`: PASS

The M12 oracle is pinned to canonical frozen MATLAB directories to avoid `_original_models` path shadowing. Frozen source quirks such as Sutton K1's double beta cleanup are preserved rather than normalized.

## Architecture decisions frozen through M12

1. M8 owns objective semantics.
2. M9 owns compatibility Ridders+BFGS MAP optimization.
3. M10 owns Hessian/covariance/Laplace evidence and LME-based restart selection.
4. M11 owns compatibility simulation and prior-predictive sampling semantics.
5. M12 owns final family-level migration classification for the frozen perceptual/observation source inventory.
6. `DONE` means compatibility implementation + parity evidence; `REFERENCE_ONLY` explicitly makes no compatibility claim.
7. HGF Toolbox 8.2.0 remains the compatibility specification.
8. PyHGF is optional for interoperability/comparison; do not fork it and do not place it under the compatibility core.
9. Native GPU/fast-mode work remains separate and must be cross-validated against compatibility mode.

## M12 coverage details

See:

- `docs/planning/M12_GATE.md`
- `docs/planning/M12_COVERAGE.md`
- `tools/check_m12_inventory.py`

## Next tasks

1. Define a MATLAB-style compatibility result object for fit/sim/sample outputs.
2. Support downstream fields such as `p_prc`, `p_obs`, `traj`, `optim`, `yhat`, `res`, `irr`/ignored-trial metadata.
3. Add `to_dict(matlab_style=True)` or equivalent stable export semantics.
4. Add compatibility entry points/names that minimize changes in existing downstream HGF analysis scripts.
5. Validate several real downstream-style consumers against frozen result fixtures.
6. Keep native Python ergonomics separate from the strict compatibility surface.

## Do not start with

- GPU optimization
- performance tuning
- batch fitting
- multi-GPU


## Corrected M12 requirement

All frozen scientific perceptual and observation model families must be implemented in HGFX with config/transform/output semantics and MATLAB parity. Scientific REFERENCE_ONLY is no longer an accepted terminal status. M13 is blocked until the corrected M12 gate passes.

Execution plan: M12A continuous AR1; M12B MAB; M12C JGET; M12D categorical/world; M12E HHMM; M12F auxiliary perceptual; M12G remaining observations; M12H exhaustive closure.
