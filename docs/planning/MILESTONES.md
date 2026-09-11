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
Parameter recovery and model recovery satisfy preregistered acceptance criteria.

## M19 — Methods Paper Dataset Frozen
Benchmark and validation outputs immutable and reproducible.

## M20 — v1.0 Candidate
All Definition-of-Done checks pass.

## Active repair gates — 2026-09-11

[MATLAB parity recovery plan](MATLAB_PARITY_RECOVERY_PLAN.md) defines R0–R6 without renumbering M0–M20.

- M18: historical FAIL; preserve raw evidence and thresholds.
- M18A: diagnostic PASS within its documented experiment; does not prove paired MATLAB parity on failed datasets.
- M18B: integrity repair implemented; corrected final artifact unverified in this review. PASS means protocol integrity only.
- R1/R2: paired MATLAB numerical-horizon gate before any stability claim.
- R3: same-data MATLAB/Python inference gate before assigning the recovery failure to model limitations.
- R4: separately preregistered scientific protocol; never relabel historical M18.
- R5: family/regime coverage and physical GPU confirmation for changed paths.
- M19/M20: OPEN; no automatic waiver of existing release criteria.

Execution update: corrected M18B local gate PASS with full archived records; paired MATLAB horizon diagnostic confirms 49 valid cases and 5 shared rejection boundaries. See `M18_HORIZON_DIAGNOSIS.md`. M18 remains FAIL; R1 rejected intermediate-state comparison and R3 remain open.

## Verified execution update — 2026-09-11 06:04 UTC

R0 corrected M18B gate is now PASS locally **and in CI** (run `34567774302`, artifact `10186837061`). See `reference/validation/m18b_corrected_ci_provenance.json` and the archived complete local records. This supersedes earlier pending-CI text. Paired MATLAB horizon run `34568178526` also passed within its explicit scope: 49 valid trajectories and 5 shared rejection boundaries. R1 rejected raw intermediates and R3 paired inference remain open. Historical M18 stays FAIL; no scientific release gate is waived.
