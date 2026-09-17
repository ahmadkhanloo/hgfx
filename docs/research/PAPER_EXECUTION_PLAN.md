# PV1-02 Methods Paper Execution Plan

Last synchronized: 2026-09-17
Status: **IN PROGRESS — publication work activated**
Tracking: GitHub issue #32
Frozen product release: `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
Frozen MATLAB oracle: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Goal

Produce a submission-ready computational methods/software-methods paper and reproducibility package from the frozen HGFX v1.0.0 evidence base without reopening, retuning, or rewriting the historical scientific validation record.

## Publication position

The primary claim is **reference-faithful Python/JAX reproduction of the frozen MATLAB HGF Toolbox 8.2.0 scientific and workflow behavior in validated scopes, with no MATLAB runtime dependency for users**.

Secondary claims may cover JAX CPU/GPU execution, batching, multi-device infrastructure, and performance only when the corresponding paper-specific evidence is frozen and traceable. Correctness/applicability and throughput/scaling must remain separate claims.

`REFERENCE_LIMITATION_MATCH` means that HGFX reproduces a limitation observed in the frozen MATLAB oracle for the exact validated scope. It is not a scientific recovery PASS and must never be presented as one.

## Global constraints

- Do not change frozen v1 thresholds, seeds, datasets, starts, grids, model families, optimizers, or historical classifications to improve paper results.
- Preserve historical M18 recovery failures and all failed experiments.
- Use `v1.0.0` as the immutable product source unless a paper-only script/document commit is explicitly identified separately.
- Every reported numerical result must map to committed machine-readable evidence and provenance.
- Freeze every new paper-only benchmark protocol before running the final experiment.
- Generate final tables and figures from scripts; do not manually transcribe final numerical values.
- Record hardware, OS, Python, JAX/JAXLIB, driver/runtime, command, source SHA, and contention state for new performance or GPU experiments.

## File map

- `paper/manuscript.md` — evidence-backed working manuscript.
- `paper/references.bib` — bibliography for the working manuscript.
- `paper/figures/` — generated figures only.
- `paper/tables/` — generated table outputs only.
- `paper/scripts/` — scripts that regenerate figures/tables from committed evidence.
- `paper/reproducibility/` — paper-specific commands, environment manifests, benchmark protocol and artifact index.
- `docs/research/PAPER_EVIDENCE_MAP.md` — authoritative claim-to-evidence map.
- `docs/research/LEVEL2_PAPER_PLAN.md` — scientific positioning and research questions.
- `docs/research/BENCHMARK_PLAN.md` — benchmark discipline.
- `docs/validation/V1_EVIDENCE_INDEX.md` — frozen v1 release evidence authority.

## Work packages

### P0 — Synchronize publication state

**Status:** DONE in the activation commit.

Deliverables:
- mark PV1-02 active and link issue #32;
- update stale pre-M19 paper documents to the post-v1.0.0 state;
- create the working manuscript and bibliography;
- preserve v1.0.0 release history unchanged.

Acceptance:
- no paper document states that M19, M20, or v1.0.0 are still open;
- the manuscript distinguishes direct parity, scoped reference limitations, and open paper-only experiments.

### P1 — Freeze the paper-specific protocol

**Status:** OPEN / REQUIRED BEFORE NEW FINAL PAPER RUNS.

Create `paper/reproducibility/PAPER_PROTOCOL.md` and freeze:
- exact paper research questions and claims;
- datasets and checksums;
- model families and observation models;
- parameter-recovery and model-selection metrics;
- trial horizons and replicate counts for any new identifiability experiment;
- CPU/GPU/performance workload matrix;
- warm-up/compile/repeat policy;
- statistical summaries and uncertainty intervals;
- inclusion/exclusion rules;
- acceptance/interpretation rules;
- exact software and hardware fields required in provenance.

Acceptance:
- protocol is committed before final paper-only executions;
- no final paper-only result exists whose settings were chosen after inspection of its outcome.

### P2 — Generate the core equivalence tables from frozen v1 evidence

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
- `REFERENCE_LIMITATION_MATCH` rows are visually and textually distinct from PASS rows;
- historical FAIL rows remain present where scientifically relevant.

### P3 — Recovery and identifiability analysis

**Status:** OPEN / STRONGLY RECOMMENDED FOR THE STRONGER METHODS PAPER.
Tracking: PV1-01 / issue #21.

Run the frozen recovery protocol at trial horizons `128`, `256`, `512`, and `1024` for `hgf_binary`, `ehgf_binary`, and `uhgf_binary` without changing the historical M18 criterion or hiding failed configurations.

Report:
- convergence fraction;
- RMSE and standardized RMSE by parameter;
- bias;
- median parameter correlation where meaningful;
- likelihood/profile diagnostics;
- model-selection accuracy;
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
- manuscript language is updated to the observed evidence rather than the desired result.

### P4 — Paper-grade performance benchmark refresh

**Status:** OPEN / REQUIRED ONLY IF PERFORMANCE IS A HEADLINE PAPER CLAIM.

Freeze and run representative workloads across CPU, single GPU, and multi-GPU where hardware is available. Report cold compilation separately from steady-state execution.

Minimum provenance:
- CPU/GPU model and count;
- RAM/VRAM;
- OS/kernel;
- Python/JAX/JAXLIB;
- CUDA/driver where applicable;
- `CUDA_VISIBLE_DEVICES` and JAX memory settings if used;
- source SHA/tag;
- workload definition;
- warmups/repeats;
- contention/shared-host caveat.

Acceptance:
- no historical H100/T4 result is silently substituted for a new paper benchmark;
- performance claim is scoped to the tested hardware and workload;
- correctness evidence is not inferred from speed measurements.

### P5 — Figures and statistical summaries

**Status:** OPEN.

Required figure set for the stronger methods paper:
- validation overview / evidence-flow schematic;
- representative MATLAB-vs-HGFX trajectory parity plot;
- recovery/identifiability plot across trial horizons if P3 is executed;
- paired model-selection summary;
- CPU/JAX/GPU objective agreement plot;
- performance/scaling plot only if P4 is executed.

Required script behavior:
- read committed machine-readable inputs;
- emit deterministic files;
- record input hashes and source SHA;
- avoid manual data edits.

Acceptance:
- deleting generated figures and rerunning scripts reproduces them from committed inputs.

### P6 — Reproducibility package

**Status:** OPEN.

Create a paper reproduction entry point documenting:
- checkout/tag command;
- frozen MATLAB oracle acquisition/init procedure for cross-language regeneration;
- Python environment creation;
- validation commands;
- paper table/figure regeneration;
- optional GPU commands;
- expected outputs and hashes;
- which steps require MATLAB and which do not.

Acceptance:
- a competent independent reviewer can regenerate the paper outputs from repository instructions without chat history.

### P7 — Complete manuscript

**Status:** IN PROGRESS.

The working manuscript exists at `paper/manuscript.md` and currently contains evidence-backed text for the released v1 validation record. Complete it by:
- replacing editorial submission notes after P2–P6;
- integrating generated tables/figures;
- finalizing authors, affiliations, corresponding author and acknowledgments;
- selecting the target journal and converting to its template;
- completing code/data availability and conflict/funding statements;
- ensuring the abstract contains only frozen supported claims;
- ensuring Discussion explicitly covers historical recovery failures and reference limitations.

Acceptance:
- every numerical sentence passes the claim-to-evidence audit;
- no unsupported claim remains about recovery, GPU scaling, speed, or general equivalence outside validated scope.

### P8 — Independent pre-submission review

**Status:** OPEN / FINAL GATE.

Review the exact submission candidate for:
- scientific overclaiming;
- reproducibility gaps;
- evidence traceability;
- statistical/reporting errors;
- licensing/provenance;
- citation accuracy;
- consistency between abstract, results, tables, figures and supplement.

Classify findings as CRITICAL/HIGH/MEDIUM/LOW/INFO. Submission is blocked by unresolved CRITICAL/HIGH findings.

## Minimum submission package

The paper is submission-ready only when all of the following exist and are internally consistent:

- complete manuscript source;
- complete bibliography;
- frozen paper protocol;
- generated core equivalence tables;
- generated figures required by the selected claim set;
- reproducibility instructions and environment/provenance records;
- machine-readable paper evidence inputs;
- explicit mapping from each main claim to evidence;
- independent review with no unresolved blocking findings.

## Recommended claim strategy

For the current evidence base, the defensible main contribution is MATLAB-toolbox reproduction with rigorous evidence accounting and transparent reference-limit handling. Recovery/identifiability and performance should strengthen the paper only if P3/P4 are executed prospectively. They should not be allowed to delay a software-methods submission indefinitely if the target venue does not require them.
