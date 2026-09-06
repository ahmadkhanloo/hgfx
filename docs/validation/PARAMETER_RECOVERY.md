# Parameter Recovery Plan

For each selected model:

```text
theta_true
   ↓
simulate
   ↓
fit
   ↓
theta_hat
```

Report:
- bias;
- RMSE;
- correlation;
- convergence/failure rate;
- recovery by parameter;
- recovery by trial count;
- recovery by noise regime;
- recovery CPU vs GPU.

Predefine parameter grids before final paper runs.
