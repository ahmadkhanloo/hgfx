# Benchmark Plan

Last synchronized: 2026-09-17
Status: **POST-v1 / PAPER BENCHMARK PROTOCOL NOT YET FROZEN**
Tracking: PV1-02 / issue #32

## Principle

Scientific/reference equivalence is validated before performance claims are interpreted. A faster backend is not acceptable evidence if it changes validated scientific behavior.

Historical M19 is already **PASS/FROZEN** for the released v1.0.0 evidence package. It must not be reopened or reused as the name of a future paper benchmark gate. New publication experiments use a separate paper-specific protocol freeze and final paper-evidence freeze.

The paper benchmark program distinguishes four questions:

1. Does HGFX reproduce the frozen MATLAB reference on the required scientific/workflow surface?
2. Do HGFX backends agree with the validated compatibility path?
3. How does HGFX compare with relevant contemporary tooling such as pyhgf on genuinely overlapping model/workflow surfaces?
4. After 1–3 are scoped correctly, what performance/scaling benefit is obtained on prospectively frozen workloads?

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

The HGFX paper must not claim to be the first or only Python/JAX HGF implementation. A fair comparison must:

- pin an exact pyhgf release/version before execution;
- first map semantic overlap and non-overlap;
- compare only model/workflow surfaces that can be matched without changing either tool's intended semantics;
- use the same input data, precision, hardware and timing policy for empirical comparisons where possible;
- report `NOT_DIRECTLY_COMPARABLE` rather than forcing a numerical ranking when parameterization, model semantics or fitting workflow differ materially;
- separate feature/architecture comparison from numerical/performance comparison;
- avoid claims that HGFX is generally superior to pyhgf unless a prospectively frozen benchmark directly supports that statement.

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

Any common-scope empirical benchmark is part of the paper-specific protocol and must be frozen before final execution.

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

Every performance/backend run records:
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

## Timing policy

Separate at minimum:
- environment/setup time where relevant;
- cold compilation;
- warm/steady-state execution;
- host/device transfer;
- simulation time;
- forward/objective time;
- optimizer time;
- Hessian/statistics/postprocessing time.

Do not combine compile cost and steady-state throughput into one number without reporting both components.

## Repetitions and summary statistics

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

## Paper benchmark axes

The paper-specific protocol, not M19, must select and freeze scientifically justified values across:
- trials;
- subjects;
- model candidates;
- restarts;
- HGF levels/model families;
- CPU/JAX CPU/GPU backend;
- GPU count where applicable;
- comparator version/workflow where pyhgf is included.

Earlier exploratory axes remain planning candidates until they are committed in `paper/reproducibility/PAPER_PROTOCOL.md` before final execution.

## Current performance evidence

Historical physical H100 evidence exists for M14–M17. The recorded M17 shared-system scaling snapshot is:
- 1 GPU: median `81.719055 s`, `0.783 subjects/s`, `1.566 fits/s`, speedup `1.000`, efficiency `1.000`;
- 2 GPU: median `73.838342 s`, `0.867 subjects/s`, `1.734 fits/s`, speedup `1.107`, efficiency `0.553`;
- 4 GPU: median `58.860710 s`, `1.087 subjects/s`, `2.175 fits/s`, speedup `1.388`, efficiency `0.347`.

The released v1 evidence also contains physical Tesla T4 correctness/applicability evidence. These historical results retain their original scope. They are not automatically the final paper performance benchmark and must not be presented as general speed/scaling claims without the paper protocol.

## Output and provenance

Machine-readable outputs go under versioned paper/benchmark evidence paths. Final paper tables and figures must be generated by scripts from machine-readable data.

Every paper-used result must be traceable to:
- HGFX SHA/tag;
- MATLAB reference SHA if paired;
- comparator name/version/commit where applicable;
- run/job identifiers or equivalent local provenance;
- artifact ID/name;
- artifact SHA-256;
- command/protocol;
- environment record.

Do not manually type final numerical paper tables from memory or chat summaries.

## Paper protocol freeze

Before any new final paper-only experiment is executed:
- approve the intended claim and workload grid;
- freeze datasets/configs/seeds/protocols;
- freeze comparator version and semantic mapping where applicable;
- freeze metrics and interpretation rules;
- commit `paper/reproducibility/PAPER_PROTOCOL.md` with status `FROZEN_FOR_EXECUTION`.

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