# PERF-01D: original subject-7 native optimizer termination (2026-11-06)

**Status: AUTHOR-SIDE SOURCE-NATIVE TERMINATION REPRODUCED. Original all-64 public fitting remains 63/64 SCIENTIFIC NON-PASS. Independent PERF-01C review NOT APPROVED. No timing.**

## Question and immutable sources

The original 101-record optimizer buffer holds 25 populated values, with overwritten duplicated terminal slots. The archive alone could not establish the MATLAB termination reason. This experiment asks for the **actual source-native stop category** without modifying the frozen reference optimizer or changing numerical settings.

- Original MATLAB HGF Toolbox 8.2.0 source SHA **2437f4dc241541072722a2695ddeca7b44d83dd3**, MATLAB R2026a, unchanged public fitModel, quasinewton_optim and original optimization config.
- Original HGFX v1.0.0 SHA **4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27**, unchanged public fit_model and exposed frozen compatible quasinewton_optim.
- Original model **hgf_binary + unitsq_sgm**; original zero-based subject **7**, same 128 binary trials, prior, mask and transformed 15-vector start. Free parameter indices 12,13,14; **tolArg=tolGrad=1e-3**, maxStep=1, maxIter=100, maxRegu=16, maxRst=10, nRandInit=0, Ridders min_steps=10.
- Full original 64-subject fitting [CI 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), summary and both raw SHA256 verified before the new fitting. The historical result **63/64** and subject-7 failed full trajectory fields **mu and muhat** remain unchanged; no tolerance, seed, subject, data or source substitution.

## Source-native diagnostic and safeguards

1. MATLAB public fitModel is executed **twice in the SAME MATLAB session** with the same original source/data/config. The ONLY changed option is the frozen official optimizer verbose flag (false vs true). All original numerical outputs, optimizer full iter history and **all 11 HGF trialwise fields** must match **exactly using isequaln** before a termination category is accepted. The one source-native log event is parsed strictly: either gradient, argument, max-iteration or max-reset stop.
2. Frozen HGFX public fit_model is evaluated with the original configuration; its original 3-free-coordinate objective is passed to the original exposed compatible quasinewton_optim. The direct optimizer's reported stop reason is accepted only when its arg_min, entire 101-entry iter.x and iter.val buffers **exactly reproduce** those of the original public fit in the same process.
3. The original MATLAB public baseline is compared to original archived MATLAB full-fit output for **all 28 original numerical/trajectory fields** with unchanged original acceptance tolerances; this cross-run calculation is explicitly diagnostic.
4. The two original SHA256 hashes remain checked exactly. MATLAB JSON changes struct field names containing a dot, so the comparator normalizes **only the two original known raw-file hash keys**. Unknown or altered hashes fail closed.
5. Scientific fitting classification remains independent of any source-native stop label.

## Verified execution and results

[Successful complete CI **42232378487**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42232378487) executed exact diagnostic SHA **6351160b2b528a9db894e873ce65677ee847bbe5**, **19/19 focused tests** (12 new negative/positive controls and 7 original cohort tests). The original MATLAB+HGFX raw fitting SHA256 and full source SHAs were verified before fitting. Both calculations are **untimed**.

| Original-source observation | MATLAB 8.2.0 | HGFX v1.0.0 |
|---|---|---|
| **Source-native stop reason** | **tol_grad** (original message: Converged on gradient size) | **tol_grad** (frozen QuasiNewtonResult.termination) |
| Internal numerical control | Entire public normal-vs-verbose result **exactly equal**, all optimizer and 11 trajectory fields | Direct source optimizer **exact** to same-run public fit: arg_min, iter.x and iter.val |
| Original populated history | 25 of 101 allocated | 25 of 101 allocated |
| Actual source-reported iterations | Not a separate MATLAB scalar; original MATLAB console and full buffers retained | **24** |
| Source-reported resets | Original source history has none | **0** |
| New MATLAB default vs old original MATLAB, 28 fields | **ZERO outside existing tolerances** | Not a replacement for paired full-fitting scientific gate |

Full new raw SHA256:
- HGFX raw: **71867c75c84de0e919e195a0f5124726c8352bfcfac233f9ac8cd6fe7e75d3c3**
- MATLAB raw: **c16736a221758d39b4ccef45a217798a3661dd6c78b75fec0d6f7f19869cbf48**

Permanent machine-readable evidence: [derived-native-termination-42232378487.json](../../benchmarks/runtime_v1/issue90_results/derived-native-termination-42232378487.json), bot evidence SHA **d908f32132103b20f5c01f41fb866835ad71c0bb**. Full individual new MATLAB normal/verbose source output and diagnostic logs, HGFX direct public/optimizer trace and raw-source checksums are retained in the CI artifact.

### Historical failed diagnostic attempts retained

- [42230730748](https://github.com/ahmadkhanloo/hgfx/actions/runs/42230730748): **FAILURE before computations** due synthetic fixture aliasing and a test-status substring assertion. Both tests fixed.
- [42230878876](https://github.com/ahmadkhanloo/hgfx/actions/runs/42230878876): **FAILURE after HGFX numerical evaluation** when serializing an unsupported MatlabStruct wrapper; fixed only diagnostic JSON value extraction.
- [42231172777](https://github.com/ahmadkhanloo/hgfx/actions/runs/42231172777): **FAILURE in new MATLAB start-identity check** due row/column JSON decoding. Corrected to the original previously tested column-normalized equality, no numerical values changed.
- [42231735347](https://github.com/ahmadkhanloo/hgfx/actions/runs/42231735347): **FAILURE after both MATLAB and HGFX real calculations** from MATLAB JSON struct field normalization; two raw sources and original equal-status MATLAB log preserved. Strict two-key normalization and explicit SHA-tampering negative control added.

These failed runs must never be hidden or interpreted as scientific fit failures or scientific passes.

## Interpretation and unchanged scientific gate

**Supported:** Both unchanged source-compatible optimizers stop through **the SAME gradient-size criterion**, not different categories of convergence. Thus difference in *termination type* is not an explanation for the original two fitted endpoints, although floating-point gradient values or execution paths can still differ. MATLAB normal-vs-verbose is numerically exactly identical; no instrumentation of frozen optimizer source was required.

**Not supported:** equality of the exact final gradients, exact floating-point optimizer operations, global identifiability, matching full-scientific fitting trajectories, declaration of MATLAB limitation, or retrospective acceptance. The original full public fit remains **63/64 NON-PASS** with subject 7 having four original failing mu and four failing muhat coordinates. Original 28 prospective runtime cells **16 independent-review pending / 12 blocked**, six of nine primary CPU cells ineligible. [Independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88) remains OPEN, [original scientific mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89) remains OPEN, [BLAS portability #90](https://github.com/ahmadkhanloo/hgfx/issues/90) remains OPEN. **PERF-01C NOT FROZEN, PERF-01E-H NOT RUN, NO CPU/GPU SPEEDUP CLAIM.**

An independent reviewer must compare the exact original full-source objective, gradient and optimizer numerical path and scientific data before issuing any explicit signed prospective benchmark gate decision. A common source-native stop **name** alone does not imply full scientific parity.
