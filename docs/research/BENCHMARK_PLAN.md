# Benchmark Plan

Last synchronized: 2026-09-17
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
