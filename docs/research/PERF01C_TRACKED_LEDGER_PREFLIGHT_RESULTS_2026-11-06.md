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
