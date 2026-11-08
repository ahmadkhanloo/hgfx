# Computational Statistics revision ledger

**Scope:** `COMPSTAT_REVISION_PLAN.md`; working branch `compstat-revision`.
**Baseline main commit:** `46fe45e1fdd110a0e72a6dc661bf05c9c38e8885` (2026-11-08).
**Historical release evidence:** HGFX v1.0.0 at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; immutable.
**Phase:** REV-1 audits are IN PROGRESS; REV-1.1 and REV-1.2 are `EXPLAINED` with committed evidence. REV-0 baseline tag remains outstanding.
**Gate REV-0:** NOT PASSED until baseline tag verified. REV-0.4 focused CI PASS is an inventory, not final 100% numeric-claim coverage.

## REV-0.3 verified repository inventory (2026-11-09)

| Plan expectation | Checked result at baseline | Status |
|---|---|---|
| Revision branch | `compstat-revision` created from recorded `main` SHA | CREATED |
| `pre-compstat-revision` tag | Not present in Git refs; connected GitHub tools cannot create tags | HUMAN_ACTION / OPEN |
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
- **Phase gate:** REV-1 remains IN PROGRESS pending REV-1.3/1.4 and human decision D1; REV-0 tag remains OPEN.
