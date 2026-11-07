# PERF-01D — same-source-state original HGFX BFGS step 6, gradient substitution sensitivity (2026-11-07)

**POST-RESULT EXPLORATORY SINGLE-STEP ALGEBRA; AUTHOR-SIDE CI SUCCESS, ORIGINAL SCIENTIFIC FITTING 63/64 NONPASS, EXTERNAL REVIEW NOT RECEIVED, PERF-01C NOT FROZEN. NO TIMING/GPU/SPEEDUP.**

## Scientific position and provenance

The historical frozen HGFX v1.0.0 / original MATLAB HGF 8.2.0 complete public 64-subject fitting failure **63/64 NONPASS** remains unchanged (zero-based subject **7**, four `traj.mu` plus four `traj.muhat` out-of-original-tolerance trial values). All original failed real same-runner experiments, all 28 original benchmark cases and independent reviewer issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) are retained. Frozen MATLAB oracle SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`; frozen HGFX v1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Neither source, dataset, thresholds nor optimizer policies were changed.

The [direct-private objective/Ridders 50-history-anchor experiment](PERF01D_DIRECT_NESTED_GRADIENT_BFGS_RESULTS_2026-11-07.md) recorded an anomalous same-x `6.884955006114524e-08` first gradient-component difference at historical HGFX source BFGS record zero-based **6**. [Actual frozen Ridders stencil source replay](PERF01D_RIDDERS_STENCIL_ANOMALY_RESULTS_2026-11-07.md) reproduced its 100-level, `realmax`-contaminated extrapolation and differing best rows. [Eight-arm exact-bit gradient interposition result](PERF01D_ORIGINAL_GRADIENT_INTERPOSITION_RESULTS_2026-11-07.md) found the **historical x6 was not reached** on the new runner, so those whole-optimizer x6-only interventions were **NOT_TRIGGERED**; no causal negative can be claimed.

**Important selection disclosure:** the original x6 maximal discrepancy was selected **after** observing the fixed 50-point results. A preliminary author-side local calculation of these x6 one-step candidate differences had also already been conducted **before this reproducible script and CI were committed**. Thus this is an exploratory, already-inspected algebraic follow-up, **not prospective independent evidence for a scientific acceptance gate**.

## Bounded same-state comparison and source formula

Use the **unaltered historical HGFX source** x at original BFGS history record **6**:
`[-1.1621811570388512,-6.37816839506084,-0.23738383160834042]`, its **same original saved** 3×3 inverse-Hessian matrix `T6` from [original run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), and scalar original `f(x6) = 108.28848680066957`. Feed **two** numerical gradients measured on **exactly this original HGFX x6** into the same original MATLAB `core/quasinewton_optim.m` source step formula: (a) original HGFX Ridders gradient `[5.046862798072859,0.004963434493695078,12.997797151110694]`; (b) genuine frozen **private nested MATLAB** Ridders gradient at this same HGFX x6 `[5.046862866922409,0.004963434493194171,12.99779715111046]`. Both came from the original [50 direct-private probe 42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614).

For each gradient compute **original unclipped** `d = -T6 @ grad`, original `slope = grad @ d`, source `maxStep=1` clipped direction `d/||d||` when `||d||>1`, a single `x_next = x6 + clipped_d` full-step candidate, **unchanged** source `1e-4 * slope` Armijo RHS and original fixed-subject frozen HGFX `evaluate_free(x_next)` as LHS. Compare both descriptive candidate x values to the actual preserved original HGFX-own x7 and **different-x MATLAB-own** x7. This is a **one-step frozen-source-formula reconstruction**, not modified MATLAB execution, not an entire optimizer branch log, and not a genuine public-fit experiment. Actual frozen MATLAB **private** objective was **not** evaluated at these two new candidate x7 values.

Immutable archive verification: original BFGS HGFX raw SHA-256 `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`; MATLAB raw SHA-256 `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`. 50-source paired report SHA-256 `2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d`; prior anchors SHA-256 `d92690111b2fa128c045f29b39aa95110b5e5cd838f90c48a733400a3e537913`; MATLAB private raw SHA-256 `90de6c75c13736fae95bc0645950ac0352546fd7262c4d5f70d97f8b9b14e978`. These were checked prior to computing the two candidates, along with original unchanged 63/64 failed full-fit outcome and source-config/data identity.

## Executed CI and observed numerical response

[Real CI **42366705874**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874) **SUCCESS**, executed diagnostic commit **`9e4bffaba040e2f66b8b3d985053a6b2a353b4a5`**, **10/10** synthetic controls and verified original SHA-256; frozen original HGFX 1.0.0 installed, same fixed subject original data; no original source patch or timing. [Artifact **13572445302**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874/artifacts/13572445302), ZIP SHA-256 **`654667abec22c7b59e00bbf19ee5db2308414cdff398e4ca1409eeb6c376109c`**; full report `source-same-state-two-gradient-candidates.json` SHA-256 **`b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144`**. Source-algebra code: [`subject7_one_step_exact_same_state.py`](../../benchmarks/runtime_v1/subject7_one_step_exact_same_state.py), with source and model error checks.

| Source-based quantity | Frozen HGFX original gradient at original x6 | Real-private MATLAB gradient at **same original HGFX x6** |
|---|---:|---:|
| `||-T6 grad||` before max-step clipping | `1.2488674959153816` | `1.2488675492807984` |
| Clipping invoked (`maxStep=1`) | Yes | Yes |
| Unclipped gradient·direction | `-5.994998154185824` | `-5.99499832595494` |
| Frozen HGFX `evaluate_free` at reconstructed one-step candidate | `105.8665439753067` | `105.8665440308226` |
| Reconstructed source Armijo full-step inequality on that **HGFX objective** | True | True |
| Candidate discrepancy vs original HGFX recorded x7 (max absolute component) | `5.329070518200751e-15` | `1.0444791836983214e-08` |

**Key fixed-state sensitivity:** replacing only the Ridders gradient vector *in the very same original x6 and T6* moves the source-formula **one-step candidate** by **`1.0444791836983214e-08`** in its largest free-coordinate component. The maximum recorded **original HGFX-own vs original MATLAB-own x7** component difference is **`1.964719109626145e-09`**. These are different contrasts: the original MATLAB-own x6 and T6 are not the HGFX x6 and T6. Do NOT equate either new counterfactual x7 to the actual original MATLAB next x7; do not ascribe the full historical path separation to this single numerical source error.

The original HGFX-gradient source candidate reproduces its original saved actual HGFX next x7 to **`5.329070518200751e-15`**, providing a source-algebra check. The MATLAB-private same-x-gradient counterfactual is also a **valid full-step Armijo candidate on the frozen HGFX objective** (not the unmeasured MATLAB private objective). Both hypothetical one-step paths are compatible with the *same* Armijo Boolean result under these limited conditions. This is consistent with source-gradient sensitivity in BFGS direction formation **without** a recorded branch flip. It is **not** a demonstration of the *real* MATLAB private optimizer's acceptance choice.

## Scientific interpretation and independent reviewer disposition

**Established only in this fixed source state:** the observed same-x Ridders difference is large enough after multiplication by the original saved BFGS inverse Hessian (and source max-step normalization) to alter the next-step candidate on the order of 1e-8. It can therefore contribute to a plausible numerical path-sensitivity mechanism. It is not proof that this difference occurred as a decisive cause of the original whole-fit divergence or that the original MATLAB private objective accepted the new hypothetical candidate.

**Not established:** an actual internal branch-event trace, exactly matched original different-engine x6/T6, replacement at x6 in the new-host public full fit, every subsequent optimizer step, trialwise post-fit trajectory parity, scientific reference limitation, or original 64/64 PASS. The original original source failure **63/64 NONPASS**, eight same-runner failures, PERF-01C **NOT FROZEN**, no independent reviewer verdict and no runtime/GPU/manuscript speedup remain binding.

Independent reviewer [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) should review source formula and SHA provenance alongside the original failures, distinguish numerical sensitivity from causal proof, and record a separately signed verdict before any scientific gate adjustment.
