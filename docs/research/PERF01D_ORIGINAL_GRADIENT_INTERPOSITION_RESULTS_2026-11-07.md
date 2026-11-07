# PERF-01D — exact-bit original-gradient interposition counterfactuals, eight-arm results (2026-11-07)

**AUTHOR-SIDE EXPLORATORY EXECUTION SUCCESS, ORIGINAL 64-PUBLIC-FIT SCIENCE STILL 63/64 NONPASS. INDEPENDENT REVIEW NOT RECEIVED, PERF-01C NOT FROZEN, NO TIMING, NO PERFORMANCE OR GPU CLAIM. These counterfactual results are NOT original frozen HGFX fits.**

## Design/protocol and immutable evidence

[Prospective-to-this-new-run but explicitly post-result-selected exploratory protocol](PERF01D_ORIGINAL_GRADIENT_INTERPOSITION_EXPLORATORY_PROTOCOL_2026-11-07.md) was committed at **`7049b23a6acf118038149a1bbbb31cb5d40da45f`** before these source-gradient interventions ran. Original HGFX v1.0.0 frozen source `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and MATLAB HGF 8.2.0 frozen source `2437f4dc241541072722a2695ddeca7b44d83dd3`. Original source 64-subject full fitting [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) is **63/64 SCIENTIFIC NONPASS**; the original zero-based subject 7 has **4 `traj.mu` + 4 `traj.muhat`** failures, preserved; nested 15/16 NONPASS and all eight real same-runner failing comparisons are unchanged.

Original full subject-7 public fit [BFGS run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) original raw HGFX SHA-256 `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce` and MATLAB SHA-256 `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`. Real frozen private nested MATLAB Ridders gradient oracle at 25 HGFX-own plus 25 MATLAB-own source coordinates comes from [42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614) and SHA-256 **`2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d`** for its complete paired report. All original raw and full-cohort failed provenance hashes were checked before intervention.

Fixed original model `hgf_binary`+`unitsq_sgm`, subject zero-based **7**, original 128 trials, unchanged input/config/prior/free indices [12,13,14], start `[-3,-6,3.871201010907891]`, original frozen BFGS and Ridders `min_steps=10`. No freeze, no new threshold and no timer.

### Execution history and unmodified-source discipline

- Initial workflow [42366055097](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366055097) @ `e40b9adbc9521b83d78e715d34397750a0904cbc`: **FAILED before any optimizer intervention** on synthetic Ridders fake signature and arm-dispatch tests; original source unchanged.
- Subsequent test-fix runs [42366146173](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366146173) and [42366148737](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366148737): **FAILED in engineering synthetic controls** (invalid duplicate-gradient synthetic test, NumPy-array equality test), no scientific outcome, original runs preserved.
- Final [42366198103](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366198103) at exact candidate SHA **`8a70d1cad64d03b664cbf735079f63d1dfc5b444`**: **SUCCESS**: **14/14** synthetic engineering controls passed; input/config, original fit and all five original BFGS+private MATLAB-gradient raw SHA verified; all **eight predeclared arms completed**, no discarded arm, and source Ridders import restored after each intervention. [Complete artifact **13571871384**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366198103/artifacts/13571871384), ZIP SHA-256 **`4fd318f66d97792738874a0d35c65db90bc5d7c72df151489d76b8c50facd6b2`**. Full eight-arm raw JSON SHA-256 **`8a478e7ace9c85c5185c26980b4f4a6a3f7226c2cba2561f77809a8c6588416e`**; original original frozen sources and prior archives were never mutated.

Host: GitHub Actions, **AMD EPYC 9V45**, Linux 7.0.0-1017-azure x86_64, Python 3.11.18, NumPy 2.3.5, SciPy 1.17.1, JAX/JAXlib 0.10.2, HGFX 1.0.0, OpenBLAS threads 4, OMP/MKL 1, JAX CPU. The original archived optimizer was run on a different underlying host and bitwise cross-host replay is not guaranteed; see issue [#90](https://github.com/ahmadkhanloo/hgfx/issues/90).

The experiment used the **unaltered** frozen HGFX `quasinewton_optim` and **unaltered** original `evaluate_free`; only a temporary **harness-side interposition of the imported Ridders return vector** was made for diagnostic arms. It first called the genuine frozen HGFX gradient, then replaced preselected exact binary64 components by the previously measured frozen MATLAB private gradient **at that exact original free x**. No approximate coordinate matching or gradient interpolation, no modified MATLAB function and no source patch. All synthetic checks verify restoration of the original imported function after intervention.

## Exact eight-arm outcome (within this host)

Distances are `max_i abs(free_i - reference_i)`, in the three originally free transformed coordinates. They are **descriptive numerical responses**, not trialwise public scientific-fit acceptance metrics.

| Precommitted arm | Exact anchor replacements executed | Max distance to original MATLAB endpoint | Max distance to same-host baseline | Classification |
|---|---:|---:|---:|---|
| Unmodified baseline | 0 | `3.277081539465598e-08` | 0 | ORIGINAL FROZEN ENGINE WITH NEW-HOST FLOATING DIFFERENCE |
| Original-HGFX gradient at initial x (placebo) | 1 | `3.277081539465598e-08` | 0 | Placebo leaves current result unchanged |
| Original MATLAB private component 0 at initial x | 1 | **`3.3157530054950257e-09`** | `3.608656840015101e-08` | Diagnostic counterfactual, closer only |
| Original MATLAB private 3 components at initial x | 1 | **`2.2791900811114374e-07`** | `2.606898235057997e-07` | Diagnostic counterfactual, farther |
| Original MATLAB private component 0 at HGFX-own x6 | **0** | `3.277081539465598e-08` | 0 | **NOT_REACHED_EXACT_ANCHOR** |
| Original MATLAB private 3 components at HGFX-own x6 | **0** | `3.277081539465598e-08` | 0 | **NOT_REACHED_EXACT_ANCHOR** |
| Original MATLAB 3 components at x0 AND original x6 | **1: x0 only** | `2.2791900811114374e-07` | `2.606898235057997e-07` | x6 not reached |
| Original MATLAB 3 components at all 25 original HGFX-own history occurrences | **1: x0 only** | `2.2791900811114374e-07` | `2.606898235057997e-07` | 24 distinct source x, only one reached |

All eight original optimizer runs reported `tol_grad` termination and completed. No hidden nonconverged or failed arm was dropped.

**Original same-host baseline source consistency guard:** the new-host **unmodified** HGFX run first diverged bitwise from the archived original HGFX `iter.x` at **record 2** (0-based), maximum absolute coordinate difference over original 25 retained source rows **`9.060663330728858e-10`**, final transformed free-vector max difference to original HGFX endpoint **`1.4572520967703895e-10`**. This is **not a bitwise original full-fit replay**, despite small scales and unchanged final original-HGFX-to-MATLAB max distance.

**Critical no-hit qualification:** all 25 original history anchor occurrences were retained in the protocol, but new-host trajectory deviated by record 2 and did **not** hit the exact original record-6 x; thus x6-only arms' unchanged endpoints DO **NOT** establish no causal effect. The all-25 arm in fact triggered at only **the initial x**, so it is not evidence that substituting every original gradient along an unchanged path has been tested. Never replace exact matching with approximate coordinates without a **new separately recorded protocol**.

## What can and cannot be concluded

The same-host original-HGFX-gradient placebo **exactly matched** the within-host baseline endpoint; direct MATLAB-private component-0 gradient at the original start shifted the counterfactual endpoint **closer by about a factor 9.9**, while replacing all three start components shifted it **farther by about a factor 6.95**. Small source-gradient perturbations can change the final BFGS path in both directions; this is a **bounded optimizer numerical sensitivity result**, not evidence that MATLAB's derivative or its resulting fit is absolutely correct.

At the original *unreached* record 6, prior real private MATLAB/HGFX same-x Ridders discrepancy, and original source Hessian/Armijo diagnostics, remain valid historical observation but lack this experiment's causal intervention. The exact reference scientific cause of the original 4+4 trajectory differences is **still unproven**, with implementation/optimizer/environment/model-selection uncertainty requiring external review and potentially separately precommitted experiments.

**No scientific gate promotion, no changed fitting acceptance threshold, no missing original failures, no reinterpretation of any counterfactual as the original frozen package, no performance-timing or GPU/speedup claim.** Issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) remains pending independently signed scientific disposition; PERF-01C **NOT FROZEN**.
