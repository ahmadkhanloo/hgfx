# Published-input fixed-temperature softmax: executed MATLAB8.2/HGFX1.0 evidence

**Date:** 2026-11-04. **Outcome: PASS_BOUNDED_FIXED_VECTOR_RESPONSE_PARITY** under the previously committed [protocol](PUBLISHED_REALDATA_SOFTMAX_PROTOCOL_2026-11-04.md). **Neither original published study fit nor scientific finding was reproduced.**

## Auditable run

- Actual GitHub Action: [#41811411017](https://github.com/ahmadkhanloo/hgfx/actions/runs/41811411017), success, immutable research commit `d84d311394e7e95b86be280068156d9968bd6234`; PR-merge runtime GITHUB_SHA `33c1b005d47097a4f61fc053fe58fd5815b231ee`.
- Reference: real MATLAB **R2025b Update 7**, `25.2.0.3360999`, frozen HGF Toolbox `8.2.0@2437f4dc241541072722a2695ddeca7b44d83dd3`, physically invoked via `matlab-actions/setup-matlab@v3` / `run-command@v3`.
- Test target: installed, non-editable PyPI **hgfx==1.0.0**, JAX **0.10.2**, CPU float64, `JAX_ENABLE_X64=true`.
- Exact public source pin/hash and the corrected subject/block denominator are in the original [324-case protocol](PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_V2_2026-11-04.md), with input bytes downloaded and verified in the ephemeral runner.
- Predeclared three-arm `hgf_ar1_binary_mab` perceptual parameters unchanged from M12B, then both implementations' `softmax` on one-step predictions with **fixed transformed log(beta)=0**. No optimizer, Bayesian parameter recovery, refit, changes to original exclusions or performance tuning.

## Actual aggregate result

| Evidence | Value |
|---|---:|
| Dataset source blocks | **324** (260 Suthaharan, 64 Reed) |
| Original trials | **25,920** |
| MATLAB perceptual executions | 324 successful |
| MATLAB observation executions | **324 successful** |
| Paired B/C complete block results | **324 PASS; 0 FAIL** |
| Observation quantity comparisons | **1,296** (4 per block) |
| Compared numeric elements | **78,084** |
| Failed elements at frozen M7 gate | **0** |
| Maximum absolute error across four quantities | **2.842170943040401×10⁻¹⁴** |
| Numerically ignored source trials | **293** |
| Python cases with captured RuntimeWarning | **48** |
| Threshold inherited from original M7 | **rtol=2×10⁻¹¹; atol=2×10⁻¹³** |
| Local tests performed before running MATLAB | **4 passed** |

The 48 warning-case count and its `RuntimeWarning` type are retained; exact causes have not been independently localized. Passing the paired numerical gate does not imply warning-free software.

The CI's `two-published-source-fixed-softmax-likelihood` artifact is **aggregate only**, with case-level status metadata but no raw participant inputs, individually fitted parameters or per-trial trajectories. The original source MATs and full MATLAB comparison matrices were generated only in CI temporary storage. No published result tables or clinical inference were recreated.

## Essential scope restriction

The published Suthaharan 2021 and Reed 2020 analyses use a **third-level-volatility-dependent softmax response**, not this fixed-beta ordinary `softmax`. This O11 result is independent observation-family compatibility under real data and a fixed parameter vector. The [subsequent preregistered O14 study-family protocol](PUBLISHED_REALDATA_MU3_PROTOCOL_2026-11-04.md) addresses `softmax_mu3` specifically. No future successful result from that protocol may be written here before actually executing it.

**Original-paper fit replication: BLOCKED/OPEN** for older historical HGF version, exact per-participant priors, response model, sequential initialization and optimizer/subject exclusion rules; HGFX1.0 public `fit_model` does not dispatch the MAB+softmax_mu3 workflow. See [source-grounded feasibility audit](PUBLISHED_MODEL_FIT_FEASIBILITY_2026-11-04.md) and [Issue #83](https://github.com/ahmadkhanloo/hgfx/issues/83).

The HGFX 1.0.0 source/tag, failed P3/M18 gates, previously failed 326-case protocol and historical manuscript are unchanged. No journal submission, source redistribution of participant datasets or fee commitment occurred.
