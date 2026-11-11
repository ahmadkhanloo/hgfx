# PERF-01D / Issue #90 — immutable ABBA v2 four-source archived-replay results (2026-11-06)

**Author-side engineering source replay COMPLETE: 36/36 focused structural/source tests PASS and SHA-locked derived analysis SUCCESS. Scientific MATLAB↔HGFX full public fitting still 63/64 NONPASS. PERF-01C OPEN/NOT FROZEN. No timing, GPU, independently approved reference limitation, or speedup.**

Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [independent review #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [scientific mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89), [numerical portability #90](https://github.com/ahmadkhanloo/hgfx/issues/90).

## Exact, independently traceable experiment sources

Original full public **64×128** HGF binary `unitsq_sgm` fit source/reference [CI 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), frozen HGFX **v1.0.0 SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`**, frozen MATLAB HGF Toolbox **8.2.0 SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`**. Original subject index **7 (zero-based)** is the single unchanged nonconcordant case; all original 28 fields, all four `mu` and four `muhat` failures and every old fit/trajectory numerical tolerance remain unchanged.

The four genuine, unmodified HGFX v1.0.0 public fits were obtained in the same original [CI 42249566219](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219) with original source candidate **`c84e76ac15779357b620a3d273add224cad2cdf5`**, and fully retained in [artifact 13519787585](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219/artifacts/13519787585). Exact predeclared **A1–B1–B2–A2** order, A=explicit `OPENBLAS_CORETYPE=SkylakeX`, B=explicit `OPENBLAS_CORETYPE=Haswell`. Same runner, original subject/trials/data/config/start/free mask and `nRandInit=0`, four pinned logical cores `[0,1,2,3]`, NumPy **2.3.5**, effective OpenBLAS **0.3.30** with **4 threads**, `JAX_PLATFORMS=cpu`. Each process reported effective mode and exact CPU/affinity/environment metadata and was separately SHA-256 verified.

Raw four original fit files (no reruns):
- `SkylakeX_1`, `SkylakeX_2`: `8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2`
- `Haswell_1`, `Haswell_2`: `10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a`.

The source-run analysis-stage failure and later new-run hardware SIGILL are independently retained:
- [first v1 auto-mode environment-control failure 42248605099](https://github.com/ahmadkhanloo/hgfx/actions/runs/42248605099);
- [initial v2 archived four-fit analyzer schema bug 42249566219](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219);
- [later v2 fresh SkylakeX SIGILL on a different runner 42250002320](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250002320);
- [first archive-only missing-package dependency failure 42250386120](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250386120).

**Successful, separately executed archived-source analysis:** [GitHub Actions 42250539438](https://github.com/ahmadkhanloo/hgfx/actions/runs/42250539438), exact analyzed source SHA `9b8d6cd69382248ac1fabdff92fd242992cf63e9`, 17 explicit ABBA guards + 12 original full-trajectory guards + 7 original fit-cohort guards = **36/36**. It downloaded the **same four original raw bytes**, verified exact published SHA-256, unmodified archived 63/64 source, exact 4 process environment/source SHA and every output inventory, then compared all 28 preexisting fields with unchanged tolerances. **No fit, MATLAB, new kernel intervention, timing or GPU execution in this analysis workflow.**

Permanent machine-readable report:
`benchmarks/runtime_v1/issue90_results/derived-archived-v2-42250539438.json`; Git blob SHA **`839be1d068f25ec024c96debc28b71f8a630ad77`**, committed by GitHub Actions at **`0de04d735e7c0295d1aa661bcd89ffc695700252`**, in addition to the independently uploaded raw/derived archived artifact. Analyzer `compare_subject7_same_host_repeatability_v2.py`; complete exact six contrasts, all per-field bitwise counts, and all four original-reference comparisons are in JSON.

## Complete 28-field outcomes, unchanged old numerical tolerances

| Contrast | Bitwise equality of all 28 serialized fields | Fields failing original numerical tolerance | Failing `traj.mu` cells | Failing `traj.muhat` cells |
|---|---|---|---:|---:|
| A1 ↔ A2 (SkylakeX repeat) | **YES** | none | 0 | 0 |
| B1 ↔ B2 (Haswell repeat) | **YES** | none | 0 | 0 |
| A1 ↔ B1 | **NO** | `traj.mu`, `traj.muhat` | 4 | 4 |
| A2 ↔ B2 | **NO** | `traj.mu`, `traj.muhat` | 4 | 4 |
| A1 ↔ B2 | **NO** | `traj.mu`, `traj.muhat` | 4 | 4 |
| A2 ↔ B1 | **NO** | `traj.mu`, `traj.muhat` | 4 | 4 |

The two within-mode raw JSON file hashes also match **exactly**. Across A and B the original final transformed parameter vector differs by max absolute **`3.968255768427298e-8`**; other 28-field differences are preserved, not only failed fields. This is **direct same-runner numerical path sensitivity with controlled OpenBLAS dispatch** on this source/hardware configuration and NOT evidence for universal bitwise determinism.

## All four vs the exact unchanged archived original MATLAB reference

| HGFX new original-source fit | Fields failing vs the ORIGINAL MATLAB fit | `traj.mu` failures | `traj.muhat` failures |
|---|---|---:|---:|
| SkylakeX_1 | `traj.mu`, `traj.muhat` | 4 | 4 |
| SkylakeX_2 | `traj.mu`, `traj.muhat` | 4 | 4 |
| Haswell_1 | `traj.epsi`, `traj.mu`, `traj.muhat`, `traj.psi` | 14 | 14 |
| Haswell_2 | `traj.epsi`, `traj.mu`, `traj.muhat`, `traj.psi` | 14 | 14 |

Both SkylakeX fits are within old 28-field tolerances of the **original archived HGFX** fit. Both Haswell fits fail `traj.mu/muhat` vs original HGFX. Comparisons against original MATLAB run are **cross-run / different-host diagnostics**, not matched-host MATLAB re-execution or independent scientific adjudication.

## Boundaries and next acceptance action

What is supported: **within this one constrained CPU runner**, both same-BLAS-mode fitting repeats produce the same serialized binary64 outputs across all 28 original fields, and the two distinct OpenBLAS dispatch kernels produce distinct frozen HGFX full-fit outputs with original `traj.mu/muhat` numeric failures. This isolates a bounded environment numerical-path mechanism for this HGFX self-comparison; it does **not** establish a specific source implementation defect, explain the historical MATLAB reference optimizer trajectory with independent same-host data, or establish universal bitwise repeatability across hardware.

A separate new runner's SIGILL is an environment/platform compatibility limitation: forcing a CPU kernel unsupported on a given host can crash before fitting, so future prospective compatible hosts must prove ISA capabilities **before** executing the predeclared kernel. Do **not** change the failed-run protocol, hide it, retune a scientific tolerance, or select only matching subjects to manufacture PASS.

**Binding scientific status: original full public MATLAB/HGFX 63/64 NONPASS**, nested cohorts 1/1, 15/16, 63/64. **Independent scientific reviewer issue #88 OPEN**, issue #89 OPEN, issue #90 OPEN; PERF-01C prospective freeze NOT APPROVED, 28 originally planned workload cells 16 review-pending / 12 blocked, and six of nine original primary CPU cells ineligible. PERF-01E–H NOT RUN. The reviewer must examine the original MATLAB reference/optimizer evidence alongside this bounded kernel sensitivity, explicitly classify the remaining 63/64 discrepancy, and only then decide eligibility/prospective performance protocol freeze. No speedup claim.


## 2026-11-06 — numeric-margin audit to distinguish severity from acceptance

[Original-tolerance subject-7 exceedance report](PERF01D_SUBJECT7_ORIGINAL_TOLERANCE_MARGINS_2026-11-06.md): [Actions 42266125766](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766), tested source SHA `ef26ddc9e9efeca31cf9f8dc2cd8ae91ccb1b788`, **14/14 tests**, machine artifact [13526892782](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766/artifacts/13526892782). Recomputed old `atol=3e-10 / rtol=3e-8` numerical bounds for **every original failed** `mu/muhat` cell without changing criterion or raw evidence. Against *historical different-host MATLAB*, both SkylakeX repeated fits have **4+4** failed cells (max `mu` exceedance 1.66198× old bound); both Haswell fits **14+14** (max 3.66090×); all four same-host cross-dispatch comparisons **4+4** (max 1.99892×). Exactly one-trial `mu`→`muhat` lag in every failed list. These are descriptive old-gate failure severity diagnostics, **not independent approval or a license to pick the more matching kernel post hoc**. The earlier test-expectation failure [42266034562](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266034562) is retained.

**Binding acceptance and scientific status:** exact frozen original full public fit **63/64 SCIENTIFIC NONPASS**, 28 original cases 16 review-pending/12 blocked, independent #88 NOT RECEIVED, PERF-01C NOT FROZEN, no MATLAB-vs-HGFX benchmark timing or speed claim.
