# M18A — Parameter Recovery Diagnosis

Status: **PASS — DIAGNOSIS COMPLETE**

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


## Executed diagnosis result

Evidence source:

- workflow: `M18A Parameter Recovery Diagnosis`;
- branch commit: `db9f1dee38237b2cc7010eee2c465265ef1b2a7a`;
- grid: 3 models × {128, 256} trials × 3 replicates at 0.35 prior SD;
- unit tests, diagnosis workflow, full regression, and existing parity checks passed.

### Root-cause summary

| Model / parameter | Baseline median error (prior SD) | Truth-start | Single-parameter oracle | Likelihood-profile offset | Diagnosis |
|---|---:|---:|---:|---:|---|
| HGF `om[1]` | 0.0067 | 0.0063 | 0.0073 | ~0.00 SD | identifiable; healthy |
| HGF `om[2]` | 0.1005 | 0.0643 | 0.1074 | **1.10 SD** | **finite-data likelihood identifiability** |
| HGF `logze` | 0.3908 | 0.3883 | 0.3261 | 0.45 SD | confounding / finite-data mixed |
| eHGF `om[1]` | 0.0428 | 0.0437 | 0.0666 | 0.05 SD | healthy / mild mixed effects |
| eHGF `om[2]` | 0.0902 | 0.0927 | 0.1157 | 0.10 SD | no optimizer pathology; mixed |
| eHGF `logze` | 0.1508 | 0.1507 | 0.0904 | 0.05 SD | cross-parameter confounding |
| uHGF `om[1]` | 0.0371 | 0.0368 | 0.0226 | ~0.00 SD | identifiable; healthy |
| uHGF `om[2]` | 0.1789 | 0.1878 | 0.2157 | **0.90 SD** | **finite-data likelihood identifiability** |
| uHGF `logze` | 0.3957 | 0.3923 | **0.1879** | 0.20 SD | **cross-parameter confounding** |

Errors in this table are standardized by the frozen prior SD, not by the intentionally
small empirical truth spread used by the original M18 standardized-RMSE statistic.

### H1 — optimizer/start point

**Not the dominant cause.**

Across the diagnostic datasets, initializing the full MAP fit at the known generating
truth normally reaches essentially the same solution/objective as the frozen-prior start.
Median objective improvements from truth-start are approximately zero. Several normal
`tol_arg`/`tol_grad` terminations still have substantial recovery error.

Therefore increasing `max_iter` or simply seeding at truth cannot explain or repair M18.

### H2 — cross-parameter confounding

**Confirmed, especially for observation `logze`.**

For uHGF `logze`, median standardized error falls from 0.396 in the full fit to 0.188
when all other parameters are fixed at truth. eHGF `logze` similarly improves from
0.151 to 0.090. This indicates real trade-offs between observation noise/sensitivity and
perceptual volatility parameters.

### H3 — finite-data likelihood identifiability

**Confirmed for the second perceptual volatility parameter.**

With all other parameters fixed at truth, the median likelihood-profile minimum is about
1.10 prior SD away from truth for HGF `om[2]` and 0.90 prior SD for uHGF `om[2]`.
Thus the realized 128/256-trial datasets often favor values meaningfully different from
the generating parameter even before joint fitting or prior effects.

This is the strongest explanation for the poor correlation of the second perceptual
parameter in the original M18 gate.

### H4 — prior-driven MAP bias

**Secondary, not dominant.**

The joint-profile minima are generally closer to truth/prior than the displaced
likelihood minima for problematic `om[2]`. The prior therefore regularizes rather than
being the primary source of the large likelihood displacement. For `logze`, the main
failure is parameter trade-off, not a large systematic prior pull.

## M18A conclusion

M18A is **PASS** as a diagnosis milestone.

The original M18 failure is not evidence of a broad implementation/parity defect:

- the same simulation/objective paths already passed MATLAB parity;
- `om[1]` is strongly recoverable under the same pipeline;
- truth-start fitting does not reveal a hidden better optimizer basin;
- the failure localizes to finite-data identifiability and parameter confounding.

The original M18 thresholds remain unchanged and M18 remains **FAIL**.

## Required next milestone

**M18B — Recovery Protocol Redesign / Identifiability-Aware Validation**

M18B should preserve the frozen M18 result as evidence, then design a scientifically
defensible recovery experiment that separates:

1. intrinsic estimator recoverability at realistic trial counts;
2. parameter identifiability as trial count increases;
3. observation/perceptual confounding;
4. optimizer correctness.

The corrective work must not make M18 pass by merely lowering its thresholds.
