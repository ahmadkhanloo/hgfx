# M6 — uHGF Forward Parity Gate

Status: **PASS**

## Frozen reference

- HGF Toolbox: `8.2.0`
- Commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Validation workflow: `M6 uHGF Forward Parity`
- Passing workflow run: `34125217371`
- Numerical mode: CPU float64

## Scope validated

- [x] public `uhgf_binary` wrapper through the unified binary recursion
- [x] public `uhgf` wrapper through the unified continuous recursion
- [x] regular binary uHGF trajectory
- [x] irregular + ignored binary uHGF trajectory
- [x] regular continuous uHGF trajectory
- [x] irregular + ignored continuous uHGF trajectory
- [x] MATLAB-like `traj` fields and `infStates`
- [x] uHGF weighting factor recomputed at predicted mean `muhat`
- [x] Expansion 1 quadratic approximation at the prediction
- [x] Lambert W0 approximate posterior mode
- [x] Expansion 2 quadratic approximation at that mode
- [x] non-positive Expansion 2 precision fallback
- [x] non-finite Expansion 2 fallback to Expansion 1
- [x] variational-energy softmax weighting
- [x] Gaussian-mixture moment matching
- [x] positive final posterior precision
- [x] M4 HGF and M5 eHGF Python forward regressions preserved

## Calibrated tolerances

No forward tolerance was widened relative to M4/M5.

- uHGF internal diagnostics: `rtol=5e-12`, `atol=5e-14`
- recursive uHGF trajectories: `rtol=5e-11`, `atol=5e-13`

## Passing jobs

Workflow run `34125217371`:

- `python-uhgf-tests`: PASS
- `matlab-python-uhgf-parity`: PASS

The Python regression job executes standard HGF, eHGF, and uHGF forward unit suites together.

## Scientific compatibility decisions frozen by M6

- uHGF shares the exact unified HGF/eHGF recursion and changes only the volatility update branch plus the frozen uHGF last-level `v` semantics;
- uHGF computes random-walk variance using the predicted upper-level mean `muhat_j`, not the previous posterior mean;
- the second expansion uses the principal Lambert `W_0` branch with the frozen eight-step Halley implementation;
- Lambert-W arguments are formed in log-space and capped at `realmax(double)` before exponentiation, matching MATLAB;
- if Expansion 2 precision is non-positive, the frozen positive precision approximation is substituted;
- if Expansion 2 remains non-finite, both its precision and mean fall back to Expansion 1;
- component weighting uses the frozen variational-energy logistic expression `b = 1/(1+exp(I1-I2))`;
- the final Gaussian is obtained by exact two-component mixture moment matching;
- ignored-trial copying, irregular-time semantics, binary level-2 hard-coded `t=1`, trajectory fields, and `infStates` order remain shared with M4/M5.

## Diagnostic fixtures

The MATLAB oracle exports internal deterministic quantities for a nominal case, including:

- `v`, `w`
- `pi1`, `mu1`
- `gamma_c`, `pihat_y`
- Lambert-W log argument, capped argument, `W_0`, and `x_star`
- `w2`, `da2`, `pi2`, `mu2`
- variational energies `I1` and `I2`
- blend weight `b`
- final mixture mean, variance, and precision

A second extreme deterministic case forces the frozen non-finite Expansion 2 path and verifies fallback to Expansion 1 while retaining a finite, positive public posterior.

## Architecture decision

M6 keeps one scientific source of truth for HGF/eHGF/uHGF in the Python unified recursions. Public model wrappers only select `update_type`; no separate uHGF recursion was introduced.

## Next milestone

`M7 — Observation Parity`
