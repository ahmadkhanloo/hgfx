# PERF-01D / Issues #89–#90 — original subject-7 tolerance-exceedance audit (2026-11-06)

**Author-side derived evidence: SUCCESS. Scientific original full public MATLAB/HGFX fitting: 63/64 NONPASS. PERF-01C: OPEN / NOT FROZEN. No independent reviewer verdict, new MATLAB fit, physical GPU or performance timing.**

## Exact execution

- [Successful GitHub Actions 42266125766](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766), verified executed source SHA **`ef26ddc9e9efeca31cf9f8dc2cd8ae91ccb1b788`**, **14/14 tests passed**.
- [Machine-readable per-cell result, artifact 13526892782](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766/artifacts/13526892782), archived as `perf01d-subject7-original-tolerance-42266125766`.
- Script: `benchmarks/runtime_v1/derive_subject7_original_tolerance_margins.py`; negative/positive tests: `tests/test_perf01_subject7_original_tolerance_margins.py`; workflow: `.github/workflows/perf01-subject7-tolerance-margins.yml`.
- **Sole input to this new computation** is the already SHA-pinned *tracked derived* ABBA archive `benchmarks/runtime_v1/issue90_results/derived-archived-v2-42250539438.json`, immutable tracked SHA-256 **`7898bee80dd50a53b2ae9605fdf10d4e9562ef3b45783fb103a822a1ec619730`**. Original raw source bytes were independently verified in the preceding [seven-source raw archive replay 42263893242](https://github.com/ahmadkhanloo/hgfx/actions/runs/42263893242). The new job **did not re-download or rehash those remote raw artifacts**, nor rerun MATLAB/HGFX.
- Fixed original product HGFX v1.0.0 @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`. Historical 64-fit source run **41863441006**: **63/64 NONPASS** at zero-based subject index **7**; original failure fields `traj.mu` and `traj.muhat` (four cells each).

## Original numerical threshold (not redefined)

For each listed originally failed trajectory cell, the script re-evaluates `absolute_difference = abs(other_value - archived_reference_value)` and the **pre-existing original** bound `atol + rtol * abs(archived_reference_value)` using **`atol = 3e-10`, `rtol = 3e-8`**. The descriptive **exceedance ratio** is `absolute_difference / original_bound`. Values above 1 indicate that the *already archived* cell exceeds the unchanged original tolerance. This does not introduce a revised acceptance threshold, excuse a failure or establish a statistical error guarantee. All original 28 output fields retain their historical comparator classifications.

| Original archived comparison | Failed `traj.mu` cells | Failed `traj.muhat` cells | Maximum original-bound exceedance for `traj.mu` |
|---|---:|---:|---:|
| SkylakeX_1 versus original MATLAB (different host/run) | 4 | 4 | **1.66198×** |
| SkylakeX_2 versus original MATLAB (different host/run) | 4 | 4 | **1.66198×** |
| Haswell_1 versus original MATLAB (different host/run) | 14 | 14 | **3.66090×** |
| Haswell_2 versus original MATLAB (different host/run) | 14 | 14 | **3.66090×** |
| SkylakeX_1 versus SkylakeX_2 (same-runner repeat) | 0 | 0 | no failures |
| Haswell_1 versus Haswell_2 (same-runner repeat) | 0 | 0 | no failures |
| All four SkylakeX–Haswell cross-mode contrasts (each distinct pair) | 4 each | 4 each | **1.99892×** each |

Original MATLAB-comparison failed *one-based* `traj.mu` trials for SkylakeX_1/2: **84, 109, 117, 127**. The four cross-BLAS `mu` failures have the same trial indices. Original MATLAB-comparison Haswell_1/2 failures: **79, 83, 84, 85, 87, 108, 109, 110, 111, 112, 115, 116, 117, 127**. Each matching `traj.muhat` failure is exactly **one trial later** than the associated `traj.mu` failure, with the same recorded values and level, consistent with the original model's lagged-state output structure. A fail-closed test explicitly checks this lag and refuses changed first-mismatch locations, absolute differences or stored numerical bounds.

**Numerical finding:** the same frozen public HGFX fit/data/start can yield different fitting endpoints and inherited-tolerance trialwise failures under two original CPU BLAS dispatch choices on one constrained runner. The original reference comparison additionally depends on the original historical MATLAB run from a *different host*. The 4-versus-14 difference therefore **must not** be interpreted as proof that one kernel fixes the MATLAB fitting compatibility, and choosing SkylakeX to obtain fewer failures would be post-hoc environment selection and is not authorized.

## Failure history and scientific limits

The first new [workflow 42266034562](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266034562) **FAILED** because a synthetic negative test anticipated the lag guard while a stricter earlier `first_mismatch_index_zero_based` check caught the same mutation. The derived evidence itself passed its positive synthetic test; no new MATLAB/HGFX model calculation occurred. The follow-up change tested the lag at the *second* mismatch without invalidating the first-mismatch guard, and added a separate first-mismatch negative test. Successful [42266125766](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766) reports **14/14**. Keep the first failure visible; it is a test fixture expectation error, not a scientific failure or PASS.

**What this does not demonstrate:** same-host matched MATLAB/HGFX full-fitting parity, universal cross-run bitwise determinism, scientific identifiability, a source defect, a scientifically certified MATLAB-reference limitation, full 64/64 acceptable fits, or runtime/speedup. The original 28 planned workload cases remain **16 review-pending / 12 blocked**, and six original primary nine-case CPU tasks are ineligible. Issues [#88](https://github.com/ahmadkhanloo/hgfx/issues/88), [#89](https://github.com/ahmadkhanloo/hgfx/issues/89), and [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) remain open.

**Required next acceptance action:** an **independent** reviewer must inspect exact original source semantics and raw fitting evidence, adjudicate the subject-7 original workflow mismatch and the numerical portability limits, and issue signed `BLOCK_FREEZE` or `APPROVE_PROSPECTIVE_FREEZE` with reviewed SHA, evidence hashes, case eligibility and timing policy. Do **not** time the benchmark for paper use without a prospectively approved new protocol lock.
