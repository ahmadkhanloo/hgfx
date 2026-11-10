# REV-2.4 Panel G — single original-oracle execution kickoff (2026-11-10)

**Authority:** author requested project continuation on 2026-11-10; current D1=A / Computational Statistics remains in force.
**Task:** REV-2.4 / C1, original preregistered protocol `compstat-rev2-4-objective-cross-eval-v1` committed at `d1986311b8a5ff97f088ebac35c612e16cbe89db` **before** this kickoff.
**Panel:** G only, 200 original transformed free-vector draws each for `hgf_binary`, `ehgf_binary`, `uhgf_binary`; one complete 600-vector paired MATLAB/HGFX objective evaluation.
**Frozen software:** MATLAB HGF Toolbox 8.2.0 commit `2437f4dc241541072722a2695ddeca7b44d83dd3`, released HGFX 1.0.0 commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, PyPI Wheel SHA-256 `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`.
**Execution scope:** the existing `.github/workflows/compstat-rev24-original-oracle.yml` records original output and uploads raw artifacts, with a predeclared `NOT_GLOBAL_PASS` classification; it must not infer acceptance from job success. All nonfinite outcomes and exceptions stay in the 600-case denominator.
**Historical outcomes:** REV-1.4 DOCUMENTED_LIMITATION, M18 recovery FAIL, P3 FAIL, original 63/64 NONPASS and PERF-01C BLOCK_FREEZE remain unchanged.
**Panel E:** D02/D08/64 endpoint cross-evaluation remains separate; D02 missing original HGFX full endpoint is not replaced.
**Run policy:** one scientific attempt; at most one rerun exclusively for a documented infrastructure failure as authorized by the original frozen protocol. Never alter thresholds, seeds, model families, endpoints or datasets to obtain PASS. Record exact Actions run/artifact IDs, runtime, hashes and failures in the revision ledger before D2.
