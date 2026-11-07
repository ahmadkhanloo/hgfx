# PERF-01D — SHA-locked archive-only replay of actual MATLAB-private Armijo source (2026-11-07)

**AUTHOR-SIDE ARCHIVE REANALYSIS: SUCCESS. THIS IS NEITHER A NEW MATLAB FIT NOR INDEPENDENT SCIENTIFIC REVIEW. ORIGINAL 63/64 FITTING NONPASS, PERF-01C NOT FROZEN, NO PAPER SPEEDUP OR GPU CLAIM.**

## Reanalysis purpose and fixed evidence

Re-evaluate the *already archived* true private MATLAB nested-objective measurements and the two original saved same-x6/T6 full-step candidate source conditions, using an **independently written stdlib Python comparison pathway** without importing `subject7_private_candidate_armijo.py` (the original generator's verifier). There are **zero** new objective calls and **zero** benchmark timings. The source experiment was **post-result selected**; the new replay makes no prospective scientific acceptance claim.

Frozen original scientific incident [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) remains 63/64 NONPASS, zero-based subject 7: **four** `traj.mu` and **four** `traj.muhat` values fail unchanged original fitting tolerances. Frozen HGFX 1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; frozen MATLAB HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`. The original MATLAB-native vs instrumented 26-field `isequaln` control was performed by the *producer MATLAB process*; it is not independently re-executed by this archive replay because individual field arrays are not in its private three-point artifact.

Archived immutable exact inputs:

| Source | Run / member | Required SHA-256 |
|---|---|---|
| Original one-step same-HGFX-x6/T6 candidate | [42366705874](https://github.com/ahmadkhanloo/hgfx/actions/runs/42366705874) `source-same-state-two-gradient-candidates.json` | `b2f2134a4eb5276fd7734dacedb26c74b4cd410eb984caf945befe9758b42144` |
| Actual frozen private MATLAB objective | [42375431029](https://github.com/ahmadkhanloo/hgfx/actions/runs/42375431029) `private-matlab-three-candidate-objectives.json` | `b901486c9f8a17cc414f60b284ecc707c0fb314652e1089db29a91ae208fadd7` |
| Original author-side derived decisions | [42375431029](https://github.com/ahmadkhanloo/hgfx/actions/runs/42375431029) `derived-private-matlab-armijo-summary.json` | `f42274c7f284edaa19bbb5ff09e69887471be9e04bbb615e9effca3a35a75275` |

Replay checks exact *member byte* SHA-256 (not only a filename), original full-fit 63/64 failure fields/count, immutable source SHAs, input candidate x and origin, all 3 original private objective statuses/coordinates, original unclipped `1e-4*slope`, actual `f(x_candidate)-f(x6)`, strict Armijo Boolean, source previous-HGFX objective, original derived result, and provenance including original run `42375431029` at `b3821627e787380766843660a36ae04017535987`. The independent replay uses no new tolerance and fails closed for missing or mismatched source. No scientific acceptance flag can be set by this workflow.

## Execution accounting

- First replay [42377115157](https://github.com/ahmadkhanloo/hgfx/actions/runs/42377115157) at `3d9ed2750bf7159f16697269a028a911536e26ee`: **FAILED before archive download** at an engineering negative unit test. The expected regex `three` did not match the error's capitalized `Three`. Other nine tests succeeded. The first failure is preserved; no scientific or archival result obtained from that failed run.
- Test-message-only correction [`fed89db35f944a2fffd5d829fd43d0c93fcd1e3a`](https://github.com/ahmadkhanloo/hgfx/commit/fed89db35f944a2fffd5d829fd43d0c93fcd1e3a) changed no input, threshold, evaluator, source formula or MATLAB.
- Subsequent [archive-only Actions **42377148619**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42377148619) at exact `fed89db35f944a2fffd5d829fd43d0c93fcd1e3a`: **SUCCESS**, **10/10** synthetic fail-closed tests, exact three source member SHA-256 checks, and independent-codepath re-derivation of all **two** full-step Armijo margins from the real archived private MATLAB values. No new MATLAB/HGFX optimization or original public fit. [Artifact **13576246270**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42377148619/artifacts/13576246270), ZIP SHA-256 `42a76ae25deb373b0e0df4e77361b0f71e188faadad9b39c6bd590f8aae0e7ec`, new derived `private-armijo-archived-replay.json` SHA-256 `f4eb117d5ec8545c03d0b4873bf068b4380852656ba87b212d677dec3aca3606`.
- Author-only source replay code: [`replay_subject7_private_armijo_archive.py`](../../benchmarks/runtime_v1/replay_subject7_private_armijo_archive.py), [10 fail-closed controls](../../tests/test_perf01_subject7_private_armijo_archive_replay.py), [self-contained archive workflow](../../.github/workflows/perf01-private-armijo-archive-replay.yml).

## Recomputed numerical Armijo evidence

For **the original HGFX-own source x6 and T6** (not MATLAB-own x6/T6), actual private MATLAB `f(x6)=108.28848680066957`. Three archived values at identical coordinates match the corresponding HGFX objective values exactly, but this does **not** prove objective equality on other stencil points or the whole parameter surface.

| Same original HGFX-owned x6/T6; only gradient swapped | Real MATLAB-private next f | Actual delta `f(next)-f(x6)` | Source RHS `1e-4*g'*(-T6*g)` | Armijo RHS − LHS | `lhs < rhs` |
|---|---:|---:|---:|---:|---|
| Original HGFX gradient | 105.8665439753067 | -2.4219428253628763 | -0.0005994998154185825 | **2.4213433255474577** | **TRUE** |
| MATLAB private gradient at same original HGFX x6 | 105.8665440308226 | -2.4219427698469786 | -0.000599499832595494 | **2.421343270014383** | **TRUE** |

These both have substantially positive retrospective Armijo margins **for this local full-step source reconstruction**. There is **no Armijo Boolean flip** between the two selected candidates, and both are far from the local Armijo acceptance boundary at the measured values. The previously observed `1.0444791836983214e-08` one-step coordinate sensitivity remains a valid limited diagnostic, not causal attribution of the original global fitted-vector divergence.

## Reviewer boundaries and next required decision

The archive arithmetic replay establishes *only* input-byte integrity and source-formula consistency for this pre-existing observation. It **does not independently reproduce** the actual MATLAB-private `fitModel` evaluations, physical runner arithmetic, the 26 individual native/instrumented public field values, internal private BFGS branch events, or full subsequent optimization paths. It does not turn a source-archive author-side validation into an independently signed scientific conclusion. The earlier real MATLAB source runner is still the observational oracle.

Independent reviewer [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) must decide whether this local evidence materially narrows the cause of historical trajectory mismatch without overstating its scope; read both raw and failed source runs, review original MATLAB source and full original 28-case eligibility, and sign a verdict **before** PERF-01C prospective freeze or performance timing. Also review [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) (original scientific fitting failure) and [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) (host-dependent reductions). Until then scientific fit **63/64 NONPASS**, 28 workload cases **16 review-pending/12 blocked**, PERF-01C **BLOCKED**, PERF-01E–H **NOT RUN**, and **no scientific reference-limitation waiver / GPU validation / speedup**.
