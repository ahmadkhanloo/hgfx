# PV1-02 Methods Paper Execution Plan

Last synchronized: 2026-09-18
Status: **IN PROGRESS — P1/P2/P2A/P3/P5/P6/P6A-1/P6A-2 DONE; REPLACEMENT P7 CANDIDATE IN PREPARATION; P8 REVIEW REQUIRED BEFORE FINAL P6A FREEZE**
Tracking: GitHub issue #32
External-gap reconciliation: `PAPER_REVIEW_GAP_ASSESSMENT.md`
Frozen product release: `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
Frozen MATLAB oracle: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`
Paper protocol: `paper/reproducibility/PAPER_PROTOCOL.md` / `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`

## Goal

Produce a submission-ready computational methods/software-methods paper and reproducibility package from the frozen HGFX v1.0.0 evidence base without reopening, retuning, or rewriting the historical scientific validation record.

## Current readiness correction

The manuscript is **not absent**: `paper/manuscript.md` already contains a substantive working Abstract, methodology/validation, Results, Discussion, Limitations, Reproducibility and Conclusion. It remains **IN PROGRESS**, because final generated figures, paper-only prospective results, reproducibility bundle, declarations/journal formatting and independent review are still open. The six P2 core equivalence tables are now generated, committed and provenance-checked.

The paper-specific protocol is now frozen before final paper-only execution. It fixes the claim set, recovery/identifiability experiment, statistical summaries, `pyhgf==0.3.2` comparator identity and semantic gate, provenance requirements, and the decision not to make general performance/scaling a headline claim under protocol version 1.

Historical M19 is already **PASS/FROZEN** for v1.0.0. Publication work must not reopen M19. This plan therefore uses two separate publication gates:

- **Paper protocol freeze** — DONE as `hgfx-paper-protocol-1` before new final paper-only experiments;
- **Final paper-evidence freeze** — after all evidence selected for submission has been generated and audited.

D02/D08 are not open tasks to force into direct PASS. Their direct failures remain visible and the exact validated scopes are frozen as `REFERENCE_LIMITATION_MATCH`. The paper task is to report them accurately, not to retune them away.

## Publication position

The primary claim is **reference-faithful Python/JAX reproduction of the frozen MATLAB HGF Toolbox 8.2.0 scientific and workflow behavior in validated scopes, with no MATLAB runtime dependency for users**.

Secondary claims may cover JAX CPU/GPU execution, batching, multi-device infrastructure, and recovery/identifiability only when the corresponding paper-specific evidence is prospectively frozen and traceable. Correctness/applicability and throughput/scaling remain separate claims.

Under paper protocol 1, general speedup and multi-GPU scaling are **not** headline claims. Historical H100/T4 performance evidence remains in its original engineering scope only unless a future protocol revision prospectively activates a paper performance benchmark.

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
- `paper/tables/` — generated table outputs and the P2 table provenance manifest.
- `paper/scripts/` — scripts that regenerate figures/tables from committed evidence.
- `paper/reproducibility/PAPER_PROTOCOL.md` — frozen paper-only protocol (`hgfx-paper-protocol-1`).
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

**Status:** DONE / `FROZEN_FOR_EXECUTION`.

Frozen protocol: `paper/reproducibility/PAPER_PROTOCOL.md`  
Protocol ID: `hgfx-paper-protocol-1`

The protocol freezes:
- exact paper claim set;
- immutable historical-evidence policy;
- M18C.2 recovery/identifiability models, horizons, scales, replicates, seeds, fitting contracts and criteria;
- input-manifest/checksum policy before paired execution;
- statistical summaries and uncertainty intervals;
- `pyhgf==0.3.2` comparator identity and source-distribution hash;
- semantic gate for any direct HGFX↔pyhgf empirical comparison;
- inclusion/exclusion and outcome-classification rules;
- exact provenance fields required for every new paper result;
- table/figure generation rules;
- protocol-deviation/versioning rules;
- general performance/scaling as **not activated** under protocol version 1.

Acceptance:
- protocol is committed before final paper-only executions;
- no final paper-only result exists whose settings were chosen after inspection of its outcome;
- any later activation of headline performance requires a new frozen protocol version before execution.

### P2 — Generate core equivalence tables from frozen v1 evidence

**Status:** DONE / PASS.

Generated deterministically by `paper/scripts/generate_p2_tables.py`:
1. `paper/tables/model_workflow_coverage.md`;
2. `paper/tables/matlab_demo_parity.md`;
3. `paper/tables/fitting_statistics_classification.md`;
4. `paper/tables/recovery_model_selection.md`;
5. `paper/tables/backend_gpu_applicability.md`;
6. `paper/tables/release_reproducibility_provenance.md`.

Provenance:
- committed checksum manifest: `paper/tables/p2_tables_manifest.json`;
- required inputs include the frozen v1 evidence manifest/index, D02/D08 reference-limitation decisions, S7 paired-recovery decision and `pyproject.toml`;
- generator fails loudly when a required input is missing;
- focused CI gate: `.github/workflows/p2-paper-tables.yml`;
- validation run `35231582282` on paper commit `332d248a7ba51ae4ba5d25a387d78bfbc71855b0`: **PASS**;
- the gate regenerated the tables, verified zero diff against committed Markdown, ran the P2 acceptance tests, and regenerated/uploaded the provenance manifest.

Acceptance:
- PASS — every generated row/cell carries an evidence source;
- PASS — `REFERENCE_LIMITATION_MATCH` is textually distinct from direct PASS;
- PASS — D02/D08 direct failures remain visible and are not converted into artificial PASS;
- PASS — historical M18 scientific FAIL and S7 scientific recovery limitations remain visible;
- PASS — committed table outputs reproduce from frozen machine-readable inputs;
- PASS — input/output SHA-256 values are recorded in the committed P2 manifest.

### P2A — Fair pyhgf positioning and common-scope comparison

**Status:** DONE / PASS WITH SCOPED RESPONSE-NLL NDC.

Completion evidence:
- P2A.1–P2A.9 froze the feature/design matrix, semantic mappings, numerical policy and exact common-scope case before execution;
- P2A.10 scientific run `35268575414` executed `p2a9-binary-hgf-common-scope-001` without changing the frozen protocol;
- 11/11 mapped perceptual/inference quantities are `PASS_FOR_EXECUTED_QUANTITY`;
- participant-response NLL per-trial and total are `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` under the predeclared boundary-nonfinite policy;
- raw result was hash-verified before interpretation and preserved byte-for-byte with exact environment/workflow provenance;
- no general accuracy, performance or superiority conclusion is drawn.

Reference literature:
- Legrand et al. (2026), `pyhgf: A neural network library for predictive coding`, PLOS Computational Biology 22(6):e1014340, DOI `10.1371/journal.pcbi.1014340`.

Frozen comparator for paper protocol 1:
- package: `pyhgf==0.3.2`;
- source distribution: `pyhgf-0.3.2.tar.gz`;
- SHA-256: `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d`;
- release date: 2026-09-11.

Required work:
- produce a qualitative feature/design matrix based on primary documentation and paper sources;
- map which HGF workflows are scientifically comparable between HGFX and pyhgf;
- identify non-overlap explicitly rather than treating it as failure;
- apply the frozen semantic gate before any direct numerical comparison;
- where a common surface exists, use the same input/precision policy and the protocol-fixed scientific quantity;
- compare forward/inference outputs only after parameterization and semantics are shown to match sufficiently;
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

Acceptance result: **PASS**. The manuscript/evidence map now report the prospectively frozen scoped result, including the response-NLL NDC outcome without post-result retuning.

### P3 — Recovery and identifiability analysis

**Status:** DONE / EXECUTED / `INSUFFICIENT_REFERENCE_EVIDENCE` / `gate_pass=false`.  
Tracking: PV1-01 / issue #21.  
Protocol: `m18c2-trial-horizon-identifiability-1`.  
GitHub Actions run: `35272347167`.  
Aggregate SHA-256: `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`.  
Official result: `docs/research/P3_M18C2_RESULT.md`.

The prospectively frozen 24-shard MATLAB/HGFX matrix executed the predefined horizons `128`, `256`, `512`, and `1024` for `hgf_binary`, `ehgf_binary`, and `uhgf_binary`. Invalid/failed simulations were retained rather than dropped.

Official classification:

- overall: `INSUFFICIENT_REFERENCE_EVIDENCE`;
- per-model: `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`;
- historical M18 unchanged: true.

Interpretation boundary:

- do not promote a data-horizon explanation;
- do not promote a structural/weak-identifiability explanation;
- do not describe P3 as parameter-recovery success;
- preserve the completed inconclusive result in Results/Limitations and the reproducibility package;
- any follow-up intended to distinguish implementation from optimizer behavior requires a new prospectively frozen protocol and may not rewrite this result.

Acceptance result: **EXECUTION COMPLETE / SCIENTIFIC GATE NOT PASSED**.

### P4 — Paper-grade performance benchmark refresh

**Status:** NOT ACTIVATED IN `hgfx-paper-protocol-1` / OPTIONAL FUTURE PROTOCOL.

General speedup and multi-GPU scaling are not headline paper claims under protocol 1. Therefore no new final paper performance run should be executed merely to add a stronger-looking result.

Historical H100/T4 measurements remain available only in their original engineering scope. The frozen v1 physical Tesla T4 evidence may support GPU applicability/correctness, not a general throughput claim.

If performance is later promoted to a headline contribution, first create and freeze a new paper protocol version that specifies representative CPU, single-GPU and multi-GPU workloads and reports cold compilation separately from steady-state execution.

Minimum provenance for any future activated performance protocol:
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

Acceptance if activated in a future protocol:
- no historical H100/T4 result is silently substituted for a new paper benchmark;
- performance claim is scoped to tested hardware/workload;
- correctness evidence is not inferred from speed measurements.

### P5 — Figures and statistical summaries

**Status:** DONE / PASS FOR CURRENT CLAIM SET, INCLUDING P3 DIAGNOSTIC FIGURE.

Required figure set for the selected claim set:
- validation overview / evidence-flow schematic;
- representative MATLAB-vs-HGFX trajectory parity plot;
- recovery/identifiability plot across trial horizons if P3 is retained;
- paired model-selection summary;
- CPU/JAX/GPU objective agreement plot;
- pyhgf common-scope comparison figure/table only where direct comparison is scientifically valid.

A performance/scaling plot is not required under protocol 1 because P4 is not activated.

Required script behavior:
- read committed machine-readable inputs;
- emit deterministic files;
- record input hashes and source SHA;
- avoid manual data edits.

Acceptance:
- PASS — six canonical PNG figures are script-generated from committed evidence (`paper/scripts/generate_p5_figures.py`, `paper/figures/p5_figures_manifest.json`);
- PASS — Figure 6 (`fig_p3_horizon_diagnostics.png`) is generated directly from the hash-verified P3 aggregate, preserves incomplete HGF 512/1024 cases as gaps, and is zero-diff gated in CI;
- the figure is diagnostic-only and does not alter the official `INSUFFICIENT_REFERENCE_EVIDENCE` classification.

### P6 — Reproducibility package

**Status:** DONE FOR PROTOCOL-1 ENTRY POINT (`paper/reproducibility/README.md`).

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

**Status:** IN PROGRESS — P6A-1 DONE/PASS; P6A-2 must be refreshed for the new candidate; final freeze remains blocked on independent P8 PASS.

This is a new publication gate and is **not M19**.

P6A-1 completed in PR #61 / merge `56c64678550ef87744b27630d20bf8de0c72a5a8`:

- deterministic machine-readable draft manifest: `paper/reproducibility/p6a_paper_evidence_manifest.json`;
- status remains `DRAFT_NOT_FROZEN`;
- 51 committed evidence/source artifacts are hashed from canonical Git bytes, independent of Windows/Linux checkout line endings;
- all six canonical figures now have deterministic PNG/PDF outputs; P5 records both PNG and PDF hashes;
- raw evidence, generated tables/figures, generator scripts, protocol/reproducibility files and current manuscript/bibliography are inventoried;
- negative/inconclusive outcomes are explicit: historical M18 `FAIL_PRESERVED`, D02/D08/S7 recovery `REFERENCE_LIMITATION_MATCH`, pyhgf response NLL NDC, and P3 `INSUFFICIENT_REFERENCE_EVIDENCE`;
- freeze guard refuses `FROZEN_FOR_SUBMISSION` unless P8 records PASS for the exact candidate SHA;
- P6A read-only run `35333572515`: PASS with zero diff for regenerated P2 tables, P5 figures and P6A manifest.

P6A-2 completed in PR #63 / merge `c1bcd6a80556138ee1af6a8bf4e23d1bc616b821`:

- `paper/reproducibility/p6a_claim_audit.json` maps 45 current numerical/versioned manuscript claim lines to exact committed evidence;
- 10 explicit structural/non-claim exemptions and 20 automatic section/front-matter exemptions are recorded;
- unmapped numerical lines: 0;
- high-risk MATLAB-demo, S7, physical-GPU, pyhgf and P3 values are machine-checked against direct source artifacts;
- P6A manifest inventory expanded to 57 committed artifacts, including direct demo/GPU/final-release provenance and `paper/highlights.txt`;
- read-only P6A run `35335397062`: PASS;
- full regression run `35335397063`: PASS on Ubuntu and Windows.

Ordering now:
1. exact P7 manuscript candidate is locked;
2. independent P8 records PASS for that exact candidate with no unresolved CRITICAL/HIGH findings;
3. regenerate P6A as `FROZEN_FOR_SUBMISSION` with the same candidate SHA.

Acceptance for final P6A:
- paper results can be reconstructed without narrative notes or chat history;
- every numerical manuscript claim is evidence-mapped;
- the exact P8-approved candidate SHA is recorded;
- the v1 M19 manifest remains unchanged.

### P7 — Complete manuscript

**Status:** IN PROGRESS — P7 CONTENT/PREFLIGHT COMPLETE; REPLACEMENT CANDIDATE LOCK REQUIRED AFTER P8-HARDENING EDITS.

P7-1 completed in PR #64 / merge `6257bc5b87551baeaefd6fe345c8b9d9ffdb7d68`.

P7-1 evidence:
- P7 JNM preflight run `35337207046`: PASS;
- abstract: 237 words;
- keywords: 6;
- highlights: 5, each <=85 characters and without acronym/jargon violations under the automated check;
- bibliography: zero unresolved citation keys;
- stale Technology-and-Code wording removed;
- neuroscience-method research component made explicit;
- Elsevier-style competing-interest, CRediT, funding and generative-AI disclosures added;
- P6A read-only run `35337207243`: PASS / zero diff;
- regression run `35337207135`: PASS on Ubuntu and Windows, 214 passed / 4 skipped on each platform.

P7-2 completed after the author supplied and approved the institutional email `m.ahmadkhanloo@ipm.ir`.

Prior candidate `82bbb0c30893651f8ccb15ba27195c3d58bae521` is superseded for submission because its tree still contained stale pre-restoration P6A/P8 gate metadata. A replacement candidate is being prepared from current `main` with the same frozen scientific evidence plus narrower abstract wording and synchronized publication-gate documents. The replacement SHA is locked only after strict P7/P6A/P2/P5/regression checks pass.

The working manuscript already contains evidence-backed sections for the released v1 validation record. Complete it by:
- integrating the pyhgf related-work/positioning section and final comparison evidence;
- integrating generated P2/P5 tables and figures;
- keep the completed P3 `INSUFFICIENT_REFERENCE_EVIDENCE` result and its diagnostic Figure 6 explicit in Results/Limitations without upgrading the scientific conclusion;
- strengthening Methods with exact reproducibility/protocol details rather than repository shorthand;
- keeping D02/D08 and historical recovery limitations explicit in Results and Discussion;
- finalizing the corresponding-author institutional email; author/affiliation/declarations/acknowledgments are otherwise preflighted;
- selected target: *Journal of Neuroscience Methods* (Elsevier hybrid, subscription track / no APC);
- not JCR Q1 (Neurosciences Q3; Biochemical Research Methods Q2);
- converting to the JNM Research Article format (Highlights, Materials and methods, abstract ≤250 words);
- funding recorded as none; remaining conflict/author metadata left for the authors;
- ensuring the abstract contains only frozen supported claims.

Paper-grade performance Results are not required under protocol 1 because general performance/scaling is not a headline claim.

Acceptance:
- Methods, Results and Discussion are complete as standalone scientific sections rather than repository summaries;
- every numerical sentence passes the claim-to-evidence audit;
- no unsupported claim remains about recovery, GPU scaling, speed, comparison with pyhgf, or equivalence outside validated scope.

### P8 — Independent pre-submission review

**Status:** REQUIRED / OPEN — independent paper-delta review must PASS before final P6A freeze.

Checklist: `docs/research/PAPER_P8_REVIEW_CHECKLIST.md`. Review packet: `docs/research/P8_REVIEW_PACKET.md`. Replacement candidate SHA: `PENDING_LOCK`. The checklist is not a completed review.
 Deterministic delta manifest: `docs/research/P8_DELTA_MANIFEST.json`; PR #66 / run `35344626071` PASS.

The v1 implementation/release baseline was already independently reviewed in `docs/validation/INDEPENDENT_REVIEW_REPORT.md`; H1/H2 were remediated and closed in `docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md`. Do not repeat that unchanged baseline.

Review the exact submission candidate only for the paper/post-review delta:
- scientific overclaiming;
- reproducibility gaps;
- evidence traceability;
- fairness/accuracy of pyhgf comparison;
- statistical/reporting errors;
- licensing/provenance;
- citation accuracy;
- consistency between abstract, results, tables, figures and supplement.

Classify findings as CRITICAL/HIGH/MEDIUM/LOW/INFO. Any CRITICAL/HIGH finding must be resolved before submission. P8 is a repository publication gate and final P6A freeze is forbidden until an independent PASS is recorded for the exact replacement candidate.

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
- independent P8 review is required and no unresolved CRITICAL/HIGH finding may be ignored.

## Recommended claim strategy

For the current evidence base, the defensible main contribution is **MATLAB-toolbox reproduction with rigorous evidence accounting and transparent reference-limit handling**, positioned explicitly alongside pyhgf rather than as a replacement for all modern Python HGF tooling.

PV1-01 recovery/identifiability remains the prospective analysis most likely to strengthen the scientific contribution under protocol 1. General performance/scaling is intentionally excluded from the headline claim set unless prospectively activated by a later protocol revision.

PyPI publication is complete and can be cited as a reviewer-usability/distribution fact, but it is not a substitute for scientific validation or reproducibility.
