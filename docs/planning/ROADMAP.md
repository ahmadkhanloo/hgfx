# HGFX Roadmap

## Active correction sequence — 2026-09-11

Follow [MATLAB parity recovery plan](MATLAB_PARITY_RECOVERY_PLAN.md): R0 evidence integrity → R1 paired 512-trial reproduction → R2 reference-backed repair → R3 paired M18 inference → R4 independent recovery protocol → R5 coverage/GPU confirmation → R6 release. These are repair steps, not replacements for milestone numbers. Historical checks below retain their original scope and commit. M18 remains FAIL; corrected M18B evidence is unverified; M19/M20 remain OPEN.

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

## Phase 12 — Native GPU engine (M14 PASS)
- [x] `lax.scan` trial recursion
- [x] subject/same-shape `vmap` primitive
- [x] restart/objective `vmap` primitive
- [x] `jit` forward/objective
- [x] explicit compile signature/cache
- [x] trial-length bucketing/padding
- [x] explicit device placement and CPU x64 device-residency tests
- [x] compatibility-vs-JAX CPU forward/objective parity
- [x] physical GPU x64 forward/objective parity

CPU evidence: M14 workflow `34242409271`; 9 M14 tests passed; full regression 80 passed. Physical H100 evidence on 2026-09-09 at stacked commit `45139c07ec90a7558e3ace0d36fb7a56754539c1`: strict M14 test 1 passed in 4.95s; combined M14–M16 strict suite 20 passed in 112.97s. See `docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## Phase 13 — GPU fitting (M15 PASS)
- [x] differentiable fast objective/grad gate
- [x] optimizer abstraction
- [x] JAX BFGS implementation
- [x] on-device optimizer state
- [x] final-objective / trajectory equivalence on CPU x64
- [x] strict physical GPU fitting parity harness
- [x] physical GPU fitting parity

M15 physical H100 fitting parity is PASS on 2026-09-09: strict M15 test 1 passed in 14.43s; combined M14–M16 strict suite 20 passed in 112.97s. See `docs/planning/M15_GATE.md` and `docs/planning/M14_M16_H100_GPU_EVIDENCE.md`.

## Phase 14 — Batch engine (M16 PASS — GPU validated)
- [x] subject batching
- [x] restart batching
- [x] model scheduler
- [x] single-vs-batch equivalence
- [x] heterogeneous-length bucketing
- [x] compile-cache reuse
- [x] device-resident batch outputs
- [x] physical GPU batch parity/device residency

M16 CPU/JAX evidence: workflow `34253080856`; frozen reference PASS; targeted batch suite 5 passed; full regression 88 passed with 2 GPU-only skips. Physical H100 evidence on 2026-09-09: strict M16 test 1 passed in 21.87s and combined M14–M16 strict suite 20 passed in 112.97s. Throughput/scaling benchmarks remain M17/Methods work. See `docs/planning/M16_GATE.md`.

## Phase 15 — Multi-GPU (M17 PASS)
- [x] independent data-parallel batches
- [x] device scheduler
- [x] physical two-GPU numerical parity/device residency
- [x] shared-server multi-GPU scaling benchmark

M17 physical correctness is PASS. Shared-server scaling on H100 measured 1.000× / 1.107× /
1.388× speedup at 1 / 2 / 4 GPUs respectively, with corresponding throughput of 0.783 /
0.867 / 1.087 subjects/s. Because the production GPU node could not be made fully idle,
these results are explicitly treated as realistic contended-node performance rather than
uncontended peak scaling. See `docs/planning/M17_H100_GPU_EVIDENCE.md`.

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
