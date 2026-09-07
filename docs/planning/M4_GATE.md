# M4 — HGF Forward Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Validation workflow: `M4 HGF Forward Parity`
- Passing workflow run: `34120120732`
- Numerical mode: CPU float64

## Scope validated

- [x] B02 `hgf_prediction`
- [x] B03 `hgf_pihat`
- [x] B04 `hgf_pihat_last`
- [x] B05 `hgf_binary_level1`
- [x] B06 `hgf_binary_level2`
- [x] B07 `hgf_continuous_level1`
- [x] B08 `hgf_volatility_update` shared HGF/eHGF/uHGF block branches
- [x] B09 `hgf_volatility_pe`
- [x] B10 `hgf_check_trajectories`
- [x] standard binary HGF full forward trajectory
- [x] standard continuous HGF full forward trajectory
- [x] regular-interval fixtures
- [x] irregular-interval + ignored/NaN-trial fixtures
- [x] MATLAB-like `traj` fields and `infStates`
- [x] first-divergence reporting by fixture / field / trial / level

## Calibrated tolerances

No tolerance was widened in response to a numerical mismatch.

- shared building blocks: `rtol=2e-13`, `atol=2e-14`
- uHGF branch spot-check inside B08: `rtol=5e-12`, `atol=5e-14`
- recursive standard-HGF trajectories: `rtol=5e-11`, `atol=5e-13`

The uHGF full recursive gate remains M6; M4 only validates the shared B08 branch as a building block.

## Passing jobs

Workflow run `34120120732`:

- `python-forward-tests`: PASS
- `matlab-python-forward-parity`: PASS

Regression evidence on the same PR head:

- M1 Golden Harness `34120120741`: PASS
- M2 Parameter/Config Parity `34120120738`: PASS
- M3 Scalar Numerical Parity `34120120734`: PASS

## Scientific compatibility decisions frozen by M4

- binary level-2 predicted precision preserves the frozen source's deliberate `t=1` call even when irregular intervals are enabled;
- ignored input trials copy the frozen state arrays exactly;
- continuous ignored trials leave `dau` undefined/NaN, matching `hgf_unified.m`;
- output trajectories retain MATLAB field semantics for `mu`, `sa`, `muhat`, `sahat`, `v`, `w`, `da`, `ud`, `psi`, `epsi`, `wt`, plus `dau` for continuous HGF;
- `infStates` retains the MATLAB channel order `[muhat, sahat, mu, sa]`.

## Oracle-path issue caught by the gate

The first irregular-interval CI attempt exposed a MATLAB path-shadowing hazard: `addpath(genpath(...))` could resolve the legacy `_original_models/hgf_binary.m`, whose historical time-axis code falls back to unit intervals after reducing the input to one column. The M4 oracle was therefore pinned explicitly to the canonical frozen `hgf_binary_unified` / `hgf_unified` implementations.

A second CI attempt exposed MATLAB `jsonencode` collapsing an `N×1` trajectory matrix to a JSON vector. The checker now restores that singleton serialization dimension only for the affected `w` field; numerical tolerances were unchanged.

## Next milestone

`M5 — eHGF Forward Parity`
