# PERF-01D — Trialwise and full-fitting diagnostic evidence (2026-11-04)

Status: **DIAGNOSTIC SCIENTIFIC EVIDENCE COMPLETE FOR EXECUTED CELLS; PERF-01D NOT FROZEN / NOT CERTIFIED PASS**  
Benchmark protocol: `hgfx-matlab-runtime-1` (**SPECIFIED, NOT FROZEN**)  
Tracking: [#86](https://github.com/ahmadkhanloo/hgfx/issues/86), [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87)

## Immutable scientific comparators

- `hgfx==1.0.0`, product SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; isolated from mutable `main` (which currently reports `1.1.0b1`).
- MATLAB HGF Toolbox **8.2.0** @ `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB **R2026a**.
- Canonical 64-subject `u`/`y` JSON inputs for horizons 128, 512 and 1024; 9 candidate resolved config/start snapshots; source file SHA-256 stored in `inputs_manifest.json` and `resolved_configs_manifest.json`. No data, seed, start or threshold was changed after observing failures.
- Same GitHub Actions **CPU runner** within each trialwise and fitting comparison workflow. **No timing**, physical GPU, multi-GPU or claimed accelerator comparison.

## Stage 1 — Full trialwise evidence

[Workflow 41854644533](https://github.com/ahmadkhanloo/hgfx/actions/runs/41854644533) **success** as diagnostic script execution. Machine-readable classification:  
`benchmarks/runtime_v1/trialwise_results/summary-41854644533.json`.

Ten exact fixed-vector cells (three model variants × three horizons plus one masked HGF) were preserved:

- **7 / 7 completed cells:** all 4 `infStates` channels, all eleven `traj` fields (`mu`, `sa`, `muhat`, `sahat`, `v`, `w`, `da`, `ud`, `psi`, `epsi`, `wt`), trial likelihood, `yhat`, and residuals were within the preexisting diagnostic `rtol=3e-8, atol=3e-10` criteria. Largest observed raw absolute difference over these compared vector fields: **1.5631940186722204e-13** (`uhgf_binary`, 1024 trials, trial log-likelihood). No scientific acceptance gate or source code was changed.
- **3 / 3 invalid standard-HGF inputs:** both frozen implementations report invalid trajectory behavior. The first invalid **prefix length**, found by sequentially invoking each unchanged implementation, matches exactly:
  - HGF 512 regular: **348**;
  - HGF 1024 regular: **346**;
  - HGF 512 masked: **349**.
- These are *first invalid prefix lengths under the original prefix-specific RMS validator*, not necessarily the first instantaneous mathematical divergence in an unvalidated raw recurrence. This distinction matters because the validator uses an RMS aggregated over the current prefix; a binary-search monotonicity assumption is invalid.
- Invalid cases remain **BLOCKED_SCIENTIFIC_PARITY / REFERENCE-BEHAVIOR MATCH DIAGNOSTIC**, not newly declared general `REFERENCE_LIMITATION_MATCH` scientific PASS.
- Raw data are archived as GitHub Actions artifact `perf01-trialwise-run-41854644533` and linked by SHA-256 in the summary. The GitHub workflow result alone is not a scientific-parity acceptance decision.

## Stage 2 — Full fitModel boundary evidence

[Workflow 41855647245](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855647245) **success** as diagnostic script execution. Machine-readable classification:  
`benchmarks/runtime_v1/fitting_results/summary-41855647245.json`.

All **three** preregistered primary fitting horizons remain accounted for:

| Horizon | Status | Interpretation |
|---:|---|---|
| 128 | `FULL_FIT_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES` | Actual MATLAB `fitModel` and HGFX `fit_model` completed; final free/full parameters, H, Sigma, Corr, negLl, negLj, LME and decomposition, AIC/BIC, trial log-likelihood, prediction/residual/autocorrelation and trajectory compared with previously documented M10-family diagnostic tolerances. No out-of-tolerance field in this run. |
| 512 | `BLOCKED_UNSTABLE_DEFAULT_START_NONCOMPARABLE_RESTART_POLICY` | Fixed initial HGF forward/objective invalid in both packages; no fitting performed on this preregistered cell. |
| 1024 | `BLOCKED_UNSTABLE_DEFAULT_START_NONCOMPARABLE_RESTART_POLICY` | Same condition; no fitting performed. |

Maximum observed 128-fit absolute differences in the compared fields: full final parameters **9.048761739904876e-12**, Hessian **9.621636820611457e-12**, covariance `Sigma` **2.537614562925228e-10**, `traj.psi` **1.524789183804387e-10**. These are descriptive values only.

**Critical workflow distinction:** the frozen MATLAB `fitModel.m` automatically resamples unstable initial parameters from prior distributions (up to 1000 attempts) when the default start is invalid. The HGFX 1.0.0 compatibility fitting API rejects an invalid default start instead. Without a prospectively fixed, semantically equivalent start-control policy, the 512- and 1024-trial fitting runtimes are **NOT DIRECTLY COMPARABLE**. Benchmarking MATLAB's automatic random retries against HGFX's immediate error is prohibited.

The first fitting diagnostic workflow [41855569387](https://github.com/ahmadkhanloo/hgfx/actions/runs/41855569387) failed **at JSON serialization of an HGFX `MatlabStruct`**, before producing a fitting artifact; its log remains preserved. This exporter-only defect was repaired in the research tooling, without modifying HGFX 1.0.0, MATLAB reference, seeds, starts, or numerical criteria. Run 41855647245 is the successful rerun.

## Matrix, gate and claim decisions

| Gate | Status after these experiments |
|---|---|
| PERF-01A | **PARTIAL**: MATLAB R2026a and exact toolbox available in CI; validated matched CPU thread controls and physical GPU environment still missing |
| PERF-01B | **IMPLEMENTED, REVIEW PENDING**: canonical input/config/start candidate files and checksums committed; full 64-subject cross-language semantics audit and protocol lock still missing |
| PERF-01C | **OPEN / NOT FROZEN**: independent scientific/methodology review, finalized per-cell eligibility and timing-contract freeze required before final benchmarking |
| PERF-01D | **IN PROGRESS, PRELIMINARY DIAGNOSTICS**: 7 good fixed-vector trialwise comparisons, 3 matching invalid prefixes, 1 numerically concordant completed fit, 2 blocked fitting cells. No prospective independent gate |
| PERF-01E–H | **NOT EXECUTED**: no performance, statistics, throughput or GPU speedup numbers exist |

**Implication for the original nine primary CPU cells:** HGF standard 512/1024 forward and objective are invalid at the frozen starts; their fitting workflows are also ineligible. The strong **nine-cell aggregate “HGFX CPU faster than MATLAB” headline decision rule cannot currently PASS**. This is an outcome, not permission to silently replace the failed horizons, data, seeds or starts. A separately preregistered and independently reviewed additional stable workload may be proposed, *without replacing or hiding any of these recorded failures*. The existing 128 trial cells and eligible eHGF/uHGF cells may still support explicitly scoped speed claims **only after the relevant protocol and correctness gates are frozen and satisfied**.

## Next non-optional tasks

1. An independent reviewer audits complete raw vector/fit artifacts, MATLAB model resolution path, output-field mapping, frozen per-field tolerances and preserved invalid prefixes. Record verdict and exact reviewed commit, without retroactively rewriting diagnostic evidence.
2. Resolve the exact timeable API boundaries: MATLAB full `fitModel` vs HGFX full `fit_model`; JAX compiled and GPU batch paths remain a separate, explicitly different-optimizer comparison. Specify CPU affinity, thread controls and host/runtime versions.
3. Decide the predeclared eligibility/status of all nine primary CPU cells and full throughput grid, preserving blocked records. Document any proposed **new** prospective workload as a new protocol version, not a silent patch to this observed dataset.
4. Freeze `PERF-01C` with a reviewed source SHA, complete parameter/timing/data manifest and acceptance map **before any final timing**. Do not modify frozen historical `hgfx-paper-protocol-1` in place.
5. Only then execute real paired CPU timings, JAX compilation/transfer diagnostics and any genuine physical-GPU batch tests. Raw failures and failed runs must remain visible.

**Conclusion: MATLAB-vs-HGFX performance remains `NOT TESTED`. No scientifically validated speedup exists.**

## 2026-11-04 addendum: whole-cohort fixed-vector source review

This additional test **extends the scientific diagnostic denominator only**, without modifying or replacing the preceding 10 trialwise, 3 fitting, or frozen-horizon evidence. Same-job reference/HGFX cohort probe [41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774) returned:

| Model | Trials | Subject pairs with concordant finite fixed-vector objective | Both reject at frozen start | Total |
|---|---:|---:|---:|---:|
| HGF | 128 | 64 | 0 | 64 |
| HGF | 512 | 0 | 64 | 64 |
| HGF | 1024 | 0 | 64 | 64 |
| eHGF | 128 / 512 / 1024 | 64 per horizon | 0 | 192 |
| uHGF | 128 / 512 / 1024 | 64 per horizon | 0 | 192 |
| **Total** | | **448** | **128** | **576** |

All 576 comparisons used the *existing* SHA-256-verified `inputs/` arrays and resolved `configs/` start vectors. The largest recorded absolute fixed-vector negative-log-joint difference was `1.6370904631912708e-11` (uHGF, 1024 trials, zero-based subject index 21). Both reject cases were matching `tapas:hgf:VarApproxInvalid`-family reference/implementation behaviors; this **does not** grant a new scientific `REFERENCE_LIMITATION_MATCH` verdict. The source and prior/variance checks passed for all declared pairs.

The first attempt [41859496548](https://github.com/ahmadkhanloo/hgfx/actions/runs/41859496548) completed the numerical audit and retained its artifacts but could not push the report because the PR branch advanced. The same unmodified input data and comparison rules were rerun under a rebase-aware archiver [41860187774](https://github.com/ahmadkhanloo/hgfx/actions/runs/41860187774), which passed. Both workflow histories are preserved.

**Not demonstrated:** parity of *all trialwise* trajectories across 64 subjects, fitted parameters for 16 or 64 subjects, scientific identifiability, CPU speed, GPU speed or a nine-cell benchmark headline. All 28 original preregistered cases are accounted for by [the generated eligibility candidate](../../benchmarks/runtime_v1/eligibility_candidates/trialwise41854644533_fit41855647245_cohort41860187774.json) with 16 review-pending and 12 blocked. See [PERF01C timed-boundary audit](PERF01C_TIMED_BOUNDARY_AUDIT_2026-11-04.md) and independent review issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88). PERF-01C remains **NOT FROZEN** and speed is **NOT MEASURED**.
