# HGFX v1.0 Live TODO

Last synchronized: 2026-09-16
Status: **FINAL `1.0.0` SOURCE PASS — TAG/GITHUB RELEASE OBJECT PENDING**
Branch: `main`
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
- PR #29 merged to `main` at `ffa84c616343714d7d384b0a21e6f8d73f7cb990`; main `HGFX Regression` run `35087865209`: PASS.
- Final package/citation metadata: `1.0.0`.
- PR #30 final-promotion head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`:
  - S10 run `35089882319`: PASS.
  - M19/M20 preflight run `35089882608`: PASS.
  - D10/D11 run `35089882668`: PASS.
  - Regression run `35089882392`: PASS on Ubuntu and Windows.
- PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; main Regression run `35090329868`: PASS on Ubuntu and Windows.

## Ordered remaining work

1. **DONE:** M20 RC gate and evidence freeze.
2. **DONE:** independent final review.
3. **DONE:** resolve all Critical/High review findings (H1/H2).
4. **DONE:** rerun post-fix cross-platform regression and release gates.
5. **DONE:** merge PR #29 and verify its main integration.
6. **DONE:** promote package/citation metadata to `1.0.0` on PR #30.
7. **DONE:** validate PR #30 exact head, merge to `main`, and verify final main source target `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
8. **PENDING REPOSITORY-HOSTING MECHANIC:** create `v1.0.0` Git tag/GitHub Release targeting `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, then record its URL/identifier in `../validation/V1_FINAL_RELEASE_PROVENANCE.md`.
9. Non-blocking review findings (M1/L1/L2) remain maintenance items and must not be used to rewrite historical scientific evidence.

## Continuation policy

Use `V1_RELEASE_GATE.md`, `M19_GATE.md`, `M20_GATE.md`, `FINAL_REVIEW_CHECKLIST.md`, `../validation/V1_EVIDENCE_INDEX.md`, `../validation/V1_FINAL_RELEASE_PROVENANCE.md`, and `../validation/INDEPENDENT_REVIEW_REMEDIATION.md` as the continuity set.

Do not reopen completed D02/D08/S7/S8 diagnostics merely to manufacture a green scientific result. Historical failures remain immutable. No tolerance, seed, data, grid, model family, optimizer, or acceptance threshold may be changed post-hoc to obtain PASS.
