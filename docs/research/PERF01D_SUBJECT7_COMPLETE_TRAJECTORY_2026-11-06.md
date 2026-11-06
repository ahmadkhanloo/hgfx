# PERF-01D — original subject-7 complete fitted trajectory, unchanged scientific tolerances (2026-11-06)

**AUTHOR-SIDE UNTIMED SCIENTIFIC DIAGNOSTIC ONLY. Original all-64 full public fitting 63/64 NON-PASS is preserved. No independent adjudication or speedup.**

Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87); [subject-7 scientific mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89); [independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88); [OpenBLAS portability #90](https://github.com/ahmadkhanloo/hgfx/issues/90).

## Exactly frozen source and original reference

- HGFX **1.0.0** frozen public `fit_model` code checkout SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; untouched HGF Toolbox **8.2.0** MATLAB R2026a `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Original reference cohort, **64 subjects × 128 binary trials**, unchanged `hgf_binary` + `unitsq_sgm`, exactly original subject zero-based **7**, original priors/config/start, zero randomized initializations. Complete archived original MATLAB and HGFX cases restored from [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), exact 64-subject summary tracked under `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json`.
- The original full-cohort raw checksums, **63 within original tolerances / 1 numerical-or-trajectory mismatch**, and subject-7 mismatched fields `traj.mu` and `traj.muhat` were **verified before** the new two-mode fitting. Archived original raw SHA256: HGFX `6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb`, MATLAB `2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98`.
- Comparison code reuses the **unchanged** `compare_fits.TOLS` and trialwise `rtol=3e-8`, `atol=3e-10` from `compare_fit_cohort.py`, with all original **28** fields (`optim` without double-counted `decompLME`, all 3 decomposition fields, and all 11 trialwise fields). No tolerance, sample, seed, configuration or performance-workflow change.
- First stage of verification recomputed the original full subject-7 field counts and mismatch indices directly from original raw files, and compared every field status, first mismatch index, original tolerance and mismatch count against the unchanged historical 64-case summary, failing if anything changed. All original four mismatches in each of `mu` and `muhat` remain.

## Actual CI provenance, environment and raw outputs

- [**CI 42203036203**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42203036203): **SUCCESS**, exact diagnostic source SHA `c4d858bcdc090ff6590d99ca7f9c6f9609d1884a`, **12 new structural tests + 7 original all-64 source-comparator tests = 19/19**, full canonical input/config preflight.
- Two new *complete frozen public HGFX fitting* runs in separate Python processes on **one CPU runner**: default OpenBLAS auto (effective SkylakeX) and `OPENBLAS_CORETYPE=Haswell`. Frozen HGFX v1.0.0, identical input, original initial parameters, no restarts. Real full `fit.traj`, full `fit.optim`, no fitting model substitution.
- New untimed source-verified full raw outputs, retained as separate workflow artifacts and **never replacing the original all-64 records**: `auto_raw.json` SHA256 `c04dff8462628e2c9bca2ba7839a1aaa0e15811f21b4f5212591e00fedf28f61`; `Haswell_raw.json` SHA256 `10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a`.
- Machine-readable derived complete 28-field comparisons and **all failing trial coordinates** at `benchmarks/runtime_v1/issue90_results/derived-full-trajectories-42203036203.json`, bot evidence commit `542290f06e264925c0ce592383ff659f6a43d08d`. The same CI artifact retains source raw data and per-process environment.
- No MATLAB rerun on the new runner was performed. Archived MATLAB reference is the exact original public `fitModel` run, so any new HGFX-vs-MATLAB comparisons are *cross-run, not same-host controls*.

## Complete 28-field numerical comparisons

All comparisons below apply the historical fitting/trajectory tolerances, not revised ones. The labels for new cases are **author-side diagnostics**, never retrospective acceptance or new eligible samples.

| Comparison | Failing fields, out of all 28 | `traj.mu` failing cells | `traj.muhat` failing cells |
|---|---|---:|---:|
| Historical HGFX ↔ historical MATLAB | **`traj.mu`, `traj.muhat`** | 4 | 4 |
| Fresh HGFX auto ↔ historical MATLAB | **`traj.mu`, `traj.muhat`** | 4 | 4 |
| Fresh HGFX Haswell ↔ historical MATLAB | **`traj.epsi`, `traj.mu`, `traj.muhat`, `traj.psi`** | **14** | **14** |
| Fresh HGFX auto ↔ fresh HGFX Haswell | `traj.mu`, `traj.muhat` | 4 | 4 |
| Fresh HGFX auto ↔ historical HGFX | no fields outside original numeric tolerances | 0 | 0 |
| Fresh HGFX Haswell ↔ historical HGFX | `traj.mu`, `traj.muhat` | 4 | 4 |

For **fresh Haswell versus original MATLAB**: `traj.epsi` has **5** failing cells (max absolute overall delta `5.758153849566572e-10`), `traj.mu` and `traj.muhat` each have **14** (max absolute overall delta `3.4593145709083117e-9`), and `traj.psi` has **40** (max absolute overall delta `8.825820749791546e-7`). Some large max deltas outside the failing list are inside original *relative* tolerances; failure decisions strictly follow per-element `isclose` with old tolerance. All 28 field reports are retained, including those within tolerance.

### Original four `mu` mismatch locations (and one-step `muhat` lag)

- All are at second HGF level (zero-based column 1).
- `traj.mu` one-based trials: **84, 109, 117, 127** (zero-based rows 83,108,116,126).
- `traj.muhat` one-based trials: **85, 110, 118, 128** (zero-based rows 84,109,117,127).
- Original `mu` / `muhat` pointwise absolute deltas: `7.841805399477764e-10`, `7.501016509314784e-10`, `5.624418569771805e-10`, `6.203096508672346e-10`; original, unchanged per-coordinate bounds (at MATLAB reference values): `7.299856796816515e-10`, `5.282733891438433e-10`, `3.384168267912972e-10`, `5.484480428789678e-10`. These are genuine failures of the original strict comparator.
- Fresh auto↔MATLAB retains **the exact four positions and values**; fresh Haswell↔MATLAB first failing `mu` occurs already at one-based **79** rather than 84 and has 14 failures in both `mu` and shifted `muhat`.

## Findings, limitations and next scientific gate

**Confirmed in the tested environment:** BLAS dispatch choice changes the full trialwise scientific outputs of frozen HGFX fitting, not just internal optimizer records. Choosing Haswell did **not** cure subject-7 scientific nonparity and **expanded** the mismatch from two to four fields in the cross-run reference comparison. No post-hoc dispatch selection can be used to manufacture scientific PASS.

**Not established:** whether the original mismatch primarily arises from source-level forward model numerical differences at matched transformed parameters versus (already documented) quasi-Newton optimizer numerical-path drift. A bounded next diagnostic may compute the full **MATLAB and HGFX forward trajectories at identical frozen final parameter vectors from each original endpoint** (crossed fixed-vector forward experiment). This requires same HGF family, exact transformed parameters, same input, and independent source/precision checks, and must be distinct from actual end-to-end fitting equality.

**Unchanged release scientific status:** historical **63/64** full fitting NON-PASS. 28 original performance workload cells retain 16 review pending / 12 blocked, six of nine original primary CPU fitting cells ineligible. **PERF-01C independent review #88 not signed / NOT FROZEN**, issue #89 subject-7 scientific fitting OPEN, issue #90 numeric environment portability OPEN, **PERF-01E–H NOT RUN; NO speedup or GPU-performance claim.**
