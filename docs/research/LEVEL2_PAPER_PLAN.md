# Methods-Level Paper Plan

Last synchronized: 2026-09-17
Status: **ACTIVE / POST-v1.0.0 — manuscript drafting and paper evidence production in progress**
Tracking: PV1-02 / GitHub issue #32
Execution plan: `PAPER_EXECUTION_PLAN.md`

## Working title

**HGFX: A Python/JAX Reproduction of the Hierarchical Gaussian Filter Toolbox with Validated MATLAB Equivalence and Accelerator-Compatible Execution**

The primary contribution is MATLAB-reference reproduction. GPU/scaling must not outrank equivalence unless a prospectively frozen paper benchmark supports the stronger claim.

## Frozen anchors

- HGFX release: `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- MATLAB oracle: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- M19: **DONE / PASS — evidence manifest frozen**.
- M20: **PASS_M20_CANDIDATE** before final 1.0.0 promotion.
- Independent review H1/H2: **RESOLVED** without changing frozen scientific criteria.
- v1.0.0 release gate: closed.

## Current paper objective

Establish that HGFX reproduces the frozen MATLAB toolbox's required model/configuration semantics, trajectories, observation/objective calculations, fitting/statistical surfaces, simulation and official demo workflows, and paired model-selection behavior without requiring MATLAB at user runtime.

The manuscript must preserve the distinction between:

1. direct numerical/workflow parity;
2. exact-scope `REFERENCE_LIMITATION_MATCH` behavior;
3. historical scientific FAIL evidence;
4. CPU/JAX/GPU correctness/applicability;
5. performance/scaling.

A matched MATLAB limitation is compatible with the product-equivalence objective but is not a scientific recovery PASS.

## Publication position

Primary target: computational methods/software-methods paper with two linked contributions:

1. **Reference-faithful Python reproduction** of the HGF Toolbox with explicit evidence accounting and transparent treatment of reference limitations.
2. **Modern accelerator-compatible execution** in Python/JAX, with backend/GPU correctness demonstrated separately from throughput claims.

A stronger methods framing may add prospective identifiability and performance experiments. A software-methods submission remains scientifically defensible without making recovery/scaling headline claims.

## Core research questions

### RQ1 — Functional and numerical equivalence
Can HGFX reproduce required configurations, transforms, trajectories, observation likelihoods, objectives, fitting outputs, Hessian/covariance/statistics, and simulation workflows within frozen tolerances?

### RQ2 — Workflow equivalence
Can official MATLAB demo behavior be reproduced in Python using the same model family, data, priors, fixed/free parameters, starts, and workflow semantics?

### RQ3 — Recovery and model-selection behavior
Under matched protocols, which recovery/model-selection conclusions agree, and which failures reflect reference limitations or identifiability rather than implementation mismatch?

### RQ4 — Numerical reproducibility
Which binary64/runtime differences are scientifically negligible, and which are amplified by finite differences or optimization enough to require compatibility handling?

### RQ5 — Backend equivalence
Do compatibility CPU, JAX CPU, and physical-GPU paths preserve the required scientific outputs on validated workloads?

### RQ6 — Performance and scaling
If retained as a paper claim, how do compile time, steady-state runtime, throughput, memory, and device scaling behave under a prospectively frozen benchmark matrix?

## Evidence hierarchy

Paper claims must be sourced in this order:

1. frozen reference identity and v1 manifests;
2. milestone/gate documents and machine-readable validation artifacts;
3. paired MATLAB/HGFX raw outputs;
4. CI run/job/artifact provenance;
5. generated paper tables/figures.

No engineering observation becomes a paper result without a stable protocol, provenance, and explicit interpretation.

## Current evidence status

- Frozen MATLAB reference: **PASS**.
- HGFX v1.0.0 release: **RELEASED / VERIFIED**.
- M0–M17: complete in documented scopes.
- Historical M18 scientific recovery experiment: **FAIL_PRESERVED**.
- D02 exact official scope: **REFERENCE_LIMITATION_MATCH**.
- D08 exact failed seed: **REFERENCE_LIMITATION_MATCH**.
- Official eHGF model-selection demo: **PASS_MODEL_SELECTION_PARITY**.
- Official uHGF→AR(1) workflow: **PASS_UHGF_AR1_WORKFLOW_PARITY**.
- S7 paired parameter recovery: scoped **REFERENCE_LIMITATION_MATCH** where MATLAB also fails.
- S7 paired model selection: **PASS_PAIRED_MODEL_SELECTION**, 36/36 BIC winners match.
- S9 CPU/backend: **PASS_CPU_BACKEND_EQUIVALENCE**.
- S9 physical GPU: **PASS_PHYSICAL_GPU_APPLICABILITY** on 2x Tesla T4, maximum final-objective gap `1.4210854715202004e-14` vs frozen `1e-7`.
- S10 release readiness: **PASS**.
- M19 evidence freeze: **PASS_FROZEN**.
- Independent release review: completed; H1/H2 resolved; post-review Ubuntu/Windows regression passed.

## Experimental program for the paper

### E1 — Frozen v1 equivalence synthesis

Generate manuscript tables from the frozen v1 evidence for configuration/model coverage, forward/observation/objective parity, fitting/statistics, simulation/workflows, recovery/model selection, backend agreement, and release provenance.

Status: **required / open for paper generation**. The underlying v1 evidence is frozen; the paper synthesis scripts are not yet complete.

### E2 — Official workflow figures

Generate representative MATLAB-vs-HGFX trajectory/inference plots from committed paired evidence for the official demo workflows.

Status: **open**.

### E3 — Trial-horizon / identifiability study

Run the prospectively defined 128/256/512/1024-trial recovery analysis across `hgf_binary`, `ehgf_binary`, and `uhgf_binary` if the stronger recovery/identifiability contribution is desired. This is PV1-01 / issue #21.

Status: **open / recommended for stronger methods paper**.

### E4 — Paper-grade backend/performance benchmark

Freeze a new workload matrix before execution. Separate cold compilation from steady-state execution and record complete hardware/runtime provenance.

Status: **open / required only for headline performance claims**.

Historical H100/T4 measurements remain historical evidence and must not be silently repurposed as the final paper benchmark.

### E5 — Reproducibility package and independent manuscript review

Package exact commands, environments, hashes, and regeneration scripts, then review the exact submission candidate for claim/evidence consistency.

Status: **open / required**.

## Floating-point and numerical policy

The compatibility target is the scientific behavior of the frozen MATLAB reference, generally in IEEE-754 binary64. The project does not prefer mathematically higher precision when that would change the frozen reference behavior.

For consequential runtime differences:

1. freeze an exact MATLAB oracle case;
2. preserve/add a regression;
3. apply the smallest evidence-backed compatibility repair;
4. rerun unchanged scientific gates;
5. retain historical failed evidence.

Never change seeds, datasets, model families, optimization settings, or thresholds after seeing outcomes to manufacture agreement.

## Main paper vs supplement vs repository

### Main paper
Reference identity, validation design, aggregate parity/workflow results, paired model-selection/recovery interpretation, backend/GPU applicability, selected numerical compatibility findings, and prospective performance/recovery results only if their paper protocols are frozen before execution.

### Supplement
Full model/workflow matrices, tolerance/error distributions, exact reference-limitation cases, extended recovery grids, environments, and numerical case studies.

### Repository
Raw JSON, trial-level values, intermediate probes, CI logs, run/job/artifact IDs, hashes, failed experiments, debugging diagnostics, and figure/table source data.

## Manuscript readiness

`paper/manuscript.md` now exists as the working manuscript and is synchronized to the released v1 evidence. It is **not submission-ready** until the PV1-02 submission gate in `PAPER_EXECUTION_PLAN.md` is satisfied.
