# M20 — v1.0 Candidate

Last synchronized: 2026-09-15
Status: **READY TO FINALIZE — M19 FROZEN**
Branch: `migration/m18-workflow-closure`

## Purpose

M20 is the final v1.0 candidate gate. It does not reopen scientific validation. It verifies that the accepted MATLAB-equivalence surface, packaging, provenance, metadata and M19 evidence freeze are internally consistent and ready to merge/tag.

## Preconditions for M20 PASS

- [x] M19 evidence manifest is committed with status `FROZEN`.
- [x] S9 physical NVIDIA GPU applicability is PASS on the current numerical path under `M18_S9_PHYSICAL_GPU_AMENDMENT.md`.
- [x] S10 release-readiness remains PASS.
- [x] `reference/validation/v1_release/evidence_index.json` has no unresolved blocker other than the M20 gate itself.
- [ ] Package/citation metadata are promoted to release-candidate quality and remain mutually consistent.
- [ ] M19 manifest hashes are refreshed after metadata-only release-candidate promotion.
- [ ] `scripts/check_m20_candidate.py --mode finalize` returns `PASS_M20_CANDIDATE`.
- [x] PR/release documents preserve historical FAIL and scoped `REFERENCE_LIMITATION_MATCH` evidence.

## Current state

M19 finalize workflow run `34966661492` succeeded and committed a `FROZEN` manifest at commit `b71301b978e07cb0fa5ac2ad14cc92235fadc5ee`.

The only active release blocker is now M20. The next ordered actions are:

1. promote package and citation metadata from `1.0.0.dev0` to `1.0.0rc1`;
2. rerun the M19 finalizer to refresh release-file hashes without changing scientific evidence;
3. run `scripts/check_m20_candidate.py --mode finalize`;
4. mark M20 PASS only if the final checker succeeds.

## Candidate checker

`scripts/check_m20_candidate.py` supports:

- `preflight`: validates candidate prerequisites available before final closure;
- `finalize`: requires an M19 `FROZEN` manifest, valid physical NVIDIA GPU release accounting, release-candidate/final version metadata, and no earlier active blockers.

## Definition of done

When M20 returns `PASS_M20_CANDIDATE`, the closure PR may be made ready/merged and the corresponding v1.0 candidate/release tag can be created. Until that checker succeeds, M20 remains **READY TO FINALIZE**, not PASS.
