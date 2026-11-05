# Editorial integration candidate: published-input forward compatibility

**Status: VERIFIED NUMERICAL EVIDENCE / MANUSCRIPT INTEGRATION PENDING.** This file is a stand-alone section proposal; the current `manuscript.md`, claim ledger and frozen PDF/source ZIP have **not** been regenerated or changed. Verify against the exact [executed evidence](../case_studies/REALDATA_FORWARD_PARITY_RESULT_2026-11-04.md) before inclusion. Original papers' model fitting and published findings remain unsupported.

## Candidate Methods paragraph (English)

To examine whether HGFX's previously validated fixed-parameter perceptual calculations also agree with MATLAB on independently collected behavioral inputs, we selected two publicly archived datasets before comparison: two 80-trial learning blocks per participant from Suthaharan et al. (2021) and Reed et al. (2020). Source archives and exact Git commits were pinned and SHA-256 verified. A source-inventory discrepancy in Reed's MATLAB workspace was recorded as a failed pre-execution gate and resolved in a separate protocol revision, establishing 130 and 32 available participant prefixes, respectively. All 324 source-defined blocks (25,920 input trials) were retained, including missing-response masks. With the same native 17-parameter vector frozen in our earlier M12B reference test, we evaluated the `hgf_ar1_binary_mab` perceptual recurrence on MATLAB HGF Toolbox 8.2.0 and the released HGFX 1.0.0 Python package using CPU float64. We compared all corresponding inference-state and trajectory fields under the unchanged M12B criteria (`rtol = 2e-9`, `atol = 2e-11`), preserving nonfinite-value semantics. This evaluation did not refit participant parameters or implement the original studies' observation models.

## Candidate Results paragraph (English)

All 324 MATLAB runs completed, and HGFX reproduced the corresponding 12 state or trajectory outputs per block within the prespecified numerical criteria. Across 3,888 compared fields and 2,540,160 numerical elements, none exceeded the tolerance; the maximum absolute difference was `3.1086244689504383 × 10^-15`. Forty-eight HGFX runs produced runtime warnings, retained in the audit; their numerical significance and mechanisms require separate review. This result provides a real published-input test of fixed-parameter implementation compatibility. It does not reproduce the studies' fitted parameter estimates, model comparisons, group-level effects or substantive conclusions, and it does not demonstrate improved accuracy, speed or parameter identifiability relative to MATLAB.

## Proposed limitations sentence (English)

The two published datasets were used only as independent input sources for a common fixed-parameter perceptual model, not as complete replication targets; historical HGF releases, original observation likelihoods, optimization configurations and published inferential analyses were not reproduced.

## Editorial gates still open

- Verify publisher citations and exact APA/author-year bibliography keys for both papers.
- Verify warning categories for the 48 cases.
- Cite full protocol history and stable GitHub Actions run #41809919116 in the machine-readable claim ledger; distinguish this prospective new evaluation from original frozen v1.0.0 evidence.
- Incorporate only after scientific author review, then rebuild and verify editable source and rendered PDFs, manifests, figures and claim ledger.
- Retain the previous frozen manuscript and failed/incomplete P3 scientific evidence without alteration.
