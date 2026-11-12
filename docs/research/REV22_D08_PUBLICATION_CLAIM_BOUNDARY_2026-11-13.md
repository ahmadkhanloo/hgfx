# REV-2.2 D08 — bounded publication claims and evidence exclusions (2026-11-13)

**Status:** PRE-D2 EDITORIAL EVIDENCE NOTE, NOT an accepted manuscript claim, scientific PASS, independent review, or permission to execute a new experiment. Target remains *Computational Statistics* (D1=A). PR #107 stays DRAFT; D2/D3 BLOCKED.

## Scope and exact observations

Original official D08 uses the authentic HGF Toolbox 8.2.0 reference and published HGFX 1.0.0 wheel, original 614 USD/CHF inputs with seed 123456789 simulated responses, and the exact `uhgf + gaussian_obs` continuous model (not a binary-uHGF substitute). The full source, configuration and provenance are in [original D08 report](REV22_D08_ORACLE_ORIGINAL_RESULT_2026-11-11.md), [original evidence](../../evidence/revision/rev22_d08_official_paired_summary_2026-11-11.json), and [Issue #111](https://github.com/ahmadkhanloo/hgfx/issues/111).

Two workflows were inadvertently launched concurrently, contrary to the single-invocation protocol. Their retained immutable evidence must be presented as *two protocol-deviating executions*, not as a preregistered repeatability study:

| Observation | Run A, Actions 42910756224 | Run B, Actions 42910835710 |
| --- | --- | --- |
| Immutable artifact | 13808150860 | 13808625206 |
| Direct fields satisfying existing appropriate gates | 24/25 | 24/25 |
| Finite `traj.epsi` coordinates outside original gate | 4/1228 | 3/1228 |
| First failed index (zero-based trial, level) | (178,1) | (178,1) |
| Other failed trial indices | 322, 412, 577 | 412, 577 |
| Interpretation | UNRESOLVED_DISCREPANCY | UNRESOLVED_DISCREPANCY |

Both workflows report the same authentic MATLAB reference JSON SHA256 `5546a6cbd51d780d7d0886bcd14de982d0b970bda857752a2d37344975d5f165`, exact same archived responses and released wheel; both actually resolved JAX 0.10.2. The HGFX transformed endpoints differ by a maximum absolute `5.716338513650498e-10`. Neither run demonstrates complete direct fitting parity. Success of the workflow itself is not scientific acceptance.

At the *same* archived MATLAB endpoint, the reported aggregate negative log likelihood and negative log joint match exactly at exported precision. They also agree at the Run A endpoint at exported precision and differ by about `4.55e-13` at the Run B endpoint. These are descriptive same-vector observations **without a preregistered uHGF-family objective gate**; they do not establish optimizer trajectory equivalence, convergence, identifiability, or family-wide parity.

## Why historical gradient evidence does not resolve the official released-wheel discrepancy

The [official-seed historical archive audit](REV22_OFFICIAL_D08_RIDDERS_ARMIJO_SOURCE_AUDIT_2026-11-11.md) authenticated old source-selected Ridders/Armijo observations (including 22/22 objective samples and 17/17 Armijo samples matching for their selected states). But the actual historical probing used an **editable development checkout**, not the published HGFX 1.0.0 wheel. The [historical-to-release source lineage](REV22_OFFICIAL_D08_HISTORICAL_TO_RELEASE_SOURCE_LINEAGE_2026-11-11.md) identifies source-identical optimizer core files **and** genuine changes on the reachable continuous forward exponential path before release. The selected historical observations therefore cannot certify a first causal BFGS/gradient split for either published-wheel A/B run. The holdout seed 314159265 has different simulated responses and cannot supply that missing proof.

The exact numerical cause of the A/B difference remains unknown: do **not** label it CPU/BLAS scheduling, optimizer instability, an HGFX implementation defect, or a scientific identifiability limitation as an established finding. The original M18 D08 FAIL, original 63/64 full-cohort trajectory NONPASS, and all published v1.0.0 evidence remain intact.

## Suggested manuscript-safe wording (subject to D2/author review)

> In the continuous uHGF USD/CHF fitting example, HGFX and MATLAB returned closely agreeing aggregate objective values when evaluated at identical fitted parameter vectors. Nevertheless, the two archived HGFX fitting executions, launched concurrently in deviation from the planned single-run protocol, each failed the pre-existing numerical acceptance criterion for a small number of finite predicted-precision trajectory entries (4/1228 and 3/1228). We therefore do not claim full fit-level equivalence or independently confirmed numerical reproducibility for this example. The first causal optimizer or forward-computation divergence in the released implementation has not been established.

This wording is **proposed, not yet incorporated into manuscript**. A separate explanation of the convergence/termination field must not claim a successful stop: the published source does not export the termination reason. The original `lastwarn` capture is not exhaustive Ridders warning classification.

## Decisions and next bounded actions

1. **No new D08 fit** under exhausted REV-2.2 protocol. Preserve both original artifacts, including the protocol deviation and all failed coordinates.
2. **Independent read-only audit** (if not already complete) may check archived source lineage, provenance, and draft wording; do not imply source audit establishes optimizer causality. A new numerical protocol would require distinct preregistration, independent scientific review, and explicit author approval before execution.
3. Continue remaining manuscript readiness tasks with explicit statuses: REV-2.1 design choice Issue #110 BLOCKED; REV-2.4 global parity Issue #108 NOT_GLOBAL_PASS; REV-2.2 warning coverage and causal attribution OPEN; D2/D3 BLOCKED. Do not convert descriptive same-vector equality into a family PASS.
4. At D2, obtain human authorization for the precise claim scope. Only after D2 may REV-3 rewrite title/abstract/manuscript around supported results; do not silently treat this note as D2 approval.

**No new model, MATLAB, optimizer, fitting, or numerical experiment is performed by this document.** This document adds editorial traceability, not validation evidence.
