# PV1-02 P2 Core Paper Tables Implementation Plan

**Goal:** Generate the six core methods-paper tables from frozen HGFX v1 evidence without manually transcribing scientific results or altering the frozen validation record.

**Architecture:** Add one stdlib-only generator under `paper/scripts/` that reads committed frozen evidence, validates required records, writes six deterministic Markdown tables under `paper/tables/`, and writes a SHA-256 sidecar manifest. Tests regenerate into a temporary directory, assert negative/reference-limitation evidence remains visible, and byte-compare regenerated outputs with the committed tables.

**Tech stack:** Python standard library (`json`, `hashlib`, `pathlib`, `re`), pytest, existing GitHub Actions regression workflow.

**Specification:** `docs/research/PAPER_EXECUTION_PLAN.md` P2 and `paper/reproducibility/PAPER_PROTOCOL.md` section 10.

## Global constraints

- Do not change frozen v1 thresholds, seeds, datasets, starts, grids, model families, optimizers, or historical classifications.
- Preserve historical M18 `FAIL_PRESERVED` evidence.
- Preserve D02/D08 direct failures and their exact-scope `REFERENCE_LIMITATION_MATCH` release disposition.
- Treat physical GPU evidence as correctness/applicability only; do not introduce speed or scaling claims.
- Fail loudly if a required evidence file, evidence ID, or required parsed provenance field is absent.
- Every table row must identify its evidence source.
- Generated outputs must be deterministic from identical committed inputs.

## Task 1 — RED: define generator contract

- [ ] Add `tests/unit/test_paper_table_generation.py` before the generator exists.
- [ ] Verify the focused test fails because the generator/output contract is not implemented.

## Task 2 — Implement evidence-driven generator

- [ ] Add `paper/scripts/generate_core_tables.py`.
- [ ] Read the frozen v1 evidence index/manifest plus exact D02, D08, S7, historical M18, D09, physical-GPU, demo, release, PyPI, and paper-protocol records.
- [ ] Require all expected evidence IDs and provenance fields.
- [ ] Generate:
  1. `model_workflow_coverage.md`
  2. `official_matlab_demo_parity.md`
  3. `fitting_statistics_classification.md`
  4. `recovery_model_selection.md`
  5. `backend_gpu_applicability.md`
  6. `release_reproducibility_provenance.md`
- [ ] Generate `core_tables_manifest.json` with input/output SHA-256 hashes and integrity flags.

## Task 3 — GREEN: freeze generated P2 outputs

- [ ] Run focused paper-table tests.
- [ ] Confirm committed tables are byte-identical to regeneration.
- [ ] Confirm D02/D08 direct failures, historical M18 FAIL, S7 reference limitations, and paired model-selection PASS all remain visible.
- [ ] Confirm GPU table contains the tested 2x Tesla T4 scope and no performance/scaling claim.

## Task 4 — Repository verification and P2 closeout

- [ ] Run the existing regression suite on the feature branch through GitHub Actions.
- [ ] Update `docs/research/PAPER_EXECUTION_PLAN.md`, `docs/research/PAPER_EVIDENCE_MAP.md`, and `docs/planning/V1_TODO.md` only after the P2 acceptance gate is satisfied.
- [ ] Record exact commit SHA and CI run evidence.

## Completion gate

P2 is complete only when all six tables and the sidecar manifest regenerate deterministically from committed evidence, required negative/reference-limitation rows are retained, focused tests pass, and branch regression passes. P2 completion does not imply P2A, P3, P5, P6, P6A, P7, or P8 completion.
