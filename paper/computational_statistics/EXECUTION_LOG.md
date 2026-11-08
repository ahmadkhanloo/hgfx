# Execution log - 2026-11-04

Scope: execute the Pain handoff P1-P5 and J1-J6, conditional on its scientific gates. No submission, email, preprint upload, or financial commitment is authorized.

## Baseline

- Branch: `paper/computational-statistics-revision`; starting HEAD and origin/main: `1a122985b30a352637132160369c3732aedf407b`.
- Pre-existing changes: `.gitignore`, `.freebuff/`, `.repowise/`; excluded from this work.
- Read AGENTS.md and its eight required documents, the Pain handoff, published-case addendum and parent publication plan.
- Protected 75 tracked historical files in `baseline_hashes.json` before authoring. No historical results will be recomputed.
- `.venv/Scripts/python.exe scripts/verify_reference_freeze.py`: PASS, 334 MATLAB files; oracle 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Local Python: 3.12.14; JAX 0.11.1. MATLAB R2025b executable exists; this does not resolve the original Pain environment.
- Pain checkout pinned to `3f1d32aff73826a1385c359ca638ad0e11a7fda7` in ignored local_only; SPIRL archive CRC passed and extracted there.

## Evidence and execution boundary

Source inventory is read-only. A failed feasibility gate stops fitting, not independent editorial preparation. Protocols for blocked studies are gate records, not preregistrations of an executed replication. Agent source checks are not human verification.

## P1-P2 source feasibility: completed, terminal blocks recorded

- `git clone`, detached checkout and clean-source verification succeeded for Pain; 504 files hashed. All five named participant/questionnaire files are present. Case-sensitive task inventory: 52 folders, each one 192-trial task; c01 excludes two. This is a source inventory, not a reconciled final eligible sample.
- `audit_case_sources.py` records 38 external MATLAB symbols, exact oracle candidates, absent helper and declared-name mismatches. Root code license is absent; per-file GPL simulation notices exist. Main likelihood/config permission and original environment remain unresolved.
- Pain decision: BLOCKED_UNLICENSED_CUSTOM_RESPONSE_AND_UNRESOLVED_ENVIRONMENT. SPIRL fallback: BLOCKED_CUSTOM_JOINT_MODELS_REQUIRE_NEW_MIGRATION; custom eHGF, seven combined models and 399 random starts verified.
- No upstream source translated/copied into core; no source/data force-added. No mathematical migration, no new Migration Matrix completion status. Relevant existing surfaces are C01/C04, binary HGF families and observation semantics; documentation/plotting does not create a new mathematical component.
- Pain P3 is a blocked gate record committed at f716eec, not a complete runnable protocol. P4 and case-result P5 are NOT RUN. No numbered published scientific result or participant comparison figure is invented.

## Independent synthetic workflow: completed

- Before execution, committed selection of existing quickstart vectors and release-default fit at f716eec. No recovery or associations.
- Fresh Python 3.12.10 venv outside checkout. Primary PyPI file-host DNS failed; Tsinghua mirror supplied wheel bytes matching official PyPI SHA-256 5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90. Dependencies installed offline from cache into the isolated venv; exact lock retained.
- External-cwd `worked_example/run.py --output .../result.json`: PASS_WORKFLOW_ONLY, hgfx 1.0.0, JAX 0.11.1, CPU:0, x64 true, 24 synthetic trials. Finite LME/BIC and arrays are recorded. This is not MATLAB parity or a real-data replication.
- Public API aliases inspected in the installed wheel; api_contract.json records its module hash and exports.

## J1-J6 independent preparation: completed to author-review boundary

- Rechecked official journal scope, author instructions and publishing options. Subscription selected; comprehensive mandatory fee/institutional clearance OPEN. No waiver assumed, no journal metrics/quartile invented.
- Opened publisher records for two 2024-online/2025-volume software articles and read complete arXiv author versions. Version-of-record text is behind subscription; that difference is explicit.
- Rewrote manuscript across Introduction, formulation, workflow, evaluation, results, discussion and declarations. Abstract 203 words; full source approximately 5500 words including tables. Original scientific results retained with their limitations.
- Created paragraph claim ledger with hashes/locators and human approval PENDING. DOI content negotiation opened metadata for inherited scientific DOI references and both case-study papers. Non-DOI software entries retain source URLs; human bibliographic verification pending.
- Figures: new conceptual workflow, independent agreement/accuracy panels, grayscale paired recovery and all-trial pyhgf residual. Horizon/backend figures retain exact historical bytes. No fitting, smoothing, resampling or changed threshold.
- Independent read-only agent review corrected P3 free-index scope, Pain per-file licenses, exact tapas_sgm mapping, filename/declaration mismatches, rounded supplement labels, NDC diagnostics and consumed-input build hashes. All corrections incorporated; this is not human verification.
- Official Springer class download returned 403. Generic Pandoc article source is explicitly labeled author-review layout. Initial MiKTeX build lacked fancyvrb; disabling optional syntax highlighting resolved the dependency without changing manuscript content. Failed build log retained.
- Built main/supplement PDFs, editable flat LaTeX/BibTeX/figure archive, cover letter (298 words), policy/venue dossier, preprint change summary and notices. Official bioRxiv API reports v1 posted 2026-09-28; exact posted PDF identity and authenticated revision preflight remain open. No upload.

## Verification

- Tests written before source-inventory and agreement figure implementation: initial two failures confirmed missing implementation; then passed. Expanded figure/caption and all-trial residual checks plus existing paper-figure checks: 5 passed.
- Candidate builder verifies rendered reference tokens/title/failure text and records all consumed text, figure PDF and CSL hashes. Flat source ZIP CRC checked.
- PDFs rendered with Poppler and visually reviewed at page and figure level. Corrected duplicate/detached captions, broken compact tables and reference-entry splitting. The table-preservation fix is applied after Markdown conversion so table syntax cannot leak into the PDF. No overfull boxes remain; underfull compact-table box warnings are retained and visual inspection shows no clipping. Fonts are embedded; generic layout is not journal formatting certification.
- Final `verify_revision.py` verifies 75 unchanged protected files, every paragraph/source digest, citation keys, abstract length, output hashes, figure hashes and external smoke identity. Status is local artifact checks only; author verification and zero-fee clearance stay open.

## Delivery

The complete locally executable package is prepared. External real-data replication is blocked under the plan's terminal gates; this is not scientific case-study completion. No journal submission, preprint upload, email, recovery rerun, threshold change, core model change or financial commitment occurred. Only mission files are staged; pre-existing .gitignore/.freebuff/.repowise changes remain untouched. Git delivery is on paper/computational-statistics-revision; final SHA and remote verification are reported in the handoff.


## Checkout portability correction

Post-push inspection found the repository's existing /paper/** eol=lf rule converted local CRLF text, invalidating raw-byte verification in a fresh checkout. Mission-owned text writers now emit LF. The original raw baseline hashes remain recorded; an additional files_lf inventory verifies canonical text content and exact binary bytes. All historical local files were checked against Git after newline normalization; no scientific content difference exists and none was rewritten. Ledger and figure input hashes explicitly use LF text and exact binary hashes. A regression check distinguishes line-ending portability from actual value changes and binary-byte changes. Final local suite: 6 passed. A canonical Git-archive checkout verification is performed before the corrective push.

Canonical checkout result: PASS_CANONICAL_CHECKOUT. `git archive` of 0433501 plus the pinned oracle was extracted outside the working tree and verify_revision.py passed all 75 protected identities, 74 claim rows and package/figure checks. Main and supplement layout-text extraction is identical before/after the LF correction. Details: checkout_verification.json.

## Critique-resolution execution, 4 November 2026

Protocol committed as a25690a before the new empirical fit. Original P3 shard
archives and the S7 aggregate were reacquired using public artifact downloads;
archive digests were verified. No recovery fit was rerun. The diagnostic audit
corrects the interpretation of empty selections and failed-output index vectors
without changing historical gates. A regression test distinguishes absent,
conflicting and matching winners. The empirical released-wheel run used all 614
USD/CHF observations outside the checkout and completed in 182.001 seconds.
Ridders invalid-subtraction warnings were visible; finite outputs are not a
convergence certificate. No optimizer/priors/thresholds/core implementation changed.
Author declarations were confirmed in the conversation. See the critique response
for remaining scope limitations; no external communication or submission occurred.

## Published-input evidence integrated, 8 November 2026

The revision begins at paper branch commit `e059e80d3804c02dc3ca152e96158e31ea79c4f1`.
It integrates the previously executed 324-block comparison into the abstract,
Methods 4.6, Results 5.5, Discussion and Supplement S7. Two publisher-verified
references and the archived numerical summary support the new text. The original
aggregate ZIP was retrieved through the connected GitHub app and rehashed.
All 324 unique status records and the 48 warning records were counted directly.
The summary contains aggregate and block-status information. Observed input
values and trialwise posterior arrays are absent from that artifact.

A separate paragraph reports the 63/64 full-fit diagnostic from run 41863441006.
Its complete comparison JSON was copied byte-for-byte from the immutable
research commit, with the original eight trajectory failures retained.
The paper's standard HGF fitting and MAB Forward experiments remain distinct.

The publication strategy focuses the article on reference-compatible statistical
software, published-input Forward validation, existing recovery experiments and
a descriptive empirical example. The prospective MATLAB/HGFX speed benchmark
remains a separate research gate. Article acceptance is an editorial decision.
Final scientific author approval, warning review, source-data reuse review and
the recorded financial/portal clearance remain open.

The first PDF build attempt was stopped before execution because the automatic
approval reviewer reached its usage limit. Following the request to continue,
the local build ran. Later checks and visual inspection are recorded in
VISUAL_QA.md and verification.json.

## Linux CI portability correction

The first PR #106 integrity job (run 42500192492) stopped on the newly cited
YAML workflow source. Its Git blob was LF and the Windows worktree was CRLF.
The verifier's text-extension list omitted YAML, so the claim ledger recorded
the checkout bytes. A regression test first reproduced that difference. The
existing text-hash policy now includes .yml and .yaml, while ZIP/PDF bytes stay
exact. Scientific sources, fixture bytes and thresholds were untouched.
