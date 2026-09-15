# HGFX v1.0 Live TODO

Last synchronized: 2026-09-15
Status: **IN PROGRESS — FINAL EXTERNAL GPU EVIDENCE DEFERRED**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Authority

Use this file with `M18_COMPLETION_PLAN.md`, `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, and exact-scope decision records under `reference/validation/`.

HGFX v1.0 targets functional/scientific equivalence with the frozen MATLAB toolbox, not global bitwise identity. Never change thresholds, seeds, datasets, starts, validation grids, model family, or optimizer settings after seeing results to obtain PASS.

## DONE / accepted release accounting

- M0-M17: completed in documented scopes.
- Historical M18 scientific experiment: **FAIL, preserved**.
- D02 direct fit: **FAIL preserved**; exact official release scope: `REFERENCE_LIMITATION_MATCH`.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265`: `REFERENCE_LIMITATION_MATCH`.
- D04: PASS, run `34763542557`.
- D09: PASS, run `34842943557`.
- D10/D11: PASS, run `34847266268`.
- D12: PASS, run `34854238549`.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS; run `34896442847`, artifact `10370615292`, SHA-256 `3ba9fc576a2b6a909ef05837bf5039e0b6b2f887356bff9614fdc1e958a1ef92`.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners match.
- S8: **DONE** for required v1 scope; semantic repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`; no unresolved required S7-derived mismatch.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`; run `34901924475`, job `104169632034`, artifact `10371308067`, SHA-256 `875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826`.
- S10: **PASS**. Latest current-preparation-head rerun `34934079865`, artifact `10383235791`, SHA-256 `8abf4488e91c6ae28983c318670f4a92dfab57c4acc8caad494be02fca47eb2b`.
- M19 evidence-freeze preflight: **PASS_PREFLIGHT**, run `34934079973`, job `104268154143`.
- M20 candidate preflight: **PASS_PREFLIGHT**, same run/job.
- M19/M20 preflight artifact: `10383425031`, SHA-256 `3f711a260f68ff0454d18b2b09b3645d28ab5b370384c8729d4fd431bee5e7cf`.

## BLOCKED / DEFERRED — S9 physical H100

This is the only missing external evidence. The user has explicitly deferred execution until later.

Required frozen acceptance:

- execute the same repaired S9 numerical path on a physical H100;
- actual GPU residency must be demonstrated;
- JAX CPU-vs-GPU final-objective gap must be `<= 1e-7`;
- hardware/runtime/command/source commit/environment limitations must be recorded;
- no CPU/mock evidence may substitute.

Do not add new scientific validation while this is deferred.

## PREPARED / BLOCKED — M19

- [x] Evidence-freeze gate document exists.
- [x] Machine-readable manifest builder exists.
- [x] Non-GPU preflight passes.
- [ ] Physical H100 evidence passes.
- [ ] Run `scripts/build_v1_evidence_manifest.py --mode finalize`.
- [ ] Commit `reference/validation/v1_release/evidence_manifest.json` with status `FROZEN`.

M19 is not PASS until all unchecked items above are satisfied.

## PREPARED / BLOCKED — M20

- [x] Candidate gate document exists.
- [x] Candidate preflight checker exists.
- [x] Package/citation metadata are on development v1 line (`1.0.0.dev0`) with no placeholder `TBD`.
- [x] Non-GPU M20 preflight passes.
- [ ] M19 is `FROZEN`.
- [ ] Promote version/CITATION to the chosen release-candidate/final version.
- [ ] Update release evidence index/blockers from physical-H100/M19 evidence.
- [ ] Run `scripts/check_m20_candidate.py --mode finalize`.
- [ ] Make PR ready/merge/tag only after final candidate gate passes.

## Closed historical diagnostics

S8 negative-precision/precheck workflows deliberately probe a parameter region where frozen MATLAB itself can raise `Negative posterior precision`. They are preserved for provenance/manual reproduction but are not ordinary PR/release gates after S8 closure. Their historical failures do not reopen S7/S8.

## Status vocabulary

Use only evidence-backed **DONE/PASS**, **IMPLEMENTED BUT NOT VALIDATED**, **IN PROGRESS**, **BLOCKED**, **OPEN/TODO**. `PASS_PREFLIGHT` is preparation evidence, not final milestone PASS.
