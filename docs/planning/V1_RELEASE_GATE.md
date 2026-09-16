# HGFX v1.0 Release Gate

Last synchronized: 2026-09-16
Status: **FINAL REVIEW REMEDIATION PASS — READY FOR `1.0.0` PROMOTION AFTER PR #29 MERGE/MAIN VALIDATION**

## Product definition

HGFX v1.0 is a functional/scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`, with no MATLAB runtime dependency for users. Bitwise identity is not generally required except where a frozen compatibility fixture explicitly requires it. Every accepted equivalence or reference limitation must follow the frozen validation policies and preserve failed evidence.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md`, and `../validation/INDEPENDENT_REVIEW_REMEDIATION.md` as acceptance/provenance records.

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
- [ ] PR #29 merged to `main` and required main/push checks green on the integration commit.
- [ ] Final package/citation metadata promoted to `1.0.0` and final release provenance recorded.

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
- Post-remediation validated source: `09c49031cda95b449f8115030a9d32dcba36098e`.
- `HGFX Regression` run `35080084509`: **PASS** on Ubuntu 24.04 and Windows Server 2025; Windows `178 passed, 4 skipped, 0 failed`; frozen MATLAB source verification `PASS`, 334 files.
- `M18 S9 Backend Robustness` run `35080084517`: **PASS**.
- `S10 v1 Release Readiness` run `35080084519`: **PASS**.
- `M19 M20 Release Preflight` run `35080084594`: **PASS**.
- `V1 Full MATLAB Demo Composition` run `35080084742`: **PASS**.

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

The independent review has been executed, its two HIGH blockers have been resolved, and post-fix validation is green. Remaining promotion work is integration/release mechanics rather than an unresolved scientific or High/Critical engineering finding:

1. merge PR #29 after final PR-head checks;
2. verify required main-branch checks on the merge commit;
3. promote package/citation metadata from `1.0.0rc1` to `1.0.0`;
4. run final release checks on that exact revision;
5. create the final tag/release and record exact provenance.

## Integrity

No threshold, seed, dataset, start, grid, model family, optimizer, historical evidence, or physical-GPU acceptance criterion was changed post-hoc to manufacture final PASS. The original independent review remains preserved; remediation evidence is additive.
