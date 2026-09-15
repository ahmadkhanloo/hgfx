# HGFX v1.0 Live TODO

Last synchronized: 2026-09-16
Status: **RC READY — M20 PASS; FINAL `1.0.0` REQUIRES INDEPENDENT REVIEW**
Branch: `migration/m18-workflow-closure`
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
- Candidate metadata: `1.0.0rc1`.
- M20: **PASS** on `b52dc06ca58d29afeb5c265f7eb67746824178e0`; finalizer run `34989737851` returned `PASS_M20_CANDIDATE`, `failures=[]`.
- All active release PR checks on that validated candidate SHA completed successfully.

## Ordered remaining work

1. DONE: release-document/evidence synchronization through M20 PASS.
2. DONE: M20 final candidate gate.
3. NEXT RC INTEGRATION: make PR #26 ready, merge after required checks, and create the `1.0.0rc1` candidate tag/release.
4. REQUIRED BEFORE FINAL `1.0.0`: execute the independent final review defined by `CHAT_WORKFLOW.md` against `FINAL_REVIEW_CHECKLIST.md`.
5. If review reports Critical/High findings: resolve them without changing frozen acceptance criteria, then rerun the relevant oracle/GPU/full-regression validation.
6. Rerun full final validation on the post-review candidate.
7. If and only if final review has no unresolved Critical/High findings and validation is green: promote metadata from `1.0.0rc1` to `1.0.0`, create the final tag/release, and record exact release provenance.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, `FINAL_REVIEW_CHECKLIST.md`, and `../validation/V1_EVIDENCE_INDEX.md` with machine-readable evidence.

Do not reopen completed D02/D08/S7/S8 diagnostics merely to obtain green runs. Historical oracle/diagnostic workflows remain manually reproducible. Numerical source changes require relevant oracle and GPU revalidation. No tolerance, seed, data, grid or historical evidence may be changed to obtain PASS.
