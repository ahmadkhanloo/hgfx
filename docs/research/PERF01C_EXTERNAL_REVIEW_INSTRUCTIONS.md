# PERF-01C — Independent scientific reviewer instructions (bounded)

**This task must be performed by someone independent of the PERF-01 implementation.** This file is a handoff, **not an implementation-side sign-off**. Tracking: [issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88).

## Objective

Decide whether the prospective **new, narrow** MATLAB 8.2.0 vs HGFX 1.0.0 CPU benchmark may be frozen **before any timing**, without retroactively repairing or hiding the failed original nine-case primary design. Review the scientific and measurement contract, not whether one tool is faster. An independent reviewer may conclude `BLOCK_FREEZE` for any unsupported claim.

## Checkout / commit identity

Using a local clone with appropriate GitHub access:

```bash
git clone https://github.com/ahmadkhanloo/hgfx.git hgfx-perf-review
cd hgfx-perf-review
git fetch origin pull/87/head:refs/remotes/origin/perf01-pr87
git checkout --detach refs/remotes/origin/perf01-pr87
git rev-parse HEAD
git show -s --format='%H %an <%ae> %ai' HEAD
```

Record the **actual full reviewed commit SHA**, rather than an assumed current head. If the PR advances after checkout, do not claim to have reviewed those later commits without repeating the relevant diff audit. Compare current base `main` SHA to the review commit and record both.

## Exact scientific evidence to inspect

- Prospective original protocol: `docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V1.md`.
- Separate unapproved, potentially scoped successor: `docs/research/RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md`.
- Diagnostic evidence: `docs/research/PERF01D_DIAGNOSTIC_EVIDENCE_2026-11-04.md`, `docs/research/PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md`.
- Original immutable inputs, priors/start snapshots and manifests under `benchmarks/runtime_v1/inputs/`, `configs/`, `inputs_manifest.json`, `resolved_configs_manifest.json`.
- First-subject full trajectory/likelihood: `trialwise_results/summary-41854644533.json` with [Actions run 41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533).
- Full single-subject fit: `fitting_results/summary-41855647245.json` with [Actions run 41855647245](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855647245).
- All 64 subjects × three models × three trial lengths: `cohort_results/summary-41860187774.json` with [Actions run 41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774).
- Complete original-case ledger: `eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json`.
- Additional prospective whole-cohort **complete** 128-trial fit probe: `benchmarks/runtime_v1/fit_cohort_hgfx.py`, `matlab/fit_cohort_matlab.m`, `compare_fit_cohort.py`; record its own run and outcome only **if actually completed and verified**. No conjectural promotion from queued CI.

MATLAB reference MUST be HGF Toolbox 8.2.0 commit `2437f4dc241541072722a2695ddeca7b44d83dd3` and product MUST be HGFX `v1.0.0` `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Never use current `main` package instead. Check the actual MATLAB function-resolution paths.

## Eight decisions (bounded scope)

1. **Identity:** confirm both SHA identities, MATLAB toolbox resolution and installed HGFX 1.0.0 from real recorded CI logs.
2. **All rows and hashes:** independently check original 28-case ledger, all 576 subject statuses (448 finite compatible, 128 invalid in both), SHA-256 of source inputs/configs/raw reference artifacts. Reject a missing or silently excluded row.
3. **Correctness:** recompute selected *raw* trialwise/likelihood difference and nonfinite masking; verify 7 valid trajectories and three first-invalid-prefix lengths (348 regular HGF512, 346 HGF1024, 349 masked HGF512). Never infer full scientific identifiability from objective agreement.
4. **Fitting:** check entire public `fitModel` versus `fit_model` 128-trial output (final, H, Sigma, Corr, trial likelihood, LME, AIC, BIC, predictions/residuals and optimizer termination/iteration). Treat default-start recovery and MATLAB implicit resampling as a potentially **material workflow difference**, not a free compatibility match.
5. **Denominator:** independently verify 16 prospective good/review-pending versus 12 blocked among the original 28 predeclared workloads, and that **six out of the nine original primary CPU workloads are ineligible**. Original headline must not pass.
6. **Clock boundary:** confirm matched scientific work for forward, objective and complete fit. MATLAB `negLogJoint` is nested/private, and MATLAB `fitModel` unconditionally prints results; select a defensible prospective stdout policy, not an ex-post faster option.
7. **Hardware/statistics:** confirm explicit same physical CPU core/thread/affinity policies, paired order, warmups, sample counts and 10,000-resample CI with v1 unchanged 1.10 threshold. No fake precision or silently discarded noisy block; JAX compilation and real physical GPU evidence separate.
8. **Decision:** advise whether `RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md` can be frozen *after* its runner/host contract is completed, or issue specific remaining fixes. Do not claim GPU validation from CPU.

## Mandatory reviewer output

Commit to an **independent** review branch or post a signed, specific GitHub PR review / issue #88 comment including:

- reviewed SHA and base SHA, own identity and independence declaration;
- exact artifact IDs and SHA-256 values that were directly verified;
- discrepancy table with severity, source path/line, reproduction command and supported classification;
- every predeclared blocked/unsupported cell;
- explicit decision `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE`, with concrete checklist of remaining blockers;
- separate scientific/measurement interpretation from engineering execution success.

**Current default: `BLOCK_FREEZE / REVIEW NOT YET DONE`.** Neither this prompt, a green CI, nor author-side static audit constitutes the independent approval. A new immutable, reviewed protocol lock must exist before any paper-use timing.


## New author-side six-source raw evidence replay (2026-11-06)

A reproducible CI check was added to reduce the *mechanical* work needed by an independent reviewer; it does **not** constitute independent scientific review.

- [Executed run 42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894): 47/47 author-side regression tests, six original archived input runs, eleven raw JSON files SHA-256-verified, all original comparators reconstructed, and both 28-case ledgers unchanged.
- Exact **tested commit**: 1dd22bc5eef4502136e6b61a586d2129be951a8d. For any later PR head, explicitly check the intervening diff before claiming coverage.
- Machine-readable replay artifact: perf01-evidence-regression-42108194894, under the run's artifacts.
- [Complete bounded provenance and unchanged failing outcome](PERF01C_SIX_SOURCE_EVIDENCE_REPLAY_2026-11-06.md).
- Entry point: benchmarks/runtime_v1/verify_evidence_regression.py. Original artifacts include run IDs 41854644533, 41855647245, 41860187774, 41863441006, 41868723514 and 41870479069.
- The MATLAB-only reference probe is independently checked against the exact original fitted MATLAB raw endpoint, the baseline zero shift, **all six** +/-eps probes, math.ulp(start), and the preexisting 3e-8 relative / 3e-10 absolute final-parameter tolerance. The original free-coordinate-2 negative-step numerical mismatch and 63/64 fitting outcome remain **failures**.
- Independently assess model/source paths, MATLAB optimizer convergence/termination, numerical basin/classification and the *prospective* clock/hardware contract. Do not treat a comparator replay or this document as an external reviewer signature.

**Review verdict remains unset: BLOCK_FREEZE / REVIEW NOT YET DONE, with PERF-01C OPEN and no performance timing.**


## Original subject-7 BFGS branch audit, additional review material (2026-11-06)

The newest *author-side* diagnostic has a fully preserved, source-anchored evidence chain: [real MATLAB/HGFX BFGS run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), [rederived immutable mathematical branch report 42188247052](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052), and [numeric report](PERF01D_SUBJECT7_BFGS_BRANCH_2026-11-06.md). Two raw SHA-256-checked BFGS exports hold each engine's 101-slot history, 25 finite objective/gradient states, 24 inverse-Hessian matrices and all reset indices. The source-derived record-1 first matrix difference, record-10 ~183.57× matrix norm change, 22 curvature decisions, 22 reconstructable candidate full steps and terminal history overwrite must all be reviewed **as diagnostics**. No hidden/altered original 63/64 fitting result or 28-case prefreeze ledger is permitted.

**Additional mandatory external-review distinction:** same candidate reconstructed step/Armijo and BFGS curvature branch does *not* prove the exact internal acceptance event log, equality of optimizer floating-point accumulation, precise MATLAB termination reason, or a permissible reference limitation. Evaluate source code and identify if more evidence is needed; do not upgrade the release gate based on green author-side CI. The original subject-7 scientific mismatch remains a recorded non-PASS, and independent `APPROVE_PROSPECTIVE_FREEZE`/`BLOCK_FREEZE` judgement is still absent.


## PERF-01D Issue #90 numerical environment reproduction evidence (2026-11-06)

Two additional *author-side* original-source diagnostics now have source-checked CI and new machine-readable evidence: [OpenBLAS same-runner scalar audit 42197971370](https://github.com/ahmadkhanloo/hgfx/actions/runs/42197971370) and [untimed real full HGFX public fitting under two OpenBLAS cores 42199013326](https://github.com/ahmadkhanloo/hgfx/actions/runs/42199013326). Review the paired reports [controlled scalar ULP isolation](PERF01D_ISSUE90_OPENBLAS_SAME_HOST_2026-11-06.md) and [full frozen fitting sensitivity](PERF01D_ISSUE90_FULL_FIT_DISPATCH_2026-11-06.md), including checksummed original model/data/source and preserved failed workflow attempts. On one hardware runner, BLAS dispatch changes both post-hoc scalar bits and actual HGFX optimizer states; **this is not evidence of a satisfactory MATLAB-versus-HGFX scientific trajectory match**. Crucially, MATLAB was not rerun on that runner, and both modes' entire `traj.mu`/`traj.muhat` acceptance results were not evaluated. No implicit reference-limitation ruling, scientific gate PASS, accepted protocol change or benchmark timing authorization follows from this evidence. Original **63/64** fitting non-PASS and [independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88) remain blocking; cross-host diagnostic repeatability [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) remains separately OPEN.


## Reviewer source cross-over for fitting versus forward identifiability (2026-11-06)

Review [crossed fixed-parameter MATLAB/HGFX source-locked 18/18 test CI 42204633161](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204633161) and [full source/three-vector/11-field detailed report](PERF01D_SUBJECT7_CROSSED_FORWARD_2026-11-06.md). This records exact original subject zero-based 7, original hgf_binary+unitsq_sgm model family, both historical optimizer fitted endpoints and original frozen start, with **the exact same transformed parameter vector evaluated by BOTH original source implementations on the same input**. Forward outputs agree within unchanged 3e-8/3e-10 tolerance for all 11 trajectory fields and inference states at all three points, and each direct forward reproduces its own original actual public `fitModel` trajectory at its archived endpoint. This is independent of optimization in the new experiment.

Do NOT confuse that author-side **fixed-vector forward implementation concordance** with original **full-fitting scientific parity** (still 63/64 NON-PASS), with any external/reference-limitation classification, or with three points representing the whole parameter domain. The reviewer must still resolve numerical optimizer-endpoint equivalence/acceptable reference-limitation policy and sign the *prospective* PERF-01C eligibility lock; neither changed BLAS kernels nor post hoc tolerance adjustment may be used to claim PASS. Timing and physical GPU claims remain not authorized.


## 2026-11-06 — original two-perceptual-parameter crossed-forward attribution handoff

Please independently examine [the full 2×2 immutable original omega2/omega3 counterfactual evidence](PERF01D_SUBJECT7_OMEGA_COUNTERFACTUAL_2026-11-06.md), [successful MATLAB+HGFX CI 42213683575](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213683575), and source-verified complete derived data [derived-omega-counterfactual-42213683575.json](../../benchmarks/runtime_v1/issue90_results/derived-omega-counterfactual-42213683575.json). The predeclared four exact original 15-vector combinations are based only on the original two fitted perceptual omega coordinates 12 and 13 from the original failed 64-subject public fits. Both engines' forward trajectories and 11/11 original fields agree at all four identical vectors within original numerical tolerances; original mu/muhat failed points have signed delta overwhelmingly from the difference in original **fitted omega2** rather than source-forward code. **That does not establish why the frozen full optimizer generated a different omega2 or certify scientific fitting compatibility**, nor can one reinterpret an original fit as acceptable merely because exact-vector forward parity is established. The original **63/64 fitting non-PASS, 28-case denominator, pending independent review and NOT FROZEN PERF-01C** must remain unchanged. Reviewer must issue their own explicit verdict tied to original SHA/source evidence; no speed claim before prospective protocol lock.


## Independent adjudication handoff: why fit parameters can be within tolerance but trialwise trajectory fails (2026-11-06)

Read [the 2x2 source-matched omega forward counterfactual](PERF01D_SUBJECT7_OMEGA_COUNTERFACTUAL_2026-11-06.md) jointly with [original 25-slot omega2 optimizer chronology](PERF01D_SUBJECT7_OMEGA2_HISTORY_2026-11-06.md), including [source-locked CI 42213683575](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213683575) (23/23 tests) and [CI 42214972548](https://github.com/ahmadkhanloo/hgfx/actions/runs/42214972548) (27/27 tests). The original exact full-fitting omega2 endpoint differs by about **1.89e-8**, **within** the original inherited final parameter bound around **2.47e-7**, while four original near-zero fitted mu and four muhat trialwise points **exceed** their distinct original absolute/relative tolerance. Source-matched direct HGF forward shows that this same original fitted omega2 difference explains the dominant signed part of those trialwise deltas under original fixed-endpoint counterfactual algebra, **not** that the original full fitting has achieved parity.

External reviewer must keep the **63/64 subject-level non-PASS**, no post-hoc exclusions/seeds/tolerance/BLAS swaps, and must examine the original optimizer output parity independently before any scientific reference-limitation ruling. The original 25-slot trace is POST-FIT reconstructed (not an instrumented termination record); last two transitions are not interpretable as accepted steps. PERF-01C remains OPEN / NOT FROZEN; no CPU or GPU runtime claim.


## 2026-11-06 — independent evaluation of actual unmodified-source stopping reason

Read [CI 42232378487](https://github.com/ahmadkhanloo/hgfx/actions/runs/42232378487) and [source-native MATLAB/HGFX termination report](PERF01D_SUBJECT7_NATIVE_TERMINATION_2026-11-06.md), including independently SHA-verified full raw normal/verbose MATLAB fits, original complete subject7 fitting and original HGFX direct source optimiser replay. Original MATLAB fitModel has no separate termination string in its public structure, but original unmodified frozen quasinewton_optim prints **Converged on gradient size** when original **verbose** option is enabled. The new CI verifies that **ONLY logging changed** (all normal-vs-verbose original numeric full fit output and trajectory fields exactly equal). Frozen HGFX public and direct source optimizer exactly match their full iteration history, and native stop is also **tol_grad**, 24 iterations/zero resets. This is bounded source-native diagnostic evidence, NOT proof of identical floating-point gradients/steps, accepted scientific fitted trialwise trajectories, or MATLAB-only reference limitation. Original scientific complete fitting **63/64 NON-PASS**, all original cases intact, PERF-01C still NOT FROZEN; independent reviewer must explicitly adjudicate the frozen full-original scientific gate before future runtime timing.


## 2026-11-06 — review source-native gradient margin and bitwise run portability separately

[Source-locked SHA256 replay **42244053396**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42244053396) (42/42 tests) and [PERF01D_SUBJECT7_GRADSTOP_REPEATABILITY_2026-11-06.md](PERF01D_SUBJECT7_GRADSTOP_REPEATABILITY_2026-11-06.md) distinguish three independent questions: (1) Original MATLAB and HGFX source-native criterion is **tol_grad**; after original full fitting, **post-fit** recalculated scaled gradient metric is ~`2.267e-4` in both, against frozen `1e-3`, with Ridders *heuristic* scaled uncertainty ~`9e-14`. This is not an independent truth bound or in-loop event log. (2) Two separate frozen-HGFX CI runs drift bitwise from optimizer record2 despite equal source/stopping criterion, while both 11-field HGF trajectories agree with each other under old tolerances; two MATLAB source raw SHA256 happen to be identical. No matched CPU/BLAS mechanism proof. (3) Both HGFX runs still fail the original **four `mu` and four `muhat` cells** against MATLAB; original complete fitting outcome **63/64 NON-PASS**, not automatically reclassified. Review the already frozen reference limitation policy and source optimization semantics; do not infer original scientific passing from a shared stop type, pointwise gradient margin, or repeatability under a different scientific criterion. **No PERF-01C prospective benchmark freeze until an external reviewer signs the whole original 28-case policy and acceptable scientific eligibility**, no CPU/GPU performance claims.


## 2026-11-06 — numeric-margin audit to distinguish severity from acceptance

[Original-tolerance subject-7 exceedance report](PERF01D_SUBJECT7_ORIGINAL_TOLERANCE_MARGINS_2026-11-06.md): [Actions 42266125766](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766), tested source SHA `ef26ddc9e9efeca31cf9f8dc2cd8ae91ccb1b788`, **14/14 tests**, machine artifact [13526892782](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766/artifacts/13526892782). Recomputed old `atol=3e-10 / rtol=3e-8` numerical bounds for **every original failed** `mu/muhat` cell without changing criterion or raw evidence. Against *historical different-host MATLAB*, both SkylakeX repeated fits have **4+4** failed cells (max `mu` exceedance 1.66198× old bound); both Haswell fits **14+14** (max 3.66090×); all four same-host cross-dispatch comparisons **4+4** (max 1.99892×). Exactly one-trial `mu`→`muhat` lag in every failed list. These are descriptive old-gate failure severity diagnostics, **not independent approval or a license to pick the more matching kernel post hoc**. The earlier test-expectation failure [42266034562](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266034562) is retained.

**Binding acceptance and scientific status:** exact frozen original full public fit **63/64 SCIENTIFIC NONPASS**, 28 original cases 16 review-pending/12 blocked, independent #88 NOT RECEIVED, PERF-01C NOT FROZEN, no MATLAB-vs-HGFX benchmark timing or speed claim.


## 2026-11-06 — newly executed SAME-RUNNER frozen MATLAB/HGFX subject-7 evidence

The [prespecified same-runner scientific experiment](PERF01D_SUBJECT7_MATCHED_RUNNER_PRESPEC_2026-11-06.md), followed by the [source-verified complete outcome](PERF01D_SUBJECT7_MATCHED_RUNNER_RESULTS_2026-11-06.md), has now run **four full frozen HGFX public fits and two full frozen MATLAB HGF Toolbox 8.2.0 fits on the same GitHub Actions host**. Source-run [42268256755](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268256755) produced all six original raw fits but **failed its post-fit hash-key parser**; artifact 13528955307 and its ZIP SHA-256 are preserved. Another source attempt [42268506282](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268506282) **failed SIGILL (unsupported CPU instruction) before MATLAB**, retained without choosing a different BLAS mode. SHA-pinned derived-only [42268990557](https://github.com/ahmadkhanloo/hgfx/actions/runs/42268990557) replayed the original six real-fit source files, **43/43 tests PASS**, eight/8 complete original 28-field paired comparisons, full report SHA-256 recorded, and compact [machine result](../../benchmarks/runtime_v1/issue90_results/summary-matched-runner-42268990557.json) committed.

**New narrower scientific evidence:** both MATLAB reruns reproduce each other bitwise for all original 28 output fields and the 101×3 optimizer-state history; two repetitions of each HGFX OpenBLAS mode are also within-mode bitwise identical. Yet all **four HGFX SkylakeX vs MATLAB pairs retain 4 `traj.mu` + 4 `traj.muhat` failures**, and all **four Haswell vs MATLAB pairs retain 5 `traj.epsi`, 14 `traj.mu`, 14 `traj.muhat`, and 40 `traj.psi` failing cells**, under **unchanged original acceptance thresholds**. The original cross-host MATLAB ambiguity is no longer a sufficient *sole* explanation for these particular same-runner mismatches. However MATLAB ran with `maxNumCompThreads=1`, HGFX OpenBLAS with four threads and explicit four-core affinity, and library kernels may differ; **not a matched CPU timing contract**. No new reference limitation, optimizer scientific equivalence or performance PASS may be asserted by the implementer.

**Mandatory independent assessment:** original full 64-subject fitting still **63/64 SCIENTIFIC NONPASS**; 16 originally specified cases review-pending, 12 blocked, six original primary CPU cells ineligible, **PERF-01C OPEN/NOT FROZEN**, no benchmark timing, no GPU/speed claim. External reviewer must examine all eight new 28-field outcomes and frozen source optimizer semantics before any new protocol eligibility verdict. This addendum is NOT the sign-off.


## 2026-11-06 — post-hoc local Hessian / Laplace-scale interpretation (NOT acceptance)

A separate [author-side post-hoc audit](PERF01D_SUBJECT7_LAPLACE_SCALE_2026-11-06.md) was executed using ONLY the same six frozen public fitting source outputs and eight old-tolerance 28-field comparisons from the successful same-runner audit. [GitHub Actions 42282108311](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282108311), source SHA `fa6dcc0e77b244f483482b7ef8e01429d6884c4c`, **24/24 focused tests + 3 negative end-to-end original-source integrity controls**, machine [artifact 13536250592](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282108311/artifacts/13536250592), derived report SHA-256 `4ead097fe2958229176cdb3c610a02dd1b8746ca3b338e3c87bac3624b45c889`. Compact [machine provenance/scale summary](../../benchmarks/runtime_v1/issue90_results/summary-subject7-laplace-scale-42282108311.json).

Original exported MATLAB local 3×3 fitted Hessian H has **positive eigenvalues ~[0.0625, 0.3830, 6.5505], condition number ~104.8**; similarly positive H/Sigma were recorded by all four original HGFX fits. Three-free-parameter endpoint Euclidean separations from the two exact repeat MATLAB public outputs are ~3.786×10⁻⁸ under SkylakeX, ~8.364×10⁻⁸ under Haswell, or **1.602×10⁻⁸ / 3.532×10⁻⁸ on conditional local MATLAB Hessian quadratic distance**. These *fitted local conditional covariance-scale calculations* are **post hoc descriptions, not validated scientific identifiability or confidence/acceptance criteria**. They demonstrate small transformed-parameter displacements on this local matrix scale, yet **all eight** frozen MATLAB/HGFX full-fit pairings STILL FAIL original strict trajectory fields. No optimizer/trajectory tolerance was relaxed, no additional model fitting or timing occurred and no automatic reference-limitation classification is justified.

**External reviewer must still adjudicate** the exact mismatch and protocol; the original **63/64 NONPASS**, 28-case **16 review pending/12 blocked**, original ineligible six primary cells, PERF-01C **NOT FROZEN**, performance **NOT RUN**, no GPU/timed speedup all remain unchanged.


## Independent review addendum — exact actual-private gradient, Ridders stencil, and post-result interposition (2026-11-07)

**This is additional author-side evidence only. Neither the author nor a green workflow provides the independent verdict. Original 63/64 full public fits remain SCIENTIFIC NONPASS; PERF-01C NOT FROZEN.**

New, SHA-locked results to include in the independent scientific assessment:

1. [Direct private nested MATLAB objective/Ridders 50-anchored original-history experiment](PERF01D_DIRECT_NESTED_GRADIENT_BFGS_RESULTS_2026-11-07.md): pre-result protocol commit `0ed460572d5323ba6e1c1f562955755eea7a29d7`, complete [run 42305573614](https://github.com/ahmadkhanloo/hgfx/actions/runs/42305573614) @ `b9ff63685aac7ecd10a7cc4d1c33a4dc28699a62` artifact 13546219957 (ZIP SHA-256 `9d7c9ee3b5e25ce713319f071a2ee95a8e59e83eca7b6faa37f6cd39172f0d39`). All 25 HGFX-own plus 25 MATLAB-own original x preserved, 50 actual private MATLAB Ridders gradients, strict 28/28 native/instrumented public-fit equality. Objective values at same x match exactly 41/50, other nine within 1–2 ULP, but the largest component-gradient discrepancy is `6.884955006114524e-08` at HGFX-own source record 6. These are **not** original fitting parity gates.
2. [Actual frozen MATLAB private Ridders objective-call trace and source-Richardson result](PERF01D_RIDDERS_STENCIL_ANOMALY_RESULTS_2026-11-07.md): **one target deliberately selected after seeing the 50 results**, with post-result exploratory method committed at `e1c3e2e83045896195701926a5f94fa361b0f091` before fresh values. [Trace run 42361286407](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361286407) artifact 13569423003 ZIP SHA-256 `fc8068b3d0fe5d6bfacc4ace54c00ee4adca29be0fea1c6ac7dd4c12a6eb6e4e`: 245 actual objective calls at exact same binary64 coordinates, 33 objective differences of 1–2 ULP; MATLAB native 28/28 scientific fields unchanged. First x+h step for component zero returns original MATLAB/HGFX finite `realmax`, and both first-coordinate Ridders runs exhaust 100 source levels. [Original frozen-source Richardson replay 42361769881](https://github.com/ahmadkhanloo/hgfx/actions/runs/42361769881), artifact 13569229297 ZIP SHA-256 `1e66252097e525f868493ac23633152e3a5d5edeb1da91dde84d0abf1cfb67b8`, reproduces all six source gradients/errors at exact binary64; selected row 80 HGFX vs 87 MATLAB. The replay is **not** directly logged internal MATLAB branch events and **not** proof that this difference caused the original 4+4 trialwise trajectory failure.
3. [New eight-arm, exact-source-anchor counterfactual protocol](PERF01D_ORIGINAL_GRADIENT_INTERPOSITION_EXPLORATORY_PROTOCOL_2026-11-07.md) committed *before new intervention results* at `7049b23a6acf118038149a1bbbb31cb5d40da45f`. [Workflow](https://github.com/ahmadkhanloo/hgfx/actions/workflows/perf01-subject7-gradient-interposition.yml) compares original unmodified frozen HGFX optimizer with temporary **diagnostic** source-gradient substitutions from original real private MATLAB only at exact binary64 original anchors, and records never-hit sites separately. Such arm results are **NOT** original frozen HGFX fits and can never independently satisfy scientific or benchmark gates. Verify exact workflow run/SHA if executed; do not report unverified outcomes.

Independent reviewer must retrieve original raw artifact files, verify the three locked SHA-256 members in each archived run and all 50 original anchor positions, check original toolbox `core/fitModel.m`, `utilities/riddersgradient.m`, `utilities/riddersdiff.m` and `core/quasinewton_optim.m`, and independently distinguish these:

- Scalar objective implementation agreement at saved vectors vs off-base perturbation agreement; Ridders's internal error estimate is **not** a bound on cross-engine differences.
- Source-formula curvature/Armijo retrospective condition agreement vs **actual internally observed optimizer branching**; no branch-event-level oracle was recorded by the 22-step reconstructions.
- The observed numerical derivative-selection mechanism vs a causally demonstrated explanation for the final public-fit trialwise mismatch; do not classify a MATLAB/reference scientific limitation without independent reference evidence.
- Post-result one-vector exploratory selection and any gradient-interposition perturbation vs the 50-point preregistered diagnostic and original 64-fit acceptance denominator.

Mandatory independent reviewer disposition remains `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE` with identity, reviewed exact PR SHA, original and new raw artifacts verified, scoped limitations and reference-evidence-based scientific rationale. **Default still BLOCK_FREEZE / NO INDEPENDENT REVIEW**, with no paper-speed timer, GPU claim, passing 64/64 fit or changed eligibility.


### Completed follow-up to item 3: exact-bit gradient interposition, all eight arms (2026-11-07)

[Exact eight-arm result](PERF01D_ORIGINAL_GRADIENT_INTERPOSITION_RESULTS_2026-11-07.md), authored at commit `bf85cfda415f88d38f1a186cdbdbf4606d391eaf`: [workflow 42366198103](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366198103), tested source SHA `8a70d1cad64d03b664cbf735079f63d1dfc5b444`, **14/14** engineering controls, eight/eight complete, raw artifact 13571871384 ZIP SHA-256 `4fd318f66d97792738874a0d35c65db90bc5d7c72df151489d76b8c50facd6b2`, eight-arm JSON SHA-256 `8a478e7ace9c85c5185c26980b4f4a6a3f7226c2cba2561f77809a8c6588416e`. Exact frozen product source was not changed; diagnostic arms explicitly substituted archived MATLAB real-private gradients at **bitwise-identical original x only**.

- New-host frozen HGFX baseline does **not** reproduce its own archived old BFGS `iter.x` bitwise: first mismatch at record **2**, terminal difference `1.4572520967703895e-10`. Thus the maximal-gradient-discrepancy historical original record **6 is NOT REACHED EXACTLY**, and interventions at this point do not occur; do not infer absence of causal effect from unchanged arms.
- Placebo original-HGFX initial gradient matches same-host baseline exactly. Replacing only initial gradient component zero by the real MATLAB private gradient reduces transformed-parameter max distance to the original MATLAB endpoint from `3.277081539465598e-08` to `3.3157530054950257e-09`; replacing all three initial components instead increases distance to `2.2791900811114374e-07`. A deliberate gradient change can thus shift BFGS endpoints either direction. These are **optimizer numerical sensitivity**, **not original full public fit**, and **not proof that the original 4+4 trajectory failure has been explained**.
- Three failed earlier diagnostic workflows [42366055097](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366055097), [42366146173](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366146173), [42366148737](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366148737) were synthetic/engineering fixture failures before intervention and remain preserved in Actions.

Independent reviewer #88 must separately review the source-locked original 63/64 scientific failed cohort, the non-bitwise same-host baseline, strict exact-anchor no-hit condition and original-vs-intervened distinction. No `APPROVE_PROSPECTIVE_FREEZE` verdict or runtime/GPU/tolerance relaxation follows.


### Post-result original BFGS x6/T6 *single-step* sensitivity, source-based reconstruction (2026-11-07)

Additional author-side [same-state single-step report](PERF01D_SUBJECT7_SAME_STATE_BFGS_ONE_STEP_RESULTS_2026-11-07.md) committed `007d6cba5f815e7137bd45eec6d2e32985022ad1`; [Actions 42366705874](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874) SUCCESS, tested SHA `9e4bffaba040e2f66b8b3d985053a6b2a353b4a5`, **10/10** source-formula synthetic controls. [Artifact 13572445302](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874/artifacts/13572445302) ZIP SHA-256 `654667abec22c7b59e00bbf19ee5db2308414cdff398e4ca1409eeb6c376109c`, single-step raw JSON SHA-256 `b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144`.

For the **same actual original saved HGFX BFGS x6 and inverse-Hessian T6**, original source clipped-step algebra with frozen HGFX Ridders versus real frozen MATLAB private Ridders **at precisely that original HGFX x6** moves the hypothetical full-step candidate by `1.0444791836983214e-08`. Both candidate objective values on frozen HGFX satisfy original source Armijo and the original HGFX-source candidate matches its preserved x7 within `5.329070518200751e-15`. The original HGFX-versus-MATLAB **different-source-state** x7 difference `1.964719109626145e-09` is a separate contrast; this single-step result is **not** an internal MATLAB accepted-step trace or a causal reproduction of full fit divergence. The target was selected after original source observations, and a preliminary calculation occurred before this source script: it must NOT be called a preregistered scientific validation result.

Reviewer #88 must not infer original trialwise 4+4-failure resolution or scientific reference limitation from this same-state numerical exercise. Original **63/64 NONPASS**, original 28 benchmark candidates, no independent verdict and PERF-01C **NOT FROZEN** persist.
