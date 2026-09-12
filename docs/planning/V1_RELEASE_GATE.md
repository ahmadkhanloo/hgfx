# HGFX v1.0 Release Gate

## Product Definition

HGFX v1.0 is a functional and scientific replacement for the MATLAB HGF Toolbox.

The v1 target is not only numerical parity of individual algorithms. It is end-to-end workflow compatibility.

## Mandatory Acceptance Criteria

- Complete MATLAB HGF Toolbox model coverage required for v1
- Fit workflow parity
- Simulation workflow parity
- Trajectory output parity
- Hessian/LME/statistical output parity
- Parameter recovery validation
- Model recovery validation
- CPU/GPU numerical agreement within defined tolerances
- Python reproduction of MATLAB demo workflows
- Documentation and examples sufficient for independent usage

## Versioning Rule

Any capability required to reproduce MATLAB HGF Toolbox workflows remains in v1.x.

Capabilities beyond MATLAB Toolbox scope may be scheduled for v2.x.

## Execution and decision rule

Use [M18 completion plan](M18_COMPLETION_PLAN.md), S1–S10. Required MATLAB
functionality must be complete before v1.0; v1.x is not permission to defer missing
replacement functionality past the initial release. Preserve M19/M20 milestone meanings.

Every required validation row needs raw, traceable evidence. Unresolved implementation,
optimizer or model-selection mismatches, missing reference evidence, or incomplete demo
surfaces block release. Exact-case REFERENCE_LIMITATION_MATCH is acceptable under the
reference-limitations policy and must be disclosed; it is not scientific recovery PASS.
Historical M18 FAIL remains unchanged. The aggregate evidence checker is still TODO.

## M18 Release Validation

M18 is the final validation gate for HGFX v1.0 and validates MATLAB Toolbox replacement readiness.

Checklist:

- [ ] Model parity
- [ ] Fit parity
- [ ] Simulation parity
- [ ] Demo parity
- [ ] Recovery validation
- [ ] Robustness validation
- [ ] Release documentation
