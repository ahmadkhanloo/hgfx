> **Decision record (current; supersedes this document's original pending-choice language):** On 2026-11-10, the author explicitly selected **Option B: change journal**. D1 is DONE at the venue-category level. *Computational Statistics* is no longer the target. No specific journal, article charge, or final upload was authorized. Existing REV-2–REV-5 criteria remain as historical unexecuted scope, not PASS. New active authority: [Software publication plan](SOFTWARE_PUBLICATION_PLAN.md) and [gate](../validation/SOFTWARE_PUBLICATION_GATE.md).

# D1 author decision packet — Computational Statistics revision

**Status: HUMAN D1 DECIDED — OPTION B, RETARGET (2026-11-10).** Prepared from REV-0 and all REV-1 terminal audit records; this is **not** author approval, independent scientific review, journal acceptance, or permission to proceed to REV-2. Historical M18 scientific FAIL, P3 failed criterion, and PERF-01C BLOCK_FREEZE are preserved.

## Source and revision integrity

- Original immutable HGFX v1.0.0: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; MATLAB HGF 8.2.0 oracle: `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- Branch: `compstat-revision`, [PR #107](https://github.com/ahmadkhanloo/hgfx/pull/107) (draft, not merged).
- Source-only REV-1.4 record: [`first_divergence_source_replay.json`](../../evidence/revision/first_divergence_source_replay.json); terminal disposition: [`first_divergence_audit.json`](../../evidence/revision/first_divergence_audit.json).
- The separate [publication-cycle audit at `58383e8`](https://github.com/ahmadkhanloo/hgfx/commit/58383e81c9e67f7ab2ebe69f4cc262d2c28ce522) suggests a tightly bounded software/compatibility paper and says speed benchmarking is not a prerequisite **if no speed claim is made**. This is a strategy recommendation, **not** an already executed change to the COMPSTAT acceptance plan or D1 signoff.

## REV-1 audit outputs (no heavy new fitting)

| Task | Terminal status | Evidence and exact limits |
|---|---|---|
| REV-1.1 | EXPLAINED | Original 36-case BIC winner reconstruction; MATLAB/HGFX paired winners 36/36; HGF/eHGF/uHGF confusion rows `[4,2,6]`, `[0,11,1]`, `[4,2,6]`; balanced accuracy 0.583333. Equal marginal rows are not copied raw cases. |
| REV-1.2 | EXPLAINED | 95% exact CIs, chance tests and paired-cluster bootstrap (B=2000, precommitted seed); HGF and uHGF recovery remain weak; original parameter-recovery failures unchanged. |
| REV-1.3 | EXPLAINED | 324 original blocks; 48 blocks / 86 warning events, all in Reed ignored-trial blocks; numerical warning message/type and causal mechanism **not archived**. |
| REV-1.4 | DOCUMENTED_LIMITATION | Four exact P3 cases: HGFX stopped at pre-optimizer initial stability guard; MATLAB fit reports were recorded. Subject 7: 8 out-of-gate `mu/muhat` cells in 64-fit original; first threshold exceedance trial 83/level 1. No matched-vector MATLAB objective/intermediate replay: **cause not established**. |

## Scientific claims to retain or exclude

**Supported in frozen scope:** fixed-vector forward comparison on 324 source blocks, original S7 BIC-selection agreement 36/36, uncertainty-qualified and limited model/parameter recovery diagnostics, reproducible provenance. These do NOT imply that original published empirical analyses were replicated.

**Unsupported / must not be stated as established:** complete fitting parity or full 64/64 numerical trajectory parity, generative-model identifiability, numerical harmlessness of warnings, USD/CHF MATLAB fit equivalence/convergence certificate, overall HGFX speedup, physical GPU benchmark on this revision, or end-to-end reproduction of two human studies.

**Specific unresolved C1:** four P3 pre-optimizer HGFX failures vs MATLAB optimizer outputs, plus one subject-7 numerical trajectory failure. `DOCUMENTED_LIMITATION` is a **bounded-investigation outcome**, not a scientific/model limitation diagnosis; no threshold, seed, dataset or original outcome was changed.

## D1 — ONE author choice required before REV-2

**Option A: continue targeting Computational Statistics.** Keep the existing REV-2 scientific agenda, with REV-2.4 same-vector objective/oracle analysis prioritized because C1 is unresolved; do not call the article ready before D2/REV-3/REV-4/REV-5. If MATLAB/GPU are missing, explicitly apply the predeclared per-task fallbacks, limit empirical claims accordingly and keep failed outcomes. Any reduction of compulsory scope requires a separate explicit author decision and prospectively updated acceptance matrix; do not silently delete old tasks.

**Option B: retarget to a software-/methods-oriented venue.** Preserve REV-0/REV-1 evidence; create a new prospective venue-specific scope/acceptance plan after author approval, keep historical COMPSTAT milestone meanings intact, explicitly exclude unmeasured speed claims and unsupported full fitting/replication claims. REV-2 cannot be treated as implicitly passed or retroactively waived.

**Original D1 question — answered 2026-11-10:** author selected **B / retarget**. The resulting active scope is SWPUB, not REV-2. A particular destination venue remains unapproved.

## Administrative state

- REV-1 **audit-documentation phase complete with one documented limitation**; this does **not** mean validation PASSED.
- D1 = DONE (author B / retarget on 2026-11-10). The old COMPSTAT D2/D3 have not occurred and do not govern the new SWPUB article. No submission.
- REV-1.4 source-only replay **and five targeted tests** have now been executed locally on Linux/Python 3.13.5 using the exact committed script/test blobs. Evidence: [`first_divergence_local_validation.json`](../../evidence/revision/first_divergence_local_validation.json), SHA-256 `1588d972a89962254afe85583f84fb46e2610dc5858f444b3c0b484ff396201f`. New branch GitHub Actions Python 3.11 CI and matched MATLAB oracle objective comparisons are **still NOT RUN/PASS**. Do not merge draft PR #107 as submission-ready.


## D1 outcome addendum — 2026-11-10 (append-only)

- **Author decision:** B — retarget journal; confirmed directly in conversation; do not infer a named destination.
- **Prospective candidate:** *SoftwareX* subject to publication fee/waiver clearance and exact author-guideline fit; alternative *Software: Practice and Experience* subscription route subject to novel-contribution assessment. *JOSS* no-fee but currently ineligible for immediate submission due to public development-age gate.
- **Preserved:** REV-1.1 to REV-1.4 reports, original M18 recovery FAIL, P3 insufficient evidence, 63/64 full-fit NONPASS, PERF-01C BLOCK_FREEZE. REV-2–REV-5 are not automatically passed or silently scoped away; the new article has distinct `SWPUB` acceptance gates.
- **No authority implied:** financial commitment, human final claims approval, actual journal submission or preprint upload. Next step `SWPUB-1` venue and cost preflight.
