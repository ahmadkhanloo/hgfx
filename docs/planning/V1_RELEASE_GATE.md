# HGFX v1.0 Release Gate

Last synchronized: 2026-09-16
Status: **FINAL `1.0.0` SOURCE PASS — TAG/GITHUB RELEASE OBJECT PENDING**

## Product definition

HGFX v1.0 is a functional/scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`, with no MATLAB runtime dependency for users. Bitwise identity is not generally required except where a frozen compatibility fixture explicitly requires it. Every accepted equivalence or reference limitation must follow the frozen validation policies and preserve failed evidence.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`, `../validation/INDEPENDENT_REVIEW_REMEDIATION.md`, and `../validation/V1_FINAL_RELEASE_PROVENANCE.md` as acceptance/provenance records.

## Mandatory release acceptance criteria

- [x] Required MATLAB model/workflow coverage accounted for under direct PASS / scoped reference-limitation policy.
- [x] Fit, simulation, trajectory and required statistical-output surfaces evidence-backed in documented scopes.
- [x] Paired parameter recovery completed against the same MATLAB oracle/workflow; exact S7 grid is `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- [x] Paired model selection passed with 36/36 BIC winners matching.
- [x] CPU/backend robustness accepted.
- [x] Physical NVIDIA GPU applicability accepted with physical-device evidence.
- [x] Zero MATLAB runtime dependency for users.
- [x] M19 aggregate evidence/provenance freeze completed.
- [x] M20 RC candidate gate returned `PASS_M20_CANDIDATE`.
- [x] Independent frontier review executed against the RC candidate.
- [x] Every Critical/High independent-review finding resolved without changing frozen scientific acceptance criteria.
- [x] Fresh post-remediation cross-platform/release validation green.
- [x] PR #29 merged to `main` and main/push regression green on integration commit `ffa84c616343714d7d384b0a21e6f8d73f7cb990` (run `35087865209`).
- [x] Package/citation metadata promoted from `1.0.0rc1` to `1.0.0`.
- [x] Exact final promotion head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b` passed all active promotion gates.
- [x] Final promotion merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and main regression run `35090329868` passed on Ubuntu and Windows.
- [ ] `v1.0.0` Git tag/GitHub Release object created and its URL/identifier recorded.

## Current evidence snapshot

Historical evidence is preserved; release evidence is additive.

- M0–M17: complete in documented scopes.
- Historical M18 scientific result: **FAIL, preserved**.
- D02 exact official workflow: scoped `REFERENCE_LIMITATION_MATCH` for release accounting only.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265` remains scoped `REFERENCE_LIMITATION_MATCH` for release accounting only.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners match.
- S8 required-scope repair: DONE at `0239f52f772825e0a4fc74cdf3559cafa18a603e`.
- S9 physical GPU: `PASS_PHYSICAL_GPU_APPLICABILITY` on 2x Tesla T4; maximum CPU/GPU objective gap `1.4210854715202004e-14` against frozen `1e-7`.
- M19: **PASS / FROZEN**.
- M20 finalizer: run `34989737851`, **SUCCESS**, `PASS_M20_CANDIDATE`, `failures=[]`.
- Independent review source report: `../validation/INDEPENDENT_REVIEW_REPORT.md`.
- Blocking findings H1/H2: **RESOLVED**, documented in `../validation/INDEPENDENT_REVIEW_REMEDIATION.md`.
- Post-remediation source `09c49031cda95b449f8115030a9d32dcba36098e` passed release workflows `35080084509`, `35080084517`, `35080084519`, `35080084594`, and `35080084742`.
- PR #29 merge/main integration source `ffa84c616343714d7d384b0a21e6f8d73f7cb990`: `HGFX Regression` run `35087865209` **PASS**.
- Final promotion head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`:
  - `S10 v1 Release Readiness` run `35089882319`: **PASS**.
  - `M19 M20 Release Preflight` run `35089882608`: **PASS**.
  - `M18 D10 D11 Analysis Surfaces` run `35089882668`: **PASS**.
  - `HGFX Regression` run `35089882392`: **PASS** on Ubuntu and Windows.
- Final main source target `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`: `HGFX Regression` run `35090329868`: **PASS** on Ubuntu and Windows.

## Physical-GPU evidence boundary

The archived physical run is not replaced by CPU evidence. Its tested JAX GPU execution path is byte-identical to the post-review source: all files under `src/hgfx/gpu/` retain their blob identities from physical-GPU source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`, and `scripts/run_m18_s9_backend_robustness.py` retains blob SHA `d886819c2ef8fa4969f397310f39ca0ac4b02bc8`. Post-review H1 changes affect the MATLAB/CPU compatibility libm path, which was freshly revalidated against the unchanged JAX backend by S9 run `35080084517`.

This preserves the physical-device claim only for the unchanged tested path; it does not make any new H100 or performance/scaling claim.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: prospectively frozen Level-2 numerical protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited; acceptable for v1 MATLAB-equivalence but not a scientific PASS.
- `PASS_PHYSICAL_GPU_APPLICABILITY`: the tested numerical path executed resident on eligible physical NVIDIA hardware and satisfied the frozen CPU-vs-GPU criterion.
- `PASS_FROZEN`: M19 release evidence is frozen and machine-readable.
- `PASS_M20_CANDIDATE`: synchronized RC candidate accounting passes; it is not itself the independent final review.

Historical/direct/prospective failures remain immutable evidence.

## Final `1.0.0` promotion gate

1. **DONE:** independent review and H1/H2 remediation.
2. **DONE:** post-remediation release validation.
3. **DONE:** final package/citation metadata promotion to `1.0.0`.
4. **DONE:** PR #30 exact-head release validation.
5. **DONE:** merge to `main` and fresh Ubuntu/Windows regression on final source target `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
6. **PENDING REPOSITORY-HOSTING MECHANIC:** create `v1.0.0` tag/GitHub Release targeting `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and record the resulting release URL/identifier.

## Integrity

No threshold, seed, dataset, start, grid, model family, optimizer, historical evidence, or physical-GPU acceptance criterion was changed post-hoc to manufacture final PASS. The original independent review remains preserved; remediation and final-promotion evidence are additive.
