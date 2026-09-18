# arXiv reader-facing version

This directory contains a reader-facing preprint derivative of the locked journal manuscript.

Scientific data, thresholds, seeds, datasets, model families, optimizers, and frozen classifications are unchanged. The arXiv layer changes presentation only:

- quantitative values are shown directly whenever possible;
- predeclared criteria are drawn as reference lines rather than encoded as PASS/FAIL labels;
- negative results use neutral scientific language such as "criterion not met", "outside the predeclared target", or "insufficient evidence";
- internal case IDs, workflow-run IDs, commit hashes, and checksums are kept out of the main narrative and remain available in Supplementary Appendix S6 / the reproducibility package;
- canonical frozen paper figures under `paper/figures/` are not modified.

Regenerate reader-facing figures with:

```bash
python paper/scripts/generate_arxiv_reader_figures.py
```

Outputs are written to `paper/arxiv/figures/` as 300-dpi PNG and vector PDF files.
