# arXiv reader-facing version

This directory contains the reader-facing arXiv preprint derived from the locked HGFX paper evidence.

Scientific data, thresholds, seeds, datasets, model families, optimizers, and frozen classifications are unchanged. The arXiv layer changes presentation only:

- quantitative values are shown directly whenever possible;
- predeclared criteria are drawn as reference lines rather than encoded as PASS/FAIL labels;
- negative results use neutral scientific language;
- internal workflow identifiers and detailed provenance remain in Supplementary Appendix S6 / the reproducibility package;
- canonical journal figures under `paper/figures/` remain historical evidence and are not replaced by the arXiv presentation layer.

## Canonical arXiv sources

- `manuscript.md` — reader-facing manuscript
- `figures/*.pdf` — the three canonical vector figures used in the final preprint
- `build_submission.py` — deterministic PDF/source-bundle builder
- `paper/references.bib` — bibliography
- `paper/SUPPLEMENTARY_APPENDICES.md` — S1–S6

The reader figures are generated from committed machine-readable evidence with:

```bash
python paper/scripts/generate_arxiv_reader_figures.py
```

Only vector PDF copies are retained in `paper/arxiv/figures/`; redundant PNG copies are intentionally omitted.

The submission package is built and smoke-tested by `.github/workflows/arxiv-package.yml`. A freeze commit whose message contains `[freeze-arxiv]` stores an immutable PDF, source ZIP, manifest, and SHA-256 checksums under `paper/arxiv/frozen/<freeze-id>/`.

Frozen submission files must not be edited in place. A future revision must use a new freeze ID.
## Current frozen submission

`2026-09-18-r1` is superseded and must not be submitted. The current submission candidate is `2026-09-18-r2`, built from the final reader-facing manuscript and the revised-preprint visualization language. It contains three main figures: parameter recovery, trial-horizon diagnostics, and the pyhgf common-scope trajectory comparison. The standalone MATLAB sensitivity figure and standalone GPU figure are intentionally not part of the main paper.

