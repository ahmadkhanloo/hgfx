# P8 independent review packet

Status: **PRIOR INDEPENDENT V1 REVIEW ACCEPTED / PAPER-DELTA REVIEW PACKET READY / INDEPENDENT DELTA REVIEW OPEN**  
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

The existing delta manifest describes the prior locked candidate. It must be regenerated after the replacement candidate SHA is locked. No scientific threshold, seed, dataset, optimizer setting, frozen MATLAB reference file, or frozen v1 release-evidence artifact is changed by the P8-hardening edits.

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

The reviewed candidate `c6ef9e5f4113e373a5d492cb73c9dbe0fe89fd28` is **rejected for submission** by P8. The next replacement candidate SHA is **PENDING LOCK** and must be created only after remediation and fresh strict P7/P6A/P2/P5/regression checks pass.

The reviewer must review the exact next replacement candidate SHA recorded after the lock, not an unspecified moving `main`.

## Candidate gate evidence

Historical gate evidence for the failed `c6ef9e5` candidate is recorded above. All required gates must be re-run on the next replacement candidate.

  - status: `PASS_P7_PREFLIGHT`
  - abstract: 237 words
  - keywords: 6
  - highlights: 5
  - corresponding email present and equals the author-approved `m.ahmadkhanloo@ipm.ir`
  - blockers: 0
  - format/evidence errors: 0
- P6A Paper Evidence Draft run `35342538572`: PASS
  - claim audit status: `COMPLETE_P6A_2_NOT_FROZEN`
  - mapped numerical/versioned claim lines: 45
  - unmapped numerical lines: 0
  - manifest status: `DRAFT_NOT_FROZEN`
  - inventory: 59 committed artifacts
  - zero-diff regeneration: PASS
- P2 Paper Tables run `35342538617`: PASS
- HGFX Regression run `35342538746`: PASS
  - Ubuntu: 214 passed, 4 skipped
  - Windows: 214 passed, 4 skipped
  - frozen reference verification: PASS
  - frozen MATLAB source classification: PASS

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
