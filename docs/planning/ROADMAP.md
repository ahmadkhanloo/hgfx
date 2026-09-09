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
- [x] PyHGF dependency/fork decision gate

M5 CI: `34123043904`.  
M6 CI: `34125217371`.  
M12 decision: frozen MATLAB remains the compatibility specification; PyHGF stays an optional interoperability/comparison target rather than a required dependency or fork.

## Phase 6 — Observation models
- [x] unit-square sigmoid
- [x] binary softmax
- [x] softmax
- [x] Gaussian
- [x] all P0/P1 response families

M7 gate evidence: 12 P0/P1 families match MATLAB trial-wise `logp/yhat/res`, irregular-trial NaN semantics, and total log likelihood. CI run: `34143177077`.

## Phase 7 — Objective and fitting
- [x] priors
- [x] trial likelihood
- [x] total objective
- [x] compatibility quasi-Newton
- [x] multi-start fitting / LME-based restart selection

M8 gate evidence: fixed-vector `hgf_binary + unitsq_sgm` objective decomposition matches frozen `fitModel.m` for regular and ignored/irregular cases, including trial exclusion, `logLl/negLogLl`, Gaussian prior terms, and `negLogJoint`. CI run: `34152468348`.

M9 gate evidence: frozen `quasinewton_optim` behavior and deterministic default MAP fitting (`nRandInit=0`) match MATLAB on a quadratic optimizer oracle and the `hgf_binary + unitsq_sgm` reference fit. CI run: `34161336607`.

M10 gate evidence: numerical Hessian, optimizer-`T` fallback, Sigma/Corr, Laplace LME decomposition, accuracy/complexity, AIC/BIC, and LME-based restart selection match MATLAB. CI run: `34162675825`. Restart selection is validated from MATLAB-exported seeded startpoints; MATLAB-vs-NumPy RNG stream identity is not claimed.

## Phase 8 — Fit statistics
- [x] Hessian
- [x] covariance
- [x] correlation
- [x] AIC
- [x] BIC
- [x] LME
- [x] accuracy/complexity decomposition

## Phase 9 — Simulation
- [x] simModel parity
- [x] sampleModel parity
- [x] seeded tests
- [x] distributional tests

M11 gate evidence: frozen `simModel.m` / `sampleModel.m` orchestration, parameter transforms, ignored-trial behavior, deterministic response probabilities, MATLAB-exported prior random drivers, same-runtime seed reproducibility, and stochastic distribution checks pass. CI run: `34167613757`. Cross-language RNG-stream identity is not claimed.

## Phase 10 — Complete model family coverage (M12 PASS)
- [x] PU / PU-TBT — HGF/eHGF/uHGF
- [x] AR1 — continuous + binary HGF/eHGF/uHGF coverage
- [x] MAB — binary MAB, AR1 MAB, AR1 binary MAB HGF/eHGF/uHGF
- [x] JGET — HGF/eHGF/uHGF
- [x] categorical — categorical + categorical-normalized
- [x] RW / dual-RW
- [x] Pearce-Hall
- [x] Sutton K1
- [x] Kalman
- [x] HMM / HHMM
- [x] WhatWorld / WhichWorld
- [x] Bayes-optimal auxiliary families
- [x] response-speed / squared-PE auxiliary families
- [x] remaining conditional/world observation families
- [x] zero scientific REFERENCE_ONLY families
- [x] exhaustive config/transform/public-API closure
- [x] final complete-model MATLAB parity CI

M12 was reopened because the project goal is full computational coverage, not inventory-only coverage. Corrected M12 now passes with zero scientific REFERENCE_ONLY families and a green full regression suite. Evidence: M12A `34224773192`; M12B/C `34224773186`; M12D/E `34225650007`; M12F/G `34225649883`; config/prior `34224773097`; exhaustive closure `34225650015`.

## Phase 11 — API compatibility (M13 PASS)
- [x] MATLAB-style result object for fit/sim/sample
- [x] `p_prc`, `p_obs`, `traj`, `optim`, `yhat`, `res`
- [x] 1-based `irr` / `ign` metadata
- [x] `to_dict(matlab_style=True)`
- [x] Python-first and MATLAB-style public entry points
- [x] downstream consumer compatibility tests
- [x] full regression gate

M13 gate evidence: workflow `34234431858`; reference freeze PASS; API/consumer suite 13 passed; full regression 71 passed.

## Phase 12 — Native GPU engine (M14 — implementation complete, GPU gate pending)
- [x] `lax.scan` trial recursion
- [x] subject/same-shape `vmap` primitive
- [x] restart/objective `vmap` primitive
- [x] `jit` forward/objective
- [x] explicit compile signature/cache
- [x] trial-length bucketing/padding
- [x] explicit device placement and CPU x64 device-residency tests
- [x] compatibility-vs-JAX CPU forward/objective parity
- [ ] physical GPU x64 forward/objective parity

CPU evidence: M14 workflow `34242409271`; 9 M14 tests passed; full regression 80 passed; the single physical-GPU test was skipped because no GPU device exists on the hosted runner.

## Phase 13 — GPU fitting (M15 — implementation complete, GPU gate pending)
- [x] differentiable fast objective/grad gate
- [x] optimizer abstraction
- [x] JAX BFGS implementation
- [x] on-device optimizer state
- [x] final-objective / trajectory equivalence on CPU x64
- [x] strict physical GPU fitting parity harness
- [ ] physical GPU fitting parity

M15 is not formal PASS until a real GPU confirms CPU/GPU objective, fitted parameter, trajectory, and device-residency parity. See `docs/planning/M15_GATE.md`.

## Phase 14 — Batch engine (M16)
- [ ] subject batching
- [ ] restart batching
- [ ] model scheduler
- [ ] single-vs-batch equivalence

## Phase 15 — Multi-GPU (M17)
- [ ] independent data-parallel batches
- [ ] device scheduler
- [ ] multi-GPU benchmarks

## Phase 16 — Scientific validation
- [ ] parameter recovery
- [ ] model recovery
- [ ] robustness sweep
- [ ] CPU/GPU agreement
- [ ] optimizer agreement

## Phase 17 — Methods paper
- [ ] benchmark protocol freeze
- [ ] benchmark runs
- [ ] validation figures
- [ ] recovery figures
- [ ] speedup figures
- [ ] manuscript
- [ ] reproducibility package
