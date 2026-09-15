# HGFX v1.0 Live TODO

Last synchronized: 2026-09-15
Status: **IN PROGRESS — M20 FINALIZER ON SYNCHRONIZED RC REVISION**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Accepted evidence

- M0–M17: complete in documented scopes.
- Historical M18 scientific experiment: **FAIL preserved**.
- D02/D08 direct failures and S7 parameter recovery: scoped `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- D04/D09/D10–D11/D12: PASS in recorded scopes.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8 required repair: DONE; numerical repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`.
- S9 CPU: `PASS_CPU_BACKEND_EQUIVALENCE`.
- S9 physical GPU: `PASS_PHYSICAL_GPU_APPLICABILITY`, 2x Tesla T4; maximum CPU/GPU objective gap `1.4210854715202004e-14` versus frozen `1e-7`.
- M19: PASS / FROZEN, run `34966661492`.
- Package and citation: `1.0.0rc1`.
- Fresh candidate revision `5cf17dcd13c9f30dbfcd500ad409d39d41296b20`: all 10 active PR workflows PASS.
- Fresh Regression `34984783677`: 171 passed, 4 physical-GPU skips, 5 warnings.
- Fresh S10 `34984783640`: PASS, wheel artifact `10402688684`.
- Fresh S7 `34984783703`: PASS for release accounting; raw scientific recovery remains FAIL / `scientific_pass=false`, exact-scope release classification remains `REFERENCE_LIMITATION_MATCH`.

## Ordered remaining work

1. DONE: fresh candidate CI on `5cf17dcd13c9f30dbfcd500ad409d39d41296b20`.
2. DONE: S7 release-accounting mismatch fixed without changing scientific criteria or results.
3. IN PROGRESS: synchronize release documents/evidence with the fresh candidate runs.
4. TODO: require `m20-finalize.yml` / `check_m20_candidate.py --mode finalize` to PASS on that synchronized revision.
5. TODO after M20 PASS: mark PR #26 ready, merge it, and create the `1.0.0rc1` candidate tag.
6. TODO before final `1.0.0`: execute the independent final review defined by `CHAT_WORKFLOW.md`, resolve all Critical/High findings, and rerun full validation.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, and
`../validation/V1_EVIDENCE_INDEX.md` with machine-readable evidence.
Do not reopen completed D02/D08/S7/S8 diagnostics merely to obtain green runs.
Archived oracle/diagnostic workflows remain manually reproducible.
Numerical source changes still require relevant oracle and GPU revalidation.
No tolerance, seed, data, grid or historical evidence may be changed to obtain PASS.

M20 is a release-candidate gate. Passing it is sufficient to merge/tag `1.0.0rc1`; it is not a substitute for the independent final review required before promotion to final `1.0.0`.
