# PERF-01D — direct frozen private MATLAB Ridders and original BFGS decision margins (2026-11-07)

**AUTHOR-SIDE ENGINEERING EXECUTION: SUCCESS. ORIGINAL SCIENTIFIC FITTING: 63/64 NONPASS. EXTERNAL SCIENTIFIC REVIEW: NOT RECEIVED. PERF-01C: NOT FROZEN. PERFORMANCE TIMING: NOT RUN.**

## Predeclared experiment and original failed evidence

The prospective source-locked protocol was committed **before** new direct-private-gradient observations as [`0ed460572d5323ba6e1c1f562955755eea7a29d7`](https://github.com/ahmadkhanloo/hgfx/commit/0ed460572d5323ba6e1c1f562955755eea7a29d7); see [protocol](PERF01D_DIRECT_NESTED_GRADIENT_BFGS_PRESPEC_2026-11-07.md). All **25 populated original BFGS history records from each of the original HGFX and MATLAB real public fitting histories** (50 occurrences, 24 distinct vectors in each original history) were retained, in source order, including duplicates; not the two MATLAB-only histories of the earlier scalar objective experiment.

Frozen original HGF Toolbox v8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, frozen HGFX v1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; MATLAB R2026a Update 5 (`26.1.0.3346908`), Actions Ubuntu 24.04 / Python 3.11 / NumPy 2.3.5 / CPU. Original zero-based subject **7**, 128 trials, `hgf_binary` / `unitsq_sgm`; start `[-3,-6,3.871201010907891]`, free indices `[12,13,14]`, original source objective/gradient and optimization settings. Original BFGS archive [run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) @ `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d`, validated exact SHA-256: `hgfx_raw.json` = `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`; `matlab_raw.json` = `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.

The original complete 64-subject public fitting outcome **63/64 NONPASS** is unchanged: subject 7 fails **4 `traj.mu` and 4 `traj.muhat`** elements under the existing scientific tolerances. The source 16-subject check remains **15/16 NONPASS**; all eight later real same-runner failing comparisons remain recorded. No thresholds, seeds, subjects, datasets, reference code, original raw files, or workload eligibility have been changed.

## Runs, preservation of failures, raw evidence provenance

1. [42305357824](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305357824) at `bc1f1458fec68ac98c3e14663bec40c155251345`: **FAILED at pre-execution MATLAB decoded-array shape validation** (`Frozen scientific start changed`); frozen inputs, original evidence hash and 16 focused controls passed. Preserved partial artifact `13545223873`. This is an engineering failure, not a scientific gradient result.
2. Orientation-only fix committed at `b9ff63685aac7ecd10a7cc4d1c33a4dc28699a62`, with no change to source indices, free parameters, gradient algorithm, thresholds or scientific protocol.
3. [42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614) at **`b9ff63685aac7ecd10a7cc4d1c33a4dc28699a62`**: **SUCCESS**. All 16 focused positive/negative source-integrity tests, frozen source SHA checks, original full-fitting failure check, all **50/50 real private MATLAB objective/Ridders probes**, original optimizer delegation and native-vs-instrumented **28-field strict binary64 neutral control** succeeded. The complete paired original MATLAB/HGFX 50-row gradient and BFGS margin report was produced. No performance timer.

[Full immutable artifact 13546219957](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614/artifacts/13546219957); downloaded archive ZIP SHA-256 `9d7c9ee3b5e25ce713319f071a2ee95a8e59e83eca7b6faa37f6cd39172f0d39`. The following three raw SHA-256 hashes were checked independently against the archived `provenance.json`:

| Artifact member | SHA-256 |
|---|---|
| `locked-50-bfgs-anchors.json` | `d92690111b2fa128c045f29b39aa95110b5e5cd838f90c48a733400a3e537913` |
| `real-private-matlab-ridders.json` | `90de6c75c13736fae95bc0645950ac0352546fd7262c4d5f70d97f8b9b14e978` |
| `paired-direct-private-gradient-bfgs-margins.json` | `2ff7dddac3892f1f7a6b7a78b20e5839315badebce60fd2d81c8847a3d4e2d2d` |

## Direct same-x scalar and Ridders-gradient evidence

The MATLAB callback received the actual private nested `fitModel` objective, evaluated `obj(x)` and frozen reference `riddersgradient(obj,x,struct('min_steps',10))` at **all 50 original occurrence coordinates**, and delegated exactly once to the unchanged reference optimizer. Original MATLAB `isequaln` plus a separate Python strict binary64 comparison confirmed all **28 native/instrumented public output fields exactly equal**, with zero changed fields.

| Observed quantity | Exact diagnostic |
|---|---:|
| Prespecified / evaluated direct-private MATLAB gradient occurrences | **50 / 50** |
| Exact scalar HGFX-vs-real-MATLAB objective pairs | **41 / 50** |
| Nonzero scalar objective pairs by original occurrence | **9 / 50** |
| Objective ULP-distance distribution | **41 × 0, 8 × 1, 1 × 2** |
| Maximum same-x scalar objective absolute difference | **2.842170943040401e-14** |
| Maximum same-x absolute Ridders gradient component difference | **6.884955006114524e-08** |
| 25 HGFX-own history anchors: largest gradient component discrepancy | **6.884955006114524e-08** at original slot **6** |
| 25 MATLAB-own history anchors: largest gradient component discrepancy | **2.4016344468691386e-11** at original slot **2** |
| MATLAB private direct scalar vs stored original HGFX-own `iter.val` | **1/25 nonzero**, magnitude `1.4210854715202004e-14` |
| MATLAB private direct scalar vs stored original MATLAB-own `iter.val` | **0/25 nonzero** |
| MATLAB native vs instrumented 28 public fit fields | **28/28 strictly identical** |

**Scientific counterexample retained:** Original HGFX-own record **6** has `x=[-1.1621811570388512,-6.37816839506084,-0.23738383160834042]`, and the actual private MATLAB objective equals HGFX **exactly at that x** (`108.28848680066957`). Yet the first Ridders gradient component is **5.046862798072859 (HGFX)** against **5.046862866922409 (MATLAB)**, absolute difference **6.884955006114524e-08**. The respective internal Ridders reported errors for that component are `8.881784197001252e-16` and `2.6645352591003757e-15`, which do **not** bound the cross-implementation discrepancy. This result is a numerical/method diagnostic, **not** proof of an incorrect derivative or the cause of the original full-fit mismatch. No originally specified gradient acceptance tolerance exists.

At the *different* MATLAB-own original record 6 x=`[-1.1621811570747047,-6.378168395057576,-0.23738383159660303]`, the same-x absolute max Ridders component discrepancy is only `1.7212897773788427e-12`. These must never be falsely treated as same coordinates. Original optimizer histories are identical at record 0, diverge by up to `9.769962616701378e-15` at record 1, `3.5853542357244805e-11` at record 6, `1.964719109626145e-09` at record 7, and `3.7255962581639324e-07` at record 22 (max absolute parameter component). Correlation or coincidence in history order is not causal attribution.

## BFGS, Armijo and stopping margins: descriptive original-source reconstructions

The archived actual original public BFGS matrices and history vectors were reused, with the new **same-x direct-private MATLAB** and **same-x frozen HGFX** gradients. These records are calculations of source-formula conditions, **not a log of internal private optimizer branch executions**:

| Original source-formula diagnostic | HGFX-own original history | MATLAB-own original history |
|---|---:|---:|
| Curvature-safe slots 1..22 with reconstructed BFGS update | 21/22 | 21/22 |
| Curvature-safe slots 1..22 without update | record 11 | record 11 |
| Curvature inferred condition agrees with saved inverse-Hessian change | **22/22** | **22/22** |
| Transitions 0..21 satisfying reconstructed Armijo inequality | **22/22** | **22/22** |
| Transitions 0..21 compatible with full step (residual <1e-11) | **22/22** | **22/22** |
| Source direction clipping for these 22 transitions | 11 yes / 11 no | 11 yes / 11 no |
| Retrospective grad-stop test true among 25 stored records | only records 23 and 24 | only records 23 and 24 |
| Smallest positive Armijo RHS-minus-LHS margin | `0.012318560487808555` (transition 21) | `0.012318573518023783` (transition 21) |
| Closest positive curvature lhs-minus-rhs margin | `0.007268377561782211` (slot 10) | `0.007268379426284031` (slot 10) |
| Negative curvature margin at skipped update | `-0.046077708610690445` (slot 11) | `-0.04607771446586489` (slot 11) |
| Final retrospective gradient convergence score (tolerance `1e-3`) | `0.0002267376638137286` | `0.000226736901805916` |

The original terminal records 22..23 are ambiguous/overwritten in the source buffers and are **excluded from accepted-step branch assertions**, even though all 25 gradient-stop scores are preserved. The small same-x gradient differences do **not** show a reconstructed curvature or Armijo Boolean branch flip on the prespecified safe slots. Original MATLAB source `quasinewton_optim.m` uses `tolGrad=1e-3` and `riddersgradient` with `min_steps=10`, without any scientific policy alteration.

The CI run logs also contain NumPy overflow/invalid-operation `RuntimeWarning` messages within the frozen HGFX Ridders extrapolation implementation; all 50 returned comparison gradients/errors were finite and recorded. The warnings must not be retrospectively suppressed or interpreted as proof of scientific reliability.

## Interpretation and independent-review handoff

**Established:** the actual private frozen MATLAB nested objective and frozen HGFX compare closely at these fixed original optimizer anchor coordinates; all 50 real reference gradients are present; the reference wrapper does not alter its public fit; the observed single gradient counterexample and original BFGS margins are traceable to immutable raw evidence.

**Not established:** equality of gradients at all stencil perturbations; exact parity of internal Ridders selection history; absence of small-step numerical/BLAS sensitivities; direct BFGS decision-branch event parity; cause of original trialwise 4+4 failure; global or scientific identifiability parity; eligible benchmark workloads; performance speedup; independent scientific PASS.

The next scientific investigation, explicitly **post-result exploratory and not prespecified as an acceptance gate**, is to inspect the actual `x±h` Ridders stencil objective evaluations and Richardson selection decisions at HGFX-own original record 6, compare exactly the same perturbations on the MATLAB private nested and HGFX `evaluate_free` objectives, then classify whether the `6.884955e-08` discrepancy comes from objective rounding, Ridders selection, platform differences or insufficient evidence. Preserve negative findings and full original evidence. Record any new investigation protocol **before** collecting its fresh values and identify the original counterexample as selected from observed results.

Issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) still requires independent reviewer identity, frozen SHA and raw-hash verification, source-level scope/method verdict and signed acceptance/disposition. **No scientific PASS, tolerance changes, PERF-01C freeze, timings, GPU or speedup claims** until independent decision.
