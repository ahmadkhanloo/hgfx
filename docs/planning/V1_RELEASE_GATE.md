# HGFX v1.0 Release Gate

Last synchronized: 2026-09-16
Status: **RC GATE PASS — M20 `PASS_M20_CANDIDATE`; FINAL `1.0.0` REVIEW REMAINS**

## Product definition

HGFX v1.0 is a functional/scientific Python replacement for frozen MATLAB HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`, with no MATLAB runtime dependency for users. Bitwise identity is not generally required. Every accepted equivalence or reference limitation must follow the frozen validation policies and preserve failed evidence.

Use `../validation/MATLAB_EQUIVALENCE_POLICY.md`, `../validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`, and `../validation/M18_S9_PHYSICAL_GPU_AMENDMENT.md` as acceptance policy.

## Mandatory RC acceptance criteria

- [x] Required MATLAB model/workflow coverage accounted for under direct PASS / scoped reference-limitation policy.
- [x] Fit, simulation, trajectory and required statistical-output surfaces evidence-backed in documented scopes.
- [x] Paired parameter recovery completed against the same MATLAB oracle/workflow; exact S7 grid is `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- [x] Paired model selection passed with 36/36 BIC winners matching.
- [x] CPU/backend robustness accepted.
- [x] Physical NVIDIA GPU applicability accepted.
- [x] Zero MATLAB runtime dependency for users.
- [x] M19 aggregate evidence/provenance freeze completed.
- [x] Candidate package/citation metadata set to `1.0.0rc1`.
- [x] Fresh release checks green on the validated candidate revision.
- [x] M20 finalizer returned `PASS_M20_CANDIDATE`.

## Current evidence snapshot

Historical evidence is preserved; release evidence is additive.

- M0–M17: complete in documented scopes.
- Historical M18 scientific result: **FAIL, preserved**.
- D02 exact official workflow: scoped `REFERENCE_LIMITATION_MATCH` for release accounting only.
- D08 prospective Level-2 holdout: **FAIL preserved**; exact failed seed `314159265` is a scoped `REFERENCE_LIMITATION_MATCH` for release accounting only.
- S7 parameter recovery: exact-grid `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- S7 model selection: `PASS_PAIRED_MODEL_SELECTION`, 36/36 BIC winners match.
- S8 required-scope repair: DONE at `0239f52f772825e0a4fc74cdf3559cafa18a603e`.
- S9 CPU/backend: `PASS_CPU_BACKEND_EQUIVALENCE`.
- S9 physical GPU: `PASS_PHYSICAL_GPU_APPLICABILITY` on 2x Tesla T4; maximum CPU/GPU objective gap `1.4210854715202004e-14` against frozen `1e-7`.
- M19: **PASS / FROZEN**.
- M20 validated source: `b52dc06ca58d29afeb5c265f7eb67746824178e0`.
- M20 finalizer: run `34989737851`, **SUCCESS**, `PASS_M20_CANDIDATE`, `failures=[]`.
- M20 manifest artifact: `10405351087`, SHA-256 `d2ecfca5b858705eb36e8f40a6b55ae52ada0871e9e19e66c3bf3f20c5a0631e`.
- Active PR checks on the same source SHA: all active release workflows completed successfully.

## Accepted result semantics

- `PASS`: frozen direct gate passes.
- `PASS_NUMERICAL_EQUIVALENCE_ENDPOINT_SENSITIVITY`: prospectively frozen Level-2 numerical protocol passes.
- `PASS_INFERENTIAL_EQUIVALENCE`: separately preregistered inference-level protocol passes all required quantities.
- `REFERENCE_LIMITATION_MATCH`: exact paired MATLAB limitation, disclosed and scope-limited; acceptable for v1 MATLAB-equivalence but not a scientific PASS.
- `PASS_PHYSICAL_GPU_APPLICABILITY`: the current numerical path executes resident on eligible physical NVIDIA hardware and satisfies the frozen CPU-vs-GPU criterion.
- `PASS_FROZEN`: M19 release evidence is frozen and machine-readable.
- `PASS_M20_CANDIDATE`: synchronized `1.0.0rc1` candidate accounting passes; it is not an independent final-review result.

Historical/direct/prospective failures remain immutable evidence.

## RC closure

There is no unresolved scientific or engineering blocker inside the documented `1.0.0rc1` acceptance surface after M20 PASS. PR #26 may be made ready/merged and the RC tag may be created.

## Final `1.0.0` promotion gate

Final `1.0.0` is intentionally stricter than M20. Per `CHAT_WORKFLOW.md`, promotion requires:

1. freeze the RC candidate;
2. provide the frozen repository to an independent frontier coding/reasoning agent;
3. review against `FINAL_REVIEW_CHECKLIST.md` without modifying acceptance criteria during the review;
4. resolve every Critical/High finding;
5. rerun full validation after fixes;
6. only then promote package/citation metadata and create the final `1.0.0` release.

M20 PASS must not be reported as completion of this independent review.

## Integrity

No threshold, seed, dataset, start, grid, model family, optimizer, historical evidence, or physical-GPU acceptance criterion may be changed post-hoc to manufacture final PASS.
