# PV1-02 P2 Core Paper Tables Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the six P2 manuscript tables deterministically from frozen, machine-readable HGFX v1 evidence, with explicit evidence provenance and failure on missing required inputs.

**Architecture:** `paper/reproducibility/core_tables_spec.json` defines table rows as JSON-pointer-like field selections from frozen evidence files and immutable literal labels only. `paper/scripts/generate_core_tables.py` validates every required source, resolves fields, renders Markdown and CSV, and writes a machine-readable output manifest. Tests verify missing-source failure, preservation of FAIL/REFERENCE_LIMITATION_MATCH classifications, and byte-for-byte regeneration of committed outputs.

**Tech Stack:** Python 3.11 standard library (`json`, `csv`, `hashlib`, `pathlib`, `argparse`), pytest.

**Spec:** `docs/research/PAPER_EXECUTION_PLAN.md` P2 and `paper/reproducibility/PAPER_PROTOCOL.md`.

## Global Constraints

- Frozen HGFX product source remains `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Frozen MATLAB oracle remains `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Do not alter historical thresholds, seeds, datasets, grids, model families, optimizers, or classifications.
- D02/D08 direct failures must remain visible beside `REFERENCE_LIMITATION_MATCH` release classifications.
- Historical M18 `FAIL_PRESERVED` and S7 scientific non-PASS must remain visible.
- A missing required source or field is a hard error; no row may be silently dropped.
- Generated numerical/categorical cells come from machine-readable evidence, not hand-transcribed narrative values.

---

### Task 1: Lock the generator contract with failing tests

**Files:**
- Create: `tests/test_paper_core_tables.py`

**Interfaces:**
- Consumes: repository files named by the future spec.
- Produces: expectations for `paper/scripts/generate_core_tables.py` CLI and outputs.

- [ ] **Step 1:** Add a test invoking `python paper/scripts/generate_core_tables.py --check`; expect exit 0 once implemented.
- [ ] **Step 2:** Assert exactly six table stems are generated: `model_workflow_coverage`, `official_demo_parity`, `fitting_statistics_classification`, `recovery_model_selection`, `backend_gpu_applicability`, `release_reproducibility_provenance`.
- [ ] **Step 3:** Assert generated content includes `FAIL_PRESERVED` and `REFERENCE_LIMITATION_MATCH`, including D02 and D08 direct-gate evidence.
- [ ] **Step 4:** Run `pytest -q tests/test_paper_core_tables.py` before implementation and preserve the expected RED result caused by the missing generator.
- [ ] **Step 5:** Commit the failing test.

### Task 2: Add a source-only table specification

**Files:**
- Create: `paper/reproducibility/core_tables_spec.json`

**Interfaces:**
- Consumes: frozen JSON evidence under `benchmarks/`, `reference/validation/`, and `gpu_validation_results/`.
- Produces: declarative row/column mapping consumed by the generator.

- [ ] **Step 1:** Define the six table IDs, titles, columns, required sources, and row mappings.
- [ ] **Step 2:** Use source fields for classifications, metrics, run IDs, artifact IDs, hardware, criterion values, and hashes; literals are limited to stable row labels/descriptions.
- [ ] **Step 3:** Add explicit D02/D08 fields for both direct `FAIL_PRESERVED` and release `REFERENCE_LIMITATION_MATCH`.
- [ ] **Step 4:** Add S7 parameter-recovery metrics and `36/36` model-selection evidence from `m18_s7_reference_limitation/decision.json`.
- [ ] **Step 5:** Reference the v1 release evidence manifest/index for release/backend provenance and the M18 validation matrix for coverage.

### Task 3: Implement deterministic generation and validation

**Files:**
- Create: `paper/scripts/generate_core_tables.py`

**Interfaces:**
- Consumes: `core_tables_spec.json` and all referenced source JSON files.
- Produces: six `.md`, six `.csv`, and `paper/tables/core_tables_manifest.json`.

- [ ] **Step 1:** Implement strict JSON loading and dotted-path resolution; raise on missing files, fields, duplicate table IDs, or malformed rows.
- [ ] **Step 2:** Render Markdown with an `Evidence` column and CSV with identical logical cells.
- [ ] **Step 3:** Compute SHA-256 for every required input and generated output and write `core_tables_manifest.json` with generator/source identity.
- [ ] **Step 4:** Implement `--check` to regenerate in memory and fail if any committed output differs or is missing.
- [ ] **Step 5:** Run focused tests and correct only generator/spec defects; do not change scientific source evidence.

### Task 4: Generate and commit the six P2 tables

**Files:**
- Create: `paper/tables/model_workflow_coverage.md`, `.csv`
- Create: `paper/tables/official_demo_parity.md`, `.csv`
- Create: `paper/tables/fitting_statistics_classification.md`, `.csv`
- Create: `paper/tables/recovery_model_selection.md`, `.csv`
- Create: `paper/tables/backend_gpu_applicability.md`, `.csv`
- Create: `paper/tables/release_reproducibility_provenance.md`, `.csv`
- Create: `paper/tables/core_tables_manifest.json`

**Interfaces:**
- Consumes: generator + frozen source evidence.
- Produces: manuscript-ready deterministic P2 outputs.

- [ ] **Step 1:** Run `python paper/scripts/generate_core_tables.py`.
- [ ] **Step 2:** Run `python paper/scripts/generate_core_tables.py --check` and require exit 0.
- [ ] **Step 3:** Run `pytest -q tests/test_paper_core_tables.py` and require PASS.
- [ ] **Step 4:** Run the full `pytest -q` suite in CI on Ubuntu and Windows.
- [ ] **Step 5:** Commit outputs only after regeneration checks pass.

### Task 5: Synchronize publication planning and evidence map

**Files:**
- Modify: `docs/research/PAPER_EXECUTION_PLAN.md`
- Modify: `docs/research/PAPER_EVIDENCE_MAP.md`
- Modify: `docs/planning/V1_TODO.md`

**Interfaces:**
- Consumes: verified generated outputs and CI evidence.
- Produces: repo continuity showing P2 status and next work.

- [ ] **Step 1:** Mark P2 DONE only after generator `--check` and CI pass.
- [ ] **Step 2:** Link all six generated tables and `core_tables_manifest.json` in the paper evidence map.
- [ ] **Step 3:** Keep P2A and P3 open/in-progress; do not imply completion of comparator or prospective recovery analysis.
- [ ] **Step 4:** Record exact implementation PR/head/CI run identifiers after verification.

### Task 6: Integration gate

**Files:** No scientific source changes permitted.

- [ ] **Step 1:** Review branch diff and confirm only paper tooling/tests/generated outputs/planning docs changed.
- [ ] **Step 2:** Confirm no frozen evidence JSON changed.
- [ ] **Step 3:** Require green `HGFX Regression` on Ubuntu and Windows for the final head.
- [ ] **Step 4:** Merge only after all checks are green and report exact merge SHA and workflow run IDs.
