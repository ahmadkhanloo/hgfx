# HGFX v1.0 Live TODO

Last synchronized: 2026-09-15
Status: **IN PROGRESS — M20 CANDIDATE VALIDATION / FRESH CI**
Branch: `migration/m18-workflow-closure`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Accepted evidence

- M0–M17: complete in documented scopes.
- Historical M18 scientific experiment: **FAIL preserved**.
- D02/D08 direct failures and S7 parameter recovery: scoped `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- D04/D09/D10–D11/D12: PASS in recorded scopes.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners.
- S8 required repair: DONE; numerical repair `0239f52f772825e0a4fc74cdf3559cafa18a603e`.
- S9 CPU: `PASS_CPU_BACKEND_EQUIVALENCE`, run `34901924475`.
- S9 physical GPU: `PASS_PHYSICAL_GPU_APPLICABILITY`, 2x Tesla T4;
  evidence commit `7179484ce782c25d6edde34cc56a0d689831e1cc`.
  Maximum objective gap `1.4210854715202004e-14` versus frozen `1e-7`.
- Historical S10 release preparation: PASS, run `34934079865`.
- M19: PASS / FROZEN, initial run `34966661492`; candidate manifest at `a032ca5d1779a5d7f61673969e16f2025c0037ed`.
- Package and citation: `1.0.0rc1`.

## Ordered remaining work

1. Verify maintenance changes and full CPU regression once; keep all tests.
2. Run S10 clean-wheel candidate build/install/quickstart on the updated revision.
3. Refresh M19 release-file hashes, preserving archived scientific evidence.
4. Run `python scripts/check_m20_candidate.py --mode finalize` and retain output.
5. Verify fresh GitHub candidate/regression checks; queued CI is not PASS.
6. Make PR #26 ready/merge/tag only after all mandatory checks and review pass.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, and
`../validation/V1_EVIDENCE_INDEX.md` with machine-readable evidence.
Do not reopen completed D02/D08/S7/S8 diagnostics merely to obtain green runs.
See `CI_MAINTENANCE.md`: archived oracle/diagnostic workflows remain manually
reproducible. Numerical source changes still require relevant oracle and GPU
revalidation. No tolerance, seed, data, grid or historical evidence was changed.
