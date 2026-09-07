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

Bootstrap gate: frozen MATLAB `tapas_logit` fixture → canonical NPZ → independent Python result → reproducible numerical diff.

## Phase 2 — Core schemas
- [ ] Parameters
- [ ] Transforms
- [ ] Priors
- [ ] Fixed/free semantics
- [ ] Placeholders
- [ ] Irregular trial masks
- [ ] Time axis

## Phase 3 — Scalar math
- [ ] logit/sigmoid
- [ ] Boltzmann
- [ ] Lambert W0
- [ ] nearest PSD
- [ ] covariance→correlation
- [ ] Ridders numerical derivatives

## Phase 4 — Shared HGF blocks
- [ ] prediction
- [ ] precision prediction
- [ ] binary level 1
- [ ] binary level 2
- [ ] continuous level 1
- [ ] volatility prediction error
- [ ] volatility update
- [ ] trajectory validation

## Phase 5 — Core model parity
- [ ] standard HGF
- [ ] eHGF
- [ ] uHGF
- [ ] PyHGF dependency/fork decision gate

## Phase 6 — Observation models
- [ ] unit-square sigmoid
- [ ] binary softmax
- [ ] softmax
- [ ] Gaussian
- [ ] remaining response families

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
