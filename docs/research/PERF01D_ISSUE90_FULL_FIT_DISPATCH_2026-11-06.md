# PERF-01D / Issue #90 — same-host BLAS dispatch affects real frozen HGFX subject-7 fitting (2026-11-06)

**Status: new author-side untimed full-public-fit numerical-sensitivity evidence, not an independent scientific finding. The original 63/64 MATLAB/HGFX fitting diagnostic remains NON-PASS.**

## Objective and immutable source

This experiment follows [the within-runner binary64 scalar dispatch audit](PERF01D_ISSUE90_OPENBLAS_SAME_HOST_2026-11-06.md) and asks a separate question: *with the frozen HGFX public fitting implementation and identical data/optimizer, does changing OpenBLAS dispatch change the actual fitting path?* It does **not** change the reference workflow, accepted tolerances, original 64-subject sample, seeds or validation grids.

- HGFX v1.0.0 exact source SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, public `fit_model` with `hgf_binary` + `unitsq_sgm`, original zero-based subject 7, **128 trials**, original config and `nRandInit=0`.
- HGF Toolbox 8.2.0 MATLAB reference SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`. MATLAB reference was **NOT re-executed** in this experiment.
- Source and config were checked against unchanged original [64-fit CI 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), with its original tracked summary manifest `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json` and both original raw file SHA-256 checks. Original failure `FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH=1`, within old diagnostic tolerances `=63` explicitly asserted before new fitting.
- Previously frozen raw BFGS full public traces [CI 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) rechecked with full HGFX raw SHA-256 `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce` and MATLAB raw SHA-256 `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.
- Both newly executed fit calls use the **unmodified** frozen public source, the same 64×128 binary dataset, **identical original fitting start**, same Ridders `min_steps=10`, same BFGS parameters; no time measurement.

## CI, environment, evidence

- First workflow attempt [42198798176](https://github.com/ahmadkhanloo/hgfx/actions/runs/42198798176) **FAILURE** at input staging, before fitting: the raw 64-subject artifact did not contain the tracked summary-manifest file. The tracked manifest was copied explicitly alongside hash-checked original raw artifacts in the corrected workflow, without modifying archived data.
- Actual [**CI 42199013326**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42199013326) **SUCCESS**, exact experimental code SHA `81c0edf92f28d525f12ecae900527ebd45fe8946`, **10/10 focused comparator tests**, source/config checks, untouched frozen v1.0.0 verification, same Linux x86_64 GitHub runner for both modes, NumPy **2.3.5**, OpenBLAS **0.3.30**, 4 BLAS threads, JAX CPU platform forced. Linux `7.0.0-1017-azure`.
- Original `OPENBLAS_CORETYPE` unset: effective kernel **SkylakeX**; forced `OPENBLAS_CORETYPE=Haswell`: effective kernel **Haswell**. Both runs recorded the same GitHub run ID and platform.
- SHA-256 of **newly produced, distinct** full-public-fit raw records: automatic/SkylakeX `848e2aaee266d772420231c4749268a8922b5a49e70da9b1eff8a4fefbf86246`; Haswell `58a4db667706988257724cf3237bd261a1376e60a738eb5399debae9b2af2a1b`.
- Machine-readable derived result `benchmarks/runtime_v1/issue90_results/derived-full-fit-42199013326.json`, committed by bot at `cbf809891b3a291bb2867568e3875ff095f7db92`. Complete separately labeled raw/refit JSONs plus host metadata archived as artifact in [CI 42199013326](https://github.com/ahmadkhanloo/hgfx/actions/runs/42199013326). No old evidence file overwritten.

## Original public fit differences on the SAME physical runner

| Frozen public-fit output, auto vs Haswell | Compared finite coordinates | Nonidentical finite coordinates | Largest absolute difference |
|---|---:|---:|---:|
| `iter.x` — actual optimizer parameter-path coordinates | 75 | 65 | **`4.4914698094089545e-7`** |
| `iter.val` — actual optimizer objective-value records | 25 | 22 | **`2.6154653198773303e-7`** |
| `iter.invH` — original BFGS inverse-Hessian entries | 216 | 194 | **`1.8149043592075031e-4`** |
| 25 own-state recomputed Ridders gradients | 75 | 66 | **`4.875479618360323e-7`** |
| `optim.final` — full final parameter vector | 11 | 3 | **`3.968255768427298e-8`** |

Arrays retain original NaN/nonfinite masks (11 finite components among 15 final parameters); no changed mask was hidden. No additional configuration, model family, data, training or optimizer parameter choice was introduced. These are real **full fitting** output differences, not only floating-formatting differences in a post hoc norm. The numerical-path sensitivity is reproducible under an **environment-only dispatch intervention** on this tested runner.

### Descriptive comparison with historical MATLAB reference

The original untouched MATLAB BFGS archive is **from another CI execution**, so the following values are **cross-run diagnostics**, not a same-host scientific compatibility oracle:

| Comparison of frozen final transformed/full 15-component vector (11 finite) | Largest absolute difference |
|---|---:|
| New HGFX auto ↔ historical MATLAB | `3.277081539465598e-8` |
| New HGFX Haswell ↔ historical MATLAB | `7.245337307892896e-8` |
| Historical HGFX ↔ historical MATLAB | `3.291654060433302e-8` |
| New HGFX auto ↔ historical HGFX | `1.4572520967703895e-10` |
| New HGFX Haswell ↔ historical HGFX | `3.953683247459594e-8` |

**Important:** matching the historical diagnostic's bit patterns with Haswell did **not** make the new HGFX fitted endpoint closer to historical MATLAB in this comparison. Crucially, this workflow did **not** export or compare the fitted `traj.mu` or `traj.muhat` fields anew. Therefore no complete scientific fitting PASS/NONPASS classification can be obtained from this endpoint-only table; the original **63/64 non-PASS remains binding**.

## Interpretation and next acceptance work

**Established within this bounded experiment:** changing only OpenBLAS kernel dispatch on one host changes many numerical states along the actual unmodified HGFX v1.0.0 full public fitting process. This supplies direct evidence that numerical optimizer path sensitivity is affected by the floating kernel (within the tested setup). It does not isolate a unique HGFX implementation defect relative to identical-workflow MATLAB, prove why subject 7 fails the originally accepted `traj.mu/muhat` scientific gate, or justify a reference limitation.

**Still required:** use the exact original MATLAB `traj.mu`/`traj.muhat` reference and compute full trajectory outputs for both environment-controlled HGFX fits, comparing with **unchanged** original tolerances and publishing both non-PASS and passed components. A separately authorized independent reviewer must decide scientific classification and prospective benchmark eligibility. No failed subject may be excluded post hoc, and no old gate threshold may be relaxed. The [Issue #90](https://github.com/ahmadkhanloo/hgfx/issues/90) cross-run bitwise diagnostic portability question also remains OPEN: the original host's effective BLAS mode was not archived, and a general hardware-independent bitwise policy is not yet approved.

**PERF-01C OPEN / NOT FROZEN; original 64-fit 63/64 NON-PASS, 28-case inventory 16 review pending / 12 blocked, six of nine original primary CPU cells ineligible; PERF-01E–H NOT RUN, NO CPU/GPU SPEEDUP CLAIM.**
