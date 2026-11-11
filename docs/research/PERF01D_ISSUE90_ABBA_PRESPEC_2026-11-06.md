# PERF-01D / Issue #90 — predeclared same-runner ABBA numerical-repeatability control (2026-11-06)

**PROSPECTIVE AUTHOR-SIDE ENGINEERING CONTROL — NOT EXECUTED AT PROTOCOL AUTHORING.** This is not a scientific PASS, a new benchmark performance protocol, a new paper speed claim or an external review. PR #87; original scientific mismatch #89; external review #88; numerical portability #90.

## Original immutable scope

Frozen HGFX v1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; HGF Toolbox 8.2.0 MATLAB `2437f4dc241541072722a2695ddeca7b44d83dd3`. Original 64 subjects × 128 trials from run 41863441006, unchanged `hgf_binary + unitsq_sgm`, zero-based subject 7, exact original inputs, priors, optimizer, transformed start, fixed/free mask, source `nRandInit=0`. Original result **63/64 NON-PASS**, subject 7 has four failed `traj.mu` and four `traj.muhat` coordinates. All 28 original numeric fields retain their preexisting acceptance thresholds.

The source/summary raw SHA-256 from run 41863441006 must be verified BEFORE every fit. Existing report from [run 42203036203](https://github.com/ahmadkhanloo/hgfx/actions/runs/42203036203) showed auto-versus-Haswell complete fitted trajectory differences on one runner, but did not test within-mode repeatability on an explicit common CPU affinity. Later two independent source-native fit jobs varied slightly across runners; the cause is not uniquely attributable to hardware or BLAS from those cross-run records.

## New single-runner four-process design

Predeclared fixed order **A1–B1–B2–A2**, where A = OpenBLAS auto (must resolve to SkylakeX) and B = `OPENBLAS_CORETYPE=Haswell`. Each is a separate *untimed* Python process on a **single GitHub ubuntu-24.04 runner** with the same first four available logical CPU IDs captured before any fitting; `taskset` enforces the same four-core affinity for all four fits. If fewer than four CPUs are allowed, FAIL; never silently change the CPU set.

Pinned runtime: Python 3.11, `numpy==2.3.5`, OpenBLAS 0.3.30, `OPENBLAS_NUM_THREADS=4`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `JAX_PLATFORMS=cpu`. Verify effective BLAS dispatcher, thread count, CPU affinity, CPU identity and run ID **per process**; fail closed if the environment is not as declared. Identical original subject/model/config/start/iteration inventory are required. No seed, dataset, threshold, optimizer, model or version change is permitted.

Predetermined contrasts are two same-dispatch repeats (A1↔A2; B1↔B2), four cross-dispatch pairs (A1↔B1; A2↔B2; A1↔B2; A2↔B1), and every new fit against each immutable archived MATLAB/HGFX original fit. Report **all** original 28 fitting/trialwise fields using the original source tolerances AND separate strict serialized binary64 comparisons for the six new-new pairs; do not choose a favorable pair after observing results.

Each raw fit and the independently captured environment gets a separate record, SHA-256, complete derived 28-field comparison, original-failure checksum, workflow run ID and code SHA. A green engineering CI verdict means only that this bounded replay/analysis executed correctly; it **does not** mean bitwise reproducibility or scientific equality was obtained. A failed run, changed effective dispatcher, missing original raw evidence or divergent source path remains a visible failure.

## Scientific interpretation / release gates

This experiment can distinguish *observed within-mode numerical variability* from *observed between-mode variation* on one constrained runner. With two runs per mode it **cannot** establish universal reproducibility, uniquely isolate CPU/BLAS root cause, declare the archived MATLAB scientific limitation, or convert `63/64` to `64/64`. Comparing the new HGFX fits to old MATLAB remains cross-run; it is not a matched-host MATLAB control. CPU affinity and BLAS thread constraints are *diagnostic controls*, not rewritten historical conditions.

PERF-01C remains **OPEN / NOT FROZEN** until an identifiable independent reviewer signs #88 with exact source/evidence hashes and protocol acceptance. The existing 28 prospective workload cells remain 16 review-pending / 12 blocked, and six of original nine primary CPU cells remain ineligible. PERF-01E–H remain NOT RUN. **No MATLAB-vs-HGFX speedup or paper performance claim.**

Implementation: `benchmarks/runtime_v1/compare_subject7_same_host_repeatability.py`, `tests/test_perf01_subject7_same_host_repeatability.py`, `.github/workflows/perf01-subject7-same-host-abba.yml`. Result/evidence documentation must be updated separately **after** actual execution, preserving the original run and any failures.
