# Agent Handoff

Last synchronized: 2026-09-15
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`
Milestone: **v1.0 release closure — IN PROGRESS / ONLY PHYSICAL NVIDIA GPU + DEPENDENT FINALIZATION REMAIN**
Historical M18 scientific experiment: **FAIL, preserved**

## Read first

1. `V1_TODO.md`
2. `M18_COMPLETION_PLAN.md`
3. `V1_RELEASE_GATE.md`
4. `M19_GATE.md`
5. `M20_GATE.md`
6. `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`
7. `../validation/V1_EVIDENCE_INDEX.md`
8. equivalence/reference-limitation policies and validation matrix

## Current release-accounting state

- M0-M17: completed in documented scopes.
- Historical M18 scientific experiment: FAIL preserved.
- D02 direct fit and D08 prospective holdout failures remain preserved; exact accepted scopes are `REFERENCE_LIMITATION_MATCH`.
- D09/D10-D11/D12: PASS.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8 required-scope repair: DONE; no open required S7-derived mismatch.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`, run `34901924475`, job `104169632034`, artifact `10371308067`.
- S9 physical GPU: **BLOCKED / DEFERRED BY USER**. It is mandatory for final release, but it is no longer H100-specific.
- S10: PASS.
- M19/M20 preflight: PASS_PREFLIGHT.
- Package/citation metadata remain `1.0.0.dev0` until physical GPU/M19 finalization.

## Do not reopen

Do not return to D02/D08 ULP chasing or rerun/redefine S7/S8 merely to produce greener historical diagnostics. Reopen only if a mandatory current gate shows a genuine HGFX-only semantic regression in required scope.

## Only missing external evidence — physical NVIDIA GPU

Use `scripts/run_m18_s9_physical_gpu_revalidation.py`.

Hardware eligibility is frozen by `docs/validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`: any physical NVIDIA CUDA-capable GPU supported by the installed JAX/CUDA runtime is acceptable. T4 is sufficient for this numerical-applicability gate; H100 is not required.

Required final evidence:

- physical NVIDIA GPU visible to JAX and `nvidia-smi`;
- actual GPU residency;
- same repaired numerical/data path;
- CPU-vs-GPU final-objective gap `<= 1e-7`;
- GPU model, driver/runtime, command, source commit, git status and environment note recorded.

CPU/mock evidence cannot substitute.

## Exact continuation after GPU evidence arrives

1. Validate the JSON/provenance against frozen S9 criteria. If it fails, classify the failure; do not relax the gate.
2. If PASS, update release evidence index/docs with `PASS_PHYSICAL_GPU_APPLICABILITY` / full S9 closure.
3. Run `python scripts/build_v1_evidence_manifest.py --mode finalize`; commit the manifest only if status is `FROZEN`. Then M19 may be PASS.
4. Promote `pyproject.toml` and `CITATION.cff` from `1.0.0.dev0` to selected candidate/final version.
5. Remove satisfied physical-GPU/M19 blockers and run `python scripts/check_m20_candidate.py --mode finalize`.
6. Only after M20 final PASS: mark PR #26 ready, merge according to repository policy, and create the corresponding v1.0 tag if required CI is green.

## Integrity rules

Never declare PASS without gate evidence; never tune thresholds/seeds/data/starts/grids/model/optimizer after results; preserve failures and scoped limitation semantics. `PASS_PREFLIGHT` is not final milestone PASS.
