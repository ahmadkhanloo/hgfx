# Brain Informatics transfer dossier (2026-10-31)

## Status and provenance
- STATUS: PREPARED — not transferred or submitted to Brain Informatics; no waiver approval has been received.
- Journal: Brain Informatics (Springer Nature); editor-recommended transfer after rejection by Neuroinformatics.
- Manuscript: "HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox".
- Neuroinformatics submission ID: b6d791b5-88bf-491d-8c77-cc11f2da33d7 (REJECTED; no external reviewer reports provided in the decision email supplied by the author).
- Earlier Journal of Neuroscience Methods submission: JNEUMETH-D-26-01047 (REJECTED; no concurrent active review asserted).
- Author and corresponding author: Mohammad Ahmadkhanloo, Institute for Research in Fundamental Sciences (IPM), Tehran, Iran; m.ahmadkhanloo@ipm.ir.
- Starting scientific source: main @ bbf17e9cf0d14d91bf44f50e307a0be55cbede02, paper/manuscript.md and paper/reproducibility/PAPER_PROTOCOL.md. This is **not** proof that the exact binary previously submitted to Neuroinformatics matches the repository text; author must check.
- Frozen scientific protocol and historical negative results MUST remain unchanged; this dossier is journal-facing administrative preparation, not revised scientific evidence.

## Journal-specific requirements checked against official pages
- Instructions: https://link.springer.com/journal/40708/submission-guidelines
- Research article: https://link.springer.com/journal/40708/submission-guidelines/research
- Article type: Research.
- Abstract 150–250 words; 3–10 keywords.
- Single-anonymous review (not double-blind): include title page with full author name, affiliation and corresponding author, unless live portal indicates a different file requirement.
- Editable manuscript (DOCX or LaTeX sources), double spacing, line and page numbering.
- Required headings under Declarations: Availability of data and materials; Competing interests; Funding; Authors' contributions; Acknowledgements. Include 'Not applicable' where appropriate.
- Software availability should include project page, archived release identifier/DOI if available, OS, language, license, and restrictions, and cite supporting datasets.
- Recheck figures, references, supplementary appendices, disclosures, AI-use disclosure, and precise claims against the frozen manuscript.
- APC listed on 2026-10-31 as EUR 940 (subject to taxes and acceptance-time pricing); full OA.
- Springer hardship waiver policy: select waiver/discount in submission process, then follow the separate application link after submission or via email, completing the form within 14 days. Merely selecting the check box is not the application. No guarantee of waiver. https://support.springernature.com/en/support/solutions/articles/6000227580-apc-waivers-and-discounts
- Official transfer explanation: https://link.springer.com/journal/40708/submission-guidelines (Manuscript transfers). Author must personally consent to transfer and complete destination submission. Research Square cannot transfer between journals.
- Author-facing recommendations URL: https://notifications.springernature.com/notifications/b4cf1085-66e3-47c2-b7b5-da820384f381?channel=email

## Proposed journal-specific emphasis
This is a computational neuroscience **scientific-software reproducibility and validation** contribution, not a new generative model or claim of universal optimizer parity. Focus on established HGF workflows for computational cognition, traceable MATLAB equivalence, reproducibility, and explicitly scoped limitations. Never assert speedup, multi-GPU performance or scientific identifiability beyond frozen evidence.

## Proposed cover letter (author to confirm declarations before use)

Dear Editor-in-Chief,

Please consider our manuscript, “HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox,” for publication as a Research Article in Brain Informatics. We are submitting it through Springer Nature’s transfer process following the editorial recommendation made after consideration at Neuroinformatics.

The Hierarchical Gaussian Filter is widely used to study learning under uncertainty and volatility. HGFX 1.0.0 provides a MATLAB-independent Python/JAX implementation intended to reproduce the scientific and workflow behavior of a frozen MATLAB HGF Toolbox 8.2.0 reference within explicitly validated scopes. Instead of claiming a new learning model, we make compatibility and reproducibility measurable through predeclared numerical tolerances, paired workflows, model-selection checks, and reproducibility artifacts.

The manuscript reports agreement for two official reference workflows and all 36 BIC winners in a frozen paired model-selection grid. Equally importantly, it preserves parameter-recovery failures, optimizer-sensitive cases, and explicitly non-comparable quantities rather than representing those results as successful scientific validation. We believe this distinction is relevant to Brain Informatics' interest in the cognitive and computational foundations of brain science and in reliable computational methods.

The open-source code and documentation are available at https://github.com/ahmadkhanloo/hgfx. The manuscript discloses AI-assisted development and preparation, and distinguishes supported numerical and GPU-applicability claims from performance claims.

I am the corresponding author. [AUTHOR TO CONFIRM: I have approved the submitted version, it is not under review by any other journal, and all necessary author approvals and disclosures are included.] I am the software's developer and maintainer; the related interest is disclosed in the manuscript.

Thank you for considering our work.

Sincerely,
Mohammad Ahmadkhanloo
Institute for Research in Fundamental Sciences (IPM), Tehran, Iran
m.ahmadkhanloo@ipm.ir

## Proposed APC waiver request (for designated fee-support form, not the scientific cover letter)

I am requesting a full (100%) discretionary waiver of the article processing charge for my manuscript, “HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox,” submitted to Brain Informatics through Springer Nature's journal transfer process.

I am the corresponding author affiliated with the Institute for Research in Fundamental Sciences (IPM), Tehran, Iran. This work received no specific research grant, and I do not have funds available to pay the journal's listed EUR 940 APC. Financial constraints affecting research in Iran and difficulties in arranging international payments make the charge unaffordable. I would therefore be grateful if the journal could consider a full waiver under Springer Nature's financial-need policy.

I understand that a waiver request is assessed separately and does not affect the scientific review process. I can provide any additional information needed to assess my financial situation.

Mohammad Ahmadkhanloo
m.ahmadkhanloo@ipm.ir

## Transfer workflow and open checks
1. In the Springer Nature recommendations page, select **Brain Informatics** under **Editor's choice**, then follow consent/transfer steps. Do not use Research Square for transfer.
2. Review the destination submission populated files, title, author/affiliation, all supplementary materials and updated cover letter. Avoid a fresh standalone submission if transfer is available.
3. Confirm abstract length, keyword count, title page, Declarations, data/software statement, figures, AI disclosure, and correspondence details. Preserve historical results/limitations.
4. In Declarations / Additional Information, select the waiver/discount request option. Complete the separate formal fee-support form **within 14 days of journal submission**; retain written confirmation and waiver decision.
5. Record new submission ID, submission date, official transferred status, fee-support application status and decision here after confirmation.
6. Do not claim the manuscript has been transferred, is under external review, has a fee waiver, or has been accepted without corresponding portal/email evidence.

## Pending actual outcome (intentionally blank)
- Brain Informatics submission ID: NOT YET PROVIDED
- Transfer completion: NOT CONFIRMED
- Waiver form submitted: NOT CONFIRMED
- Waiver decision: UNKNOWN
- Editorial status: NOT SUBMITTED/UNKNOWN


## Submission preparation update (2026-10-31)
- A locally downloadable Brain Informatics submission kit has been prepared: main manuscript DOCX, optional title-page DOCX, complete S1-S6 supplementary DOCX, full bibliography, cover letter, waiver request, text-preview PDFs, instructions, and immutable source Markdown.
- The scientific source documents were checked with exact Git blob identities: manuscript `6ffa1ddd710fddb760ac1abef205868037c978a5`; appendices `8d52cfc5c2e844462046d074426d26fb110ed9bc`; bibliography `1924b681c2e636d3dad16e745b3081cd7e49d026`.
- IMPORTANT: The user-download kit does not yet embed the 6 original PNG + 6 original PDF figure binaries because the creation runtime could not download them. A cross-platform downloader verifies Git blobs against pinned main `bbf17e9cf0d14d91bf44f50e307a0be55cbede02`. **Do not mark submission materials complete until 12/12 original figure assets are retrieved and verified.**
- A publicly indexed bioRxiv preprint exists: DOI `10.64898/2026.09.22.753415`, posted 2026-09-28. This is distinct from declining Research Square's optional preprint posting; the destination portal and cover letter must accurately disclose the bioRxiv preprint.
- The journal currently offers APC EUR 940 (acceptance-date pricing), and financial-need waivers need an official form submitted within 14 days of manuscript submission. Drafting a letter or selecting the waiver checkbox alone is NOT a waiver application. No waiver outcome is known.
- No live Springer transfer/submission, no Brain Informatics submission ID, and no official waiver application have been confirmed.


## SNAPP declarations review — author-provided draft state (2026-10-31)
- Brain Informatics **DRAFT** ID `a41d238b-de46-4406-8110-3b2acbbbb4c6` (SNAPP /new/submission/); this is **not** a confirmed submitted manuscript ID.
- Manuscript and supplementary appendices appear uploaded according to user's Files screen. Figure binaries still require confirmation; the SNAPP form recommends a manuscript with all figures/tables in editable body.
- Author-entered competing interests: YES — sole author is developer/maintainer of HGFX; no other declared interests, consistent with frozen manuscript.
- Dual publication: YES because a 2026-09-28 bioRxiv preprint was posted (DOI `10.64898/2026.09.22.753415`); Springer Nature policy says preprints are *not* prior journal publication. The explanation should also mention the earlier Neuroinformatics rejection, if submission history is requested.
- Data used/generated: YES, simulated data and reproducibility artifacts; reference GitHub repository and v1.0.0 release.
- Funding: NO; authorship and third-party materials self-declarations to be confirmed by corresponding author. Acknowledgements optional and portal field overrides manuscript's acknowledgements when populated.
- **OPEN**: The supplied plain-text rendering of SNAPP Declarations contains the fee commitment clause but does **not** establish that the APC waiver-interest checkbox has been selected. Check or expand "Discounts or waivers in cases of financial hardship..." before final submission. Selecting waiver interest is not the actual fee-support application.
- Official 2026-10-16 Springer policy: https://support.springernature.com/en/support/solutions/articles/6000227580-apc-waivers-and-discounts — interest at submission, separate application link after submission / email, form within 14 days, discretionary outcome unknown.
- **Financial risk**: acceptance without full waiver or institutional coverage can trigger full APC under the SNAPP acceptance language. Do not misclassify this as an approved waiver or unconditional no-cost route.
- Before submitting, check that the cover letter names the already posted bioRxiv DOI as per Springer Nature's preprint/similarity-check guidance.


## SNAPP Review page — author-provided state (2026-10-31)
- Review page says transfer in progress, compatible with Brain Informatics. **No final submission confirmation yet**.
- Draft remains `a41d238b-de46-4406-8110-3b2acbbbb4c6`.
- The declaration **"I want to apply for an APC discount or waiver" is explicitly selected**. This records waiver interest only, NOT submitted hardship form/approved 100% waiver. Official follow-up form still needed within 14 days of actual submission.
- Reviewer Files summary shows only two scientific files: `HGFX_BrainInformatics_Manuscript.docx` and `HGFX_Supplementary_Appendices.docx`. Cover letter is separately present in Details.
- **BLOCKER: required scientific figures missing from submitted main file and from separate Figures list.** The generated `HGFX_BrainInformatics_Manuscript.docx` currently stored in the local submission kit has **0 embedded `word/media` entries, 0 inline drawings**, while the manuscript calls out six figures. The Review summary does not show any separate figure uploads. The author's actual SNAPP uploaded DOCX is named identically; absent other edits, it has the same defect. Before final Submit, recover and Git-verify all six original figures, then upload separately in correct order in SNAPP Files > Figures and tables (optional), or replace manuscript with an editable document that embeds all six. Do not alter/recreate scientific figure data.
- Cover letter in kit already contains bioRxiv preprint DOI `10.64898/2026.09.22.753415`.
- Research Square In Review preprint option is not necessary because bioRxiv preprint already exists; suggest selecting **No** to avoid duplicate preprint posting unless explicitly desired.
- Competing interests, author details, dual-publication disclosure, simulated-data statement and no-funding declaration align with manuscript. Retain all.
- Next user-facing checkpoint: Review shows six figure files and waiver-interest selection; then submit and follow official APC hardship-form link. Record final submission ID and dated receipt only on evidence.
