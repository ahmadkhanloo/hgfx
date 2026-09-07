# HGFX Roadmap

## Phase 0 — Freeze reference
- [x] Freeze HGF reference version
- [x] Record exact commit SHA
- [x] Add pinned reference as submodule
- [x] Generate recursive MATLAB manifest
- [x] Generate immutable per-file content hashes (Git blob SHA; SHA-256 generator included)

Reference: HGF 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3` (334 MATLAB files)

## Phase 1 — Golden harness
- [x] MATLAB fixture exporter
- [x] Python fixture schema
- [x] Fixture loader
- [x] Numerical diff reporter

## Phase 2 — Core schemas
- [x] Parameters
- [x] Transforms
- [x] Priors
- [x] Fixed/free semantics
- [x] Placeholders
- [x] Irregular trial masks
- [x] Time axis

Gate evidence: config/parameter parity CI `34088423448`.

## Phase 3 — Scalar math
- [x] logit/sigmoid
- [x] Boltzmann
- [x] Lambert W0
- [x] nearest PSD
- [x] covariance→correlation
- [x] Ridders numerical derivatives

Gate evidence: scalar parity CI `34114052778`.

## Phase 4 — Shared HGF blocks
- [x] prediction
- [x] precision prediction
- [x] binary level 1
- [x] binary level 2
- [x] continuous level 1
- [x] volatility prediction error
- [x] volatility update
- [x] trajectory validation

Gate evidence: HGF forward parity CI `34120120732`.

## Phase 5 — Core model parity
- [x] standard HGF
- [x] eHGF
- [x] uHGF
- [ ] PyHGF dependency/fork decision gate

M5 CI: `34123043904`.  
M6 CI: `34125217371`.

## Phase 6 — Observation models
- [x] unit-square sigmoid
- [x] binary softmax
- [x] softmax
- [x] Gaussian
- [x] all P0/P1 response families

M7 gate evidence: 12 P0/P1 families match MATLAB trial-wise `logp/yhat/res`, irregular-trial NaN semantics, and total log likelihood. CI run: `34143177077`.

## Phase 7 — Objective and fitting
- [ ] priors
- [ ] trial likelihood
- [ ] total objective
- [ ] compatibility quasi-Newton
- [ ] multi-start fitting

## Phase 8 — Fit statistics
- [ ] Hessian
- [ ] covariance
- [ ] correlation
- [ ] AIC
- [ ] BIC
- [ ] LME
- [ ] accuracy/complexity decomposition

## Phase 9 — Simulation
- [ ] simModel parity
- [ ] sampleModel parity
- [ ] seeded tests
- [ ] distributional tests

## Phase 10 — Specialized model families
- [ ] PU / PU-TBT
- [ ] AR1
- [ ] MAB
- [ ] JGET
- [ ] categorical
- [ ] RW / dual-RW
- [ ] Pearce-Hall
- [ ] Kalman
- [ ] HMM / HHMM
- [ ] WhatWorld / WhichWorld
- [ ] Bayes-optimal families

## Phase 11 — Native GPU engine
- [ ] `lax.scan`
- [ ] `vmap`
- [ ] `jit`
- [ ] compile cache
- [ ] trial-length bucketing
- [ ] on-device optimizer state

## Phase 12 — Batch fitting
- [ ] subject batching
- [ ] restart batching
- [ ] model scheduler
- [ ] single-vs-batch equivalence

## Phase 13 — Multi-GPU
- [ ] independent data-parallel batches
- [ ] device scheduler
- [ ] multi-GPU benchmarks

## Phase 14 — Scientific validation
- [ ] parameter recovery
- [ ] model recovery
- [ ] robustness sweep
- [ ] CPU/GPU agreement
- [ ] optimizer agreement

## Phase 15 — Methods paper
- [ ] benchmark protocol freeze
- [ ] benchmark runs
- [ ] validation figures
- [ ] recovery figures
- [ ] speedup figures
- [ ] manuscript
- [ ] reproducibility package
