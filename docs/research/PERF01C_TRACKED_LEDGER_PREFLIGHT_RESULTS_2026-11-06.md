# PERF-01C — author-side tracked-evidence preflight, executed 2026-11-06

**Engineering consistency check: SUCCESS. Independent scientific decision: NOT RECEIVED / PERF-01C NOT FROZEN. No new fitting, MATLAB, physical GPU or timing.** This is not an endorsement to benchmark or publish speedup.

## Exact tested execution and status

- [GitHub Actions run 42254625805](https://github.com/ahmadkhanloo/hgfx/actions/runs/42254625805), **SUCCESS**, tested commit **`5ad5fde6c4c541fb84d58f51dfecdaf3727557cf`**.
- **17/17** synthetic positive/negative and unchanged-source ledger checks passed. Artifact: [`perf01c-tracked-ledger-42254625805`, ID 13522430501](https://github.com/ahmadkhanloo/hgfx/actions/runs/42254625805/artifacts/13522430501).
- Source: `benchmarks/runtime_v1/verify_perf01_prefreeze_ledger.py`; unit tests: `tests/test_perf01_prefreeze_ledger_guard.py`; workflow: `.github/workflows/perf01-prefreeze-ledger-guard.yml`.
- Exact output status: **`AUTHOR_SIDE_TRACKED_LEDGER_CONSISTENT_NOT_INDEPENDENT_REVIEW`**. The log/artifact records tested source SHA, evidence-file SHA-256, `NOT_RECEIVED` reviewer verdict and `NOT_FROZEN` protocol.

## Checked tracked derived reports (not re-downloaded raw archives)

| Source | SHA-256 of tracked JSON | Unchanged outcome |
|---|---|---|
| Cohort `summary-41860187774.json` | `65579669c3641e399b286f059f3f662fde7a358044ad8bd9d13f01b852098549` | 576 unique cases, 448 valid-compatible, 128 matching invalid |
| Public full fit `summary-41863441006.json` | `e499ce994efcaf32d33803eb1c563da47dfe72ecb523527e6ef68a1d77f9fcbc` | Original **63/64 NONPASS**; index 7, exactly four failed `traj.mu` and four `traj.muhat` cells |
| Original 28-case inventory `trialwise41854644533_fit41855647245_cohort41860187774.json` | `45c86cac7bb26f643c9e74ba793a2160b6bb3c099eac1ff810555247c91e81e3` | Original 28-case status retained |
| Derived 28-case inventory `candidate_v2_fullfit41863441006.json` | `4fae29055bf33edfde79f4ef2cdb30921b8f9fbf1ff15f45c9d0868cc29fb601` | 16 review pending / 12 blocked; exact 1/1, 15/16, 63/64 additional fitting evidence |
| ABBA `derived-archived-v2-42250539438.json` | `7898bee80dd50a53b2ae9605fdf10d4e9562ef3b45783fb103a822a1ec619730` | 2 same-mode bitwise equal pairs; 4 cross-mode `traj.mu/muhat` original-tolerance failures |

**Prior failed experiments retained and attributed:** the first new guard run [42254199674](https://github.com/ahmadkhanloo/hgfx/actions/runs/42254199674) rejected documented fitting annotations too strictly (checker specification bug, not new scientific mismatch); the next [42254523903](https://github.com/ahmadkhanloo/hgfx/actions/runs/42254523903) had **17/17 tests and evidence checks successful**, but GitHub artifact upload failed because the workflow-generated artifact name had an invalid backslash. Both are historical engineering failures, not a scientific pass or failed model experiment. Fixes retained in commits `f6031e30fcdb090d9e93429207953b7ea3cd7f16` and `5ad5fde6c4c541fb84d58f51dfecdaf3727557cf`.

## Hard limitations / actual next acceptance gate

The completed preflight only verifies *internal consistency of five already tracked JSON summaries*. It **does not independently re-download/recompute the original Actions raw files**, check MATLAB scientific source pathways or prove MATLAB/HGFX fitted-workflow equivalence. Existing separate raw-evidence replay [42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894) and the archived source/oracle review remain separate evidence and reviewer obligations.

**Required from a genuinely independent reviewer:** record identity and exact reviewed commit SHA; verify original raw files and SHA-256 and source scientific semantics; resolve or explicitly block subject-7 optimizer-endpoint mismatch classification; confirm 28-case eligibility and timing/CPU/GPU policy; issue signed `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE` against [Issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88). A new prospectively locked protocol is required before *any* publication timing. Do not treat this engineering check as reviewer signature.

**Binding current state:** original 63/64 scientific full fit **NONPASS**, 28 planned cells **16 pending independent review / 12 blocked**, PERF-01C **OPEN / NOT FROZEN**, issues #88/#89/#90 OPEN, PERF-01E–H NOT RUN, no established MATLAB-vs-HGFX runtime speedup.


## 2026-11-06 — sixth tracked ledger and COMPLETE remote eight-pair source report checked

[Detailed six-ledger / full-artifact results](PERF01C_SIX_LEDGER_AND_FULL_EIGHT_PAIR_PREFLIGHT_2026-11-06.md) supersede the **scope** of the initial five-ledger-only local check, not its historical evidence or test outcome. Successful [Actions 42282680926](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282680926) @ `d0f328061a4b83b2014f6913b4eeb20cd4665d12`, **31/31 tests**; downloadable [artifact 13535289252](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282680926/artifacts/13535289252). The sixth tracked JSON reports **all eight** same-runner frozen MATLAB/HGFX pairs, each **NONPASS** under the original unchanged 28-field fitting criteria. The CI independently downloads the **complete 239,651-byte eight-pair derived report**, verifies full SHA-256 `3c90a24b94921b90e80f1967dfaaaaff821b809d893b5939b5a314ed8635b327`, and cross-checks every paired field/tolerance/failing cell with the original frozen fitting ledger. Both raw-source and derived ZIP artifact digests are checked through GitHub metadata; the raw-source ZIP bytes themselves are **not re-downloaded in this CI**, but were verified in earlier source-archive replay.

First attempted [42282580753](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282580753) FAILED the new synthetic tests because the guard compared plain-hex archive SHA-256 to the prefixed `sha256:<hex>` form from GitHub. Fix `d0f328061a4b83b2014f6913b4eeb20cd4665d12` adjusts only the format comparison without altering the hexadecimal value or historical evidence; the failure is retained.

**Original 63/64 scientific NONPASS, 16 review-pending/12 blocked predeclared cases, no independent verdict/signature, PERF-01C OPEN/NOT FROZEN and PERF-01E–H NOT RUN remain unchanged.** A successful six-report integrity preflight is not independent scientific acceptance or a GPU/CPU speed claim.


## 2026-11-06 extension — six tracked reports and full archived same-runner eight-pair cross-check

The earlier 17-test **five-report** success above remains historical fact. A **separate additive extension**, source commit `a4d2647bc9c8beb76bab75c4007302579d4e5128`, added the sixth tracked same-runner report `benchmarks/runtime_v1/issue90_results/summary-matched-runner-42268990557.json` (SHA-256 `a20f91a15c6114ea9aec2aed574d49af68c1e40be67cb8af29b9c65eafa310f8`) plus 14 more tests. This tracked report still records the two real source-run failures and **all eight mismatched original-tolerance MATLAB/HGFX 28-field comparisons**, not an automatic scientific PASS.

- First extension workflow [42282580753](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282580753) **FAILED**: 31 tests executed, 8 failures + 1 error. The checker compared the 64-character hexadecimal hash stored in tracked JSON with GitHub's `sha256:`-prefixed artifact digest as if the strings had the same representation. The complete scientific evidence was **not** modified.
- Fixes `d0f328061a4b83b2014f6913b4eeb20cd4665d12` and `aa8c286e371bf2ab126c41620648a3fcdb2b7209` compare precisely the same 64 hex digits after stripping only the known `sha256:` format prefix; neither relaxes a SHA requirement or original scientific tolerance.
- Final [Actions **42282848478**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282848478), tested SHA **`aa8c286e371bf2ab126c41620648a3fcdb2b7209`**: **SUCCESS, 31/31 tests**, including historic 576-case/64-fit/28-case/ABBA/eight-pair integrity and negative controls. [Machine artifact **13536061641**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282848478/artifacts/13536061641). The workflow additionally checks both original six-fit and reanalysis ZIP artifact digests via GitHub metadata and **downloads/re-hashes the complete archived eight-pair derived report** at SHA-256 `3c90a24b94921b90e80f1967dfaaaaff821b809d893b5939b5a314ed8635b327`. It does **not** download the original six-fit raw zip itself in this six-ledger job; raw-source replays remain separately recorded.
- The new post-hoc [local fitted Hessian/Laplace-scale audit](PERF01D_SUBJECT7_LAPLACE_SCALE_2026-11-06.md), [Actions **42282108311**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282108311), separately succeeded with **24/24 focused tests + 3 end-to-end tamper controls**. It describes very small free-parameter displacements on the *fitted conditional Laplace scale* yet **does not override the full original 63/64 NONPASS** or prove scientific identifiability.

**Author-side six-ledger PASS is only a reproduction/integrity result**. Source-level scientific review and a signed independent PERF-01C freeze remain **NOT RECEIVED / NOT FROZEN**. The original **63/64 NONPASS** full fits and **16 review pending/12 blocked** 28-case eligibility remain binding, with no paper-speed timing or GPU claim.
