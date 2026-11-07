# PERF-01D — source-locked, archive-only real MATLAB direct-call chronology vs original BFGS paths (2026-11-07)

**AUTHOR-SIDE ARCHIVE ARITHMETIC AND SOURCE-CALL CHRONOLOGY: PASS. ORIGINAL PUBLIC SCIENTIFIC FITTING: 63/64 NONPASS. INDEPENDENT REVIEW #88: NOT RECEIVED. PERF-01C: NOT FROZEN. NO SPEEDUP, PAPER TIMING, OR PHYSICAL GPU VALIDATION.**

## Original immutable evidence and prespec

This analysis was declared **before extracting new chronological comparisons** by [prespec](PERF01D_MATLAB_DIRECT_CALL_CHRONOLOGY_PRESPEC_2026-11-07.md), commit `3daa0a13004ed445c0c3fdd8bd2cae15428820b2`. It is **post-result selected** from previously observed original failed subject 7 and does not constitute a new scientific parity acceptance gate. No fresh MATLAB or HGFX fitting, no source edits, no changed data, no changed seed, no scientific threshold change or workload exclusions were introduced.

Only two original real source archives are compared:

1. *Actual MATLAB-owned* frozen private objective callstream and **same-run native MATLAB history** in [actual source run 42380372791](https://github.com/ahmadkhanloo/hgfx/actions/runs/42380372791), tested code SHA `6b79b7a9c0e78777eae8994cb7312ec43a8a6f5d`; actual raw direct calls `321393efe9aaf00c0fc96752de66fa27b4e9eebbc1b7f93ea485528ee59da2e9`, original derived source-call replay `1bdaa8c7a5db9c27bef65691e2a988ab6172554f8bc22af1089fdeb22014a802`, raw MATLAB native-vs-wrapper public fields and `optim.iter` MAT `5b0b0006e36d3fe5391d89a1a7121239e20a8425cd14e6b7032b1887ec929dae` (all SHA-256).
2. Original *separate-run* HGFX-owned and MATLAB-owned real public optimizer state in [run 42187240378](https://github.com/ahmadkhanloo/hgfx/actions/runs/42187240378), `hgfx_raw.json` SHA `060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce`, `matlab_raw.json` SHA `4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a`.

Both archives contain frozen HGFX 1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`, same original data/config/member SHA identities, zero-based subject 7/128 trials, unchanged `hgf_binary` / `unitsq_sgm`, start and original Ridders/BFGS. The actual original source `core/quasinewton_optim.m` is SHA-locked; its file bytes SHA-256 are `017e766ffed61c17be26bb4f2af820fe0186ee91bc0b643fc119b81b4f788c7e`.

The original 64 public full fit source [41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006) remains **63/64 SCIENTIFIC NONPASS** because the original zero-based subject 7 exceeds unchanged fitting tolerances at **4 `traj.mu` + 4 `traj.muhat`** values. Prior 15/16 NONPASS and all original 28 benchmark cells stay unchanged.

## Recorded engineering executions

- [run **42384775670**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42384775670), code SHA `c03407c7e80187f63e66b1ea8e6e19f161d60a75`: **SUCCESS**, 13/13 source integrity/chronology tests, all historical member SHA-256 checks, archive-only 25-call chronological replay. The first result showed a **single nonsequential direct call/history mismatch at zero-based row 23**, while total exact chronological pair matches were 24/25. No actual private `if` events were inferred.
- Reporting refinement [`ceff5e16883c1c185d87dbe03a6bb6a93aeba275`](https://github.com/ahmadkhanloo/hgfx/commit/ceff5e16883c1c185d87dbe03a6bb6a93aeba275) adds explicit exact terminal mismatch indices and separately checks archived original MATLAB objective **value** bits, not only free-parameter vector bits; [run **42384922459**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42384922459) **SUCCESS**.
- Two added negative controls for terminal overwrite handling and same-coordinate historical objective drift [`5de511b916d7d3785986863fd834c91e72f51ca0`](https://github.com/ahmadkhanloo/hgfx/commit/5de511b916d7d3785986863fd834c91e72f51ca0). Latest [**archive-only run 42384940474**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42384940474) at exact SHA `5de511b916d7d3785986863fd834c91e72f51ca0`: **SUCCESS**; **15/15** controls; SHA-verified three original MATLAB trace members, two original BFGS raw members, original full 63/64 scientific NONPASS; independent source-line replay and exact chronological arithmetic. No failed run in this new chronology series; separate earlier PR #92 instrumented-MATLAB engineering failures are preserved and not rewritten.
- [Latest evidence artifact **13578408543**](https://github.com/ahmadkhanloo/hgfx/actions/runs/42384940474/artifacts/13578408543); GitHub ZIP SHA-256 `d9373264c0f039beb13af5abdaa378cc7a8370f063abbc004d8ed0d23b35c677`; new derived member `matlab-direct-chronology-and-original-owned-paths.json` SHA-256 `d0f4eda571371abfa80679dbe19e27d1a135ab7c818f04554b04c00cbb0bc923`. Original source artifact ZIP and member SHAs remain unchanged.

## Actual chronological findings — distinguish callstream from accepted steps

| Archived quantity (zero-based indexing) | Recomputed result |
|---|---:|
| Real MATLAB-owned direct initial objective calls | 1 |
| Real MATLAB-owned direct line-search objective trial calls | 24 |
| Direct reset calls | 0 |
| Distinct **exact binary64** line-search trial vectors | **24 / 24** |
| One initial plus 24 direct calls compared strictly to same-run native MATLAB record at the same index | **24 / 25 exact** |
| **First and sole** chronological mismatch | direct call / native record **23** |
| Penultimate direct trial `direct[23]` equals native `history[23]` at exact vector and objective bits | **FALSE** |
| Last direct trial `direct[24]` equals native `history[24]` | **TRUE** |
| Last two saved native MATLAB history entries, `history[23]` and `history[24]`, duplicates at exact vector **and** scalar objective bits | **TRUE** |
| Actual new-dispatch MATLAB native 25 free vectors vs original separate-dispatch MATLAB-owned public fitting history | **25 / 25 bitwise identical** |
| Actual new-dispatch MATLAB native 25 scalar history objectives vs original separate-dispatch MATLAB-owned history | **25 / 25 bitwise identical** |
| First nonzero **free-vector** bit difference between this actual MATLAB history and original separate-run HGFX-own history | record **1** |
| Largest same-record MATLAB-owned versus original HGFX-owned component absolute free-vector difference | `3.7255962581639324e-07` |
| Original scientific full-cohort fitting | **63 / 64 NONPASS** |

The exact evidence illustrates why *membership* and *chronological one-to-one mapping* must not be conflated. A previous author-side report showed that each of the **24 noninitial saved MATLAB history records** had at least one matching original source-direct candidate among the 24 calls. The stricter chronological analysis finds **one mismatch at record 23**: the source direct candidate sequence still contains its distinct penultimate trial, but that candidate is not the same value as the penultimate **stored** `iter` record; the following candidate matches the last record, and the last two **stored** records are duplicates. This is consistent with (not a substitute for direct source branch logging of) original MATLAB optimizer's terminal history overwrite behavior.

Because exact source callsite identity means an objective evaluation rather than an explicit conditional branch event, **do not assert 24 distinct accepted BFGS transitions**. Even an all-exact source history would not independently expose the internal values of `j`, Armijo condition, BFGS curvature test or optimizer termination reason. The direct-call sequence instead supports the narrower fact that 24 distinct candidate vectors were evaluated in this original MATLAB-owned path, with 0 direct source reset evaluations.

The actual new-run MATLAB history also reproduces **the original earlier archived MATLAB free vectors and scalar objective bits** exactly at all 25 finite records, without asserting cross-host reproducibility in general. It differs from the archived HGFX-owned 25-record path at record 1 already and grows to a max difference `3.7255962581639324e-07`. These are **different OWN-optimizer-path coordinates**, not same-vector MATLAB-vs-HGFX function discrepancies and not evidence of a particular incorrect mathematical model or objective. Prior same-parameter true private MATLAB objective/gradient probes and the exact original 63/64 fitting failure remain independently archived.

## Scientific boundary and next review

**Supported:** original source-call chronology, actual 24 distinct original MATLAB-owned trial candidates, strict same-run objective/history mapping with explicit terminal mismatch, old-versus-new MATLAB-owned 25 vector/value bitwise reoccurrence, first HGFX-owned divergence at record 1, and complete untouched original 63/64 fitting failure.

**Not supported:** direct original HGFX private optimizer-callstream captured on this exact same runner, hidden reference Armijo/curvature/gradient-stop boolean events, definitive causal explanation for 4+4 public trajectory failures, approved reference-limitation classification, equivalence of 64/64 fits, eligible prospective 28-case workload performance protocol, CPU speedup or physical GPU validation.

A separately identified **independent scientific reviewer** still needs to audit frozen source-line chronology, the terminal overwrite interpretation, original 28 benchmark-case eligibility, model family/priors/ends, actual MATLAB- versus HGFX-owned state comparisons, cross-host caveat #90 and the original nonpass #89. Issue [#88](https://github.com/ahmadkhanloo/hgfx/issues/88) remains **BLOCK_FREEZE pending a reviewer signature**, not `APPROVE_PROSPECTIVE_FREEZE`. PERF-01C **NOT FROZEN**, PERF-01E–H **NOT RUN**. All original acceptance thresholds and failed experiments are preserved.
