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
