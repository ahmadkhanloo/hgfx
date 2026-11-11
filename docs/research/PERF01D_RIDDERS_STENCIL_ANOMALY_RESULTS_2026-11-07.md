# PERF-01D — observed real MATLAB/HGFX Ridders stencil anomaly and frozen-source Richardson replay (2026-11-07)

**AUTHOR-SIDE EXPLORATORY DIAGNOSIS: EXECUTED AND REPRODUCED. ORIGINAL PUBLIC FULL-FIT SCIENCE: 63/64 NONPASS. INDEPENDENT REVIEW: NOT RECEIVED. PERF-01C: NOT FROZEN. NO PERFORMANCE TIMING OR SPEEDUP/GPU CLAIM.**

## Provenance and non-prospective selection

This is a strictly **post-result** diagnostic of **one deliberately selected maximal observed same-x Ridders gradient discrepancy**, not a prespecified validation sample or an eligibility criterion. The prospective **original 50-occurrence** direct-private gradient analysis and all its original counterexamples remain preserved in [the 50-point source report](PERF01D_DIRECT_NESTED_GRADIENT_BFGS_RESULTS_2026-11-07.md) and original [run 42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614).

**New probe protocol committed before any fresh stencil samples:** [`e1c3e2e83045896195701926a5f94fa361b0f091`](https://github.com/ahmadkhanloo/hgfx/commit/e1c3e2e83045896195701926a5f94fa361b0f091), [protocol](PERF01D_RIDDERS_STENCIL_ANOMALY_EXPLORATORY_PROTOCOL_2026-11-07.md). Original frozen HGFX 1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; frozen MATLAB HGF Toolbox 8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`. MATLAB R2026a Update 5, Ubuntu 24.04 / Python 3.11 / NumPy 2.3.5. Original model `hgf_binary` / `unitsq_sgm`, zero-based subject **7**, 128 trials, unchanged full original priors and free start, optimizer and Ridders options. Original selected **HGFX-own** BFGS record zero-based **6** with x `[-1.1621811570388512,-6.37816839506084,-0.23738383160834042]`.

Original science remains **63/64 NONPASS** (subject 7: 4 `traj.mu` and 4 `traj.muhat` failed values), 15/16 NONPASS and all eight original same-runner failures. The 50-source observation's maximum same-x gradient component discrepancy was `6.884955006114524e-08`, even though base private MATLAB/HGFX objective values exactly agreed at that x. No original historical result, threshold or seed is rewritten.

## Source-faithful execution history (including engineering failure)

- **First new workflow [42361236226](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361236226), SHA `0b99aed38b005179a7c4805c826215cc51b928b7`: FAILED before MATLAB** because a synthetic truncated-trace test supplied six calls, below its own prescribed minimum of seven. **12/13 tests succeeded; one test errored.** No measured scientific stencil data from this attempt; failure retained in Actions log. Fix commit `fd32140920dce7d88559c79c44b08d32b303eb62` changed **test construction only**, not frozen source, target, parameters, thresholds or data.
- **[Actual private nested MATLAB stencil run 42361286407](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361286407)** at `fd32140920dce7d88559c79c44b08d32b303eb62`: **SUCCESS**; **13/13** synthetic/fail-closed engineering controls, all earlier original SHA-256 source artifacts reverified, original `riddersgradient` called at exactly the selected original free x using the real private `fitModel` objective, every actual objective call in source order recorded. The private-hook fitting was delegated to the original optimizer; **28/28 native-vs-instrumented public scientific outputs strictly binary64 equal**. Independently frozen HGFX `ridders_gradient` was traced at the exact same x. Source values and the original 50-point reference-gradient vector were reproduced exactly. [Complete artifact **13569423003**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361286407/artifacts/13569423003), ZIP SHA-256 `fc8068b3d0fe5d6bfacc4ace54c00ee4adca29be0fea1c6ac7dd4c12a6eb6e4e`.
- **[Frozen-source Richardson-selection replay 42361769881](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361769881)** at `59d1f6390bf39401f59cf0fae470302f9123ab58`: **SUCCESS**, **10/10** additional positive/negative controls; downloaded the *exact* archived original stencil SHA-256, replayed source `utilities/riddersdiff.m` Richardson table/arithmetic from actual recorded values for all three components, and **reproduced exact binary64 archived gradient and internal error for all 3 components in both engines**. This is a **source-formula replay, not a direct MATLAB internal-branch event log**. [Complete replay artifact **13569229297**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361769881/artifacts/13569229297), ZIP SHA-256 `1e66252097e525f868493ac23633152e3a5d5edeb1da91dde84d0abf1cfb67b8`.

Immutable artifact member SHA-256:

| Run and raw member | SHA-256 |
|---|---|
| 42361286407 `locked-postresult-stencil-target.json` | `12f7ea77552cc48a50fbaa26ef8b89c9a22c7f94a444900eb4862aa6b2e498f7` |
| 42361286407 `actual-private-matlab-stencil-trace.json` | `8f068c88cde8fd18df03e40c8f525214239786d43b3f524b06898a14a2fd1986` |
| 42361286407 `paired-actual-ridders-call-streams.json` | `45d06ee935637c6c110a75d56e77b42db0d6d9977abac58f6969115ee407f66e` |
| 42361769881 `reconstructed-original-richardson-selection.json` | `245ba51c07d1bce7bb13b4e4bef7382880d62d76ccb787b8206e8a5f474751da` |

The ZIP and member SHA-256 hashes above were independently checked against the downloaded artifacts and the included `provenance.json` records. No timer was run.

## What was actually observed at original x: the 1–2 ULP off-base difference

Both original algorithms evaluated `f(x)` first, and then all their executed `x+h` / `x-h` source points. The streams retained every call; no posthoc sample exclusion or interpolation onto approximate coordinates was performed.

| Direct source trace observation | Result |
|---|---:|
| Actual HGFX objective calls | **249** |
| Actual frozen MATLAB private objective calls | **245** |
| Chronologically aligned calls with **bitwise-identical coordinates** | **245** |
| Of these 245, equal scalar objective values | **212** |
| Of these 245, scalar objective differences | **33**, all 1–2 ULP |
| Maximum equal-x objective difference | **2 ULP = 2.842170943040401e-14** |
| First different scalar at an identical coordinate | Call zero-based **12** |
| Four extra HGFX calls not evaluated by MATLAB | Source call indices **245–248**, third-coordinate tail |
| MATLAB native-vs-instrumented public fit control | **28/28 exact binary64** |

The individual source-coordinate call inventory (including original `f(x)`): for the first free component both engines evaluated **200** +/- calls = **100 finite-difference levels**; for the second component both evaluated **22** calls = **11 levels**; for the third component HGFX evaluated **26** calls = **13 levels**, MATLAB **22** = **11 levels**. Equal-coordinate scalar mismatches by component: **26** in the first component, **5** in the second, **2** in the third. The base `f(x)` scalar is exactly equal in both engines.

**Numerical trigger at the very first finite-difference step:** for the first free component, original initial `h=1`, the actual **same-x** reference and HGFX `f(x+h)` both equal `1.7976931348623157e+308`, **the maximum finite binary64 number (`realmax`)**. The negative-side objective is `105.76934563436332`. The frozen MATLAB private `fitModel.m` can return `realmax` in its negative-log-joint failure-handling path; this is consistent with, but does not prove which internal failure category produced, the observed sentinel.

## Reproduced exact-source Ridders extrapolation mechanism

Source files: frozen [`utilities/riddersdiff.m`](https://github.com/ComputationalPsychiatry/hgf-toolbox/blob/2437f4dc241541072722a2695ddeca7b44d83dd3/utilities/riddersdiff.m), [`utilities/riddersgradient.m`](https://github.com/ComputationalPsychiatry/hgf-toolbox/blob/2437f4dc241541072722a2695ddeca7b44d83dd3/utilities/riddersgradient.m), [`core/fitModel.m`](https://github.com/ComputationalPsychiatry/hgf-toolbox/blob/2437f4dc241541072722a2695ddeca7b44d83dd3/core/fitModel.m), unmodified throughout. Source algorithm uses `init_h=1`, `div=1.2`, `min_steps=10`, `max_steps=100`, `tf=2`; Richardson candidates `P(i,j)` and the minimum within-engine parent-difference error are compared on every row.

Replaying the actual preserved 100 first-coordinate `f(x±h)` pairs under this exact frozen formula yields **5,050 populated triangular Richardson entries**, of which **195 are +Inf/-Inf and 194 NaN**, identically for each engine. The diagonal first becomes infinite at zero-based level 2 and NaN at level 3. Under the original source stop condition, comparisons involving the NaN diagonal cannot trigger the `tf*err` stop test, so the first-coordinate replay reaches the **entire 100-level max_steps ceiling**. No source function or limit was patched. The finite returned gradient is then chosen by the frozen *minimum internal extrapolation error* rule from very late, small-h candidates:

| First free-parameter derivative | Frozen HGFX | Real private frozen MATLAB |
|---|---:|---:|
| Source actual finite-difference levels | **100** | **100** |
| Replayed selected Richardson row (zero-based) | **80** | **87** |
| Replayed selected Richardson column (zero-based) | **1** | **1** |
| h at selected row | **4.6291400080406515e-07** | **1.291908018719193e-07** |
| Exactly reproduced gradient | **5.046862798072859** | **5.046862866922409** |
| Exactly reproduced source Ridders internal error estimate | **8.881784197001252e-16** | **2.6645352591003757e-15** |
| Absolute difference between the two gradients | **6.884955006114524e-08** | **6.884955006114524e-08** |

For completeness, the same exact source-formula replay reproduces the other two returned gradient components and errors in both engines. Component 2 (zero-based 1): 11 levels in each, selected (row 9, column 5) HGFX vs (row 7, column 7) MATLAB; component 3 (zero-based 2): 13 levels, selected (row 11, column 7) HGFX vs 11 levels, selected (row 10, column 9) MATLAB. The four additional HGFX evaluations belong only to the third component and were **not** paired with nonexistent MATLAB source calls.

**Source-localization conclusion, limited to this selected derivative:** the real preserved objective perturbation values and original Ridders arithmetic deterministically reproduce the observed discrepancy, including the 100-step exhaustion and different late extrapolant selection. The MATLAB/HGFX base objective exactly agreeing at `x` does not imply equal derivatives; 1–2 ULP differences at actual `x±h` are relevant. The tiny internally reported Ridders errors do **not** bound cross-engine numerical discrepancy here. This is direct support for **optimizer/numerical-path sensitivity**, not evidence justifying a changed tolerance or a verdict that HGFX implementation is wrong. The very first `realmax` sentinel is a plausible source-level mechanism for the nonfinite extrapolation table; which underlying model/likelihood error originally produced it remains unmeasured.

## Remaining scientific boundary and required review

None of these new diagnostics evaluates the full 64-subject public fit scientific gate anew or resolves whether this one derivative selection is **causally sufficient** to produce the 4+4 final `traj.mu`/`traj.muhat` mismatches. The previous [50-anchor BFGS margin reconstruction](PERF01D_DIRECT_NESTED_GRADIENT_BFGS_RESULTS_2026-11-07.md) observed 22/22 curvature agreements and Armijo-compatible transitions for each original engine, but these too were **not logged internal optimizer decisions**.

Independent reviewer [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) must review the frozen source, SHA-verified traces, source-formula replay, original failed public fits and explicit post-result selection. Reviewer should classify implementation mismatch vs numerical optimizer instability vs model-selection mismatch vs scientific limitation vs insufficient reference evidence. **No scientific PASS, no PERF-01C freeze, no original acceptance-tolerance or dataset changes, no benchmark timing, no GPU claim, no manuscript speedup.**
