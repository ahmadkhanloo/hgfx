# PERF-01C — Exact independent-review assignment, Git branching, commit, push, and return protocol

**Prepared:** 2026-11-08. **Status:** AUTHOR-PREPARED INSTRUCTIONS ONLY. **Independent reviewer has NOT submitted a verdict.** This document is for a *different person* who is scientifically independent of the implementation and author-side engineering investigations.

## 1. Canonical URLs and immutable reference pins

- Repository: https://github.com/ahmadkhanloo/hgfx
- Benchmark-candidate PR **#87**: https://github.com/ahmadkhanloo/hgfx/pull/87
  - Source branch: `research/perf-01-preflight-fixtures`
  - Head checked when this guide was prepared: `271e480216ed8ecd19f76c960b75a3826ed89337`
  - Base: `main` (base SHA when checked: `44353387ab2578339174f0d8252aecb737654ae7`)
- Research, evidence, and reviewer-handoff PR **#99**: https://github.com/ahmadkhanloo/hgfx/pull/99
  - Source branch: `research/perf01d-unitsq-intermediate-arithmetic`
  - Parent/base: `research/perf01d-x0-infstate-observation-source`; it is a **stacked DRAFT PR**, not a replacement for the original #87 candidate.
  - Head *before this instruction file is added*: `7b3e8762431d716af8e767abbb5217d8d253b64d`. **This very document necessarily changes the latest branch head.** The reviewer must record the *actual* SHA fetched, not trust this stale illustrative SHA.
- Canonical reviewer-verdict Issue **#88**: https://github.com/ahmadkhanloo/hgfx/issues/88
- Independent 28-case worksheet: https://github.com/ahmadkhanloo/hgfx/blob/research/perf01d-unitsq-intermediate-arithmetic/docs/research/PERF01C_28_CASE_INDEPENDENT_DECISION_WORKSHEET_2026-11-08.md
- Scientific/methods reviewer instructions: https://github.com/ahmadkhanloo/hgfx/blob/research/perf01d-unitsq-intermediate-arithmetic/docs/research/PERF01C_EXTERNAL_REVIEW_INSTRUCTIONS.md
- Full reviewer handoff: https://github.com/ahmadkhanloo/hgfx/blob/research/perf01d-unitsq-intermediate-arithmetic/docs/research/PERF01C_INDEPENDENT_REVIEW_HANDOFF.md
- Frozen MATLAB/HGFX numerical equivalence policy: `docs/validation/MATLAB_EQUIVALENCE_POLICY.md`.
- Frozen original HGFX `v1.0.0`: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Frozen original MATLAB HGF Toolbox 8.2.0: `2437f4dc241541072722a2695ddeca7b44d83dd3`.

**Never replace the original reference with the current `main` software, renumber completed milestones, reclassify existing failures, adjust numerical acceptance thresholds, change seeds/datasets, remove planned benchmark cases, or run paper-claim timings before an independently approved prospective freeze.**

## 2. Fetch *both* actual PR heads and lock the evidence examined

Prerequisites: Git and GitHub CLI (`gh`, logged in with `gh auth login`); alternatively use GitHub web for PR creation and Issue comment. Commands below are for Bash/Git Bash or a POSIX terminal.

```bash
git clone https://github.com/ahmadkhanloo/hgfx.git hgfx-perf01c-independent-review
cd hgfx-perf01c-independent-review
git fetch origin pull/87/head:refs/remotes/origin/perf01-pr87
git fetch origin pull/99/head:refs/remotes/origin/perf01-pr99
git rev-parse refs/remotes/origin/perf01-pr87
git rev-parse refs/remotes/origin/perf01-pr99
git rev-parse origin/main
git log --oneline -3 refs/remotes/origin/perf01-pr87
git log --oneline -3 refs/remotes/origin/perf01-pr99
git diff --stat origin/main refs/remotes/origin/perf01-pr87
git diff --stat refs/remotes/origin/perf01-pr87 refs/remotes/origin/perf01-pr99
```

**Record all three full SHAs**: PR #87, PR #99 and `main`. Review the original PERF-01 candidate at PR #87 *and* the later scientific evidence/reviewer policy at PR #99. Do not silently assume they describe the same code. If either PR moves during review, identify exactly which full SHA was reviewed and whether a delta review is required.

Create your own review branch **from the fetched PR #99 tip** so the review report is a *single additive change*, not a rewrite of the author's code or history:

```bash
git switch -c review/perf01c-REVIEWER-20261108 refs/remotes/origin/perf01-pr99
git rev-parse HEAD
```

Replace `REVIEWER` everywhere with your GitHub username (lowercase, no spaces). **Do not push directly to `main`, either research branch, or PR #87/#99 source branches. Do not amend author commits.**

## 3. Exactly what to review, and what to leave blocked

1. **Original true sources:** confirm fixed HGFX and MATLAB SHAs, active `fitModel`, `hgf_binary`, `unitsq_sgm` resolution, version/configuration, fixed/free parameters, trial masks, prior/starting point and full 64-subject dataset. Review original evidence, not just the green regression checks.
2. **Full source integrity:** confirm all **28 originally planned** benchmark case IDs, original file hashes, derived records and original 64-subject fit. The original case split is **16 diagnostic-concordant / REVIEW_PENDING** and **12 BLOCKED** (8 invalid original workloads; 2 noncomparable starting policies; 2 multisubject numerical-fitting mismatch). Exactly **6 of 9 primary CPU rows** are blocked. No dropping failed rows.
3. **Scientific tolerance not bit equality:** the original full public fit is **63/64 SCIENTIFIC NONPASS**, with four out-of-tolerance `traj.mu` cells and four `traj.muhat` cells in zero-based subject 7. Existing trajectory tolerance is `abs(HGFX - MATLAB) <= 3e-10 + 3e-8*abs(MATLAB)`. Other fields have their **own** frozen tolerances. Small `1e-15` per-operation bit differences are not themselves acceptance failures. Crucially, **do not retroactively turn the original 63/64 into 64/64**. An acceptable narrower prospective claim may still be possible if every relevant gate is explicitly and independently satisfied.
4. **Endpoint sensitivity:** inspect original same-parameter forward runs and MATLAB/HGFX public optimizer convergence, gradients, finite differences and line-search decisions. Apply the existing policy's conditional Level-2 scientific/optimizer exception **only if its original conditions are independently verified**. Algebraic local parity cannot be confused with full-fit scientific identifiability.
5. **Timing comparability:** assess the *same scientific computation and materialized result* for each proposed forward, objective or entire fitting cell. Account for private MATLAB `negLogJoint`, `fitModel` stdout, default-start resampling, optimizer family, warm/cold start, JAX JIT compile/transfer/synchronization, and source exactness. Do not compare a full MATLAB fit to an HGFX forward pass or a different optimizer.
6. **Prospective measurement protocol:** verify a real **same physical CPU** runner/affinity/thread/BLAS configuration; matched benchmark scope, materialization and logging; counterbalanced order (ABBA/BAAB), warmups, repetitions and CI/statistical policy, original sample denominators and versioned source lock **before timing**. Do not infer physical GPU performance from CPU-only jobs.
7. **Verdict:** after independently auditing all 28 rows and all reference evidence, issue exactly one **signed** verdict in Issue #88: `APPROVE_PROSPECTIVE_FREEZE` *only if every required condition and specific restricted scope are justified*, or `BLOCK_FREEZE` with precise remaining blockers. This decision is a **prospective new protocol**, not rewriting the historical 28-cell or 63/64 source record. If source evidence is missing, a qualified BLOCK_FREEZE is valid; **do not invent a reviewer approval**.

To retrieve the **original full-fit raw source artifact** if it is still available:

```bash
mkdir -p evidence/original-64
gh run download 41863441006 --repo ahmadkhanloo/hgfx \
  --name perf01-64-full-fits-41863441006 --dir evidence/original-64
sha256sum evidence/original-64/*
```

Original paired 64-fit ZIP artifact: https://github.com/ahmadkhanloo/hgfx/actions/runs/41863441006/artifacts/13341288055 (GitHub ZIP SHA-256: `45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587`). A ZIP hash is not the same as an extracted member hash; calculate and record both as appropriate. If the archive is unavailable, **record the access blocker** instead of fabricating evidence.

Check the tracked candidate/fit files, without modifying them:

```bash
python - <<'PY'
import json
from pathlib import Path
root = Path("benchmarks/runtime_v1")
candidate = json.loads((root/"eligibility_candidates/candidate_v2_fullfit41863441006.json").read_text())
fit = json.loads((root/"fit_cohort_results/summary-41863441006.json").read_text())
assert len(candidate["cases"]) == 28
assert candidate["classification_counts"] == {
    "DIAGNOSTIC_CONCORDANT_REVIEW_PENDING":16,
    "BLOCKED_INVALID_FROZEN_REFERENCE_WORKLOAD":8,
    "BLOCKED_NONCOMPARABLE_FITTING_START_POLICY":2,
    "BLOCKED_MULTISUBJECT_FIT_NUMERICAL_MISMATCH":2,
}
assert fit["subject_count"] == 64
assert fit["classification_counts"]["FIT_OUTPUTS_WITHIN_EXISTING_DIAGNOSTIC_TOLERANCES"] == 63
assert fit["classification_counts"]["FIT_NUMERICAL_OR_TRAJECTORY_MISMATCH"] == 1
assert fit["cases"][7]["fields"]["traj.mu"]["mismatch_count"] == 4
assert fit["cases"][7]["fields"]["traj.muhat"]["mismatch_count"] == 4
print("Integrity checks passed: 28 cases, 63/64 NONPASS, 4+4 failures.")
PY
```

This mechanical script is **not** an independent scientific review on its own. Review original MATLAB source paths and the result/timing contracts, and cite original artifact IDs, SHA-256 hashes, paths and lines.

## 4. Reviewer-authored report file: what must be committed

Create one new Markdown review report, e.g.:

`docs/research/reviews/PERF01C_EXTERNAL_REVIEW_REVIEWER_2026-11-08.md`

The report must be genuinely written and signed by the independent reviewer; **do not submit the blank author worksheet as a finished review**. It must contain:

- Reviewer full name, GitHub handle, role/organization, explicitly stated independence from PERF-01 implementation, UTC timestamp, and report Git author identity.
- Exact *reviewed* PR #87, PR #99 and base `main` **full 40-character SHAs**. Note any later moved branches explicitly.
- Original immutable source/model versions and exact verified artifact IDs, raw SHA-256 hashes, any unavailable evidence or access blockers.
- **All 28 case IDs** with an evidence-based row-level decision/reason; no case omission, retroactive selection or threshold relaxation. Clear separation of prior 16 `REVIEW_PENDING` from the 12 already `BLOCKED`.
- Numerical science assessment: original **63/64 NONPASS**; original **4 + 4** trajectory exceedances, original frozen fieldwise thresholds; conditional Level-2 scientific/optimizer evidence, unresolved issues and any material limitations.
- Benchmark-method assessment: eligibility, actual same-workload comparability, stdout/logging, optimization/restarts, hardware, affinity, thread count, timing boundary, statistics and source versioning.
- Findings ranked `CRITICAL`, `MAJOR`, `MINOR` with **path/line, raw-evidence reference and a concrete closure condition**; tests actually executed with command/runtime/commit/result and skipped/not executed tests labeled honestly.
- Verdict **one of** `APPROVE_PROSPECTIVE_FREEZE` or `BLOCK_FREEZE`; the permitted *new prospective* scope and blocked cases, or smallest required remediation list. Do not label the original public fit, original nine-primary headline, GPU, or paper timing PASS unless its documented gate actually passed.
- Closing statement: `Reviewer: @REVIEWER — I independently reviewed PR #87 SHA ... and PR #99 SHA ...; verdict: ...; UTC date ...`; sign with the independent GitHub account. Cryptographic signed commit `git commit -S` is welcome when configured, but do **not** claim cryptographic signature unless GitHub verifies it.

The author-side [28-case worksheet](PERF01C_28_CASE_INDEPENDENT_DECISION_WORKSHEET_2026-11-08.md) is an evidence index to use; **write a new file rather than overwriting historical author-side worksheet or any science report**.

## 5. Commit + push on an *independent* branch and create a review PR

Once the independent report is complete, use your own git name/email and commit only the **new review report**:

```bash
mkdir -p docs/research/reviews
# EDIT and save docs/research/reviews/PERF01C_EXTERNAL_REVIEW_REVIEWER_2026-11-08.md
git config user.name "YOUR ACTUAL REVIEWER NAME"
git config user.email "YOUR OWN VERIFIED GITHUB COMMIT EMAIL"
git status --short
git add docs/research/reviews/PERF01C_EXTERNAL_REVIEW_REVIEWER_2026-11-08.md
git diff --cached --check
git diff --cached --stat
git commit -m "review(perf01c): independent 28-case scientific and benchmark eligibility verdict"
git rev-parse HEAD
```

**Option A — you have write access to the original repository:**

```bash
git push -u origin review/perf01c-REVIEWER-20261108
gh pr create --repo ahmadkhanloo/hgfx \
  --base research/perf01d-unitsq-intermediate-arithmetic \
  --head review/perf01c-REVIEWER-20261108 \
  --title "Independent PERF-01C review — @REVIEWER — signed verdict" \
  --body "Independent review report for Issue #88. Reviewed PR #87 and #99 exact SHAs documented in the report. Verdict and original 28-case denominator included; original 63/64 NONPASS preserved. Review-only change; no benchmark execution."
```

**Option B — you do NOT have write access: fork the public repo, push to YOUR fork, open a cross-fork PR:**

```bash
gh repo fork ahmadkhanloo/hgfx --clone=false --remote=false
git remote add fork https://github.com/REVIEWER/hgfx.git
git push -u fork review/perf01c-REVIEWER-20261108
gh pr create --repo ahmadkhanloo/hgfx \
  --base research/perf01d-unitsq-intermediate-arithmetic \
  --head REVIEWER:review/perf01c-REVIEWER-20261108 \
  --title "Independent PERF-01C review — @REVIEWER — signed verdict" \
  --body "External source/eligibility review for #88; documented full source commit SHAs and verdict. Review file only."
```

If `gh pr create` fails because of permissions, open the corresponding **Compare & pull request** in GitHub and select **base** `ahmadkhanloo/hgfx:research/perf01d-unitsq-intermediate-arithmetic` and **compare** your review branch or fork. **Do not merge the reviewer PR yourself**; the project maintainer will verify the report and independent provenance.

## 6. Post the binding reviewer verdict to Issue #88

After the reviewer PR is open, add a **reviewer-authored, authenticated GitHub comment** directly to https://github.com/ahmadkhanloo/hgfx/issues/88. Include all:

```text
PERF-01C INDEPENDENT REVIEW VERDICT: [APPROVE_PROSPECTIVE_FREEZE | BLOCK_FREEZE]
Reviewer: @REVIEWER / <full name and independence declaration>
UTC date:
Reviewed original PR #87 commit (full SHA):
Reviewed stacked PR #99 commit (full SHA):
Reviewed main base commit (full SHA):
External review report PR URL:
External review report commit (full SHA):
Exact original evidence run IDs / artifact SHA-256 checked:
28-case outcome: 16 review-pending / 12 blocked originally; independently reviewed row-level results in report.
Original 64-subject fitting: 63/64 SCIENTIFIC NONPASS (4 traj.mu + 4 traj.muhat out-of-tolerance cells).
Specific scientific/runner eligibility conclusions and unresolved blockers:
Prospective new protocol scope/version and whether all acceptance conditions hold:
I independently reviewed the above evidence and sign this verdict as @REVIEWER.
```

Use GitHub UI or `gh issue comment 88 --repo ahmadkhanloo/hgfx --body-file <FILE_CONTAINING_YOUR_FINAL_COMMENT>`. Report content must match the committed independent review; issue comment must be posted **by the actual reviewer GitHub account**, not the author-side assistant.

If you have GitHub PR-review rights, also submit a PR review/comment on PR #87 documenting critical findings, with Issue #88 linking to the complete report. **The authoritative decision is the signed #88 comment plus the independently authored review PR and exact commit**, not a green GitHub Actions result.

## 7. Exact hand-back packet for the project owner / ChatGPT

Send the project owner **all five values** below:

```text
1. REVIEW_VERDICT: APPROVE_PROSPECTIVE_FREEZE  (or BLOCK_FREEZE)
2. REVIEW_REPORT_PR: https://github.com/ahmadkhanloo/hgfx/pull/<NEW_REVIEW_PR_NUMBER>
3. REVIEW_REPORT_COMMIT_SHA: <40-character SHA>
4. ISSUE_88_SIGNED_COMMENT: https://github.com/ahmadkhanloo/hgfx/issues/88#issuecomment-<ID>
5. REVIEWED_SOURCE_SHAS: PR87=<40-char>, PR99=<40-char>; MAIN=<40-char>
```

Optionally include the SHA-256 hashes of supplemental raw artifacts if the report cites newly produced ones. The owner can paste these five values into a new ChatGPT message: **“Continue HGFX PERF-01C using this independent reviewer result; verify the reviewer-authored PR, exact SHAs, source hashes, per-case decision and signed issue comment; do not change historical science gates.”** The project is repository-first: the PR/comment/report are primary evidence and should not depend on any previous chat context.

**Until this is done, actual state remains:** `PERF-01C = OPEN / NOT FROZEN / BLOCKED_PENDING_EXTERNAL_REVIEW`, the original public fitting `63/64 SCIENTIFIC NONPASS`, original 28 planned cases `16 REVIEW_PENDING + 12 BLOCKED`, and **no paper-ready runtime speedup claim or new physical GPU benchmark PASS**.
