# PERF-01C — independent-review quickstart and evidence boundary (2026-11-06)

**Review status: OPEN / NO EXTERNAL VERDICT / NO PROSPECTIVE FREEZE.** This page is an author-side handoff, not a signed reviewer report. Read `PERF01C_INDEPENDENT_REVIEW_HANDOFF.md` for the complete independent-review scope.

## Immutable sources and existing machine results

| Source | Exact original execution | What it does and does not establish |
|---|---|---|
| Original trialwise MATLAB/HGFX | [41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533) | Seven valid matched cells, three matched invalid paths; does **not** establish general fitting parity |
| Full cohort fixed-vector objectives | [41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774) | 448 valid-compatible, 128 matching invalid; not 576 completed public fits |
| Original 64 public full fits | [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) | **63/64 NON-PASS**, original subject index 7: four `traj.mu`, four `traj.muhat` out-of-tolerance cells |
| Original endpoint cross replay | [41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514) | Same-vector MATLAB/HGFX forward agrees; two different fitted vectors do not equal full-fit parity |
| MATLAB exact reference self sensitivity | [41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069) | One of six ±eps original-start probes crosses original final-vector fitting tolerance; not a certified scientific reference limitation |
| Four frozen HGFX full fits on same runner | [42249566219](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219) | Explicit SkylakeX/Haswell/Haswell/SkylakeX, same CPU affinity; original scientific 63/64 unchanged |
| Archived four-fit derived replay | [42250539438](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250539438) | 36/36 focused engineering tests; 28 fields; two exact same-mode comparisons, four mismatched cross-mode `mu/muhat`; **not an independent scientific review** |

Frozen versions: HGFX v1.0.0 @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and MATLAB HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`. Original fitting thresholds **rtol=3e-8 and atol=3e-10 for trial trajectories**; other fitting-field tolerances retain their specific original policy.

## Reproduction steps (reviewer executable)

1. Pin the **exact candidate commit SHA under review**, not only a movable PR branch name. Read the full handoff and the original source compatibility policy.
2. On the pinned checkout, run `python -m unittest discover -s tests -p test_perf01_prefreeze_ledger_guard.py -v` followed by `python benchmarks/runtime_v1/verify_perf01_prefreeze_ledger.py --root . --output reviewer-preflight.json`. This uses only tracked **derived JSON**, and must never be represented as rehashing remote raw evidence.
3. Separately download the original GitHub Actions artifacts above (the first six-source replay [42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894) provides an existing scripted raw/recompute pathway), run the archived raw SHA-256 checks and original scientific comparators on the **same** unchanged source/config/data, and record the first mismatched coordinates and masks.
4. Verify the exact source of MATLAB `core/fitModel.m`, `core/quasinewton_optim.m`, the active binary HGF path, optimizer gradient/termination semantics, full iteration field interpretation and numerical sensitivity evidence. Review source-only one-ULP reference self-sensitivity without a post-hoc exception.
5. Verify all **28** preregistered workload cases, including 16 concordant *review-pending* and 12 *blocked*; the 9-cell headline is ineligible. Review CPU affinity/threads, full API timing boundary, GPU physical hardware policy and analysis statistics. **Do not execute final paper-performance timing** at this point.
6. A reviewer independent of the implementer must provide a signed `PERF01C_REVIEW_<date>.md`: identity, exact reviewed SHA, all evidence hashes/artifacts, findings and severity, issue references, per-case eligibility, and explicit `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE`. If approved, a new versioned performance protocol lock and acceptance manifest must be committed **before** any final timing. A green job is not the review.

## Cross-ledger guard limitations

The new `benchmarks/runtime_v1/verify_perf01_prefreeze_ledger.py` cross-checks five immutable **tracked derived reports**: 576 subject/model/horizon combinations, 64 public fits and 28 fields, unchanged original and updated 28-case ledgers, and six ABBA contrasts with four source/run identifiers. It fails on moved denominators, changed original failure fields, fabricated independent-review status, altered BLAS report/hash entries or a changed blocked-case justification outside the two originally described fitting cases.

The guard validates **internal consistency only**, not that these archived raw bytes and MATLAB paths are scientifically correct; the remote raw re-download and independent source inspection remain mandatory. It never sets scientific or runtime gate status to PASS and makes no performance claim.

Historical failures remain visible: raw ABBA v1 auto-kernel control [42248605099](https://github.com/ahmadkhanloo/hgfx/actions/runs/42248605099), v2 analyzer legacy label error [42249566219](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219), new-run ISA SIGILL [42250002320](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250002320), and archive-only missing-package preflight [42250386120](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250386120). None retroactively qualifies as scientific pass.

**Current disposition:** PERF-01C OPEN, external reviewer NOT RECEIVED, frozen performance protocol NOT APPROVED, PERF-01E–H NOT RUN, final performance/speedup NOT ESTABLISHED.

## 2026-11-06 — seven ORIGINAL raw-source replay now completed

The [seven-source executed results](PERF01C_SEVEN_SOURCE_RAW_REPLAY_RESULTS_2026-11-06.md) and [GitHub Actions run 42263893242](https://github.com/ahmadkhanloo/hgfx/actions/runs/42263893242) @ SHA `6ac44118de6d87bec59c6dffba73e06e217c6f7a` downloaded and SHA-reverified all six original MATLAB/HGFX scientific artifacts **plus** the seventh original same-runner ABBA four-fit source archive. **52/52 focused tests PASS**. The six scientific original recomputations matched the archived original; the *entire* recomputed 28-field ABBA derived JSON matched its earlier immutable report **exactly except for the original report's added analysis-provenance field**. Original within-kernel exactness and across-kernel `mu/muhat` failure classifications were preserved.

Machine evidence: [artifact 13525532759](https://github.com/ahmadkhanloo/hgfx/actions/runs/42263893242/artifacts/13525532759). This **does not** run MATLAB/HGFX fits afresh; the seventh fit source-run historically FAILED in its post-fit analyzer and remains marked failed. It is author-side source-archive replay, not a second independent reference evaluation or independent reviewer verdict. The full original 64 public fit **63/64 NONPASS** persists (subject index 7), 28-case ledger **16 review-pending / 12 blocked**, six original primary HGF cells ineligible. The reviewer must still independently verify source-level science and approve or block a prospective protocol lock. PERF-01C **OPEN / NOT FROZEN**; PERF-01E–H **NOT RUN**; no speed claim.


## 2026-11-06 — sixth tracked ledger and COMPLETE remote eight-pair source report checked

[Detailed six-ledger / full-artifact results](PERF01C_SIX_LEDGER_AND_FULL_EIGHT_PAIR_PREFLIGHT_2026-11-06.md) supersede the **scope** of the initial five-ledger-only local check, not its historical evidence or test outcome. Successful [Actions 42282680926](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282680926) @ `d0f328061a4b83b2014f6913b4eeb20cd4665d12`, **31/31 tests**; downloadable [artifact 13535289252](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282680926/artifacts/13535289252). The sixth tracked JSON reports **all eight** same-runner frozen MATLAB/HGFX pairs, each **NONPASS** under the original unchanged 28-field fitting criteria. The CI independently downloads the **complete 239,651-byte eight-pair derived report**, verifies full SHA-256 `3c90a24b94921b90e80f1967dfaaaaff821b809d893b5939b5a314ed8635b327`, and cross-checks every paired field/tolerance/failing cell with the original frozen fitting ledger. Both raw-source and derived ZIP artifact digests are checked through GitHub metadata; the raw-source ZIP bytes themselves are **not re-downloaded in this CI**, but were verified in earlier source-archive replay.

First attempted [42282580753](https://github.com/ahmadkhanloo/hgfx/actions/runs/42282580753) FAILED the new synthetic tests because the guard compared plain-hex archive SHA-256 to the prefixed `sha256:<hex>` form from GitHub. Fix `d0f328061a4b83b2014f6913b4eeb20cd4665d12` adjusts only the format comparison without altering the hexadecimal value or historical evidence; the failure is retained.

**Original 63/64 scientific NONPASS, 16 review-pending/12 blocked predeclared cases, no independent verdict/signature, PERF-01C OPEN/NOT FROZEN and PERF-01E–H NOT RUN remain unchanged.** A successful six-report integrity preflight is not independent scientific acceptance or a GPU/CPU speed claim.
