# HGFX

**HGFX — A GPU-Native Python Toolbox for Hierarchical Gaussian Filters**

HGFX is a scientific reimplementation and extension framework for the Hierarchical Gaussian Filter (HGF), designed for:

- numerical/scientific parity with a frozen reference release of the MATLAB HGF Toolbox;
- Python-first workflows;
- JAX-based automatic differentiation;
- CPU and GPU execution from the same computational core;
- high-throughput batch fitting;
- extensible HGF/eHGF/uHGF and custom models;
- parameter recovery, model recovery, and rigorous benchmarking.

## Project status

Early research-engineering scaffold.

The project is intentionally test-first. A component is **not considered migrated** merely because it executes; it is accepted only when it passes the required numerical reference tests.

## Scientific objective

The target is not bit-for-bit equality across hardware. The target is **scientific and numerical equivalence within calibrated floating-point tolerances**, with explicit validation against frozen MATLAB reference outputs.

## Reference implementation

The reference HGF Toolbox is kept as a development-time oracle only.

Runtime goal:

```text
MATLAB dependency = 0
```

## Core documents

Read these before implementing:

1. `docs/planning/MIGRATION_MATRIX.md`
2. `docs/planning/EXECUTION_PLAN.md`
3. `docs/planning/ROADMAP.md`
4. `docs/planning/MILESTONES.md`
5. `docs/architecture/ARCHITECTURE.md`
6. `docs/architecture/NUMERICAL_POLICY.md`
7. `docs/validation/GOLDEN_TEST_SPEC.md`
8. `docs/validation/ACCEPTANCE_CRITERIA.md`

## Initial vertical slice

The first end-to-end target is:

```text
3-level binary HGF
    ↓
unit-square sigmoid response
    ↓
trial likelihood
    ↓
total objective
    ↓
MAP fitting
    ↓
Hessian / covariance
    ↓
LME / AIC / BIC
```

## Publication goal

The intended research output is a **methods-level paper**, not only a software note.

See:

`docs/research/LEVEL2_PAPER_PLAN.md`

## License

HGFX project code is intended to be MIT-licensed unless a future dependency or copied component requires a different compatible notice.

Third-party source must never be copied without preserving its provenance and license.
