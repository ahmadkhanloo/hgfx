# M20 — v1.0 Candidate

Last synchronized: 2026-09-16
Status: **PASS — `PASS_M20_CANDIDATE`**
Branch: `migration/m18-workflow-closure`
Validated revision: `b52dc06ca58d29afeb5c265f7eb67746824178e0`

## Purpose

M20 is the final v1.0 release-candidate gate. It does not reopen scientific validation. It verifies that the accepted MATLAB-equivalence surface, packaging, provenance, metadata and M19 evidence freeze are internally consistent and ready to merge/tag as the `1.0.0rc1` candidate.

Final `1.0.0` promotion remains subject to the independent final-review process in `CHAT_WORKFLOW.md`; M20 PASS is not an independent-review PASS.

## M20 acceptance result

All M20 preconditions are satisfied in the documented release-candidate scope:

- [x] M19 evidence is `FROZEN`.
- [x] S9 physical NVIDIA GPU applicability is PASS under `M18_S9_PHYSICAL_GPU_AMENDMENT.md`.
- [x] S10 release-readiness is PASS.
- [x] Package and citation metadata are `1.0.0rc1` and mutually consistent.
- [x] Historical M18 FAIL and scoped `REFERENCE_LIMITATION_MATCH` evidence remain preserved.
- [x] Required fresh PR workflows on the validated revision are green.
- [x] S7 release accounting preserves `scientific_pass=false` while using the frozen exact-scope `REFERENCE_LIMITATION_MATCH` decision.
- [x] `scripts/check_m20_candidate.py --mode finalize` returned `PASS_M20_CANDIDATE`.

## Exact finalizer evidence

M20 finalizer workflow:

- workflow: `M20 Finalize v1.0 Candidate`
- run: `34989737851`
- source SHA: `b52dc06ca58d29afeb5c265f7eb67746824178e0`
- result: **SUCCESS**
- checker status: `PASS_M20_CANDIDATE`
- version: `1.0.0rc1`
- failures: `[]`
- final manifest artifact: `10405351087`
- artifact SHA-256: `d2ecfca5b858705eb36e8f40a6b55ae52ada0871e9e19e66c3bf3f20c5a0631e`

The candidate-synchronized manifest produced by this run had `status=FROZEN`, `failures=[]`, physical NVIDIA GPU evidence accepted, and source commit equal to the validated SHA.

## Fresh PR checks on the same SHA

The active release checks on `b52dc06ca58d29afeb5c265f7eb67746824178e0` completed successfully:

- M19 M20 Release Preflight `34989742402`
- S10 v1 Release Readiness `34989742503`
- M18 D09 Official sampleModel `34989742408`
- M18 D10 D11 Analysis Surfaces `34989742423`
- M18 Demo uHGF AR1 Workflow Parity `34989742476`
- M18 Demo Model Selection Parity `34989742422`
- M18 S9 Backend Robustness `34989742512`
- HGFX Regression `34989742411`
- M18 D12 Bayesian Parameter Averaging `34989742426`
- M18 S7 Paired Recovery `34989742522`

## Scientific integrity

M20 PASS is release accounting, not a rewrite of scientific history.

- Historical M18 scientific FAIL remains FAIL.
- D02/D08 and exact-grid S7 parameter-recovery limitations remain scoped `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- S7 model selection remains 36/36 BIC-winner agreement.
- No tolerance, seed, dataset, start, validation grid, model family, optimizer, or physical-GPU criterion was changed to obtain M20 PASS.

## Candidate versus final `1.0.0`

M20 PASS permits PR #26 to be made ready/merged and the `1.0.0rc1` candidate to be tagged. Promotion from RC to final `1.0.0` still requires the independent frontier-agent review defined by `CHAT_WORKFLOW.md`, resolution of every Critical/High finding, and a fresh full validation run.
