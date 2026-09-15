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

1. DONE: maintenance validation and full CPU regression (167 passed, four GPU skips).
2. DONE locally: S10 clean-wheel candidate build/install/quickstart.
3. DONE: M19 release-file hashes refreshed; archived scientific evidence preserved.
4. DONE locally: `check_m20_candidate.py --mode finalize` returned `PASS_M20_CANDIDATE`; output retained.
5. Verify fresh GitHub candidate/regression checks; queued CI is not PASS.
6. Make PR #26 ready/merge/tag only after all mandatory checks and review pass.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, and
`../validation/V1_EVIDENCE_INDEX.md` with machine-readable evidence.
Do not reopen completed D02/D08/S7/S8 diagnostics merely to obtain green runs.
See `CI_MAINTENANCE.md`: archived oracle/diagnostic workflows remain manually
reproducible. Numerical source changes still require relevant oracle and GPU
revalidation. No tolerance, seed, data, grid or historical evidence was changed.

## Maintenance validation — 2026-09-15

CI/docs revision `60472362d05412a35b046b197a32daacc05ebbef` passed local
CPU regression (167 passed, four physical-GPU skips), candidate clean-wheel
build/install/API import/quickstart, and the static reference/release checks.
M19 refresh and the M20 final checker passed locally with no failures.
Evidence: `reference/validation/ci_maintenance_20260915/`.

Fresh GitHub regression `34971334728` and S10 `34971334355` were queued
at inspection. M20/release closure remains IN PROGRESS pending fresh CI;
no merge/tag or new physical-GPU validation is claimed. Classic branch
protection could not be read (403); do not bypass required checks.
