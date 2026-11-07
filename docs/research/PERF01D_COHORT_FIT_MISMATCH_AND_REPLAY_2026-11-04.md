# PERF-01D — all-64 complete fitting mismatch and subject-7 exact-vector replay (2026-11-04)

Status: **DIAGNOSTIC SCIENTIFIC EVIDENCE, FITTING 16/64 NOT FULLY CONCORDANT; NO TIMING**  
Protocol: `hgfx-matlab-runtime-1` (**NOT FROZEN**)  
Tracking: [PERF-01 #86](https://github.com/ahmadkhanloo/hgfx/issues/86), [mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89), [independent pre-freeze review #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87).

## Immutable sources and experiment identity

- HGFX `v1.0.0` distribution/source commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- HGF Toolbox **8.2.0**, source commit `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2026a.
- Exactly the original `benchmarks/runtime_v1/inputs/binary_128_s64.json` and `configs/hgf_binary_128.json`: 64 subjects, 128 trials, unchanged deterministic inputs, observation model `unitsq_sgm`, native parameter start, prior/fixed/free indices and `quasinewton_optim_config`.
- No runtime timing, no GPU, no changed seeds, starts, optimization thresholds, model family, trial count, excluded subjects, reference outputs or historical evidence.

## 64 complete public fitting workflows

[CI run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) performed the full `fitModel` vs `fit_model` calls and emitted the source-verified complete output fields including `optim.final`, Hessian, Sigma, Corr, LME/decomposition, AIC/BIC, trial likelihood, predictions, residuals and all trajectory fields. All 64 subjects remain in the result.

- Scientific diagnostic classification: **63/64 within inherited field-specific diagnostic thresholds, 1/64 with out-of-tolerance fitted trajectory entries**. The scientific comparator **intentionally failed** the workflow rather than declaring a scientific PASS. Its raw original outputs remain available as artifact `perf01-64-full-fits-41863441006`, checksummed from `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json`.
- Original nested cohorts: **1/1**, **15/16**, **63/64** compatible *full-fit outputs*. The original first-subject fit remains concordant; **both** 16- and 64-subject fit strata remain **BLOCKED_SCIENTIFIC_PARITY** under the existing diagnostic criteria.
- The only out-of-tolerance subject is **zero-based index 7** (eighth original subject). Only `traj.mu` and `traj.muhat` fail; there are **four** out-of-tolerance positions in each field. First `mu` mismatch: zero-based **[83,1]**, first `muhat`: **[84,1]**. Each field has maximum absolute delta `1.5704625655477145e-9`. All other compared fitted-output fields, including estimated parameters and posterior statistics, remain within their existing per-field numerical diagnostic tolerances. Maximum difference between the distinct final full fitted vectors: `3.277081539465598e-8`.
- MATLAB and HGFX each retained **101 iteration-history values** and `nRandInit=0`. Equality of history length does **not** establish identical iteration paths, identical optimizer convergence or scientific identifiability.

## Exact fitted-vector cross-replay to localize the mismatch

Two archived fitted endpoint vectors—one from HGFX and one from MATLAB—were taken **from the unchanged original raw fit artifact**, with raw SHA-256 rechecked against `summary-41863441006.json`. No fitting or parameter adjustment took place in the replay.

[Successful CI run 41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514) executes frozen HGF forward and `unitsq_sgm` at **each identical parameter vector on both platforms** and compares all `infStates`, eleven trajectory fields, per-trial likelihood, `yhat` and residuals, keeping the previous `atol=3e-10, rtol=3e-8` diagnostic tolerances unchanged.

| Frozen replayed exact vector | MATLAB/HGFX same-vector result | Largest observed illustrative delta |
|---|---|---:|
| Original **HGFX fitted endpoint** | **All 15 full trialwise fields within diagnostic tolerances** | `traj.psi` ~`2.0605739337042905e-13` |
| Original **MATLAB fitted endpoint** | **All 15 full trialwise fields within diagnostic tolerances** | trial log-likelihood ~`4.440892098500626e-16` |

Within each **single** implementation, comparing the *two distinct original fitted endpoint vectors* reproduces the same out-of-tolerance discrepancy in `traj.mu` and `traj.muhat`:

- First distinct-vector `traj.mu` mismatch at **one-based trial 84**; maximum absolute delta `1.5704625655477145e-9` in both implementations.
- First distinct-vector `traj.muhat` mismatch at **one-based trial 85**; maximum absolute delta `1.5704625655477145e-9` in both.
- `infStates` also differs between the **two different parameter vectors** within each implementation. That is not a same-parameter implementation mismatch.

Machine evidence: `benchmarks/runtime_v1/subject7_results/summary-41868723514.json`. Archived original raw reference/HGFX outputs and SHA-256 provenance are recorded there; the uploaded artifact is `perf01-subject7-same-vector-41868723514`.

**Narrow diagnostic interpretation:** the observed fitted-trajectory discrepancy is reproduced by the difference between the two original Optimizer final vectors, while matched-vector numerical forward evaluation agrees. This is **`OPTIMIZER_ENDPOINT_SENSITIVITY_CANDIDATE`**, **not** proof that the frozen MATLAB optimizer is inherently unstable, not a scientific `REFERENCE_LIMITATION_MATCH` verdict, and **not** full fitting parity on the original 64-subject workflow. A legitimate reference-limitation disposition would require further frozen MATLAB reference self-sensitivity and optimizer-path/convergence evidence, independently reviewed under the existing policy.

## Engineering failures and archive integrity

- [Initial cross-replay run 41868107083](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868107083) failed **before MATLAB replay**: research-only Python JSON reporter calculated a descriptive maximum over a full fitted vector containing nonfinite fixed-value placeholders, producing `NaN` in strict JSON output. Original fit artifact hashes were already verified; no modified numerical result was produced. The reporter was repaired to compare **only paired finite parameter positions** while separately retaining the nonfinite masks. The successful run `41868723514` does not erase this failed execution.
- [HGFX Regression run 41864233108](https://github.com/ahmadkhanloo/hgfx/actions/runs/41864233108) failed a **synthetic test-fixture shallow-copy error**, not a product numerical regression (Windows: 246 passed, 1 failed, 4 skipped). The test fix deep-copied its synthetic MATLAB nested `optim` fixture; the error and fix are preserved in Git history, with new CI to be verified on the latest commit.
- The original all-64 fit workflow failed **intentionally** due to one true output discrepancy; preserve its non-PASS status and evidence. Do not reclassify a scientifically failed workflow as success merely because its reporting steps completed.

## Scope and next gate

- The previous 28-case prefreeze eligibility candidate reported **16 diagnostic concordant / review pending; 12 blocked**. A separately generated *new* derived eligibility candidate may replace the **reason** for the two blocked 16-/64-subject 128-trial cells from `BLOCKED_MULTISUBJECT_FIT_PARITY_NOT_VALIDATED` to `BLOCKED_MULTISUBJECT_FIT_NUMERICAL_MISMATCH`, but must not change the original candidate or demote the evidence of 1/16 and 1/64 failure.
- The original nine-cell primary HGF speedup headline remains blocked, with six ineligible frozen 512-/1024-trial cases. Newly proposed scoped `RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md` remains **DRAFT / NOT FROZEN**.
- Required before a scientific reference limitation claim: MATLAB reference-only optimizer end-point/startpoint sensitivity; terminal convergence behavior and exact optimizer termination compared at the same frozen data/parameters; independent reviewer audit.
- Required before any matched runtime or GPU claim: approved independently reviewed protocol lock and CPU timeable boundary, verified same-host CPU/threads/affinity, actual physical GPU environment and prospective statistics.

**Performance result: `NOT RUN`. No MATLAB–HGFX speedup has been established.**


## Reference-only sensitivity addendum — 2026-11-04

The previously listed reference-only sensitivity blocker was investigated *without changing the frozen MATLAB library or its 64-subject baseline data*. [GitHub Actions run 41870479069](https://github.com/ahmadkhanloo/hgfx/actions/runs/41870479069) uses the exact frozen `core/quasinewton_optim.m`, `_original_models/hgf_binary.m`, `observation/unitsq_sgm.m` and an independently composed exact-form `negLogJoint` equivalent from source. **The unperturbed MATLAB reference optimizer endpoint was exactly reproduced** (maximum original-endpoint discrepancy `0`; source joint `100.73136405842156`). This is a prerequisite to interpreting the subsequent diagnostic perturbations.

Each of the **three original free initial coordinates** was independently changed by `-eps(x)` or `+eps(x)` while the original source data, prior means/variances and optimizer algorithm/options remained the same. Exactly one of the six reference-only runs crossed the inherited v1 parameter-final numerical tolerance: **free coordinate index 2 (zero-based), `-4.440892098500626e-16` initial perturbation**, final parameter vector maximum absolute shift **`7.640946009246363e-7`**. The other five recorded endpoint shifts are also archived; do not omit them. Machine evidence: `benchmarks/runtime_v1/matlab_sensitivity_results/summary-41870479069.json` and artifact `perf01-matlab-reference-self-sensitivity-41870479069`.

**Interpretation:** the frozen MATLAB reference is empirically start-sensitive for the identical subject/model/regime at one-ULP perturbation. Together with exact same-vector forward parity [41868723514](https://github.com/ahmadkhanloo/hgfx/actions/runs/41868723514), this supports a *specific optimizer numerical-basin sensitivity candidate* as the explanation for the original single-subject trajectory mismatch. It does **not** overwrite the original 63/64 fitting comparison, prove that optimizer algorithms are identical in every basin, resolve scientific identifiability, or authorize `REFERENCE_LIMITATION_MATCH` or a CPU speedup without independent audit and exact-scope disposition. [Issue #89](https://github.com/ahmadkhanloo/hgfx/issues/89) and independent [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) remain **OPEN**.

The revised, **separately derived and still unapproved** [28-case candidate](../../benchmarks/runtime_v1/eligibility_candidates/candidate_v2_fullfit41863441006.json) was committed by [run 41869747776](https://github.com/ahmadkhanloo/hgfx/actions/runs/41869747776). It preserves the original 28-cell ledger and **16 diagnostic-concordant pending-review / 12 blocked** accounting, with specific actual mismatches for 16/64-subject fitting. The frozen original v1 release and prior paper gate remain unchanged; `PERF-01C = NOT FROZEN` and `PERF-01E–H = NOT RUN`.
