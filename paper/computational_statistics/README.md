# Computational Statistics working revision

> **HISTORICAL COMPSTAT CANDIDATE — superseded for future submission (2026-11-10).** The author chose D1 B (change journal). Keep this directory, its prior manuscript and frozen evidence as history; do **not** rename completed REV tasks or treat old REV-2–REV-5 as passed. Active new path: [software-publication plan](../../docs/planning/SOFTWARE_PUBLICATION_PLAN.md), [working paper directory](../software_publication/README.md) and [new acceptance gate](../../docs/validation/SOFTWARE_PUBLICATION_GATE.md). The final venue/author fee clearance remains OPEN.


> Current execution authority (2026-11-09): [COMPSTAT revision plan](../../docs/planning/COMPSTAT_REVISION_PLAN.md), with its [task ledger](../../docs/planning/COMPSTAT_REVISION_LEDGER.md). The earlier [case-study handoff](../../docs/superpowers/plans/2026-11-04-pain-case-study-handoff.md) is historical planning, not authority to run experiments outside the fixed COMPSTAT task list. Submission remains excluded until D1–D3 author gates.

Status: **DRAFT — initial editorial revision, not submission-ready** (2026-11-03).

Start with [the complete execution plan](../../docs/superpowers/plans/2026-11-03-publication-revision.md). It is written for an agent without access to prior conversations. The [audit](../../docs/submissions/2026-11-03_publication_audit_fa.md) explains the journal choice and financial uncertainty.

`manuscript.md` is the active working copy for this revision. It derives from `paper/manuscript.md` at `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`. Initial edits change the title, abstract, audience framing in the Introduction and Discussion, and Figure 3 caption. Existing methods, numerical results, references, declarations, and remaining captions are inherited, not newly validated or approved by the author. Inherited declarations require author reconfirmation before submission.

The historical manuscript and frozen artifacts remain unchanged. Results concern HGFX 1.0.0, not all features on current main. All `paper/...` paths inside the draft are repository-root paths. Figures and bibliography currently refer to historical assets; Figure 3 still needs the visual revision specified in the plan. No final PDF or new figure bundle has been built for this candidate.

Remaining work includes the mathematical summary, runnable worked example in a clean 1.0.0 environment, source-bound software comparison, full editorial review, updated figures, claim ledger, rendering, and zero-cost submission preflight. Existing paper tests validate their historical inputs, not this new manuscript automatically.

Do not run the old `paper/scripts/build_journal_submission.py` and assume its output uses this draft: it hard-codes the historical manuscript. The plan requires a separate build path or explicit candidate inputs.

## bioRxiv revision

Official guidance permits a revision before formal journal acceptance through **Author Area → Submit a Revision**. Revisions retain the DOI and prior versions remain accessible. Source checked on 2026-11-03: [bioRxiv overview](https://www.biorxiv.org/about-biorxiv) (official indexed text retrieved; direct page access returned HTTP 403 during this session).

The recorded DOI is `10.64898/2026.09.22.753415`. Verify the actual posted version in the author's account before preparing its revision; no identity between that PDF and the current repository draft has been established here. Use the existing submission, not a new preprint record. Prepare the completed revised PDF and an accurate change summary, then obtain author approval. This work has not uploaded or submitted anything.

## Delivery boundary

Local preparation can proceed through all eight tasks. Actual journal submission, bioRxiv upload, author declarations, and any unresolved financial eligibility require the author's final action. A free subscription APC policy alone does not settle every possible mandatory charge; record the final terms before submission.

## Published-study extension

The author requested real published applications with public code and data. See [the source dossier](../case_studies/README_FA.md) and [the execution addendum](../../docs/superpowers/plans/2026-11-03-published-case-studies.md). This is source acquisition and a prospective plan, not completed replication evidence. No new case-study results have been inserted into the manuscript.


## REV-1 evidence and updated candidate figures (2026-11-09)

The original S7 36-case matrix and the new per-parameter uncertainty audit are traceable in
`evidence/revision/confusion_audit.json` (REV-1.1) and
`evidence/revision/recovery_uncertainty.json` (REV-1.2).
Both were computed from archived original MATLAB/HGFX paired S7 shards. No refitting.
For current candidate-specific review, Figure 2 and Figure 3 with confidence intervals
and the one-third chance baseline are generated at:

- `paper/computational_statistics/figures/fig2_recovery_uncertainty.{png,pdf}`
- `paper/computational_statistics/figures/fig3_model_recovery_uncertainty.{png,pdf}`
- `paper/computational_statistics/figures/revision_figures_manifest.json`

Use `python tools/plot_compstat_recovery_uncertainty.py` to regenerate
these figures from the committed REV-1.2 JSON. The **historical**
`paper/figures` assets must remain unmodified. The active manuscript has
not yet been rewritten to include these new figures: that is REV-3, after D2.
REV-1.3/1.4 are open and the publication is **not** submission-ready.
