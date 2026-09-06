# Agent Handoff

Use this file when handing the repository to a new coding or review agent.

## Project goal

Build a Python/JAX HGF toolbox with scientific parity to the frozen MATLAB reference and high-throughput GPU fitting.

## First files to read

1. `AGENTS.md`
2. `docs/planning/MIGRATION_MATRIX.md`
3. `docs/planning/EXECUTION_PLAN.md`
4. `docs/planning/ROADMAP.md`
5. `docs/planning/MILESTONES.md`
6. `docs/architecture/NUMERICAL_POLICY.md`
7. `docs/validation/GOLDEN_TEST_SPEC.md`
8. `docs/validation/ACCEPTANCE_CRITERIA.md`

## Current milestone

`M0 — Reference Frozen`

## First tasks

1. Pin exact HGF v8.2.0 commit.
2. Add reference repo as a submodule.
3. Generate `matlab_manifest.tsv`.
4. Generate `matlab_checksums.tsv`.
5. Build the MATLAB golden-fixture exporter.
6. Implement the first vertical slice only after the golden harness works.

## Do not start with

- GPU optimization;
- full repo translation;
- model refactoring;
- plotting;
- performance micro-optimizations.
