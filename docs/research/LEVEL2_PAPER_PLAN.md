# Methods-Level Paper Plan

## Working title

**HGFX: Scalable Differentiable GPU Inference for Hierarchical Gaussian Filter Models**

## Intended contribution level

This is **not** intended to be only a software-description paper.

The target is a methods paper demonstrating that a modern differentiable JAX implementation can preserve the scientific behavior of established HGF workflows while enabling large-scale CPU/GPU inference.

## Core research questions

### RQ1 — Numerical equivalence
Can HGFX reproduce reference HGF trajectories, likelihoods, objectives, and model-comparison statistics within calibrated numerical tolerance?

### RQ2 — Fitting equivalence
Do compatibility and GPU-native optimizers recover scientifically equivalent parameter solutions?

### RQ3 — Scaling
How does runtime scale with:
- number of trials;
- subjects;
- model candidates;
- random restarts;
- HGF levels?

### RQ4 — GPU crossover
At what workload size does GPU execution become advantageous over CPU/MATLAB baselines?

### RQ5 — Recovery
Does HGFX preserve parameter recovery and model recovery properties?

### RQ6 — Differentiability
Can autodiff provide reliable gradients/Hessians and improve throughput without altering scientific conclusions?

## Required methods contribution

To reach methods-paper level, the final system should ideally include at least two of:

1. validated batched MAP estimation;
2. automatic differentiation of full HGF objectives;
3. GPU-native multi-start optimization;
4. scalable subject/model batching;
5. a compositional custom-model API;
6. GPU Hessian or structured second-order inference;
7. hierarchical/group inference;
8. multi-GPU execution.

## Experimental sections

### Experiment 1 — Forward numerical validation
Reference MATLAB vs JAX CPU vs JAX GPU.

### Experiment 2 — Objective and fitting validation
Fixed-theta objective parity + fitted MAP comparison.

### Experiment 3 — Recovery
Parameter recovery across models and regimes.

### Experiment 4 — Model recovery
Candidate-model confusion matrix.

### Experiment 5 — Performance
Runtime, fits/sec, memory, compilation overhead.

### Experiment 6 — Scaling
Subjects × models × restarts.

### Experiment 7 — Differentiation
Ridders/compatibility derivatives vs autodiff where applicable.

## Minimum benchmark axes

```text
trials: 100 / 500 / 1000 / larger
subjects: 1 / 16 / 128 / 512+
models: 1 / multiple
restarts: 1 / 5 / 10
levels: 2 / 3 / 4+
```

## Baselines

- reference MATLAB HGF;
- MATLAB parallel path when practical;
- JAX CPU x64;
- JAX GPU x64.

## Metrics

Scientific:
- trajectory error;
- likelihood error;
- objective error;
- MAP objective;
- parameter distance;
- recovery metrics;
- model-selection agreement.

Engineering:
- wall time;
- compile time;
- steady-state time;
- fits/sec;
- peak RAM;
- peak VRAM.

## Evidence discipline

Final paper benchmark protocol must be frozen before final benchmark execution.

Raw outputs must be archived and figures regenerated from scripts.

## Likely publication positioning

This project can support a computational-methods manuscript if it demonstrates:
- broad model coverage;
- strong reference validation;
- meaningful acceleration at realistic research scale;
- recovery equivalence;
- methodological benefit from differentiable/batched inference.

A software-only publication remains a fallback, not the primary goal.

## Active correction requirements — 2026-09-11

The active prerequisite is R0–R6 in `docs/planning/MATLAB_PARITY_RECOVERY_PLAN.md`. Preserve the failed historical M18 experiment and report paired MATLAB/Python evidence before attributing failure to identifiability. Separate toolbox parity, recovery performance, protocol integrity and throughput claims. M19/M20 remain open; a diagnostic M18B PASS is not scientific-recovery or release PASS.
