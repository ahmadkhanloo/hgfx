# HGFX v1 Product Definition

## Objective

HGFX v1.0 is intended to be a Python replacement of the MATLAB HGF Toolbox.

The goal is not only algorithmic implementation or numerical parity of isolated functions. The v1 release target is functional, scientific, and workflow compatibility with the MATLAB HGF Toolbox.

## v1 Release Criteria

HGFX v1 must provide:

- Equivalent model coverage
- Equivalent fitting workflow
- Equivalent simulation workflow
- Equivalent trajectory outputs
- Equivalent optimization behaviour within calibrated numerical tolerances
- Hessian/LME/statistical analysis compatibility
- Parameter and model recovery validation
- Python reproductions of official MATLAB Toolbox demonstrations

## Primary Product Acceptance Test

A user should be able to reproduce the core MATLAB HGF Toolbox demo workflows in Python using HGFX and obtain scientifically equivalent results.

Demo parity is a release gate, not an optional example.

## Versioning Rule

Any capability required for MATLAB HGF Toolbox equivalence belongs to HGFX v1.x.

Capabilities beyond MATLAB Toolbox functionality may be scheduled for HGFX v2.x.

## Validation Philosophy

GPU acceleration, batching, and performance improvements are secondary to scientific compatibility. No optimization is accepted if it changes validated scientific behaviour.
