# PERF-01D Issue #90 — v2 analysis guard error and archived exact four-source evidence (2026-11-06)

**Historical failed analysis run:** [GitHub Actions 42249566219](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219), v2 source SHA `c84e76ac15779357b620a3d273add224cad2cdf5`. This is **an engineering source-schema acceptance bug**, not a scientific mismatch and not a verified analysis PASS. The first v1 environment-control failure [42248605099](https://github.com/ahmadkhanloo/hgfx/actions/runs/42248605099) is separately documented and remains unchanged.

All four actual frozen HGFX v1.0.0 public subject-7 fitting processes completed on the same pinned logical CPU IDs `[0,1,2,3]` and OpenBLAS 0.3.30 / 4 threads, selecting effective `SkylakeX` / `Haswell` as explicitly prespecified in `PERF01D_ISSUE90_ABBA_V2_PRESPEC_2026-11-06.md`. They restored and verified original failed 64-fit source SHA256 and controls first; no scientific thresholds or frozen datasets changed.

The reusable original `compare_subject7_full_fit_trajectories.validate_new` helper was written for the previous **auto/Haswell** experiment and explicitly expects `blas_mode_requested=None` for `auto`, or `Haswell` for other mode labels. The newly requested and verified explicit `SkylakeX` metadata therefore produced `ValueError: SkylakeX: original unchanged public refit identity not verified`. This rejects a *valid v2 source label*, not a fitting output. The failed workflow preserved all ten source/environment files as [artifact 13519787585](https://github.com/ahmadkhanloo/hgfx/actions/runs/42249566219/artifacts/13519787585) instead of issuing a derived decision or committing evidence.

Raw JSON SHA256:
- `SkylakeX_1` and `SkylakeX_2`: `8bef283bd89d31588ffae5e4a9f6944a1873440f2684dec4ffd026a2a62ad3e2`
- `Haswell_1` and `Haswell_2`: `10f0577e8843850aecaaa24da1a23fd62dfd9a95e274f90e79ad68e70b362e9a`

The exact SHA equality is a **bounded raw serialization repeatability observation on this runner** only; it does not establish any all-host generalization, original MATLAB scientific equivalence, or speedup.

**Corrective implementation only:** new `validate_explicit_coretype` in the separate v2 comparator validates `SkylakeX` or `Haswell` explicitly **without mutating any raw evidence**; it checks every frozen/source/fitting/full-field/start/trajectory condition from original `validate_new` and adds targeted positive and fail-closed controls. V2 experimental design, four cases, original 63/64 scientific NONPASS, thresholds, input SHA256 and scientific scope remain unchanged. The initially failed v2 run remains permanently recorded, and the correction requires a *new run ID* before any derived classification is reported.
