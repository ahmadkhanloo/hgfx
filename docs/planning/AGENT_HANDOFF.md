# Agent Handoff

Last synchronized: 2026-09-15
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: `2437f4dc241541072722a2695ddeca7b44d83dd3`
Milestone: **v1.0 release closure — IN PROGRESS / ONLY PHYSICAL H100 + DEPENDENT FINALIZATION REMAIN**
Historical M18 scientific experiment: **FAIL, preserved**

## Read first

1. `V1_TODO.md`
2. `M18_COMPLETION_PLAN.md`
3. `V1_RELEASE_GATE.md`
4. `M19_GATE.md`
5. `M20_GATE.md`
6. `../validation/V1_EVIDENCE_INDEX.md`
7. `../validation/MATLAB_EQUIVALENCE_POLICY.md`
8. `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
9. `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`

## Current release-accounting state

- M0-M17: completed in documented scopes.
- Historical M18 scientific experiment: FAIL preserved.
- D02 direct fit: FAIL preserved; exact official scope = `REFERENCE_LIMITATION_MATCH`.
- D08 prospective holdout: FAIL preserved; exact failed seed `314159265` = `REFERENCE_LIMITATION_MATCH`.
- D09/D10-D11/D12: PASS.
- S7 paired parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8 required-scope repair: DONE; repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no open required S7-derived implementation/optimizer/model-selection mismatch.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`, run `34901924475`, job `104169632034`, artifact `10371308067`.
- S9 physical H100: **BLOCKED / DEFERRED BY USER**. This is still mandatory for final release.
- S10: PASS. Latest release-preparation-head rerun `34934079865`, artifact `10383235791`, SHA-256 `8abf4488e91c6ae28983c318670f4a92dfab57c4acc8caad494be02fca47eb2b`.
- M19 preflight: PASS_PREFLIGHT.
- M20 preflight: PASS_PREFLIGHT.
- M19/M20 preflight run `34934079973`, job `104268154143`, artifact `10383425031`, SHA-256 `3f711a260f68ff0454d18b2b09b3645d28ab5b370384c8729d4fd431bee5e7cf`.
- Package/citation metadata are intentionally development state `1.0.0.dev0`; do not promote until H100/M19 finalization.

## Do not reopen

Do not return to D02/D08 ULP chasing or rerun/redefine S7/S8 merely to produce greener historical diagnostics. Reopen only if a mandatory current release gate shows a genuine HGFX-only semantic regression in required scope.

The S8 negative-precision and raw-precheck workflows are historical localization probes. They deliberately exercise an invalid parameter region where frozen MATLAB can itself raise `Negative posterior precision`. Their old runs and failures remain preserved; the workflows are manual-only after S8 closure and are not ordinary release gates.

## Only missing external evidence — physical H100

Use the existing `scripts/run_m18_s9_h100_revalidation.py`. Do not change frozen criteria.

Required final evidence:

- physical H100 visible to JAX;
- actual GPU residency;
- same repaired numerical/data path;
- CPU-vs-GPU final-objective gap `<= 1e-7`;
- hardware, driver/runtime, command, source commit and environment/contention note recorded.

CPU/mock evidence cannot substitute.

## Exact continuation after H100 evidence arrives

1. Validate the H100 JSON/provenance against frozen S9 criteria. If it fails, classify the failure; do not relax the gate.
2. If PASS, update `reference/validation/v1_release/evidence_index.json` and docs with `PASS_PHYSICAL_GPU_APPLICABILITY` / full S9 closure.
3. Run `python scripts/build_v1_evidence_manifest.py --mode finalize`; commit the resulting `reference/validation/v1_release/evidence_manifest.json` only if status is `FROZEN`. Then M19 may be PASS.
4. Promote `pyproject.toml` and `CITATION.cff` from `1.0.0.dev0` to the selected candidate/final version (`1.0.0rc1` or `1.0.0`) only after M19 freeze.
5. Remove already-satisfied H100/M19 blockers from the machine index and run `python scripts/check_m20_candidate.py --mode finalize`.
6. Only after M20 final PASS: mark PR #26 ready, merge according to repository policy, and create the corresponding v1.0 candidate/release tag if all required CI is green.

## Integrity rules

Never declare PASS without gate evidence; never tune thresholds/seeds/data/starts/grids/model/optimizer after results; preserve failures and scoped limitation semantics. `PASS_PREFLIGHT` is not final milestone PASS.
