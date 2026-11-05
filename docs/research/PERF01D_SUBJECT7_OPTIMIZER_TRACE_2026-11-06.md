# PERF-01D — original subject-7 optimizer path forensic evidence (2026-11-06)

**Status: AUTHOR-SIDE SCIENTIFIC DIAGNOSTIC / NO INDEPENDENT DISPOSITION / NO PERFORMANCE TIMING.**

Linked gates: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [PERF-01C #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [subject-7 #89](https://github.com/ahmadkhanloo/hgfx/issues/89).

## What was learned from frozen source, before the new run

In exact MATLAB HGF Toolbox 8.2.0 source SHA 2437f4dc241541072722a2695ddeca7b44d83dd3, core/quasinewton_optim.m allocates `iter.x = NaN(maxIter+1,...)` and `iter.val = NaN(maxIter+1,1)` when `optIter` is enabled. Its convergence branches write the last state back into index `i` as well. Frozen HGFX 1.0.0 source SHA 4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27, src/hgfx/optim/compat_quasinewton.py, preserves this history bookkeeping.

The prior cohort-fitting evidence reported **101 saved history entries** on both sides; 101 is the **preallocated length**, **not proof of 100 actual optimization iterations or identical optimizer termination**. This was a genuine evidentiary limitation of the earlier result, not a change to the numerical acceptance gate.

## New same-host, full public fitting experiment (no timers)

- [Original untimed paired execution: GitHub Actions 42115887599](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599), **SUCCESS**. Exact runner source SHA: `b378fef6ff93f6efa041f4e8304dafba742ae4ab`, GitHub-hosted ubuntu-24.04, Python 3.11 / NumPy 2.3.5, MATLAB R2026a. Exact MATLAB reference and HGFX 1.0.0 source SHA enforced at checkout.
- Only the unchanged **128-trial original subject index 7**, public `fitModel` and `fit_model`, `hgf_binary` + `unitsq_sgm`, original start and `quasinewton_optim_config` were used. The original 64-subject run **41863441006** remained untouched and was checked via its raw file SHA-256 before re-execution.
- [Raw trace artifact 13457295710](https://github.com/ahmadkhanloo/hgfx/actions/runs/42115887599/artifacts/13457295710) includes `hgfx_raw.json`, `matlab_raw.json`, `comparison.json` and `summary.json`.
- SHA-256 of exact original run's trace exports:
  - HGFX `hgfx_raw.json`: `6fe10be1dd1860612859e6efbe7bee13717e4787aed4a62f0e6b67a2072aac7a`.
  - MATLAB `matlab_raw.json`: `ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f`.
- The **fresh** MATLAB and HGFX fitted parameter vectors each remain within the inherited final-parameter diagnostic tolerance versus their own ORIGINAL 64-fit vectors, independently and separately.
- Each tool has **101 allocated history slots but only 25 finite, sequentially populated slots**; 76 trailing slots are NaN. Both have identical last two finite records **within their own trace**. This is evidence of matching history shapes/record populations, not a documented MATLAB termination reason.
- **Initial record:** identical parameter starting point and scalar objective.
- **First nonzero binary64 numerical difference:** record index **1** (zero-based), max free-vector delta `9.769962616701378e-15`; absolute scalar-objective delta `1.1368683772161603e-13`. This is a small numerical difference, **not** a scientific gate failure at that record.
- **First difference beyond the existing final-parameter numeric tolerance used as a diagnostic trace lens:** record index **14** (zero-based), maximum free-parameter delta `9.962832248078257e-8`, scalar objective delta `5.8638704558688914e-8` (the latter is within the same inherited tolerance). **That tolerance is established for FINAL fitting results, not independently authorized as a per-iteration acceptance threshold.** This is a localization finding only.
- Frozen MATLAB public `fitModel`/reference `quasinewton_optim` returned no machine-readable termination reason. The diagnostic explicitly marks it `NOT_EXPOSED_BY_UNMODIFIED_PUBLIC_FITMODEL`, and does not infer termination from buffer length, number of finite slots, or the duplicate last record.

## Independently reproducible derived analysis, no fresh optimization

[Derived replay GitHub Actions 42117014225](https://github.com/ahmadkhanloo/hgfx/actions/runs/42117014225), **SUCCESS** (11/11 tests) downloaded original exact trace bytes, checked both raw SHA-256 values, reran the comparator, checked all original result fields and created a **new separate** machine-readable ledger:

`benchmarks/runtime_v1/subject7_optimizer_trace_results/derived-42115887599.json`

Derived evidence commit: `7ae03eadd012bb8464abc28fafb8c23bec46ac1d`. The original raw outputs and summary were not rewritten. The initial derived workflow [42116861461](https://github.com/ahmadkhanloo/hgfx/actions/runs/42116861461) failed at JSON export because a NumPy Boolean was not cast to a native `bool`, an *engineering serialization issue*. The original paired scientific trace run succeeded; the derived script fix is preserved in Git history.

## Scientific interpretation and remaining open gate

This result **directly documents gradual MATLAB/HGFX optimizer trajectory drift from the same initial state**, with the first nonzero machine-level difference at record 1 and larger drift by record 14. It makes optimizer/numerical-path behavior a supported and specifically localized explanatory candidate for the original subject-7 fitted-trajectory mismatch. It does not independently prove a general reference numerical-basin limitation, full fitting equivalence, identical optimizer termination conditions or scientific identifiability. In particular, exact trace differences are not automatically a code implementation bug.

The original **63/64** complete-fit diagnostic and **15/16** nested diagnostic remain non-PASS; original **16 review pending / 12 blocked** case inventory and the invalid six original primary CPU cells remain unchanged.

An **independent reviewer** must still adjudicate whether the observed optimizer path and frozen MATLAB-only +/-eps sensitivity support any exact-regime `REFERENCE_LIMITATION_MATCH` under docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md, inspect termination behavior/source-level choices, and decide the prospective CPU method and runner freeze. **PERF-01C OPEN / NOT FROZEN, PERF-01E-H NOT EXECUTED, no CPU/GPU timing claim.**


## Repeat execution and retained engineering failures

A second full untimed MATLAB/HGFX public-fitting source trace, [Actions run 42117014238](https://github.com/ahmadkhanloo/hgfx/actions/runs/42117014238), **SUCCESS** at commit `b0bb316c9cf99a57bbd70a263ce07c8a9466efcd`, replicated the **25/25** finite-slot counts and first inherited-final-tolerance crossing at record **14**. The numerical maximum at that record was `9.985809334978057e-8` rather than `9.962832248078257e-8` in the first run. The original paired MATLAB trace raw SHA-256 remained **identical** (`ce4a96e6eb2aad48ee08c39f0361c0cebd5d2306b048b9674c96a45a4570a40f`), while the HGFX trace changed slightly (raw SHA-256 `1df0608f750a6fd1712bf4c4db3aae04ca62f06a7272c3800787150caad64f6c`). This is additional repeated-run numerical variability, not permission to ignore the original subject-7 failure or alter thresholds. Raw archive: [artifact 13455614093](https://github.com/ahmadkhanloo/hgfx/actions/runs/42117014238/artifacts/13455614093). The exact first-run source evidence and derived report are preserved unchanged.

The intermediate workflow runs [42116642560](https://github.com/ahmadkhanloo/hgfx/actions/runs/42116642560) and [42116678111](https://github.com/ahmadkhanloo/hgfx/actions/runs/42116678111) produced the MATLAB/HGFX fit traces but failed at **comparison JSON serialization** of a NumPy Boolean (`numpy.bool_`); the machine error is recorded in those run logs and was repaired by explicit conversion to Python `bool` in `b0bb316c9cf99a57bbd70a263ce07c8a9466efcd`. [Derived archival run 42116861461](https://github.com/ahmadkhanloo/hgfx/actions/runs/42116861461) failed for the same JSON type issue before the successful replay [42117014225](https://github.com/ahmadkhanloo/hgfx/actions/runs/42117014225). **These are engineering report failures, not corrected numerical results or silently discarded science.**
