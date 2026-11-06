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
