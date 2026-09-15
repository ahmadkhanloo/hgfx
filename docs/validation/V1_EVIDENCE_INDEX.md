# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-16
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Release branch: `migration/m18-workflow-closure`

This index preserves historical failures and distinguishes direct PASS, scoped reference limitations, physical-GPU applicability, frozen release evidence, candidate validation and the final independent-review gate.

## M18/v1 closure evidence

| Surface | Classification | Evidence |
|---|---|---|
| M0–M17 | PASS_IN_DOCUMENTED_SCOPES | milestone evidence |
| Historical M18 scientific experiment | FAIL_PRESERVED | historical evidence |
| D02 exact official scope | REFERENCE_LIMITATION_MATCH | frozen decision JSON |
| D08 exact failed seed | REFERENCE_LIMITATION_MATCH | frozen decision JSON |
| D04 uHGF → AR1 | PASS | recorded MATLAB-equivalence workflow evidence |
| D09 sampleModel | PASS | active candidate run `34989742408` |
| D10/D11 analysis surfaces | PASS | active candidate run `34989742423` |
| D12 BPA | PASS | active candidate run `34989742426` |
| S7 paired parameter recovery | REFERENCE_LIMITATION_MATCH | active candidate run `34989742522`; scientific result remains FAIL where MATLAB fails |
| S7 paired model selection | PASS_PAIRED_MODEL_SELECTION | 36/36 BIC winners match |
| S8 required repair scope | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU robustness/backend | PASS_CPU_BACKEND_EQUIVALENCE | active candidate run `34989742512` |
| S9 physical GPU | PASS_PHYSICAL_GPU_APPLICABILITY | source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`; 2x Tesla T4; max objective gap `1.4210854715202004e-14` vs `1e-7` |
| S10 release readiness | PASS | active candidate run `34989742503` |
| M19/M20 preflight | PASS_PREFLIGHT | active candidate run `34989742402` |
| M19 evidence freeze | PASS_FROZEN | committed/finalizer manifest status `FROZEN`, failures empty |
| HGFX regression | PASS | active candidate run `34989742411` |
| M20 candidate | PASS_M20_CANDIDATE | run `34989737851`; source `b52dc06ca58d29afeb5c265f7eb67746824178e0`; failures `[]`; artifact `10405351087` |

Other active candidate workflows on the same source SHA also completed successfully: Demo model selection `34989742422` and Demo uHGF AR1 parity `34989742476`.

## M20 finalizer evidence

`M20 Finalize v1.0 Candidate` run `34989737851` built a candidate-synchronized M19 manifest with:

- `status=FROZEN`;
- `failures=[]`;
- physical NVIDIA GPU evidence accepted;
- source commit `b52dc06ca58d29afeb5c265f7eb67746824178e0`.

It then executed `scripts/check_m20_candidate.py --mode finalize`, which returned:

- `status=PASS_M20_CANDIDATE`;
- `version=1.0.0rc1`;
- `failures=[]`.

The uploaded final manifest artifact is `10405351087`, SHA-256 `d2ecfca5b858705eb36e8f40a6b55ae52ada0871e9e19e66c3bf3f20c5a0631e`.

## Scientific interpretation

The M20 result does not alter historical scientific evidence. Exact shared MATLAB/HGFX failures remain scoped `REFERENCE_LIMITATION_MATCH`; they are accepted only for MATLAB-equivalent product accounting and are not scientific PASS claims. No threshold, seed, dataset, start, model family, optimizer or validation grid was changed to obtain release-candidate PASS.

## Candidate versus final release

The `1.0.0rc1` acceptance surface has no unresolved M20 blocker. PR #26 may be integrated and the RC tag/release created.

Promotion to final `1.0.0` remains subject to the independent frontier-agent review defined by `CHAT_WORKFLOW.md` against `FINAL_REVIEW_CHECKLIST.md`, resolution of all Critical/High findings, and fresh full validation after any changes.
