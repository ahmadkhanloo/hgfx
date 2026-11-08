# PERF-01C: proposed seven-forward call-only CPU boundary (untimed candidate)

Prepared: 2026-11-08. **IMPLEMENTED, PAIRED CI NOT YET ADJUDICATED** at initial commit. Parent: [PR #101](https://github.com/ahmadkhanloo/hgfx/pull/101) with [real untimed full-output 7/7 reference diagnostic 42479888100](https://github.com/ahmadkhanloo/hgfx/actions/runs/42479888100). Review [PR #100](https://github.com/ahmadkhanloo/hgfx/pull/100) recorded owner-published `BLOCK_FREEZE`, **not an independent external signoff**; [Issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88) remains `BLOCK_FREEZE / NOT FROZEN`.

## Exact candidate computation boundary — no timer exists in this change

**Frozen original scientific sources:** HGFX `1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` (NumPy binary64 forward, synchronous eager outputs) and genuine MATLAB HGF 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3` running MATLAB R2026a. Source version, resolved model/path, original subject-zero inputs, transformed parameter starts and configurations are unchanged. Both engines return all **11 perceptual trajectory fields** and `N×3×4` inference states. No response probability, observation likelihood, objective composition, fit, optimizer, warmup, timer, CPU benchmark or GPU work is performed.

A prospective CPU **compute-only** region is defined by the following one-call functions, separately in each runtime:

- Python: `forward7_boundary_hgfx_untimed.forward_only_call(model, inputs, parameters)` executes `FORWARD[model](inputs,parameters, transformed=True, ignored_trials=())`.
- MATLAB: `forward7_boundary_matlab_untimed.forward_only_call(model,r,p)` executes `feval(model,r,p,'trans')`, using the recorded active frozen `which(model)` path under the specified original toolbox.

**Outside** the future candidate compute-only region: loading JSON, verifying full original 28-case/9-config manifests, Python/MATLAB configuration object construction, input array and parameter allocation, start/prior and input-hash checks. **After** the call and outside the proposed region: assert all eleven trajectory fields and full state array shapes, materialize/serialize the entire outputs into JSON, recompute comparisons and save archives. Nothing is permitted to turn these full outputs into a scalar proxy. No compiler startup/JIT optimization is involved in this frozen NumPy forward family. A future reviewer must confirm whether including/excluding post-call materialization is operationally symmetric before approving a timer (the present wrappers have **zero clocks**).

The all-seven candidate set is exactly `primary_forward_128` and eHGF/uHGF forward 128/512/1024. It is **not** a new declaration that the other 21 original rows are eligible or dropped. Historical original 28 remain **16 REVIEW_PENDING / 12 BLOCKED** (6/9 original primary CPU blocked); original 64 whole-fit remains **63/64 SCIENTIFIC NONPASS** (subject index 7, 4 `traj.mu` and 4 `traj.muhat` old-tolerance failures).

## Source files / validation layers

- `benchmarks/runtime_v1/forward7_boundary_hgfx_untimed.py`
- `benchmarks/runtime_v1/matlab/forward7_boundary_matlab_untimed.m`
- `benchmarks/runtime_v1/compare_forward7_boundary_untimed.py`
- `tests/test_perf01_forward7_boundary_untimed.py`
- `.github/workflows/perf01-forward7-boundary-untimed.yml`

The comparator rejects mismatch of region ID, missing or asymmetric pre/post boundary declarations, any claimed clock, changed model/input/config bytes, missing/duplicate original case IDs, wrong axes or incomplete outputs, and old-frozen-tolerance differences. It **delegates actual numerical comparison unchanged** to the existing author-side `compare_forward7_untimed.py`. A positive result is `UNFROZEN_FORWARD_DIAGNOSTIC_CONCORDANCE`, never an eligible time/whole-fit scientific PASS. The workflow installs and verifies both exact frozen checkouts, runs the old and new negative-control tests, once executes genuine MATLAB/HGFX full-output call boundaries without time instrumentation, and preserves JSON artifacts regardless of success.

## Remaining genuine freeze gates (still BLOCKED)

1. Review exact run SHA, full raw output and MATLAB actual resolved source path; download/re-hash complete raw ZIP and member bytes with independent authentication. Check a genuine original-matrix raw archive replay, not solely tracked derived JSON or artifact metadata.
2. Have a scientifically independent reviewer judge exact same-workload numerical eligibility and existing Level-2/optimizer semantics separately (do **not** reclassify 63/64).
3. Specify real *same physical CPU* model/ISA and process/affinity/BLAS/NumPy/MATLAB threads, active dispatch, OS versions and power/contention controls. MATLAB and Python sharing a GitHub Actions job does **not** alone establish the prospective timer hardware/thread policy.
4. Obtain reviewer approval of pre/post-materialization policy, actual timer implementation (still **NOT IMPLEMENTED**), ten paired ABBA/BAAB blocks, three **untimed** warmups, original `20261104` order/bootstrap seed, 10,000-resample 95% paired CI and preserved `1.10×` threshold, retries and failure accounting. Version and lock the full accepted restricted protocol **before** measured benchmark execution.
5. Do not claim paper speedup or GPU validation. The original nine-case primary aggregate stays ineligible even if the seven forward-only diagnostics match.

Current: `PERF-01C BLOCK_FREEZE / NOT FROZEN`, no scientific-performance PASS. Preserve all failed experiments, original source hashes, and history.
