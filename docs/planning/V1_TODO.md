# HGFX v1.0 Live TODO

Last synchronized: 2026-09-15
Status: **IN PROGRESS — FINAL EXTERNAL PHYSICAL-GPU EVIDENCE DEFERRED**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

Use this file with `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`, equivalence/reference-limitation policies, and exact decision records under `reference/validation/`.

## DONE / accepted release accounting

- M0-M17: completed in documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.
- D02 direct fit: **FAIL preserved**; exact official release scope: `REFERENCE_LIMITATION_MATCH`.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265`: `REFERENCE_LIMITATION_MATCH`.
- D04/D09/D10-D11/D12: PASS in documented scopes.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS; model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8: **DONE** for required v1 scope; semantic repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no unresolved required S7-derived mismatch.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`; run `34901924475`, job `104169632034`, artifact `10371308067`, SHA-256 `875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826`.
- S10: **PASS**; latest release-preparation-head rerun `34934079865`, artifact `10383235791`.
- M19/M20 non-GPU preflight: **PASS_PREFLIGHT**, run `34934079973`, job `104268154143`, artifact `10383425031`.

## BLOCKED / DEFERRED — S9 physical NVIDIA GPU

This is the only missing external evidence. GPU model is **not constrained**. Any physical NVIDIA CUDA-capable GPU supported by JAX is eligible; the exact model must be recorded.

Required frozen acceptance:

- run the same repaired S9 numerical path on the physical NVIDIA GPU;
- actual GPU residency demonstrated;
- JAX CPU-vs-GPU final-objective gap `<= 1e-7`;
- GPU model, driver/CUDA/JAX/JAXLIB/Python, command, source commit, git status and environment limitations recorded;
- no CPU/mock evidence may substitute.

Use `scripts/run_m18_s9_physical_gpu_revalidation.py`. The old H100-named wrapper is retained only as a compatibility alias.

## PREPARED / BLOCKED — M19

- [x] Evidence-freeze gate document exists.
- [x] Machine-readable manifest builder exists.
- [x] Non-GPU preflight passes.
- [ ] Physical NVIDIA GPU evidence passes.
- [ ] Run `python scripts/build_v1_evidence_manifest.py --mode finalize`.
- [ ] Commit `reference/validation/v1_release/evidence_manifest.json` with status `FROZEN`.

## PREPARED / BLOCKED — M20

- [x] Candidate gate/checker exists.
- [x] Package/citation metadata are on development v1 line (`1.0.0.dev0`).
- [x] Non-GPU preflight passes.
- [ ] M19 is `FROZEN`.
- [ ] Promote version/CITATION to chosen release-candidate/final version.
- [ ] Run `python scripts/check_m20_candidate.py --mode finalize`.
- [ ] Make PR ready/merge/tag only after final candidate gate passes.

## Closed historical diagnostics

S8 negative-precision/precheck workflows are preserved manual diagnostics, not ordinary release gates. Do not reopen D02/D08/S7/S8 without a genuine mandatory current-scope regression.

## Status vocabulary

Use only evidence-backed **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**. `PASS_PREFLIGHT` is not final milestone PASS.
