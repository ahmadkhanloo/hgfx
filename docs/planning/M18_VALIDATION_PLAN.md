# M18 — MATLAB Toolbox Replacement Validation

## Objective

M18 is the final validation gate for HGFX v1.0.

The target is not to prove that base HGF solves every scientific scenario. The target is to reproduce the MATLAB HGF Toolbox capability and workflow.

## Validation Principle

HGFX is validated against MATLAB Toolbox behavior:

- If MATLAB uses HGF, HGFX must reproduce HGF behavior.
- If MATLAB uses eHGF, HGFX must reproduce the eHGF workflow.
- If MATLAB uses uHGF, HGFX must reproduce the uHGF workflow.
- If MATLAB uses a specialized observation model or auxiliary family, HGFX must support the equivalent path.

The reference is the MATLAB Toolbox solution strategy, including known limitations.

## Acceptance Criteria

- [ ] Parameter recovery following MATLAB reference workflows
- [ ] Model recovery following MATLAB reference workflows
- [ ] Robustness sweeps for supported model families
- [ ] CPU/GPU numerical agreement
- [ ] Optimizer agreement
- [ ] Demo workflow reproduction
- [ ] Documentation of MATLAB limitations and HGFX equivalent behavior

## Versioning Rule

Capabilities required to reproduce MATLAB Toolbox behavior remain in HGFX v1.x.

Capabilities beyond MATLAB Toolbox scope may move to v2.x.
