# Methods-Level Paper Plan

Last synchronized: 2026-09-13
Status: **IN PROGRESS — manuscript evidence not frozen**

## Working title

**HGFX: A Python/JAX Reproduction of the Hierarchical Gaussian Filter Toolbox with Validated Scientific and GPU-Compatible Workflows**

The title is provisional. The final title must reflect the evidence that survives M19 freeze; GPU/scaling claims must not outrank MATLAB-equivalence unless the final benchmark evidence supports them.

## Current paper objective

The primary scientific/software claim for v1 is no longer merely that HGFX implements HGF-like algorithms or provides GPU acceleration. HGFX v1.0 is intended to be a Python replacement for the frozen MATLAB HGF Toolbox 8.2.0 reference at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`.

The paper must therefore establish, with paired evidence, that HGFX reproduces the reference toolbox's required model coverage, fitting and simulation workflows, trajectories, likelihood/objective calculations, model-quality statistics, official demonstrations, and scientifically relevant recovery behavior without requiring MATLAB at user runtime.

GPU acceleration, batching, differentiability and multi-GPU execution are secondary methodological contributions. They are publishable only where they preserve the validated scientific behavior of the compatibility path.

## Publication position

Primary target: a computational methods/software-methods paper with two linked contributions:

1. **Reference-faithful Python reproduction** of the MATLAB HGF Toolbox, including explicit treatment of reference limitations and model-family choices.
2. **Scalable modern execution paths** (JAX/CPU/GPU/batch/multi-GPU) whose scientific outputs are checked against the compatibility/reference path.

A software-only article remains a fallback if the final recovery/scaling evidence does not support the stronger methods positioning.

## Core research questions

### RQ1 — Functional and numerical equivalence
Can HGFX reproduce the frozen MATLAB toolbox's required configurations, parameter transforms, trajectories, observation likelihoods, objectives, fitting outputs, Hessian/covariance/statistics and simulation workflows within predeclared tolerances?

### RQ2 — Workflow equivalence
Can official MATLAB demo/workflow behavior be reproduced in Python using the same model family, observation model, data, priors, fixed/free parameters, starts, seeds/stochastic drivers and workflow semantics?

### RQ3 — Recovery equivalence
When MATLAB and HGFX are run under matched protocols, do parameter-recovery and model-recovery conclusions agree? A MATLAB limitation may be reported as a matched reference limitation; it must not be relabeled as scientific recovery PASS.

### RQ4 — Numerical reproducibility across runtimes
Which elementary floating-point/runtime differences are scientifically irrelevant, and which are amplified by finite-difference gradients or optimization enough to require compatibility handling? Can such cases be isolated with regression evidence rather than post-hoc tolerance changes?

### RQ5 — Backend equivalence
Do compatibility CPU, JAX CPU and physical-GPU paths preserve required scientific outputs on the validated workload surface?

### RQ6 — Performance and scaling
After scientific equivalence is established, how do runtime, throughput, compilation overhead and memory scale with trials, subjects, model candidates, restarts and device count?

## Required evidence hierarchy

Paper claims must be sourced in this order:

1. frozen reference identity and manifests;
2. milestone/gate documents and machine-readable validation artifacts;
3. paired MATLAB/HGFX raw outputs;
4. CI run/job/artifact provenance;
5. paper tables/figures generated from frozen machine-readable data.

Do not promote an engineering observation to a paper result until it has a stable protocol, provenance and acceptance interpretation.

## Experimental program

### Experiment 1 — Reference and configuration equivalence
Covers reference freeze, model/config inventory, parameter order/transforms, priors, fixed/free semantics, placeholders, masks and public compatibility surface.

Primary sources: M0–M2 and M12–M13 evidence.

### Experiment 2 — Numerical forward/observation/objective equivalence
Paired MATLAB vs HGFX comparisons for scalar primitives, HGF/eHGF/uHGF forward trajectories, observation likelihoods and fixed-parameter objective decomposition.

Primary sources: M3–M8.

### Experiment 3 — Fitting and model-quality equivalence
Matched fitting workflows using the MATLAB-compatible optimization path, including MAP/final parameters, trajectories, predictions/residuals, Hessian, covariance/correlation, AIC/BIC/LME and optimizer-path diagnostics where required.

Primary sources: M9–M10 plus the M18 official workflow-closure evidence.

### Experiment 4 — Simulation and official workflow reproduction
Reproduce required MATLAB simulation/demo workflows, including correct model-family selection and documented reference limitations.

Primary sources: M11–M13, D01–D12 workflow matrix and M18 product-closure evidence.

### Experiment 5 — Parameter and model recovery
Run paired MATLAB/HGFX recovery under the same data, candidate models, seeds, priors, parameterization and selection rule. Historical failed recovery experiments remain part of the provenance and are not overwritten by redesigned protocols.

Primary sources: historical M18, M18A/M18B, and product-level paired recovery work in M18 S7/S8.

### Experiment 6 — CPU/GPU/backend agreement
Validate required outputs across compatibility CPU, JAX CPU and physical GPU. GPU claims require physical-device evidence; CPU or mocked-device results are not substitutes.

Primary sources: M14–M16 plus M18 S9 applicability audit.

### Experiment 7 — Scaling and throughput
Measure realistic scientific workloads across subjects, trials, model candidates, restarts and GPU count. Report cold compile separately from steady-state execution and distinguish throughput from scientific compatibility.

Primary sources: M17 and final paper benchmark matrix.

### Experiment 8 — Numerical compatibility case studies
Only scientifically consequential cases belong here. Detailed debugging remains in repository artifacts/supplement.

Current candidate: D02, where sub-ULP/ULP elementary/runtime differences are amplified by Ridders finite differences and quasi-Newton fitting. As of run `34776952053` at head `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`, the selected residual case is classified `FORWARD_NUMERICAL_DIVERGENCE`; replaying observation arithmetic on exact MATLAB state removes the log-likelihood mismatch. This is **diagnostic evidence, not a closed result**.

## Metrics

Scientific metrics:
- configuration/parameter identity;
- trajectory absolute/relative error;
- per-trial and total likelihood error;
- objective and objective-decomposition error;
- optimizer-path/final-parameter agreement where required;
- Hessian/covariance/correlation error;
- AIC/BIC/LME agreement;
- parameter-recovery metrics;
- model-selection/model-recovery agreement;
- reference-limitation classification.

Engineering metrics:
- wall time;
- cold compile time;
- steady-state time;
- fits/sec and subjects/sec;
- peak RAM and VRAM;
- scaling speedup and efficiency;
- failure count.

## Floating-point and numerical policy for the paper

The compatibility target is the scientific behavior of the frozen MATLAB reference, generally in IEEE-754 double precision. The project does **not** seek arbitrary-precision results that are mathematically more accurate but behaviorally different from MATLAB.

When a runtime primitive differs materially:

1. freeze an exact MATLAB oracle case;
2. add a regression test before the repair;
3. apply the smallest evidence-backed compatibility repair;
4. rerun unchanged scientific gates;
5. retain failed historical evidence.

Never change seeds, datasets, model families, optimization settings or acceptance thresholds after seeing results to manufacture agreement.

## Main paper vs supplement vs repository

### Main paper
Include the reference version, validation design, preregistered/declared acceptance logic, aggregate parity results, recovery results, backend/GPU results, performance results and concise discussion of consequential numerical-compatibility findings.

### Supplement
Include model/workflow matrices, detailed tolerances/error distributions, matched limitation cases, extended recovery grids, environment details and selected numerical case studies such as D02/D08 if they remain scientifically informative.

### Repository/evidence artifacts
Retain full JSON outputs, intermediate probes, trial-level values, CI logs, run/job/artifact IDs, hashes, failed experiments and debugging-only diagnostics. These should not be copied wholesale into the manuscript.

## Current evidence status

- Frozen MATLAB reference: **PASS** — HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- M0–M17: historical gate evidence exists; physical H100 evidence exists for GPU milestones, subject to M18 applicability audit for final paper claims.
- Historical M18 scientific recovery experiment: **FAIL, preserved**.
- M18B protocol/integrity gate: **PASS recorded**, but not equivalent to full product/recovery closure.
- D02 model-family selection behavior: **PASS_MODEL_SELECTION_PARITY**.
- D04 uHGF→AR(1) official workflow: **PASS**.
- Latest official nine-case fit/Bayes closure: **7/9 PASS**; D02_fit and D08_fit remain blocking.
- Latest diagnostic run: `34776952053`, job `103776700085`, head `4e92ccf3e3812564c4fa93cd85c9500b6a3436e1`; artifact `10323968264`, SHA-256 `ac4d0094cfe49b5e5ee8d5c75f89311c35a2727b46ed433078412be63c3b5f9c`.
- M18 product closure: **OPEN / IN PROGRESS**.
- M19 paper dataset freeze: **OPEN / TODO**.
- M20 v1.0 candidate: **OPEN / TODO**.

## M19 paper freeze rule

M19 may be declared complete only after the required v1 evidence surface is closed and the exact paper benchmark/validation dataset is frozen. At freeze time record:

- HGFX commit/tag;
- MATLAB reference commit;
- protocol versions/hashes;
- datasets and checksums;
- environments;
- run/job/artifact IDs and artifact SHA-256 hashes;
- machine-readable aggregate result files;
- scripts that regenerate every paper table/figure.

After M19, paper tables and figures must be regenerated from frozen data rather than manually edited.

## Manuscript readiness

The manuscript may be outlined before M19, but final Results/Discussion claims must remain provisional until M19. `docs/research/PAPER_EVIDENCE_MAP.md` is the live mapping from candidate paper claims to validated repository evidence.
