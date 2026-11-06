# Benchmark Plan

Last synchronized: 2026-11-04
Status: **POST-v1 / PAPER PROTOCOL FROZEN / PERFORMANCE NOT ACTIVATED IN PROTOCOL 1**
Tracking: PV1-02 / issue #32
Paper protocol: `paper/reproducibility/PAPER_PROTOCOL.md` / `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`

## Principle

Scientific/reference equivalence is validated before performance claims are interpreted. A faster backend is not acceptable evidence if it changes validated scientific behavior.

Historical M19 is already **PASS/FROZEN** for the released v1.0.0 evidence package. It must not be reopened or reused as the name of a future paper benchmark gate. New publication experiments use the separate paper-specific protocol freeze and final paper-evidence freeze.

Paper protocol 1 freezes the primary contribution around MATLAB-toolbox reproduction, evidence accounting, recovery/identifiability, neutral pyhgf positioning, and scoped GPU applicability. It deliberately does **not** activate general speedup or multi-GPU scaling as a headline claim. A later decision to add headline performance requires a new protocol revision frozen before final benchmark execution.

The paper benchmark program distinguishes four questions:

1. Does HGFX reproduce the frozen MATLAB reference on the required scientific/workflow surface?
2. Do HGFX backends agree with the validated compatibility path?
3. How does HGFX compare with relevant contemporary tooling such as pyhgf on genuinely overlapping model/workflow surfaces?
4. If a later protocol activates performance, what performance/scaling benefit is obtained on prospectively frozen workloads?

## Reference identity

Every MATLAB-paired scientific run must record:
- MATLAB HGF Toolbox version;
- frozen HGF reference commit;
- MATLAB version;
- HGFX commit/tag;
- protocol version/hash;
- dataset/file checksums;
- model family and observation model;
- configuration/prior hashes or serialized values;
- fixed/free parameter mask;
- initial point/start/restart policy;
- seeds and, where RNG identity cannot be guaranteed, exported stochastic drivers;
- acceptance thresholds fixed before examining the result.

For v1 the compatibility oracle is HGF Toolbox 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3`, and the immutable HGFX release source is `v1.0.0` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

## Paired MATLAB/HGFX scientific comparison policy

A MATLAB/HGFX comparison is valid only when the compared runs use the same scientific workflow. Before classifying a mismatch, verify:
- same data and trial masking;
- same model family;
- same observation model;
- same parameter order/transforms;
- same priors and fixed/free semantics;
- same start point/restart selection;
- same seed or exported random driver;
- same fitting/simulation workflow.

If MATLAB itself fails or selects a different model family for the exact matched case, record that as reference evidence rather than silently forcing another HGFX workflow. `REFERENCE_LIMITATION_MATCH` is not a scientific PASS.

## pyhgf comparison policy

`pyhgf` is a distinct contemporary Python implementation with a different design center: generalized/nodalized predictive-coding networks, modular graph construction, differentiability and JAX/Rust execution. It was described by Legrand et al. in PLOS Computational Biology in 2026 (DOI `10.1371/journal.pcbi.1014340`).

Paper protocol 1 freezes the comparator identity as:

```text
pyhgf==0.3.2
pyhgf-0.3.2.tar.gz
SHA256 8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d
```

The HGFX paper must not claim to be the first or only Python/JAX HGF implementation. A fair comparison must:

- first map semantic overlap and non-overlap;
- compare only model/workflow surfaces that can be matched without changing either tool's intended semantics;
- use the same input data and precision policy for empirical comparisons where possible;
- report `NOT_DIRECTLY_COMPARABLE` rather than forcing a numerical ranking when parameterization, model semantics or fitting workflow differ materially;
- separate feature/architecture comparison from numerical comparison;
- avoid claims that HGFX is generally superior to pyhgf without direct prospectively frozen common-scope evidence.

Minimum qualitative comparison axes:
- primary design objective;
- MATLAB-toolbox behavioral compatibility target;
- HGF/gHGF model representation and extensibility;
- fitting/model-comparison workflow;
- differentiability/JAX integration;
- CPU/GPU execution;
- arbitrary network construction/generalized filtering;
- evidence/provenance strategy;
- installation/distribution and documentation.

The first candidate direct empirical surface under protocol 1 is a fixed-parameter three-level binary HGF forward trajectory / surprise calculation. It remains conditional on a committed semantic mapping that satisfies the protocol gate. If the gate fails, the correct classification is `NOT_DIRECTLY_COMPARABLE` and no numerical ranking is forced.

## Scientific metrics

Record as applicable:
- parameter/config identity;
- scalar primitive error;
- trajectory absolute/relative error;
- per-trial likelihood error;
- total likelihood error;
- perceptual/observation prior decomposition;
- objective and negative-log-joint error;
- fitted parameter distance;
- optimizer-path/termination agreement when required;
- Hessian, covariance and correlation error;
- AIC/BIC/LME agreement;
- predictions/residuals/autocorrelation;
- parameter-recovery metrics;
- model-selection/model-recovery agreement;
- classification: `PASS`, `IMPLEMENTATION_MISMATCH`, `OPTIMIZER_MISMATCH`, `MODEL_SELECTION_MISMATCH`, `REFERENCE_LIMITATION_MATCH`, `NOT_DIRECTLY_COMPARABLE`, or `INSUFFICIENT_REFERENCE_EVIDENCE`.

Do not modify thresholds, seeds, datasets, starts, model family, validation grid or optimization settings after seeing a result to obtain PASS.

## Frozen recovery / identifiability benchmark

Paper protocol 1 retains the M18C.2 analysis with:

- models: `hgf_binary`, `ehgf_binary`, `uhgf_binary`;
- observation model: `unitsq_sgm` frozen default configuration;
- trial horizons: `128`, `256`, `512`, `1024`;
- truth scales: `0.15`, `0.35` prior standard deviations;
- parameter recovery: 6 replicates per model × horizon × truth-scale stratum;
- model recovery: 3 replicates per generating-model × horizon × truth-scale stratum;
- frozen scientific thresholds inherited unchanged from M18;
- paired-integrity gate before identifiability interpretation;
- decisive preregistered interpretation based on the 256→1024 comparison.

Statistical uncertainty under the paper protocol uses Wilson 95% intervals for proportions and deterministic 10,000-resample bootstrap intervals (`seed=20260917`) for replicate-level continuous summaries and stratified model-recovery balanced accuracy. These intervals are descriptive and do not replace frozen PASS/FAIL criteria.

## Numerical-runtime diagnostics

Detailed primitive/ULP probes are engineering evidence, not default paper benchmarks. They are executed only when an unchanged scientific gate exposes a consequential mismatch.

For such cases:
1. freeze the exact failing coordinate/input;
2. export MATLAB intermediates at full IEEE precision;
3. compare HGFX at the exact same coordinate;
4. add regression evidence before a repair;
5. make the smallest compatibility repair;
6. rerun the unchanged scientific gate.

These diagnostics may become a paper/supplement case study only if they materially explain scientific reproducibility.

## Hardware/environment capture

Every new paper execution records as applicable:
- CPU model;
- RAM;
- GPU model;
- GPU count;
- VRAM;
- CUDA/runtime version;
- driver version;
- Python version;
- NumPy version;
- JAX/JAXLIB version;
- comparator package/version where applicable;
- MATLAB version where applicable;
- HGF reference commit;
- HGFX commit/tag;
- device visibility/residency evidence;
- whether the system is shared/contended.

Physical GPU evidence is required for GPU validation claims. CPU tests and mocked devices do not count as physical-GPU validation.

## Timing policy for any future activated performance protocol

Performance is not activated in paper protocol 1. If a future protocol revision activates it, separate at minimum:
- environment/setup time where relevant;
- cold compilation;
- warm/steady-state execution;
- host/device transfer;
- simulation time;
- forward/objective time;
- optimizer time;
- Hessian/statistics/postprocessing time.

Do not combine compile cost and steady-state throughput into one number without reporting both components.

## Repetitions and summary statistics for any future activated performance protocol

Use repeated runs and report:
- median;
- IQR;
- min/max where useful;
- failure count;
- workload definition;
- warmup count;
- repeat count.

For multi-GPU scaling additionally report:
- single-device baseline;
- speedup;
- scaling efficiency;
- subjects/sec and/or fits/sec;
- known contention limitations.

No workload, repeat count, timing boundary, or hardware choice may be selected after comparative timing results are inspected.

## Paper benchmark axes under protocol 1

Frozen active axes:
- MATLAB/HGFX scientific equivalence: existing v1 frozen evidence only unless a prospective paper analysis explicitly requires new paired execution;
- recovery/identifiability: models/horizons/scales/replicates frozen above;
- pyhgf: exact comparator `0.3.2`; qualitative design comparison required; direct empirical comparison conditional on the semantic gate;
- GPU: frozen historical physical-T4 applicability/correctness evidence may be reported in its original scope;
- general CPU/GPU/multi-GPU performance: **not activated**.

A future performance paper claim must use a later protocol version; exploratory historical axes cannot be silently promoted into final paper benchmark settings.

## Current performance evidence

Historical physical H100 evidence exists for M14–M17. The recorded M17 shared-system scaling snapshot is:
- 1 GPU: median `81.719055 s`, `0.783 subjects/s`, `1.566 fits/s`, speedup `1.000`, efficiency `1.000`;
- 2 GPU: median `73.838342 s`, `0.867 subjects/s`, `1.734 fits/s`, speedup `1.107`, efficiency `0.553`;
- 4 GPU: median `58.860710 s`, `1.087 subjects/s`, `2.175 fits/s`, speedup `1.388`, efficiency `0.347`.

The released v1 evidence also contains physical Tesla T4 correctness/applicability evidence. These historical results retain their original scope. Under protocol 1 they are not final paper performance benchmarks and must not be presented as general speed/scaling claims.

## Output and provenance

Machine-readable outputs go under versioned paper/benchmark evidence paths. Final paper tables and figures must be generated by scripts from machine-readable data.

Every paper-used result must be traceable to:
- HGFX SHA/tag;
- MATLAB reference SHA if paired;
- comparator name/version/package hash where applicable;
- run/job identifiers or equivalent local provenance;
- artifact ID/name;
- artifact SHA-256;
- command/protocol;
- environment record.

Prospective input datasets/shards are frozen in an immutable checksum manifest before fitting or comparison. A hash mismatch must abort the result stage rather than silently regenerate inputs after outcomes are known.

Do not manually type final numerical paper tables from memory or chat summaries.

## Paper protocol freeze

**Status: DONE.**

`paper/reproducibility/PAPER_PROTOCOL.md` is frozen as `hgfx-paper-protocol-1` with status `FROZEN_FOR_EXECUTION` before final paper-only runs. It freezes the active claim set, recovery experiment, statistical policy, pyhgf comparator identity/semantic gate, provenance requirements, and exclusions.

A necessary post-freeze deviation must preserve the original evidence and create a new protocol version before rerunning under changed settings.

## Final paper-evidence freeze

After all results intended for the submission are generated:
- archive raw outputs and hashes;
- freeze exact environment manifests and commands;
- freeze table/figure generation scripts;
- regenerate all included tables/figures from committed inputs;
- record failed/limited/not-directly-comparable cells rather than deleting them;
- create a machine-readable paper evidence manifest mapping each manuscript result to inputs and hashes;
- mark the paper evidence set `FROZEN_FOR_SUBMISSION` only after the claim audit passes.

This publication freeze is separate from historical M19 and does not alter the released v1.0.0 evidence set.

## Prospective MATLAB-vs-HGFX runtime comparison (2026-11-04)

A new **separate, not-yet-frozen and not-yet-timed** post-v1 protocol was authored at [RUNTIME_PERFORMANCE_PROTOCOL_V1.md](RUNTIME_PERFORMANCE_PROTOCOL_V1.md) (ID `hgfx-matlab-runtime-1`; PERF-01). It preregisters a matched CPU MATLAB/HGFX comparison, conditional JAX/GPU and batch benchmarks, correctness preflight, timing/uncertainty policy, and a paper-claim decision gate.

It does **not** amend historical `hgfx-paper-protocol-1`, open M19, or demonstrate an HGFX-over-MATLAB speedup. The protocol, inputs and runner must be formally frozen with hashes before final comparative runs; paper headlines additionally require a new paper protocol revision.

## PERF-01 status synchronization — 2026-11-04

The preceding protocol `hgfx-matlab-runtime-1` remains a **prospective specification**, not a passed performance gate. The distinction between **untimed scientific preflight (executed)** and **final comparative runtime measurement (NOT EXECUTED)** is essential.

- **A — PARTIAL:** verified immutable HGFX 1.0.0 and MATLAB 8.2.0/R2026a on CI; matched controlled CPU thread/affinity and real physical-GPU run environment still required.
- **B — IMPLEMENTED / REVIEW PENDING:** canonical 64-subject inputs, nine complete HGFX config/start snapshots and SHA-256 manifests committed; all 576 exact model × horizon × subject prior-objective checks completed. [Run 41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774): **448 concordant successful, 128 invalid in both**, no configuration or examined scalar discrepancy outside existing diagnostic thresholds.
- **C — OPEN / NOT FROZEN:** independent review [issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88), runtime boundary audit [PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md](PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md). The original nine-primary-cell aggregate **cannot PASS** because six standard-HGF 512/1024 tasks are scientifically ineligible. A new, explicitly separate [RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md](RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md) proposes only narrow future claims; status **REVIEW DRAFT / NO TIMING**. It neither changes nor replaces the original failed cells.
- **D — DIAGNOSTIC EVIDENCE / NOT CERTIFIED PASS:** 7 valid model × horizon complete trialwise paths and three matching invalid first-prefix events, plus one complete 128-trial full fit with matched outputs. Follow-up all-64 **full fitting** validation (128-trial, 1/16/64 original subject cohorts) is a separate ongoing non-timed experiment. No blocked status is removed before actual evidence and independent review.
- **E/F/G/H — NOT EXECUTED:** zero published or paper-use MATLAB-vs-HGFX timing, GPU acceleration, batch speedup or hardware-scaled claims.

The current original 28-case eligibility inventory is `benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json` ([workflow 41860891268](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860891268)): **16 diagnostic-concordant, review pending; 12 blocked**. This is not an independent reviewer verdict; any newly proven 64-subject fitting correspondence must be preserved in a **new evidence candidate**, not rewritten into the historical JSON.

Historical frozen M17/M18/M19 evidence and `hgfx-paper-protocol-1` remain separate, unchanged and authoritative in their original scopes.


### Follow-up correction — 64 complete fits and reference self-sensitivity

The planned all-64 full-fitting preflight **has now executed**, so any older "ongoing / untested" wording above is superseded for this exact original 128-trial cohort. MATLAB/HGFX full fitting [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006): **63/64 fitted outputs concordant**, **1/64** scientific trajectory mismatch (zero-based subject 7, `traj.mu` and `traj.muhat`). The workflow correctly failed the scientific gate; original data, parameter vectors and all outputs are archived.

Same-vector cross-replay [41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514) found complete forward/likelihood concordance in both implementations at **each original fitted vector**, while the two original fitted endpoints differ, reproducing the fitted-trajectory discrepancy. Frozen-reference-only MATLAB sensitivity probe [41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069) exactly reproduced MATLAB's baseline endpoint (zero delta) and demonstrated one `-eps` perturbation of the third free start coordinate causing a reference end-point shift `7.640946009246363e-7` outside the inherited final-parameter numerical gate. This is **reference sensitivity evidence / numerical-basin candidate**, not independent approval or a general scientific PASS. [Detailed report](PERF01D_COHORT_FIT_MISMATCH_AND_REPLAY_2026-11-04.md).

A **new derived** [28-case candidate](../../benchmarks/runtime_v1/eligibility_candidates/candidate_v2_fullfit41863441006.json), produced by [41869747776](https://github.com/ahmadkhanloo/hgfx/actions/runs/41869747776), keeps **16 review-pending / 12 blocked**, now explicitly classifying two 128-trial 16-/64-subject fitting cases as `BLOCKED_MULTISUBJECT_FIT_NUMERICAL_MISMATCH`. The earlier original candidate is unchanged. Original primary nine-case all-eligible headline remains impossible; the separate v2 scoped CPU protocol remains a DRAFT. `PERF-01C = OPEN / NOT FROZEN` and `PERF-01E–H = NOT RUN`; no MATLAB-vs-HGFX performance number has been measured.


### 2026-11-06 — six-source raw evidence reproducibility, not scientific closure

Author-side [GitHub Actions 42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894), tested at commit 1dd22bc5eef4502136e6b61a586d2129be951a8d, **SUCCESS**: 47/47 focused regressions, 11 checksum-verified original raw evidence files across six archived runs, all original diagnostics and two 28-case eligibility inventories reconstructed. The newer replay verifies exact baseline and all six reference-only MATLAB +/-eps(start) probes, independently recalculating the original M10 final-parameter threshold classification. Source and full provenance: [PERF01C_SIX_SOURCE_EVIDENCE_REPLAY_2026-11-06.md](PERF01C_SIX_SOURCE_EVIDENCE_REPLAY_2026-11-06.md).

This is an **engineering reproducibility check of already archived non-timed experiments**. It does not repair the original 63/64 fitting failure, approve the v2 CPU measurement boundaries, settle optimizer identifiability, satisfy external review [#88](https://github.com/ahmadkhanloo/hgfx/issues/88), or supply GPU/timing evidence. **PERF-01C remains OPEN / NOT FROZEN; PERF-01E-H remain NOT EXECUTED.**


### 2026-11-06 — actual public-fit optimizer trace clarifies preallocation

The previously cited 101 optimizer-history entries on both sides were **preallocated buffers** (`maxIter+1`), not 100 validated iterations or a documented convergence verdict. The new **non-timed** frozen public-fitting [subject-7 trace 42115887599](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599) found 25 finite stored trace slots in each of HGFX and MATLAB, identical starting scalar objective, first nonzero machine-level drift at record 1, and first difference beyond the **existing final-parameter** fitting tolerance (used descriptively, not as a new iteration gate) at record 14. Both fresh endpoints remained within existing final-parameter tolerance of each tool's own archived original endpoint. Verified raw archive and source-path evidence are preserved in [PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md](PERF01D_SUBJECT7_OPTIMIZER_TRACE_2026-11-06.md).

[Derived raw-evidence replay 42117014225](https://github.com/ahmadkhanloo/hgfx/actions/runs/42117014225) and `benchmarks/runtime_v1/subject7_optimizer_trace_results/derived-42115887599.json` preserve a separately derived interpretation with full raw SHA-256 provenance and 11/11 focused tests. MATLAB's exact optimizer termination reason is **not exposed** in this frozen public API; equality of trace buffer length or populated-slot count does not establish equal convergence.

The original subject-7 complete-fitting **scientific discrepancy remains 63/64**, and optimizer-path differences are an independently reviewable **numerical-path hypothesis**, not an automatically approved reference limitation. **PERF-01C OPEN / NOT FROZEN; PERF-01E–H NOT RUN.**


### 2026-11-06 — original subject-7 common-vector objective and gradient comparison

The optimizer-path forensic experiment was followed by the exact-source **untimed** [MATLAB/HGFX matched-vector objective/Ridders gradient run 42120381058](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120381058), tested at `b9e1982fb7fee931ea907f5a25d3bc7a7cbbd1e1`, **SUCCESS** with **11/11** targeted tests. Ten original saved optimizer parameter vectors—five from each archived engine trace, selected as an explicitly post-hoc diagnostic—were evaluated identically in frozen MATLAB 8.2.0 and HGFX v1.0.0. **10/10** pairs completed; maximum observed objective difference `1.4210854715202004e-14`, maximum Ridders-gradient component difference `1.6621634624236492e-11`. Zero components crossed the old fitting **final-parameter** numerical threshold, which is employed here **descriptively only**, not as a newly accepted gradient criterion. Raw artifact SHA-256 values, frozen source IDs, error handling and prior failed reporting runs are preserved in [PERF01D_SUBJECT7_GRADIENT_2026-11-06.md](PERF01D_SUBJECT7_GRADIENT_2026-11-06.md).

This reinforces a narrow candidate for accumulated optimizer trajectory/line-search/BFGS numerical sensitivity rather than a large same-vector objective/gradient mismatch at these anchors. It is **not an external reference-limitation certification** or blanket optimizer parity. Historical 63/64 fitting failure, original case denominators, and the prohibition on prospective timing remain unchanged: **PERF-01C NOT FROZEN, PERF-01E–H NOT EXECUTED.**


### 2026-11-06 — full BFGS history, curvature decisions and source-derived full steps

[Original real paired full-public fitting/BFGS diagnostic 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), **SUCCESS** at exact tested source SHA `5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d`, exported the unmodified frozen MATLAB 8.2.0/HGFX 1.0.0 subject-7 optimizer `iter.x`, `iter.val`, `iter.invH`, `iter.rst`, plus independently recomputed Ridders gradients at all 25 finite stored records; no timers, 10/10 structural tests passed. The original 64-full-fit raw results were SHA-verified before execution and their **63/64 failure preserved**.

[Immutable derived BFGS curvature/step replay 42188247052](https://github.com/ahmadkhanloo/hgfx/actions/runs/42188247052) **SUCCESS**, 18/18 tests, checked both original raw SHA-256 values and archived a separate `derived-42187240378.json`. In the **22 source-derived unambiguous BFGS decisions**, MATLAB and HGFX both applied 21 updates and skipped only record 11; no cross-language branch differences, and no mismatch between the source curvature condition and the saved T-change behavior. In **22 reconstructable nonterminal transitions**, both saved next-point records agree with a **candidate full step** (`alpha=1`) and source Armijo inequality; maximum reconstruction residual `2.6645352591003757e-15`. These are *reconstructions, not instrumented internal acceptance events*. Terminal history overwrite prevents interpreting the last two transitions.

Both BFGS matrix norms grew ~**183.57×** from record 9 to 10; the largest MATLAB/HGFX elementwise T delta was `0.00015053299961209632` at record 10. Numerical-path amplification remains a candidate, **not established causation or independently approved reference limitation**. The original scientific **63/64 full-fit mismatch**, old 28-case eligibility denominator, unchanged thresholds and non-PASS stand. **PERF-01C NOT FROZEN / PERF-01E–H NOT RUN / NO SPEEDUP CLAIM.** Complete [source-hash/science/failed-run report](PERF01D_SUBJECT7_BFGS_BRANCH_2026-11-06.md).

 
### 2026-11-06 — source-hash-verified BFGS directional difference decomposition

[New derived CI 42194769569](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194769569) **SUCCESS**, 39/39 targeted engineering tests, **NO NEW MATLAB/HGFX FITS OR TIMERS**, verifies original real BFGS [42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) and paired same-vector Ridders [42120381058](https://github.com/ahmadkhanloo/hgfx/actions/runs/42120381058) raw SHA-256 and immutable old reports; produces a NEW separately labeled derived record. Unmodified product/reference, inputs and scientific denominators. At original history record 10, raw direction delta L2 `6.569361905386501e-5` but **after original `maxStep=1` clipping** delta L2 `1.6207306067271615e-9`; BFGS spectral condition increased from ~22.2 at record 9 to ~45198 at record 10 in both implementations. At same-parameter anchor 14, the direct HGFX/MATLAB Ridders gradient-engine term was only L2 `6.299323553659936e-12` under the chosen algebraic decomposition versus larger terms involving the diverged optimization states/matrices; **NOT A UNIQUE CAUSAL EXPLANATION**.

Original strict bitwise diagnostic replay succeeded in 42188247052 but **failed across later hosts** on small float-valued `line_search_candidates` differences at [42194275053](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194275053) and [42194481974](https://github.com/ahmadkhanloo/hgfx/actions/runs/42194481974), with exact original raw SHA256 unchanged. [Issue #90](https://github.com/ahmadkhanloo/hgfx/issues/90) tracks this OPEN engineering reproducibility issue; historical failures and unchanged strict reporter preserved. Latest new algebraic report explicitly **does not assert bitwise cross-host replay**. [Full separate evidence and limitations](PERF01D_SUBJECT7_DIRECTION_DECOMPOSITION_2026-11-06.md). Original **63/64** scientific fitting non-PASS, original 28-case and nine-primary CPU eligibility, **PERF-01C NOT FROZEN**, **PERF-01E-H NOT RUN** and **no speedup** unchanged.


### 2026-11-06 — Issue #90 controlled OpenBLAS kernel isolation and original subject-7 full-fit sensitivity

[Controlled **single-host** binary64 experiment 42197971370](https://github.com/ahmadkhanloo/hgfx/actions/runs/42197971370) **SUCCESS**, 22/22 engineering tests, unchanged 48 HGFX+MATLAB original BFGS states, 48 norms plus 48 slopes, no fitting/timing. On the **same AMD EPYC runner** with NumPy 2.3.5 and OpenBLAS 0.3.30, auto and forced SkylakeX matched in 96/96 current scalar bits, with 3 norm and 13 slope values different (max 1 ULP) from the source archive. Forced Haswell reproduced **96/96 archived scalar bits**. This identifies a kernel-dispatch mechanism for the **auxiliary scalar** cross-host bitwise replay discrepancy on that runner; it is not full MATLAB/HGFX scientific equivalence. [Complete source/CPU/provenance and failed YAML initial run](PERF01D_ISSUE90_OPENBLAS_SAME_HOST_2026-11-06.md), permanent `benchmarks/runtime_v1/issue90_results/derived-same-runner-42197971370.json`.

[Bounded **real frozen HGFX full public fit** run 42199013326](https://github.com/ahmadkhanloo/hgfx/actions/runs/42199013326), **SUCCESS**, 10/10 comparator tests; same runner, original v1.0.0 release, original 128-trial subject 7/start/model/data/optimizer, two untimed runs under auto (effective SkylakeX) vs Haswell. Maximum observed differences: `iter.x` `4.4914698094089545e-7`, `iter.val` `2.6154653198773303e-7`, `iter.invH` `1.8149043592075031e-4`, final 15-vector `3.968255768427298e-8`. Thus BLAS kernel choice changes actual public optimizer path and fitted endpoint, not merely reporting. No same-host MATLAB re-fit or full `traj.mu`/`muhat` scientific comparison was executed. Original historical MATLAB final comparison **does not** improve simply by selecting Haswell; no post-hoc mode selection allowed. [Full scientifically bounded report](PERF01D_ISSUE90_FULL_FIT_DISPATCH_2026-11-06.md), `benchmarks/runtime_v1/issue90_results/derived-full-fit-42199013326.json`. Failed precursor input-manifest staging [42198798176](https://github.com/ahmadkhanloo/hgfx/actions/runs/42198798176) retained.

**Issue #90 remains OPEN** for portable diagnostic reproducibility policy; **Issue #89 remains OPEN**, original **63/64 full public fitting scientific non-PASS**, original 28-case denominator and frozen eligibility unchanged, **PERF-01C NOT FROZEN, PERF-01E–H NOT RUN, NO SPEEDUP CLAIM**.


### 2026-11-06 — exact 28-field subject-7 full public fitModel trajectory comparison for two BLAS modes

[GitHub Actions 42203036203](https://github.com/ahmadkhanloo/hgfx/actions/runs/42203036203) **SUCCESS**, exact tested SHA `c4d858bcdc090ff6590d99ca7f9c6f9609d1884a`, 19/19 focused engineering tests, unchanged original v1.0.0 HGFX public `fit_model` on original zero-based subject 7, 128 binary trials, all original starts/configs and entire historical 64-case raw SHA-256 and science summary validated first. Two fresh **untimed** full fits on the same CPU under auto=SkylakeX and forced Haswell; complete 28 fitting/trajectory fields compared against original MATLAB fit from run 41863441006 using the **exact original 28-field source comparator tolerances** (`traj rtol=3e-8,atol=3e-10`). Historical HGFX vs MATLAB and fresh auto vs historic MATLAB both fail `traj.mu` and `traj.muhat` (4 coordinate mismatches each). Fresh Haswell vs historic MATLAB fails **four fields**, `traj.epsi` (5 cells), `traj.mu` (14), `traj.muhat` (14), and `traj.psi` (40). No reference rerun on the fresh host. Haswell **worsened** cross-run diagnostic concordance and is *not* a sanctioned mode-selection strategy. Original subject-7 63/64 scientific fitting **NON-PASS** remains unchanged; original full raw archives retained.

Report [PERF01D_SUBJECT7_COMPLETE_TRAJECTORY_2026-11-06.md](PERF01D_SUBJECT7_COMPLETE_TRAJECTORY_2026-11-06.md), machine-readable `benchmarks/runtime_v1/issue90_results/derived-full-trajectories-42203036203.json` bot evidence SHA `542290f06e264925c0ce592383ff659f6a43d08d`, exact new raw checksums in report; still no timing, GPU validation, reference-limitation certification or reviewer decision. **PERF-01C OPEN/NOT FROZEN; PERF-01E–H NOT RUN; NO SPEEDUP CLAIM.**


### 2026-11-06 — crossed original-endpoint same-vector forward isolates the observed full-fit trajectory divergence

[Successful real MATLAB/HGFX forward source-locked CI **42204633161**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42204633161), tested code SHA `690d00fcb1fcb3384aa23db92fba1df963be719e`, **18/18** engineering tests, 3 predeclared original identical parameter vectors (original HGFX fitted 15-vector, original MATLAB fitted 15-vector, original frozen start), original HGF Toolbox 8.2.0 and HGFX 1.0.0, original subject 7/128 trials/data/prior model, **no fitting or timing**. Both complete unmodified HGF forward engines agree on **all 11 original trialwise fields at all 3 vectors within the original exact numerical tolerances (`rtol=3e-8`, `atol=3e-10`)**, and on full `128x3x4` inference-state arrays; `traj.mu` and `traj.muhat` show **zero failed cells at each common vector**. Each engine's direct forward at its own archived public fitted endpoint additionally reproduces **all 11 fields of its respective original public fit `fit.traj`** within the original tolerance. In contrast, historical *separately optimized* end-to-end fitting remains 63/64: subject 7 has four failing coordinates each in `traj.mu`/`traj.muhat`.

**Interpretation:** isolated source-level forward parity at these three original points supports differing fitted parameter states/optimizer path as a candidate explanation for the original trajectory mismatch; this is **not causal attribution, a general forward equivalence theorem, a full-fit scientific PASS, independent reference-limitation classification, eligibility lock or timing authorization**. Both raw SHA-256 values and all historical failed BFGS experiments preserved. Full detailed [crossed fixed-vector evidence/provenance](PERF01D_SUBJECT7_CROSSED_FORWARD_2026-11-06.md), committed separate `benchmarks/runtime_v1/issue90_results/derived-crossed-forward-42204633161.json` at bot SHA `4d97ba775194cbd71625308c8a50d19f0a6c45a6`. Original 63/64 scientific NON-PASS, original 28-case cohort and six of nine primary CPU cells ineligible, **PERF-01C NOT FROZEN / PERF-01E–H NOT RUN / NO SPEEDUP CLAIM**.


### 2026-11-06 — exact two-perceptual-omega counterfactual attributes original subject-7 trajectory differences

[REAL frozen-source MATLAB/HGFX CI **42213683575**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213683575) **SUCCESS**, exact executed diagnostic SHA **f79f16003404f8060c5cfcec9e284f90f4e8862d**, 16 new + 7 old all-64 comparator = **23/23 tests**. Original HGF binary + unitsq_sgm, **64-case full fit raw SHA256**, original v1.0.0 HGFX and HGF Toolbox 8.2.0 source SHA, subject zero-based **7**, 128 trials and both original fitted 15-vectors verified. Four **predeclared** original omega2/omega3 combination corners (MM, HM, MH, HH; perceptual coordinates zero-based **12,13**), with the original observation coordinate 14 unchanged in source endpoints; **NO fitting or timer**. At **all 4/4 corners**, all **11/11 trialwise fields** and inference states were within exactly inherited **rtol=3e-8 / atol=3e-10** across matched-parameter MATLAB/HGFX forward source implementations.

New signed counterfactual decomposition evaluated **all 11 fields** and the exact 8 original failed coordinates (4 mu, 4 one-trial-lagged muhat). At original mu trials **84,109,117,127**, the original source HGFX-MATLAB signed fitted output differences are about **−(5.62–7.84)e-10**; the parameter substitution of **omega2 (original fitted om[1], idx12)** explains **99.9995379%–99.9997989%** of each signed difference *under this two-coordinate Shapley forward decomposition*, whereas omega3 (idx13) is about **1e-15** at those failed cells; source-forward and algebraic residual recorded zero there. Same values one trial later in muhat. This is **descriptive forward input-parameter attribution**, not unique optimizer numerical cause, not a performance benchmark, no scientific acceptance.

Full exact [report](PERF01D_SUBJECT7_OMEGA_COUNTERFACTUAL_2026-11-06.md); new SHA-verified [raw and derived CI 42213683575](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213683575); separately committed machine-readable report [derived-omega-counterfactual-42213683575.json](../../benchmarks/runtime_v1/issue90_results/derived-omega-counterfactual-42213683575.json) at bot commit **c55e451b92a81a3e31925944a8be06ac0c57755a**. Failed first [CI 42213536812](https://github.com/ahmadkhanloo/hgfx/actions/runs/42213536812), which revealed a synthetic JSON-array test-fixture bug, is preserved separately; no original data/tolerance/source edits. **ORIGINAL 63/64 full fitting NON-PASS remains**, original 28 workload count and 6/9 invalid primary CPU cases unchanged, PERF-01C NOT FROZEN, PERF-01E–H NOT RUN, NO SPEEDUP.


### 2026-11-06 — original omega2 25-saved-state optimizer history (source-only; NOT new scientific gate)

[Original SHA256-verified MATLAB/HGFX BFGS history 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378) replayed using [CI **42214972548**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42214972548) **SUCCESS**, code SHA **ca50e37b26a9d4c271136acc43d76ee9cee51c3b**, **27/27** synthetic/archived-source tests. Entire original 101 allocated / **25 actually populated** optimizer history records retained. Zero-based original fitted omega2 coordinate first differs at history record **1** by **−3.552713678800501e-15**, can reach **+3.7255962581639324e-7** at record **22**, and ends at original **−1.890746936794585e-8** (HGFX minus MATLAB), identical in duplicated terminal records **23/24**. Source-derived **22** nonterminal BFGS clipped-step transitions reconstruct original recorded point deltas; transitions **22,23** excluded as terminal-overwritten and NOT inferable as actual accepted optimizer events. At record **20**, omega2 first differs beyond the existing *FINAL fitted parameter tolerance* when that tolerance is applied **descriptively to intermediate states**; this is NOT a newly approved optimizer intermediate threshold. At the original final MATLAB fitted omega2 ≈ **−8.223463945398366**, old FINAL fit bound ≈ **2.47003918361951e-7** exceeds final delta **1.890746936794585e-8**. Nevertheless the original separate **trialwise near-zero mu/muhat values still fail existing 3e-10+3e-8*abs(reference) per-element bounds** (4 each). Full [forensic report](PERF01D_SUBJECT7_OMEGA2_HISTORY_2026-11-06.md) and [immutable source-derived evidence](../../benchmarks/runtime_v1/subject7_bfgs_results/derived-omega2-history-42187240378.json) committed via bot SHA **fa525b569943e2060e0792ba01c65b3acd620369**. This is author-side source replay, **not unique optimizer root-cause proof or independent reviewer approval**.

**Original 63/64 public full fitting NON-PASS remains, 28 prospective cases unchanged (16 independent-review pending, 12 blocked), six of nine CPU primary cells ineligible, PERF-01C NOT FROZEN, PERF-01E-H NOT RUN, NO speedup.**
