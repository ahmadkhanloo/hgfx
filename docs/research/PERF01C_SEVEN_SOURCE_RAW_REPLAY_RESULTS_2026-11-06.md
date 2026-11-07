# PERF-01C: seven-original-source raw replay and ABBA integration — 2026-11-06

**ENGINEERING REPLAY: PASS. SCIENTIFIC FULL-FIT COMPARISON: 63/64 NONPASS. INDEPENDENT REVIEW: NOT RECEIVED. PERF-01C: NOT FROZEN. No performance timing or speedup.**

## Exact source/runner and artifact

- Successful [GitHub Actions run 42263893242](https://github.com/ahmadkhanloo/hgfx/actions/runs/42263893242), source commit **`6ac44118de6d87bec59c6dffba73e06e217c6f7a`**, job ID `128050614756`.
- [Machine artifact #13525532759](https://github.com/ahmadkhanloo/hgfx/actions/runs/42263893242/artifacts/13525532759), `perf01c-seven-source-original-raw-42263893242`. The artifact contains a complete newly recomputed ABBA 28-field report, original source SHA ledger, and evidence/reviewer status, not newly fitted or timed data.
- New seven-source verifier: `benchmarks/runtime_v1/verify_perf01_seven_source_handoff.py` and `.github/workflows/perf01-seven-source-raw-replay.yml`; 10 new negative/positive tests in `tests/test_perf01_seven_source_handoff.py`.
- **52/52** targeted tests PASS (10 seven-source tamper tests + 17 ledger tests + 17 original ABBA tests + 8 reference self-sensitivity tests). Frozen release checked out at HGFX **`4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`**, NumPy **2.3.5**, CPU only.

## Exact seven historical original-source runs, never modified

| Original Actions run | Retrieved original artifact / activity | Outcome of this replay |
|---|---|---|
| [41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533) | Original MATLAB/HGFX 10 trialwise comparisons | Source SHA-256 and full comparator **MATCH**; 7 comparable, 3 matching invalid prefixes |
| [41855647245](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855647245) | One-subject 3-horizon public-fitting preflight | Source SHA-256 and full comparator **MATCH**; 128 valid, 512/1024 blocked |
| [41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774) | 576 fixed-vector combinations | Source SHA-256 and full comparator **MATCH**; 448 compatible, 128 both invalid |
| [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) | 64-subject full paired fits, original failed science | Source SHA-256 and full comparator **MATCH**; **63/64 NONPASS** with subject index 7, four `traj.mu` and four `traj.muhat` failures |
| [41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514) | Two original optimizer endpoints, exact-vector cross-replay | Both raw SHA-256 and 15 trialwise-field comparisons **MATCH**; optimizer endpoint difference remains |
| [41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069) | Frozen MATLAB-only self-sensitivity | Original MATLAB raw SHA-256 and all six ±eps probes **MATCH**; no reference-limitation approval |
| [42249566219](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219) | Four original same-host frozen HGFX fits, explicit ABBA BLAS dispatch | Four raw SHA-256 and original machine/BLAS metadata **MATCH**; 6 pairwise original 28-field conclusions and 4 source MATLAB comparisons all **MATCH** |

The seventh source is the original four-real-fit artifact from a workflow that **failed its post-fit legacy analysis stage**. The four actual raw fits remain verifiable and were not regenerated or edited. The original source-run failure, later runner SIGILL and standalone successful ABBA report remain preserved as separate historical results, not rewritten as successful original workflow executions.

## Recomputed ABBA result: full report matches, not just acceptance labels

The new verifier replays the original four raw source files and original full 64-subject MATLAB/HGFX reference from run 41863441006 using the unchanged original fitting-field tolerances. It validates all four raw source SHA-256, source-run SHA `c84e76ac15779357b620a3d273add224cad2cdf5`, original four CPU affinity/BLAS metadata, all **six** A/B comparisons, **28** original fitting fields and the four historical MATLAB contrasts.

The recomputed full ABBA report was **exactly equal to the earlier committed derived report after omitting only the later `analysis_provenance` field** (`complete_derived_report_exact_except_analysis_provenance: true`). That earlier report was produced by [42250539438](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250539438), with immutable tracked JSON SHA-256 **`7898bee80dd50a53b2ae9605fdf10d4e9562ef3b45783fb103a822a1ec619730`**. No new tolerance, exclusions or selective case acceptance was introduced. A negative test requires that even descriptive finite scalar drift be explicitly reported as **not exact**, while preserving the scientific decision gate.

Within the one original ABBA runner, two repeated SkylakeX and two repeated Haswell fits match bitwise across all 28 serialized fields **within their respective modes**. Four cross-dispatch comparisons each fail four `traj.mu` and four `traj.muhat` cells under the original tolerances. Against the unchanged archival MATLAB fit, both SkylakeX variants still fail four `mu`/`muhat`; both Haswell variants have 14 each plus `traj.epsi/psi`. There is **no fresh matched-host MATLAB fit**, and this diagnostic cannot certify scientific fit parity.

## Remaining acceptance blockers

Scientific source audit and reviewer **identity + signed verdict** remain absent. The prospective performance protocol cannot be frozen and no final timing has occurred. Source artifacts are unchanged; the previously **16 review-pending/12 blocked** 28-case ledger and **six ineligible original primary CPU cases** remain unaltered. Issues [#88](https://github.com/ahmadkhanloo/hgfx/issues/88), [#89](https://github.com/ahmadkhanloo/hgfx/issues/89), [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) stay OPEN. Before any paper-performance experiment, a reviewer independent from the implementer must check the source/model/optimizer semantics, raw hashes, fixed protocol and environment, and issue a signed verdict. This CI alone cannot authorize a lock.
