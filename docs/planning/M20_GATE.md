# M20 — v1.0 Candidate

Last synchronized: 2026-09-15
Status: **PREPARED / BLOCKED BY M19 + PHYSICAL NVIDIA GPU EVIDENCE**
Branch: `migration/m18-workflow-closure`

## Purpose

M20 is the final v1.0 candidate gate. It does not reopen scientific validation. It verifies that the accepted MATLAB-equivalence surface, packaging, provenance, metadata and M19 evidence freeze are internally consistent and ready to merge/tag.

## Preconditions for M20 PASS

- M19 evidence manifest is committed with status `FROZEN`.
- S9 physical NVIDIA GPU applicability is PASS on the current numerical path under `M18_S9_PHYSICAL_GPU_AMENDMENT.md`.
- S10 release-readiness remains PASS.
- `reference/validation/v1_release/evidence_index.json` has no unresolved blocker other than the M20 gate itself before final closure.
- Package/citation metadata are release-candidate quality and contain no placeholder values.
- Package version is promoted from development metadata only after preceding gates pass.
- PR/release documents preserve historical FAIL and scoped `REFERENCE_LIMITATION_MATCH` evidence.

## Current preparation

The package remains `1.0.0.dev0` while closure is blocked. Final promotion to `1.0.0rc1` or `1.0.0` occurs only after physical GPU PASS and M19 freeze.

`scripts/check_m20_candidate.py` supports:

- `preflight`: validates all candidate prerequisites that can be checked before physical-GPU/M19 finalization;
- `finalize`: requires an M19 `FROZEN` manifest, valid physical NVIDIA GPU release accounting, release-candidate/final version metadata, and no earlier active blockers.

## Definition of done

When M20 passes, the closure PR may be made ready/merged and the corresponding v1.0 candidate/release tag can be created. M20 remains **PREPARED / BLOCKED** until those gates are actually satisfied.
