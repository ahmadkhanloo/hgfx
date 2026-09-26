# P8 independent review packet

Status: **REPLACEMENT CANDIDATE LOCKED / NEW INDEPENDENT DELTA REVIEW REQUIRED**  
Prepared: 2026-09-18  
Tracking: PV1-02 / issue #32

## Accepted prior independent-review baseline

An independent frontier review **was already completed** before v1.0.0 release:

- report: `docs/validation/INDEPENDENT_REVIEW_REPORT.md`;
- reviewer: Independent Frontier AI Reasoning Agent (Antigravity);
- reviewed RC source: `ad8f5cd6fbea3bd1e5ac1cef8b51dbbb9a970a84`;
- two release-blocking HIGH findings (H1/H2) were identified;
- remediation record: `docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md`;
- post-remediation validated source: `09c49031cda95b449f8115030a9d32dcba36098e`;
- remediation status: **POST-REVIEW VALIDATION PASS — NO UNRESOLVED CRITICAL/HIGH FINDINGS**;
- final v1.0.0 promotion subsequently passed its release gates.

This prior review is accepted as the independent baseline for implementation, scientific-release integrity, cross-platform portability, frozen-source coverage, GPU applicability and release-readiness areas that it actually reviewed. P8 must **not repeat those checks from scratch** unless a later paper change invalidates the old evidence.

The remaining P8 scope is therefore a **delta review** of the current paper candidate: manuscript wording/overclaiming, paper-only P2A/P3 evidence, paper tables/figures, claim-to-evidence mapping, declarations/journal metadata, and any post-review code/evidence changes that affect manuscript claims.

Deterministic delta manifest: `docs/research/P8_DELTA_MANIFEST.json`  
Delta-scope guide: `docs/research/P8_DELTA_SCOPE.md`

The delta manifest is regenerated for the exact replacement candidate locked below. No scientific threshold, seed, dataset, optimizer setting, frozen MATLAB reference file, or frozen v1 release-evidence artifact is changed by the P8-remediation edits.

Delta-scope implementation: PR #66 merged as `39255756c8ef6bd1f4aaf3e5357ea70e430c55f3`.  
P8 Delta Scope run `35344626071`: PASS / full-history execution / zero-diff.  
Generic regression run `35344625984`: PASS on Ubuntu and Windows; 214 passed, 5 skipped on each platform. The extra skip is only the history-dependent delta test on shallow generic checkouts; the dedicated P8 workflow executes it non-skipped with `fetch-depth: 0`.

## Independent review attempt on replacement candidate — FAIL

The independent paper-delta review targeted candidate `c6ef9e5f4113e373a5d492cb73c9dbe0fe89fd28` (tree `e5ffa30435d7d3fa1d95ad00be60ee4f56dba82e`) and returned **FAIL** on 2026-09-26. This result is historical evidence and must not be rewritten as PASS.

Exact candidate gate runs were all successful before review:

- P2 Paper Tables `35540117257`: PASS
- P5 Paper Figures `35540117270`: PASS
- P6A Paper Evidence `35540117282`: PASS
- P7 JNM Preflight `35540117313`: PASS
- P8 Delta Scope `35540117266`: PASS
- HGFX Regression `35540117256`: PASS

Blocking review findings included: evidence-inconsistent Figure 4 backend magnitudes/criteria, stale candidate/provenance lock metadata, a reproduction README that referenced a workflow absent from the reviewed revision, and journal-facing outputs without a canonical citeproc bibliography-rendering path.

## Exact submission candidate

Replacement candidate SHA: `b66f294f4799968404273127a9b06b4fc451ffb3`  
Candidate tree: `507c7568ac0c53ccd69c59e630e0f164cbe40284`  
State: **LOCKED FOR NEW INDEPENDENT P8 REVIEW / NOT PASSED / NOT FROZEN**

This content candidate remediates the known CRITICAL/HIGH blockers from the failed `c6ef9e5` review. The lock itself is recorded in the subsequent documentation-only commit and does not alter the candidate under review.

## Candidate gate evidence

All required gates passed on the exact replacement candidate:

- P2 Paper Tables run `36242284491`: PASS
- P5 Paper Figures run `36242284480`: PASS
- P6A Paper Evidence run `36242284539`: PASS
- P7 JNM Preflight run `36242284523`: PASS
  - journal-facing DOCX/PDF are built with Pandoc citeproc before preflight;
  - bibliography-render verification passed.
- P8 Delta Scope run `36242284495`: PASS for the pre-lock manifest machinery.
- HGFX Regression run `36242284568`: PASS
  - Ubuntu: 216 passed, 5 skipped
  - Windows: 216 passed, 5 skipped
  - frozen-reference guards passed on both platforms.

The candidate is therefore **READY FOR INDEPENDENT REVIEW**, not PASS. The independent reviewer must review this exact SHA and use the regenerated delta manifest.

## Review scope

Review these files at the replacement candidate SHA once it is locked:

- `paper/manuscript.md`
- `paper/highlights.txt`
- `paper/references.bib`
- `paper/tables/`
- `paper/figures/`
- `paper/reproducibility/`
- `docs/research/PAPER_EVIDENCE_MAP.md`
- `docs/research/P3_M18C2_RESULT.md`
- `docs/research/PYHGF_COMMON_SCOPE_NUMERICAL_RESULT.md`

Use `docs/research/PAPER_P8_REVIEW_CHECKLIST.md` for findings.

## Reviewer rules

- This review must be independent of the implementation/self-review that produced the candidate.
- Findings use: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`.
- Any unresolved `CRITICAL` or `HIGH` finding blocks submission.
- Do not change scientific thresholds, seeds, datasets, grids, optimizer settings, historical classifications, or failed evidence to clear a finding.
- P3 remains `INSUFFICIENT_REFERENCE_EVIDENCE`; historical M18 remains preserved FAIL.
- D02/D08/S7 reference-limitation classifications must not be promoted to scientific PASS.
- pyhgf comparison remains the single authorized common-scope cell; response NLL remains NDC.
- GPU evidence is applicability/correctness evidence, not a speed/scaling claim.

## After P8

If and only if the independent review records `PASS` for this exact candidate SHA:

1. resolve any accepted MEDIUM/LOW findings without silently changing the reviewed scientific claim set;
2. if manuscript/evidence content changes materially, create and review a new candidate SHA;
3. once the reviewed candidate is final, run the final P6A freeze with:
   `status=FROZEN_FOR_SUBMISSION` and this exact candidate SHA;
4. verify that M19/v1.0.0 frozen evidence remains unchanged.
