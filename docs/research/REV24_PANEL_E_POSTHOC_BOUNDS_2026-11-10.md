# REV-2.4 / Panel E — posthoc endpoint objective-gap bounds (2026-11-10)

**Status:** reproduced analytical bounds from **original archived fit objective values** and the **already executed** paired Panel E same-vector gaps; **NO NEW MATLAB/HGFX OBJECTIVE EXECUTION**, NO new sample/seed/threshold, and NO scientific acceptance change.

## Evidence and validation

- Original paired Panel E run [42786519173](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786519173), audited [sanitized artifact 13749028134](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786519173/artifacts/13749028134); immutable `panel_e_comparison.json` SHA-256 `051aea43a11f7788b85d64a9cb8e82a59a274a70aa347f1927920d991a8ce86d`.
- Original historical D08 artifact `10339403480`, whole-ZIP SHA-256 `c7bbc4f8b5ed9ae62b4f340e13297689112801af11683f4ac4cfae6490f3b3de`. Original historical 64-fit artifact `13341288055`, whole-ZIP SHA-256 `45d3ae8c52f335b85af7d63bc9600596eb398d40f36996e5adaf9b0e3d938587`; the original two raw cohort JSONs are verified against their frozen SHA-256 in `tools/compstat_rev24_endpoint_sources.py`.
- Pure posthoc arithmetic and source-identity tool: [`tools/compstat_rev24_endpoint_gap_bounds.py`](../../tools/compstat_rev24_endpoint_gap_bounds.py) and [six synthetic contracts](../../tests/paper/test_compstat_rev24_endpoint_gap_bounds.py). **Actual GitHub Actions run [42787522512](https://github.com/ahmadkhanloo/hgfx/actions/runs/42787522512) `success`**, six synthetic tests PASS, SHA checks for frozen original data and Panel E summary PASS. No MATLAB or HGFX code import and NO new numerical objective evaluation.
- Published sanitized [artifact 13749878975](https://github.com/ahmadkhanloo/hgfx/actions/runs/42787522512/artifacts/13749878975), ZIP SHA-256 `faeae69aefffa00be28dbeade9371c5e0df85c784d64ff8d2961640d4ca09c4c`, member `endpoint_gap_bounds.json` SHA-256 `e0dae861801721d33e2f219c73fcc8694621968d028befc198baa483faab9caf`. The source raw endpoint vectors, trial data and private per-trial likelihoods were **not** uploaded.

## Mathematical scope (triangle inequality, not a fitted inference test)

For two *historical fitted final vectors* `x_M` (MATLAB fit) and `x_H` (HGFX fit), let `a=M(x_M)` and `b=H(x_H)` denote the **original archived own-implementation negative log joint** and let `d_M=|M(x_M)-H(x_M)|`, `d_H=|M(x_H)-H(x_H)|` be the **already executed** same-vector absolute gaps of the Panel E report. Writing `g=|a-b|`, the endpoint-to-endpoint objective gap in the MATLAB implementation obeys `max(0,g-d_H) ≤ |M(x_M)-M(x_H)| ≤ g+d_H`; in HGFX it obeys `max(0,g-d_M) ≤ |H(x_M)-H(x_H)| ≤ g+d_M`. This is a deterministic bound on **recorded floating-point values**, not a new numerical acceptance threshold, and not an additional original paired objective run.

## Findings

| Original source | Archived cross-fit `negLj` gap | Derived bound |
| --- | ---: | --- |
| D08, `uhgf+gaussian_obs` | `3.979039320256561e-10` | Both numerical gap bounds coincide at this archived precision; no family-specific objective acceptance gate |
| 64-subject HGF cohort, maximum (subject 47 zero-based) | `3.4023628359136637e-10` | Maximum MATLAB upper bound `3.402504944460816e-10`; maximum HGFX upper bound `3.4023628359136637e-10` |
| 64-subject HGF cohort, median archived own-fit gap | `1.2079226507921703e-13` | Descriptive median only, not acceptance |
| Original subject 7 | `1.0865619515243452e-10` | MATLAB upper `1.0865619515243452e-10`; HGFX upper `1.0867040600714972e-10` |

All 64 archived own-fit endpoint objective records were accounted for and all 128 previously paired HGF same-vector endpoint statuses were verified as valid before deriving bounds. The original D02 HGFX fitted endpoint is **still missing**; no D02 endpoint-gap bound was invented.

**Interpretation constraint:** very small objective differences can coexist with materially different fitted parameter vectors, sensitivity to local optimizer paths, and historical trajectory/Hessian/covariance failures. No conclusion about optimization-path equivalence, identifiability, scientific interchangeability, restored 64/64 gate or accepted eHGF/uHGF family-specific objective parity follows from these bounds. Original M18/P3/63-of-64/PERF-01C failures remain unchanged.

## Open decision gates

- Locate an independently verifiable original D02 HGFX full transformed 15-vector (if it exists) without constructing it from partial evidence.
- Diagnose Panel G `REV24-G-ehgf_binary-019` first **causal** state divergence using existing data or a separately authorized prospective diagnostic protocol; retain the historical failure.
- Seek previously registered eHGF/uHGF objective thresholds or keep `NO_PREDECLARED_FAMILY_OBJECTIVE_GATE`; no retrospective threshold creation.
- Independent scientific review and publication claim mapping before D2; author D3 and release claims remain blocked.

**REV-2.4 is still `IN PROGRESS / NOT_GLOBAL_PASS`**. The objective-data evidence is stronger, but nothing in this report closes fitting equivalence or scientific inferential compatibility.
