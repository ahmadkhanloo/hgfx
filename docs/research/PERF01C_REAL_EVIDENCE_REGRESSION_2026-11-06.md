# PERF-01C: archived raw-evidence regression (2026-11-06)

**State: ENGINEERING REPLAY SUCCESS; INDEPENDENT SCIENTIFIC REVIEW NOT DONE; NOT FROZEN; NOT TIMED.**

Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [review issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [program #86](https://github.com/ahmadkhanloo/hgfx/issues/86).

## Exact executed revision and CI evidence

- Source commit evaluated: **98619cfab16851883747226c2b4a1f99297d88bd**; base main before review: **44353387ab2578339174f0d8252aecb737654ae7**.
- Script introduced by **a05a4c5ac886c97975e2d1c2ccf66d1733adc1ec**: benchmarks/runtime_v1/verify_evidence_regression.py.
- Workflow: .github/workflows/perf01-evidence-regression.yml.
- [GitHub Actions run 42106901417](https://github.com/ahmadkhanloo/hgfx/actions/runs/42106901417): **SUCCESS**, job ID **127523981293**.
- GitHub-hosted ubuntu-24.04; Python 3.11.18; NumPy 2.3.5. No fresh MATLAB/HGFX execution, benchmark timers, physical GPU, or second-host scientific replication.
- Existing regression suite: **39/39 unit tests passed**.
- Produced artifact: [perf01-evidence-regression-42106901417](https://github.com/ahmadkhanloo/hgfx/actions/runs/42106901417/artifacts/13452871020); ID 13452871020, containing regression_result.json.

## Recomputed original raw artifacts (verified by real file SHA-256)

Each of the four original workflow artifacts was downloaded under its original run ID, both original raw exports were hash-verified against the archival summary, and the existing comparator was actually rerun. The entire recalculated scientific diagnostic result exactly matched the original saved result except for archival run-location/hash metadata.

| Original run / evidence | Raw HGFX SHA-256 | Raw MATLAB SHA-256 | Result |
|---|---|---|---|
| 41854644533 trialwise | 482029ec9b1410560c5f9ee8fc25c6282546f0521e7f3ec4667226768b80cf7e | 0fd002c79a776c8f5a6a8f713440abd5898bf9629db6e09540fe329e3e5a86f4 | MATCH |
| 41855647245 fit | 5fedcec3eebe6515b5be6bee983a7ee9c21929422b7c9c2db0fe0694b7e53e04 | 6aa0c5f03d1d0cced124090a04316656bdb2fadcb93d43055c58c414a306fd4a | MATCH |
| 41860187774 cohort | 4ac081900860d7db0f2b2f001a7cf19fb22d9c6c5dc30b6dd7ff821bfd53209f | cafe8c269dea419c3f75c1fc4134be07352afa30393e358000dbed3a793ac417 | MATCH |
| 41863441006 cohort fit | 6c9a2598e12e0340a62d871011e8fd7652ec2d975d2c03395a37854052043abb | 2ea074f97fd470149d0d871e06ed42bf8c2ab604ee38f340a3b18e6b4f81cd98 | MATCH, historical scientific failure retained |

Frozen sources: HGFX v1.0.0 **4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27**; MATLAB HGF 8.2.0 **2437f4dc241541072722a2695ddeca7b44d83dd3**.

SHA-256: canonical input manifest **37390df7133ac3d7bc2389fefb03aaf9230597e325a6f6d7eb40c429d4621dbe**; resolved configuration manifest **2515f48cea886f0d9446532544cb163adbebc716eb65f8771803f3f14522ba21**. All referenced dataset/configuration bytes were checked.

## Preserved scientific outcome

- Trialwise comparison: **7/10** compatible diagnostic cells, **3/10** invalid paths, first-invalid-prefix lengths **348, 346, 349**.
- Fixed-vector comparison: **576** records, **448** matched valid objectives and **128** invalid in both implementations. This is not evidence for 576 successful full fits.
- 64-subject complete fitting: **63/64** inside original tolerances, **1/64** scientific mismatch at zero-based subject **7** (trajectory mu and muhat). Nested outcomes: **1/1, 15/16, 63/64**. This remains a scientific non-PASS.
- Both historical and derived 28-case ledgers reproduced exactly: **16** diagnostic-concordant/review-pending, **12** blocked (8 invalid input workloads; 2 divergent start/restart fitting workflows; 2 multi-subject fitting numerical mismatches). **Six of nine** original primary CPU cells remain ineligible.
- The candidate classification is author-side only. No acceptance thresholds, seeds, starts, denominator, frozen data, historical evidence or protocol were changed.

## Remaining gate

The result is reproducibility of archived raw exported evidence, **not** a new independent execution of MATLAB, external scientific sign-off, optimizer equivalence, CPU-thread/affinity validation, or speed performance proof. Issue #88 must separately adjudicate model/source oracle paths, raw scientific validity, subject-7 MATLAB sensitivity, fitting/measurement boundaries, CPU matching and any prospective v2 lock.

**PERF-01C = OPEN / BLOCKED_PENDING_INDEPENDENT_REVIEW; PERF-01E-H = NOT RUN; NO SPEEDUP CLAIM.**
