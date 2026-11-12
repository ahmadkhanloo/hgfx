# Computational Statistics — publication-readiness and claim disposition (2026-11-12)

**Status: AUTHOR-REVIEW DRAFT; NOT A SUBMISSION / NOT A SCIENTIFIC PASS.**
**Decision authority:** latest explicit author instruction: prioritize an honest, publishable scientific software article, with no positive or negative presumption about speed. Historical REV-2.3/PERF-01C and REV-2.4 gates remain unchanged. This file is an **editorial tracking record**, not a new retrospective protocol, acceptance threshold, author D2 approval, or experiment authorization.

## Why this journal is a plausible target

- Official [Computational Statistics aims and scope](https://link.springer.com/journal/180/aims-and-scope) (checked 2026-11-12) **explicitly accepts software articles and package reports**, with emphasis on the interaction of computing and statistics, and on analysis of complex datasets. An HGFX software-validation paper **can be in scope** if it demonstrates a useful and defensible statistical-computing contribution. Venue scope does **not** ensure peer review or acceptance.
- Official [author instructions](https://link.springer.com/journal/180/submission-guidelines) (checked 2026-11-12): **150–250-word abstract**, **4–6 keywords**, editable source manuscripts, with LaTeX recommended and Word accepted; abstract should not rely on undefined abbreviations. Required statements/declarations and code/data availability need verified facts. Current Markdown draft is not the required submission source bundle.
- Official [publication choices](https://link.springer.com/journal/180/how-to-publish-with-us): the **subscription publishing option has no APC**; voluntary open access has an APC. This is a publisher-specific statement about APC only, not an author-specific guarantee against all possible charges, licensing conflicts or funder mandates. No mandatory APC is evident for the subscription choice.
- Springer Nature [code policy](https://www.springernature.com/gp/open-science/code-policy): a Code Availability statement and persistent identifier for deposited code are strongly encouraged/required as appropriate. GitHub link alone does not substitute for a permanent identifier. Exact software release DOI/archive is **NOT YET VERIFIED**.

## Evidence-first hierarchy for the paper

| Scientific or engineering claim | Original evidence and current disposition | Article action |
| --- | --- | --- |
| Core workflow reproduction / covered official demonstrations | Archived released-1.0.0 MATLAB paired oracle source; existing release-specific gates | Retain only exact documented models, inputs, precision and workflow scopes |
| Fixed-vector classic-HGF objective agreement | Original Panel G: 164/200 both-valid within old M8 objective gate; 36/200 both-invalid. Panel E: 128/128 historic classic-HGF endpoint evaluations within original M8 criterion | **Promote to reader-facing original scientific evidence** with denominators; never call 200/200 or global fitting parity |
| Fixed-vector enhanced/unbounded HGF | Panel G 198/200 both-valid per family; no preregistered family-specific objective criterion; one released-1.0.0 enhanced-HGF one-sided invalid. Panel E enhanced stress endpoint missing, unbounded original endpoints not gated | Describe the raw observations and missingness; **NO FAMILY PARITY PASS** |
| Historical fit endpoints vs independently optimized inference | D02 and D08 holdout show limited start sensitivity; original USD/CHF official seed differs, and its two accidentally concurrent original released-Wheel runs have `traj.epsi` failures 4/1228 and 3/1228 | **UNRESOLVED DISCREPANCY** for official D08; not a general reference-limitation, optimizer-cause, or model-identifiability claim |
| Paired model selection | Independent frozen S7 comparison: 36/36 BIC winner agreement, generating-model recovery balanced accuracy 0.583 and parameter-recovery failures | Keep cross-implementation *agreement* separate from identifying a true generating model; cite uncertainty |
| Physical GPU consistency | Earlier exact T4 objective consistency in tested cells, retained with specified physical hardware and original provenance | Report applicability only; no inferred performance/scaling advantage |
| Throughput / HGFX vs MATLAB | REV-2.3 all 44 candidate cells pending; PERF-01C BLOCK_FREEZE | **Unmeasured; neither assume speedup nor forbid reporting slower/mixed results if a prospective future gate passes** |
| Broader computational-statistics contribution | Current paper offers layered parity/optimization/inference validation; redesigned REV-2.5 / REV-2.6 precision-stability data not yet verified | Frame existing **validation methodology** as the substantive contribution. If journal review demands new numerical insight, complete one precommitted REV-2.6 angle rather than inventing findings |

## Submission-critical remaining work (prioritized)

**P0 — manuscript truth and readability**
- [x] Begin a new *provisional*, evidence-led article abstract (201 whitespace-separated words), original published-release fixed-vector results, explicit official D08 failures, and aligned Supplementary Appendix S2.3–S2.4. A source edit is **not** a full article-evidence audit.
- [ ] Verify every manuscript claim in main + ESM against actual primary evidence and sources, not just matching narrative summaries. Do not mark `REV-3 PASS` until final strict `tools/check_manuscript_claims.py` gate succeeds. The earlier 257 unmapped numeric tokens were an initial inventory, not proof all are scientific claims.
- [ ] Complete revision of methods/limitations and figures to remove unsupported general fitting parity, numerical stability claims, or headline speed. At minimum align captions and prose with original Panel G/E denominators and official USD/CHF discrepancies.
- [ ] Independent scientific adjudication of original eHGF one-sided-invalid, missing D02 endpoint, original D08 fit disagreement, and family-specific objective thresholds **without** rerunning exhausted protocols, widening thresholds or relabeling historical failures. Gate REV-2.4 remains `NOT_GLOBAL_PASS`.
- [ ] Resolve redesigned recovery REV-2.5 and statistical-computing REV-2.6 as executed, explicitly blocked, or omitted from paper claims, before author D2. The current text **must not** advertise them as results.

**P0 — reproducibility and journal formalities**
- [ ] Obtain a verified permanent software/archive identifier and confirm all source, evidence, and example archives can be retrieved for review. Verify the release software citation and license for both new code and third-party referenced materials.
- [ ] Review human/secondary data permission and ethics declaration (if applicable), corresponding-author information and AI-use disclosure. Preserve user-authored responses and applicable previous preprint/transfer disclosure. No new ethics exemption is presumed here.
- [ ] Build the flat Springer-compatible LaTeX (or editable Word) submission files, figure source/artwork, bibliography and a compiled PDF; no file package exists under this step. Resolve any bibliography/render failures.
- [ ] Verify current portal article type, funding/waiver/funder-mandate compatibility, subscription licensing and total fees directly before submission. Official Springer says subscription option `no APC` but not a guarantee about every other possible charge.
- [ ] Author D2 approves precise title, abstract, results claims and residual limits; only then final manuscript lock, independent review and D3 submission approval.

**P1 — conditional, not on the critical path until justified**
- [ ] REV-2.3 timed performance experiment: finish only if scientifically comparable inputs and timing boundaries can be prospectively frozen and independently reviewed. Do not add more synthetic guard scripts for their own sake.
- [ ] Additional GPU scaling or numerical-stability study only under the originally authorized gate (or new precommitted prospective protocol); no unrun result may enter manuscript.

## Exact source edits to date

- [Planning correction `378f78a8bc33789ae11a742bc627b4e4a6aa3cd0`](https://github.com/ahmadkhanloo/hgfx/commit/378f78a8bc33789ae11a742bc627b4e4a6aa3cd0): author priority and official journal abstract rule.
- [Main draft rewrite `32b667c4db56c6e4447309c7b7ff3006a802ebbe`](https://github.com/ahmadkhanloo/hgfx/commit/32b667c4db56c6e4447309c7b7ff3006a802ebbe): 201-word abstract, recorded fixed-vector results, mismatch distinctions.
- [ESM `147f556f169c66a8d6d65ae54b08e1f46811eb0b`](https://github.com/ahmadkhanloo/hgfx/commit/147f556f169c66a8d6d65ae54b08e1f46811eb0b): objective denominators and different official-vs-holdout D08 regimes.
- [Declarations `6ac49f35b73e3458a15cf126a3d449daafa9d46e`](https://github.com/ahmadkhanloo/hgfx/commit/6ac49f35b73e3458a15cf126a3d449daafa9d46e): group conflicts/contributions/funding under journal-requested heading.

**Research state remains:** D1=A (Computational Statistics), REV-2.4 NOT_GLOBAL_PASS, original M18/P3/fitting failures preserved, REV-2.3 unrun, PERF-01C BLOCK_FREEZE, REV-3 provisional in progress, final D2/D3 approvals NOT GIVEN. This document does not advance a scientific gate.
