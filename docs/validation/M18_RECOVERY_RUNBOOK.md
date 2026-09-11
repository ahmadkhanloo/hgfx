# M18 Recovery Execution Runbook

## Objective

Execute scientific recovery validation against the MATLAB Toolbox parity target.
The purpose is not to require perfect parameter identifiability, but to distinguish:

1. HGFX implementation mismatch;
2. optimizer/convergence issues;
3. intrinsic model identifiability limitations also present in HGF Toolbox workflows.

## Validation order

### Stage 1 — Smoke validation

Command:

```bash
python scripts/run_m18_scientific_validation.py --preset ci
```

Checks:

- recovery pipeline executes;
- all candidate models are available;
- simulation and fitting parameter ordering agrees;
- JSON result generation works.

### Stage 2 — Parameter recovery

Models:

- hgf_binary
- ehgf_binary
- uhgf_binary

Axes:

- trials: 128, 256
- truth perturbation: 0.15, 0.35 prior SD
- deterministic replicates

Metrics:

- convergence rate
- parameter bias
- RMSE
- median absolute error
- parameter correlation
- standardized RMSE

Interpretation:

A failed metric does not immediately imply a software bug. Diagnose against:

- MATLAB reference behavior;
- parameter identifiability;
- optimizer convergence;
- prior constraints.

### Stage 3 — Model recovery

For each generated model:

- simulate data;
- fit all candidate models;
- select using BIC;
- report confusion matrix.

Required output:

```
generating_model x selected_model
```

and balanced accuracy.

### Stage 4 — Regression gate

Before declaring M18 PASS:

- freeze commit SHA;
- archive JSON outputs;
- verify CPU/GPU agreement;
- keep MATLAB dependency runtime-free.

## Failure classification

| Symptom | Investigation |
|---|---|
| Objective mismatch | M8/M9 parity regression |
| Fit mismatch | optimizer compatibility |
| Poor recovery for one model | identifiability or model-specific issue |
| Poor recovery for all models | pipeline or optimizer issue |
| CPU/GPU difference | numerical backend issue |

## Product acceptance criterion

HGFX v1 is accepted when it reproduces the validated MATLAB Toolbox workflows and limitations, not when it exceeds the scientific behavior of the original toolbox.
