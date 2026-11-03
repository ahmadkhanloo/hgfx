# Source acquisition verification — 2026-11-03

This delivery performs discovery, source inspection, acquisition and planning only. No MATLAB or HGFX fitting was run. No result in the frozen scientific evidence was changed.

## Obtained

- Five candidate publications have DOI-resolved citation metadata and BibTeX. DOI content negotiation succeeded after a direct Crossref batch hit HTTP 429; this is metadata verification, not an execution result.
- SPIRL: all five Zenodo deposit files downloaded and checked against Zenodo MD5; JSON files contain 20 pilot and 59 main records. Original MATLAB analysis source archived at `86fd5122a744acfb5bc7ba12720426d8b4aa0ffa`, with GPL license and original notices. ZIP CRC validation passed. Submodule contents are not bundled.
- SPIRL article: publisher full-text HTML downloaded. Publisher/PMC PDF attempts failed; the failed PDF entry remains in the manifest.
- Arthur and Henco articles: original publisher PDFs downloaded, parsed successfully (23 and 22 pages respectively); article identities checked from first-page text. This was a read-only identity check, not a new document layout review.
- Arthur: all 128 files in the OSF Data/Code inventory downloaded locally and verified against source-provided SHA-256. Two additional model/priors DOCX supplements downloaded locally and parsed as Office XML. These external files have no verified project redistribution license and are excluded from Git.
- Henco README downloaded locally. `Patient_Study.zip` timed out; no claim is made that its dataset was acquired or that its full contents were inspected.

The primary acquisition manifest contains **138 successful asset records and two failed attempts**, including local-only files. The two Arthur supplements are recorded separately in `arthur_2023/supplement_acquisition.json`. Success means file acquisition/integrity, not scientific validity.

## Feasibility findings

- Arthur Study2 calls `tapas_hgf_binary_config_david1` and `...david2`, absent from the downloaded Data/Code inventory. Supplement text was obtained, but no exact equivalence to those absent source definitions has been established. Hard-coded local source paths need documented adaptation. Original-toolbox version remains unresolved.
- SPIRL uses custom eHGF extensions, seven joint choice/RT response models and `nRandInit=399`. The complete published workflow cannot be assumed supported by the standard HGFX1.0 API. Its old TAPAS pin differs from HGFX's frozen 8.2.0 oracle.
- Henco's paper explicitly distinguishes shareable processed outputs from restricted individual raw data. Two-stream model compatibility is not assumed.
- Pain's GitHub tree and MATLAB fit script were inspected; custom logRT response files and raw trial files exist. No root license was detected. Gao's announced OSF project returned 401, so practical data access is not verified.

## Delivery checks

- SHA-256 checked for all successful primary-manifest downloads; all 128 Arthur source hashes matched.
- Licensed source archive CRC and included LICENSE checked.
- PDF identity/page count and public JSON syntax checked.
- `local_only/` ignore rule checked; these files must not enter the staged public commit.
- Plan links verified; all scientific implementation/reference/frozen paper paths have no tracked diff.
- No software tests were rerun: this change adds reference materials and plans, not implementation behavior. Prior-turn test results are not relabeled as new results.

## Reacquisition

For any file, use the exact `url` in the relevant manifest/inventory and verify `sha256` after download. Keep the same relative destination; respect `redistribute: false`. For the SPIRL source snapshot, clone the recorded upstream repository and check out the exact commit; do not follow moving master for the comparison. The new execution addendum specifies the remaining feasibility/protocol gates.
