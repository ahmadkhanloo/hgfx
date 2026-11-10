# REV-2.4 Panel E original-source coverage — 2026-11-10

**Status:** SOURCE-ONLY AUDIT PASS; **SCIENTIFIC / OBJECTIVE CROSS-EVALUATION NOT RUN**. The historical fitting and recovery failures are preserved without reclassification.

## Authoritative execution

- GitHub Actions source-only preflight: [run 42773865848](https://github.com/ahmadkhanloo/hgfx/actions/runs/42773865848), workflow `.github/workflows/compstat-rev24-endpoint-preflight.yml`, source commit `2585e3b9cb5c88a6734ff8764e9125066418b17c`, conclusion **success**. Its source check tests, checkout of original input commit, all three archival downloads, whole-ZIP and inner-file SHA-256 checks, endpoint counts and sanitized result upload completed successfully.
- Archival preflight artifact `compstat-rev24-panel-e-source-preflight`, artifact ID `13743111655`. Contained only sanitized `source_audit.json` (SHA-256 `e5b89d42a4e99cfda3fd704537f178d9907256ba59fff52e096568009651d393`) and `coverage_audit.json` (SHA-256 `80c0c60e13e6da3d086d6b4ce5ab301f827044dfc271c64c17d3fb4593745da3`). No participant-level data or fitted parameter vectors uploaded.
- Read-only original artifacts: D02 `10339454535` / run `34823572071`; D08 `10339403480` / run `34823572192`; 64 subjects `13341288055` / run `41863441006`. Original exact archive SHA-256 and inner 64-subject JSON SHA-256 are in `tools/compstat_rev24_endpoint_sources.py`. These archives were already historical; no new fit was made.

## Original endpoint/source coverage

| Case | Model and observation | Input evidence | Original MATLAB endpoint | Original HGFX endpoint | Result |
| --- | --- | --- | --- | --- | --- |
| D02 | `ehgf_binary + unitsq_sgm` | Original 320-trial input and response, seed `123456789` in `m18_workflows.json` | Complete full 15-vector present | **Full original 15-vector NOT FOUND** in pinned original run archive; a first-divergence scalar is inadequate | **BLOCKED on source** |
| D08 | `uhgf + gaussian_obs` | Original 614-trial input and response in `m18_d08_endpoint.json` | Complete 11-vector present | Complete 11-vector in original comparison; original MATLAB vector cross-matches | **READY FOR IMPLEMENTING cross-evaluation**, NOT executed |
| 64 cohort | `hgf_binary + unitsq_sgm` | Every original subject has the same 128-trial source identity | 64/64 complete full 15-vectors | 64/64 complete full 15-vectors | **READY FOR IMPLEMENTING cross-evaluation**, NOT executed |

Original cohort input `benchmarks/runtime_v1/inputs/binary_128_s64.json` was fetched from its **executing source commit** `81ae256b318e18ea08b03ab6fcb69100ac6c836d`, Git blob `bb8989b96de1cbe66a6b880a0146b82a9b1817dc`, SHA-256 `6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae`. The SHA matches the original HGFX 64-fit `input_sha256`. Historical 64-fit workflow [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) concluded **failure**, despite producing the original artifacts; that scientific failure is **not** reclassified by a source-preflight PASS.

## Exact outstanding scientific gate

1. Find the **complete original** D02 HGFX 15-parameter transformed final vector with a verifiable source artifact SHA, or retain `INSUFFICIENT_REFERENCE_EVIDENCE`. Do not reconstruct missing components from one recorded divergence or rerun fitting to replace the original endpoint.
2. Execute the pinned Panel-G 600-vector same-vector objective experiment (authentic MATLAB HGF 8.2.0, released HGFX 1.0.0 Wheel); the manual-only workflow `.github/workflows/compstat-rev24-original-oracle.yml` is presently in the draft revision branch and **has no recorded scientific run**. Verify the frozen reference, free-vector order and existing family-specific objective gates before any claim.
3. Implement and run original Panel-E cross-endpoint objective evaluations at both original fitted endpoints for D02, D08 and all 64 subjects; explicitly preserve missing rows/status, negative-log-likelihood/joint discrepancy, first-divergence evidence or NOT_EXPORTED.
4. Preserve REV-1.4 `DOCUMENTED_LIMITATION`, M18 scientific FAIL, P3 FAIL, 63/64 historical full-fit NONPASS and PERF-01C `BLOCK_FREEZE`. No numerical threshold, seed, cohort or dataset was changed. No D2/D3 author approval or article submission has occurred.

**Scope:** source and archival identity only. Neither HGFX 1.0.0 objective execution nor physical MATLAB numerical execution is represented by this report.
