# M19 — Methods Paper Dataset Frozen

Last synchronized: 2026-09-15
Status: **PREPARED / BLOCKED BY PHYSICAL NVIDIA GPU EVIDENCE**
Branch: `migration/m18-workflow-closure`

## Purpose

M19 keeps its historical name but serves the v1.0 release as the evidence-freeze gate. It freezes the validated release evidence package so another reviewer can reproduce the release accounting without relying on chat history.

## Preconditions for M19 PASS

- S9 CPU/backend evidence is PASS under `m18-s9-robustness-backend-1`.
- Current numerical-path physical NVIDIA GPU evidence is recorded and passes the unchanged CPU-vs-GPU final-objective gap `<= 1e-7` with actual GPU residency.
- GPU model is not constrained; exact hardware and runtime must be recorded per `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`.
- S10 release-readiness is PASS.
- D02/D08/S7 scoped `REFERENCE_LIMITATION_MATCH` records and historical failures remain preserved.
- Release-critical evidence files are hashed into one machine-readable manifest.

## Current state

All non-GPU prerequisites are implemented and evidence-backed. The only missing runtime input for final freeze is fresh physical NVIDIA GPU evidence for the repaired S9 numerical path.

## Freeze mechanism

`scripts/build_v1_evidence_manifest.py` has two modes:

- `preflight`: hashes the current evidence package, verifies S10/non-GPU records, and reports physical GPU as deferred;
- `finalize`: additionally requires valid eligible physical NVIDIA GPU evidence and writes a manifest classified `FROZEN`.

The expected GPU evidence path is `gpu_validation_results/m18_s9_physical_gpu_revalidation.json`. The final committed manifest is `reference/validation/v1_release/evidence_manifest.json`.

## Integrity rule

M19 is an evidence freeze, not a rerun or retuning stage. No thresholds, seeds, datasets, starts, grids, model families, optimizers, historical failures, or reference-limitation scopes may be changed to make M19 pass.
