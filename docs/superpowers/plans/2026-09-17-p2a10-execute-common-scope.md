# P2A.10 — Execute frozen HGFX ↔ pyhgf common-scope case

Status: IN PROGRESS
Date: 2026-09-17
Protocol: `hgfx-paper-protocol-1`
Case: `p2a9-binary-hgf-common-scope-001`
Tracking: issue #33

## Goal
Execute exactly the P2A.9-authorized 128-trial HGFX v1.0.0 ↔ pyhgf 0.3.2 case without changing inputs, responses, parameters, versions, dtype/guard policy, compared fields, or tolerances.

## Integrity order
1. Validate final-gate authorization and immutable case hashes.
2. Execute both implementations in the exact frozen CPU/x64 environment.
3. Write `p2a10_raw_numeric_result.json` containing per-implementation arrays, dtypes and boundary diagnostics.
4. Compute and embed `raw_result_sha256` over the canonical raw payload, write the file, then reopen and verify it.
5. Only after step 4, compute comparison metrics/classifications and write `p2a10_comparison.json` referencing the verified raw hash.
6. Preserve both files and the workflow environment evidence before updating manuscript/evidence-map claims.

## Frozen execution contract
- `hgfx==1.0.0` source identity: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- `pyhgf==0.3.2` source identity: `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`
- Python 3.12.14; NumPy 2.3.3; JAX/JAXLIB 0.6.2
- Ubuntu 24.04 CPU; `JAX_ENABLE_X64=1`; `JAX_PLATFORMS=cpu`
- pyhgf: `volatility_updates="standard"`, `mean_field_updates=True`, `precision_clipping_value=0.0`, `max_posterior_precision=inf`
- No timing/performance comparison.

## Tasks
- [ ] TDD RED: add focused tests for immutable authorization, native parameter assembly, deterministic raw hashing, comparison metrics and nonfinite classification.
- [ ] TDD GREEN: implement `tools/run_p2a10_common_scope.py` with lazy scientific imports.
- [ ] Add a manual-only GitHub Actions workflow using only exact frozen package versions; do not install HGFX editable from the branch.
- [ ] Verify repository regression on the final runner/workflow head.
- [ ] Dispatch the benchmark workflow exactly once for the frozen case.
- [ ] Download and inspect the raw artifact; verify its embedded SHA-256 before interpreting comparison output.
- [ ] Commit raw result, comparison result and workflow provenance unchanged from the artifact.
- [ ] Update issue #33 and paper evidence map/manuscript comparison text according to the observed classification; do not change the frozen protocol after seeing results.
- [ ] Merge only after fresh regression CI passes.
