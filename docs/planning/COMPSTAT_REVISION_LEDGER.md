# Computational Statistics revision ledger

> **Latest status (2026-11-10, author D1=A):** REV-0 PASS; REV-1.1–1.3 terminal EXPLAINED, REV-1.4 terminal DOCUMENTED_LIMITATION (not scientific PASS); REV-2 is authorized with REV-2.4 first, scientific tests still OPEN. Earlier D1 B decision and SWPUB preparation remain preserved as chronological history; active manuscript is Computational Statistics. M18/P3/63-of-64 and PERF-01C failed/block statuses are unchanged.


**Scope:** `COMPSTAT_REVISION_PLAN.md`; working branch `compstat-revision`.
**Baseline main commit:** `46fe45e1fdd110a0e72a6dc661bf05c9c38e8885` (2026-11-08).
**Historical release evidence:** HGFX v1.0.0 at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; immutable.
**Phase:** REV-0 gate PASS. REV-1 audits IN PROGRESS: REV-1.1 and REV-1.2 `EXPLAINED`; REV-1.3 and REV-1.4 OPEN.
**Gate REV-0:** PASS (branch, exact baseline tag, ledger/backlog, verified path inventory, numeric-claim coverage script operational). REV-0.4 inventory is not the later final 100% manuscript-claim gate.

## REV-0.3 verified repository inventory (2026-11-09)

| Plan expectation | Checked result at baseline | Status |
|---|---|---|
| Revision branch | `compstat-revision` created from recorded `main` SHA | CREATED |
| `pre-compstat-revision` tag | Lightweight tag created and verified by [CI 42529284444](https://github.com/ahmadkhanloo/hgfx/actions/runs/42529284444), resolves to `46fe45e1fdd110a0e72a6dc661bf05c9c38e8885` | FIXED |
| MATLAB oracle workflows | `.github/workflows/m18-s7-paired-recovery.yml`, `m18-d02-matlab-self-sensitivity.yml`, `m18-d08-matlab-self-sensitivity.yml`, `m18-scientific-validation.yml` and more | PRESENT; execution NOT VERIFIED |
| GPU capability | Historical physical T4 result in `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` | HISTORICAL EVIDENCE PRESENT; current runner UNKNOWN |
| `evidence/s7_aggregate.json` | No `evidence/` tree on `main`; `reference/validation/m18_s7_reference_limitation/decision.json` summarizes S7; raw shards are workflow artifacts | EXPECTED FILE MISSING; historical 12 raw S7 shard archives recovered and audited from run `34896442847` |
| `evidence/published_input_41809919116.json` | Not in `main` tree | MISSING |
| `empirical_example/`, `worked_example/` | Neither present in `main` tree | MISSING |
| `Manuscript.tex` and `ESM_1.tex` | No committed `.tex` files; active journal source: `paper/computational_statistics/manuscript.md`, supplement `paper/SUPPLEMENTARY_APPENDICES.md` | MARKDOWN BASELINE; TeX NOT CREATED |
| Frozen paired model selection | `reference/validation/m18_s7_reference_limitation/decision.json`: 36/36 BIC winners, balanced accuracy 0.583333... | JSON SOURCE PRESENT |
| P3 horizon integrity | `paper/reproducibility/p3_m18c2_aggregate_35272347167.json`: 10/72 discordant | JSON SOURCE PRESENT; gate FAILED historically |
| Physical T4 objective agreement | `gpu_validation_results/m18_s9_physical_gpu_revalidation.json`: 1.4210854715202004e-14 max gap, fixed 1e-7 criterion | JSON SOURCE PRESENT; no timing claim |
| Performance `182.001 s`, warnings `86`, blocks `324` | No direct JSON key verified in current checkout for these manuscript-plan example numbers | UNMAPPED; do not assert provenance |

## REV-0.4 implementation notes

- `tools/check_manuscript_claims.py` audits numeric tokens in current Markdown inputs by default and accepts explicit `--source` paths for later TeX.
- `docs/planning/COMPSTAT_CLAIM_MAP.json` maps an initial subset of article numbers to JSON pointers. SHA-256 is computed from actual file bytes at execution.
- **Strict mode fails** on either missing mappings or evidence mismatches; `--allow-unmapped` is a REV-0 inventory mode and must never be interpreted as final 100% verification.
- Run `python tools/check_manuscript_claims.py --allow-unmapped --json-out /tmp/compstat-claims.json` to collect baseline coverage; run without the flag to enforce the final gate.
- MATLAB, GPU, physical runtime, and all new experiments are deliberately untouched in REV-0.

## Task reports (append only on terminal resolution; maximum 15 lines per task)

Task report format: ID · `FIXED|EXPLAINED|DOCUMENTED_LIMITATION` · actions · evidence paths and SHA-256 · manuscript numbers · open limitations · time spent.

REV-1.1 terminal report follows below. Recording an inventory is not a claim that REV-0 gate passed.


## REV-0.4 targeted CI evidence (initial audit; not a terminal task report)

- First CI run `42525152221`: **FAIL** (1 of 3 tests): sentence-final decimal was not recognized; raw log retained in GitHub Actions.
- Correction in commit `b597101e799a56e5170dda97866ec61ba167b168`: numeric-token regex now recognizes sentence-final values without changing any evidence.
- CI run `42525216174`: **PASS (3 tests)**; claim inventory executed with zero evidence mismatches.
- Inventory: active manuscript 13/166 numeric tokens mapped; supplement 0/104; **257 tokens unmapped** (including section labels, version numbers, file paths, and scientific values). This is not 13/166 scientific-claim coverage.
- SHA-256 checked: S7 decision `6b8400e49bad979e3a5e24592615868cc96462724a1545b9fd0c6e54b008cf4c`.
- SHA-256 checked: P3 aggregate `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`.
- SHA-256 checked: physical T4 record `7d6fe31cd59186b6f749cc1b330f6c28a3cf3eff1bce95fa4ca4595d66a9ce82`.
- Those fingerprints are now pinned in the mapping registry; later unexpected evidence changes are an audit error.
- Full-run results and `pre-compstat-revision` tag are separate pending gate items. REV-1 experiments have NOT started.

## REV-1.1 — terminal task report (2026-11-09; ≤15 lines)

- **ID · status:** REV-1.1 · `EXPLAINED` (C2 reporting audit; not a model-identifiability PASS).
- **Actions:** Downloaded all 12 original S7 shard ZIPs from historical workflow [34896442847](https://github.com/ahmadkhanloo/hgfx/actions/runs/34896442847); recomputed per-dataset minimum-BIC winners for all 36 cases from original comparisons, verified case-input digests and model-specific seeds, and inspected generator dispatch.
- **Independent verification:** [Targeted CI run 42526812868](https://github.com/ahmadkhanloo/hgfx/actions/runs/42526812868) PASS; deliberate corruption of one reported matrix count correctly caused FAIL; no new fit or simulation.
- **Evidence:** `evidence/revision/confusion_audit.json`, SHA-256 `0b652e5eda3827ee304281fe0f3ce5000b3651beb968c981765d026b526053b6`.
- **Raw evidence:** twelve artifact/member SHA-256 hashes are pinned in the JSON; archived `aggregate.json` SHA-256 `fcc7ce91383ecb4e46847fba6844f7c91562d98be4997d3745f79f25ba9cfdda`; source decision SHA-256 `6b8400e49bad979e3a5e24592615868cc96462724a1545b9fd0c6e54b008cf4c`.
- **Manuscript figures:** BIC-selection counts (generating rows × winning columns HGF, eHGF, uHGF) = `[[4,2,6],[0,11,1],[4,2,6]]` in **both** MATLAB and HGFX; `36/36` paired winners match; balanced accuracy `0.5833333333333334` (chance baseline `1/3`, descriptive only).
- **Explanation:** Two identical marginal HGF/uHGF confusion rows are genuine: only `4/12` matched-stratum datasets have the same selected model, with `0/12` same seeds, inputs, or responses and `12/12` identical transformed truth vectors. Data generation uses distinct HGF/uHGF model dispatch. Small BIC runner-up margins and the limited grid are consistent with weak separation, not evidence of an aggregation/copy bug.
- **Open limitation:** This audit does not identify a causal scientific/structural identifiability mechanism; REV-1.2 and REV-2.5 address uncertainty/design. S7 historical parameter-recovery failures are preserved.
- **Time spent:** not instrumented precisely; bounded audit completed without rerunning the historical experiment.
- **Phase gate at time of REV-1.1:** REV-1 was incomplete; REV-1.2–1.4 were OPEN. See subsequent REV-1.2 report.


## REV-1.2 — terminal task report (2026-11-09; ≤15 lines)

- **ID · status:** REV-1.2 · `EXPLAINED` (C2 uncertainty audit; historical scientific FAIL unchanged).
- **Protocol before execution:** `evidence/revision/protocols/REV-1.2_PROTOCOL.md` committed at `15907221646aa2664dc8e05b6d0ee6ff5bd32994`.
- **Actions:** Retrieved original 12 S7 shards from run `34896442847`; verified pinned artifact/member SHA-256; no simulations, no fitting, no resampling of original cases.
- **Statistics:** Clopper–Pearson two-sided 95% CIs for convergence and per-class recovery; one-sided and two-sided exact binomial p-values vs chance 1/3; paired-horizon cluster bootstrap for correlations/sRMSE, B=2000, seed `20261109`, with all 2000 draws valid.
- **Primary parameters:** transformed omega2, omega3, log zeta (zero-based free indices `12,13,14`) for each perceptual model; pooled medians are secondary.
- **Raw proof:** `evidence/revision/recovery_uncertainty.json` SHA-256 `e5437e5cbdaced53e811050c19761835672b5c8673b234055e0b8e0b7c46a538`; S7 decision source SHA-256 `6b8400e49bad979e3a5e24592615868cc96462724a1545b9fd0c6e54b008cf4c`.
- **Test:** [workflow 42528948338](https://github.com/ahmadkhanloo/hgfx/actions/runs/42528948338) PASS; five focused tests PASS; no frozen metric changed. Output commit `f0640674f654884929e589f07f03b74c617cfe55` created by verified CI.
- **Figure outputs:** `paper/computational_statistics/figures/fig2_recovery_uncertainty.{png,pdf}` and `fig3_model_recovery_uncertainty.{png,pdf}` plus `revision_figures_manifest.json`, with SHA-256 for each. Historical `paper/figures` untouched.
- **Model recovery (HGF/eHGF/uHGF):** correct `4/12`, `11/12`, `6/12`; 95% CIs `[0.0992,0.6511]`, `[0.6152,0.9979]`, `[0.2109,0.7891]`; one-sided chance p-values `0.606925`, `0.00004704`, `0.177722`; balanced accuracy `0.5833333`.
- **Convergence (HGF/eHGF/uHGF):** `20/24`, `22/24`, `19/24`; original M18 convergence criterion `>=0.80` remains unchanged; uHGF `0.7917` is below it.
- **Example primary diagnostic:** HGF omega3 correlation `-0.3964899554`, 95% paired-cluster bootstrap interval `[-0.6222508675,-0.1253496962]`; this does not establish general structural identifiability.
- **Limitations:** historical deterministic/stratified truths and reused paired horizons limit nominal CI/test interpretation; no general population inference; scientific recovery FAIL preserved.
- **Time spent:** not instrumented precisely; audit completed without heavy computation.
- **Phase gate at time of REV-1.2:** REV-1 remains IN PROGRESS pending REV-1.3/1.4 and D1. The separately verified tag is accounted for under REV-0 below.

## REV-0 terminal reports and gate verification (2026-11-09)

- **REV-0.1 · FIXED:** `compstat-revision` originates from `main` `46fe45e1fdd110a0e72a6dc661bf05c9c38e8885`; lightweight `pre-compstat-revision` tag resolves exactly to that SHA. GitHub Actions run `42529284444` PASS; no historical release tag changed; effort not separately timed.
- **REV-0.2 · FIXED:** committed this ledger, `REVISION_BACKLOG.md`, and REV task registry in `MILESTONES.md`; code and document path links are retained; effort not separately timed.
- **REV-0.3 · EXPLAINED:** listed present/missing oracle workflow, raw evidence, GPU status and active Markdown article in table above. Original S7 shards were subsequently located and verified (REV-1.1); absent `evidence/published_input_41809919116.json` and example directories remain explicit limitations; effort not separately timed.
- **REV-0.4 · FIXED:** `tools/check_manuscript_claims.py` plus pinned JSON claim map, focused tests and operational coverage report; run `42529284493` PASS, while **257 numeric tokens remain unmapped** for later audit. This is a setup/coverage gate only, never the final 100% claims-validation gate; effort not separately timed.
- **REV-0 phase gate · PASS:** branch/tag confirmed, ledger/backlog committed, evidence inventory committed, claims checker runs and prints source coverage. No MATLAB or physical GPU execution was inferred.
- **Current REV-1 phase gate · OPEN:** REV-1.1–1.3 recorded; REV-1.4 and D1 remain outstanding; REV-2 experiments are not authorized.

## REV-1.3 — terminal task report (2026-11-09; ≤15 lines)

- **ID · status:** REV-1.3 · `EXPLAINED` (archived-warning counts and masking association, **NOT** causal classification).
- **Precommitted source-only protocol:** `evidence/revision/protocols/REV-1.3_PROTOCOL.md` at `07ff49a24502d88a799fe662b3ce498818cbacac`, before source-only reconstruction.
- **Original evidence:** workflow [41809919116](https://github.com/ahmadkhanloo/hgfx/actions/runs/41809919116), artifact `13311622738`; ZIP SHA-256 `1adfd1cd69b6f7d7a89ba2c8b9d564e774fd8a8841fa7243d6972605bd9f7391`, embedded JSON SHA-256 `47432c35aa4914a652a8f1dc2aad81dc4d76fb5175dd0fc1fd47532b81756b70`.
- **Archived file availability correction:** complete 324-case `published_input_41809919116.json` found on **separate branch** `paper/published-input-validation-20261108` at `paper/computational_statistics/evidence/published_input_41809919116.json`; it is still absent from `main` and the revision branch, and the CI reads the original artifact rather than copying a narrative aggregate.
- **Reed source-only mask audit:** `ModelDBRepository/258631@39ccaca508b81ca610e7666a613e061c801faaf9/IRL_Data.mat`, exact SHA-256 `b5a2e70a9604221a0d578f9be5fb09567431e51a764a1ac40f5794fb7c14e708`; original row-order, arms, 80-trial masks and per-case ignored-trial counts all verified. No model, objective, simulation or fit was executed.
- **Counts:** 324 source blocks (260 Suthaharan, 64 Reed); **48 warning blocks**, **86 warning events**: 29 blocks × 1, 19 blocks × 3; 293 ignored trials, all concentrated in 48 Reed blocks. All warning-positive blocks have ignored trials; the 276 zero-ignore blocks had zero warnings.
- **Arm cross-tab:** Reed `804020`: 22/32 warning blocks, 44 warning events, 151 ignored trials; `905010`: 26/32, 42 events, 142 ignored trials. Source labels reconstructed using pinned original MAT, not guessed from block ID alone.
- **First ignored position:** 19/48 affected Reed blocks start with a missing trial at zero-based index 0 and carry 3 warnings each (57 events); 29/48 first ignore a later trial and carry 1 warning each (29 events). Complete per-position aggregate histograms are in the JSON.
- **Audited output:** `evidence/revision/warning_crosstab.json`, SHA-256 `630a099912bd6ed44d4ea88ed393ee0a3d412e64b8eb67858da6443c1aa60eb2`; no participant-level outcomes, choices, trajectories or casewise masks committed.
- **Independent CI:** [42531284505](https://github.com/ahmadkhanloo/hgfx/actions/runs/42531284505) **PASS**; 5 focused unit tests PASS, archived ZIP and Reed MAT SHA pins verified, all 324 archived statuses and 64 original Reed masks reconciled. Derived report committed by Actions bot at `28b125f10e6a2cc157ef6f314e2505db1753f194`.
- **Warnings classification limit:** Original status evidence stores **count** only; warning message text/type and causal numerical operation were not archived. This strong index-0 association is **not a proven numerical mechanism**; warning categories and multi-vector sensitivity remain REV-2.1, blocked by D1.
- **Historical scope:** frozen `hgfx==1.0.0` fixed-vector forward parity only, **not** published paper-fitting replication. The failed 326-case prescreen run `41809479255` is retained separately and is not reclassified.
- **Time spent:** not separately instrumented; bounded source-only cross-tab.
- **Gate:** REV-1.3 terminal descriptive audit complete; REV-1.4 **OPEN**, D1 not reached, REV-2 blocked. Final paper 100% claim audit is also still pending.

## REV-1.4 — bounded source-only audit implementation (NONTERMINAL)

- **Status:** IN PROGRESS; **not** FIXED, EXPLAINED, DOCUMENTED_LIMITATION, or REV-1 gate PASS.
- Frozen five-case protocol precommitted at `260483f225d413c0f770a3abed95e267e5e5274c`: `evidence/revision/protocols/REV-1.4_PROTOCOL.md`. Original P3 artifacts 10519038480/10519860062 and original 64-fit artifact 13341288055 verified **present/unexpired in GitHub's archive inventory**, not yet byte-replayed by this revision.
- Source-only Python audit, five independent integrity tests and PR-only workflow authored at `18d82ea00ea4c6afdfda54f7c17adb68608f00b8`. This stage is **not** new paired MATLAB/HGFX execution or optimizer repair. It preserves historical P3 FAIL and subject-7 63/64 NONPASS.
- **Execution evidence:** no REV-1.4 workflow result or committed `first_divergence_audit.json` yet at this ledger update. Do not claim five-case source replay, a first causal intermediate, or test PASS until run/job/artifact hashes are inspected.
- **Next:** obtain one authenticated archive replay via `.github/workflows/compstat-first-divergence-audit.yml`, log actual run and derived JSON SHA-256, then execute only any missing same-input/same-start MATLAB oracle comparisons on the four P3 cases and subject 7. If absent MATLAB/arrays, use the documented terminal limitation after the bounded budget; then present D1 to the author. No REV-2 before D1.

## REV-1.4 — ORIGINAL source archive replay completed (NONTERMINAL; 2026-11-09)

- **Executed independent source-only byte replay**: original P3 artifacts `10519038480` (T=512), `10519860062` (T=1024), and original 64-subject artifact `13341288055` were downloaded from GitHub, materialized locally and verified against their original exact ZIP SHA-256 hashes. The source-original `matlab_raw.json`, `hgfx_raw.json`, and `comparison.json` member SHA-256s were also verified; original P3 shard and case SHA-256s were independently recomputed from case payloads.
- **Immutable result record:** [`evidence/revision/first_divergence_source_replay.json`](../../evidence/revision/first_divergence_source_replay.json) committed at `750c920233f2fe271b3b8206fd604b2fa9f52162`; exact source artifact and case SHA-256s are included. This aggregate includes no participant-level source data, trialwise arrays or refitted outcomes.
- **Original P3 four cases:** T512/R0 MATLAB `negLj=-Inf` (`max_resets`), R4 `247.25740970068986` (converged); T1024/R0 MATLAB `-Inf` (`max_resets`), R4 `620.4345219314272` (converged). In **all four**, original HGFX fit halted with `RuntimeError: Initial recovery fit point is unstable for hgf_binary`. The original P3 comparison does **not** contain an HGFX fitted initial/endpoint vector in these four cases; no inference of same-vector numerical objective parity is permitted.
- **Original 64-fit subject 7:** first original `traj.mu` outside frozen gate is zero-based trial **83**, level **1**, diff `7.841805399477764e-10` vs allowed `7.299856796816515e-10`; `traj.muhat` first outside at trial **84**, level **1**, same numbers. First nonzero float differences (within gate) occur earlier; eight historical above-gate cells remain exactly 4 `mu` + 4 `muhat`. Original scientific **63/64 NONPASS** remains unchanged; no causal intermediate inferred.
- **Remaining / BLOCKED:** original source-only archive evidence does not include matched-initial objective/gradient/intermediate-state MATLAB-HGFX replay for these four P3 cases or the first causal state of subject 7. Current local execution environment has no MATLAB engine or installed HGFX wheel; original historical GitHub artifact was available, but no new MATLAB oracle run or release-wheel forward fit has occurred. The authored PR CI workflow has not yet produced a run on these recent GitHub-app commits, and the five authored unit tests have **not** been claimed PASS.
- **Decision:** REV-1.4 is **IN PROGRESS**, not a terminal task outcome. The source-only audit is actual validated work, but neither `FIXED` nor `EXPLAINED` can be assigned. D1/REV-2 remain blocked. The next bounded diagnostic must compare the same original P3 input and transformed starting vector in frozen MATLAB 8.2.0 versus HGFX 1.0.0, without rerunning the historical P3 grid. Stop/escalate if oracle access is unavailable, rather than redefining the gate.

## REV-1.4 — terminal report and REV-1 audit gate (2026-11-09; terminal)
- **ID / terminal:** REV-1.4 · **DOCUMENTED_LIMITATION** (bounded first-divergence investigation incomplete; this is NOT a proven scientific/model limitation or an implementation repair).
- **Actual source audit:** pinned original P3 archive ZIPs 10519038480/10519860062 and 64-fit ZIP 13341288055 verified against SHA-256; original four P3 case canonical hashes and all eleven raw Subject-7 trajectory fields independently checked locally (read-only; no fit). Earlier archival replay: `evidence/revision/first_divergence_source_replay.json`, blob `db14df55918d6bc3312810412067e2a45af818ed`.
- **Terminal evidence:** `evidence/revision/first_divergence_audit.json` (fixed five IDs, original observed values, unknown cause, terminal classification), exact file SHA-256 `dcad4fa10324cabfad1fd4f7887daa97fcf5f172258d545abf3356b783d4399b`; Git blob `55cc8116df3f1ccc63d2bbd2efccc7e1f0a016b9`. Original artifact ZIP SHA-256 pins are in the JSON.
- **Original P3:** T512 and T1024, scale 0.35, R0/R4; MATLAB `negLj` = `-Inf,247.25740970068986,-Inf,620.4345219314272`; original HGFX `RuntimeError: Initial recovery fit point is unstable for hgf_binary` in all four; this is a **pre-optimizer workflow discrepancy**, not an established first mathematical state mismatch.
- **Original 64-fit:** subject zero-based 7, original 63/64 NONPASS unchanged. First out-of-gate `traj.mu` at trial 83/level 1 and `traj.muhat` at trial 84/level 1, each abs delta `7.841805399477764e-10` > allowed `7.299856796816515e-10`; exactly four offending cells per field. Starts match, but final parameter vectors differ; no same-vector forward causal proof.
- **Missing evidence / blocker:** no matched-initial MATLAB vs HGFX objective/per-trial intermediate trace, no frozen MATLAB runtime in current environment; no validated HGFX-only code fix. Zero code-fix attempts; no threshold/seed/data changes. The source-only audit is PASS for provenance, not science.
- **Tests:** independent local source/hash/11-field checks PASS; authored GitHub REV-1.4 unit tests and new PR CI **NOT RUN**, no CI PASS claimed.
- **Scope consequence:** preserve historical M18 scientific FAIL, P3 FAIL, 63/64 NONPASS and PERF-01C BLOCK_FREEZE; fit-level and causal claims excluded from submission absent further matched-vector evidence.
- **Phase gate:** REV-1.1–1.3 have existing terminal reports; REV-1.4 now has this terminal limitation and evidence. **REV-1 report-completion checklist MET, scientific parity NOT PASS**. D1 is HUMAN PENDING; do not start REV-2.
- **D1 author pack:** `docs/planning/COMPSTAT_D1_DECISION_PACK.md` gives options A (continue COMPSTAT with REV-2.4 priority) and B (prospective retarget); no human choice inferred.
- **Time:** not precisely instrumented; source-only audit and one bounded local validation, no new optimizer experiment.

## REV-1.4 — postterminal local validation (supplement, 2026-11-09)

- The EXACT repository source files were reconstructed and checked against their Git blob SHAs: `tools/audit_compstat_first_divergence.py` = `cf5eb85cc828143c774a242e5d9a50984216c8f9`; `tests/paper/test_compstat_first_divergence.py` = `840ff1e781316ddca53824a07c4ed36867f0550e`.
- **Executed** `python -m unittest discover -s tests/paper -p 'test_compstat_first_divergence.py' -v` on Linux CPU / Python 3.13.5: **5 tests PASS, 0 errors, 0 failures**. This is local targeted validation, **not** the as-yet-unexecuted GitHub Actions Python 3.11 CI workflow.
- **Executed** the checked-in source audit against the three pinned ORIGINAL artifact ZIPs 10519038480, 10519860062, 13341288055; exit code 0; archived original ZIP digests, four case SHA-256/IDs, and subject-7 four `mu` plus four `muhat` above-gate cells verified. Local derived source-only JSON SHA-256: `747c211e006a36537e09cdfbedd9fc248e9d7208750d6673ce0a90122aeaf03b`.
- Repeatable command, environment, Git blobs and unmodified failure flags are recorded in `evidence/revision/first_divergence_local_validation.json`, SHA-256 `1588d972a89962254afe85583f84fb46e2610dc5858f444b3c0b484ff396201f`, blob `96ba1b76f81f9a0d195146970b5212724c11f664`.
- **Unchanged gates:** REV-1.4 terminal `DOCUMENTED_LIMITATION`; scientific MATLAB-HGFX first-cause still unestablished. No fit, optimization, new experiment, tolerance edit, CI/physical GPU claim, or D1 author selection. **D1 PENDING; REV-2 BLOCKED**.


## D1 — author decision recorded 2026-11-10 (terminal human scope choice)

- **HUMAN D1 = OPTION B / RETARGET**. The author explicitly requested a journal change, superseding the earlier request for CompStat. This is an authorized scope decision, not a numerical/scientific PASS.
- Old CompStat REV-0/REV-1 reports remain complete in their original meaning; REV-1.4 `DOCUMENTED_LIMITATION` and its original incomplete MATLAB-oracle trace are unchanged.
- Old REV-2–REV-5 were **not run**, are not counted as PASS, and are not the new publication task queue. Preserve their historical protocol definitions and evidence inventory.
- New active publication track: `docs/planning/SOFTWARE_PUBLICATION_PLAN.md`; hard acceptance gates: `docs/validation/SOFTWARE_PUBLICATION_GATE.md`; venue screen: `docs/submissions/2026-11-10_SOFTWARE_VENUE_SCREEN.md`.
- No particular venue approved yet. *SoftwareX* is conditional editorial/fee candidate; JOSS cannot pass the current six-month public-development requirement; no waiver or zero charges inferred. No paper or preprint was submitted.
- New release/product M0–M20 closed evidence and the separate PERF-01C `BLOCK_FREEZE` remain unaffected. The next open stage is `SWPUB-1` venue/fee verification, NOT old `REV-2.1`.


## D1 — latest author direction A / resume Computational Statistics (2026-11-10)

- **LATEST AUTHOR DECISION: D1 = OPTION A / CONTINUE COMPUTATIONAL STATISTICS**, following the earlier explicit B retarget decision on the same date. The author cited the six-month public-repository age requirement for JOSS. This new explicit instruction supersedes B for future actions; previous B entry and SWPUB-0 paperwork remain preserved as provenance, not deleted or passed into a science gate.
- **Execution authority:** original `COMPSTAT_REVISION_PLAN.md` restored. The next task is **REV-2.4 (C1)**, prioritized because REV-1.4 terminal `DOCUMENTED_LIMITATION` established only the first observed output discrepancy and not the first causal objective/intermediate difference. Remaining REV-2 tasks are open, unexecuted; none is PASS by decision.
- **Science unchanged:** exact immutable source HGFX v1.0.0 `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; MATLAB HGF Toolbox 8.2.0 `2437f4dc241541072722a2695ddeca7b44d83dd3`. M18 parameter recovery scientific FAIL, P3 paired-integrity FAIL, 64-subject 63/64 NONPASS and PERF-01C `BLOCK_FREEZE` all remain.
- **Publication gates still open:** Computational Statistics author charges / subscription route, journal article-format preflight, independent scientific review, strict manuscript claim mapping, D2/D3 and human final submission approval are not complete. **No upload or fee acceptance**.
- **Required immediate next action:** write a bounded `REV-2.4_PROTOCOL.md` with N=200 transformed free vectors per model, D02/D08/64 endpoint cross-evaluation and unchanged frozen objective tolerances; commit it **before** any new execution. If the MATLAB oracle is unavailable, record that condition; never substitute development-branch results for validated 1.0.0 results.

## REV-2.4 — preregistered input-grid implementation and execution gate (2026-11-10; NONTERMINAL)

- **ID:** REV-2.4 / C1, prioritized by author D1 A; **status = IN PROGRESS / IMPLEMENTED BUT NOT SCIENTIFICALLY VALIDATED**. REV-1.4 terminal `DOCUMENTED_LIMITATION` remains unchanged, and historical P3 FAIL / 63-of-64 NONPASS are not retested or overwritten.
- **Preregistered BEFORE execution:** `evidence/revision/protocols/REV-2.4_PROTOCOL.md`, commit `d1986311b8a5ff97f088ebac35c612e16cbe89db`. Locked grid: `N=200` transformed prior-based free vectors each for `hgf_binary`, `ehgf_binary`, `uhgf_binary` (600 total), no exclusion; original model/observation configuration and exact HGFX v1.0.0 vs frozen MATLAB HGF 8.2.0 only; D02/D08 and all original 64 fit endpoints are distinct Panel E.
- **Implementation:** `tools/compstat_rev24_manifest.py` with frozen default seeds, little-endian binary64 input/response hashes, per-case/manifests SHA256, strict fixed/free prior masks, exact 600 denominator, NumPy 2.0.2 and HGFX 1.0.0 non-editable Wheel + installed source-byte guards. Source commits `45cb2b8` and `38b22bb` (initial and strengthened). `tests/paper/test_compstat_rev24_manifest.py` includes **8 authored** pure guard tests (commit `69dff30`), including missing-case, RNG version, mutated fixed parameter and installed Wheel mismatch rejection.
- **CI:** `.github/workflows/compstat-rev24-manifest-contract.yml`, commit `939dd07`, Python 3.11/NumPy 2.0.2 static manifest-contract job. **No new CI execution PASS on this branch has been observed**; authored tests are not declared passed or run here.
- **Scientific source limitations:** current local Python 3.13.5, NumPy 2.3.5, no installed HGFX v1.0.0 or MATLAB command; a configured-index `pip download hgfx==1.0.0` found no matching version. **No frozen manifest was generated and zero MATLAB/HGFX scientific objective evaluations were run.** Runner handoff/commands: `docs/research/REV24_EXECUTION_HANDOFF.md`, commit `9de8334`.
- **Unchanged gates:** M8 existing HGF objective family `rtol=2e-11, atol=2e-13` only, other families cannot claim objective PASS absent a previously registered exact objective tolerance; original M18 fit-field gates unchanged. No threshold, seed, optimizer or archived source evidence changed; no performance/GPU evidence.
- **Next:** run input-contract CI on authorized infrastructure, obtain/pin original `v1.0.0` wheel and real MATLAB 8.2.0 oracle, implement exact source-matched paired evaluators and execute once. If environment remains unavailable, explicitly record `INSUFFICIENT_REFERENCE_EVIDENCE` rather than a scientific PASS. D2/REV-3 remain BLOCKED.

## REV-2.4 — repository source-only preflight (2026-11-10; no scientific run)

- **Source head checked:** `1f9b79c2f31f0a07ec13f45b16faf6f1fef61bb9` (9 additive commits since the prior SWPUB branch head); 19 changed files limited to planning/research/paper text, new REV-2.4 protocol, tools, tests and CI contract — **no changes under `src/`, frozen `reference/validation/v1_release/`, or external reference**.
- **Executed 15/15 static repository checks PASS** against fresh GitHub file content: latest D1 A, original plan authority, preregistration-before-tool chronology, exact 3×200 grid, fixed seeds and original source SHAs, case/manifest hash guards, installed release Wheel-byte guard, eight authored test definitions and NumPy 2.0.2 contract workflow, no v1 science edits, SWPUB history preserved, and critically **no actual `rev24_grid_manifest.json` or `rev24_objective_result.json` output exists**. Script blob `44009c711ee8685b77cde8062db614a4b4f3a43f`, tests blob `57fab23d72430ebc9cd1853c985f65bf51ee99df`, protocol blob `8268ac3af33579e651d1518c094b2d94b2c67ff6`.
- **Scope of this PASS:** source-only governance/static inspection, **not** test execution, semantic validity, MATLAB reference, HGFX 1.0.0 scientific fit, GPU evidence, validation gate or CI workflow PASS. The eight authored unit tests and real oracle paired-evaluation remain unexecuted in the available environment.
- **Next scientific blocker:** authorized Python 3.11/NumPy 2.0.2 with exact PyPI HGFX 1.0.0 installed Wheel bytes plus frozen MATLAB HGF 8.2.0 evaluator for **the identical manifest**. Existing M8 objective tolerance applies only to its documented family; do not invent a gate for other families. See `docs/research/REV24_EXECUTION_HANDOFF.md`.

## REV-2.4 — fixed-vector paired oracle implementation handoff (2026-11-10; NONTERMINAL)

- **Author-approved objective:** D1 A / Computational Statistics; REV-2.4 priority. Original frozen protocol `evidence/revision/protocols/REV-2.4_PROTOCOL.md` at `d1986311` and prospective explicit IEEE NaN fixed-placeholder encoding addendum are preserved; **grid N=200 x 3, original seeds/data/parameter masks and all original scientific thresholds unchanged**.
- **Resolved pre-execution implementation blocker:** immutable v1.0.0 HGF config has undefined `NaN` parameters in the fixed/full transformed vector. Earlier Python manifest generator incorrectly rejected them. Now it encodes literal `"NaN"` in strict JSON while leaving all free draws and case SHA-256 rules unchanged; finite/free and negative/Inf guards added with focused regression cases. No frozen scientific manifest was previously produced or altered.
- **Built end-to-end execution code:** `tools/compstat_rev24_manifest.py` (12 authored tests, no new Actions PASS); `tools/compstat_rev24_hgfx_eval.py` (1.0.0 Wheel only, objective without optimizer); `reference/matlab/run_compstat_rev24_matlab.m` (real frozen HGF 8.2.0 only, **MATLAB execution not performed**); `tools/compstat_rev24_compare.py` (600-case audit, original HGF M8 tolerance only). Full manual-only workflow `.github/workflows/compstat-rev24-original-oracle.yml` retains all inputs/results as Actions artifacts with no automatic global SCIENCE PASS.
- **Provenance hardening:** official PyPI `hgfx-1.0.0-py3-none-any.whl` SHA-256 `5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90` (https://pypi.org/project/hgfx/1.0.0/). PyPI attestation publisher commit `8d46da2` is 10 commits after frozen tag `4dd8fbd` with no `src/hgfx/` changes in GitHub diff; final pre-execution workflow still checks every actual Wheel module against frozen tag bytes and refuses mismatches.
- **Local, genuinely executed validation:** independent synthetic-only comparator tests **9/9 PASS**, Python **3.13.5** (blobs `1402b34246698e4fff623ab94e9a59e96e6d54b5`, `bca56157aeb2a86e40b463a86b40fa0ecba899db`); one isolated undefined-NaN JSON fixed-slot smoke PASS. Neither is full Wheel/runtime test or MATLAB scientific evidence. **12 generator tests authored but not executed/CI-verified on new head**; MATLAB/HGFX evaluators not executed; new GitHub Actions REV-2.4 run count **0** at the time of check.
- **Evidence snapshot:** `evidence/revision/REV24_IMPLEMENTATION_PREFLIGHT_2026-11-10.json`. No `rev24_grid_manifest.json`, `rev24_objective_result.json` or Panel-E cross-endpoint results exist. D02, D08 and all 64 original subjects remain a separately required Panel E, not silently waived.
- **Status:** **REV-2.4 IN PROGRESS / IMPLEMENTED BUT NOT SCIENTIFICALLY VALIDATED**. Scientific gate not PASS; archived M18 recovery FAIL, P3 paired FAIL, subject 7 (63/64 diagnostic NONPASS) and PERF-01C BLOCK_FREEZE retained unchanged. D2 and REV-3 submission claims remain blocked pending real pinned-oracle evidence, family-specific pre-existing tolerances and independent review.


## REV-2.4 — original wrapper fix and Panel E archival preflight (2026-11-10; NONTERMINAL)

- **ID / status:** REV-2.4 C1; `IN PROGRESS`, not `FIXED` or scientific `PASS`; source-only readiness.
- **Code:** corrected MATLAB frozen-family dispatch in `reference/matlab/run_compstat_rev24_matlab.m` (commit `b9c7378fa970f57622933153af6fe941c2d30b4a`), using `pc.prc_fun` rather than nonexistent eHGF/uHGF `*_unified` entrypoints. No frozen model/data/seed/gate modification.
- **Panel E evidence:** original D02 artifact `10339454535`, D08 `10339403480`, 64-fit artifact `13341288055`, all present and unexpired at inspection; original archive SHA-256 pins preserved in `tools/compstat_rev24_endpoint_sources.py`. No archived endpoint values or participant data committed.
- **Validation:** local Python 3.13.5 `python -m unittest discover -s tests/paper -p 'test_compstat_rev24_endpoint_sources.py' -v` = **5 tests PASS**, synthetic ZIP fixture contract ONLY. MATLAB source dispatch contracts authored; no authentic MATLAB invocation.
- **Workflow:** `.github/workflows/compstat-rev24-endpoint-preflight.yml` downloads three original archives and checks hashes, while uploading only sanitized source-identities; actual run and results remain to be independently checked. The original scientific `workflow_dispatch` is still branch-only and **not executed**.
- **Open:** exact original D02/D08/64 endpoint parsing, vector/mask cross-evaluation, single authentic Panel G/G+E oracle result, family-specific existing objective gates, and independent scientific adjudication.
- **Scientific history:** REV-1.4 `DOCUMENTED_LIMITATION`, P3 FAIL, 63/64 original fit NONPASS, M18 recovery FAIL, PERF-01C `BLOCK_FREEZE` unchanged. Manuscript/D2 and author D3 not passed.
- **Detailed handoff:** `docs/research/REV24_EXECUTION_HANDOFF.md` (2026-11-10 continuation). 


## REV-2.4 — real source-coverage CI result (2026-11-10; NONTERMINAL)

- **ID/status:** REV-2.4 / C1; source-only archival gate **PASS**, scientific objective parity **NOT ASSESSED** (original task still IN PROGRESS).
- **Executed:** [Actions run 42773865848](https://github.com/ahmadkhanloo/hgfx/actions/runs/42773865848), head `2585e3b9cb5c88a6734ff8764e9125066418b17c`, completion `success`; tests, three original ZIP SHA-256 checks, input source commit checkout and full-endpoint source-coverage audit passed. No science evaluator invoked.
- **Sanitized evidence:** workflow artifact `13743111655`: `coverage_audit.json` SHA-256 `80c0c60e13e6da3d086d6b4ce5ab301f827044dfc271c64c17d3fb4593745da3`; `source_audit.json` SHA-256 `e5b89d42a4e99cfda3fd704537f178d9907256ba59fff52e096568009651d393`.
- **Numbers:** D02 original MATLAB 15-vector and 320 inputs present, but full original HGFX endpoint not found in pinned archived source; D08 original MATLAB+HGFX 11-vectors and 614 trial inputs complete; original 64 cohort MATLAB+HGFX 64×15 endpoints and 64×128 source inputs complete; original input SHA-256 `6d9b0a2e77c5a2dcc3e3503bf4f52ad8db5695aadbcb3c25bb13cf224db136ae`.
- **Authoritative details:** `docs/research/REV24_PANEL_E_COVERAGE_2026-11-10.md`; original source audit code `tools/compstat_rev24_endpoint_coverage.py` and synthetic-only tests; historical 64 fitting run `41863441006` was **failure**, unchanged.
- **Still OPEN:** D02 HGFX endpoint provenance, true MATLAB/HGFX 1.0.0 Panel G and original Panel E cross-evaluation, prior family gates and independent review. D2/D3 remain blocked; zero new scientific comparisons, zero changed historic thresholds or seeds.
