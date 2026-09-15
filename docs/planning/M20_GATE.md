# M20 — v1.0 Candidate

Last synchronized: 2026-09-15
Status: **PREPARED / BLOCKED BY M19 + PHYSICAL H100 EVIDENCE**
Branch: `migration/m18-workflow-closure`

## Purpose

M20 is the final v1.0 candidate gate. It does not reopen scientific validation. It verifies that the already accepted MATLAB-equivalence surface, release packaging, provenance, metadata and evidence freeze are internally consistent and ready to merge/tag.

## Preconditions for M20 PASS

- M19 evidence manifest is committed with status `FROZEN`.
- S9 physical-H100 applicability is PASS on the current numerical path.
- S10 release-readiness remains PASS.
- `reference/validation/v1_release/evidence_index.json` has no unresolved blocker other than the M20 gate itself before final closure.
- Package/citation metadata are release-candidate quality and contain no placeholder `TBD` values.
- Package version has been promoted from development metadata to the chosen v1 candidate/release version only after the preceding gates pass.
- PR/release documents agree on the same release classification and preserve all historical FAIL / scoped `REFERENCE_LIMITATION_MATCH` evidence.

## Current preparation

The package is moved to `1.0.0.dev0` while closure is still blocked. This is intentionally not a release candidate. The final promotion to `1.0.0rc1` (or directly `1.0.0` if release policy chooses that) happens only after physical-H100 evidence and M19 freeze are complete.

`scripts/check_m20_candidate.py` supports:

- `preflight`: validates all candidate prerequisites that can be checked before H100/M19 finalization;
- `finalize`: requires an M19 `FROZEN` manifest, valid physical-GPU release accounting, release-candidate/final version metadata, and no earlier active blockers.

## Definition of done

When M20 passes, the closure PR may be made ready/merged and the corresponding v1.0 candidate/release tag can be created. M20 must remain **PREPARED / BLOCKED** until those documented gates are actually satisfied.
