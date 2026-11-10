> **CURRENT EXECUTION AUTHORITY — 2026-11-10, latest explicit author D1 decision = A / COMPUTATIONAL STATISTICS:** After first choosing B (software-venue retarget), the author explicitly reversed that decision and approved A because the JOSS repository public-history criterion is not yet met. This **newer decision supersedes B for future work**, without deleting the B decision, SWPUB-0 documentation gate or historical scientific results. The active task queue is the original [COMPSTAT_REVISION_PLAN.md](COMPSTAT_REVISION_PLAN.md), with `REV-2.4` first because REV-1.4 found an unresolved fit-level difference; follow its predeclared N=200/model and existing tolerances unchanged. [COMPSTAT_REVISION_LEDGER.md](COMPSTAT_REVISION_LEDGER.md) records the scope decision. [SOFTWARE_PUBLICATION_PLAN.md](SOFTWARE_PUBLICATION_PLAN.md) is **PAUSED, not cancelled or PASSED**. REV-3/4/5 and D2/D3 are still pending, and the journal fee/portal route and final author submission remain unverified.

> **REV-2.4 IMPLEMENTATION SNAPSHOT — 2026-11-10 (NONTERMINAL):** Original frozen Panel G and Panel E same-vector objective experiments executed and evidence archived: Panel G 600 fixed vectors (560 both-valid, 39 both-invalid, 1 eHGF one-sided-invalid); Panel E 131/132 original endpoint slots matched with D02 original HGFX endpoint still unavailable. HGF valid-domain original M8 same-vector objectives supported, **not general fitting/scientific parity**. After a limited external AI review (not human), an independently preregistered *single original eHGF-019* trace localized the first latent finite-status mismatch to zero-based trial 8, level 3 posterior variance; first observation likelihood mismatch at trial 11. A source-based numerical discrepancy in `max(0,NaN)` versus `np.maximum(0,NaN)` has a golden pre-fix FAIL, and development-only **1.1.0b1** correction `np.fmax` passed **22/22 CPU unit tests**. **This is IMPLEMENTED BUT NOT SCIENTIFICALLY VALIDATED**; published HGFX v1.0.0 results are immutable. No new full G/E replay or further D019 diagnostic is authorized by the exhausted protocols. Human source review, maintenance family-specific original MATLAB objective validation under a new precommitted protocol, D02 provenance and eHGF/uHGF original family objective gates remain unresolved. Original M18/P3/63-of-64/PERF-01C failures persist. **REV-2.4 is IN PROGRESS / `NOT_GLOBAL_PASS`; D2/D3 BLOCKED.** See [updated execution ledger](COMPSTAT_REVISION_LEDGER.md), [original D019 trace report](../research/REV24_EHGF019_ORIGINAL_TRACE_RESULT_2026-11-10.md), [maintenance result](../research/REV24_EHGF019_MAINTENANCE_RESULT_2026-11-10.md) and [issue #109](https://github.com/ahmadkhanloo/hgfx/issues/109).


> **REV-2.4 END-OF-MAINTENANCE FULL CPU CI RESULT — 2026-11-10 (NOT PASS):** After the development-only eHGF `np.fmax` fix, 22/22 targeted CPU unit tests PASS. The first full Linux/Windows regression attempt [42800906817](https://github.com/ahmadkhanloo/hgfx/actions/runs/42800906817) failed test collection due to `tools` import path; the single documented infrastructure retry [42801485168](https://github.com/ahmadkhanloo/hgfx/actions/runs/42801485168) executed full suite on both OSes with **302 PASS / 1 FAIL / 5 SKIPPED each**, with the one P6A historical Git-ancestry test failing because the special one-shot workflow used shallow checkout (missing a real Git ancestor; server compare independently confirmed ancestry). Permanent regression CI invocation now uses `python -m pytest`; the separate full maintenance workflow now also has `fetch-depth: 0`, but there is **NO third full-suite execution or unearned PASS**. Full status `NOT_PASS`; new scientific release parity unvalidated. Source report [`REV24_EHGF019_FULL_REGRESSION_RESULT_2026-11-10.md`](../research/REV24_EHGF019_FULL_REGRESSION_RESULT_2026-11-10.md) and [updated revision ledger](COMPSTAT_REVISION_LEDGER.md) preserve both failures. REV-2.4/D2/D3 remain BLOCKED; past original 1.0.0 evidence not reclassified.


> **REV-2.4 ISOLATED P6A GIT-HISTORY FOLLOW-UP — 2026-11-10 (SCOPED PASS, FULL CI STILL NOT PASS):** A separate, preregistered, read-only **single-test** diagnostic [Actions 42815782002](https://github.com/ahmadkhanloo/hgfx/actions/runs/42815782002) confirms that the historic P6A ancestry object exists on both Ubuntu and Windows under `fetch-depth:0`; the previously failed unchanged `test_committed_p6a_manifest_matches_generator` **PASSED 1/1 on both OSes**. This substantiates a CI checkout-depth explanation, **but is not a third complete-suite execution** and cannot change archived Linux/Windows full CPU `302 PASS / 1 FAIL / 5 SKIPPED` or `NOT_PASS`. No new MATLAB/HGFX scientific run, numerical threshold, model parameter, seed, dataset, or historical milestone status changed. [Exact scope, sources and run evidence](../research/REV24_EHGF019_P6A_GIT_DEPTH_ISOLATED_RESULT_2026-11-10.md). Development maintenance remains **IMPLEMENTED_BUT_NOT_FULL_CI_OR_SCIENTIFICALLY_VALIDATED**; original REV-2.4 `NOT_GLOBAL_PASS` and D2/D3 **BLOCKED**.

# COMPSTAT_REVISION_PLAN.md
 
Target: `docs/planning/COMPSTAT_REVISION_PLAN.md` in `ahmadkhanloo/hgfx`.
Purpose: take the HGFX manuscript (Computational Statistics, software/package article) from "author-review package" to a submittable, defensible version, by resolving every referee-style criticism C1–C8 below in a bounded number of steps.
 
This plan sits under `AGENTS.md`. Where they conflict, `AGENTS.md` wins. Scientific correctness has priority over speed, but this plan is deliberately time-boxed: **finishing with an honest limitation is a valid outcome; looping is not.**
 
---
 
## 0. Ground rules (read first, apply everywhere)
 
### 0.1 Non-negotiable (inherited from AGENTS.md)
- Never raise a tolerance, change a seed, drop a case, or redefine a criterion to obtain a PASS. Frozen v1.0.0 evidence (`4dd8fbd8`) is never edited or re-labelled.
- On any mismatch, locate the first divergent trial, level, state and intermediate variable before proposing a fix.
- New experiments are *new*, with their own protocol file committed **before** execution. They never replace historical results.
- Every PR references an ID from this plan (`REV-x.y`), registered in `docs/planning/MILESTONES.md`.
### 0.2 Anti-loop rules (the point of this plan)
1. **Fixed task list.** Do only the tasks below. Any new idea goes to `docs/planning/REVISION_BACKLOG.md` and is *not* executed.
2. **Three terminal states per task.** Every task ends as exactly one of:
   - `FIXED` (cause found, fix merged, acceptance check passes),
   - `EXPLAINED` (cause found, no fix needed, documented),
   - `DOCUMENTED_LIMITATION` (cause not found within budget; first-divergence data and what is unknown are recorded).
   Then move on. There is no fourth state such as "keep trying".
3. **Attempt caps.** Max **2 fix attempts** per mismatch. After the 2nd failed attempt → `DOCUMENTED_LIMITATION`.
4. **One run per experiment.** Freeze protocol → run once → report whatever comes out. A rerun is allowed only for infrastructure failure (crash, OOM, runner outage), at most once, and must be logged as such.
5. **Test discipline.** While working: run only targeted tests for the touched module. Run the full CI once at the end of each phase. Do not re-run the full suite after every edit.
6. **Time boxes** (below) are hard. When a box is spent, write the task report and stop.
7. **Phase gates.** A phase is done when its gate checklist is satisfied. Negative results satisfy the gate if they are recorded.
8. **Escalate to the human, don't improvise,** when: MATLAB or GPU access is missing, a time box is exceeded, a decision gate (D1–D3) is reached, or a result contradicts a claim in the manuscript.
9. **Task report template** (append to `docs/planning/COMPSTAT_REVISION_LEDGER.md`, ≤15 lines): ID · status (3 states) · what was done · evidence file paths + SHA-256 · numbers that go into the manuscript · open limitation (if any) · time spent.
### 0.3 Environment assumptions the agent must verify in REV-0 (do not assume)
Repo layout, MATLAB oracle workflow(s) in `.github/workflows/`, paths like `evidence/s7_aggregate.json`, `evidence/published_input_41809919116.json`, `empirical_example/`, `worked_example/`, and whether a GPU runner is available. Record what is missing; do not invent paths.
 
---
 
## 1. Criticism register (what each task must resolve)
 
| ID | Criticism | Resolved by |
|----|-----------|-------------|
| C1 | "Reference-compatible" is proven only for the forward filter at one parameter vector; fit-level evidence is weak (D02/D08 endpoints, failed P3 gate, 4 asymmetric cases, 1/64 subject-7 trajectory mismatch). Endpoint parity is the wrong criterion because MATLAB itself is perturbation-sensitive (6/6 and 13/14). | REV-1.4, REV-2.4, REV-3 |
| C2 | Recovery analysis is weak: deterministic sinusoidal truths, narrow scales, 24 cases/model, single start, no intervals; confusion matrix shows HGF and uHGF rows identical (4/2/6) and at chance; balanced accuracy 0.583 driven by eHGF alone; omega3 correlation negative. | REV-1.1, REV-1.2, REV-2.5 |
| C3 | 48 Python warnings (all in Reed blocks, all with ignored trials, 86 events), cause uncharacterized; only one fixed 17-parameter vector tested. | REV-1.3, REV-2.1 |
| C4 | No performance evidence although the package is "GPU-native"; GPU evidence is from a pre-release runtime; USD/CHF takes 182 s. | REV-2.3, REV-3 (naming) |
| C5 | USD/CHF example: no MATLAB comparison, no termination reason, Ridders warnings, statistics reported without convergence certificate. | REV-2.2 |
| C6 | No statistical-computing contribution beyond a port; unclear what the paper adds for the journal's readers. | REV-2.6, REV-3 |
| C7 | Writing: undefined internal labels (D02, D08, P3, S7, M18, NDC, "frozen", Actions run IDs, "8 November editorial revision"), non-result sections (Pain, SPIRL, Oberwelland, Gao), repetitive negations, "revision"/"candidate" wording. | REV-3 |
| C8 | Administrative/ethical: no DOI archive, HGFX reference without DOI/URL, cover-letter internal language, secondary-data reuse and GPL items open, AI-use verification, preprint overlap, journal template/portal items. | REV-4 |
 
---
 
## 2. Timeline and decision gates
 
| Phase | Content | Budget |
|-------|---------|--------|
| REV-0 | Setup, baseline freeze, ledger | 0.5 day |
| REV-1 | Audits of existing evidence (no new heavy compute) | 2 days |
| **D1** | Human decision: continue to CompStat, or retarget (see §8) | — |
| REV-2 | Six bounded new experiments | 6–8 days (compute-dependent) |
| **D2** | Human decision: which claims survive; final scope | — |
| REV-3 | Manuscript + ESM rewrite | 3 days |
| REV-4 | Archive, licensing, declarations, cover letter | 1.5 days |
| REV-5 | Final verification and submission pack | 1 day |
| **D3** | Human final approval (author) | — |
 
Total ≈ 14–16 working days. If REV-2 compute is unavailable, apply the fallbacks given per task; do not stall.
 
---
 
## REV-0 — Setup and baseline (0.5 day)
 
**Goal:** make everything traceable, change nothing scientific.
 
- REV-0.1 Create branch `compstat-revision` from `main`. Tag the current `main` as `pre-compstat-revision`.
- REV-0.2 Create `docs/planning/COMPSTAT_REVISION_LEDGER.md` (task reports) and `docs/planning/REVISION_BACKLOG.md` (parking lot). Register REV-IDs in `MILESTONES.md`.
- REV-0.3 Verify and list (in the ledger): MATLAB workflow names, GPU availability, locations of the evidence files named in §0.3, and which manuscript numbers have an evidence file. Mark missing ones.
- REV-0.4 Build the **claims ledger script** `tools/check_manuscript_claims.py`: a table mapping every numeric claim in `Manuscript.tex` / `ESM_1.tex` (e.g. 324 blocks, 25,920 trials, 0.583, 36/36, 3.109e-15, 182.001 s, −2387.622, 86 warning events) to an evidence JSON key and its SHA-256. The script fails if a number in the TeX has no mapped source or differs from it. This is the human-verification substitute required by the generative-AI disclosure. Time box: 3 h; unmapped numbers are listed, not blocking.
**Gate REV-0:** branch/tag exist; ledger and backlog exist; claims script runs and prints a coverage table.
 
---
 
## REV-1 — Audit existing evidence (2 days, no new fitting)
 
### REV-1.1 Recompute the confusion matrix from raw records (C2) — 3 h
- Source: `evidence/s7_aggregate.json` and the 36 per-dataset BIC records (or shard archives).
- Recompute from per-dataset selections, not from stored proportions (ESM says counts were "recovered from proportions").
- Check specifically whether the HGF and uHGF rows (4/12, 2/12, 6/12 each) are truly identical, or a copy/aggregation artifact. Check data generation: confirm the uHGF datasets are not generated by the same configuration as HGF.
- Output: `evidence/revision/confusion_audit.json` + one paragraph.
- Outcome rules: if a bug → `FIXED` in the *reporting* layer only (frozen raw data stays); the corrected matrix replaces the ESM matrix and the manuscript text; stop. If genuinely identical → `EXPLAINED` with the mechanism (e.g. why uHGF ≈ HGF at these settings).
### REV-1.2 Add uncertainty and chance baselines to existing results (C2) — 3 h
- No refitting. Using existing per-case outputs: exact (Clopper–Pearson) CIs for convergence rate and per-class recovery; bootstrap (percentile, B=2000, fixed seed) CIs for median correlation, median sRMSE; chance level (1/3) and an exact binomial test per generating-model row.
- Report per-parameter results (omega2, omega3, log ζ) as primary; the pooled median becomes secondary.
- Output: `evidence/revision/recovery_uncertainty.json`, regenerated Fig 2/3 with intervals.
- Rule: figures changed only by adding intervals/baselines; values unchanged.
### REV-1.3 Warnings: classify from archived records (C3) — 2 h
- From the archived 324-block status records: reproduce the count (86 events in 48 Reed blocks: 29×1, 19×3; all with ignored trials).
- Cross-tab by: dataset, number/position of ignored trials, arm, first ignored trial index.
- No claim about mechanism yet (REV-2.1 does that).
- Output: `evidence/revision/warning_crosstab.json`.
### REV-1.4 Four asymmetric P3 cases + subject-7 trajectory mismatch: first-divergence localization (C1) — time box 1 day total
- Cases: classic HGF, truth scale 0.35, T = 512 and 1024, replicates 0 and 4 (MATLAB negative log joint: −inf, 247.2574…, −inf, 620.4345…); and subject index 7 of the 64-fit cohort (level-2 posterior/predicted means).
- Method (AGENTS rule 07): regenerate the exact simulated data from the stored seed; evaluate **both** implementations' objective at the *same* initial transformed parameter vector; compare per-trial log-likelihood and states; find first divergent trial/level/variable.
- Attempt cap: 2. If a real HGFX defect is found and the fix is small (≤ ~30 lines) → fix with a golden test; **any fix goes into 1.0.1/main only and must not alter the 1.0.0 evidence**. If not localized → `DOCUMENTED_LIMITATION` with the divergence table.
- Do **not** re-run the P3 grid.
**Gate REV-1:** REV-1.1 – 1.4 each have a ledger report; `REV-1` evidence directory committed. **Then D1.**
 
### D1 (human) — scope decision
Present: the corrected confusion matrix, uncertainty intervals, warning cross-tab, divergence findings. Decide: (a) continue targeting *Computational Statistics*; (b) retarget (see §8). Continue to REV-2 only after the decision. If the REV-1.4 result shows an unexplained HGFX defect, REV-2.4 gets priority and the submission date moves.
 
---
 
## REV-2 — Bounded new experiments (6–8 days)
 
For each experiment: write `evidence/revision/protocols/REV-2.x_PROTOCOL.md` (hypotheses, data, seeds, parameters, metrics, pass/fail criteria, stopping rule, exclusion policy = none), commit it, **then** run once. Use the released 1.0.0 wheel for anything claimed as evidence for 1.0.0; anything run on `main` / 1.1.0b1 must be labelled "development line" and kept out of the 1.0.0 claims.
 
### REV-2.1 Warning root cause + multi-vector forward sweep (C3) — 1.5 days
1. Re-run the 324-block forward comparison **capturing** each warning's category, message, file/line, block ID, trial and level (use `warnings.catch_warnings(record=True)`; no behaviour change). Same tolerances, same vector.
2. Classify each warning: numerical (invalid value, divide, overflow), masking-related, or other. Determine whether any compared array contains nonfinite entries that were "matched" only because both are NaN, and whether those correspond to ignored trials.
3. **Multi-vector sweep:** add 20 additional parameter vectors drawn from a fixed-seed distribution around the M12B vector (±0.5 prior SD in transformed space, plus 3 deliberately extreme vectors) on a pre-specified subset: all 64 Reed blocks + 64 Suthaharan blocks (fixed seed for selection). Same field-specific tolerances.
4. Outcome: either all pass (report as extended evidence), or locate the first divergence (rule 07, cap 2 attempts).
- Acceptance: every warning has a category; the manuscript can state mechanism or state that it is unresolved with the categorized evidence.
- Fallback: if the full capture is infeasible, run on the 48 warning blocks + 48 random non-warning blocks only.
### REV-2.2 USD/CHF vs MATLAB and convergence diagnostics (C5) — 1 day
1. Run the toolbox's own demo on the same 614-observation series in MATLAB 8.2.0 (existing oracle workflow). Compare: fitted transformed/native parameters, negative log likelihood/joint, BIC/LME, trajectories at each implementation's own optimum **and** cross-evaluated objective at the other's optimum.
2. Expose a non-breaking `termination` / `converged` field in the optimizer result if it does not exist (small change; additive; changelog entry; unit test). Report Hessian condition and positive-definiteness of the curvature used.
3. Characterize the Ridders warnings: count, location (parameter index), and effect (does the final statistic change if the step settings are varied within the *documented* options? at most 3 settings, no tuning).
- Outcome classes use the existing vocabulary (direct parity / matched limitation / not comparable) but **defined once, in plain words**, in the manuscript.
- Acceptance: the example either has MATLAB agreement at a stated criterion or the manuscript states the observed differences with their sizes. No claim of convergence without the field.
### REV-2.3 Performance and resources (C4) — 2 days
Pre-registered benchmark, single pass:
- Workloads: (a) forward filter, T ∈ {128, 1,024, 8,192, 65,536}; (b) single-subject fit (binary HGF, default config), T ∈ {128, 512}; (c) batch of subjects B ∈ {1, 32, 256, 1,024} at T = 256 using the package's batch path; (d) USD/CHF fit.
- Backends: MATLAB 8.2.0 (CPU), HGFX compatibility CPU, JAX CPU, JAX GPU (one device). Same machine for CPU rows; if MATLAB is only available on a CI runner, report its rows separately and **do not compute cross-hardware speed ratios**.
- Protocol: record hardware, OS, library versions; 1 warm-up + 5 timed repeats; report median and IQR; report JIT compile time separately from steady state; peak memory where measurable. Float64 throughout (policy).
- No optimization of code during this task. If the result is "GPU is not faster in this workload", report that. If it is slower than MATLAB on single fits, say so.
- Fallbacks: (i) no GPU → state GPU claims are limited to the retained objective-agreement evidence and drop "GPU-native" from the paper (see REV-3.1); (ii) no MATLAB → compare Python backends only.
- Acceptance: a figure + table with intervals; `evidence/revision/benchmark_*.json`; the GPU run uses the 1.0.0 wheel (replaces the "pre-release runtime" evidence, or states that it could not).
### REV-2.4 Fit-level agreement via objective cross-evaluation (C1) — 1.5 days
Replace "endpoint parity" as the headline criterion by something that is well-defined even when the optimizer path is unstable:
1. **Objective parity on a grid:** draw N = 200 transformed-parameter vectors per model family (fixed seed, prior-based, free parameters only) and compare MATLAB vs HGFX negative log likelihood and negative log joint, and gradient where available. Use the existing field-specific tolerances for the fixed-vector objective; no new ones.
2. **Cross-evaluation at endpoints:** for D02, D08 and the 64-fit cohort, evaluate each implementation's objective at the other's fitted endpoint; report objective gaps. Equal objective at both endpoints → "same optimum value, different path"; otherwise report the gap.
3. **Cohort mismatch:** summarize the subject-7 divergence from REV-1.4.
- Acceptance: a table "what is equal / what differs / how much", with every difference attached to a first-divergence record or a stated unknown. Criteria are written in the protocol before the run.
### REV-2.5 Redesigned recovery study (C2) — 2–3 days (compute-dependent)
Run only after REV-1.1/1.2. HGFX is the primary implementation; a **paired MATLAB subset** (first 30 datasets of each generating model, fixed order) checks that conclusions are implementation-independent.
- Truth parameters: random draws from the *prior* (fixed seed), not sinusoidal grids; report in transformed space.
- Design: models {HGF, eHGF, uHGF}; T ∈ {128, 256, 512}; 100 parameter datasets per model per T for parameter recovery; 60 datasets per generating model per T for model recovery; fits from the prior mean **plus 2 random starts** (best objective retained; all runs logged); convergence from a recorded termination reason.
- Metrics: per-parameter correlation, sRMSE (population SD of truths, ddof = 0), bias; model-recovery confusion matrix, balanced accuracy vs chance with exact/bootstrap CIs; BIC and a likelihood-based identifiability note (profile or curvature) for omega3.
- Predeclared thresholds stay as in the original (≥0.80 convergence, ≥0.50 correlation, ≤1.00 sRMSE, ≥0.50 balanced accuracy) so results are comparable; additionally report which are met per parameter.
- Handling failures: invalid simulations are logged and counted, never redrawn.
- Fallback if compute is short: reduce replicates by 50% uniformly (stated in the protocol before running), never drop models or horizons selectively.
- Acceptance: results reported whatever they are. If recovery is poor, the manuscript frames it as a property of the HGF + design (with the evidence), not as software behaviour.
### REV-2.6 One statistical-computing angle (C6) — 1.5 days
Choose **one** of the following after D1 (default: A). Do not do more than one.
- **A. Precision and recursion stability.** Forward-filter error growth with horizon under float32 vs float64 (JAX default float32 is the common user mistake): parameter draws as in REV-2.4, T up to 65,536, report max/median error vs float64 reference and fraction of runs reaching the negative-posterior-precision failure; characterize the parameter regions where the recursion fails in both MATLAB and HGFX. Output: one figure + one table + practical guidance ("use float64; failure region is X").
- **B. Derivative accuracy (only if 1.0.0 exposes the relevant path).** Compare JAX autodiff vs finite-difference gradients and the effect on curvature/LME. If 1.0.0 does not use autodiff in its fit path, do not use this angle for 1.0.0 claims.
- Acceptance: the Introduction can state a concrete computational question that the paper answers with data.
**Gate REV-2:** every REV-2.x has a protocol, a single result record, and a ledger report; `tools/check_manuscript_claims.py` updated for the new numbers. **Then D2.**
 
### D2 (human) — what the paper can claim
Using the ledger: list claims that are supported, claims to downgrade, and any experiment that failed. Decide the title and the abstract's headline claim. Rule of thumb: the paper should claim only (i) fixed-parameter forward agreement (extended by REV-2.1), (ii) objective-level agreement (REV-2.4), (iii) whatever REV-2.3/2.5/2.6 actually show.
 
---
 
## REV-3 — Manuscript and ESM rewrite (3 days)
 
Do not re-open experiments in this phase. If a number needs to change, change the evidence file and the claims script, not the prose alone.
 
### REV-3.1 Positioning, title, abstract (C4, C6)
- Rewrite abstract (≤ 180 words) around: the migration problem, what was verified at each level (forward filter / objective / fit / recovery), the **main new computational finding** (REV-2.6), and the performance result *as measured* (REV-2.3).
- Align naming with evidence: if REV-2.3 does not support it, remove "GPU-native" from the paper and update the README/CITATION title consistently (the repo currently says "GPU-Native Python Toolbox").
- Introduction: one paragraph stating why a statistician/computational scientist cares (precision/stability, fit sensitivity, reproducible validation methodology), one paragraph on related software (MATLAB TAPAS/HGF, pyhgf), then contributions as 3 bullets.
### REV-3.2 Structure (C1, C7)
Target ≤ 14 pages main text. Suggested outline:
1. Introduction · 2. Model and parameter conventions (short) · 3. Software · 4. Validation design (levels, in plain terms) · 5. Results: forward agreement, objective/fit agreement, recovery, performance, examples · 6. Limitations (one consolidated section: sensitive fits, P3 gate, asymmetric cases, remaining warnings) · 7. Discussion · Declarations.
- Replace internal labels with descriptive names on first use (e.g. "stress fit (D02)" → "stress-test fit"); remove run IDs, commit-chatter and dated "revision" notes from the paper; keep them in the repository ledger.
- Define the outcome vocabulary once (direct parity / matched reference limitation / failed criterion retained / not directly comparable) in a boxed table; then use it consistently.
- Cut repeated "does not establish…" sentences: state limits once in §6 and once in the abstract.
### REV-3.3 Results text (C1, C2, C3, C5)
- C1: lead with objective-level agreement and cross-evaluation (REV-2.4); present D02/D08 as evidence that the *reference itself* is path-sensitive, using the 6/6 and 13/14 numbers.
- C2: present the redesigned study (REV-2.5) as primary; the original 36-dataset grid becomes a short "initial grid" paragraph + ESM table with the corrected confusion matrix and intervals. State plainly that HGF/uHGF recovery is at or near chance if that is what the data show.
- C3: present the warning classification and multi-vector sweep; say exactly what remains unexplained.
- C5: present USD/CHF with MATLAB comparison and termination diagnostics, or state the observed differences.
- Every figure has intervals or an explicit "deterministic, no uncertainty" note.
### REV-3.4 Remove or demote non-results (C7)
- Pain, SPIRL, Oberwelland, Gao: reduce to **one paragraph** in Limitations ("transportability of custom pipelines was audited for two studies and not completed; see repository docs") and move all detail to `docs/` in the repo. Delete the Oberwelland/Gao access-failure text from the ESM.
### REV-3.5 ESM
- Re-number sections to match the new main text; self-contained identifiers (full commit SHAs stay, run IDs go to repo ledger); add tables for REV-2 outputs; keep corrected confusion matrix and intervals.
**Gate REV-3:** main text and ESM compile (`pdflatex` twice) from flat sources; claims script reports 100% of numbers mapped; no undefined acronyms (script: grep list of banned internal labels: `D02|D08|P3|S7|M18|NDC|REVISION|candidate|frozen decision`); page count ≤ 14 (main) and ≤ 10 (ESM).
 
---
 
## REV-4 — Archive, licensing and declarations (1.5 days)
 
### REV-4.1 Archive and citation (C8)
- Create a GitHub release for the exact evaluated source and deposit on Zenodo (GitHub–Zenodo integration) to obtain a **version DOI**; deposit also the evidence bundle (JSONs, protocols, manifests, benchmark data) as a separate Zenodo record or as release assets. Update `CITATION.cff`, `README.md`, and the manuscript's HGFX reference (add DOI/URL; update the title to match REV-3.1).
- Add DOIs/URLs to the JAX and Frostig et al. references.
- Move all load-bearing evidence out of "Actions artifacts" into the Zenodo bundle.
### REV-4.2 Data reuse and licensing (C8)
- Reed et al. (2020) and Suthaharan et al. (2021) input files: record each dataset's license/terms and source repository; confirm that the **derived aggregate** statistics (no per-trial data) can be redistributed; add a statement to Data availability. If a term is unclear → mark as `HUMAN_ACTION` (author contacts data owners); do not remove the check.
- Pain/SPIRL GPL: confirm no GPL source is in the HGFX package or in the submission archive; keep `THIRD_PARTY_NOTICES.md` accurate; remove any non-redistributable material from the archive.
- Verify the `empirical_example/` MIT notice and the CSL file notice remain intact (the CSL file is not part of the journal submission if the journal style is used).
### REV-4.3 Declarations and cover letter (C8)
- Cover letter: rewrite as a clean, final letter: no "proposed revision", "author-review package", or process notes; state the contribution in three sentences, the key measured results (as updated), the related preprint and what is *new* relative to it, the competing-interest statement (developer/maintainer), and exclusive-submission wording **as the author confirms** (do not invent it).
- Generative-AI statement: keep the disclosure; add one sentence on the verification process (claims script, author reading of every table, test runs).
- Funding/ethics statements unchanged unless facts changed.
### REV-4.4 Journal formalities (HUMAN_ACTION; agent prepares a checklist only)
- Download the official Springer Nature LaTeX template manually (the official ZIP was inaccessible to the agent: HTTP 403) and port the sources; confirm the portal article type and the publishing model (journal is hybrid; confirm no mandatory charge and the author's institutional agreement); check the current submission guidelines page on the day of submission.
**Gate REV-4:** DOI(s) exist and are cited; licensing note added; cover letter final draft; `HUMAN_ACTION` list written to the ledger.
 
---
 
## REV-5 — Final verification and submission pack (1 day)
 
1. Clean-room check: new virtual environment, `pip install hgfx==1.0.0` (and, if the paper reports 1.0.1, that version), run `examples/quickstart.py` and the USD/CHF example; compare output to the manuscript.
2. Full CI once on `compstat-revision`; all required gates must pass; nothing may be waived by changing a tolerance.
3. Claims script: 100% coverage, zero mismatches.
4. Final build: `Manuscript.pdf`, `ESM_1.pdf`, source zips, figures (PDF + EPS), cover letter, `README.txt` upload map, `manifest.json` with SHA-256 hashes, `archive_verification.json` regenerated.
5. Merge `compstat-revision` → `main` via PR (PR description lists the REV IDs and ledger summary). Tag `compstat-submission-YYYYMMDD`.
6. Prepare a **point-by-point limitation table** (one page, in the ledger) mapping C1–C8 to final status — useful later when answering referees.
**Gate REV-5 / D3 (human):** the author reads the manuscript, ESM and the ledger, approves scientific content, confirms declarations and uploads in the portal.
 
---
 
## 3. Stop conditions for the whole plan
The agent stops and reports (instead of continuing) if:
- a REV-1.4 or REV-2.4 result shows an unexplained HGFX defect that changes a headline claim;
- REV-2.5 cannot be completed within the compute budget even after the stated fallback;
- 2 or more time boxes are exceeded;
- any task would require changing a frozen criterion, seed, threshold or the 1.0.0 evidence.
## 4. What "done" means
The plan is complete when: all REV tasks have a terminal status and a ledger report; the manuscript contains only numbers mapped by the claims script; each criticism C1–C8 is `FIXED`, `EXPLAINED` or `DOCUMENTED_LIMITATION`; and the human has taken decisions D1–D3. Nothing else is required, and nothing else should be started.
 
## 5. Out of scope (park in `REVISION_BACKLOG.md`)
New model families; speed optimization; making classic HGF recover omega3; reproducing original study results; full Pain/SPIRL/Oberwelland/Gao migrations; further GPU scaling work; 1.1.0 features (MAP, VKF, dual-stream, softmax) beyond labelled development-line notes.
 
## 6. Mapping to AGENTS.md rules
Rule 06 (no tolerance inflation) → §0.1; rule 07 (first divergence) → REV-1.4, REV-2.1, REV-2.4; rule 04/05 (float64, CPU before GPU) → REV-2.3, REV-2.6; rule 14 (Migration Matrix ID) → REV-IDs registered in MILESTONES.md; failure policy → attempt caps and terminal states in §0.2.
 
## 7. Suggested agent prompt (paste at the start of each session)
> Read `AGENTS.md` and `docs/planning/COMPSTAT_REVISION_PLAN.md`. Work only on task `REV-x.y`. Follow §0.2 (3 terminal states, 2-attempt cap, one run per experiment, time box). Write the protocol before running anything. When finished, append the ledger report and stop; do not start another task.
 
## 8. Alternative venues (for decision D1 only)
If D1 concludes the paper's statistical-computing contribution is too thin after REV-1/REV-2.6, retarget to a software-/application-oriented venue (e.g. *Journal of Open Source Software*, *Journal of Open Research Software*, *Frontiers in Neuroinformatics*, *Behavior Research Methods*) and shorten the paper accordingly; the REV-2 evidence remains reusable.
