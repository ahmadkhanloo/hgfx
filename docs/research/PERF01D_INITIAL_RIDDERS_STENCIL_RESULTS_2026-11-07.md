# PERF-01D — genuine first Ridders source x±h and bidirectional same-x HGFX/MATLAB objective observations (2026-11-07)

**AUTHOR-SIDE ACTUAL MATLAB + FROZEN HGFX EXECUTION SUCCESS, INDEPENDENTLY REPLAYABLE RAW ARTIFACTS. NOT A NEW SCIENTIFIC ACCEPTANCE GATE. ORIGINAL 63/64 SCIENTIFIC NONPASS, INDEPENDENT REVIEW #88 NOT RECEIVED, PERF-01C NOT FROZEN, NO PAPER TIME/SPEED OR GPU.**

## Pre-execution protocol and exact reference

[Source experiment protocol](PERF01D_INITIAL_RIDDERS_STENCIL_PRESPEC_2026-11-07.md) committed **before** new first-gradient node observations, SHA **`39fc6bd63c40f7b48ceec572a2d2bdf6e7ac537d`**. Zero-based subject 7 was deliberately chosen **after** the original fitting mismatch and earlier 8/11/3 ULP optimizer first-trial observation; not a prospective scientific parity sample.

- Frozen original HGFX v1.0.0 Git SHA **`4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`** and MATLAB HGF Toolbox v8.2.0 Git SHA **`2437f4dc241541072722a2695ddeca7b44d83dd3`**. Actual MATLAB R2026a, GitHub Actions Ubuntu 24.04 runner, Python 3.11, NumPy 2.3.5, no physical GPU.
- Same **original `hgf_binary` + `unitsq_sgm`** full public fitting objective, original 64-by-128 binary data, subject 7, 128 trials, transformed free indices `[12,13,14]`, free start **`[-3,-6,3.871201010907891]`**, unchanged free/fixed priors. Original `riddersgradient(f,x,struct('min_steps',10))` against genuine nested MATLAB `fitModel` private objective and untouched original HGFX `ridders_gradient(...,RiddersOptions(min_steps=10))`. Original Ridders defaults `init_h=1`, `div=1.2`, `max_steps=100`, `tf=2`; original `riddersdiff` source not modified.
- Original 64-subject public [source 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) remains **63/64 SCIENTIFIC NONPASS**, with **4 `traj.mu` plus 4 `traj.muhat`** failed entries for subject 7 at unchanged published science tolerance. Original 15/16 failed result, 28 PERF-01C workload cells and all earlier raw failures unchanged. Original [BFGS archive 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378): `hgfx_raw.json` SHA `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`; `matlab_raw.json` SHA `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.

## Engineering execution history, including failed diagnostic tests

1. [Workflow 42389200581](https://github.com/ahmadkhanloo/hgfx/actions/runs/42389200581) at `fb4fd1d9ac63b99c7e1d6dbc464316e314553a7c`: **FAILED before Python source first-gradient invocation or MATLAB**; two synthetic test-fixture problems (NumPy scalar type used instead of a JSON Python float; a negative test expected missing MAT before the missing original scientific preflight). Existing 12 other synthetic checks passed; no raw scientific source changed. Fixed **only tests** at `4ab5f42754b1200433d9b7dc6832e1ee7c45be8f`. Failed run/log remains preserved.
2. [Real same-runner workflow **42389292284**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42389292284) at **`4ab5f42754b1200433d9b7dc6832e1ee7c45be8f`**: **SUCCESS**, 14/14 synthetic fail-closed stencil-order/sign/source tests; both original source Git SHA and BFGS member SHA checks; real original frozen HGFX `ridders_gradient` at x0 with its actual free-objective values; genuine original MATLAB private nested `fitModel` objective at same x0 with its actual `riddersgradient` stencil; MATLAB private objective was also evaluated at every HGFX stencil x, and frozen HGFX objective at every actual MATLAB stencil x; all reported fields retained. Same MATLAB runner native and delegated public fits had **26/26 original stable public fields and the entire `optim.iter` exact equal**, independently read from real raw MAT-v7 by separately coded Python SciPy; 25 finite original optimizer history rows preserved, original 63/64 SCIENTIFIC NONPASS unchanged. No timer.
3. [Archive-only independent replay **42389872139**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42389872139) at `912fca482e378528f1c4ba70556466bf2fbaee59`: **SUCCESS**, **12/12** synthetic positive and negative controls, all five real original file member SHA-256 checks, independent byte-exact matching of source-grid x points and objective values with previously validated true same-x cross-comparison JSON. Original scientific NONPASS checked. No new HGFX or MATLAB fit; original source members unmodified.

## Actual first Ridders gradient and raw source evidence

| Exactly same 3-D free start `[-3,-6,3.871201010907891]` | HGFX frozen objective | Genuine MATLAB nested private objective |
|---|---:|---:|
| Actual first-gradient source total objective evaluations | **71** | **71** |
| Ridders observed x±h step pairs for coordinates 0,1,2 | **[11,11,13]** | **[11,11,13]** |
| Gradient coordinate 0 | `420.3828348417702` | `420.38283484176924` |
| Gradient coordinate 1 | `0.10523987386444607` | `0.10523987385121879` |
| Gradient coordinate 2 | `1386.6296379643848` | `1386.6296379644` |
| Absolute coordinate-0 gradient difference | \multicolumn{2}{c}{`9.663381206337363e-13`} |
| Absolute coordinate-1 gradient difference | \multicolumn{2}{c}{`1.3227280382110962e-11`} |
| Absolute coordinate-2 gradient difference | \multicolumn{2}{c}{`1.5234036254696548e-11`} |

The 71 objective evaluations consist of **one original center `f(x0)` evaluation** and **70 ordered ± stencil evaluations**. A separate archive replay verified all **70/70 matched source positive/negative coordinate vectors bitwise identical across MATLAB and HGFX**, as well as the identical center vector. Thus **this first-gradient discrepancy cannot be attributed to choosing different finite-difference x±h coordinates or different counts of Ridders steps** in this comparison.

Direct same-x scalar comparisons were performed *bidirectionally* — MATLAB's genuine private objective on **all 71 actual HGFX x samples**, and frozen HGFX `evaluate_free` on **all 71 genuine MATLAB x samples**. Both original grids are bitwise identical, and the two independently recorded comparisons agree:

| Genuine same-x source objective comparison | Original HGFX-grid evaluations | Original MATLAB-grid evaluations |
|---|---:|---:|
| Objective values **binary64 identical** | **57/71** | **57/71** |
| Objective values binary64 nonidentical | **14/71** | **14/71** |
| Maximum same-x scalar absolute difference | `4.547473508864641e-13` | `4.547473508864641e-13` |
| Maximum same-x scalar discrepancy in ULP | **2 ULP** | **2 ULP** |

These 14 same-x scalar mismatches are source observations, **not** an implementation-correctness PASS/FAIL threshold; no new numerical tolerance was introduced. A distinct raw failed subject **x6** counterexample from the original 50-anchor experiment has much larger same-x Ridders gradient discrepancy (`6.884955006114524e-08`) and remains archived separately. This first-gradient result must not be generalized to the entire 25-step BFGS trajectory or used to reclassify x6.

The prior true same-runner full fitting trace [42387244467](https://github.com/ahmadkhanloo/hgfx/actions/runs/42387244467) observed **2,163 total objective calls in HGFX versus 1,938 MATLAB** (both 1 initial + 24 direct source line-search and zero direct source reset; HGFX 2,138 indirect vs MATLAB 1,913). The Ridders first-gradient source call count here is **identical (71/71)**, so the additional 225 indirect objective calls in the entire prior public fit **cannot be explained by the first-gradient call count alone**. Cause(s) of later per-coordinate Ridders stopping, different source-path gradients, and potential source-overhead classifications remain **UNRESOLVED**.

## Immutable artifacts, verifiable individual SHA-256

[**Real private-MATLAB + HGFX source artifact 13580303409**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42389292284/artifacts/13580303409), complete ZIP SHA-256 **`99a00582ab9fe3f52546b105490f609de4299fd0177ed4afdae456f18c4c23f1`**:

| Archive member | SHA-256 |
|---|---|
| `hgfx-first-ridders.json` (all HGFX first actual gradient node x/value, source errors and metadata) | `fd8ea94bbf85e6f01feb1d7477ae15a42f86026cc0704503c9e0f00c9803599d` |
| `matlab-first-private-ridders.json` (genuine private nested source nodes/values, true Ridders gradient/error, all HGFX source-node cross-values) | `1826535a8e15c522bc3c987978c15978e14a5594664fae25d618e6f9f22a4685` |
| `matlab-first-ridders-native-and-wrapped.mat` (actual native/diagnostic MATLAB public 26 values and full `iter` on both sides) | `6a4c30ccd4e9088fa373c5474522854972dd6bfcd15b577643f483e43d345ae4` |
| `true-x0-both-stencils-cross-objective-audit.json` (all both-grid same-x actual scalar pairs) | `13c2b32d10fbb508a651c954c13de3c674c5f06ae6a2bb1e641c710ec8abd0c6` |
| `independent-matlab-26-fields-and-full-iter.json` (actual separately parsed raw MATLAB neutrality) | `8c39b3f6709c76e805534bbe4ffd040bdc17251c1aa47d517f97763b195649d4` |

[**Archived original-grid ULP audit artifact 13580738767**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42389872139/artifacts/13580738767), complete ZIP SHA-256 **`75ad9dbf3b69005c6cc26b09869ff0b6e5bbe2f522b77101a3093462fe2f9718`**. Derived `independent-original-stencils-grid-and-same-x-ulps.json` SHA-256 **`1bfa7dc78c5878d8b441d6d0d6b551d9f0bb2b214c8892fc46685b45d63a37ff`**. Full 70-row source grid pair inventory with exact binary64 matching, all real unequal nodes and original status flags retained.

## Scientific classification and next falsifiable work

**Author-side engineering DONE/PASS:** identical original 71/71 Ridders first-gradient call counts, per-coordinate [11,11,13] stop lengths, exact original same x0 and all ±h source-grid coordinates, independent raw 26+complete `iter` MATLAB neutrality, bidirectional same-x 57/71 objective scalar bit equality with 14 mismatches (max 2 ULP), original full public scientific NONPASS preserved.

**NOT established:** whether the 14 scalar 1–2 ULP changes **alone** account for the three Ridders gradient output differences, the exact source-internal Richardson best-index selection/stop `if` outcomes, why subsequent full-fitting Ridders calls differ in total, exact BFGS branch parity or scientific limitation, accepted 64/64 fit parity. The next narrower post-result (prospectively recorded before new analysis) step is to independently replay **all triangular Ridders Richardson interpolation** steps from these authentic 71 scalar-value pairs at the same exact x nodes, retaining per-coordinate best-index, error updates, source stop condition at observed step count, and exact residuals to both original source outputs. Do NOT substitute extrapolated results for the original MATLAB gradient oracle or adjust Ridders stopping thresholds to achieve a desired match.

Issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) **independent reviewer verdict NOT RECEIVED** (no signed `BLOCK_FREEZE` or `APPROVE_PROSPECTIVE_FREEZE`). PERF-01C 28-case prospective freeze **BLOCKED/NOT FROZEN**. Original scientific fitting **63/64 NONPASS**, issue [#89](https://github.com/ahmadkhanloo/hgfx/issues/89), host issue [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) open. Paper speedup, physical GPU validation and scientific reference-limitation disposition: **NOT RUN/NOT ADJUDICATED**.
