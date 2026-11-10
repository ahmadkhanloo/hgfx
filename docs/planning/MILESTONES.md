> **LATEST AUTHOR D1 INSTRUCTION — 2026-11-10: A / CONTINUE COMPUTATIONAL STATISTICS.** This explicitly supersedes the earlier B retarget for **future** work; the post-D1 SWPUB section below is preserved as dated history but the SWPUB track is **PAUSED**. Original REV-2 tasks resume; `REV-2.4` is priority and not yet scientifically validated. D2/D3 remain human gates. [Current revision plan](COMPSTAT_REVISION_PLAN.md) · [ledger](COMPSTAT_REVISION_LEDGER.md).

> **CURRENT REV-2.1 SOURCE BLOCKER (2026-11-10):** [Original source-only preflight 42833384591](https://github.com/ahmadkhanloo/hgfx/actions/runs/42833384591) independently confirmed the 324-case archived fixed-vector corpus and 86 warning events without a model run, but the original **free native phi2=0** has no finite transformed logit centre for the plan's M12B-centred perturbation design. No new science has run; logit clipping/parameter substitution are prohibited. Pre-outcome decision tracked in [issue #110](https://github.com/ahmadkhanloo/hgfx/issues/110) and [evidence report](../research/REV21_SOURCE_PREFLIGHT_RESULT_2026-11-10.md). REV-2.4 frozen original science remains `NOT_GLOBAL_PASS`, D2/D3 BLOCKED. Historical notes below are dated snapshots; the newer D1=A decision in the first notice governs.

# Milestones and Gates

## M0 — Reference Frozen
Pass only if exact version, commit, source manifest, and checksums are recorded.

## M1 — Golden Harness Operational
Pass only if one MATLAB case can be exported, loaded in Python, and diffed reproducibly.

## M2 — Parameter/Config Parity
Pass only if parameter order, transforms, priors, fixed/free semantics, placeholders, and masks match.

## M3 — Scalar Numerical Parity
Pass only if utility-level golden tests pass in CPU float64.

## M4 — HGF Forward Parity
Pass only if standard HGF trajectories match within calibrated tolerance.

## M5 — eHGF Forward Parity
Same gate for eHGF.

## M6 — uHGF Forward Parity
Must separately validate Lambert W0, dual approximation logic, variational weighting, and mixture moments.

## M7 — Observation Parity
P0/P1 observation families must match trial-wise and total likelihoods.

## M8 — Objective Parity
At fixed parameter vectors, objective decomposition must match.

## M9 — Compatibility Fitting
MAP objective and fit behavior must be scientifically equivalent on reference fixtures.

## M10 — Hessian/LME Parity
Hessian, covariance, correlation, AIC, BIC, LME and decomposition validated.

## M11 — Simulation Parity
sim/sample behavior validated.

## M12 — Specialized Model Coverage
Every frozen source/model family has a final migration status.

## M13 — API Compatibility
Downstream scripts can consume compatibility results with minimal changes.

## M14 — GPU Engine
CPU/GPU float64 forward and objective parity validated.

## M15 — GPU Fitting
On-device optimization validated.

## M16 — Batch Engine
Batch result equals repeated single-fit result within tolerance.

## M17 — Multi-GPU
Scaling validated.

## M18 — Scientific Recovery
Historical scientific gate: parameter recovery and model recovery satisfy preregistered acceptance criteria; the recorded FAIL is preserved. M18B protocol-integrity PASS is separate.

Current product closure follows `M18_COMPLETION_PLAN.md` and the frozen reference-limitations policy. Required MATLAB workflow accounting, paired recovery classification, robustness/backend validation and physical NVIDIA GPU applicability are closed in documented scopes. A matched reference limitation is acceptable product evidence, not a scientific-recovery PASS. Existing M18C.2 horizon-analysis issue #21 remains research work rather than a v1 blocker.

## M19 — Methods Paper Dataset Frozen
**PASS / FROZEN.** Historical failures and scoped reference limitations remain preserved in the machine-readable release evidence.

## M20 — v1.0 Candidate
**PASS.** Historical RC candidate metadata were `1.0.0rc1`. Finalizer run `34989737851` on source `b52dc06ca58d29afeb5c265f7eb67746824178e0` returned `PASS_M20_CANDIDATE` with `failures=[]`. M20 is preserved as the release-candidate gate and is not redefined by final promotion.

## Final v1.0.0 Promotion
**PASS / RELEASED.** The independent frontier review was completed; H1/H2 were resolved without changing frozen scientific criteria. Final metadata were promoted to `1.0.0` on PR #30 head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`. Active final-promotion gates all passed (`35089882319`, `35089882608`, `35089882668`, `35089882392`). PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, and main regression run `35090329868` passed on Ubuntu and Windows.

Git tag `v1.0.0` is verified to resolve directly to `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. GitHub Release ID `389966452` is published at https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0 and is neither draft nor prerelease.

**The HGFX v1.0.0 milestone/release sequence is closed.** Future research, publication, maintenance, upstream compatibility, packaging/distribution, or feature work requires explicit post-v1 milestones and does not reopen the frozen v1 evidence.


## Post-v1 publication revision — COMPSTAT (new REV IDs; historical M0–M20 unchanged)

Authority: [COMPSTAT_REVISION_PLAN.md](COMPSTAT_REVISION_PLAN.md). The publication revision is distinct from the v1.0.0 scientific and release gates; no M18 scientific FAIL is reclassified.

| Task ID | Scope | Current status | Acceptance |
|---|---|---|---|
| REV-0.1 | Branch and pre-revision tag | FIXED | Tag verified at original baseline SHA; CI 42529284444 |
| REV-0.2 | Ledger, backlog, REV registration | FIXED | Ledger, backlog, registry committed in PR #107 |
| REV-0.3 | Reality-check workflows, evidence paths, GPU | EXPLAINED | Paths verified; missing evidence and current GPU unavailability documented |
| REV-0.4 | Manuscript numeric-claim checker | FIXED (REV-0 setup gate) | Checker and audit CI PASS; 257 numeric tokens unmapped remain REV-3 gate |
| REV-1.1 | Raw BIC confusion audit | EXPLAINED / CI PASS | Original 36 raw selections verified; evidence JSON + terminal ledger report; run 42526812868 |
| REV-1.2 | Recovery uncertainty and chance baselines | EXPLAINED / CI PASS | Frozen 12-shard audit; exact CIs, paired-horizon bootstrap B=2000, revised figures; run 42528948338 |
| REV-1.3 | Archived warning cross-tab | EXPLAINED / CI PASS | 324 original status records + 64 pinned Reed masks verified; 48 warning blocks / 86 events; types/mechanism unknown; CI 42531284505 |
| REV-1.4 | First divergence (four asymmetric cases and subject 7) | DOCUMENTED_LIMITATION (NO SCIENTIFIC PASS) | Original P3/64-fit ZIP and case hashes audited; four HGFX initial prechecks vs MATLAB fit outputs; subject-7 first threshold exceedance found; same-vector MATLAB intermediate evidence unavailable; terminal report and D1 packet |
| REV-2.1 | Warning capture and multi-vector sweep | **PRE-EXPERIMENT DESIGN BLOCKED; SCIENCE NOT RUN** | Source-only original 324-case/86-warning audit [CI 42833384591](https://github.com/ahmadkhanloo/hgfx/actions/runs/42833384591) PASS (9 tests); original **free phi2=0** lacks finite inverse logit; prospective input-design decision [#110](https://github.com/ahmadkhanloo/hgfx/issues/110) required before full experiment |
| REV-2.2 | USD/CHF comparison and convergence | **IN PROGRESS — STOP REPORTING IMPLEMENTED / TARGETED CPU PASS; USD/CHF SCIENCE NOT RUN** | Additive `fitModel().optim.termination/converged` result fields, no solver changes; [targeted CPU CI 42838228644](https://github.com/ahmadkhanloo/hgfx/actions/runs/42838228644) **11/11 PASS both Ubuntu and Windows**; authentic 614-series paired MATLAB/HGFX fit, curvature and Ridders warning tests OPEN |
| REV-2.3 | Performance/resource benchmarking | OPEN (D1 A AUTHORIZED; NOT YET EXECUTED) | Precommitted protocol, hardware provenance |
| REV-2.4 | Objective cross-evaluation | **IN PROGRESS / ORIGINAL `NOT_GLOBAL_PASS`** | Authentic frozen MATLAB and HGFX Panel G 600 comparisons [run 42776781367](https://github.com/ahmadkhanloo/hgfx/actions/runs/42776781367); Panel E 131/132 endpoints [run 42786519173](https://github.com/ahmadkhanloo/hgfx/actions/runs/42786519173), HGF-only same-vector objective evidence; one eHGF 019 invalid, one original D02 endpoint missing. Dev-only `np.fmax` fix 22/22 targeted CPU PASS but **scientific, full CI, and human review gates OPEN**; issue [#109](https://github.com/ahmadkhanloo/hgfx/issues/109), PR #107 DRAFT |
| REV-2.5 | Redesigned recovery | OPEN (D1 A AUTHORIZED; NOT YET EXECUTED) | Precommitted protocol, full failure log |
| REV-2.6 | Statistical-computing investigation (one angle) | OPEN (D1 A AUTHORIZED; NOT YET EXECUTED) | Precommitted protocol, measured result |
| REV-3 | Manuscript and supplement rewrite | BLOCKED BY D2 | Claims and build gates |
| REV-4 | Archive/licensing/declarations | OPEN (later phase) | DOI, notices, author actions |
| REV-5 | Verification and submission package | OPEN (later phase) | Full CI, final gates, author D3 |

**REV-1 audit-report gate complete with DOCUMENTED_LIMITATION (2026-11-09):** all four REV-1 terminal reports and aggregate evidence are committed; this is NOT a scientific, fitting or causal-parity PASS. D1 decision packet: [COMPSTAT_D1_DECISION_PACK.md](COMPSTAT_D1_DECISION_PACK.md). D1 human choice remains PENDING; REV-2 BLOCKED.
**Human decision gates:** D1 after all REV-1 reports; D2 after REV-2 reports; D3 after the final submission pack. Do not run REV-2 before D1. No numerical threshold, seed, dataset, or frozen release evidence can be modified to obtain a PASS.

**REV-0 phase gate PASS (2026-11-09):** see `COMPSTAT_REVISION_LEDGER.md` and tag `pre-compstat-revision` at `46fe45e1fdd110a0e72a6dc661bf05c9c38e8885`. This does not imply final manuscript claims coverage or REV-1 phase completion.

## Post-D1 software-publication track — SWPUB (prospective, historical REV unchanged)

**Author decision 2026-11-10:** D1 **B / RETARGET DONE**: change journal from *Computational Statistics* to a software/research-software venue. This human choice does **not** approve any particular journal, fee, scientific waiver or manuscript submission. Active source: [SOFTWARE_PUBLICATION_PLAN.md](SOFTWARE_PUBLICATION_PLAN.md) and [SOFTWARE_PUBLICATION_GATE.md](../validation/SOFTWARE_PUBLICATION_GATE.md). Old REV-2–REV-5 retain their original historical definitions and were not completed or passed; they are no longer authorized as the retargeted article's task list.

| New gate | Scope | Status | Acceptance authority |
| --- | --- | --- | --- |
| SWPUB-0 | Record author D1 and establish prospective software-publication acceptance policy | **DONE / documentation-only gate PASS (2026-11-10)** | Decision, plan, gate, venue screen, workspace, linked docs verified; **not manuscript or science acceptance** |
| SWPUB-1 | Venue eligibility and **zero mandatory author fee** verification | OPEN / BLOCKED ON VERIFIED TERMS | Actual venue-specific official rules, written zero-charge eligibility, final author journal choice |
| SWPUB-2 | Source-backed software paper and honest comparison with alternatives | OPEN | Venue-specific manuscript; no unsupported fit/identifiability/speed/replication claim |
| SWPUB-3 | Frozen-release runnable examples, exact claims and source-bounded evidence audit | OPEN | Reproducible input/output, strict numeric-claim check, scoped validation, limitations preserved |
| SWPUB-4 | Archive, license, declarations, authorship, preprint and DOI review | OPEN | All legal and administrative constraints independently verified and author-confirmed |
| SWPUB-5 | Independent pre-submission review, artifact build, human final approval | BLOCKED ON SWPUB-1..4 | Exact candidate reviewed, no critical/high unresolved, explicit author submission signoff |

**Never declare SWPUB-5 PASS because older v1.0.0 software/product CI was green.** Old REV scientific results, the failed P3 gate, 63/64 nonpass and PERF-01C BLOCK_FREEZE remain permanently visible.
