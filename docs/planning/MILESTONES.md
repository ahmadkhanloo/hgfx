# Milestones and Gates

## M0 — Reference Frozen
Pass only if exact version, commit, source manifest, and checksums are recorded.

## M1 — Golden Harness Operational
Pass only if one MATLAB case can be exported, loaded in Python, and diffed reproducibly.

## M2 — Parameter/Config Parity
Pass only if parameter order, transforms, priors, fixed/free semantics, placeholders, and masks match.

## M3 — Scalar Numerical Parity
Pass only if utility-level golden tests pass in CPU float64.

## M4 — HGF Forward Parity
Pass only if standard HGF trajectories match within calibrated tolerance.

## M5 — eHGF Forward Parity
Same gate for eHGF.

## M6 — uHGF Forward Parity
Must separately validate Lambert W0, dual approximation logic, variational weighting, and mixture moments.

## M7 — Observation Parity
P0/P1 observation families must match trial-wise and total likelihoods.

## M8 — Objective Parity
At fixed parameter vectors, objective decomposition must match.

## M9 — Compatibility Fitting
MAP objective and fit behavior must be scientifically equivalent on reference fixtures.

## M10 — Hessian/LME Parity
Hessian, covariance, correlation, AIC, BIC, LME and decomposition validated.

## M11 — Simulation Parity
sim/sample behavior validated.

## M12 — Specialized Model Coverage
Every frozen source/model family has a final migration status.

## M13 — API Compatibility
Downstream scripts can consume compatibility results with minimal changes.

## M14 — GPU Engine
CPU/GPU float64 forward and objective parity validated.

## M15 — GPU Fitting
On-device optimization validated.

## M16 — Batch Engine
Batch result equals repeated single-fit result within tolerance.

## M17 — Multi-GPU
Scaling validated.

## M18 — Scientific Recovery
Historical scientific gate: parameter recovery and model recovery satisfy preregistered
acceptance criteria; the recorded FAIL is preserved. M18B protocol-integrity PASS is separate.

Current product closure additionally follows [M18 completion plan](M18_COMPLETION_PLAN.md)
S1–S10 and the reference-limitations policy: reproduce all required MATLAB workflows,
classify recovery with paired evidence, close robustness/backend checks. A matched reference
limitation is acceptable product evidence, not a scientific recovery PASS. Product closure OPEN.
Existing M18C.2 horizon-analysis issue #21 retains its identifier.

## M19 — Methods Paper Dataset Frozen
Benchmark and validation outputs immutable and reproducible.

## M20 — v1.0 Candidate
All Definition-of-Done checks pass.
