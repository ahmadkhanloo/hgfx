# Published-input volatility-dependent softmax_mu3: executed evidence (2026-11-04)

**Outcome: PASS_BOUNDED_MU3_RESPONSE_PARITY**, strictly within the prospectively frozen fixed-vector B/C compatibility scope. **Original published paper participant fits and scientific findings: NOT REPRODUCED.**

## Source, protocol, execution

- [Prospectively frozen protocol](PUBLISHED_REALDATA_MU3_PROTOCOL_2026-11-04.md) was committed at `af092b8661043e8d05b12a770d54277319894168` before the actual scientific run. It inherits **M7 O14 observation numerical criteria** `rtol=2e-11, atol=2e-13`, without post-outcome adjustment.
- [Physical MATLAB/HGFX CI run #41812452107](https://github.com/ahmadkhanloo/hgfx/actions/runs/41812452107), **SUCCESS**, workflow source head `17b14590025ffdfd38402955c2d5af0cb3b0f2aa` (stacked draft PR #85); executing GitHub PR merge SHA reported by the Python process `24dbd51bf38dfbacd4c473407825b8a44f272f80`.
- Frozen HGF Toolbox **8.2.0** from submodule SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`, on genuine MATLAB R2025b via `matlab-actions/setup-matlab@v3` and `run-command@v3`. Python uses PyPI **hgfx==1.0.0**, JAX **0.10.2**, CPU float64/x64. No working-tree modified HGFX model was used.
- Two publication-linked source inputs, verified against pinned file SHA256 hashes and commit IDs, detailed in the [source-defined full-cohort protocol v2](PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_V2_2026-11-04.md): 260 Suthaharan et al. 2021 and 64 Reed et al. 2020 80-trial blocks. The previously incorrect 326-case cohort hypothesis and failed source-gate remain documented.
- Same predeclared M12B 17-element native `hgf_ar1_binary_mab` vector (three arms, uncoupled, regular intervals), identical original 0/1 rewards and 1/2/3 choices, 293 total ignored trials. B/C both use **`softmax_mu3` / O14** with `predorpost=1` and effective temperature from the level-three posterior, not an estimated response-temperature parameter. No fit or response parameter selection was performed.
- The aggregate-only workflow artifact `published-source-original-mu3-family-aggregate` contains status metadata but not downloaded raw participant data, trial-by-trial state arrays or original fit results. The physical MATLAB/Python comparison ran in ephemeral CI storage.

## Executed numerical outcome

| Quantity | Value |
|---|---:|
| Source-defined blocks attempted | **324 / 324** |
| Source trials | **25,920** |
| MATLAB original-family response blocks | **324 / 324 succeeded** |
| Matched MATLAB/HGFX blocks within O14 gate | **324 / 324** |
| Quantities compared per block | 4 (`logp`, `yhat`, `res`, block total log likelihood) |
| Comparisons | **1,296** |
| Numeric elements compared | **78,084** |
| Failing elements | **0** |
| Maximum absolute error | **4.263256414560601e-14** |
| Frozen threshold | `rtol=2e-11; atol=2e-13` |
| Source trials skipped in response calculation | **293** |
| Blocks with captured Python RuntimeWarning | **48** |
| Warning classes reported | `RuntimeWarning` |

A warning occurrence is not asserted to be a numerical mismatch or ignored: its precise root cause and implications remain OPEN. Full original study fits, different parameter vectors, optimizer equivalence, model-selection agreement, identifiability, clinical associations, forecasting and general superiority were **not tested**.

## Interpretation and remaining gates

This run establishes real-data **B/C fixed-vector numerical equivalence of the frozen `softmax_mu3` observation equation**, jointly with the prior 324-case perceptual-forward evidence. This is a more representative study-model family than the independent [ordinary fixed-beta softmax test](REALDATA_SOFTMAX_PARITY_RESULT_2026-11-04.md), but it is **not proof that the original papers' HGF5.3.1 `softmax-mu03` model/fit is mathematically identical to the frozen 8.2.0 model**. The original reference version/likelihood/config chain must be traced independently, including temporal-state choice and any original MATLAB function differences.

Original Suthaharan/Reed historical fit reproduction remains **BLOCKED** on HGF5.3.1 source identities, complete study-specific priors/response configuration, sequential-half initialization, optimizer starts, original exclusions, and missing HGFX1.0 end-to-end MAB-fitting dispatch. See [fitting feasibility audit](PUBLISHED_MODEL_FIT_FEASIBILITY_2026-11-04.md), [Issue #83](https://github.com/ahmadkhanloo/hgfx/issues/83) and the original article sources.

**No historical result, P3/M18 scientific gate, dataset, parameter seed, tolerance, source version, manuscript or compiled PDF was altered.** This is a new scoped test on an additive research branch; no manuscript-success or published-result replication claim is authorized without a new independent review and proper journal package rebuild.
