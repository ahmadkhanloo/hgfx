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
Historical scientific gate: parameter recovery and model recovery satisfy preregistered acceptance criteria; the recorded FAIL is preserved. M18B protocol-integrity PASS is separate.

Current product closure follows [M18 completion plan](M18_COMPLETION_PLAN.md) S1–S10 and the reference-limitations policy. Required MATLAB workflow accounting, paired recovery classification, robustness/backend validation, physical NVIDIA GPU applicability, S10 release readiness, and M19 evidence freeze are closed in their documented scopes. A matched reference limitation is acceptable product evidence, not a scientific recovery PASS. Fresh candidate CI on `5cf17dcd13c9f30dbfcd500ad409d39d41296b20` passed all 10 active PR workflows, including S7, S9, S10, regression and D09–D12. Existing M18C.2 horizon-analysis issue #21 retains its identifier.

## M19 — Methods Paper Dataset Frozen
**PASS / FROZEN.** Workflow run `34966661492` committed the machine-readable frozen evidence manifest at commit `b71301b978e07cb0fa5ac2ad14cc92235fadc5ee`. Historical failures and scoped reference limitations remain preserved.

## M20 — v1.0 Candidate
**FINALIZER PENDING ON SYNCHRONIZED REVISION.** Candidate metadata is `1.0.0rc1`. Fresh candidate CI is green at `5cf17dcd13c9f30dbfcd500ad409d39d41296b20`; PASS still requires `PASS_M20_CANDIDATE` from the finalizer on the release-document/evidence synchronization revision. M20 PASS permits merge/tag of `1.0.0rc1`; final `1.0.0` promotion remains subject to the independent final-review process in `CHAT_WORKFLOW.md`.
