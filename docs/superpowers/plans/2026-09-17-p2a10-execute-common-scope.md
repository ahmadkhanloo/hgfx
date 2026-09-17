# P2A.10 — Execute frozen HGFX ↔ pyhgf common-scope case

Status: **COMPLETE / MERGED / FINAL CI PASS**
Date: 2026-09-17
Protocol: `hgfx-paper-protocol-1`
Case: `p2a9-binary-hgf-common-scope-001`
Tracking: issue #33 / PR #44

## Goal
Execute exactly the P2A.9-authorized 128-trial HGFX v1.0.0 ↔ pyhgf 0.3.2 case without changing inputs, responses, parameters, versions, dtype/guard policy, compared fields, or tolerances.

## Scientific result

```text
COMMON_SCOPE_NUMERICAL_RESULT = PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES
perceptual_and_inference_quantities = 11 / 11 PASS_FOR_EXECUTED_QUANTITY
participant_response_nll_per_trial = NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY
participant_response_nll_total = NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY
post_result_changes_applied = false
```

Scientific run: `35268575414` / job `105361841212` / head `af9000f59ecb156a92cae6fcd063b8b8b9730dd1` — SUCCESS.  
Artifact: `10517407320`; archive SHA-256 `ca449164064a2f345f73ee08098fe1c6e5aa8f4b7d45166723ed850f177d5e53`.  
Canonical raw-result SHA-256: `202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b`.

## Final integration evidence

- PR #44 final validated head: `a80d74e2b77db6dec4c718f50defc1c13ec4067c`.
- Final cross-platform regression: `HGFX Regression` #151 / run `35269599451` — **PASS** on Ubuntu 24.04 and Windows.
- Ubuntu result: `194 passed, 4 skipped, 5 warnings`; frozen-reference guard PASS; frozen MATLAB source classification PASS.
- Windows result: `194 passed, 4 skipped, 5 warnings`; frozen-reference guard PASS; frozen MATLAB source classification PASS.
- PR #44 squash merge commit: `e8160d4874f2c3bce5c0492c6986b4b4e2717ffb`.
- The merge did not alter the frozen P2A case, tolerances, package versions, numerical policy, or scientific classification.

## Integrity order
1. Validate final-gate authorization and immutable case hashes.
2. Execute both implementations in the exact frozen CPU/x64 environment.
3. Write `p2a10_raw_numeric_result.json` containing per-implementation arrays, dtypes and boundary diagnostics.
4. Compute and embed `raw_result_sha256` over the canonical raw payload, write the file, then reopen and verify it.
5. Only after step 4, compute comparison metrics/classifications and write `p2a10_comparison.json` referencing the verified raw hash.
6. Preserve both files and the workflow environment evidence before updating manuscript/evidence-map claims.

All six steps were followed. The raw artifact was also independently downloaded and rehashed outside the scientific workflow before the comparison artifact was interpreted.

## Frozen execution contract
- `hgfx==1.0.0` source identity: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- `pyhgf==0.3.2` source identity: `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`
- Python 3.12.14; NumPy 2.3.3; JAX/JAXLIB 0.6.2
- Ubuntu 24.04 CPU; `JAX_ENABLE_X64=1`; `JAX_PLATFORMS=cpu`
- pyhgf: `volatility_updates="standard"`, `mean_field_updates=True`, `precision_clipping_value=0.0`, `max_posterior_precision=inf`
- No timing/performance comparison.

## Workflow trigger note
The available repository connector did not expose a workflow-dispatch write action at the time of execution. To execute directly without asking for a manual UI action, the benchmark workflow was implemented as a **one-shot branch/path-limited push workflow**: it ran only when `.github/workflows/p2a10-common-scope.yml` was first added on `paper/p2a10-execute-common-scope`. Later result/evidence commits did not match its path filter, and merging to `main` did not match its branch filter. This operational trigger substitution did not alter any scientific setting or frozen acceptance criterion.

## Tasks
- [x] TDD RED: add focused tests for immutable authorization, native parameter assembly, deterministic raw hashing, comparison metrics and nonfinite classification. Evidence: HGFX Regression #141 / `35267813986`, Ubuntu: 6 expected failures because the runner was absent; 188 other tests passed, 4 GPU tests skipped.
- [x] TDD GREEN: implement `tools/run_p2a10_common_scope.py` with lazy scientific imports. Ubuntu full regression on HGFX Regression #142 passed before scientific execution.
- [x] Add the one-shot GitHub Actions execution workflow using only exact frozen package versions; HGFX was installed as `hgfx==1.0.0`, not editable from the branch.
- [x] Verify fresh repository regression on the final evidence/documentation head on both Ubuntu and Windows: run `35269599451`, `194 passed, 4 skipped` on each OS.
- [x] Execute the benchmark workflow exactly once for the frozen case: run `35268575414` — SUCCESS.
- [x] Download and inspect the raw artifact; independently verify embedded SHA-256 `202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b` before interpreting comparison output.
- [x] Commit raw result, comparison result and resolved environment unchanged from the artifact. Evidence-ingest run `35268965774` verified archive/file hashes and byte-for-byte copies; evidence commit `0c5611500a71ce8a7d7c4cb75e434a5bec224d29`.
- [x] Update issue #33 and paper evidence map/manuscript comparison text according to the observed classification without changing the frozen protocol. Paper-sync run `35269395863` — SUCCESS; issue comment `5720618907`.
- [x] Merge only after fresh regression CI passes; PR #44 squash-merged as `e8160d4874f2c3bce5c0492c6986b4b4e2717ffb` after final Ubuntu/Windows PASS.
- [x] Verify the P2A closeout is represented in the repository; broader paper planning remains current with P2A complete and P3 active.
