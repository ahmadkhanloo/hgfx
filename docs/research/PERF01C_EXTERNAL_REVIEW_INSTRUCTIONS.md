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
