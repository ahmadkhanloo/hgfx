# M19 — Methods Paper Dataset Frozen

Last synchronized: 2026-09-15
Status: **DONE / PASS — EVIDENCE MANIFEST FROZEN**
Branch: `migration/m18-workflow-closure`

## Purpose

M19 keeps its historical name but serves the v1.0 release as the evidence-freeze gate. It freezes the validated release evidence package so another reviewer can reproduce the release accounting without relying on chat history.

## Preconditions for M19 PASS

- [x] S9 CPU/backend evidence is PASS under `m18-s9-robustness-backend-1`.
- [x] Current numerical-path physical NVIDIA GPU evidence is recorded and passes the unchanged CPU-vs-GPU final-objective gap `<= 1e-7` with actual GPU residency.
- [x] GPU model is not constrained; exact hardware and runtime are recorded per `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`.
- [x] S10 release-readiness is PASS.
- [x] D02/D08/S7 scoped `REFERENCE_LIMITATION_MATCH` records and historical failures remain preserved.
- [x] Release-critical evidence files are hashed into one committed machine-readable `FROZEN` manifest.

## Final result

M19 finalize workflow run `34966661492` completed successfully. The generated manifest was committed at `b71301b978e07cb0fa5ac2ad14cc92235fadc5ee` to `reference/validation/v1_release/evidence_manifest.json`.

The committed manifest records:

- `status = FROZEN`;
- `mode = finalize`;
- `failures = []`;
- physical GPU `pass = true`;
- physical classification `PASS_PHYSICAL_GPU_APPLICABILITY`;
- historical failures preserved;
- no thresholds, seeds, datasets or validation grids changed for the freeze.

M19 is therefore **DONE / PASS**. Release-candidate metadata may now be promoted and M20 finalized.

## Physical-GPU prerequisite result

The accepted S9 physical run used 2x Tesla T4 in a hosted/shared Kaggle environment and source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`. JAX/JAXLIB were `0.11.1`, Python `3.12.13`, and the JAX backend was `gpu` with physical process residency visible in `nvidia-smi`.

All four required CPU-vs-GPU fitting cells pass. The maximum final-objective gap is `1.4210854715202004e-14`, well below the frozen `1e-7` criterion. Raw uploaded JSON SHA-256 is `6cd35c82be1e542830c06f6b7b7e444fda0ff4fe93773f080e6c13725212dfdf`; repository evidence record commit is `7179484ce782c25d6edde34cc56a0d689831e1cc`.

The captured git status contains only `?? gpu_validation_results/`, which is the output directory created by the validation wrapper before provenance capture. The recorded source HEAD matches the tested commit; no numerical source modification is indicated.

## Freeze mechanism

`scripts/build_v1_evidence_manifest.py --mode finalize` is the canonical M19 finalizer. It validates the physical GPU record, release evidence index and required release files, then writes the machine-readable manifest.

The GPU evidence path is `gpu_validation_results/m18_s9_physical_gpu_revalidation.json`. The committed M19 manifest is `reference/validation/v1_release/evidence_manifest.json`.

Release metadata promoted after the initial freeze must not alter numerical/scientific evidence. Before M20 final validation, the same M19 finalizer may refresh hashes for metadata-only candidate changes while retaining `FROZEN` status and the unchanged evidence semantics.

## Integrity rule

M19 is an evidence freeze, not a rerun or retuning stage. No thresholds, seeds, datasets, starts, grids, model families, optimizers, historical failures, or reference-limitation scopes may be changed to make M19 pass.
