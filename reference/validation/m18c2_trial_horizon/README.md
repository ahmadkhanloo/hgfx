# M18C.2 trial-horizon evidence

Protocol: `m18c2-trial-horizon-identifiability-1`

This directory stores post-v1 paired MATLAB/HGFX horizon-analysis artifacts.
It does not modify historical M18/S7/v1.0.0 evidence.

Full execution is GitHub Actions only:

```text
workflow: PV1-01 M18C.2 Horizon Analysis
trigger: workflow_dispatch with execute_full=true
matrix: 24 shards (3 models × 4 horizons × 2 truth scales)
MATLAB: matlab-actions/setup-matlab@v2 on ubuntu-24.04
```

Expected shard artifacts:

```text
{id}-manifest.json
{id}-matlab.json
{id}-comparison.json
```

Failed fits are retained. Incomplete coverage blocks scientific interpretation.
