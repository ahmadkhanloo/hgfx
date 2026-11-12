# Computational Statistics — active manuscript preview builder: exact-source local smoke and CI boundary

**Date:** 2026-11-13. **Scope:** article-type-setting infrastructure only, **NOT** a scientific HGF validation, actual current-manuscript PDF, journal acceptance or final author approval.

## Precise source and workflow

- `paper/computational_statistics/build_active_submission.py` committed on `compstat-revision` at [`b5037cc85536e3400a3e666cd98547d249cd7e04`](https://github.com/ahmadkhanloo/hgfx/commit/b5037cc85536e3400a3e666cd98547d249cd7e04). GitHub Git blob SHA **`56bbbbca6a7e79032f867618e3d79d50af44997e`**. Locally executed script's exact `git hash-object` matched that blob.
- Workflow first added at [`72e17ea84819973210609f43a41f74c452c25693`](https://github.com/ahmadkhanloo/hgfx/commit/72e17ea84819973210609f43a41f74c452c25693), then expanded to preserve the partial numerical-claim inventory at [`a5438300862544151b2ab53044c08f4ef4743a8b`](https://github.com/ahmadkhanloo/hgfx/commit/a5438300862544151b2ab53044c08f4ef4743a8b); later path/format correction [`4d8b586ff272d966c124679d518158617aa16d4d`](https://github.com/ahmadkhanloo/hgfx/commit/4d8b586ff272d966c124679d518158617aa16d4d). The workflow builds on GitHub-hosted Ubuntu, records source versions, and uploads the result (including failure logs). It runs **no MATLAB/HGFX/JAX simulation or benchmark**.
- Generated author-review outputs (Markdown for the exact draft, two editable `.tex`, two `.pdf`, actual six figure PDFs, BibTeX, source ZIP, manifest and logs) are gitignored and must not be mistaken for immutable scientific evidence.
- Builder uses generic Pandoc article layout; **not** the publisher's verified official Springer class. It fails if six current numbered tables, six figure captions, 150–250-word abstract, required bibliography keys, actual figure PDFs or planned page limits (main ≤14, ESM ≤10) cannot be met. No changes to original thresholds or study protocols.

## Execution actually performed on a non-scientific fixture

A synthetic, standalone **six-table / six-figure** mock Markdown manuscript was built from the *byte-identical Git blob* of the committed builder. Figures were intentionally minimal PDF test labels; the abstract was a synthetic 180-word paragraph. This is **not** an attempted model replication or final paper PDF.

Local command:

```text
python build_active_short.py --root /mnt/data/compstat_work/mock \
  --outdir /mnt/data/compstat_work/mock_short_out
```

Locally observed Python 3.13.5, pandoc 3.1.11.1, pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2025/dev/Debian), Poppler pdfinfo 25.06.0. Main produced **8 test-only pages**, ESM **1 test-only page**, with editable LaTeX and a source ZIP; fixture status `DRAFT_PAGE_LIMITS_MET` only under mock data. The mock first page was rendered via Poppler and visually inspected; the two mock PDFs are **not** offered as current scientific article output.

**Negative checks actually executed:** a fixture abstract shortened to one word raised a `ValueError` before conversion; removal of one PDF figure raised `FileNotFoundError` instead of silently substituting an illustration. These do not prove all possible invalid inputs are rejected.

## Active science/article source checks (static, not rendered)

Re-fetched active exact GitHub source bytes and checked:
- Manuscript abstract **237 words** under current range; main Table headings **1–6**, figure caption IDs **1–6**, and source caption regex accepts each; 14 BibTeX keys with no undefined reference in main+ESM; ESM retains seven numbered appendices.
- All six active `paper/figures/*.pdf` paths exist in the active Git tree (GitHub textual fetch reported binary PDF UnicodeDecodeError, so **binary PDF bytes and geometry were not retrieved**).
- Cross-read all **16** existing numerical claim-map phrases and numeric JSON-pointer values against four existing machine-readable evidence files; *the examined values matched* (source metadata and sources not modified). This is a targeted interpreted source check, **NOT** execution of `tools/check_manuscript_claims.py` or proof of full number coverage, all digests, citation completeness or independent scientific interpretation.
- Current PR #107 is still **DRAFT**; last checked Actions/run API returned **zero PR-triggered run records** for the workflow commits. A missing run record does **not** prove the workflow ran, passed or failed.

## Blocking next results; do not infer from mock

1. **Actual-source PDF build has not been observed:** exact PR checkout plus actual six figure-PDF binaries and journal build dependencies need to execute the new workflow, producing identifiable run ID/commit/manifest and real main/ESM page counts. The main's historical pre-revision TeX/PDF ZIP is **not** a substitute and has not been copied.
2. **Rendered PDF visual QA is OPEN:** all actual pages, caption placement, math notation, citations, longtable fragmentation, reference formatting and accessibility need inspection. If main >14 or ESM >10 under the original plan, shorten content or restructure figures/tables *without changing data, claims or page limits*.
3. **Full numeric evidence coverage OPEN**: partial `--allow-unmapped` inventory is never a final claims PASS; strict mode, independent scientific review and author D2/D3 decisions are outstanding.
4. The original REV-2.4 `NOT_GLOBAL_PASS`, official D08 own-fit trajectory discrepancies, D02 missing source endpoint, old P3/M18 failures, REV-2.3 `NOT_RUN`, and PERF-01C `BLOCK_FREEZE` remain intact.

**Classification:** `TYPESETTING_BUILDER_IMPLEMENTED / EXACT_SOURCE_LOCAL_SYNTHETIC_SMOKE_PASS`; `ACTUAL_ARTICLE_PDF_NOT_VALIDATED`; `ARTICLE_READY_FOR_SUBMISSION=NO`.
