# PERF-01D — actual frozen MATLAB 26-field public-fit raw archive and SciPy replay (2026-11-07)

**AUTHOR-SIDE SUPPLEMENTARY RAW EVIDENCE EXECUTED: 26/26 PAIRS STRICTLY IDENTICAL IN REAL ARCHIVED VALUES; 10/10 SYNTHETIC FAIL-CLOSED CONTROLS. THIS IS NOT AN INDEPENDENT SCIENTIFIC REVIEW VERDICT OR A NEW SCIENTIFIC GATE. ORIGINAL 63/64 FITTING NONPASS, PERF-01C NOT FROZEN, NO PAPER SPEEDUP OR GPU VALIDATION.**

## Pre-execution source and scope

Supplementary [raw-value experiment prespec](PERF01D_26_PUBLIC_FIELDS_RAW_ARCHIVE_PRESPEC_2026-11-07.md) was committed at SHA **`5eb723ea859e160564c10fb181e52de68ece175e`**, before the new raw 26-field observation. Original post-result selected HGFX-own x6/T6 and two saved hypothetical gradient substitutions are unchanged, with source candidate JSON SHA **`b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144`**. Frozen HGFX 1.0.0 **`4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`** and MATLAB HGF Toolbox 8.2.0 **`2437f4dc241541072722a2695ddeca7b44d83dd3`**. MATLAB R2026a Update 5 (`26.1.0.3346908`). Same original 128 trials, subject index zero-based 7, same BFGS config, data/start, fitModel and nested original objective. The 26 fields are the **existing 15 `optim` and 11 complete original `traj` fields**, not a later selected subset; names and actual paired values are stored in a raw MATLAB `-v7` MAT file.

The original four-argument actual MATLAB probe is retained without behavior changes; an **optional fifth output-path argument** allows archiving selected stable public output arrays from each native and instrumented fit. Previously successful author-side frozen private MATLAB [run 42375431029](https://github.com/ahmadkhanloo/hgfx/actions/runs/42375431029), archive-only [Armijo replay 42377148619](https://github.com/ahmadkhanloo/hgfx/actions/runs/42377148619), and all original failed source artifacts remain preserved; this new experiment is not substituted for them.

The original public full-fit [source run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) is still **63/64 SCIENTIFIC NONPASS**, with original 4 `traj.mu` + 4 `traj.muhat` failed values for zero-based subject 7 at unchanged thresholds. The original 28-case runtime protocol remains 16 review-pending / 12 blocked.

## Runs, including first failure

- First supplemental raw-archive [run **42378148766**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42378148766) at `4eb2187e5fd25e885791362b016642f58713234c` **FAILED at the synthetic Python test fixture before any new MATLAB fitting**, due to SciPy `savemat`'s default 31-character struct-field-name restriction. All 10 fixture tests were blocked by that serialization problem; no scientific conclusion was generated from the failed attempt. Historical failed run and logs preserved.
- The **synthetic fixture only** was updated with `long_field_names=True` in `savemat`, commit `e8d543ba0b49b73edcde8fe0c01bc2e7081a4da2`. No original 26-field selection, MATLAB optimizer, source dataset, acceptance threshold or measured output changed.
- Second [GitHub Actions run **42378200899**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42378200899) at exact SHA **`e8d543ba0b49b73edcde8fe0c01bc2e7081a4da2`** **SUCCESS**: 10/10 synthetic positive/negative controls; frozen MATLAB/HGFX Git SHA checks; both original BFGS raw SHA checks; original candidate SHA check; original 63/64 public-fit 4+4 failure check; real native and callback-instrumented MATLAB fit and 3 real private objective calls; raw MATLAB `-v7` snapshot containing all **52 values (26 pairs)**; a separately coded SciPy parser reading actual archive bytes, deep comparison of all **26/26** pairs (nested structures/cells, shapes, dtypes, values, matching NaNs). The parsed field-by-field JSON lists every field, equality, per-side type/shape and first mismatch (none observed). No new time/throughput benchmark.
- Backward-compatible original 4-argument [run **42377908677**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42377908677) at the optional-export MATLAB code change was also SUCCESS; it does not independently verify the supplemental 26-field archive.

## Raw artifact and verified hashes

[**Full downloadable evidence artifact 13576990352**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42378200899/artifacts/13576990352) from successful run 42378200899:

| Artifact member (inside ZIP) | Actual SHA-256 |
|---|---|
| `native-instrumented-all-26-fields.mat` (both actual MATLAB public fits) | `be6b845a2db5100d878e534f0eece5ee221fd1cd405b2c9d1711bf85cbd3bdb2` |
| `independently-parsed-26-field-results.json` (every actual field, independent Python code path) | `26c022c188f62300ed01a97ab52927bbd57773df8521bea1482a20e209c785b7` |
| `private-three-source-objectives-new-run.json` (original nested private source values for this run) | `888112a48a167428400b3bf8111ca7e238fa0f45c2a4e5d6bf385bf47ca7b5dc` |
| `private-three-source-objectives-derived.json` | `54bc684e7732c73fb79d44a1087cc79ec0aa481caeac36e037932b5135b3bd3a` |
| Entire GitHub artifact ZIP | **`62894798cefc5ebfa86eb536fe8779e87d87e6584d7b98636af6f8ef179542d8`** |

The bundle also includes `provenance.json` with run/commit/protocol/frozen-source IDs, member SHA-256, original 63/64 NONPASS, no review, no freeze, no timing. Archive `.mat` is inspectable outside the producer by SciPy or MATLAB.

## Exact observation and scientific limitations

The full raw MATLAB 26-field pair-by-pair source equality is now reproducible **from the archived values**; this closes the previous author-side evidence-transparency gap where only the producer's `native_instrumented_stable_fields_identical=true` aggregate assertion existed. `scipy.io.loadmat` nested value comparator returned `AUTHOR_SIDE_PUBLIC_26_FIELD_RAW_REPLAY_IDENTICAL`, `native_and_instrumented_fieldwise_exact=true`, `compared_fields_count=26`. The producer's own `isequaln` aggregated boolean also remained true, but **the archive comparator does not rely on that boolean to decide field equality**.

The three private MATLAB objective values also matched original run 42375431029 at these same three counterfactual points:

- HGFX-owned source x6: `108.28848680066957`
- Original HGFX-gradient x7 candidate at same x6/T6: `105.8665439753067`, source original Armijo full-step **TRUE**.
- Actual private MATLAB-gradient x7 candidate at same HGFX-owned x6/T6: `105.8665440308226`, original Armijo full-step **TRUE**.

**Neither this raw archive nor the equal 26-field native/instrumented control proves that original HGFX and MATLAB 64-subject fits match.** It verifies only that the instrumented and noninstrumented *same frozen MATLAB reference fitting* produce identical stable public fields on this selected subject, and that the archived counterfactual objective math has not been perturbed. The actual original MATLAB-owned x6/T6 is different from HGFX's selected x6/T6; no real full-path MATLAB optimizer decision/causality has been proven. Existing 33/245 Ridders stencil 1–2 ULP differences outside these points and the original 4+4 trajectory NONPASS remain unchanged.

**Reviewer signoff still required.** Although the producer and the separate Python comparator are now independently executable code paths and the **raw values** are preserved, both were implemented/executed author-side. A separately identified scientific reviewer must still evaluate provenance, original 28-case coverage, thresholds, fit output mapping, optimizer branch/convergence interpretation and the full original failed fitting. Required reviewer verdict in [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) remains **NOT RECEIVED**. Do not merge as scientific approval, classify scientific reference limitation, make 64/64 parity claim, or run paper timing/GPU comparison before prospective PERF-01C decision. Related [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) and [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) remain open.
