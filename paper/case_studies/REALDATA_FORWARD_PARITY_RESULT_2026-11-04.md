# Published real-data forward compatibility: executed evidence (2026-11-04)

**Result: PASS — on the narrowly defined fixed-parameter MATLAB8.2 ↔ HGFX1.0 forward-equivalence criterion.** **Original papers' model fits and scientific results: NOT REPRODUCED.**

## Predeclared protocol and correction (historical evidence retained)

- [Initial pilot protocol](PUBLISHED_REALDATA_PAIR_PROTOCOL_2026-11-04.md) locked native model family, parameter vector, input coding and tolerances before results.
- [Original 326-case full-source hypothesis](PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_2026-11-04.md) failed **before scientific model execution**: [source-gate run 41809479255](https://github.com/ahmadkhanloo/hgfx/actions/runs/41809479255). The 33rd Reed “person” was actually MATLAB workspace variable `ans`, not a participant.
- [Version 2 corrected full-source population](PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_V2_2026-11-04.md), recorded before the full scientific run: **130 Suthaharan people × 2 blocks = 260, 32 Reed people × 2 blocks = 64; total 324 source blocks, 25,920 trials**. This is explicit source-schema correction, not selection according to scientific outcome. The old failed run and 326-case plan are not overwritten.

## Sources independently retrieved and hashed

- Suthaharan et al. (2021), *Paranoia and belief updating during the COVID-19 crisis*, DOI `10.1038/s41562-021-01176-8`. `psuthaharan/covid19paranoia@c618e032228fb4ed03821f11bdc57af608695631`, `data/hgfPRL/pandemic_prelockdown_TP117_TP261_130.mat`, SHA256 `9c3e81cc4533b49dfa993f1f885678f1a541dd2f31d6738e6e845bb2e7834428`.
- Reed et al. (2020), *Paranoia as a deficit in non-social belief updating*, DOI `10.7554/eLife.56345`. `ModelDBRepository/258631@39ccaca508b81ca610e7666a613e061c801faaf9`, `IRL_Data.mat`, SHA256 `b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708`.

Only these **two source MAT files** were evaluated, not every published dataset or the original studies' subject exclusions. Neither raw participant data nor per-trial reconstructed trajectories were uploaded; source downloaded to ephemeral CI disk only.

## Actual physical MATLAB and released-wheel execution

- [Passing run #41809919116](https://github.com/ahmadkhanloo/hgfx/actions/runs/41809919116), workflow branch head `e09f72020dbab52f2d73b90ff4d9ee40999b9fae`. PR merge checkout `GITHUB_SHA=5d9142f903acce414657a35c78f626ebf0331310`.
- Genuine MATLAB **R2025b Update 7** `25.2.0.3360999`; pinned `external/hgf-toolbox/perceptual/hgf_ar1_binary_mab.m` at Toolbox 8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Real PyPI **hgfx==1.0.0**, not editable development source; Python 3.11.18, JAX/JAXLIB 0.10.2, NumPy 2.2.6, SciPy 1.14.1, CPU float64.
- Frozen HGF `hgf_ar1_binary_mab`, three arms, uncoupled, regular intervals. Native parameter vector (unchanged from `tools/check_m12bc_parity.py`):
  `[NaN, 0, 1, NaN, .1, 1, NaN, 0, .2, NaN, 0, 1, 1, 1, NaN, -2, -6]`.
- Predeclared inherited numeric gate: `rtol=2e-9`, `atol=2e-11`, matching nonfinite values and masks, all 12 fields per block.

## Complete source-population results

| Quantity | Observed |
|---|---:|
| Matched published-input trial blocks | **324 / 324** |
| Original trials | **25,920** |
| MATLAB real successful forward executions | **324; 0 failed** |
| HGFX numeric-gate successful executions | **324; 0 failed** |
| Fields (12 per block, including `infStates`) | **3,888** |
| Numeric elements compared | **2,540,160** |
| Elements outside frozen tolerance | **0** |
| Maximum absolute difference | **3.1086244689504383e-15** |
| Maximum relative difference (descriptive only) | **5.603239773513641e-11** |
| Cases with Python runtime warnings | **48 / 324** |

**Warnings are not silently ignored.** Warning type/causal audit remains OPEN; their presence does not change the reported numerical result, but complete diagnostics are not certified.

The associated GitHub Actions upload `two-published-study-fullcohort-aggregate-parity` contains aggregate/per-case *status* only, not observed values or per-trial posterior arrays. [First actual 80-trial pilot #41808999660](https://github.com/ahmadkhanloo/hgfx/actions/runs/41808999660) separately PASSed both prespecified first blocks.

## Strict scientific boundary

**Proven:** at this one preselected 17-element native vector and same actual published stimulus/choice sequences, the frozen MATLAB 8.2 and HGFX1.0 recursive perceptual outputs match at binary64 rounding scale across the two source-defined datasets. This extends software-compatibility evidence beyond synthetic cases.

**Not proven:** replication of the **original papers**, which used older HGF releases and study-specific observation models, parameter priors, fits, restarts, original cohort exclusions, published group-level statistics and hypothesis tests. No original paper fitting or model-comparison workflow was executed. No claim that HGFX is more accurate, faster, more identifiable or scientifically superior follows from these results.

**Publication handling:** Do not claim “two papers reproduced”; if used, describe this as *real published-input, frozen-parameter forward compatibility* and disclose the scope, warning count, source and numeric gate. The existing frozen manuscript and compiled paper were **not modified**; editorial insertion and review remain separate.

## Next required work for actual published-result replication

Obtain original reproducible MATLAB/HGF versions, precise perceptual+observation models, fit priors, starts/optimizer and original grouping/exclusions. Lock each full analysis protocol **before fitting**. Compare original historical fit (A), frozen MATLAB8.2 (B) and HGFX1.0 (C), without tuning model family or suppressing failed subjects. If A cannot be reproduced, B/C must be labeled a new ported analysis and cannot validate original paper results.
