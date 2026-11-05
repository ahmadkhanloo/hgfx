# Computational Statistics author-review package

Executed 2026-11-04 under the [Pain and journal handoff](../../docs/superpowers/plans/2026-11-04-pain-case-study-handoff.md) and [parent plan](../../docs/superpowers/plans/2026-11-03-publication-revision.md).
**Ready for author review; not ready for submission.**

- [Main PDF](package/HGFX_CompStat.pdf), [supplement PDF](package/HGFX_Supplement.pdf), and [flat editable LaTeX/BibTeX/figure source](package/HGFX_CompStat_source.zip).
- [English manuscript](manuscript.md), [supplement source](supplement.md), [claim ledger](CLAIM_EVIDENCE.csv) and [independent review in Persian](EDITORIAL_REVIEW_FA.md).
- [Submission status](SUBMISSION_CHECKLIST.md), [policy and fee checks](JOURNAL_POLICY_CHECK.md), [venue fit](VENUE_FIT.md), [cover letter](cover_letter.md), [preprint revision note](BIORXIV_REVISION.md), [execution log](EXECUTION_LOG.md).
- [Pain feasibility](../case_studies/pain_2025/FEASIBILITY.md) and [SPIRL fallback feasibility](../case_studies/spirl_2025/FEASIBILITY.md).

Pain inputs are present, but exact custom-response permission and historical environment remain unresolved. SPIRL needs a separate migration of custom joint models. Neither case was fitted. No real-data replication figure is claimed. The [24-trial synthetic quickstart](worked_example/README.md) did run from a verified 1.0.0 wheel outside the checkout on CPU float64; it is workflow evidence.

The manuscript is rewritten around the statistical workflow, adds a source-checked formulation and software comparison, separates implementation agreement from recovery, and preserves failed recovery/P3 gates and NDC. Historical manuscript, tables, reference evidence and figures remain unchanged. Scientific claims concern frozen 1.0.0, not current development additions.

## Rebuild and check

From the repository root, with Python, matplotlib, Pandoc, pdfLaTeX and Poppler:

```sh
python paper/computational_statistics/generate_figures.py
python paper/computational_statistics/build_submission.py
python paper/computational_statistics/verify_revision.py
python -m pytest tests/paper/test_compstat_revision.py tests/paper/test_p5_figures.py -q
```

The builder reads this candidate explicitly, uses author-year citeproc, and produces a flat source archive under package/. The layout is a generic author-review article, not the official Springer class: the linked official template download returned 403. Source/PDF hashes and tool versions are in the build manifest. See [third-party notices](THIRD_PARTY_NOTICES.md) for the CSL style. PDFs were rendered and inspected; a failed-build log and the fixes are recorded.

Remaining gates: human claim/declaration approval, no executed external application, comprehensive zero-fee/institutional clearance, final venue/account preflight and current preprint-revision policy. No submission, upload, email or financial commitment occurred.

Text source hashes use LF consistently with the existing repository attributes; binary hashes remain byte-exact. Original raw baseline hashes are retained alongside canonical text identities.

## Critique-resolution revision (4 November 2026)

See [response to critique](RESPONSE_TO_CRITIQUE_FA.md), [frozen protocol](REVISION_PROTOCOL.md),
[empirical example](empirical_example/README.md) and [raw-result audit](evidence/p3_diagnostic_audit.json).
The historical 10 unmatched-winner flags are 10 jointly absent winners, not
10 conflicting nonempty choices. The original failed gate remains unchanged.
S7 parameter-wise results and its confusion matrix are now reported. Author
metadata/declarations were confirmed in chat; scientific approval remains pending.
A 614-observation empirical-input workflow completed with finite statistics;
it is not an external participant-study replication or a new MATLAB parity test.
Rebuild the audit first with `python paper/computational_statistics/audit_frozen_results.py`.
Then use the figure/build/verification commands above. The latest revision
manifest supersedes prior package hashes; historical checkout verification is
retained as an earlier record, not proof for this revision.
