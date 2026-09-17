# P2A.9 Final Semantic Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze and verify the exact pre-execution common-scope protocol that can authorize the first HGFX v1.0.0 ↔ pyhgf 0.3.2 numerical comparison without inspecting cross-tool numerical outcomes first.

**Architecture:** A committed JSON case manifest carries immutable inputs, responses, model/observation parameters, environment pins, compared quantities, tolerances, and result-classification rules. A pure-Python checker validates hashes and schema locally; a dedicated GitHub Actions preflight installs the exact comparator environment, verifies package/runtime identities and public guard settings, and emits environment provenance without running either tool's forward trajectory. Only after that preflight succeeds is the final semantic-gate document allowed to set `benchmark_authorized=true`.

**Tech Stack:** Python 3.12, NumPy, JAX/JAXLIB, HGFX 1.0.0, pyhgf 0.3.2, pytest, GitHub Actions, JSON/SHA-256.

**Spec:** `paper/reproducibility/PAPER_PROTOCOL.md`, especially sections 6.2, 8, 9, and 12; P2A.3–P2A.8 mapping artifacts under `docs/research/` and `paper/reproducibility/`.

## Global Constraints

- HGFX scientific implementation is immutable `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Comparator is immutable `pyhgf==0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`; frozen sdist SHA-256 `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d`.
- Direct common scope is standard three-level binary HGF with mean-field updates, unit value/volatility coupling, zero drift, fully observed finite binary input, unit time, CPU, JAX x64, no pyhgf binary prediction clipping, no posterior-precision cap, and unclipped derived binary surprise.
- No cross-tool trajectory, likelihood, surprise, or error value may be executed or inspected while P2A.9 settings are selected.
- Tolerances, inputs, responses, package versions, and output fields may not be changed after the first authorized numerical result is inspected. A necessary change requires a new protocol version and preservation of the original result.
- Performance/timing comparison remains out of scope under `hgfx-paper-protocol-1`.

---

### Task 1: Freeze the exact common-scope case

**Files:**
- Create: `paper/reproducibility/pyhgf_common_scope_case.json`
- Test: `tests/test_p2a9_preexecution.py`

**Interfaces:**
- Consumes: P2A.4 parameter mapping, P2A.5 initialization mapping, P2A.6 input/masking mapping, P2A.7 output mapping, P2A.8 precision policy.
- Produces: one immutable `case_id`, exact `inputs`, exact `responses`, canonical SHA-256 hashes, inverse temperature, environment pins, output-field list, tolerances, and classification rules.

- [ ] **Step 1: Write the failing tests** for canonical bit-array hashing, manifest integrity, binary values/lengths, expected fixed parameters, and exact prospective tolerances.
- [ ] **Step 2: Run `pytest tests/test_p2a9_preexecution.py -q` and verify RED** because `tools.check_p2a9_preexecution` does not yet exist.
- [ ] **Step 3: Commit the frozen manifest without changing any product runtime source.**

### Task 2: Implement a non-empirical P2A.9 checker

**Files:**
- Create: `tools/check_p2a9_preexecution.py`
- Test: `tests/test_p2a9_preexecution.py`

**Interfaces:**
- Consumes: `paper/reproducibility/pyhgf_common_scope_case.json`.
- Produces: deterministic schema/hash validation plus an optional environment provenance JSON. It must not call `hgf_binary`, `Network.input_data`, response likelihood evaluation, or any other cross-tool scientific execution.

- [ ] **Step 1: Implement `canonical_bit_hash(values)`** using comma-separated ASCII `0`/`1` values with no whitespace.
- [ ] **Step 2: Implement `validate_manifest(data)`** and reject changed hashes, non-binary values, unequal lengths, missing fixed settings, or changed tolerances.
- [ ] **Step 3: Implement `runtime_preflight(data)`** to verify exact Python/core-package versions, CPU backend, JAX x64, installed HGFX/pyhgf identities, `Network` public guard settings, and availability of the unclipped `binary_surprise` API without feeding scientific data through either implementation.
- [ ] **Step 4: Run the focused pytest target and verify GREEN.**

### Task 3: Add and execute the dedicated preflight workflow

**Files:**
- Create: `.github/workflows/p2a9-preflight.yml`
- Output artifact: `p2a9-preflight-environment.json`

**Interfaces:**
- Consumes: exact environment pins from the case manifest and `tools/check_p2a9_preexecution.py`.
- Produces: GitHub run/job identity plus actual Python/NumPy/JAX/JAXLIB/HGFX/pyhgf versions, import locations, OS/platform details, CPU backend and x64 evidence.

- [ ] **Step 1: Configure Ubuntu-only preflight with `JAX_ENABLE_X64=1` and `JAX_PLATFORMS=cpu`.**
- [ ] **Step 2: Install exact prospective versions and run the checker in runtime-preflight mode.**
- [ ] **Step 3: Upload the environment JSON and print it in the log.**
- [ ] **Step 4: Confirm the workflow succeeds before authorizing numerical execution.**

### Task 4: Freeze the final semantic gate

**Files:**
- Create: `docs/research/PYHGF_FINAL_SEMANTIC_GATE.md`
- Create: `paper/reproducibility/pyhgf_final_semantic_gate.json`
- Modify: GitHub issue #33 progress section.

**Interfaces:**
- Consumes: P2A.2–P2A.8 evidence, the exact case manifest, and the successful P2A.9 environment-preflight run.
- Produces: the single pre-execution authorization decision for the first numerical comparator run.

- [ ] **Step 1: Record every semantic restriction carried forward from P2A.2–P2A.8.**
- [ ] **Step 2: Record the exact environment-preflight run ID and verified versions.**
- [ ] **Step 3: Set `FINAL_SEMANTIC_GATE=PASS_FOR_FROZEN_COMMON_SCOPE` and `benchmark_authorized=true` only if all required checks are satisfied.**
- [ ] **Step 4: State that the next action is execution of the already-frozen case with no tolerance/input/version changes.**
- [ ] **Step 5: Run repository regression CI, merge only on PASS, then verify `main` points to the merged commit.**
