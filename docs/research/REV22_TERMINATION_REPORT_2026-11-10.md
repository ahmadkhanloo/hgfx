# COMPSTAT REV-2.2 — additive quasi-Newton stop reporting (2026-11-10)

**Scope:** first engineering subtask of REV-2.2 (C5, USD/CHF convergence characterization). **Result: IMPLEMENTED / TARGETED CPU UNIT VALIDATED on Ubuntu and Windows. REV-2.2 scientific comparison NOT EXECUTED; overall milestone IN PROGRESS.** Original released HGFX v1.0.0 code, scientific results and run budgets unchanged.

## Source issue and bounded correction

Prior to this change, frozen compatibility optimizer `hgfx.optim.compat_quasinewton.QuasiNewtonResult` already stored `termination` with possible values `tol_grad`, `tol_arg`, `max_iter`, `max_resets`, but `hgfx.fitModel(...).optim` and its public `to_dict(matlab_style=True)["optim"]` did not expose that reason. This prevented unambiguous programmatic reporting of convergence in REV-2.2.

**Exact source code change:** [commit `f4dd0197166f752450c657e6a76454ad7c5100b8`](https://github.com/ahmadkhanloo/hgfx/commit/f4dd0197166f752450c657e6a76454ad7c5100b8), only `src/hgfx/compat/fit.py`: add `optim.termination` (the existing optimizer reason, *not recomputed*) and `optim.converged` (native Python bool). `converged = reason in {"tol_grad","tol_arg"} AND finite final value AND all finite final coordinates`. This is an **algorithmic stopping condition**, *not* proof of a stationary point, global optimum, Hessian positive-definiteness, stable inference or MATLAB scientific parity. A small-step `tol_arg` termination may indicate stagnation.

The extension is *additive* to `MatlabStruct`, preserving all pre-existing MATLAB-style keys (including `negLj, negLl, H, Sigma, Corr, iter, AIC, BIC, LME`) and downstream mapping/attribute use. The compatibility BFGS algorithm, gradient/Ridders stencil, numerical tolerances, initial vectors, forward, objective, priors and optimizer selection were **not** changed. Both the standard binary HGF `fit_model` path and alternate `fit_workflow` path use the shared `_optimizer_struct` formatter.

**Test & docs:** [`tests/unit/test_rev22_optimizer_stop_reporting.py`](../../tests/unit/test_rev22_optimizer_stop_reporting.py), initial commit `34ba7fa8f0f711501e56a1e67903fe3542139694`, tests tolerances, exhausted budgets, nonfinite rejection and one small *synthetic* public `fitModel` call. Existing M13 API and M9 compatibility tests included. [Public API docs](../user/API.md) and [changelog](../../CHANGELOG.md) updated. No real USD/CHF subject-series/614 trial data were used.

## Real target-platform test evidence

[**GitHub Actions run `42838228644`**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42838228644), exact run head `c6e5f95824ff03ba898888a5cb850d95f2b1967c`, workflow `.github/workflows/compstat-rev22-optimizer-stop.yml`, complete **SUCCESS**:

| Platform | Reference source verification | Targeted tests | Status |
| --- | --- | --- | --- |
| Ubuntu 24.04, Python 3.11, JAX CPU x64 | `Reference freeze verification: PASS` (334 MATLAB files) | **11 passed in 2.63s** | **PASS, TARGETED ONLY** |
| Windows latest, Python 3.11, JAX CPU x64 | `Reference freeze verification: PASS` (334 MATLAB files) | **11 passed in 4.34s** | **PASS, TARGETED ONLY** |

This CI **does not** run MATLAB itself, does not evaluate real 614 USD/CHF inputs, does not audit Ridders warning locations or Hessian conditioning, does not validate arbitrary optimizer paths, and does not constitute a full CPU regression suite. Historical full-suite maintenance attempts still **302 passed / 1 failed / 5 skipped per OS** before the isolated P6A ancestry success; full CPU remains `NOT_PASS`.

## Original 614-series and D08 workflow source identity (inspection only)

A repository source audit (NO simulation/fitting) found that `demo/example_usdchf.txt` in original MATLAB HGF 8.2.0 gitlink `2437f4dc241541072722a2695ddeca7b44d83dd3` contains **614 finite numeric source observations**, original Git blob `29a4d0322faf8894c414883c517950aa87b481db` (the public source file itself is *not* a new observed outcome). The existing historical reference runner `reference/matlab/export_m18_workflows.m` Git blob `bc5dae87294e106ca57532c995ea92ac091ed313` defines the original D08 **simulated** responses from the same 614 source observations: MATLAB seed **`123456789`**, sim and fit `uhgf + gaussian_obs`, native perceptual parameters `[1.04 1 .0001 .1 0 0 1 -13 -2 1e4]`, Gaussian observation variance `.00002`, frozen quasinewton optimization. This is not a fit to 614 independently observed USD/CHF behavioral responses. Original archived D08 fitted endpoint and historical failure evidence are retained; the development termination feature is separate. Another source-audited history experiment uses seed `314159265` for a **different holdout** and must not be substituted for official D08. Before new REV-2.2 scientific evaluation, freeze **which original response-generating protocol** and version-specific comparator is used, rather than mixing these two seeds or source branches.

## Next unresolved REV-2.2 gates

1. Preregister authentic pinned MATLAB HGF 8.2.0 and original released HGFX v1.0.0 USD/CHF demo **614-series** numerical experiment and exact source/parameter/initialization/optimizer config. Use existing original demo reference as oracle; first verify data identity and model family. Do not substitute development-only `1.1.0b1` outputs for historical 1.0.0 science.
2. Evaluate the actual final/cross-evaluated transformed/native parameters, NLL/NLJ, BIC/LME, trajectories, Hessian positive-definiteness/condition and optimizer trajectory/termination under a precommitted protocol. No new tolerance selected after seeing results; report mismatch.
3. Classify Ridders warning count/file/parameter index and explore **at most three previously documented option values**, prospectively registered, not tuned after observation. Old fit failures retained.

**Scientific conclusion: NONE from these targeted unit tests.** `REV-2.2 = IN_PROGRESS`; `REV-2.1 = BLOCKED_PRE_SCIENCE` pending [Issue #110](https://github.com/ahmadkhanloo/hgfx/issues/110); `REV-2.4 = NOT_GLOBAL_PASS` and D2/D3 `BLOCKED`, independent human review for eHGF-019 remains open. Do not classify a scientific limitation based on unit tests alone.
