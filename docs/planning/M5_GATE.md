# M5 — eHGF Forward Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Validation workflow: `M5 eHGF Forward Parity`
- Passing workflow run: `34123043904`
- Numerical mode: CPU float64

## Scope validated

- [x] unified binary recursion with explicit `update_type`
- [x] unified continuous recursion with explicit `update_type`
- [x] public `ehgf_binary` wrapper
- [x] public `ehgf` wrapper
- [x] regular binary eHGF trajectory
- [x] irregular + ignored binary eHGF trajectory
- [x] regular continuous eHGF trajectory
- [x] irregular + ignored continuous eHGF trajectory
- [x] MATLAB-like `traj` fields and `infStates`
- [x] eHGF mean-first volatility update
- [x] safe precision correction `max(0, correction)`
- [x] negative-standard-HGF / positive-eHGF edge case
- [x] M4 standard-HGF parity preserved after unified-core refactor

## Calibrated tolerances

No tolerance was widened to obtain M5.

- eHGF shared-block edge case: `rtol=2e-13`, `atol=2e-14`
- recursive eHGF trajectories: `rtol=5e-11`, `atol=5e-13`

## Passing jobs

Workflow run `34123043904`:

- `python-ehgf-tests`: PASS
- `matlab-python-ehgf-parity`: PASS

M4 regression on the same implementation:

- `M4 HGF Forward Parity` run `34123043853`: PASS

## Scientific compatibility decisions frozen by M5

- eHGF uses the same frozen unified recursion and parameter transforms as HGF, changing only the volatility update branch;
- posterior mean at a volatility level is updated using predicted precision `pihat`, before posterior precision is computed;
- the precision correction is clipped with `max(0, correction)`, so posterior precision cannot be reduced below predicted precision by a negative correction;
- unlike standard HGF, frozen eHGF does not call `hgf_check_trajectories` at the end of the forward recursion;
- irregular-time semantics, ignored-trial state copying, binary level-2 hard-coded `t=1`, trajectory fields, and `infStates` channel order remain identical to the frozen unified source.

## Safe-precision edge case

A deterministic B08 case is included where the standard HGF precision equation becomes negative and raises `NegPostPrec`. On the identical inputs, eHGF clips a negative precision correction to zero and retains the positive predicted precision. Both MATLAB and Python agree on this behavior.

## Architecture decision

M5 refactors standard HGF and eHGF to share one Python unified recursion per input family, matching the HGF Toolbox 8.2.0 architecture. Public wrappers select `update_type`; scientific branch differences remain localized to the shared volatility update block.

## Next milestone

`M6 — uHGF Forward Parity`
