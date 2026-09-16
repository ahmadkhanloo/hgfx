# HGFX v1.0 Live TODO

Last synchronized: 2026-09-16
Status: **POST-INDEPENDENT-REVIEW REMEDIATION PASS — FINAL `1.0.0` PROMOTION NEXT**
Branch: `fix/independent-review-high-findings` (PR #29 -> `main`)
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Accepted evidence

- M0–M17: complete in documented scopes.
- Historical M18 scientific experiment: **FAIL preserved**.
- D02/D08 direct failures and exact-grid S7 parameter recovery: scoped `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- D04/D09/D10–D11/D12: PASS in recorded scopes.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8 required repair: DONE.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`.
- S9 physical GPU: `PASS_PHYSICAL_GPU_APPLICABILITY` on 2x Tesla T4; maximum CPU/GPU objective gap `1.4210854715202004e-14` against frozen `1e-7`.
- M19: PASS / FROZEN.
- M20 RC candidate gate: **PASS**, `PASS_M20_CANDIDATE`.
- Independent frontier review: completed; original report preserved in `../validation/INDEPENDENT_REVIEW_REPORT.md`.
- Review blockers H1/H2: **RESOLVED** without changing thresholds, seeds, data, grids, model family, optimizer, or historical evidence.
- Post-remediation source `09c49031cda95b449f8115030a9d32dcba36098e`:
  - Regression run `35080084509`: PASS on Ubuntu and Windows; Windows `178 passed, 4 skipped, 0 failed`, frozen MATLAB reference 334/334 verified.
  - S9 run `35080084517`: PASS.
  - S10 run `35080084519`: PASS.
  - M19/M20 preflight run `35080084594`: PASS.
  - Full MATLAB Demo Composition run `35080084742`: PASS.
- Remediation/provenance record: `../validation/INDEPENDENT_REVIEW_REMEDIATION.md`.

## Ordered remaining work

1. **DONE:** M20 RC gate and evidence freeze.
2. **DONE:** independent final review.
3. **DONE:** resolve all Critical/High review findings (H1/H2).
4. **DONE:** rerun post-fix cross-platform regression and release gates.
5. **NEXT:** merge PR #29 to `main` after the final PR-head checks are green.
6. **NEXT:** verify required push/main checks on the merge commit.
7. **NEXT:** promote `pyproject.toml` and `CITATION.cff` from `1.0.0rc1` to `1.0.0`, run the final release checks, and record the exact final commit/tag/release provenance.
8. Non-blocking review findings (M1/L1/L2) remain maintenance items and must not be used to rewrite historical scientific evidence.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, `FINAL_REVIEW_CHECKLIST.md`, `../validation/V1_EVIDENCE_INDEX.md`, and `../validation/INDEPENDENT_REVIEW_REMEDIATION.md` as the continuity set.

Do not reopen completed D02/D08/S7/S8 diagnostics merely to manufacture a green scientific result. Historical failures remain immutable. No tolerance, seed, data, grid, model family, optimizer, or acceptance threshold may be changed post-hoc to obtain PASS.
