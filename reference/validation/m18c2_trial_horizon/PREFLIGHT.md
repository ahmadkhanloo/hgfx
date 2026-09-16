# M18C.2 Preflight Evidence

Status: **PRESERVED PRE-EXECUTION FAILURE**

This note preserves the first 512-trial generator failure encountered while implementing the frozen M18C.2 protocol. It is not a scientific PASS/FAIL result and it must not be removed merely because the pipeline is later made capable of recording the case.

## Exact evidence

- branch: `pv1-01-m18c2-horizon-analysis`
- generator implementation head: `56df7aad10dd362ea210b66ca9734ab89dae959d`
- GitHub Actions workflow: `PV1-01 M18C.2 Horizon Analysis`
- workflow run: `35110604757`
- job: `104843000061`
- frozen HGF reference guard: **PASS** at `2437f4dc241541072722a2695ddeca7b44d83dd3`
- focused tests before generator execution: 6 prior contract tests PASS
- failing case: `hgf_binary`, 512 trials, truth scale `0.15`, parameter-recovery replicate `0`
- frozen case seed: `70718`
- response seed: `70719`
- failure location: truth-data simulation through the validated HGFX HGF forward path
- error type: `ValueError`
- error message: `Variational approximation invalid. Parameters are in a region where model assumptions are violated.`

## Root-cause classification

This is not a hash, seed-formula, or CI-environment defect. The fixed truth/input combination reaches the HGF trajectory-validity boundary at the longer horizon. Historical M18B evidence already records a distinct 512-trial HGF case where MATLAB and HGFX share a variational-approximation limitation (`REFERENCE_LIMITATION_MATCH`).

The M18C.2 protocol therefore keeps the seed and case unchanged. The implementation is being changed only so generation failures are serialized as evidence instead of aborting the whole shard. No failed case will be resampled, dropped, assigned a new seed, or silently replaced.

## Interpretation rule

A generation failure is not parameter-recovery non-convergence and must not be folded into RMSE/correlation as if a dataset had been successfully generated. Downstream aggregation must expose it separately as a model/generation-validity limitation and withhold the preregistered identifiability interpretation for any affected model/horizon unless paired reference evidence establishes an appropriate narrower classification.
