# PERF-01C / PERF-01D: six-source archived scientific-evidence replay, 2026-11-06

**Engineering result: SUCCESS. Scientific decision: OPEN / NOT FROZEN / NO PERFORMANCE TIMING.**

This is an author-side evidence-reproducibility expansion of [the original four-source regression](PERF01C_REAL_EVIDENCE_REGRESSION_2026-11-06.md), not an independent scientific review. Tracking: [PR #87](https://github.com/ahmadkhanloo/hgfx/pull/87), [PERF-01C #88](https://github.com/ahmadkhanloo/hgfx/issues/88), [fitting mismatch #89](https://github.com/ahmadkhanloo/hgfx/issues/89).

## Executed identity and run

- **Successfully tested candidate SHA:** 1dd22bc5eef4502136e6b61a586d2129be951a8d.
- **GitHub Actions run [42108194894](https://github.com/ahmadkhanloo/hgfx/actions/runs/42108194894): SUCCESS**.
- Environment: GitHub-hosted ubuntu-24.04, Python 3.11, NumPy 2.3.5 (no fresh MATLAB, HGFX, optimization or physical GPU execution).
- Regression tests: **47/47 passed**, including eight new negative/positive tests of original reference-only evidence. These tests deliberately fail on deleted/duplicated +/-eps probes, tampered fitted endpoints, mismatched reference starts, incorrect one-ULP step, falsified v1 tolerance labels, an unreproduced original baseline, or unjustified scientific PASS promotion.
- Script: benchmarks/runtime_v1/verify_evidence_regression.py; workflow: .github/workflows/perf01-evidence-regression.yml; tests: tests/test_perf01_evidence_followup.py.
- The dedicated CI archived a new unapproved regression_result.json artifact under the run. Its full raw SHA-256 ledger is generated from actually downloaded ZIPs, not from manually reconstructed text.

## Six archived input runs verified and recomputed

| Original run | Scientific scope | Actual verification |
|---|---|---|
| 41854644533 | Ten first-subject trialwise diagnostics | SHA-256 of HGFX and MATLAB raw, full comparator replay: MATCH |
| 41855647245 | Full first-subject fitting and default-start blockers | SHA-256 of HGFX and MATLAB raw, full comparator replay: MATCH |
| 41860187774 | 576 fixed-vector cases across model/horizon/subject | SHA-256 of HGFX and MATLAB raw, full comparator replay: MATCH |
| 41863441006 | All 64 exact-original complete public fits | SHA-256 of HGFX and MATLAB raw, full comparator replay: MATCH, failure preserved |
| 41868723514 | Subject-7 replay at each of two archived optimizer fitted endpoints | SHA-256 of HGFX and MATLAB raw, full 15-field comparator replay: MATCH |
| 41870479069 | MATLAB frozen-reference baseline and six +/-eps probes | SHA-256 of original MATLAB raw JSON, exact summary reconstruction, independently recomputed probe magnitude/status: MATCH |

Total **eleven original raw JSON evidence files** have verified SHA-256. The original 28-case and derived 28-case inventories were reconstructed without changing cases, acceptance thresholds or historical bytes.

### Narrow subject-7 finding

- The original 128-trial full-fit result remains **63/64**, with zero-based subject index **7** out of tolerance in traj.mu and traj.muhat. The 16- and 64-subject fitting cells remain **scientifically BLOCKED**.
- For each of **both** original recorded fitted vectors, the full 15-field trialwise MATLAB/HGFX same-vector evaluation reconstructs the archived diagnostic concordance. Comparing two different optimizer endpoints is not itself a same-vector inference bug.
- The MATLAB source-only reference sensitivity raw export reproduces the **exact original MATLAB baseline fitted endpoint** and original joint objective.
- All six (three free coordinate x +/-eps) perturbations were retained. The verifier recomputed actual step sizes using math.ulp(original_start) and recomputed failures using the **unchanged** FIT_TOLS["final"] from compare_fits.py (atol=3e-10, rtol=3e-8); it does not trust the raw status flags alone.
- Exactly the original free coordinate **2**, negative step, shows an out-of-tolerance fitted endpoint shift: **7.640946009246363e-7**. The five other original perturbations remain within the old final-parameter gate.

The source-only MATLAB result supports an **optimizer endpoint/basin-sensitivity hypothesis in this exact regime**, not independent evidence of full workflow parity or scientifically acceptable reference limitation. No change was made to frozen starts, subjects, random seeds, original reference source, source model family, historical failures or v1 tolerances.

## Disposition and unresolved independent gate

**PERF-01C: OPEN / BLOCKED_PENDING_INDEPENDENT_REVIEW. PERF-01D: DIAGNOSTIC SUBJECT-7 FIT MISMATCH UNRESOLVED. PERF-01E-H: NOT RUN.**

An independent reviewer must still inspect scientific source mappings and real runtime boundaries, verify optimizer convergence/termination, decide whether this exact sensitivity permits any restricted reference-limitation classification under docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md, and approve or block a prospective v2 protocol lock. Machine archive reproducibility and CI success do not constitute that reviewer disposition. No CPU/GPU speedup or paper-use benchmark is authorized.
