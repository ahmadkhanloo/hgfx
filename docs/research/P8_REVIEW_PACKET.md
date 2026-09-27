# P8 independent review packet

Status: **ROUND-3 CANDIDATE LOCKED / READY FOR INDEPENDENT DELTA REVIEW**  
Prepared: 2026-09-26  
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

Round-3 candidate SHA: `897aed804901f9f49ad1d73ecfab6fa714d50098`  
Candidate tree: `2c50052dfd06b3013ee5402f56caa4b640ab4cce`  
State: **LOCKED FOR INDEPENDENT P8 REVIEW / NOT PASSED / NOT FROZEN**

This content candidate remediates the recorded round-2 HIGH/MEDIUM publication findings while preserving the historical failed reviews and all frozen scientific criteria/classifications. Post-candidate commits are restricted to review-lock metadata and are checked by the P8 delta guard; they do not change the content candidate.

## Candidate gate evidence

Paper-specific gates on the exact round-3 candidate:

- P2 Paper Tables run `36260396797`: PASS
- P5 Paper Figures run `36260396680`: PASS
- P6A Paper Evidence run `36260396774`: PASS
- P7 JNM Preflight run `36260396760`: PASS
- P8 CPU Postfix Evidence run `36260396759`: PASS
  - CPU/backend criterion remains `0.10`;
  - measured maximum fit-objective gap is `0.006783711260709424`;
  - this is CPU/backend correctness evidence, not a speed claim.
- P8 Delta Scope run `36263948652`: PASS on the locked manifest for the exact candidate.
- Full HGFX Regression run `36260789062`: PASS on a documentation-only lock descendant with the same implementation/manuscript/evidence content as the candidate; Ubuntu and Windows both completed successfully.

No frozen `reference/matlab/` file and no frozen `reference/validation/v1_release/` artifact changed in the candidate delta.

The candidate is therefore **READY FOR INDEPENDENT REVIEW**, not P8 PASS. The independent reviewer must review this exact SHA and record the round-3 result in `docs/research/PAPER_P8_REVIEW_CHECKLIST.md`.

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
