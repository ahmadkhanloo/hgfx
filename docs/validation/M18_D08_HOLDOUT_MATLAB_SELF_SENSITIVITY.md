# M18 D08 Failed-Holdout MATLAB Self-Sensitivity Diagnostic

Status: **FROZEN / DIAGNOSTIC ONLY**

This protocol tests the MATLAB reference optimizer itself on the exact prospective D08 holdout seed that failed inference equivalence: `314159265`.

Frozen contract:

- reference HGF Toolbox 8.2.0 commit `2437f4dc241541072722a2695ddeca7b44d83dd3`;
- `example_usdchf.txt`;
- simulation model `uhgf` with native vector `[1.04, 1, 0.0001, 0.1, 0, 0, 1, -13, -2, 1e4]`;
- observation `gaussian_obs`, native noise `0.00002`;
- simulation seed `314159265`;
- fit `uhgf_config + gaussian_obs_config + quasinewton_optim_config`;
- seven free transformed coordinates `[1,3,4,8,9,10,11]` in MATLAB 1-based full-vector indexing;
- exactly fourteen starts: plus/minus one local MATLAB `eps(start(k))` perturbation for each free coordinate;
- existing endpoint gate only: `rtol=3e-8`, `atol=3e-10`.

Classification:

- `MATLAB_START_ULP_BASIN_SENSITIVE` if the baseline replay reproduces the reference fit and at least one one-spacing start exits the existing endpoint gate;
- `NO_MATERIAL_START_ULP_SENSITIVITY_DETECTED` if all fourteen variants remain within the existing endpoint gate;
- `INVALID_BASELINE_REPLAY` or `INSUFFICIENT_REFERENCE_EVIDENCE` otherwise.

This experiment is reference-only and has **no direct acceptance effect**. It cannot erase the failed prospective Level-2 holdout, loosen tolerances, or independently classify D08 as PASS/REFERENCE_LIMITATION_MATCH. Its only purpose is to determine whether the same numerical-basin mechanism is demonstrably present in MATLAB for the exact failing seed.
