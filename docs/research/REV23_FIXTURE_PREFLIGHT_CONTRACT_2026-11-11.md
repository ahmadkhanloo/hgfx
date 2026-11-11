# REV-2.3 fixture preflight: required manifest contract

**Status: DRAFT TOOL; NO CANONICAL SCIENTIFIC INPUTS CREATED.**

The read-only validator `tools/rev23_fixture_integrity.py` is preparatory infrastructure for [REV-2.3 draft protocol](../../evidence/revision/protocols/REV-2.3_PROTOCOL.md). It must not create or choose scientific data, call MATLAB/JAX/HGFX, time models, infer parity or approve a performance claim.

## Usage after an approved input-selection decision

```bash
python tools/rev23_fixture_integrity.py path/to/candidate_input_manifest.json \
  --report path/to/rev23_fixture_preflight_report.json
```

The input JSON must include `protocol_id: "compstat-rev23-performance-1"`, `hgfx_source_commit: "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"`, `matlab_source_commit: "2437f4dc241541072722a2695ddeca7b44d83dd3"`, and a `workloads` object with **exactly these eleven IDs**: `F128 F1024 F8192 F65536 S128 S512 B1 B32 B256 B1024 D08`.

For **each** workload, required fields are: `trials`, `subjects` matching the approved fixed matrix, `model`, `observation`, `provenance` (actual original data source), `selection_policy` (prospectively approved and specified before selection), and four real file objects: `inputs`, `responses`, `config`, `start`. Each file object contains `{"path": "relative/path/in/manifest/tree", "sha256": "<actual 64-hex SHA256 from file bytes>"}`. Input/response arrays are `.npy` little-endian float64 and must have dimensions `(T,)` for one subject or `(B,T)` for batches. Config is `.json`, starts are `.npy`. Paths may not escape the manifest directory.

**Example of structure only (NON-EXECUTABLE, no fabricated SHA):**

```json
{
  "protocol_id": "compstat-rev23-performance-1",
  "hgfx_source_commit": "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27",
  "matlab_source_commit": "2437f4dc241541072722a2695ddeca7b44d83dd3",
  "workloads": {
    "F128": {
      "trials": 128,
      "subjects": 1,
      "model": null,
      "observation": null,
      "provenance": null,
      "selection_policy": null,
      "inputs": null,
      "responses": null,
      "config": null,
      "start": null
    }
  }
}
```

This example is intentionally invalid: an incomplete cohort, undefined model, and missing authentic fixture files **must fail closed**.

## Source and scientific scope guardrails

- MATLAB `fitModel(y,u)` in frozen 8.2.0 defaults to **eHGF**, while HGFX `fit_model(y,u)` in released 1.0.0 defaults to **HGF**. For `S128/S512`, explicitly specify `hgf_binary_config`, `unitsq_sgm_config`, `quasinewton_optim_config` for both; the validator is **not** an algorithm-equivalence oracle.
- F/B model family and source arrays are **not** fully specified by the original author plan. Do not silently use a prefix, repetition, padding, RNG stream or demo input file as a frozen scientific fixture without independent prospective approval.
- The D08 614-observation seed=123456789 original scientific provenance and **own-endpoint epsi FAIL** remain; do not run a new MATLAB simulation under the exhausted REV-2.2 budget.
- The validator checks file SHA256 and sizes but **does not compare scientific model parameters, priors, full optimizer output, NaN/trial masks, MATLAB struct preparation, host/BLAS affinity or device synchronization**. These are separate mandatory frozen and independently reviewed gates.
- A successful report says only `SOURCE_ONLY_CHECK_PASS`; never treat it as a fit, numerical parity or benchmark PASS.
- Current fixture input manifest: **NOT PRESENT / NOT FROZEN**. Current 44-cell eligibility matrix: all remain `PENDING_INDEPENDENT_REVIEW`. `PERF-01C=BLOCK_FREEZE`; no timing authorized.

## Verification record for this development step

The validator was created and amended in the current GitHub branch; **the validation script itself was not executed in this task** and no unit test/CI outcome is claimed. Before use, a reviewer should execute negative controls for missing IDs, changed shapes, altered SHA, path escapes, default-model mismatch and unauthorized data selection. Its status remains **IMPLEMENTED BUT NOT VALIDATED**.
