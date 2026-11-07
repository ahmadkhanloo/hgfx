# PERF-01D — genuine 71-source-node HGF infStates and unitsq observation-stage numerical localization (2026-11-07)

**AUTHOR-SIDE REAL ORIGINAL MATLAB + HGFX INTERMEDIATE/SOURCE VALIDATION PASS, NOT SCIENTIFIC FITTING PARITY. ORIGINAL 63/64 SCIENTIFIC NONPASS. INDEPENDENT SCIENTIFIC REVIEW #88 NOT RECEIVED. PERF-01C NOT FROZEN. NO PAPER SPEEDUP/GPU.**

## Original frozen source and pre-observation contract

[Prospective-to-this-diagnostic source-stage prespec](PERF01D_X0_INFSTATES_OBS_STAGE_PRESPEC_2026-11-07.md) committed **before** recording new intermediate `infStates` at SHA **`4d3c8579f84fed71e44c1aedc21398b9a8cdb107`**, stacked on draft PR #97 `b061d8223d0b61c483cc38fabed6f118866d5c69`. Subject 7 and the original 71 first-gradient Ridders positions were **post-result selected**, not eligible as prospective 64-subject scientific parity sample.

Frozen original HGFX v1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, genuine frozen MATLAB HGF Toolbox 8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, original 64 × 128 binary source zero-based subject 7, identical 71 same-x genuine source Ridders node positions and original priors/optimizer options. MATLAB R2026a, single Ubuntu Actions CPU runner, Python 3.11 / NumPy 2.3.5; no actual physical GPU or timing.

Original actual genuine MATLAB private original Ridders callback first-gradient [run 42389292284](https://github.com/ahmadkhanloo/hgfx/actions/runs/42389292284), actual HGFX x/value source SHA `fd8ea94bbf85e6f01feb1d7477ae15a42f86026cc0704503c9e0f00c9803599d`, MATLAB x/value source SHA `1826535a8e15c522bc3c987978c15978e14a5594664fae25d618e6f9f22a4685`. Both genuine original models at all these original x nodes independently reproduced their prior [42402421462](https://github.com/ahmadkhanloo/hgfx/actions/runs/42402421462) original source trial-loglikelihood archive (HGFX SHA `eb085a07e633aa10979602d9f9fb5e9221e2a1132aecd9fb7b73953a4d2850df`; MATLAB SHA `4d9cd77d1187f203a0b467b602d6ab74b4283f2c76476c97d5c8b9e3dc95d0ea`) at **all 71 × 128 trial value bits**, as well as all 71 full original private/objective negative-joint scalars.

Original 64-subject public fitting **63/64 SCIENTIFIC NONPASS** remains, zero-based subject7 original 4 `traj.mu` + 4 `traj.muhat` out-of-original-acceptance-limit source failures. Earlier original 15/16 NONPASS, 28-case PERF-01C (16 review-pending/12 blocked) and all old raw failed experiments retained; no numerical tolerance, seed, model or dataset modifications.

## Actual experiments, including source-correction provenance

1. [Actual **42404323022**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42404323022) at source SHA `d9f5609c55af274fee14d594faf9d01d5c2d83e3`: **SUCCESS**. 14/14 synthetic positive/negative source checks; SHA-256 locked original actual MATLAB/HGFX source evidence; native frozen MATLAB `fitModel` (unmodified), original HGF source `infStates` and `unitsq_sgm` 71×128 each; independent checker requires 71/71 per-engine original source LL vectors and negative-joint bits exact. Original full 128×3×4 HGF states and reciprocal source observation-predictor swaps archived. **Caveat:** HGFX diagnostic `zeta` metadata was calculated with generic `numpy.exp`, not with the native HGFX `matlab_exp_scalar` actually used inside `unitsq_sgm`. The resulting 48/71 zeta-metadata unequal figure is **INVALID AS A NATIVE HGFX-VS-MATLAB ZETA COMPARISON**, even though native original LL and infState comparisons/swap outcomes were validated and remained correct. Preserve this run, do not silently overwrite its evidence. First source ZIP [artifact 13587320212](https://github.com/ahmadkhanloo/hgfx/actions/runs/42404323022/artifacts/13587320212) SHA `9715f8b938b9df651d0207c3b1b113b82ace551d74db9c8366490a77061bf495`.
2. Narrow **diagnostic metadata ONLY** correction at commit **`a6168bb2b1be07a0f084abc07599e9ffda61b22b`**: HGFX `native_zeta` is obtained using the same *frozen HGFX* `matlab_exp_scalar` called inside the native source `unitsq_sgm`; no changes to original model/source logic or existing raw failed cohort. Original source SHA, original 71 points, priors and original reported likelihoods unchanged.
3. **Confirmed real [42404444341](https://github.com/ahmadkhanloo/hgfx/actions/runs/42404444341)** at **`a6168bb2b1be07a0f084abc07599e9ffda61b22b`**: **SUCCESS, 14/14** original source tests, genuine MATLAB native original `fitModel` plus separate original MATLAB `hgf_binary`/ `unitsq_sgm` HGF states, genuine unchanged frozen HGFX code, original 71×128 native LL values all bitwise exactly equal to prior source oracles; independently verifies four 128×3 HGF state components for every original x; records source genuine 2-way observation-swap results. **Correct HGFX/MATLAB native observation zeta values are exactly equal in all 71 / 71 original x nodes.**

### Actual source stage results

| Real original source stage comparison at all 71 original same x | Number of x nodes with at least one binary64 bit difference |
|---|---:|
| Original level-1 HGF selected predictive probability (the actual `unitsq_sgm` input) | **8 / 71** |
| Original level-1 HGF posterior mean (`mu(:,1)`) | **0 / 71** |
| Original full `infStates.muhat` 128 × 3 source matrix | **9 / 71** |
| Original full `infStates.mu` 128 × 3 source matrix | **9 / 71** |
| Original full `infStates.sahat` 128 × 3 source matrix | **16 / 71** |
| Original full `infStates.sa` 128 × 3 source matrix | **16 / 71** |
| NaN-versus-finite pattern mismatch in any source infState component | **0 / 71** |
| Original genuine model observation `zeta` | **0 / 71** |
| **Original native `unitsq_sgm` per-trial log likelihood** | **71 / 71** |
| HGFX observation output when switching only its level-1 predictor HGFX → MATLAB (other source function unchanged) | **7 / 71** |
| MATLAB observation output when switching only its level-1 predictor MATLAB → HGFX | **7 / 71** |
| **Genuine MATLAB `unitsq_sgm` versus genuine HGFX `unitsq_sgm` on the EXACT same HGFX predictor vector and same native zeta** | **71 / 71** |
| **Genuine MATLAB `unitsq_sgm` versus genuine HGFX `unitsq_sgm` on the EXACT same MATLAB predictor vector and same native zeta** | **71 / 71** |

**Interpretation strictly restricted to FIRST Ridders x0 gradient:** original sampled source HGF predictors differ at only 8/71 original x, and the original source observation native zeta values are identical at all 71. But the two original observation implementation outputs differ at **all 71 original same-x nodes even when the actual predictor and actual native zeta are held equal**. Therefore the 71/71 original observed per-trial log-likelihood vector differences **cannot be explained solely by different HGF predictor or original zeta transformation**, and discrepancies exist in original observation numerical evaluation at identical source input values.

This is far more discriminating than the prior 71/71 per-trial differences and 14/71 summed objective discrepancy. However it does **NOT** identify which original source arithmetic operation in `unitsq_sgm` first differs (e.g., `log(x)`, `log1p`, powers, `log` normalizer, order of additions/subtractions, mathematical library rounding), or explain why later BFGS performs 225 extra HGFX indirect objective calls. No source code was patched or used to override the original native fit, and counterfactual cross-input observations are **not** original full-fit objective oracles.

### Raw sources and hashes for confirmed experiment

[**Successful real frozen source artifact 13586443109**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42404444341/artifacts/13586443109), whole ZIP SHA-256 **`4538ecc0ee611074e456c8af1fc31afc72020b8f7bf0ad1af6000680c9c4f1fc`**, actual run **42404444341**, original tested source SHA **`a6168bb2b1be07a0f084abc07599e9ffda61b22b`**:

| Archive member | SHA-256 |
|---|---|
| `original-hgfx-71-infstates-and-native-ll.json` (all 71 original 128 × 3 × 4 HGF source fields and native original LL) | `53c998070dbbfc8b8a5c5ce7e8d962b44f9820635f60c567fd2012bf48fcd415` |
| `original-matlab-71-infstates-and-cross-ll.json` (real frozen MATLAB HGF original source fields, native LL, unitsq on HGFX predictions) | `15c2f3e50d3ff257d333e412b881053cd6bc0240137ddbae448b3ce7d1647006` |
| `independent-hgf-infstates-unitsq-71-source-stage.json` (all source-field and per-trial native/cross numerical comparisons) | `5d1d03f200bb8be7bf058fe54d64e63ab8909a29857a6750014bad83db029af0` |
| `original-hgfx-71-infstates-and-native-ll.sha256` sidecar | `f94d964a53ac26964ef3a962adfdc62611eacda22577e1d706c88f02d72ed84a` |

An independent source-reconstruction test of every same-x original source objective and per-trial trial LL is required and was executed inside the successful same-runner experiment. The new signed independent *scientific reviewer* remains outstanding.

## Scientific and subsequent work classification

**DONE/PASS (author-side software diagnostics):** exact original native HGF+unitsq trial LL 71×128 per engine, exact prior original objective 71 nodes and original SHA, full genuine original `infStates` matrix inventory, 14/14 synthetic source-integrity controls, exact original predictor/zeta comparisons and two-way genuine native observation on swapped predictors at identical frozen x.

**OPEN:** first exact differing original `unitsq_sgm` arithmetic operation on identical predictor and zeta; later optimizer path causality, original failed public subject-7 4+4 trajectories, scientific parity 64/64, generalization to other models/cohort, any performance eligibility or physical GPU evidence. The **next falsifiable focused experiment** is a separately prespecified source-algebra intermediate evaluation of MATLAB `log(x)`, `log1p`, `log(1-x)`, powers and final log-normalizer and corresponding frozen HGFX operations on the *same archived input prediction x and same binary64 zeta*, with exact reproduction of both original native observation per-trial LL vectors before attributing a first stage. Original 71 × 128 denominators remain intact, no threshold changes.

Independent reviewer [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) **NOT RECEIVED**, original PERF-01C 28-cell freeze **NOT FROZEN**, original full fitting **63/64 SCIENTIFIC NONPASS** and 15/16 NONPASS, no paper runtime speedup or physical GPU validation. Draft PR #98 retained. All historical failed engineering/source runs remain immutable.
