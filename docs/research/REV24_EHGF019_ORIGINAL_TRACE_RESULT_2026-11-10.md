# REV-2.4 eHGF-019 — frozen case latent-state diagnostic and source-based numerical hypothesis (2026-11-10)

**Status: ORIGINAL PAIRED TRACE EXECUTED; OFFLINE RECONCILIATION VALIDATED; SCIENTIFIC GATE `NOT_GLOBAL_PASS`.** The historical Panel G 600-vector grid, one one-sided-invalid eHGF row, original manuscript gates, fit/optimizer failures and released HGFX 1.0.0 sources are **NOT MODIFIED**. This document is a new diagnosis of the same original fixed synthetic case, not a reclassification of the original experiment.

## Prospective protocol, original and retry chronology

- Original new preregistered diagnostic [protocol](../../evidence/revision/protocols/REV-2.4_EHGF019_DIAGNOSTIC_PROTOCOL_2026-11-10.md), commit `3322249553e6479cd36cdd638ba9a9f7b6066df8` **before execution**. Original case `REV24-G-ehgf_binary-019`, fixed case SHA-256 `276d21f43a91fc8748438aafc6ec44f759f23dc2ae97dae8b4cc1274aba3fefb`, original full grid artifact `13743694091` whole ZIP SHA-256 `faebd113e9ee050a2490d08e1d1fbc54ba589becd1015d41cab4e7879a785b1c`, fixed original manifest semantic SHA `35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95`.
- Initial [run 42796827923](https://github.com/ahmadkhanloo/hgfx/actions/runs/42796827923) **failure before any new HGFX/MATLAB diagnostic**: source extraction expected three archived files, omitted original `comparison.json`. The failure is retained and documented in [single infrastructure retry policy](../../evidence/revision/protocols/REV-2.4_EHGF019_DIAGNOSTIC_RETRY_2026-11-10.md), source-only tests [42797274300](https://github.com/ahmadkhanloo/hgfx/actions/runs/42797274300) PASS after the inventory-only fix. No vector/data/model change.
- Sole authorized infrastructure retry [run 42797497943](https://github.com/ahmadkhanloo/hgfx/actions/runs/42797497943) at commit `3ddb41283b2f7af8a5183e9e57e6c774942e9070`: **workflow failure at offline JSON comparator after BOTH genuine frozen source MATLAB/HGFX trace functions completed successfully**. MATLAB `jsonencode` flattened 128×3/128×2 cell matrices in column-major order instead of nested rows. The comparator rejected the representation before any verdict, but the **unaltered original numerical traces were uploaded** as [artifact 13754932663](https://github.com/ahmadkhanloo/hgfx/actions/runs/42797497943/artifacts/13754932663), ZIP SHA-256 `a115cc946ddbe3504050e8a1720f50c0a1eb244a89a41a3ed33a9c971ab520e1`. Original `hgfx_trace.json` byte SHA `c346f54572c396a9d9b2ea29e40b726edab1de4152251bfbc1cddf0a3c007ff2`, `matlab_trace.json` byte SHA `9d96afb97ff2a516a2a224c2f52aa7a3c5675e3b0a877fd0c602f0c21a639354`. No third execution authorized; both failure records retained.
- **Offline source-only reconciliation:** [run 42798716279](https://github.com/ahmadkhanloo/hgfx/actions/runs/42798716279) **success**, with 11 synthetic contract tests and independently SHA-verified original 600-grid archive + two saved original diagnostic traces. A pure JSON transport reorientation changed **zero numeric scalars** (MATLAB flat column-major 384/256 entries → trial-major rows), documented by `matlab_json_transport_normalization.numeric_values_modified=false`; no MATLAB/HGFX model code was invoked. [Derived result artifact 13755237519](https://github.com/ahmadkhanloo/hgfx/actions/runs/42798716279/artifacts/13755237519), ZIP SHA-256 `db61cebae88dc5a408e1bf4c8955a13fe1fa0695fdc40d4b658e9497293e58be`, `diagnostic_comparison.json` SHA-256 `0dc6b7db011d79a0b5a7434aaf3311776eab84ae0c800077604d53ac3fe45fa4`. Both source likelihood finite-status sequences reproduce the original Panel G results **exactly**.

## First observed finite-status divergence, original fixed case

All trial numbers zero-based; level indices in raw data zero-based, so level 2 is **HGF level 3**.

| Observable | Earliest trial | MATLAB frozen HGF 8.2.0 | Frozen HGFX 1.0.0 |
| --- | ---: | --- | --- |
| Posterior variance `infStates.sa`, level 3 | **8** | `8.209456713045242` | `NaN` |
| Top-level volatility error `traj.da`, level 3 | **8** | `122704.84065371868` | `NaN` |
| Predicted variance `infStates.sahat`, level 3 | **9** | `12.148302864501495` | `NaN` |
| Trial observation log likelihood | **11** | `-43.96492349971353` | `NaN` |

- Original Panel G first observed likelihood divergence at **11** was downstream of the first **exported latent-state finite-status** asymmetry at **8**. The earliest finite-value difference is merely a trial-0 observation log-probability binary64 difference `4.440892098500626e-16` and is **not** evidence of a causal divergence or a gate failure.
- The original trial-8 level-3 **predicted** variance is the *same* finite `sahat=8.209456713045242` in MATLAB and HGFX. Both export the same finite `mu3=1009.0446083588881`; yet MATLAB final `sa3=sahat3`, while HGFX final `sa3=NaN`. This localizes the likely mismatch to **the eHGF top-level posterior precision correction**, before observing likelihood.

## Strong source-and-state-backed numerical mechanism; NOT a direct instrumented MATLAB intermediate

The pre-existing frozen MATLAB `building_blocks/hgf_volatility_update.m` has eHGF:

```matlab
pi_j = pihat_j + max(0, 1/2 * ka_jm1^2 * ww * (ww + rr * dd));
```

The exact released v1.0.0 Python `src/hgfx/updates/volatility.py` instead has:

```python
pi = pihat + np.maximum(np.float64(0.0), correction)
```

For this original fixed trial-8 state, the frozen transformed full vector has `ka2=exp(0)=1` and `omega2=1.391502762318833`; the **archived** top-level posterior `mu3=1009.0446083588881` implies `ka2*mu3+omega2=1010.4361111212067`, above binary64 `exp` overflow. Thus `vv=Inf`, `pimhat=1/(1/pi_prev2+Inf)=0`, `ww=Inf*0=NaN`, `rr=NaN`, and the precision correction is `NaN`. The original exported MATLAB posterior `pi3=1/sa3=0.12181074033936368` equals its predicted `pihat3=1/sahat3=0.12181074033936368`.

**The key numerical-semantics difference:** MATLAB's `max(0,NaN)` keeps the finite zero, while NumPy's `np.maximum(0.0,np.nan)` propagates `NaN`. NumPy's `np.fmax(0.0,np.nan)` has the MATLAB-like behavior. See official [MathWorks max reference](https://www.mathworks.com/help/matlab/ref/double.max.html) and [MathWorks community's explicit scalar `max(3,NaN)` example](https://www.mathworks.com/matlabcentral/fileexchange/44702-max-and-min-keeping-nans).

**Scientific classification:** `LIKELY_NUMERICAL_MAX_NAN_SEMANTICS_MISMATCH` with strong direct frozen-source/observed-state and algebraic support. This is an **implementation/numerical compatibility candidate**, **not** an intrinsic scientific or model limitation. The specific `vv/ww/rr/correction` terms were **reconstructed from already archived states and the frozen source equations**; they were NOT separately instrumented and logged in MATLAB vs HGFX. An independent, preferably human, review of this causal attribution is required before changing a scientific release gate. Nothing here makes any other eHGF family objective evaluation pass.

## Engineering and publication decisions

- The immutable published HGFX 1.0.0 wheel/source `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and original raw 600 case evidences were **not** modified; a proposed `np.fmax` replacement in a *separately versioned maintenance implementation* must first be protected by an original failure-based golden unit test and broader regressions. No new mathematical gate or scientific rerun is authorized under this diagnostic cap.
- The current external review is by Claude (AI, limited primary data); scientific reviewer/human countersign pending. D02 original HGFX endpoint missing, Panel E raw evidence not independently re-evaluated, eHGF/uHGF original family-specific objective gates remain absent. Original subject-7 trajectory failure, 63/64 cohort fit NONPASS, M18/P3/PERF-01C failures stay unchanged.
- **REV-2.4 global scientific gate remains `NOT_GLOBAL_PASS` and D2/D3 remain BLOCKED.** Scope of any manuscript claim must continue to be restricted to independently verified *same-vector* HGF objectives with exact denominators and original failures disclosed.

