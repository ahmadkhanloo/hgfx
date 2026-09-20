# Paper

Status: **PV1-02 ACTIVE / POST-M19 / WORKING MANUSCRIPT CREATED**
Tracking: GitHub issue #32

HGFX v1.0.0 is released and the M19 evidence manifest is frozen. Publication work is now a separate post-v1 objective; it does not reopen the closed v1 release gate.

## Paper objective

The primary claim is **validated Python/JAX reproduction of the frozen MATLAB HGF Toolbox 8.2.0 scientific/workflow behavior in documented scopes, with no MATLAB runtime dependency for users**.

Accelerator support is secondary. Physical GPU correctness/applicability may be reported from the frozen v1 evidence. Speed and scaling require a separate prospectively frozen paper benchmark before they can become headline results.

Historical parameter-recovery failures and exact-scope `REFERENCE_LIMITATION_MATCH` results remain visible and are not scientific PASS claims.

## Current assets

- `manuscript.md` — evidence-backed working manuscript synchronized to v1.0.0.
- `references.bib` — initial verified bibliography.
- `../docs/research/PAPER_EXECUTION_PLAN.md` — ordered publication work and submission gate.
- `../docs/research/LEVEL2_PAPER_PLAN.md` — scientific positioning and research questions.
- `../docs/research/PAPER_EVIDENCE_MAP.md` — claim-to-evidence authority.
- `../docs/research/BENCHMARK_PLAN.md` — benchmark/provenance discipline.
- `../docs/validation/V1_EVIDENCE_INDEX.md` — frozen v1 release evidence authority.

## Current readiness

- Released product/evidence baseline: **READY / FROZEN**.
- Working manuscript: **CREATED / IN PROGRESS**.
- Core manuscript narrative for v1 equivalence: **DRAFTED from committed evidence**.
- Paper-specific generated tables/figures: **OPEN**.
- Paper-specific reproducibility bundle: **OPEN**.
- Trial-horizon/identifiability study: **OPEN / recommended for stronger methods claim** (PV1-01 / issue #21).
- Fresh performance/scaling benchmark: **OPEN / required only if speed/scaling is a headline claim**.
- Authors/affiliations/target-journal formatting/declarations: **OPEN**.
- Independent pre-submission manuscript audit: **OPEN / final gate**.

## Planned structure

```text
paper/
  README.md
  manuscript.md
  references.bib
  figures/                   # generated from committed machine-readable evidence
  tables/                    # generated from committed machine-readable evidence
  scripts/                   # regeneration scripts
  reproducibility/           # frozen paper protocol, environments, commands, hashes
  supplement/                # extended matrices and numerical case studies
```

Directories are created when their first tracked artifact is added; empty directories are not required in Git.

## Evidence discipline

Do not manually promote transient debugging values into final paper results. Every numerical claim must map through `PAPER_EVIDENCE_MAP.md` to a stable protocol, source/reference SHA, machine-readable artifact, and provenance record.

New paper-only experiments must be defined and committed before their final execution. Historical failed experiments remain part of the scientific record and are never overwritten by a later protocol or repair.

## Submission gate

The manuscript is submission-ready only when the acceptance criteria in `../docs/research/PAPER_EXECUTION_PLAN.md` are satisfied: generated evidence tables/figures, reproducibility package, complete metadata/declarations, claim audit, and an independent review with no unresolved CRITICAL/HIGH findings.
