# REV-1.4 — Frozen first-divergence localization protocol

Status: **PRECOMMITTED / EXPERIMENT NOT YET RUN**. Parent: [COMPSTAT_REVISION_PLAN.md](../../../docs/planning/COMPSTAT_REVISION_PLAN.md), REV-1.4 (C1). This file must be committed **before** the diagnostic is executed. REV-1.4 remains OPEN until a separate, evidence-backed terminal ledger report.

## Required claim and discriminating question

The manuscript must not equate fixed-parameter Forward agreement with full-fit agreement. The diagnostic asks whether the original four asymmetric horizon cases and one 64-fit trajectory failure arise from HGFX same-vector model/objective divergence, reference/optimizer path sensitivity, or insufficient original intermediate evidence. **Do not assume optimizer sensitivity explains a failure.** Preserve all five failures independently.

## Immutable sources

- HGF Toolbox 8.2.0: `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- HGFX public 1.0.0: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Any later development-line diagnostics must be separately labeled and cannot retroactively validate 1.0.0.
- P3 original horizon workflow: [35272347167](https://github.com/ahmadkhanloo/hgfx/actions/runs/35272347167); original execution head `a051e747a3a60054159c81a8b8405fb4b2398277`; protocol `m18c2-trial-horizon-identifiability-1`. Immutable aggregate: `paper/reproducibility/p3_m18c2_aggregate_35272347167.json` SHA-256 `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`. The full historical P3 gate remains **FAIL / INSUFFICIENT_REFERENCE_EVIDENCE**, never overwritten.
- The **two specific original P3 shard** archive entries (GitHub API artifact ZIP digest, to be verified independently against obtained ZIP bytes or extracted-member digests where possible):
  - `m18c2-shard-hgf-t512-s035`, artifact **10519038480**, ZIP SHA-256 `35effd1aa5f46afa874042d0df9b15389ae5eb2fa0294482d7ffc52223c1d940`.
  - `m18c2-shard-hgf-t1024-s035`, artifact **10519860062**, ZIP SHA-256 `e6f6e05417f3fc7ec1f0fc2907ff026a704aebeff59651402adbb050ddc24e66`.
- Original **64-subject** raw full-fit: [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006), artifact **13341288055** (`perf01-64-full-fits-41863441006`), ZIP SHA-256 `45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587`. Exact raw members: `hgfx_raw.json` SHA-256 `6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb`, `matlab_raw.json` SHA-256 `2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98`, and `comparison.json` SHA-256 `97877d64f609a62b3ca10674809907ae18562321c170f9b47aebaf672f3fcede`.
- Existing original 64-fit result: **63/64** diagnostic-concordant, subject zero-based **7** NONPASS, `traj.mu` out-of-gate at `[83,1],[108,1],[116,1],[126,1]`; `traj.muhat` at `[84,1],[109,1],[117,1],[127,1]`. These are historical findings, not a new cause localization or a PASS.

## Frozen five-case selection and sources

| ID | Model / stratum | Replicate | Historical deterministic seed | Source |
| --- | --- | ---: | ---: | --- |
| `PR-hgf_binary-T512-S0.35-R0` | HGF, T=512, scale=0.35 | 0 | 72718 | P3 512 shard |
| `PR-hgf_binary-T512-S0.35-R4` | HGF, T=512, scale=0.35 | 4 | 72722 | P3 512 shard |
| `PR-hgf_binary-T1024-S0.35-R0` | HGF, T=1024, scale=0.35 | 0 | 123918 | P3 1024 shard |
| `PR-hgf_binary-T1024-S0.35-R4` | HGF, T=1024, scale=0.35 | 4 | 123922 | P3 1024 shard |
| `subject_index_zero_based=7` | 64-fit cohort, HGF, T=128 | 7 | source-defined; **do not infer a seed** | Original 64 full-fit archive |

Seed formula is the original preregistered P3 generator: `18018 + round(10000*scale) + 100*T + replicate` for these parameter-recovery cases. Only original `manifest.json`/case `case_sha256` and generator source decide source fidelity; never re-simulate a failed case with a replacement seed.

## Preregistered diagnostic sequence — no grid rerun

1. **Source-integrity stage (no fitting):** fetch only the two P3 shards and original 64-fit archive. Verify available exact artifact ZIP hashes, archive member hashes, protocol ID, source workflow/head, case IDs, deterministic seed/replicate/scale/T, case SHA-256, both implementations' original case outcomes, and original 63/64 plus subject-7 failing cells. Record all unavailable fields explicitly; missing original `u`/`y` is not silently regenerated as a substitute.
2. **First-exceedance stage:** compare *the same* original MATLAB/HGFX 64-fit raw subject-7 Forward trajectories and other matching trial × level arrays at pre-existing `abs(diff) <= 3e-10 + 3e-8 * abs(MATLAB_reference)` if that is the original applicable per-field gate. Record the earliest zero-based trial, level, variable for each field, exact values, delta and allowed error; distinguish first nonzero difference from first tolerance exceedance. An earlier within-gate discrepancy must not be described as an error. Preserve full eight original exceedances. No new threshold.
3. **Same-input / same-start stage** (only if source stage validates complete P3 inputs): for the four selected P3 cases, use the original validated `u`, `y`, config, transformed free-index order, and initial free vector, and compare MATLAB 8.2.0 vs HGFX 1.0.0 **at that same vector**: negative log likelihood, negative log joint, per-trial log likelihood, and level/state intermediates where both produce them. Check first divergence *before* discussing optimizer endpoints. A case where simulation was originally invalid/`y` empty remains an invalid-simulation case; do **not** call `fitModel` with invented responses.
4. If the initial objectives agree, classify discrepancies in optimizer trace and endpoint separately; no claim of optimizer sensitivity without matched-input MATLAB evidence. If objective is non-finite, distinguish shared `-inf` from a one-sided non-finite and find its first causative trial/state if raw outputs permit. No post-hoc parameter/tolerance adjustments.
5. For subject 7, do not infer an intermediate numerical cause from `traj.mu`/`traj.muhat` alone. If original raw intermediate arrays are absent, report first *observed* output discrepancy and an explicit missing-intermediate blocker. A fresh exact-subject oracle trace must preserve the same model/input/initial parameters.

## Scope, attempt cap and stopping

- **Exactly four P3 cases and subject 7; no additional horizons, seeds, models, datasets, restarts, or fits.** No P3 full grid rerun. Maximum **two fix attempts** if a demonstrated code defect is found. This source-only audit is *not* a fix attempt.
- One preregistered execution of each diagnostic experiment; at most one separately logged rerun for infrastructure failure. Working tests may exercise synthetic fixtures, but not re-run fitting.
- Avoid 1.0.0 modifications. A proven HGFX code fix requires a golden failing test and separate v1.0.1/main change (or an explicit new maintenance release decision); no alteration of historical v1.0.0 evidence.
- **Terminal options**: `FIXED` only with verified golden repair, `EXPLAINED` only with a demonstrated cause and evidence, otherwise `DOCUMENTED_LIMITATION` after the bounded attempts/time box with precise missing first-divergence fields. This diagnostic cannot alone turn P3 or PERF-01C into PASS.
- Stop/escalate when source files are missing, MATLAB cannot run, the time box is exceeded, an unexplained HGFX defect changes a headline manuscript claim, or a human D1 decision is needed. Record negative findings. Do not proceed to REV-2 before D1.

## Output contract

`evidence/revision/first_divergence_audit.json` (aggregate-only: input hashes, 5 fixed IDs, per-case source/finite/objective/trajectory status, first observed trial/level/variable or explicit unavailable marker, unmodified reference tolerance, and release classification); ≤15-line terminal report in `COMPSTAT_REVISION_LEDGER.md` with computed SHA-256, workflow/commit, actual runtime, remaining limitations. Never commit raw participant data. Evidence from archival outputs must be distinguished from newly executed cross-objective MATLAB/HGFX runs.
