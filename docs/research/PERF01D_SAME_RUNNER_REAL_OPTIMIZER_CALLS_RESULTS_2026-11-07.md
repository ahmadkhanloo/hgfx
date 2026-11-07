# PERF-01D — same-CPU-runner actual frozen HGFX and MATLAB optimizer source callstreams and source-executed HGFX Armijo (2026-11-07)

**AUTHOR-SIDE REAL EXECUTION + SEPARATE SHA-LOCKED ARCHIVE REPLAY SUCCESS. ORIGINAL 63/64 SCIENTIFIC FITTING: NONPASS. NO SIGNED INDEPENDENT REVIEW. PERF-01C NOT FROZEN. NO PAPER TIMING OR PHYSICAL GPU VALIDATION.**

## Source-of-truth constraints and prespec

This new actual paired-runner experiment followed [same-runner prespec](PERF01D_SAME_RUNNER_REAL_OPTIMIZER_CALLS_PRESPEC_2026-11-07.md) at commit **`b9c8a1be17ba46104add2113ecba3fde4f246040`**, made before any fresh paired source-call observations. Subject 7 was originally selected *post-result* from the 64-subject incident: this is exploratory forensic engineering, **not** a preregistered scientific acceptance gate. Original full public frozen 64-subject [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) remains **63/64 SCIENTIFIC NONPASS** with exactly **four `traj.mu` and four `traj.muhat`** out-of-existing-tolerance entries for zero-based subject 7. Original 15/16 NONPASS, all original 28 PERF-01C cases (16 review-pending / 12 blocked), seeds, thresholds, model, priors and original failed experiment artifacts unchanged.

Frozen HGFX 1.0.0 **`4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`**; frozen MATLAB HGF Toolbox 8.2.0 **`2437f4dc241541072722a2695ddeca7b44d83dd3`**, same original subject/128-trial binary data, `hgf_binary` + `unitsq_sgm`, free start `[-3,-6,3.871201010907891]`, original quasinewton options and Ridders `min_steps=10`. Exact original BFGS archive [42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) raw HGFX SHA-256 `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`, raw MATLAB SHA `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a` were verified before execution.

**Same runner means two independent original full public fits executed in the SAME GitHub Actions Ubuntu job at the SAME tested commit**, not the same process or identical vector at all later iterations. New Python HGFX full public `fit_model` was run unwrapped and with a temporary `FitProblem.evaluate_free` logging method; all **15 originally selected stable `optim` and 11 `traj` field pairs and complete `optim.iter`** were strictly equal (NaNs paired), original method and source-line tracer were restored. The frozen HGFX optimizer implementation was not edited. Source-line execution of the Python original optimizer captured *actual executed branch bodies*: original Armijo `break`, accepted-state assignment, curvature update, clipping and gradient termination. Frozen original MATLAB public `fitModel` was run native and via the previously validated delegated optimizer with exact private objective wrapper, and its real raw **26/26 stable fields and all `optim.iter`** were again verified via independent SciPy raw MAT-v7 parser. Original MATLAB source optimizer likewise unchanged. Both actual source traces were matched by exact GitHub run ID and tested SHA; missing/different runner was a fail-closed condition.

## Engineering execution log (failed attempts preserved)

| Execution | SHA / result |
|---|---|
| [42387121635](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387121635) | **FAILURE before any new original fits**; synthetic test fixture lacked direct MATLAB `call_number` and one negative-test regex differed. Narrow synthetic-only correction at `229e6ff14bedd4a9c4f6aae97160430907c91e00`. |
| [42387187121](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387187121) | **FAILURE before original fits**; one synthetic test incorrectly expected no first different trial when HGFX mock had 1 trial and MATLAB mock had 24. Fixed assertion to *preserve missing partner at index 1*, commit `52268e5220169aae3615d373bd52472e5e9a2336`. |
| [**42387244467**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387244467) | **SUCCESS** at exact frozen-runner evidence code SHA **`52268e5220169aae3615d373bd52472e5e9a2336`**. 15/15 source-call negative/positive controls, original frozen Git SHA and original 63/64 failed scientific source guards, real HGFX/MATLAB same-runner original public fits, strict native/wrapped neutrality, independent Python source event comparator and real raw MATLAB MAT parser. No timer. |
| [42387733662](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387733662) | **FAILURE before archive replay**: three negative synthetic assertions expected the wrong wording for an already correctly detected branch mismatch; archived source evidence unmodified. Corrected at `d7a523ebabe6dd83585c0aaedf0b40e0789a411d`. |
| [**42387781223**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387781223) | **SUCCESS** at `d7a523ebabe6dd83585c0aaedf0b40e0789a411d`: 10/10 fail-closed synthetic controls; SHA-verified all four original raw source members and prior same-runner derived comparator; independently checked every one of the 24 HGFX actual Armijo/accepted-body events against **the exact corresponding source objective call**, original `j`, optimizer iteration, candidate x and objective scalar bits. Computed exact per-coordinate binary64 ULP differences for all 24 paired MATLAB-own/HGFX-own trial vectors. No fresh fits/MATLAB/GPU. |

### Immutable evidence and hashes

Actual paired-runner [artifact **13579828855**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387244467/artifacts/13579828855), GitHub artifact ZIP SHA-256 **`cc340ee9e6a4ee784910a01f34c8bf08359f10f5e22fb4ca8389c1646de94f31`**:

| Original real artifact member | SHA-256 |
|---|---|
| `actual-frozen-hgfx-original-optimizer-source-calls.json` | `56b2e80272c42f0affd4c0084a28fc65e6ba737cf3d67335918c8ff49c335ac3` |
| `actual-frozen-matlab-optimizer-source-calls.json` | `7604e4311d2d66c3b5fc17e54db4f4fee62915e0988887168122d4cdbd58b94d` |
| `matlab-native-and-wrapped-26-plus-iter.mat` | `fe5e8ea763496a0f0fe76864bed42b849a4ad7f2878d4ad7edac383ff0c83b74` |
| `independent-same-runner-source-comparison.json` | `9ef73979f96627baa201aa72a2b9ad1b8df0a2b2273cb9b1d72ace14212d0cce` |

Source frozen HGFX original `compat_quasinewton.py` SHA-256 `13b919b849908a5bba4b079f570127eb1acf6282c83bf1287d589d6a02f47125`. Source MATLAB original `quasinewton_optim.m` SHA-256 from the previous source audit `017e766ffed61c17be26bb4f2af820fe0186ee91bc0b643fc119b81b4f788c7e`. The source Git commit SHA identities and checks are stronger than guessing paths or versions.

Independent **archive-only** branch audit [artifact **13579674778**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387781223/artifacts/13579674778), ZIP SHA-256 **`1cd39d68921b07c6b76456531a04fde6d516c48e9240ee07615d167b50da7b78`**; derived `actual-hgfx-24-armijo-source-body-replay.json` SHA-256 **`9519985759ef6f0ad98de19139e5ea156dc116cacf7863731223390543723e9e`**. Exact archived complete 24-row source and branch events are retained, including each original iteration and `j`, plus the original paired MATLAB path and metadata.

## Real same-runner source-call evidence

| Recorded quantity | Original HGFX | Original MATLAB |
|---|---:|---:|
| Direct initial objective calls | 1 | 1 |
| Direct source line-search candidate objective calls | **24** | **24** |
| Direct source reset objective calls | **0** | **0** |
| Indirect objective calls (mostly Ridders, NOT individually audited by calling category) | **2,138** | **1,913** |
| Total original objective calls | **2,163** | **1,938** |
| Executed original Armijo-success `break` body | **24** | **NOT CAPTURED (MATLAB callsite only)** |
| Executed original accepted-state update body | **24** | **NOT CAPTURED** |
| Executed original curvature BFGS-update body | **22** | **NOT CAPTURED** |
| Executed descent-vector step clipping body | **11** | **NOT CAPTURED** |
| Executed gradient stopping body | **1** | **NOT CAPTURED** |
| Real observed original HGFX Line Search regularization exponent `j` | **24 × `j=0`** | **`j` not captured in original private MATLAB callback** |

The new archive-only independent verifier matched all 24 actual HGFX source candidates **one-to-one, in time order**, to all 24 **executed** Armijo-success bodies AND all 24 executed accepted-state update bodies, requiring identical *actual* `j`, optimizer iteration, source candidate x **binary64 bytes**, and actual objective scalar bytes. This supports a strictly bounded finding: **all 24 actual original HGFX full steps with j=0 were accepted without a half-step in this run**. It is **not** inferred solely from a stored history; actual original Python source branch body execution was observed. There are 22 executed Python curvature-update bodies, but this does not demonstrate exact parity of MATLAB curvature decisions. MATLAB native/wrapped public fit was neutral, but its source `if` Boolean outcomes were not instrumented.

### First real divergence (not a scientific model diagnosis)

Both engines start at the exact same transformed free x `[-3,-6,3.871201010907891]`; nevertheless **the first real line-search trial candidate vectors differ at zero-based trial 0**. First candidate **maximum absolute coordinate difference**: **`9.769962616701378e-15`**; exact three coordinate component ULP distances: **`[8, 11, 3]`**. **All 24 paired ordinal trial candidate vectors are bitwise distinct**. Therefore there are **zero exact same-x line-search candidate scalar comparisons** within these 24 pairs; differences between objective values at different own-path coordinates must **not** be labeled an HGFX/MATLAB objective-function mismatch.

The two same-runner 25-row original own-engine `iter.x` paths first differ in bits at zero-based history record **1**. Maximum absolute component delta among corresponding history records is **`3.734656921494661e-07`** for this new run. The new-host **unmodified HGFX own history** matched the separate-run historical HGFX own history bitwise at only **2/25** records (per original real-run summary). Thus cross-run HGFX binary64 replay is not assumed and original host/environment repeatability issue [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) remains open. Cross-engine first candidate difference is a real same-runner observation, but **does not uniquely identify the source**: derivative approximation, internal arithmetic order, BLAS/platform effects, objective value roundoff, and cumulative optimizer sensitivity require separate evidence. The first source candidate could also reflect small direction rounding despite closely matched gradients; source branch equality cannot be inferred from fitted endpoints alone.

The difference in total objective calls (**225** more from HGFX, entirely in indirect calls in this run) is a **diagnostic count**, not a performance-speed result, and not yet a proven exact difference in Ridders stencil/stopping paths. No wall-clock timers, GPU or scientific acceptance adjustments were run. At same vector the original reference was separately probed in previous experiments; the current paired source trial coordinates **are not the same vectors**.

## Reviewer and release gate boundary

**DONE/PASS ENGINEERING:** real same runner source-instrumented public fits with strict native/wrapped 26 fields + complete optimizer iteration state neutrality; Python source-executed 24 real Armijo/24 accepted-state/22 BFGS curvature/11 clipping/1 grad-stop body events; SHA-locked independent 24/24 event-to-call verification and exact first 8/11/3 ULP trial candidate difference; original 63/64 source failure preserved.

**NOT VALIDATED:** true MATLAB private `if` branch outcomes or exact original MATLAB gradient stopping, full reference optimizer causal path, scientific parity of subject-7 4+4 trajectory failures, all original 28 case performance gate scientific eligibility, model-selection/scientific identifiability. The 25 public fit rows do NOT imply all 25 iterations accepted due terminal overwrite. No publication speedup or physical GPU validation.

Issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) independent reviewer identity/signature and explicit `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE` **NOT RECEIVED**. Hence PERF-01C **NOT FROZEN**, 16 review-pending / 12 blocked original workload cases, no final paper performance timing. The original 63/64 fitting is **NONPASS**, not an approved MATLAB reference limitation. Related [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) and environment [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) remain OPEN; draft PR #94 must not be confused with scientifically reviewed compatibility or merged as reviewer-approved evidence.

### Next falsifiable scientific question

The **225 additional indirect HGFX objective evaluations** in an otherwise same-runner, 24-full-step source trace suggest a useful narrower diagnostic: inspect original Ridders `riddersdiff` calls and stopping decisions along the *same starting vector* and actual first chosen direction, with each side's original objective and unchanged `min_steps=10`. Independently record exact same-x stencil values and source stopping branch decisions, without relaxing the original fitting tolerance or excluding failures. Until tested, **numerical/optimizer sensitivity remains a candidate explanation**, not a settled cause.
