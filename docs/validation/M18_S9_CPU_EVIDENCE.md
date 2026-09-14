# M18 S9 CPU backend evidence

Date: 2026-09-15
Protocol: `m18-s9-robustness-backend-1`
Numerical source commit: `9c53af707a60d27ee3d9d37e5122e7a0ba7d5460`
Frozen MATLAB reference: HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Result

**CPU backend classification: `PASS_CPU_BACKEND_EQUIVALENCE`.**

The post-repair GitHub Actions execution completed successfully on the frozen S9 CPU matrix:

- workflow run: `34901924475`
- job: `104169632034`
- workflow/job conclusion: `success`
- artifact: `10371308067` (`m18-s9-backend-robustness-cpu`)
- artifact digest: `sha256:875e20dedc50618d72cd4a301fd1cccbeb9d941f918a90209e2ad1b05fa48826`
- runner: `ubuntu-24.04`

The successful job executed all three required CPU stages without changing the frozen criteria:

1. S9 standard-HGF/eHGF semantic-boundary regression;
2. existing M14/M15 CPU backend regressions;
3. the frozen S9 robustness/backend matrix covering the required forward regimes, shared-state objective/gradient probes and compatibility-vs-JAX CPU fit comparisons.

The S9 runner returns success only when `cpu_backend_pass` is true. Therefore current numerical code has no unresolved required CPU backend implementation mismatch under protocol `m18-s9-robustness-backend-1`.

## Physical GPU disposition

S9 is **not fully closed yet**. The numerical repair at `9c53af707a60d27ee3d9d37e5122e7a0ba7d5460` changed `src/hgfx/gpu/engine.py`, so older H100 evidence cannot close current-head GPU applicability under the frozen unchanged-path rule.

Current physical-GPU classification remains:

**`PHYSICAL_GPU_REVALIDATION_REQUIRED`**

A CPU-only GitHub-hosted runner cannot be used to infer GPU PASS. The physical H100 revalidation must use the same S9 code/data path and satisfy the frozen CPU-vs-GPU final-objective gap `<= 1e-7`, with device residency and hardware/runtime/command/source evidence recorded.

## Integrity statement

No threshold, seed, dataset, start, model family, optimizer or validation grid was changed to obtain this CPU result. Historical pre-repair failure evidence remains preserved.
