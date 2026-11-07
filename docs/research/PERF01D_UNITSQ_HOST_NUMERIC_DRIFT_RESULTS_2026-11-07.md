# PERF-01D — four prospective-to-this-diagnostic same-original-input native unitsq CPU host replications, 2026-11-07

**MIXED: 1 / 4 HOST REPLICATES EXACT; 3 / 4 STRICT NUMERIC NONMATCH. ORIGINAL 63/64 SCIENTIFIC FITTING NONPASS, INDEPENDENT REVIEW #88 NOT RECEIVED, PERF-01C NOT FROZEN.** This is an exploratory post-result host diagnosis, not a prospective scientific compatibility/benchmark acceptance sample.

## Provenance and prespec

The [4-replica protocol](PERF01D_UNITSQ_HOST_NUMERIC_DRIFT_PRESPEC_2026-11-07.md) was committed at exact SHA **`d22b52f285201b2cecff2d5d54073b17256520bf`** *before new fresh-host trial scalar outcomes*. Four GitHub Actions Ubuntu 24.04 jobs were kept **all** in the matrix with `fail-fast: false`; each independently installed frozen original HGFX 1.0.0 Git SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and Python 3.11, NumPy pinned 2.3.5. No new HGF forward simulation, full fit or MATLAB execution. Genuine original unchanged HGF 71×128 selected-source `infStates`, genuine 71 original Ridders x and original 64-by-128 subject7 input downloaded from exact old sources and all source member SHA-256 validated.

Original genuine [HGF+unitsq source run **42404444341**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42404444341), tested commit `a6168bb2b1be07a0f084abc07599e9ffda61b22b` at frozen MATLAB Toolbox SHA `2437f4dc241541072722a2695ddeca7b44d83dd3`; original HGFX `original-hgfx-71-infstates-and-native-ll.json` SHA-256 `53c998070dbbfc8b8a5c5ce7e8d962b44f9820635f60c567fd2012bf48fcd415`, original MATLAB source `original-matlab-71-infstates-and-cross-ll.json` SHA-256 `15c2f3e50d3ff257d333e412b881053cd6bc0240137ddbae448b3ce7d1647006`, original checked same-run HGF observation field/LL report SHA `5d1d03f200bb8be7bf058fe54d64e63ab8909a29857a6750014bad83db029af0`. Earlier exact original source trial terms (run 42402421462) SHA `eb085a07e633aa10979602d9f9fb5e9221e2a1132aecd9fb7b73953a4d2850df`, old original BFGS x/inputs and original full 63/64 science provenance also validated in each job. Original scientific 63/64 NONPASS; subject7 4 `traj.mu` + 4 `traj.muhat` failures retained; prior 15/16 nonpass and 28-case PERF-01C ledger unchanged.

Actual code in [**run 42405702582**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405702582) exact source commit **`041f648f18bdd515337745a7e8ee782ce822e8eb`**, **10/10 synthetic exact-bit/source guard tests in every one of four jobs**. A fresh original source `unitsq_sgm` evaluation on exact 71 saved 128x3x4 genuine HGFX `infStates`, same original observation transformed `zeta` parameter and native `matlab_exp_scalar`, original zero-based response/regular mask, original inputs, no source edits, no new numerical tolerance. Each original 71×128=**9,088 trial likelihood scalar comparisons** exact binary64 and source/first differing float hex values retained.

## All four jobs — no cherry-picking

| Fixed prespecified replica | Actual Actions runner reported CPU | Exact binary64 native observation re-evaluation vs unchanged original 71×128 source | Number of source nodes with at least one mismatch | Number of individual trial scalar mismatches |
|---|---|---|---:|---:|
| **1** | **Intel Xeon Platinum 8573C** | **NONMATCH** — job FAILED strictly | 12/71 | 12/9,088 |
| **2** | **AMD EPYC 7763 64-Core** | **EXACT** — job SUCCESS | 0/71 | 0/9,088 |
| **3** | **AMD EPYC 9V74 80-Core** | **NONMATCH** — job FAILED strictly | 12/71 | 12/9,088 |
| **4** | **AMD EPYC 9V45 96-Core** | **NONMATCH** — job FAILED strictly | 12/71 | 12/9,088 |

All three nonmatching jobs independently reported **the same first** original mismatch (other changed node/trial indices are retained in each complete JSON artifact; equality of *all* mismatch-location inventories across these hosts is not yet independently proved):

- First genuine original Ridders free x node **zero-based 5**, original trial **zero-based 37**.
- Prior original frozen native HGFX per-trial logp exact bits **`0000000000000000`**, value **`0.0`**.
- Fresh source-on-same-raw-input per-trial logp exact bits **`3ce0000000000000`**, value **`1.7763568394002505e-15`**.
- Absolute difference **`1.7763568394002505e-15`**; giant unsigned ordered ULP integer `4386506037058863104` reflects that the original value was exactly zero, **not** a large scientific error. Both source bit patterns, full 71×128 mismatch source-node/trial indices, floating absolute difference and entire CPU/NumPy runtime/SIMD/ISA environment fingerprint retained separately for all four jobs.

### Immutable four job artifacts

All four were uploaded via `if: always()`, including the 3 strict failures. Whole ZIP SHA-256:

| Replica | Artifact ID | ZIP SHA-256 |
|---:|---:|---|
| 1 | [**13587581720**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405702582/artifacts/13587581720) | `f772163547a1dedcf7196853085b7827ccbad93f139e7dd5d20d120e659af424` |
| 2 | [**13587571775**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405702582/artifacts/13587571775) | `ee33363186c11f83da143774f93bcf41c89a5a359e0a59d9299c58a322b1d9b0` |
| 3 | [**13587432141**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405702582/artifacts/13587432141) | `35649d4e8036df839959b38ec874586fe82c65c826cf1f9e0d56252688b93c8c` |
| 4 | [**13586873687**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405702582/artifacts/13586873687) | `c36e3c4e74203c3762d3da4b0354c15894f71a0506732726d51289be6282191d` |

All are exactly source-sha-linked to [old same-source report and mixed replay](PERF01D_X0_INFSTATE_ARCHIVE_REPLAY_RESULTS_2026-11-07.md): earlier [42405074377](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405074377) similarly failed strict numerical native observation exact check on SHA-identical HGF input, whereas earlier [42405091313](https://github.com/ahmadkhanloo/hgfx/actions/runs/42405091313) fully deep-bit replayed the old source. Never replace original fails with only successes.

## What this supports, and what it does not

**SUPPORTED:** genuine same-raw-original-HGF-input native HGFX observation output is **not guaranteed bitwise identical across these fresh GitHub Actions CPU environments**; outcomes differ across runner CPU models observed in this four-job sample. In the observed three failing jobs, each had 12 real original trial LL bit mismatches over exactly 12 original free x nodes, tiny first 1.78e-15 float gap from exact zero; fourth job succeeded exact all 9,088 scalars. The original same-runner MATLAB-vs-HGFX source observation-stage finding (same genuine predictor and zeta yet differing output) remains supported independently and is not reclassified by these cross-host observations.

**NOT PROVED:** which CPU instruction, NumPy SIMD dispatch, libm implementation/rounding, container baseline, floating environment, operation sequence or serialization source *causes* this host-associated small bit drift. CPU name and failure are **observational correlations**; no supported causal experiment selectively changed CPU vector instruction sets or reproduced a common exact single-instruction failure. Additionally, the current full original 64-subject fit still fails original scientific parity (63/64), and no causal chain from 12 near-zero cross-host observation scalars to later subject-7 4+4 trajectory failures or additional 225 HGFX indirect full fit calls is demonstrated. Original source scientific acceptance thresholds/failed trials not altered; do not declare scientific limitation or numerical tolerance PASS.

**NEXT potential prospective diagnostic:** separately and narrowly trace original `unitsq_sgm` intermediary `log(x)`, `log1p(x-1)`, `log(1-x)`, `log1p(-x)`, `x^zeta`, `(1-x)^zeta`, and final log-normalizer using the same original 71×128 predictors and frozen original zeta on each environment, with exact native 71×128 output reproduction before selecting a first differing arithmetic boundary; record controlled CPU-dispatch interventions separately from observational hardware types.

**Original scientific fitting 63/64 SCIENTIFIC NONPASS**. Original subject 7 **4 `traj.mu` + 4 `traj.muhat`** out-of-tolerance failures. Scientific independent reviewer [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) **NOT RECEIVED**, PERF-01C original 28 cells **NOT FROZEN**, physical GPU and paper runtime speedup **NOT RUN**. Existing host issue [#90](https://github.com/ahmadkhanloo/hgfx/issues/90) remains unresolved with additional independent evidence; original BFGS host drift and current `unitsq_sgm` host drift **cannot be assumed to share a cause** without reference evidence. Draft PR #98 retained.
