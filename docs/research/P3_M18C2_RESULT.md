# P3 / M18C.2 official classification

Recorded: 2026-09-18
Protocol: `m18c2-trial-horizon-identifiability-1` (frozen before execution)
Run: GitHub Actions `35272347167` (workflow_dispatch, `execute_full=true`)
Branch: `paper/p3-m18c2-horizon-github-actions` @ `a051e747a3a60054159c81a8b8405fb4b2398277`
Aggregate artifact: `m18c2-horizon-aggregate` id `10521838356`
Aggregate SHA-256: `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`
Historical M18 unchanged: **true**

This file quotes the frozen classifier output. It does not invent a new scientific label.

## Official labels (do not rewrite)

| Field | Value |
|---|---|
| `overall_classification` | **`INSUFFICIENT_REFERENCE_EVIDENCE`** |
| `gate_pass` | **false** |
| `coverage_pass` | **false** |
| `per_model_classification.hgf_binary` | `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` |
| `per_model_classification.ehgf_binary` | `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` |
| `per_model_classification.uhgf_binary` | `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` |

Protocol rule: if the paired-integrity gate fails, **no data-horizon or structural-identifiability conclusion is promoted**. 128/512 are diagnostics only and do not replace 256→1024.

Allowed paper sentence:

> The prospectively frozen trial-horizon experiment completed on GitHub Actions (run 35272347167). The paired-integrity gate did not pass (`INSUFFICIENT_REFERENCE_EVIDENCE`). Historical M18 remains FAIL. This manuscript does not claim that longer trial horizons rescue parameter recovery.

Disallowed: claiming P3 shows short data is the cause; claiming 1024-trial identifiability; ranking HGFX vs MATLAB recovery; promoting ehgf/uhgf diagnostic PASS rows.

## Why the gate failed

Coverage counts are complete (24/24 shards, 144/144 parameter cases, 72/72 model-recovery datasets). The gate still fails because:

1. `all_winners_match = false` — 62/72 BIC winners agree; **10 mismatches**, all `hgf_binary` at T=512 or T=1024.
2. `contract_free_indices_match = false`.
3. `hgf_binary` parameter metrics at T=512 and T=1024 are missing because those truth vectors produced `SIMULATION_INVALID_TRAJECTORY` and were retained, not resampled.

Mismatched model-recovery cases: `MR-hgf_binary-T1024-S0.15-R0/R1/R2`, `MR-hgf_binary-T1024-S0.35-R1/R2`, `MR-hgf_binary-T512-S0.15-R0/R1/R2`, `MR-hgf_binary-T512-S0.35-R1/R2`.

Full numeric table: `paper/tables/p3_horizon_summary.md`.
Local/project copy of the raw aggregate: keep with SHA-256 above. Ingest the ZIP from run `35272347167` before 2026-12-16.
