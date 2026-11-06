# PERF-01D — source-native tolGrad stopping margin and 2-run bitwise replay, original subject 7 (2026-11-06)

**Author-side, untimed and SHA-256-locked engineering diagnostic: PASS. Scientific full fitting: 63/64 NON-PASS. PERF-01C independent review: OPEN / NOT FROZEN. No speedup.**

Tracking [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [PERF-01C independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [original fitting mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89), [cross-run floating-point portability #90](https://github.com/ahmadkhanloo/hgfx/issues/90).

## Question, frozen baseline and scientific boundaries

Previously, both original frozen MATLAB HGF Toolbox v8.2.0 and HGFX v1.0.0 public fitting implementations were shown by direct source-native evidence to terminate with **tol_grad**, not two different named stopping rules. This experiment asks: **how far are their original post-fit Ridders source-gradient evaluations from the actual tolGrad threshold?** It also compares the TWO already completed original frozen-source native-stop run artifacts, both of which have the same stop category but different HGFX raw SHA-256. It does not run a new optimizer or reinterpret overwritten history records as accepted source steps.

Frozen original product **HGFX v1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`**, MATLAB HGF Toolbox **8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`**, original `hgf_binary + unitsq_sgm`, subject **7 zero-based**, 128 original trials, full transformed 15-vector, original 3 free transformed params [12,13,14], original start/config/prior and 64-subject fitting source SHA256 unchanged. Historic complete public fitting result remains **63/64**, with 4 `traj.mu` and 4 `traj.muhat` failing original tolerance cells.

The original MATLAB source expression at gradient stopping is `max(abs(grad').*max(abs(x),1)./max(abs(val),1)) < tolGrad`, with frozen **tolGrad=0.001**. The original HGFX source expresses the corresponding elementwise absolute-scale computation in NumPy. All Ridders values used in this new analysis are **RECOMPUTED AFTER FIT at each own-engine archived state** (original BFGS archive), not an instrumented real-time internal optimizer event. The source Ridders error fields are **heuristic numerical estimates, NOT rigorous certified error bounds**.

## Exact immutable input archives and identity checks

1. [Original real MATLAB+HGFX BFGS public full-fit run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), tested original exporter SHA `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d`; SHA-256 **HGFX `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`**, **MATLAB `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`**, source summary and comparison JSON identity, plus prior successfully derived BFGS source branch report separately verified.
2. [First source-native optimizer stop run 42232378487](https://github.com/ahmadkhanloo/hgfx/actions/runs/42232378487), tested SHA `6351160b2b528a9db894e873ce65677ee847bbe5`: raw **HGFX `71867c75c84de0e919e195a0f5124726c8352bfcfac233f9ac8cd6fe7e75d3c3`**, **MATLAB `c16736a221758d39b4ccef45a217798a3661dd6c78b75fec0d6f7f19869cbf48`**. Both source-native stop `tol_grad`, 25 finite optimizer slots, normal-vs-verbose MATLAB full output exactly identical, HGFX direct vs same-process public optimizer state exactly identical.
3. [Second source-native optimizer stop run 42232421468](https://github.com/ahmadkhanloo/hgfx/actions/runs/42232421468), tested SHA `5d26ca719a2a3e996ca07edd2d29282fc3ca1173`: raw **HGFX `2dced38aa33bff545c1b1d36c3a0e866911e52271fcd22fcf1b357fc16cab0bf`**, **MATLAB `c16736a221758d39b4ccef45a217798a3661dd6c78b75fec0d6f7f19869cbf48`**. Same source-native stop `tol_grad`, same original model and controls. Original 64-fit raw evidence SHA256 checked in both prior runs and linked by their preserved derived metadata. **Do not misinterpret two successful source-native runs as two new scientific passes.**

The new script requires both original full raw files and native derived reports from each run, verifies all original SHA256, source identity, thresholds, free param order, trial count, original 63/64 classification, two original non-PASS fields, and original source history/success manifest. The two native raw MATLAB files have identical SHA **for exactly these two runs**; this does NOT establish universal bitwise MATLAB cross-host reproducibility. The two native HGFX raw files have distinct SHA; their numeric content must be compared before diagnosing the difference.

## Executed real GitHub Actions, tests and numerical results

[Successful derived audit **42244053396**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42244053396), exact tested code SHA **`c1eb52e375668227ed75f23fc109f9ddd4e563de`**, **42/42 tests**: 13 new gradient/replay negative and positive controls + 14 existing source-native optimizer stop controls + 7 original 64-fit source checks + 8 original BFGS branch tests. Re-downloads all three original GitHub Actions artifact sets and recomputes raw SHA-256; no new MATLAB/GPU/CPU fitting execution or timer.

Permanent machine-readable evidence `benchmarks/runtime_v1/issue90_results/derived-gradstop-two-run-42244053396.json`, bot commit **`3dcb32f9a103c7eff93b16b9be030550604054ef`**. Full derived artifact is additionally retained on the successful run. Source files: `benchmarks/runtime_v1/derive_subject7_gradstop_repeatability.py`, `tests/test_perf01_subject7_gradstop_repeatability.py`, `.github/workflows/perf01-gradstop-two-run-derived.yml`.

### Original own-source Ridders gradient criterion, after original full fitting

| Original filled history record (zero-based) | HGFX source normalized gradient score | MATLAB score | Original criterion |
|---|---:|---:|---|
| 21 | `0.0113099437026184` | `0.011309933292253755` | **above 0.001** |
| 22 | `0.010915740286267555` | `0.01091572241465266` | **above 0.001** |
| 23 (terminal stored state) | **`0.0002267376638137444`** | **`0.00022673690180591603`** | **below 0.001** |
| 24 (duplicated terminal stored state) | `0.0002267376638137444` | `0.00022673690180591603` | **below 0.001** |

At terminal record 23, both normalized source Ridders gradient scores are approximately **22.67%** of the original threshold, i.e. the threshold is about **4.4 times larger** than the normalized gradient. At the original terminal state, the largest **source-scaled Ridders heuristic error estimate** is **`8.914668594767825e-14` for HGFX** and **`8.63374327417855e-14` for MATLAB**, many orders smaller than the approximately `7.7326e-4` threshold separation. This is *descriptive numerical evidence*, not a rigorous bound on derivative error, nor proof of identical original internal loop gradients. Recorded MATLAB terminal overwrites remain explicitly unresolved as an accepted step-by-step trace.

### Separate two-real-run HGFX bitwise portability and scientific verdict

The two native-stop runs use frozen HGFX sources and original model/config. Strict bitwise comparison of the complete recorded outputs found:

| Compared original HGFX recorded quantity | First different location, zero-based | Maximum absolute difference |
|---|---|---:|
| Public final transformed 15-vector | coordinate **12** | **`1.4572520967703895e-10`** |
| Direct optimizer full 101×3 history | **record 2, coordinate 0** | **`9.060663330728858e-10`** |
| Direct optimizer full 101 objective history | record **2** | **`5.069153985459707e-10`** |

The entire 101-entry buffers and finite/nonfinite masks were retained; among finite entries, **69 history parameter values** and **23 objective values** differ bitwise. Both source-native runs still report **tol_grad**, 24 iterations and zero resets. These are **different CI executions**; hardware/BLAS dispatch were not pinned or independently instrumented for matched-runtime attribution. **Do not claim the variation was caused by a specific CPU, vendor or BLAS implementation without controlled evidence.**

Across **ALL 11** original HGF trialwise fields, both HGFX outputs are within original numerical tolerances of **each other** (zero failing cells at old **rtol=3e-8, atol=3e-10**). Against the exact same MATLAB raw trialwise output, **both** HGFX runs still fail **four original `mu` and four original `muhat` cells**, and no other original trajectory field. The numerical source repeatability difference is not itself the reason for reclassifying original scientific parity.

## Interpretation and remaining gates

**Established, bounded:** gradient stopping at archived original subject7 terminal states is consistent with both native-source **tol_grad** stop labels, with a sizeable observed normalized gradient margin based on post-fit Ridders gradients. Both frozen HGFX reruns retain the same own-process stop and old-tolerance classification, despite a small **bitwise** drift starting at history record 2. MATLAB raw output is **bitwise identical across these two recorded runs only**. Original normal-vs-verbose MATLAB output exactness is already independently verified in the source-native audit.

**Not established:** a rigorous bound on unknown true gradient, exact original in-loop gradient values, bitwise repeatability on a CPU-dispatch-controlled environment, unique cause of HGFX two-run floating drift, source-level defect, accepted reference-only scientific limitation, scientific fitting full 64/64 PASS, or prospective benchmark eligibility. **No threshold was relaxed, no historical evidence erased, no data/seed changed, and no speed test was run.**

The original full MATLAB/HGFX public fit **63/64 SCIENTIFIC NON-PASS** remains; 28 planned performance cells **16 independent-review pending / 12 blocked**, six of nine original primary CPU cases ineligible. Independent PERF-01C reviewer [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) OPEN/NOT FROZEN; original fitting issue [#89](https://github.com/ahmadkhanloo/hgfx/issues/89) OPEN; auxiliary repeatability limitation [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) OPEN. **PERF-01E–H NOT RUN; no CPU/GPU benchmark or speedup.**

**Next bounded action:** external reviewer should explicitly consider original fitting eligibility and numerical equivalence without converting post-fit source gradient compatibility into a scientific parity PASS. If resolving Issue #90 is necessary, run a *separately prespecified* same-host paired CPU/BLAS provenance control, preserving exact original raw sources, model and thresholds and the historical failed bitwise strict replay.
