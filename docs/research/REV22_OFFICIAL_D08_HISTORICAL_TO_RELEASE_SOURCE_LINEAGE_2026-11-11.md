# REV-2.2 official D08: historical diagnostic → published 1.0.0 source lineage audit (2026-11-11)

**SOURCE-ONLY FINDING, NO NUMERICAL FIT REPLAY:** The historical official-seed Ridders/Armijo selected-state diagnostics executed editable HGFX at Git commit `d360fcd45c996c21ab482d1cd6b45dea6d65574f`, whereas new prospective D08 Runs A/B use the immutable released **HGFX 1.0.0 Wheel** with source release commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Comparing both actual Git source trees and individual file Git blobs shows that **the main Ridders and quasi-Newton algorithm files are byte-identical**, but the **continuous uHGF forward numerical path is not**. Thus the old selected-state exact match is *useful historical evidence* but **not a complete released-Wheel numerical equivalence oracle**.

## Reproducible immutable Git source comparison

Both exact Git tree objects were inspected using the current GitHub repository API; trees were reported **not truncated**. The two commits pin the same frozen MATLAB Toolbox 8.2.0 submodule SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`. Under `src/hgfx/`, old commit has **88** file blobs and source release has **91**. **12** paths have different Git blob or addition: **9 modified + 3 added**. This is a source inventory, **not** an assertion that all changed files affect D08.

### Files unchanged byte-for-byte in the relevant fitting pathway

| File | Exact Git blob SHA — identical in both |
| --- | --- |
| `src/hgfx/optim/ridders.py` | `3de1fa77960b83da8128d79643730a8282cd22e2` |
| `src/hgfx/optim/compat_quasinewton.py` | `05f4797e53d96384c376fbc2a777ab37b08e93f2` |
| `src/hgfx/compat/fit.py` | `ab58036142993757ed9144a8dd16df74dc27a832` |
| `src/hgfx/compat/workflows.py` | `9e37d086a945f22823aabb89ee3423c29af947f0` |
| `src/hgfx/compat/objective.py` | `0624f12ba526cae69ec992f0ce6ae77d2c35d6ce` |
| `src/hgfx/compat/sim.py` | `3688598bd4173e72060475622da6d60b7068bed2` |
| `src/hgfx/models/uhgf.py` | `4f9bdc0134509d69d1c0cfaf233819a9fc88a2dc` |
| `src/hgfx/responses/gaussian.py` | `9630724520cf52ed80e7e1ae2f05d2faf0c8b3cd` |
| `src/hgfx/compat/configs.py` | `76469aa702a3983c92bb48465ed084f16760f039` |
| `src/hgfx/compat/fit_statistics.py` | `2837244f030d526de319dd645b9d03e82cf9e2de` |
| `src/hgfx/core/transforms.py` | `2ee3d52da9dbef0d593eedfc5359a2ab62dc190a` |
| `src/hgfx/compat/simulation.py` | `fc3371828fb4d45c6803103665fdabe34300cd2f` |

These identical optimizer files support **implementation source identity of the BFGS/Ridders core** across those commits, but do not establish the same gradient values: gradients depend on objective/forward evaluation and runtime floating-point effects. The historical diagnostic workflow was an **editable source install**, not proof of the exact installed released Wheel environment.

### Materially changed source in the continuous-uHGF model's reachable forward path

| File | Old Git blob at `d360fcd...` | Release Git blob at `4dd8fbd...` |
| --- | --- | --- |
| `src/hgfx/models/hgf.py` | `48ce18df9792f1eb1e0005727546dbd13d5cc666` | `b38e3771790783381048564fffeb85d89c74350d` |
| `src/hgfx/models/_forward_common.py` | `dfb12ac54057f69b5aaddab2b05a3ceb59d9a218` | `9b3f390fe219f7c489782371fcdeae59cc378b94` |
| `src/hgfx/math/matlab_exp.py` | `6558272feda67cc35594b95d4c82311569373606` | `97e2ea50e6512060216eb42178379de34bc82e13` |

- `src/hgfx/models/uhgf.py` in both commits calls `hgf_unified` from `models/hgf.py`, which imports the common forward helpers. This **statically establishes reachability** of the changed files from D08 continuous `uhgf`, not which exact code path was numerically taken for every archived parameter vector.
- In `models/hgf.py`, the initial theta exponential and two top-level `v[k,last-1]` exponential sites changed from `np.exp(np.float64(...))` / `np.exp(...)` to `matlab_exp_scalar(...)`. The chosen compatibility math implementation can change final binary64 rounding.
- In `models/_forward_common.py`, three slices of *continuous* transformed native parameters changed from `np.exp` to `matlab_exp` (sa0/kappa/pi_u and related transformed slots).
- `math/matlab_exp.py` was altered to expand MATLAB-compatible binary64 `exp/expm1` code; its historical and release Git blobs are different.
- **These are source-level numerical implementation changes**, not evidence that the original scientific model equations changed or that the changes caused D08's eventual `epsi` differences. They plausibly affect exact Ridders objective samples and later branch decisions, but a **matched released-Wheel and MATLAB oracle at the same actual source state** is required for causal attribution.

### Other changed/added source blobs in overall inventory

Changed: `src/hgfx/__init__.py`, `src/hgfx/compat/__init__.py`, `src/hgfx/gpu/engine.py`, `src/hgfx/models/hgf_binary.py`, `src/hgfx/responses/unitsq_sigmoid.py`, `src/hgfx/updates/binary_l1.py`; added: `src/hgfx/compat/bpa.py`, `src/hgfx/math/matlab_log.py`, `src/hgfx/plotting.py`. **These inventory differences are not themselves evidence of D08 causal impact.** In particular, the existence of a new compatibility module does not prove a change in original continuous-uHGF likelihood.

## Consequences for REV-2.2 and scientific integrity

The [authenticated historical official-seed report](REV22_OFFICIAL_D08_RIDDERS_ARMIJO_SOURCE_AUDIT_2026-11-11.md) still accurately states that, at the **old original selected source** row 2/free component 0, 22/22 Ridders objective sample comparisons and selected derivative/error were exact; old row 2→3 Armijo sampled objectives 17/17 exact, accepted `j=2`; historical official MATLAB ±one-ULP start study was **0/14** materially out-of-gate. They are NOT now recast as a released Wheel 1.0.0 fit PASS: **the forward implementation did change in three directly reachable files.**

Original new A/B released-v1.0.0 outputs still have **4/1228** and **3/1228** own-optimum epsi violations, original M18 official FAIL, **first new released-Wheel BFGS causal decision not observable** from archived final results; both simultaneously launched scientific runs and the single-run protocol deviation remain preserved in [Issue #111](https://github.com/ahmadkhanloo/hgfx/issues/111). Original holdout seed 314159265 source and `REFERENCE_LIMITATION_MATCH` remain exact-scope only. No model/gradient/optimizer rerun was made for this source comparison; no change in fixed tolerance, seed, dataset, model family, priors or historical evidence.

**Current statuses:** REV-2.2 `IN_PROGRESS / UNRESOLVED_DISCREPANCY`; original M18 D08 direct FAIL, REV-2.4 global `NOT_GLOBAL_PASS`; D2/D3 `BLOCKED`, full historical CPU `NOT_PASS`. The scientific request for independent cause attribution needs new matched-state reference evidence and reviewer approval; the old single-run cap cannot be silently reopened.
