# PERF-01C — independent review decision worksheet (UNSIGNED; no acceptance verdict)
Date prepared: 2026-11-08
Status: **AUTHOR-PREPARED REVIEW FORM ONLY — NO EXTERNAL REVIEW RECEIVED; NOT FROZEN; NOT TIMED**

**Purpose:** one reviewable decision surface for [issue #88](https://github.com/ahmadkhanloo/hgfx/issues/88), rather than further bitwise replays or redefining what counts as numerical equality. This worksheet is *not* an external review, a substitute for the source audit, or an approval. It preserves the original 28 cases and all historical failures.

## Exact candidate/evidence identity to verify independently

- Candidate branch under review: [draft PR #99](https://github.com/ahmadkhanloo/hgfx/pull/99), author-side source at creation: `ee05fa267ba9640ac97020e73f03ca7569171538` (this worksheet addition creates a later head; **reviewer MUST replace this with the exact checkout SHA actually examined**).
- Original tracked 28-case ledger: `benchmarks/runtime_v1/eligibility_candidates/candidate_v2_fullfit41863441006.json`, Git blob SHA `b4359bf2e862cc41b407ea132d124e3add8d9042`; its source evidence map: full-fit-derived `e499ce994efcaf32d33803eb1c563da47dfe72ecb523527e6ef68a1d77f9fcbc`, earlier 28-case candidate `45c86cac7bb26f643c9e74ba793a2160b6bb3c099eac1ff810555247c91e81e3`. Reviewer must independently SHA256-hash the actual tracked file and original raw artifacts, not rely on this text or a Git blob hash as a raw artifact digest.
- Original full 64-subject diagnostic: `benchmarks/runtime_v1/fit_cohort_results/summary-41863441006.json`, Git blob SHA `aa857e22ae7c3a2449bb1eab68e738fb3665fb97`; raw original paired [run 41863441006](https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006).
- Frozen HGFX `v1.0.0` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; MATLAB HGF Toolbox 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3`, actual MATLAB function resolution must be checked.
- Frozen numerical policy: `docs/validation/MATLAB_EQUIVALENCE_POLICY.md` (Git blob SHA `8ecf776b27e4fa2187271f8b33ae4b04759141ef`). **No universal bitwise requirement**; the original trajectory tolerance is `abs(HGFX−MATLAB) <= 3e-10 + 3e-8*abs(MATLAB)`; other fields retain their own family-specific thresholds. Exact model, data, starts, config, mask and source are required at Level 0.
- The original 64-fit result remains **63/64 SCIENTIFIC NONPASS**: subject zero-based **7**, `traj.mu` **4** and `traj.muhat` **4** values outside the *unchanged* bounds; max abs difference `1.5704625655477145e-9`. Historical [tolerance-margin run 42266125766](https://github.com/ahmadkhanloo/hgfx/actions/runs/42266125766): original failure is up to **1.66198×** the existing local bound. Other inference outputs, fitted final vector and Hessian/covariance/LME remain within their **respective original** diagnostic tolerances. This is a possible optimizer-endpoint sensitivity question, **not** 64/64 PASS.
- Last author-side release/analysis regression [run 42411459066](https://github.com/ahmadkhanloo/hgfx/actions/runs/42411459066) succeeded Ubuntu and Windows on `ee05fa267ba9640ac97020e73f03ca7569171538`; a green regression is **not** a scientific reviewer verdict.

## Original 28-case ledger — no case added, removed or prospectively declared eligible

For every row the **author-side state is immutable**; reviewer fills the last column **after** checking source/raw eligibility. `REVIEW_PENDING` is **not** `PASS`. A reviewer may decide a row remains blocked or give reasons for a separately locked *new-version* scoped claim, but **cannot erase a blocked row or change a historical source classification**.

| # | Original fixed case ID | Model / horizon / subjects | Author-side candidate status (historical) | Independent row-level decision + source reason |
|---:|---|---|---|---|
| 1 | `primary_forward_128` | hgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 2 | `primary_objective_128` | hgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 3 | `primary_fit_compat_full_128` | hgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 4 | `primary_forward_512` | hgf_binary / 512t × 1s | BLOCKED — invalid original workload | _unreviewed_ |
| 5 | `primary_objective_512` | hgf_binary / 512t × 1s | BLOCKED — invalid original workload | _unreviewed_ |
| 6 | `primary_fit_compat_full_512` | hgf_binary / 512t × 1s | BLOCKED — unmatched restart policy | _unreviewed_ |
| 7 | `primary_forward_1024` | hgf_binary / 1024t × 1s | BLOCKED — invalid original workload | _unreviewed_ |
| 8 | `primary_objective_1024` | hgf_binary / 1024t × 1s | BLOCKED — invalid original workload | _unreviewed_ |
| 9 | `primary_fit_compat_full_1024` | hgf_binary / 1024t × 1s | BLOCKED — unmatched restart policy | _unreviewed_ |
| 10 | `secondary_ehgf_binary_forward_128` | ehgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 11 | `secondary_ehgf_binary_objective_128` | ehgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 12 | `secondary_ehgf_binary_forward_512` | ehgf_binary / 512t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 13 | `secondary_ehgf_binary_objective_512` | ehgf_binary / 512t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 14 | `secondary_ehgf_binary_forward_1024` | ehgf_binary / 1024t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 15 | `secondary_ehgf_binary_objective_1024` | ehgf_binary / 1024t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 16 | `secondary_uhgf_binary_forward_128` | uhgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 17 | `secondary_uhgf_binary_objective_128` | uhgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 18 | `secondary_uhgf_binary_forward_512` | uhgf_binary / 512t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 19 | `secondary_uhgf_binary_objective_512` | uhgf_binary / 512t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 20 | `secondary_uhgf_binary_forward_1024` | uhgf_binary / 1024t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 21 | `secondary_uhgf_binary_objective_1024` | uhgf_binary / 1024t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 22 | `throughput_fit_1x128` | hgf_binary / 128t × 1s | REVIEW_PENDING — not approved | _unreviewed_ |
| 23 | `throughput_fit_16x128` | hgf_binary / 128t × 16s | BLOCKED — 63/64 fitted mismatch | _unreviewed_ |
| 24 | `throughput_fit_64x128` | hgf_binary / 128t × 64s | BLOCKED — 63/64 fitted mismatch | _unreviewed_ |
| 25 | `throughput_fit_1x512` | hgf_binary / 512t × 1s | BLOCKED — invalid original workload | _unreviewed_ |
| 26 | `throughput_fit_16x512` | hgf_binary / 512t × 16s | BLOCKED — invalid original workload | _unreviewed_ |
| 27 | `throughput_fit_64x512` | hgf_binary / 512t × 64s | BLOCKED — invalid original workload | _unreviewed_ |
| 28 | `robustness_masked_512` | hgf_binary / 512t × 1s | BLOCKED — invalid original workload | _unreviewed_ |

**Accounted original denominators:** 28 total = **16** diagnostic-concordant review-pending + **8** invalid original reference workloads + **2** incompatible fitting-start policies + **2** multisubject fitting numeric mismatch = **12 blocked**. Original **9 primary cells: only 3 review-pending, 6 blocked**; no nine-primary aggregate speedup permitted under frozen work. Full 64-person fit must not be relabeled based solely on small absolute error. Proposed `RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md` remains **draft**, not substitute for original failed 28-case contract.

## Five decisive review questions (bounded)

1. **Independent source and evidence identity:** Does a non-implementing reviewer confirm actual checked-out candidate commit, genuine original MATLAB/HGFX paths and exact model/workflow/config/data/hash identity? Does the reviewer confirm all **28** original rows and all **64** fits without excluding subject 7?
2. **Numerical science, not bitwise cosmetics:** At exact matched parameter endpoints, do archived same-vector trajectories/likelihoods pass the **already frozen** field-specific tolerance, and is subject-7 remaining 4+4 trajectory exceedance attributable to documented endpoint sensitivity without unresolved material optimizer-semantic differences? Existing `Level 2` cannot be announced PASS from post-hoc calibration alone; if unmet, retain blocked classification.
3. **Comparability:** For each proposed timing cell, is the scientific work and result materialization *actually* the same? Treat MATLAB implicit unstable-start resampling, private `negLogJoint`, MATLAB stdout versus HGFX no stdout, and different JAX BFGS/GPU optimizer as explicit candidate blockers; no proxy forward/objective comparison as full fit.
4. **Host/clock/statistics:** Is a **specific** prospective same-physical-CPU runner, threading/affinity/BLAS/MATLAB runtime, output/stdout policy, start/cold/warm separation, paired ABBA/BAAB order, 3 warmups, 10 blocks×2 samples, confidence intervals and all failure accounting defined, machine-checkable and prelocked? A shared runner without stable affinity metadata may be insufficient for paper claims.
5. **Gate outcome:** Is *a concrete, versioned scoped protocol* safe to freeze **before** any paper-use timing? If not, provide `BLOCK_FREEZE` and the **minimal** missing evidence/runner/contract fixes (not new bitwise-only experiments). Any approved scope must retain all 28 original rows and explicit exclusions.

## Required independent attestation — leave unsigned until actual external review

- Reviewer (identity / organization / independence from PERF-01 implementation): **NOT PROVIDED**
- Reviewed checkout full commit SHA and base SHA: **NOT REVIEWED**
- Source raw artifact IDs and SHA-256 digests *verified by reviewer*: **NONE**
- Verified original 28-case case IDs / 64 full fits and signed reviewer field mapping: **NOT VERIFIED**
- Material issues and severity, exact path/line and decision conditions: **NOT PROVIDED**
- Prospectively frozen new protocol version / original full 28-cell matrix accountability: **NONE**
- Exact proposed verdict, choose one **only after evidence review:** `APPROVE_PROSPECTIVE_FREEZE` / `BLOCK_FREEZE` — **NOT ISSUED**
- Reviewer signature and date: **UNSIGNED**

**Current operational status, not a reviewer verdict:** `BLOCKED_PENDING_EXTERNAL_REVIEW`. PERF-01C **OPEN**, original scientific fit **63/64 NONPASS**, original nine-primary headline ineligible, new scoped paper performance **NOT TIMED**, new PERF-01 GPU evidence **NOT RUN**. Past T4 v1 GPU release evidence is separate. Preserve failed research artifacts, bitwise CPU variability evidence and original historical v1.0.0 scientific release/classification untouched.

For full methods see [independent review handoff](PERF01C_INDEPENDENT_REVIEW_HANDOFF.md), [reviewer quickstart](PERF01C_REVIEWER_QUICKSTART_2026-11-06.md), and [pre-registered protocol candidate](RUNTIME_PERFORMANCE_PROTOCOL_V2_CANDIDATE.md).
