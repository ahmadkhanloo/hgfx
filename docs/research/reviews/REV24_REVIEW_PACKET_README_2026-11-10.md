# REV-2.4 — Independent-review evidence packet (2026-11-10)

**Purpose:** offline transfer to an independent scientific reviewer whose GitHub access is rate-limited. This packet does **not** certify scientific parity. The correct prior status is **`BLOCK_GLOBAL_PARITY`**; a restricted `ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY` remains conditional on the reviewer's independent SHA/source check.

**Repository:** `ahmadkhanloo/hgfx`, PR #107, branch `compstat-revision`, pinned working evidence HEAD `75a34897c84ee746feb96a874e0f2ac52789b93f` (the historical report/source state reviewed). The packet workflow itself is a later, packaging-only commit. [Issue #108](https://github.com/ahmadkhanloo/hgfx/issues/108).

## Files and confidentiality

- `evidence/panel_g_original_artifact.zip`: **complete original synthetic** 600-case numerical evidence, including identical frozen input vectors, 600-row independent HGFX and MATLAB output files, and the independent comparison. This is NOT real participant data.
- `evidence/panel_e_sanitized_artifact.zip`: SHA-pinned original Panel E **sanitized** 66-case / 132-endpoint comparison; source identifiers, objective differences and classifications, not 64-participant original input arrays, fitted vectors or per-trial raw likelihoods.
- `evidence/panel_e_posthoc_bounds_artifact.zip`: audited bounded original fit endpoint gaps, derived without extra scientific evaluation.
- `repo/`: original protocol, method, source code of Python/MATLAB evaluators, unit tests, workflows, planning ledger, historical report and original run kickoff documents **as of the pinned evidence HEAD**. Do not use later development branch code as if it were HGFX v1.0.0.
- `metadata/run_provenance.json`: original run IDs and source/commit/hash metadata. `SHA256SUMS.txt`: hashes of all included reviewed files. `verify_reviewer_packet.py`: independent Python-stdlib-only integrity/numeric-count audit (never re-evaluates HGF objectives).
- `REVIEW_RESPONSE_TEMPLATE.md`: reviewer report with separate source verified vs not verified statuses. **Only the reviewer must fill the findings**, sign with their own identity, and commit a final record. The conditional review already supplied in the chat is NOT a completed verified record.

### What is **not** supplied

The original D02, D08 and 64-subject raw archival ZIP files (artifacts 10339454535, 10339403480, 13341288055) and their trial-level data/final parameter vectors are **intentionally excluded**. The original Panel E private raw MATLAB/HGFX per-trial outputs were deleted by the executing CI workflow. This is an explicit evidence/auditability limitation, not a licensing issue or a scientific PASS. An authorized reviewer may separately receive the original historical source archives via a controlled channel, subject to the data provider's permissions. Their whole-archive SHA-256 and GitHub artifact identifiers are included in the protocol and source-checker files; no new endpoints or source data may be reconstructed from guesses.

## Offline review workflow

1. Unzip to a clean directory. Verify every included file using `sha256sum -c SHA256SUMS.txt` (Linux/macOS) or `python3 verify_reviewer_packet.py` (Python 3.11+). The script also re-counts original paired case classifications without running MATLAB, HGFX, fitting or inference.
2. Read `repo/evidence/revision/protocols/REV-2.4_PROTOCOL.md`, frozen before the science runs, and `repo/docs/research/REV24_PANEL_G_ORIGINAL_RESULT_2026-11-10.md` plus the Panel E and posthoc reports. Check script versions and independent source identities against `repo/tools/` and `repo/reference/matlab/`. For original V1.0.0/HGF reference implementation checks, request frozen source from the public upstream commits, not branch development code.
3. Explicitly record if you could independently establish the **real GitHub push chronology**. A Git commit's author/committer timestamp alone is **not** tamper-proof. Git ancestry from the preregistration commit to the executing SHA can establish content presence at run HEAD but not all server-side timing.
4. For HGF objective-only scope, verify 164 original both-valid / within M8 in Panel G and 128 original matched endpoint objective comparisons in Panel E. Retain **36 jointly invalid HGF**; **39 jointly invalid across all Panel G families**, one **one-sided invalid** eHGF case `REV24-G-ehgf_binary-019`, and the **missing D02 original HGFX endpoint**. Do not call a shared-invalid case a numerical pass.
5. Explicitly do **not** infer optimizer/parameter/Hessian/trajectory/inferential parity. Original subject-7 and historical 63/64 fit NONPASS stay unchanged. eHGF/uHGF have no located predeclared family objective gates; D08 uses **continuous `uhgf+gaussian_obs`**, not binary `uhgf_binary`.
6. If the raw Panel E historical archives or source audit cannot be independently obtained, classify that check as **NOT_VERIFIED** and explain precisely what this prevents, even though the publicly available, sanitized comparator passes its own integrity check. An open source hash is a commitment, not a substitute for the underlying data.
7. Fill `REVIEW_RESPONSE_TEMPLATE.md`. A defensible final verdict may be `BLOCK_GLOBAL_PARITY` with `ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY` under a specified evidence scope; eHGF case 019 is `UNEXPLAINED_ONE_SIDED_INVALID` pending causal state evidence, not a demonstrated scientific model limitation.

## Returning the review

The reviewer should author an immutable report named `docs/research/reviews/REV24_INDEPENDENT_REVIEW_2026-11-10.md` **on a new reviewer branch**, citing the exact reviewed commit/head, packet hash, archives and checks that actually ran. Commit and push if authorized; optionally open a separate PR against `compstat-revision`. Report the branch URL, commit SHA, report URL, reviewer identity, and any issue/PR comment links. If no GitHub write access exists, return the *completed Markdown file* to the user, who can submit it unmodified with the reviewer's authorship and evidence caveats preserved.

**Do not:** re-run any original Panel G/E numerical experiment without new prospective authorization, relax frozen thresholds, change model families, re-fit the missing D02 endpoint, drop invalid rows, or claim a full scientific gate PASS. D2/D3 submission/release claims remain BLOCKED.
