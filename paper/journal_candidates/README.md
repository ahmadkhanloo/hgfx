# HGFX — two journal-specific manuscript candidates (2026-10-23)

**Status:** DRAFTS FOR AUTHOR REVIEW — NOT SUBMITTED. Both describe the *same scientific study*. Submit only one at a time; do not initiate concurrent peer review. The JNM rejection remains part of historical publication records. No original paper manuscript, frozen product release, validation outcome or P8/P6A historical evidence is changed by this branch.

## Authoritative basis

- Source manuscript: `paper/manuscript.md` on `main` (source Git blob `6ffa1ddd710fddb760ac1abef205868037c978a5`).
- Frozen HGFX v1.0.0: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Frozen MATLAB HGF Toolbox 8.2.0: `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Scientific paper protocol: `hgfx-paper-protocol-1`. These draft changes are editorial; the frozen experiment protocols and records are not reopened.
- Common external comparator: `pyhgf==0.3.2`; 11 mapped quantities agree only in the authorized cell, while response NLL is NDC.

## Candidate A: Neuroinformatics (Springer Nature)

- Main manuscript: `neuroinformatics/manuscript.md`.
- Cover letter: `neuroinformatics/cover_letter.md`.
- Article type: **Software Original Article**. Official guidelines explicitly ask for software availability, installation, validation of exactness, and evaluation relative to existing packages.
- Original abstract: 209 words (required 150–250). Keywords: 6 (required 4–6).
- Required Information Sharing Statement is located immediately before Acknowledgments.
- Publication model: **Hybrid**; select **Subscription (no APC)** after acceptance rather than optional paid Open Access. Check any separate charges before confirmation.
- Primary guidance: https://link.springer.com/journal/12021/submission-guidelines ; https://link.springer.com/journal/12021/how-to-publish-with-us

## Candidate B: Neuroscience Informatics (Elsevier)

- Main manuscript: `neuroscience_informatics/manuscript.md`.
- Separate author title page: `neuroscience_informatics/title_page.md`.
- Cover letter: `neuroscience_informatics/cover_letter.md`.
- Article type: **Original Research**. No clinical or neurological outcome claim was introduced to force fit.
- Structured abstract: 199 words. Total Markdown manuscript: approximately **3,408 whitespace-delimited words**, including references, tables and figure legends. The 2021 archived author-guide PDF states 3,500 words inclusive for Original Research; re-check the live instructions before submission (the online Elsevier guide is access-restricted in this environment). **2021 guidance may be stale**.
- The older author guide requires **double-blind** submission. A separate title page has been provided, and the manuscript removes the named author. **However, direct links to the public GitHub repository can reveal the author's identity**; true blinding must be resolved with the editor/reviewer-access mechanism before submission.
- Journal scope is computational but includes a medical/clinical advancement qualifier. This paper does not introduce clinical data; do not assert this qualifier is definitively satisfied.
- This journal is **gold Open Access**; base Full-length APC is **USD 2,540**, per the publisher's October 2026 page. There is **no subscription-based APC-free option**. Do not submit until full institutional coverage or a 100% waiver is approved in writing.
- Historical guide (2021; treat as provisional): https://www.em-consulte.com/getInfoProduit/NEURI/instructionsAuteurs/NEURI.pdf ; current guide: https://www.sciencedirect.com/journal/neuroscience-informatics/publish/guide-for-authors

## Shared scientific evidence — unchanged

- Two official MATLAB demonstrations reproduced within frozen tolerances.
- The paired S7 grid gives **36/36 BIC winners in agreement** between HGFX and MATLAB.
- Parameter recovery is **not** a scientific PASS; historical M18 and subsequent recovery limitations are retained.
- P3 longer-horizon experiment failed paired integrity (**10/72 disagreements**); classified **INSUFFICIENT_REFERENCE_EVIDENCE** rather than an identifiability conclusion.
- Physical GPU evidence comes from the retained Tesla T4 fitting cells; it is **not** GPU speed or multi-GPU scaling evidence.
- pyhgf comparison is one mapped 128-trial cell; response NLL is **NOT_DIRECTLY_COMPARABLE**.

## Before actual submission

1. Author review the journal-specific manuscript and correspondence; ensure no citation or claim mismatches.
2. Use original figure assets under `paper/figures/` and table generator under `paper/scripts/`; check actual figure/table embedding and caption order.
3. Regenerate figure, manuscript and supplement artifacts from the exact frozen source and record hashes. Do not use a moving `main` reference as the evidence lock.
4. Convert Markdown into editable Word/LaTeX manuscript and standalone reviewer PDF, and complete publisher metadata and declarations.
5. Confirm author identity, contact address, the applicable AI declaration, current live author instructions, and any blind-review requirement.
6. For Springer choose Subscription; for Elsevier wait for written **zero-APC** confirmation.
7. Arrange independent manuscript-delta review against this exact branch before final freeze. **No claim of P8 PASS is made by these editorial drafts**.
8. Submit only one manuscript at a time. Keeping two candidate files does not constitute parallel submission.

## Known remaining blockers

- Elsevier full APC waiver/IPM coverage: **UNCONFIRMED**.
- Elsevier exact current author-guide availability: **UNVERIFIED**; 2021 archived PDF used as fallback.
- Elsevier blinded repository access: **UNRESOLVED**.
- Final manuscript rendering/figures, independent candidate review, and author confirmation: **OPEN**.
