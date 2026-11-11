# PERF-01D / Issue #90 — OpenBLAS ULP dispatch isolation on one runner (2026-11-06)

**Status: engineering numerical mechanism demonstrated for archived *auxiliary scalar diagnostics* only; Issue #90 OPEN for general cross-host replay. Original 63/64 public fitting scientific result NON-PASS. No timing.**

## Source preservation

- Original unmodified full-public subject-7 fitting/BFGS source archive: [GitHub Actions 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), exact tested diagnostics code SHA `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d`; MATLAB R2026a HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`, HGFX 1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Original HGFX BFGS raw SHA-256 `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`; MATLAB BFGS raw SHA-256 `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`. These source checks are enforced in each run.
- The original `summary.json` and `comparison.json` must be *exactly equal as parsed JSON* after excluding only original GitHub execution metadata; **no old scientific or norm fields were rewritten**. Other previous failed strict cross-host bitwise replays [42194275053](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194275053) and [42194481974](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194481974) remain preserved. The original strict comparator is still unchanged.
- This experiment uses only saved original 24 populated 3×3 `T` inverse Hessians and Ridders gradients at original parameter states per engine. It computes 48 saved-state direction norms and 48 gradient-dot-direction slopes. It is not a new fit or timing experiment.

## A. Across three runner configurations

[CI 42197170335](https://github.com/ahmadkhanloo/hgfx/actions/runs/42197170335), code SHA `7e47d3705ae754870e7412d7e9a8af7be5ec8606`: **SUCCESS on Linux automatic, Linux Haswell, Windows automatic**; 12/12 structural tests on each.

| Configuration | Effective OpenBLAS path | Scalar norm archived-bit mismatches /48 | Gradient slope mismatches /48 | Maximum scalar discrepancy |
|---|---|---:|---:|---|
| Linux auto, AMD EPYC 9V74 80-core | SkylakeX | 3 | 13 | 1 binary64 ULP |
| Linux `OPENBLAS_CORETYPE=Haswell`, AMD EPYC 9V45 96-core | Haswell | 0 | 0 | 0 |
| Windows auto | SkylakeX | 3 | 13 | 1 binary64 ULP |

All use NumPy `2.3.5`, OpenBLAS `0.3.30`, 4 reported OpenBLAS threads, exact same raw artifact bytes and frozen scientific configuration. These three parallel CI jobs occupied **different physical runners**, so the data alone do not isolate the dispatch effect from host differences.

## B. Controlled three-process rerun on **one physical runner**

[CI **42197971370**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42197971370), tested code SHA `71512913cd3ef597e824f1855ac6185634a1491d`: **SUCCESS**, `12+10=22` unit/negative-control tests. Three **separate Python processes on the same GitHub-hosted Linux runner and CPU** consumed identical SHA-256-verified archived data, with only `OPENBLAS_CORETYPE` changed.

**Fixed host:** AMD EPYC 9V74 80-Core Processor, Linux `7.0.0-1017-azure`, NumPy `2.3.5`, OpenBLAS `0.3.30`; exact GitHub run ID `42197971370`.

| Configuration on this identical host | Effective OpenBLAS | Norm mismatches /48 | Slope mismatches /48 |
|---|---|---:|---:|
| `OPENBLAS_CORETYPE` unset | SkylakeX | 3 | 13 |
| `OPENBLAS_CORETYPE=Haswell` | Haswell | **0** | **0** |
| `OPENBLAS_CORETYPE=SkylakeX` | SkylakeX | 3 | 13 |

- In **all 48 source states**, automatic selection and explicitly selected SkylakeX had **identical binary64 bits** for both scalars (96/96).
- Automatic/SkylakeX versus Haswell differed in precisely **3/48 norms** and **13/48 slopes**, at most **one ULP** relative to the historic values.
- Haswell reproduced **96/96 historic archived scalar values exactly**; this is verified with integer binary64 bit patterns, not a relaxed tolerance.
- The result establishes **within-runner OpenBLAS dispatched-kernel selection as the driver of this bounded arithmetic discrepancy**. It does **not** prove which BLAS kernel the original 42187240378 host used, because that run did not record the effective dispatch mode.
- Before the fix, [run 42197877083](https://github.com/ahmadkhanloo/hgfx/actions/runs/42197877083) **FAILED without jobs** due to an unquoted YAML colon in a step name. The YAML quoting change preserved data, tests, parameters, thresholds and historical failures.

**Permanent machine-readable evidence:** [`benchmarks/runtime_v1/issue90_results/derived-same-runner-42197971370.json`](../../benchmarks/runtime_v1/issue90_results/derived-same-runner-42197971370.json), committed automatically at `2c075f7f62c98020d33673122af0fc3636fe3412`. Test source: [`tests/test_perf01_host_binary64.py`](../../tests/test_perf01_host_binary64.py) + [`tests/test_perf01_same_host_dispatch.py`](../../tests/test_perf01_same_host_dispatch.py); audit and comparator scripts under `benchmarks/runtime_v1/`; three source-verified raw reports are retained as a separate GitHub artifact for CI 42197971370.

## C. Scientific limitations, next narrow test and gate

The dispatched-kernel effect above concerns *post-hoc algebraic derived scalar diagnostics*, not a rerun of full public fitting. In particular, matching the older archived diagnostic slope/norm with Haswell does **not** establish that a MATLAB HGF fitting reference and a frozen HGFX optimizer return identical fitted parameters/trajectories or termination state.

Next bounded **untimed** diagnostic: use exactly frozen HGFX v1.0.0 subject-7 full public fitting, unchanged inputs, release, model and optimizer, on a **single runner** in both BLAS modes; preserve complete outputs/lineage and quantify differences without treating this as a new eligible scientific sample. A direct comparison against MATLAB's matching original fit parameters/trajectory, with identically frozen protocols and independent adjudication, would still be needed for scientific acceptance.

**Original full 64-fit scientific result remains 63/64**, subject 7 `traj.mu` and `traj.muhat` mismatch, first-16 15/16. Original eligibility sample counts 28 total (16 review pending, 12 blocked), six of original nine primary CPU workloads ineligible. No tolerance/seed/dataset/prior/model/workflow was relaxed; no historical evidence hidden; no new performance numbers were collected. **PERF-01C OPEN / NOT FROZEN; PERF-01E–H NOT EXECUTED; NO SPEEDUP CLAIM; independent review #88 OPEN.** Issue #90 remains OPEN pending a documented cross-host reproducibility policy and scientific-review-approved criteria, not merely matching old scalar bytes under one dispatch mode.
