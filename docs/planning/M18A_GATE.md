# M18A — Parameter Recovery Diagnosis

Status: **DIAGNOSIS IN PROGRESS**

Parent: M18 Scientific Validation

## Why M18A exists

The preregistered M18 gate failed parameter recovery while model recovery and optimizer
agreement passed. The failed aggregate metrics were:

- minimum model-level convergence rate: 0.75;
- minimum median parameter correlation: 0.2026;
- maximum median standardized RMSE: 2.9579.

The first artifact already shows that the failure is heterogeneous:

- HGF/uHGF first perceptual free parameter recovers well (correlation about 0.97–0.99);
- the second perceptual free parameter and observation `logze` are substantially worse;
- eHGF has better optimizer convergence, yet still fails recovery criteria;
- some uHGF fits terminate normally while retaining large parameter error.

Therefore M18A must not assume that increasing optimizer iterations alone will fix M18.

## Diagnostic hypotheses

M18A separates four hypotheses.

### H1 — optimizer/start-point sensitivity

Evidence test:

- refit the identical dataset from the known generating truth;
- compare final objective and parameter error to the frozen-prior start.

Interpretation:

- large improvement from truth start indicates local optimization/start sensitivity;
- similar endpoints indicate the failure is not primarily caused by the starting point.

### H2 — cross-parameter confounding

Evidence test:

- fix all other parameters at their generating truth;
- optimize each target parameter alone;
- additionally optimize perceptual parameters jointly while holding observation truth fixed.

Interpretation:

- good oracle recovery but bad full recovery indicates parameter trade-off/confounding.

### H3 — finite-data likelihood identifiability

Evidence test:

- hold all other parameters at truth;
- profile negative log likelihood over ±1.5 prior SD around the target truth;
- record profile minimum, span, and local curvature.

Interpretation:

- a likelihood minimum displaced from truth, or a flat profile, means the realized finite
  dataset does not identify the generating value even with all other parameters known.

### H4 — prior-driven MAP bias

Evidence test:

- compare the likelihood-only profile minimum with the negative-log-joint profile minimum;
- compare both locations with the frozen prior mean.

Interpretation:

- likelihood near truth but joint shifted toward the prior indicates prior-driven MAP bias.

## M18A grid

The targeted diagnostic intentionally uses the stronger M18 regime first:

- models: HGF binary, eHGF binary, uHGF binary;
- trials: 128 and 256;
- truth scale: 0.35 prior SD;
- 3 deterministic replicates per model/trial cell;
- full compatibility optimizer;
- 31-point one-dimensional profiles.

The weak `0.15 SD` regime is not used for root-cause classification because its empirical
truth spread is intentionally small and inflates standardized RMSE; it can be revisited
after the mechanism is known.

## Output

```bash
python scripts/run_m18a_parameter_recovery_diagnosis.py
```

writes:

`benchmarks/results/m18a_parameter_recovery_diagnosis.json`

For each dataset and parameter it records:

- baseline fit;
- truth-start fit;
- single-parameter oracle fit;
- perceptual-only oracle fit;
- likelihood profile;
- joint profile;
- profile minima, span, and curvature.

## M18A completion condition

M18A is a diagnosis milestone, not a recovery-performance gate. It is complete when:

1. the diagnostic runner executes reproducibly;
2. every failed M18 parameter has an evidence-backed dominant failure mechanism or a
   documented mixed mechanism;
3. no evidence indicates an implementation discrepancy with the frozen validated
   objective/simulation paths;
4. the next corrective milestone can be specified without lowering M18 thresholds.

M18 itself remains FAIL until a subsequent correction reruns the original frozen M18 gate.
