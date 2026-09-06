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
