# HGFX v1.0.0 — version-specific software archive / DOI preflight (2026-11-15)

**Status: VERIFIED FROZEN SOURCE IDENTITY; VERSION DOI NOT VERIFIED; AUTHOR/DEPOSITOR ACTION OPEN.** This is read-only source and public-metadata due diligence. It neither mints a DOI nor uploads code, changes a Git tag, or changes the frozen scientific software baseline.

## What was independently confirmed

| Item | Source-verified observation | Meaning |
|---|---|---|
| Software tag | [Git tag `v1.0.0`](https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0) resolves to immutable commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` | Correct exact-source anchor for a software **version DOI** |
| Public GitHub Release | `v1.0.0` published 2026-09-16; release has no manually attached assets in the queried Release API | This does **not** imply GitHub's auto-generated tag source archives are absent |
| Frozen `CITATION.cff` | Title `HGFX: A GPU-Native Python Toolbox for Hierarchical Gaussian Filters`, version `1.0.0`, author `HGFX contributors`, licence MIT, repository URL; **no DOI field** | Existing source metadata is not proof of a minted DOI |
| Current `paper/references.bib` | `@software{hgfx100}` credits `HGFX developers`, has source URL and exact release commit but **no DOI** | Valid provenance citation, not a verified persistent DOI |
| Current manuscript | Sole listed author: Mohammad Ahmadkhanloo | Creator metadata mismatch with generic software citation needs **author confirmation**, not automated reassignment |
| Preprint record | Separate bioRxiv preprint DOI `10.64898/2026.09.22.753415`, verified via preprint indexing | **A paper DOI is not a software-version DOI** |

As of this check, public search did not return an attributable HGFX Zenodo software record; direct Zenodo REST record-search URLs could not be accessed from this environment. **Absence of a search hit is not evidence of DOI nonexistence.** Search status is `SOFTWARE_VERSION_DOI_NOT_VERIFIED`, **not** `DOI_DOES_NOT_EXIST`. The author's Zenodo dashboard and any existing draft/published deposits must be checked first to prevent duplicate records.

## Appropriate archival route for the old, frozen release

Official [Zenodo GitHub enable guide](https://help.zenodo.org/docs/github/enable-repository/) and [GitHub release archiving guide](https://help.zenodo.org/docs/github/archive-software/github-upload/) describe archiving **new** GitHub releases after integration is enabled. For a **pre-existing** release such as HGFX `v1.0.0`, do not assume that connecting GitHub today backfills a DOI automatically. An archived [Zenodo integration FAQ](https://github.com/zenodo/zenodo-docs-user/diffs/0?base_sha=269f85c09041de05d1587405173ca7c517a44e5a&head_user=alejandromumo&name=master&pull_number=92&qualified_name=refs%2Fheads%2Fmaster&sha1=269f85c09041de05d1587405173ca7c517a44e5&sha2=a232553c8a12064a101cf2b7e139fcad4c597e05&short_path=1e78513&unchanged=expanded&w=false) describes a manual software upload of the old release ZIP when the repository was not enabled at release time. Verify current procedures in Zenodo before acting.

**Preferred conditional plan:**

1. Author checks existing Zenodo account and public records for an exact `v1.0.0` DOI; if found, verify its archive's source SHA against `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and record DOI/URL/data hashes. Do not mint another.
2. If no exact record exists, author/depositor prepares **a new Zenodo software upload of the source archive for the already-existing tag**, not the moving `main`/development/CompStat revision tree. Capture its SHA-256; check LICENSE and `THIRD_PARTY_NOTICES.md`, release tree contents and absence of restricted/private data. Never generate a new `v1.0.0` tag or pretend a new release is the old scientific build.
3. Author verifies the correct software creator list, desired version-specific title and description, MIT license, publication date as supported by historical release, and possible preprint DOI as **related paper**, not as software identifier. `CITATION.cff` at the frozen tag says `HGFX contributors`, paper says Mohammad Ahmadkhanloo; do not invent author ordering, ORCIDs or institutional permissions.
4. Author/depositor submits/publishes the software archival record via Zenodo's account workflow and records the **version DOI** (not just a concept/all-versions DOI) and machine-readable metadata. Preserve exact archive hashes and any external evidence archive DOI separately; a GitHub Actions preview artifact is not a persistent public archival record.
5. Only **after** the real DOI resolves to the exact released code, update the active branch's `paper/references.bib`, main Data/Code Availability, ESM and `CITATION.cff` as appropriate. Keep the original release tag immutable. Re-run strict claim audit + real-source PDF and get the author to reapprove the exact revised article for D2.
6. If authentic archival rights/creators/metadata or deposits cannot be confirmed, mark the DOI step `HUMAN_ACTION_BLOCKED`; do not fill a speculative identifier or delay claims by asserting an unverified archive exists.

## Current disposition

- **DONE / VERIFIED:** Git tag and software source commit identity; existing MIT licence and reference notices read; paper-preprint identifier is distinct; public software metadata lacks a DOI field.
- **NOT VERIFIED:** published version-specific software DOI; exact Zenodo archive and content hashes; ownership of any pending Zenodo deposit.
- **HUMAN ACTION OPEN:** account check, software creator/affiliation/ORCID and metadata approval, version archive upload/publication, final DOI verification.
- **BLOCKED:** REV-4.1 version DOI and DOI-backed citation updates; author D2/D3 and actual journal submission remain independent gates.

The publication-first instruction prioritizes an accurate, **version-specific software citation**; this is a rights and reproducibility requirement, not a mandate to change software features or repeat the frozen scientific experiments.
