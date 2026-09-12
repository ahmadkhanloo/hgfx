# Benchmark Plan

## Hardware capture

Every run records:
- CPU model;
- RAM;
- GPU model;
- VRAM;
- CUDA version;
- driver version;
- Python version;
- JAX version;
- MATLAB version;
- HGF reference commit;
- HGFX commit.

## Timing policy

Separate:
- cold compile;
- warm/steady-state execution;
- data transfer;
- optimizer time;
- postprocessing.

## Repetitions

Use repeated runs and report:
- median;
- IQR;
- min/max;
- failure count.

## Output

Write machine-readable benchmark files to:

`benchmarks/results/`

Do not manually type paper tables.

## Active correction requirements — 2026-09-11

Correctness has priority: complete the relevant R0–R5 gates in the active MATLAB parity recovery plan before new performance claims. Attach benchmark rows to the validated HGFX commit, fixture/protocol hashes and supported family/regime/backend. Existing contended H100 measurements remain valid within their documented scope; an idle server is not required, but contention must be reported.
