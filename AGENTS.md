# HGFX Agent Instructions

You are working on a scientific software project. Scientific correctness has priority over speed, brevity, or stylistic refactoring.

## Mandatory reading before coding

Read:

- `docs/planning/MIGRATION_MATRIX.md`
- `docs/planning/EXECUTION_PLAN.md`
- `docs/planning/ROADMAP.md`
- `docs/planning/MILESTONES.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/NUMERICAL_POLICY.md`
- `docs/validation/GOLDEN_TEST_SPEC.md`
- `docs/validation/ACCEPTANCE_CRITERIA.md`

## Source of truth

The authoritative reference is a frozen version of the MATLAB HGF Toolbox.

The exact version and commit SHA must be recorded in:

- `reference/HGF_VERSION`
- `reference/HGF_COMMIT`

Do not implement scientific behavior against a moving upstream branch.

## Non-negotiable rules

1. Never translate MATLAB blindly.
2. Never consider a function correct because it runs.
3. Every migrated mathematical component requires a MATLAB golden-reference test or an explicitly approved exception.
4. Use JAX float64 for scientific validation.
5. Establish CPU x64 parity before GPU optimization.
6. Do not increase tolerance simply to make tests pass.
7. On mismatch, locate the **first divergent trial, level, state, and intermediate variable**.
8. Preserve parameter ordering.
9. Preserve transformed/native parameter semantics.
10. Preserve prior semantics.
11. Preserve fixed/free parameter semantics.
12. Preserve irregular-trial behavior.
13. Preserve placeholder semantics.
14. Every implementation PR must reference a Migration Matrix ID.
15. Performance work may start only after correctness gates pass.
16. Do not copy third-party code without preserving provenance and license notices.

## Required implementation sequence

For each migration item:

1. Read the MATLAB source.
2. Extract inputs and outputs.
3. Write the equations in mathematical notation.
4. Enumerate every branch and edge case.
5. Record parameter ordering and transforms.
6. Create or identify golden fixtures.
7. Write failing tests first.
8. Implement the JAX/Python version.
9. Run CPU float64 tests.
10. Produce a numerical diff report.
11. If GPU-critical, run GPU float64 parity tests.
12. Update the Migration Matrix status.
13. Update changelog if user-visible.

## Failure policy

Forbidden:

```text
test fails
→ increase tolerance
→ merge
```

Required:

```text
test fails
→ identify first divergence
→ compare intermediate states
→ identify semantic/numerical cause
→ fix implementation
```

## Completion standard

The definition of complete migration is documented in:

`docs/validation/ACCEPTANCE_CRITERIA.md`

The agent must not declare the project complete until every required criterion is satisfied.
