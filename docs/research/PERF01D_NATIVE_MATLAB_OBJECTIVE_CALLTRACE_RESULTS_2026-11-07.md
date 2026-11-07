# PERF-01D — frozen MATLAB-owned native optimizer direct objective-call trace (2026-11-07)

**AUTHOR-SIDE ORIGINAL MATLAB SOURCE-CALL OBSERVATION: EXECUTED AND VALIDATED. NOT an independent scientific review verdict. Original full fitting 63/64 SCIENTIFIC NONPASS; PERF-01C NOT FROZEN; no speed/GPU timing.**

## Purpose and pre-observation contract

Actual source-call observation was specified before execution in [PERF01D_NATIVE_MATLAB_OBJECTIVE_CALLTRACE_PRESPEC_2026-11-07.md](PERF01D_NATIVE_MATLAB_OBJECTIVE_CALLTRACE_PRESPEC_2026-11-07.md), committed at **`65e321c0e8f6555d5f0db71a92638faa74943627`**. The experiment/subject selection was explicitly **post-result exploratory** and cannot establish a prospective scientific PASS. Previous [actual private MATLAB three-point Armijo](PERF01D_PRIVATE_MATLAB_X7_ARMIJO_RESULTS_2026-11-07.md) used **HGFX-owned** x6/T6 hypothetical counterfactual candidates. **This experiment instead records actual source calls from the frozen MATLAB-owned optimizer's own public fit path**, making no assumption that its x6/T6 matches HGFX's.

Frozen HGFX v1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`, original `hgf_binary` / `unitsq_sgm` binary data, zero-based subject 7 of 64, 128 trials, unchanged free start `[-3,-6,3.871201010907891]`, original priors, BFGS and 10-step-min Ridders. MATLAB source version R2026a as recorded in raw MAT/JSON. Input/config generator checks and both original BFGS raw source member SHA-256 checks passed before MATLAB execution.

Original full public paired cohort [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) **still 63/64 NONPASS** with exactly four `traj.mu` and four `traj.muhat` original out-of-tolerance elements in subject 7. Original 15/16 NONPASS, scientific policy and all 28 original performance case definitions are not changed.

## Technical observation and neutrality requirements

The unchanged original reference `core/quasinewton_optim.m` receives a wrapper function handle through the **existing public** `fitModel` optimizer-injection seam. The wrapper calls the original **private** nested objective **exactly once** at every real evaluation and uses MATLAB `dbstack('-completenames')` to distinguish source-direct calls from indirect Ridders/other calls. Its immediate source frame is checked against actual frozen original optimizer file/path and the original source code statement lines (not hardcoded expectation alone). Exact frozen direct `f(x)` initial/reset source sites are lines **91 / 172**; `newval = f(newx)` trial site is line **142**, source text SHA-256 **`017e766ffed61c17be26bb4f2af820fe0186ee91bc0b643fc119b81b4f788c7e`**.

Unwrapped MATLAB-native and wrapped-optimizer MATLAB public fits are run in the same host dispatch. All **15 original stable `optim` + 11 original `traj` field pairs** and the entire `optim.iter` array/struct are saved as actual MAT-v7 values and independently compared using SciPy on raw archive. The source optimizer itself is NEVER rewritten. These checks establish instrumentation neutrality for this selected public fit, not general scientific cross-implementation equivalence.

A source-direct objective **callsite** demonstrates an objective was evaluated at a given vector, **not the actual Boolean outcome of every private `if` branch**. Exact source direct-candidate membership in original stored history is recorded; terminal NaN-padded/overwritten or repeated records must never be counted as unique accepted iterations solely from membership. Indirect objective calls are counted, not individually categorized as gradient/Ridders vs other unless source directly establishes it.

## Complete execution accounting, including failures

| Run | Tested commit | Result / provenance |
|---|---|---|
| [42379808708](https://github.com/ahmadkhanloo/hgfx/actions/runs/42379808708) | `20eba553b71d24df3361cb52c9b52567b1ef55ea` | **FAILED before MATLAB**: one synthetic negative control expected lowercase `source` but error began with uppercase `Original`; 10 other synthetic controls succeeded. Corrected test assertion only at `5efac26eb940ec300302fb7d956235077970aa72`. |
| [42379878818](https://github.com/ahmadkhanloo/hgfx/actions/runs/42379878818) | `5efac26eb940ec300302fb7d956235077970aa72` | **FAILED at first real source optimizer objective call**: MATLAB sibling nested logging function could not see the `obj` handle local to its sibling. No verified complete objective trace produced. Correction stores the untouched objective handle in the parent shared workspace at `b3e116a890462c8ba7a9e2994b8fd2b6f68b0e86`. |
| [42380052412](https://github.com/ahmadkhanloo/hgfx/actions/runs/42380052412) | `b3e116a890462c8ba7a9e2994b8fd2b6f68b0e86` | **FAILED before executing wrapped optimizer**: escaped `\\n` characters accidentally kept the inserted MATLAB assignment and optimizer invocation on a comment line. No complete objective-call trace. Corrected **newlines only** `6b79b7a9c0e78777eae8994cb7312ec43a8a6f5d`. |
| [**42380372791**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42380372791) | **`6b79b7a9c0e78777eae8994cb7312ec43a8a6f5d`** | **SUCCESS**: 11/11 synthetic source/chronology/identity/negative controls, SHA-verified frozen evidence, actual MATLAB private objective-source direct call trace, archived original 26 public field pairs and full native/wrapped `optim.iter`, independently parsed from raw MAT-v7 and original MATLAB optimizer source. |

All failed runs remain visible; neither original scientific evidence nor any subject, seed, model, acceptance rule, optimizer source implementation or frozen start changed to make the engineering experiment pass.

## Actual source-derived observations

| Quantity | Directly observed / independently replayed |
|---|---:|
| All real private objective calls made by the wrapped original optimizer | **1,938** |
| Source-direct initial `val = f(x)` at original optimizer line 91 | **1** |
| Source-direct candidate `newval = f(newx)` at source line 142 | **24** |
| Source-direct reset `val = f(x)` at source line 172 | **0** |
| Indirect objective calls (primarily gradient calculations; not all separately classified) | **1,913** |
| Frozen optimizer direct-call source sites | `91, 142, 172` |
| Original finite public `iter` history entries (not declared iteration count) | **25** |
| Noninitial public `iter.x`/`iter.val` entries with at least one **exact** direct candidate/value match | **24 of 24** |
| All 26 raw public native-vs-wrapped stable field pairs | **strictly identical** |
| Entire raw native-vs-wrapped `optim.iter` (includes padded/overwritten terminal slots) | **strictly identical** |
| Synthetic fail-closed control tests | **11 / 11** |

The source-direct trial call inventory contains only the 24 original reference MATLAB-owned candidate evaluations; no direct reset objective was observed. This is stronger evidence of the actual evaluation pathway than hypothetical HGFX-own x6/T6 Armijo comparisons. However, **24 matched stored history rows do not by themselves prove 24 distinct accepted decisions**: duplicate/overwritten terminal records may map to the same underlying call. Source-direct call events have no direct `j` regularization index or private conditional Boolean. The archived JSON records every direct call and every exact original history membership for independent chronological adjudication, including unmatched and repeated matches.

## Immutable current-run raw evidence and source audit

[GitHub Actions **42380372791**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42380372791) / [artifact **13577282697**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42380372791/artifacts/13577282697), entire ZIP SHA-256 **`4da1e508c3c9d96275dda83c8d6406f4f4517c458bfcafd48f307114a79b44bd`**:

| Artifact member | Actual SHA-256 |
|---|---|
| `actual-original-matlab-optimizer-direct-calls.json` | `321393efe9aaf00c0fc96752de66fa27b4e9eebbc1b7f93ea485528ee59da2e9` |
| `native-vs-wrapped-public-plus-iter.mat` | `5b0b0006e36d3fe5391d89a1a7121239e20a8425cd14e6b7032b1887ec929dae` |
| `source-callsite-replay-and-history-membership.json` | `1bdaa8c7a5db9c27bef65691e2a988ab6172554f8bc22af1089fdeb22014a802` |
| Exact source `quasinewton_optim.m` (from frozen reference checkout, checked by source Git SHA) | `017e766ffed61c17be26bb4f2af820fe0186ee91bc0b643fc119b81b4f788c7e` |

Artifact contains `provenance.json`, exact tested SHA/source/run/commit metadata, prior immutable original BFGS source SHA checks (`hgfx_raw.json=060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`; `matlab_raw.json=4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`) and full raw MATLAB optimized-state field pairs. No physical GPU tests or paper-oriented time measurements were conducted.

## Scientific interpretation and required independent adjudication

**Established author-side:** the actual **MATLAB-owned** original reference optimization called its exact nested private objective at one direct start plus 24 trial vectors, with no directly observed optimizer reset, and an additional 1,913 non-direct calls. The original frozen public fitting output and entire bookkeeping history are bitwise/NaN-equal between native and instrumented MATLAB on this runner. The separate Python source parser validated original source line identities, counts, exact historical start and original 63/64 scientific failure, and stored all direct candidate-to-history memberships. Prior same-state x6 hypothetical results remain unmodified.

**Not established:** explicit private Armijo/curvature/gradient-stop source branch-event logs, unambiguous uniqueness of each terminal accepted step, original HGFX-owned direct call trace in this same dispatch, exact cross-run/cross-host bitwise matching of previous source histories, the causal path for the original HGFX-vs-MATLAB `traj.mu` and `traj.muhat` 4+4 mismatch, or a justified reference scientific limitation. The actual MATLAB original optimizer is unchanged but is passed a logging objective handle for this experiment; neutrality has been verified only on the defined public outputs and `iter` for this subject/run.

The next appropriate scientific decision is **independent review** of these source-call events against the original reference BFGS statements and the prior frozen HGFX `iter` trace, asking whether an actual early branch difference exists versus continuous amplification of sub-ULP numerical drift. This code path alone cannot settle the causal scientific discrepancy. Review issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) requires an identified independent reviewer and signed verdict `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE`, with all 28 original benchmark case cells and historical failures preserved. Issue [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) retains **63/64 NONPASS**, [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) retains separate host repeatability limitation, PERF-01C remains **BLOCKED**, PERF-01E–H **NOT RUN**, and no GPU/speedup claim is valid.
