# Benchmark Plan

Last synchronized: 2026-09-13
Status: **IN PROGRESS — final paper benchmark protocol not frozen**

## Principle

Scientific/reference equivalence is validated before performance claims are interpreted. A faster backend is not acceptable evidence for v1 if it changes validated scientific behavior.

The final paper benchmark must distinguish three questions:

1. Does HGFX reproduce the frozen MATLAB reference on the required scientific/workflow surface?
2. Do HGFX backends agree with the validated compatibility path?
3. After 1–2 are satisfied, how much performance/scaling benefit is obtained?

## Reference identity

Every MATLAB-paired scientific run must record:
- MATLAB HGF Toolbox version;
- frozen HGF reference commit;
- MATLAB version;
- HGFX commit;
- protocol version/hash;
- dataset/file checksums;
- model family and observation model;
- configuration/prior hashes or serialized values;
- fixed/free parameter mask;
- initial point/start/restart policy;
- seeds and, where RNG identity cannot be guaranteed, exported stochastic drivers;
- acceptance thresholds used before examining the result.

For v1 the compatibility oracle is HGF Toolbox 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## Paired scientific comparison policy

A MATLAB/HGFX comparison is valid only when the compared runs use the same scientific workflow. Before classifying a mismatch, verify:
- same data and trial masking;
- same model family;
- same observation model;
- same parameter order/transforms;
- same priors and fixed/free semantics;
- same start point/restart selection;
- same seed or exported random driver;
- same fitting/simulation workflow.

If MATLAB itself fails or selects a different model family for the exact matched case, record that as reference evidence rather than silently forcing another HGFX workflow.

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
- classification: `PASS`, `IMPLEMENTATION_MISMATCH`, `OPTIMIZER_MISMATCH`, `MODEL_SELECTION_MISMATCH`, `REFERENCE_LIMITATION_MATCH`, or `INSUFFICIENT_REFERENCE_EVIDENCE`.

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
- CUDA version;
- driver version;
- Python version;
- NumPy version;
- JAX/JAXLIB version;
- MATLAB version where applicable;
- HGF reference commit;
- HGFX commit;
- device visibility/residency evidence;
- whether the GPU system is shared/contended.

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

## Benchmark axes

The final M19 matrix will select and freeze scientifically justified values across:
- trials;
- subjects;
- model candidates;
- restarts;
- HGF levels/model families;
- CPU/JAX CPU/GPU backend;
- GPU count where applicable.

Earlier exploratory axes such as `100/500/1000` trials and `1/16/128/512+` subjects remain planning candidates, not frozen paper requirements until M19.

## Current performance evidence

Physical H100 evidence exists for M14–M17. The recorded M17 shared-system scaling snapshot is:
- 1 GPU: median `81.719055 s`, `0.783 subjects/s`, `1.566 fits/s`, speedup `1.000`, efficiency `1.000`;
- 2 GPU: median `73.838342 s`, `0.867 subjects/s`, `1.734 fits/s`, speedup `1.107`, efficiency `0.553`;
- 4 GPU: median `58.860710 s`, `1.087 subjects/s`, `2.175 fits/s`, speedup `1.388`, efficiency `0.347`.

This evidence may be used in the final paper only after the M18/S9 applicability audit confirms that the benchmarked path remains representative of the final validated implementation.

## Output and provenance

Machine-readable outputs go under versioned benchmark/evidence paths; final M19 should define the exact frozen layout. Paper tables and figures must be generated by scripts from machine-readable data.

Every paper-used result must be traceable to:
- HGFX SHA;
- MATLAB reference SHA if paired;
- run/job identifiers or equivalent local provenance;
- artifact ID/name;
- artifact SHA-256;
- command/protocol;
- environment record.

Do not manually type final numerical paper tables from memory or chat summaries.

## M19 freeze

Before final benchmark execution/publication results are declared frozen:
- close required M18 v1 equivalence/recovery/robustness gates;
- approve the final workload grid and thresholds before running it;
- freeze datasets/configs/seeds/protocols;
- run the final benchmark matrix;
- archive raw outputs and hashes;
- freeze figure/table generation scripts;
- record any failed/limited cells rather than deleting them.

After M19, corrections to scientific results require an explicit new protocol/version and must not silently rewrite the frozen evidence set.
