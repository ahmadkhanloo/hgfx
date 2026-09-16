# HGFX v1 aggregate evidence index

Last synchronized: 2026-09-16
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Final validated v1.0.0 source target: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`

This index preserves historical failures and distinguishes direct PASS, scoped reference limitations, physical-GPU applicability, frozen release evidence, candidate validation, independent-review findings, remediation evidence, and final `1.0.0` promotion evidence.

## M18/v1 closure evidence

| Surface | Classification | Evidence |
|---|---|---|
| M0–M17 | PASS_IN_DOCUMENTED_SCOPES | milestone evidence |
| Historical M18 scientific experiment | FAIL_PRESERVED | historical evidence |
| D02 exact official scope | REFERENCE_LIMITATION_MATCH | frozen decision JSON |
| D08 exact failed seed | REFERENCE_LIMITATION_MATCH | frozen decision JSON |
| D04 uHGF → AR1 | PASS | recorded MATLAB-equivalence workflow evidence |
| D09 sampleModel | PASS | recorded release workflow evidence |
| D10/D11 analysis surfaces | PASS | post-review run `35080084742`; final-promotion run `35089882668` |
| D12 BPA | PASS | recorded release workflow evidence |
| S7 paired parameter recovery | REFERENCE_LIMITATION_MATCH | scientific result remains FAIL where MATLAB fails |
| S7 paired model selection | PASS_PAIRED_MODEL_SELECTION | 36/36 BIC winners match |
| S8 required repair scope | DONE | repair `0239f52f772825e0a4fc74cdf3559cafa18a603e` |
| S9 CPU robustness/backend | PASS_CPU_BACKEND_EQUIVALENCE | post-review run `35080084517` |
| S9 physical GPU | PASS_PHYSICAL_GPU_APPLICABILITY | source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`; 2x Tesla T4; max objective gap `1.4210854715202004e-14` vs `1e-7` |
| S10 release readiness | PASS | post-review run `35080084519`; final-promotion run `35089882319` |
| M19/M20 preflight | PASS_PREFLIGHT | post-review run `35080084594`; final-promotion run `35089882608` |
| M19 evidence freeze | PASS_FROZEN | committed/finalizer manifest status `FROZEN`, failures empty |
| M20 candidate | PASS_M20_CANDIDATE | run `34989737851`; failures `[]`; artifact `10405351087` |
| Independent final review | REVIEW_COMPLETE | `INDEPENDENT_REVIEW_REPORT.md`; 2 HIGH blockers H1/H2 |
| H1 portability remediation | RESOLVED | portable fdlibm-compatible `exp`/`expm1`/`log`; cross-platform regression run `35080084509` |
| H2 CRLF/hash remediation | RESOLVED | LF/canonicalized reference verification; Windows reference guard PASS in run `35080084509` |
| Post-review full regression | PASS | run `35080084509`, Ubuntu + Windows success; Windows `178 passed, 4 skipped, 0 failed` |
| Full MATLAB Demo Composition | PASS | post-review run `35080084742` |
| PR #29 main integration | PASS | source `ffa84c616343714d7d384b0a21e6f8d73f7cb990`; Regression `35087865209` |
| Final metadata promotion | PASS | `pyproject.toml` + `CITATION.cff` = `1.0.0`; PR #30 head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b` |
| Final promotion PR validation | PASS | S10 `35089882319`; preflight `35089882608`; D10/D11 `35089882668`; Regression `35089882392` |
| Final v1.0.0 main source | PASS | `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; Regression `35090329868` Ubuntu + Windows |
| Git tag / GitHub Release object | PENDING_HOSTING_MECHANIC | must target `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |

## M20 RC evidence

`M20 Finalize v1.0 Candidate` run `34989737851` built a candidate-synchronized M19 manifest with `status=FROZEN`, `failures=[]`, accepted physical NVIDIA GPU evidence, and then returned `PASS_M20_CANDIDATE` for historical candidate version `1.0.0rc1`.

The uploaded M20 manifest artifact is `10405351087`, SHA-256 `d2ecfca5b858705eb36e8f40a6b55ae52ada0871e9e19e66c3bf3f20c5a0631e`.

## Independent review and remediation

The independent report was executed against RC source `ad8f5cd6fbea3bd1e5ac1cef8b51dbbb9a970a84`. It is preserved unchanged in `INDEPENDENT_REVIEW_REPORT.md`.

The two release-blocking HIGH findings were addressed without modifying frozen acceptance criteria:

- H1: host CRT/libm dependence in D02-sensitive `expm1`/`log` paths was replaced by portable binary64 fdlibm-compatible implementations.
- H2: Windows CRLF working-tree expansion no longer causes false frozen-reference/hash failures.

Post-remediation source `09c49031cda95b449f8115030a9d32dcba36098e` passed all active release workflows used for closure:

- `HGFX Regression` `35080084509`: success on Ubuntu 24.04 and Windows Server 2025; Windows `178 passed, 4 skipped`; frozen MATLAB source guard PASS for 334 files.
- `M18 S9 Backend Robustness` `35080084517`: success.
- `S10 v1 Release Readiness` `35080084519`: success.
- `M19 M20 Release Preflight` `35080084594`: success.
- `V1 Full MATLAB Demo Composition` `35080084742`: success.

Full remediation details and the licensing erratum are in `INDEPENDENT_REVIEW_REMEDIATION.md`.

## Final 1.0.0 promotion evidence

Final package/citation metadata were promoted to `1.0.0` on PR #30 head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`. Fresh PR-head evidence on that exact revision:

- `S10 v1 Release Readiness` run `35089882319`: success.
- `M19 M20 Release Preflight` run `35089882608`: success.
- `M18 D10 D11 Analysis Surfaces` run `35089882668`: success.
- `HGFX Regression` run `35089882392`: success on Ubuntu and Windows.

PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Fresh main/push `HGFX Regression` run `35090329868` succeeded on Ubuntu and Windows. This commit is the validated final source target for tag `v1.0.0`.

## Physical-GPU provenance after remediation

The physical-GPU evidence was produced on two Tesla T4 devices at source `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`. Final promotion does not substitute CPU evidence for that run.

Applicability is retained because the tested GPU executable path is unchanged: files under `src/hgfx/gpu/` have the same blob identities at the physical-GPU source and post-review source, and `scripts/run_m18_s9_backend_robustness.py` remains blob `d886819c2ef8fa4969f397310f39ca0ac4b02bc8`. The compatibility-vs-JAX CPU portion was freshly rerun after H1/H2 and passed.

The claim remains limited to numerical applicability of the tested NVIDIA/JAX/CUDA path. It is not an H100-specific or new performance/scaling claim.

## Licensing/provenance note

The frozen HGF Toolbox commit is MIT-licensed. The original independent report contains a factual GPL-v3 wording error in its licensing checklist; the historical report is not rewritten. `INDEPENDENT_REVIEW_REMEDIATION.md` records the correction.

Portable `exp`/`expm1`/`log` routines adapted from fdlibm preserve the applicable Sun Microsystems/SunSoft permission notices in source and are recorded in `THIRD_PARTY_NOTICES.md`.

## Scientific interpretation

None of the review remediation or final-promotion changes alter historical scientific evidence. Exact shared MATLAB/HGFX failures remain scoped `REFERENCE_LIMITATION_MATCH`; they are acceptable only for MATLAB-equivalent product accounting and are not scientific PASS claims. No threshold, seed, dataset, start, model family, optimizer, validation grid, or historical failure was changed to obtain release PASS.

## Current release state

The final `1.0.0` source target is validated at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Scientific, engineering, independent-review, package metadata, PR-head, and main-branch validation gates are closed.

Only the repository-hosting object remains: create Git tag/GitHub Release `v1.0.0` targeting that exact commit and record its URL/identifier in `V1_FINAL_RELEASE_PROVENANCE.md`.
