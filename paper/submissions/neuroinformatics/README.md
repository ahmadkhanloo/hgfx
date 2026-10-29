# Neuroinformatics submission package for HGFX

**Target journal:** *Neuroinformatics* (Springer Nature)  
**Article type:** **Software Original Article**  
**Original locked scientific manuscript:** `paper/manuscript.md`, final P8 reviewed candidate `897aed804901f9f49ad1d73ecfab6fa714d50098`; P6A manifest `FROZEN_FOR_SUBMISSION`.  
**Journal conversion base:** `main` at `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`.  
**Frozen product:** HGFX `v1.0.0` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.  
**Frozen oracle:** MATLAB HGF Toolbox 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3`.

## Scope

This is a derivative **journal-specific presentation layer**. The earlier submission manuscript, validated figures, P8 review record, scientific criteria, historical results, and P6A frozen evidence manifest are **not modified**. No new validation claim or benchmark is introduced.

Deliverables:

- `manuscript.md` — complete journal-targeted editable manuscript source, 150–250 word abstract, six keywords, Software Original Article framing, Information Sharing Statement immediately before Acknowledgments, and Springer-compatible declarations.
- `cover_letter.md` — journal-specific cover letter.
- `title_page.md` — separate title page / corresponding-author details.
- `build_submission.py` — builds manuscript DOCX/PDF, title page DOCX, cover letter DOCX, supplementary DOCX/PDF, and a ZIP of submission source/figures.
- `preflight.py` — checks journal-specific format, frozen identities, six figures, and claims before a build.
- `SUBMISSION_CHECKLIST.md` — upload instructions, remaining author actions, and editorial risks.

## Build

From the repository root with Python 3.11+, Pandoc with citeproc, pdflatex, and poppler-utils:

```bash
python paper/submissions/neuroinformatics/preflight.py
python paper/submissions/neuroinformatics/build_submission.py
```

By default, built files are in `paper/dist/neuroinformatics/` (excluded from source-control if ignored); GitHub Actions `Neuroinformatics submission build` also uploads the complete set as a downloadable workflow artifact.

The manuscript PDF is a convenience review copy; the **DOCX** is the editable source required for the submission.

## Disclosure caveat

Springer requires public access to all analysis resources and a domain-appropriate data repository. Evidence and code are currently public in versioned GitHub source control. Before final submission, the author should check with the journal whether those versioned repository records meet its data-deposit expectation or deposit a snapshot in a permanent archival repository with DOI; do not invent a Zenodo DOI.

Confirm the author's details and final contribution/competing-interest declaration in the Springer submission interface. Verify the manuscript is not under consideration elsewhere. Upload only through the official Springer Nature submission portal.
