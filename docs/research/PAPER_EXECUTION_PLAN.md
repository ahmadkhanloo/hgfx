# PV1-02 Methods Paper Execution Plan

Last synchronized: 2026-09-17
Status: **IN PROGRESS — external paper-readiness critique incorporated**
Tracking: GitHub issue #32
External-gap reconciliation: `PAPER_REVIEW_GAP_ASSESSMENT.md`
Frozen product release: `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
Frozen MATLAB oracle: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Goal

Produce a submission-ready computational methods/software-methods paper and reproducibility package from the frozen HGFX v1.0.0 evidence base without reopening, retuning, or rewriting the historical scientific validation record.

## Current readiness correction

The manuscript is **not absent**: `paper/manuscript.md` already contains a substantive working Abstract, methodology/validation, Results, Discussion, Limitations, Reproducibility and Conclusion. It remains **IN PROGRESS**, because final generated tables/figures, paper-only prospective results, reproducibility bundle, declarations/journal formatting and independent review are still open.

Historical M19 is already **PASS/FROZEN** for v1.0.0. Publication work must not reopen M19. This plan therefore uses two separate publication gates:

- **Paper protocol freeze** — before new final paper-only experiments;
- **Final paper-evidence freeze** — after all evidence selected for submission has been generated and audited.

D02/D08 are not open tasks to force into direct PASS. Their direct failures remain visible and the exact validated scopes are frozen as `REFERENCE_LIMITATION_MATCH`. The paper task is to report them accurately, not to retune them away.

## Publication position

The primary claim is **reference-faithful Python/JAX reproduction of the frozen MATLAB HGF Toolbox 8.2.0 scientific and workflow behavior in validated scopes, with no MATLAB runtime dependency for users**.

Secondary claims may cover JAX CPU/GPU execution, batching, multi-device infrastructure, recovery/identifiability and performance only when the corresponding paper-specific evidence is prospectively frozen and traceable. Correctness/applicability and throughput/scaling remain separate claims.

`REFERENCE_LIMITATION_MATCH` means that HGFX reproduces a limitation observed in the frozen MATLAB oracle for the exact validated scope. It is not a scientific recovery PASS and must never be presented as one.

`pyhgf` is already an established modern Python/JAX HGF-related package and was published in PLOS Computational Biology in 2026. HGFX must therefore not be positioned as the first/only Python/JAX HGF. The defensible differentiator is the frozen MATLAB 8.2.0 behavioral-compatibility target, cross-language evidence/provenance, and explicit reference-limitation accounting.

HGFX `1.0.0` is now publicly installable from PyPI. This improves reviewer usability but does not change or strengthen any scientific validation claim.

## Global constraints

- Do not change frozen v1 thresholds, seeds, datasets, starts, grids, model families, optimizers, or historical classifications to improve paper results.
- Preserve historical M18 recovery failures and all failed experiments.
- Use `v1.0.0` as the immutable product source unless a paper-only script/document commit is explicitly identified separately.
- Every reported numerical result must map to committed machine-readable evidence and provenance.
- Freeze every new paper-only benchmark protocol before running the final experiment.
- Generate final tables and figures from scripts; do not manually transcribe final numerical values.
- Record hardware, OS, Python, NumPy, JAX/JAXLIB, driver/runtime, command, source SHA and contention state for new performance or GPU experiments.
- For external comparator experiments, pin the exact package version/commit and compare only semantically overlapping workflows.
- Preserve `NOT_DIRECTLY_COMPARABLE` as a valid outcome when tool semantics differ materially.

## File map

- `paper/manuscript.md` — evidence-backed working manuscript.
- `paper/references.bib` — bibliography for the working manuscript.
- `paper/figures/` — generated figures only.
- `paper/tables/` — generated table outputs only.
- `paper/scripts/` — scripts that regenerate figures/tables from committed evidence.
- `paper/reproducibility/PAPER_PROTOCOL.md` — paper-only protocol; must be frozen before final new runs.
- `paper/reproducibility/` — commands, environment manifests, hashes and final paper evidence manifest.
- `docs/research/PAPER_EVIDENCE_MAP.md` — authoritative claim-to-evidence map.
- `docs/research/PAPER_REVIEW_GAP_ASSESSMENT.md` — critique reconciliation and publication-gap inventory.
- `docs/research/BENCHMARK_PLAN.md` — benchmark/comparator discipline.
- `docs/research/LEVEL2_PAPER_PLAN.md` — scientific positioning and research questions.
- `docs/validation/V1_EVIDENCE_INDEX.md` — frozen v1 release evidence authority.
- `docs/planning/PYPI_PUBLISHING.md` — public distribution provenance and independent PyPI verification.

## Work packages

### P0 — Synchronize publication state

**Status:** DONE.

Deliverables:
- mark PV1-02 active and link issue #32;
- update stale pre-M19 paper documents to the post-v1.0.0 state;
- create the working manuscript and bibliography;
- preserve v1.0.0 release history unchanged;
- reconcile external paper-readiness criticism with current repository state.

Acceptance:
- no paper document states that M19, M20, or v1.0.0 are still open;
- the manuscript distinguishes direct parity, scoped reference limitations, and open paper-only experiments;
- valid external review gaps are tracked without reopening frozen v1 gates.

### P1 — Freeze the paper-specific protocol

**Status:** OPEN / REQUIRED BEFORE NEW FINAL PAPER RUNS.

Create and finalize `paper/reproducibility/PAPER_PROTOCOL.md` with status `FROZEN_FOR_EXECUTION` before final new experiments. Freeze:
- exact paper research questions and claim set;
- datasets and checksums;
- model families and observation models;
- parameter-recovery and model-selection metrics;
- trial horizons and replicate counts for identifiability experiments;
- pyhgf comparator version and semantic mapping;
- CPU/GPU/performance workload matrix;
- warm-up/compile/repeat policy;
- statistical summaries and uncertainty intervals;
- inclusion/exclusion rules;
- acceptance/interpretation rules;
- exact software and hardware fields required in provenance.

Acceptance:
- protocol is committed before final paper-only executions;
- no final paper-only result exists whose settings were chosen after inspection of its outcome.

### P2 — Generate core equivalence tables from frozen v1 evidence

**Status:** OPEN / HIGH PRIORITY.

Generate, by script:
1. model/workflow coverage table;
2. official MATLAB demo parity table;
3. fitting/statistics classification table;
4. recovery/model-selection table;
5. backend/GPU applicability table;
6. release/reproducibility provenance table.

Use the frozen evidence index and machine-readable artifacts as inputs. The script must fail if a required input is absent rather than silently dropping a row.

Acceptance:
- every cell has an evidence source;
- `REFERENCE_LIMITATION_MATCH` rows are visually/textually distinct from PASS rows;
- D02/D08 direct failures remain visible rather than being presented as unresolved bugs or artificial PASS;
- historical FAIL rows remain present where scientifically relevant.

### P2A — Fair pyhgf positioning and common-scope comparison

**Status:** OPEN / HIGH PRIORITY FOR SUBMISSION POSITIONING.

Reference literature:
- Legrand et al. (2026), `pyhgf: A neural network library for predictive coding`, PLOS Computational Biology 22(6):e1014340, DOI `10.1371/journal.pcbi.1014340`.

Required work:
- pin the exact pyhgf release/commit used in the paper;
- produce a qualitative feature/design matrix based on primary documentation and paper sources;
- map which HGF workflows are scientifically comparable between HGFX and pyhgf;
- identify non-overlap explicitly rather than treating it as failure;
- where a common surface exists, define a prospective empirical comparison under the same input/hardware/precision/timing policy;
- compare forward/inference outputs only after parameterization and semantics are shown to match sufficiently;
- compare fitting/performance only when workflows are genuinely equivalent;
- report `NOT_DIRECTLY_COMPARABLE` where they are not.

Required comparison dimensions:
- primary design goal;
- relation to MATLAB HGF Toolbox;
- fixed toolbox compatibility vs generalized/nodalized network construction;
- model coverage/extensibility;
- fitting/model-comparison workflows;
- differentiability/JAX integration;
- CPU/GPU execution;
- recovery examples/evidence;
- reproducibility/provenance strategy;
- packaging/PyPI/documentation.

Acceptance:
- manuscript contains a neutral related-work section;
- no first/only-Python-HGF claim remains;
- no superiority claim appears without direct prospective evidence;
- empirical comparison, if executed, follows the frozen paper protocol.

### P3 — Recovery and identifiability analysis

**Status:** IN PROGRESS / STRONGLY RECOMMENDED FOR THE STRONGER METHODS PAPER.**
Tracking: PV1-01 / issue #21.

The protocol is already frozen in `docs/validation/M18C2_TRIAL_HORIZON_PROTOCOL.md`. Run the predefined trial horizons `128`, `256`, `512`, and `1024` for `hgf_binary`, `ehgf_binary`, and `uhgf_binary` without changing the historical M18 criterion or hiding failed configurations.

Report:
- convergence fraction;
- RMSE and standardized RMSE by parameter;
- bias;
- median parameter correlation where meaningful;
- likelihood/profile diagnostics;
- model-selection/model-recovery accuracy;
- uncertainty across replicates.

Interpretation must separate:
- data-horizon limitation;
- weak/structural identifiability;
- optimizer/numerical mismatch;
- model-selection mismatch;
- matched MATLAB reference limitation.

Acceptance:
- machine-readable results and exact commands committed;
- conclusion does not retroactively convert historical M18 FAIL into PASS;
- manuscript language follows the observed evidence rather than the desired result.

### P4 — Paper-grade performance benchmark refresh

**Status:** OPEN / REQUIRED ONLY IF PERFORMANCE IS A HEADLINE PAPER CLAIM.

Freeze and run representative workloads across CPU, single GPU and multi-GPU where suitable hardware is available. Report cold compilation separately from steady-state execution.

Minimum provenance:
- CPU/GPU model and count;
- RAM/VRAM;
- OS/kernel;
- Python/NumPy/JAX/JAXLIB;
- CUDA/driver where applicable;
- `CUDA_VISIBLE_DEVICES` and JAX memory settings if used;
- source SHA/tag;
- comparator version if applicable;
- workload definition;
- warmups/repeats;
- contention/shared-host caveat.

Acceptance:
- no historical H100/T4 result is silently substituted for a new paper benchmark;
- performance claim is scoped to tested hardware/workload;
- correctness evidence is not inferred from speed measurements.

### P5 — Figures and statistical summaries

**Status:** OPEN / REQUIRED.

Required figure set for the selected claim set:
- validation overview / evidence-flow schematic;
- representative MATLAB-vs-HGFX trajectory parity plot;
- recovery/identifiability plot across trial horizons if P3 is retained;
- paired model-selection summary;
- CPU/JAX/GPU objective agreement plot;
- pyhgf common-scope comparison figure/table only where direct comparison is scientifically valid;
- performance/scaling plot only if P4 is retained.

Required script behavior:
- read committed machine-readable inputs;
- emit deterministic files;
- record input hashes and source SHA;
- avoid manual data edits.

Acceptance:
- deleting generated figures/tables and rerunning scripts reproduces them from committed inputs.

### P6 — Reproducibility package

**Status:** OPEN / REQUIRED.

Create a paper reproduction entry point documenting:
- checkout/tag command;
- frozen MATLAB oracle acquisition/init procedure for cross-language regeneration;
- Python environment creation;
- exact dependency versions;
- validation commands;
- seeds/configs/stochastic drivers;
- dataset checksums;
- paper table/figure regeneration;
- optional GPU commands;
- comparator install/version commands where relevant;
- expected outputs and hashes;
- which steps require MATLAB and which do not.

Acceptance:
- a competent independent reviewer can regenerate paper outputs from repository instructions without chat history;
- exact HGFX commit/tag and reference SHA are recorded;
- software environment and hardware provenance are complete for every new benchmark used in the manuscript.

### P6A — Final paper-evidence freeze

**Status:** OPEN / REQUIRED BEFORE FINAL MANUSCRIPT LOCK.

This is a new publication gate and is **not M19**.

After P2–P6 results intended for submission are complete:
- create a machine-readable paper evidence manifest;
- record hashes of all paper-used raw inputs, generated tables/figures and scripts;
- record exact environments/commands/source SHAs;
- regenerate all included tables/figures from committed inputs;
- record all FAIL, `REFERENCE_LIMITATION_MATCH`, and `NOT_DIRECTLY_COMPARABLE` outcomes;
- map every numerical manuscript claim to an evidence item;
- set the manifest to `FROZEN_FOR_SUBMISSION` only after the claim audit succeeds.

Acceptance:
- paper results can be reconstructed without relying on narrative notes or chat history;
- the v1 M19 manifest remains unchanged.

### P7 — Complete manuscript

**Status:** IN PROGRESS / SUBSTANTIVE DRAFT EXISTS.

The working manuscript already contains evidence-backed sections for the released v1 validation record. Complete it by:
- integrating the pyhgf related-work/positioning section and final comparison evidence;
- integrating generated P2/P5 tables and figures;
- updating recovery Results/Discussion after P3 if retained;
- adding paper-grade performance Results only if P4 is retained;
- strengthening Methods with exact reproducibility/protocol details rather than repository shorthand;
- keeping D02/D08 and historical recovery limitations explicit in Results and Discussion;
- finalizing authors, affiliations, corresponding author and acknowledgments;
- selecting target journal and converting to its template;
- completing code/data availability, funding and conflict statements;
- ensuring the abstract contains only frozen supported claims.

Acceptance:
- Methods, Results and Discussion are complete as standalone scientific sections rather than repository summaries;
- every numerical sentence passes the claim-to-evidence audit;
- no unsupported claim remains about recovery, GPU scaling, speed, comparison with pyhgf, or equivalence outside validated scope.

### P8 — Independent pre-submission review

**Status:** OPEN / FINAL SCIENTIFIC GATE.

Review the exact submission candidate for:
- scientific overclaiming;
- reproducibility gaps;
- evidence traceability;
- fairness/accuracy of pyhgf comparison;
- statistical/reporting errors;
- licensing/provenance;
- citation accuracy;
- consistency between abstract, results, tables, figures and supplement.

Classify findings as CRITICAL/HIGH/MEDIUM/LOW/INFO. Submission is blocked by unresolved CRITICAL/HIGH findings.

### P9 — Distribution / PyPI

**Status:** DONE / PASS / NON-BLOCKING FOR SCIENCE.
Tracking: PV1-03 / issue #34.

HGFX `1.0.0` is publicly distributed through PyPI:

```text
https://pypi.org/project/hgfx/1.0.0/
```

Evidence:
- exact source: `v1.0.0` -> `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`;
- Trusted Publishing / GitHub OIDC publication run `35207257208`: PASS;
- build, metadata validation, archive audit and pre-upload clean-install smoke: PASS;
- independent install from `https://pypi.org/simple` in run `35207903084`: PASS;
- public API import and minimal fitting smoke from the installed PyPI artifact: PASS;
- provenance: `docs/planning/PYPI_PUBLISHING.md`.

This remains distribution evidence only; it does not substitute for scientific validation or paper reproducibility evidence.

## Minimum submission package

The paper is submission-ready only when all applicable items below are internally consistent:

- complete manuscript source with standalone Methods, Results and Discussion;
- complete bibliography including pyhgf and relevant HGF/toolbox literature;
- frozen paper protocol;
- generated core equivalence tables;
- fair pyhgf positioning/comparison;
- generated figures required by the selected claim set;
- reproducibility instructions and environment/provenance records;
- machine-readable paper evidence inputs;
- final paper evidence manifest marked `FROZEN_FOR_SUBMISSION`;
- explicit mapping from every main numerical claim to evidence;
- historical failures/reference limitations clearly disclosed;
- independent review with no unresolved CRITICAL/HIGH findings.

## Recommended claim strategy

For the current evidence base, the defensible main contribution is **MATLAB-toolbox reproduction with rigorous evidence accounting and transparent reference-limit handling**, positioned explicitly alongside pyhgf rather than as a replacement for all modern Python HGF tooling.

PV1-01 recovery/identifiability can materially strengthen the scientific analysis. Paper-grade performance can strengthen the engineering contribution if executed prospectively. Neither should be allowed to manufacture a stronger conclusion than the evidence supports.

PyPI publication is now complete and can be cited as a reviewer-usability/distribution fact, but it is not a substitute for scientific validation or reproducibility.
