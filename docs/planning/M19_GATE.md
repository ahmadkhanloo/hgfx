# M19 — Methods Paper Dataset Frozen

Last synchronized: 2026-09-15
Status: **PREPARED / BLOCKED BY PHYSICAL H100 EVIDENCE**
Branch: `migration/m18-workflow-closure`

## Purpose

M19 keeps its historical name but serves the v1.0 release as the evidence-freeze gate. It freezes the validated release evidence package so another reviewer can reproduce the release accounting without relying on chat history. Manuscript acceptance is not a v1.0 requirement.

## Preconditions for M19 PASS

- S9 CPU/backend evidence is PASS under the frozen `m18-s9-robustness-backend-1` protocol.
- Current numerical-path physical H100 evidence is recorded and passes the unchanged CPU-vs-GPU final-objective gap `<= 1e-7` with actual GPU residency.
- S10 release-readiness is PASS.
- D02/D08/S7 scoped `REFERENCE_LIMITATION_MATCH` records remain explicit and historical/prospective failures remain preserved.
- Release-critical repository evidence files exist and are hashed into one machine-readable manifest.
- External workflow/artifact IDs and SHA-256 digests needed for the release are copied into the aggregate evidence index/manifest.

## Current state

All non-GPU prerequisites above are implemented and evidence-backed. S10 passed on run `34933146678`, job `104265387068`, artifact `10382605498`, SHA-256 `1d6f3650ae1d48751094f9c2e0305575988661114248143fde60719215437840`.

The only missing scientific/runtime input for final freeze is fresh physical H100 evidence for the repaired S9 numerical path. Until that file exists and passes, M19 must remain **PREPARED / BLOCKED**, not PASS.

## Freeze mechanism

`scripts/build_v1_evidence_manifest.py` has two modes:

- `preflight`: hashes the current evidence package, verifies S10 and all non-GPU records, and reports the H100 item as deferred without pretending that M19 has passed;
- `finalize`: additionally requires valid physical-GPU evidence and writes a manifest classified `FROZEN`.

The final committed manifest is `reference/validation/v1_release/evidence_manifest.json`.

## Integrity rule

M19 is an evidence freeze, not a rerun or retuning stage. No thresholds, seeds, datasets, starts, grids, model families, optimizers, historical failures, or reference-limitation scopes may be changed to make M19 pass.
