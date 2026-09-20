# P2A.9 Final Semantic Gate Implementation Plan

Status: **COMPLETE / PASS**  
Completed: 2026-09-17  
Merged implementation: PR #43 / `58adbca4fab138792040e9ccb1e909f2f647f33c`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for completed work.

**Goal:** Freeze and verify the exact pre-execution common-scope protocol that can authorize the first HGFX v1.0.0 ↔ pyhgf 0.3.2 numerical comparison without inspecting cross-tool numerical outcomes first.

**Architecture:** A committed JSON case manifest carries immutable inputs, responses, model/observation parameters, environment pins, compared quantities, tolerances, and result-classification rules. A pure-Python checker validates hashes and schema locally; a dedicated GitHub Actions preflight installs the exact comparator environment, verifies package/runtime identities and public guard settings, and emits environment provenance without running either tool's forward trajectory. Only after that preflight succeeds is the final semantic-gate document allowed to set `benchmark_authorized=true`.

**Tech Stack:** Python 3.12, NumPy, JAX/JAXLIB, HGFX 1.0.0, pyhgf 0.3.2, pytest, GitHub Actions, JSON/SHA-256.

**Spec:** `paper/reproducibility/PAPER_PROTOCOL.md`, especially sections 6.2, 8, 9, and 12; P2A.2–P2A.8 mapping artifacts under `docs/research/` and `paper/reproducibility/`.

## Global Constraints

- HGFX scientific implementation is immutable `hgfx==1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Comparator is immutable `pyhgf==0.3.2` @ `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`; frozen sdist SHA-256 `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d`.
- Direct common scope is standard three-level binary HGF with mean-field updates, unit value/volatility coupling, zero drift, fully observed finite binary input, unit time, CPU, JAX x64, no pyhgf binary prediction clipping, no posterior-precision cap, and unclipped derived binary surprise.
- No cross-tool trajectory, likelihood, surprise, or error value may be executed or inspected while P2A.9 settings are selected.
- Tolerances, inputs, responses, package versions, and output fields may not be changed after the first authorized numerical result is inspected. A necessary change requires a new protocol version and preservation of the original result.
- Performance/timing comparison remains out of scope under `hgfx-paper-protocol-1`.

---

### Task 1: Freeze the exact common-scope case — COMPLETE

**Files:**
- `paper/reproducibility/pyhgf_common_scope_case.json`
- `tests/test_p2a9_preexecution.py`

- [x] Write tests for canonical bit-array hashing, manifest integrity, binary values/lengths, expected fixed parameters, and exact prospective tolerances.
- [x] Verify the RED state before implementation. HGFX Regression run #129 (`35265057143`) failed while collecting `tests/test_p2a9_preexecution.py` because the checker was not yet present; frozen-reference and MATLAB-source guards passed first.
- [x] Commit the frozen manifest without changing product runtime/scientific source.

### Task 2: Implement a non-empirical P2A.9 checker — COMPLETE

**Files:**
- `tools/check_p2a9_preexecution.py`
- `tests/test_p2a9_preexecution.py`

- [x] Implement `canonical_bit_hash(values)` using comma-separated ASCII `0`/`1` values with no whitespace.
- [x] Implement `validate_manifest(data)` and rejection of changed hashes, binary contract, fixed settings, field list, or tolerances.
- [x] Implement `runtime_preflight(data)` for exact versions, CPU backend, JAX x64, package identities, public pyhgf guard settings, and unclipped-surprise API availability without scientific data execution.
- [x] Verify GREEN through the complete repository regression suite, which includes `tests/test_p2a9_preexecution.py`; final PR-head HGFX Regression run #138 (`35265721711`) passed on Ubuntu and Windows.

### Task 3: Add and execute the dedicated preflight workflow — COMPLETE

**Files:**
- `.github/workflows/p2a9-preflight.yml`
- Preserved output: `paper/reproducibility/pyhgf_preflight_environment_35265386637.json`

- [x] Configure Ubuntu-only preflight with `JAX_ENABLE_X64=1` and `JAX_PLATFORMS=cpu`.
- [x] Install exact prospective versions and execute the checker in runtime-preflight mode.
- [x] Upload environment JSON and `pip freeze` as an Actions artifact.
- [x] Confirm preflight success before authorization: run #4 / ID `35265386637` passed and supplied the frozen environment artifact; final PR head was reverified by preflight run #7 / ID `35265721724`.

### Task 4: Freeze the final semantic gate — COMPLETE

**Files:**
- `docs/research/PYHGF_FINAL_SEMANTIC_GATE.md`
- `paper/reproducibility/pyhgf_final_semantic_gate.json`
- GitHub issue #33 progress record

- [x] Record every semantic restriction carried forward from P2A.2–P2A.8.
- [x] Record environment-preflight run identity, exact versions, hardware/runtime evidence, artifact ID/digest, and file hashes.
- [x] Set `FINAL_SEMANTIC_GATE=PASS_FOR_FROZEN_COMMON_SCOPE` and `benchmark_authorized=true` only after preflight PASS.
- [x] State the next action as execution of the already-frozen case with no input/response/tolerance/version changes.
- [x] Run repository regression CI, merge only on PASS, and verify `main` points to merged commit `58adbca4fab138792040e9ccb1e909f2f647f33c` before this closeout update.

## Verification evidence

- TDD RED: HGFX Regression #129 / `35265057143` — expected failure before checker implementation.
- Environment/API preflight used for authorization: P2A.9 Comparator Preflight #4 / `35265386637` — PASS, no scientific execution.
- Final-head environment revalidation: P2A.9 Comparator Preflight #7 / `35265721724` — PASS.
- Final-head repository regression: HGFX Regression #138 / `35265721711` — PASS on Ubuntu 24.04 and Windows.
- PR #43 squash-merged to `main`: `58adbca4fab138792040e9ccb1e909f2f647f33c`.

## Exit state

```text
P2A.9 = DONE / PASS
FINAL_SEMANTIC_GATE = PASS_FOR_FROZEN_COMMON_SCOPE
benchmark_authorized = true for p2a9-binary-hgf-common-scope-001 only
cross-tool numerical result = NOT YET EXECUTED
```

The next project action is the first authorized numerical execution of the frozen case. Its raw outputs and SHA-256 must be persisted before interpretation.
