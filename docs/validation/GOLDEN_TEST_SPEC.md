# Golden Test Specification

## Purpose

Golden tests transform the MATLAB reference implementation into frozen numerical evidence that can be used after MATLAB is no longer available.

## Fixture levels

- G0 scalar math
- G1 building block
- G2 one-step update
- G3 trajectory
- G4 response likelihood
- G5 parameter transforms / priors
- G6 objective
- G7 fitting
- G8 Hessian / covariance / LME
- G9 simulation
- G10 CPU/GPU
- G11 batch/single equivalence
- G12 parameter recovery
- G13 model recovery
- G14 edge cases

## Fixture metadata

Every fixture must record:
- HGF version;
- HGF commit SHA;
- MATLAB version;
- model name;
- response model name;
- optimizer;
- RNG seed;
- fixture schema version.

## First-divergence requirement

Diff tooling must report:
- first failing trial;
- first failing level;
- first failing field;
- expected value;
- actual value;
- absolute difference;
- relative difference.
