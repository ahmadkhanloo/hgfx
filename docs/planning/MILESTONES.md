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

Current product closure follows `M18_COMPLETION_PLAN.md` and the frozen reference-limitations policy. Required MATLAB workflow accounting, paired recovery classification, robustness/backend validation and physical NVIDIA GPU applicability are closed in documented scopes. A matched reference limitation is acceptable product evidence, not a scientific-recovery PASS. Existing M18C.2 horizon-analysis issue #21 remains research work rather than a v1 blocker.

## M19 — Methods Paper Dataset Frozen
**PASS / FROZEN.** Historical failures and scoped reference limitations remain preserved in the machine-readable release evidence.

## M20 — v1.0 Candidate
**PASS.** Historical RC candidate metadata were `1.0.0rc1`. Finalizer run `34989737851` on source `b52dc06ca58d29afeb5c265f7eb67746824178e0` returned `PASS_M20_CANDIDATE` with `failures=[]`. M20 is preserved as the release-candidate gate and is not redefined by final promotion.

## Final v1.0.0 Promotion
**SOURCE PASS.** The independent frontier review was completed; H1/H2 were resolved without changing frozen scientific criteria. Final metadata were promoted to `1.0.0` on PR #30 head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`. Active final-promotion gates all passed (`35089882319`, `35089882608`, `35089882668`, `35089882392`). PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, and main regression run `35090329868` passed on Ubuntu and Windows.

The only remaining release mechanic is creation of the `v1.0.0` Git tag/GitHub Release object targeting `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and recording its URL/identifier. This does not reopen scientific validation.
