# M18 — Scientific Validation Gate

Status: **FAIL — HISTORICAL GATE; CORRECTIVE WORK OPEN**

The immutable failed output is `reference/validation/m18_scientific_validation.json`; provenance is beside it. See [MATLAB parity recovery plan](MATLAB_PARITY_RECOVERY_PLAN.md) for R0–R6. M18B protocol integrity does not close this gate. A redesigned experiment must use a separate protocol/version and preserve this result.

Frozen reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Scientific question

M18 tests whether HGFX preserves scientific inference behavior beyond pointwise MATLAB parity:
parameter recovery, model recovery, robustness across trial counts and parameter regimes,
optimizer agreement, and CPU/GPU agreement.

The protocol is frozen **before** the final gate run. Acceptance thresholds are encoded in
`scripts/run_m18_scientific_validation.py`; final results may not change those thresholds.

## Candidate family

The first preregistered recovery family is:

- `hgf_binary`
- `ehgf_binary`
- `uhgf_binary`

All candidates use the validated `unitsq_sgm` observation model.

Model recovery is not a proxy comparison: each candidate is independently MAP-fitted to
the same simulated dataset using the validated M8 objective semantics and M9 compatibility
quasi-Newton optimizer. BIC is the preregistered winner rule; AIC is retained as a
secondary diagnostic.

## Parameter-recovery design

For each generating model:

1. deterministically generate non-degenerate binary inputs;
2. perturb free transformed-space parameters around their frozen prior means;
3. transform the complete vector to native parameters;
4. simulate responses through the model and `unitsq_sgm`;
5. fit the same model from its frozen default starting point;
6. record truth, estimate, error, convergence, and objective.

Gate axes:

- trials: 128 / 256;
- truth perturbation scales: 0.15 / 0.35 prior SD;
- 6 replicates per trial-count/scale/model;
- deterministic seeds.

Reported metrics: per-parameter bias, RMSE, median absolute error, correlation,
standardized RMSE, and optimizer convergence rate.

## Model-recovery design

For each HGF/eHGF/uHGF generator, each trial count and truth regime, simulate data and fit
all three candidates. Report the row-normalized generating-model × selected-model
confusion matrix and balanced accuracy.

Gate axes:

- trials: 128 / 256;
- truth perturbation scales: 0.15 / 0.35 prior SD;
- 3 replicates per cell;
- BIC winner as primary model selection criterion.

## Preregistered minimum criteria

These are minimum scientific sanity criteria, not claims of perfect identifiability:

| Criterion | Threshold |
|---|---:|
| convergence rate, every parameter-recovery model | >= 0.80 |
| median parameter correlation, every model | >= 0.50 |
| median standardized RMSE, every model | <= 1.00 |
| model-recovery balanced accuracy | >= 0.50 |
| compatibility vs JAX-CPU final objective gap | <= 0.10 |
| JAX CPU vs GPU final objective gap when a GPU is visible | <= 1e-7 |

The GPU criterion is evaluated automatically on GPU-capable runtimes. Physical H100
fit parity was already independently established in M15/M17; M18 additionally records
the same scientific-validation dataset comparison when run on a GPU host.

## Reproducibility

Smoke/CI:

```bash
python scripts/run_m18_scientific_validation.py --preset ci
```

Final gate:

```bash
python scripts/run_m18_scientific_validation.py \
  --preset gate \
  --output benchmarks/results/m18_scientific_validation.json
```

The output is machine-readable JSON. `benchmarks/results/` is intentionally ignored by
Git; CI uploads the result as an artifact. Final Methods-paper results should be archived
with commit SHA and environment metadata rather than copied manually into tables.

## Pass condition

M18 becomes PASS only when:

- the complete gate preset finishes reproducibly;
- all preregistered non-hardware checks pass;
- CPU/GPU agreement is either observed in the M18 output on a physical GPU host or
  explicitly linked to the frozen M15/M17 physical-H100 evidence without changing the
  scientific code path;
- full regression remains green.
