# P8 Independent Pre-Submission Paper-Delta Review — candidate `b66f294`

## 1. Review identity

| Field | Value |
|---|---|
| Review | P8 independent pre-submission paper-delta review, round 2 |
| Reviewer | Independent Frontier AI Review Agent (four-agent read-only panel + lead re-verification, Qoder CLI). Accountable human: repository owner (sole author). |
| Date | 2026-09-26 |
| Repository | https://github.com/ahmadkhanloo/hgfx (local clones only; no manuscript or review text sent to any external service) |
| Exact candidate SHA | `b66f294f4799968404273127a9b06b4fc451ffb3` |
| Candidate tree | `507c7568ac0c53ccd69c59e630e0f164cbe40284` (verified: `git rev-parse b66f294^{tree}`) |
| Branch containing candidate | `origin/p8-remediation-20260926` (candidate is **not** on `main`; `main` = `3e25792` is an ancestor of the candidate) |
| Lock chain | `b03083c` (docs-only: packet, checklist, delta manifest) → `d24b68e` (docs-only: delta manifest canonicalisation). Verified to change **nothing** outside `docs/research/` and **zero** overlap with the 60 P6A-hashed paths. |
| Review worktree | `D:/Github/hgfx-p8-review-b66f294`, branch `p8-review/b66f294` |
| Gate reproduction HEAD | P2/P5/P6A/tests run at `b66f294`; P7 and the journal build run at `d24b68e` (docs-only descendant; `paper/manuscript.md`, `paper/references.bib` and `docs/research/P7_JNM_PREFLIGHT.md` are byte-identical between them) |

ID convention: findings in this report are prefixed `P8B-` (second paper-delta round). The failed round-1 findings against `c6ef9e5` were `P8-C1`, `P8-H1…H3`, `P8-M1…M13`; they are **not** reused or renumbered here.

## 2. Executive outcome

**FAIL.**

Four of the previous round's blockers are genuinely closed: Figure 4 now derives every plotted value from the committed S9 artifact with the correct criterion per comparison; the journal build renders a real citeproc bibliography (verified 12/12 entries in both DOCX and PDF); the README no longer instructs readers to dispatch a workflow that does not exist; and the candidate is now locked by a provably docs-only commit chain that leaves the scientific tree byte-identical.

P8 cannot PASS because one unresolved **HIGH** remains (P8B-H1): the step that P8 PASS exists to authorise — the final `FROZEN_FOR_SUBMISSION` P6A manifest — cannot pass the repository's own P6A gate. `tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator` compares the committed manifest against `build(ROOT)` in its **default draft mode**, so a frozen committed manifest is guaranteed to differ and redden the P6A workflow. Independently of that blocker, twelve MEDIUM findings remain, five of which touch referee-facing text (undisclosed evidence revision for the headline GPU result, an unsupported `nvidia-smi` residency wording, an undisclosed parity-negative classifier label, a submission artifact with no figures, and internal planning metadata leaking into the journal document).

No scientific threshold, tolerance, seed, dataset, grid, optimiser setting or frozen classification was changed by the remediation, and none was changed by this review.

## 3. Gate reproduction

Environment: Windows 10 x64 (10.0.28000), `core.autocrlf=true`, `uv 0.12.5` ephemeral env `--python 3.11 --with numpy==2.3.3 --with matplotlib==3.10.9 --with 'pytest>=8'` (the exact P5/P6A CI pins), `pandoc 3.11` + MiKTeX `pdflatex` (CI uses apt pandoc + texlive). Full command log: kept out of the repository at `D:/Github/hgfx-p8-review-intake/repro-log-b66f294.txt`.

| # | Command / check | Result | Evidence |
|---|---|---|---|
| 1 | `python paper/scripts/generate_p2_tables.py` | PASS | exit 0 |
| 2 | `git diff --exit-code -- paper/tables/*.md` | **PASS** | exit 0. All 5 hashed `reference/validation/**` inputs check out with 0 CR and their recorded `sha256` matches → the candidate's new `/reference/**/*.{json,tsv} text eol=lf` rule fixed the P2 Windows hash drift. |
| 3 | `python paper/scripts/generate_p5_figures.py` | PASS (run) | exit 0; 6 figures |
| 4 | `git diff --exit-code -- paper/figures/fig_p3_horizon_diagnostics.png paper/figures/p5_figures_manifest.json` | **FAIL off-Linux** | exit 1. All 6 PNGs: **0 differing pixels** (e.g. 0/1,859,596 for Figure 4) and all 6 PDFs byte-identical; the manifest differs for three content reasons (see P8B-M8). |
| 5 | `python paper/scripts/generate_p6a_claim_audit.py` | PASS | exit 0, zero diff; `COMPLETE_P6A_2_NOT_FROZEN`, 45 claims, 10 explicit + 20 auto exemptions, 0 unmapped manuscript lines |
| 6 | `python paper/scripts/generate_p6a_manifest.py` (draft mode) | PASS | exit 0, zero diff, `DRAFT_NOT_FROZEN`, `submission_candidate_sha: null`, 60 files |
| 7 | Recompute all 60 recorded `sha256` against `git cat-file blob b66f294:<path>` | PASS | 0 mismatches |
| 8 | `pytest -q tests/paper` | PASS | 16 passed in 22.1 s — **but the run re-dirties `paper/figures/*`** (see P8B-M8b) |
| 9 | `python paper/scripts/build_journal_submission.py` | PASS | exit 0; produced `paper/dist/journal/HGFX_JNM_submission.{docx,pdf}` |
| 10 | Bibliography rendering audit (lead, by extraction) | PASS | DOCX: `References` heading + **12/12** titles, correct diacritics (`Frässle`), DOI-bearing Chicago entries, no `Bibliography entries are in` placeholder. PDF: 12 pages, **12/12** titles. |
| 11 | `python paper/scripts/check_p7_submission.py --strict` | PASS | `PASS_P7_PREFLIGHT`, `abstract_word_count: 245`, `keyword_count: 6`, `unresolved_bibliography_keys: []`, 0 errors, 0 warnings |
| 12 | `python paper/scripts/generate_p8_delta_manifest.py --candidate-sha 82bbb0c…` | REPRODUCES, WRONG SUBJECT | semantically identical to the committed manifest → the committed delta manifest describes `82bbb0c`, not the reviewed candidate (P8B-M5) |
| 13 | `python paper/scripts/generate_p8_delta_manifest.py --candidate-sha b66f294…` | PASS | 156 files / 214 ahead, `PAPER_REVIEW_REQUIRED` 115, 0 `UNCLASSIFIED`, `frozen_matlab_reference_changed: []`, `frozen_v1_release_evidence_changed: []`; **semantically equal to the locked `d24b68e` manifest** |
| 14 | Frozen evidence: `git diff --name-only c6ef9e5 b66f294 -- reference/ gpu_validation_results/ paper/arxiv/frozen/ tests/golden/` | PASS | empty; `4dd8fbd…` (v1.0.0) confirmed an ancestor of the candidate |
| 15 | Lock-chain containment: `git diff b66f294 d24b68e` outside `docs/research/` | PASS | nothing; 60/60 hashed blobs unchanged |
| 16 | CI run IDs `36242284491/480/539/523/495/568` | **NOT INDEPENDENTLY VERIFIED** | the local-only handling policy blocked the `gh` metadata query; the IDs appear only in lock commit `b03083c:docs/research/P8_REVIEW_PACKET.md` and nowhere in the candidate tree |

## 4. Findings

Each finding gives ID, severity, location, observed evidence, why it matters, reproduction, and required remediation. "Hashed path" = whether a fix changes bytes inside the 60-entry P6A inventory and therefore forces a new candidate SHA and a re-review.

### HIGH

**P8B-H1 — The final P6A freeze cannot pass the P6A gate.** `HIGH` · not a hashed-path fix in the candidate; any remedy changes `tests/paper/**` and so **does** force a new candidate.
- Location: `tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator`; `paper/scripts/generate_p6a_manifest.py::build` defaults; `.github/workflows/p6a-paper-evidence.yml` steps "Regenerate committed P6A manifest mode" and "Run P6A integrity tests"; `docs/research/PAPER_P8_REVIEW_CHECKLIST.md` ("an independent P8 PASS for this exact candidate is a prerequisite for the final P6A freeze").
- Observed: the test asserts `committed == generator.build(ROOT)` with **no** arguments, i.e. `status="DRAFT_NOT_FROZEN"` and `submission_candidate_sha=None`. A `FROZEN_FOR_SUBMISSION` committed manifest can never equal a draft build. The workflow's regenerate step does honour the committed status, so `git diff --exit-code` would stay clean while the very next test step fails.
- Why it matters: P8 PASS exists to authorise the freeze. Handing over a PASS whose immediate next step is guaranteed to redden a required gate is not submission-ready, and the conflict was already listed as an open decision after the previous FAIL.
- Reproduction: read the two files above, or `python paper/scripts/generate_p6a_manifest.py --status FROZEN_FOR_SUBMISSION --candidate-sha b66f294f4799968404273127a9b06b4fc451ffb3` in a scratch clone after filling a PASS Outcome, then `pytest -q tests/paper/test_p6a_manifest.py`. (Not performed here: the review must not perform the freeze, and must not write a PASS it has not issued.)
- Remediation: make the integrity test rebuild in the *committed* manifest's mode (mirror the workflow's status/sha branch), or move the equality assertion behind the draft status, in a new candidate. Do **not** resolve it by deleting the assertion or by loosening the freeze guard.

### MEDIUM

**P8B-M2 — Figure 4's CPU-side number and the evidence map attribute the same claim to two different runs.** `MEDIUM` · hashed path (caption/appendix).
- Location: `paper/manuscript.md:217`, `paper/scripts/generate_p5_figures.py:229-258`, `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` (`source_commit 07b45a56…`), `docs/research/PAPER_EVIDENCE_MAP.md:46`.
- Observed: the plotted/quoted `0.0067837` is `acceptance_summary.fit_backend_max_objective_gap` inside the artifact recorded at `07b45a5…`, whereas the evidence map maps "CPU compatibility and JAX CPU backend preserve tested outputs" to post-review run `35080084517`. No committed artifact carries the post-fix CPU gap value: `fit_backend_max_objective_gap` occurs in exactly one JSON.
- Why it matters: `07b45a5…` predates the fdlibm `exp`/`log` remediation, and that remediation changed exactly the NumPy compatibility path this half of the figure measures.
- Reproduction: `grep -rln fit_backend_max_objective_gap --include=*.json .`; `git show b66f294:gpu_validation_results/m18_s9_physical_gpu_revalidation.json | grep source_commit`; `sed -n '46p' docs/research/PAPER_EVIDENCE_MAP.md`.
- Remediation: commit the post-fix S9 compat output (or state in S5 which run produced the plotted number) and align Figure 4 with it.

**P8B-M1 — Referee-facing text does not disclose that the physical-GPU evidence is a retained pre-release run.** `MEDIUM` · hashed path.
- Location: `paper/manuscript.md:22` (Abstract), `:94` (§2.4), `:154` (§3.4), `:161` (Table 5), `paper/SUPPLEMENTARY_APPENDICES.md` S5.
- Observed: the committed physical-GPU artifact records `source_commit: 07b45a569e04e8e71244c5310dd2cc53dbb2b0ec` (2026-09-15); 64 commits and the release (2026-09-16) follow, including `M src/hgfx/responses/unitsq_sigmoid.py`, `A src/hgfx/math/matlab_log.py`, `M src/hgfx/math/matlab_exp.py`. §2.4:94 states GPU applicability "were tested **after** an independent review of portability blockers (host C runtime `expm1`/`log` paths …); Both blockers were remediated". `grep 07b45a5 paper/SUPPLEMENTARY_APPENDICES.md` → no match.
- Verified by the lead, in the project's favour: the retention argument in `docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md` and `docs/planning/V1_RELEASE_GATE.md:61` **holds** — `git diff --name-status 07b45a5 v1.0.0 -- src/hgfx/gpu/` is empty, `scripts/run_m18_s9_backend_robustness.py` has an identical blob at both revisions, and `src/hgfx/gpu/{fitting,engine}.py` import only `hgfx.compat.configs`/`hgfx.compat.fitting` (the compat *problem definition*), never `hgfx.responses.unitsq_sigmoid`, so the traced JAX objective — used for both the CPU and GPU legs — does not traverse the changed NumPy libm code.
- Why it matters: the conclusion survives, the disclosure does not. A paper whose stated contribution is "an explicit evidence model" must state in the referee-facing text that the physical-GPU row is a retained Kaggle run justified by an executable-path identity argument, and §2.4:94's "tested after" wording must be corrected to "retained after".
- Remediation: one sentence in §2.4/§3.4 plus the revision and identity basis in S5.

**P8B-M3 — `nvidia-smi` process residency is asserted but not evidenced.** `MEDIUM` · hashed path.
- Location: `paper/manuscript.md:154` ("`nvidia-smi` process residency"), `paper/SUPPLEMENTARY_APPENDICES.md:76`.
- Observed: the committed artifact records only `environment.devices ["cuda:0","cuda:1"]` and an `nvidia-smi -L` enumeration (`scripts/run_m18_s9_physical_gpu_revalidation.py:48-49,68`); residency is `gpu_device_resident = gpu_fit.forward.inf_states.devices() == {gpu}` (`scripts/run_m18_s9_backend_robustness.py:291`), a JAX placement check. No process table is committed.
- Why it matters: it overstates the verification method for a headline applicability claim.
- Remediation: "JAX device-placement residency plus `nvidia-smi -L` device enumeration".

**P8B-M4 — The P3 aggregate's parity-negative per-model cause label appears in no paper file.** `MEDIUM` · hashed path.
- Location: `paper/reproducibility/p3_m18c2_aggregate_35272347167.json` (`per_model_classification`: all three models `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`); `paper/manuscript.md:102`, `:142`, S3.
- Observed: `grep -rn IMPLEMENTATION_OR_OPTIMIZER_MISMATCH paper/*.md` → empty. The paper discloses the failed paired-integrity gate and the `INSUFFICIENT_REFERENCE_EVIDENCE` conclusion but not that the frozen classifier attributed the 10/72 winner disagreements to implementation/optimizer divergence.
- Why it matters: the paper's taxonomy explicitly separates implementation mismatch from insufficient reference evidence; omitting the cause label while retaining the outcome is an asymmetric disclosure.
- Remediation: one sentence in §2.6/S3 naming the label and its interpretation limits.

**P8B-M5 — The in-candidate delta manifest describes a two-generation-old candidate.** `MEDIUM` · docs-only.
- Location: `docs/research/P8_DELTA_MANIFEST.json` at `b66f294` (`candidate.sha = 82bbb0c30893651f8ccb15ba27195c3d58bae521`, 179 ahead, 155 files).
- Observed: reproduced by running the generator for that SHA (semantically identical to the committed file). For the reviewed candidate the manifest must describe 214 commits / 156 files, adding `paper/scripts/build_journal_submission.py` as `PAPER_REVIEW_REQUIRED`. Lock commit `d24b68e` carries exactly that content and I verified it equals generator output. The packet itself states P8 run `36242284495` was "PASS for the pre-lock manifest machinery".
- Why it matters: the self-reference constraint means the in-candidate file *cannot* name its own SHA, so this is structurally expected — but the consequence is that **no CI run has ever validated a delta manifest describing `b66f294`**; the binding exists only as locally-reproduced generator output.
- Remediation: dispatch P8 Delta Scope and P6A once on the lock tip and record the run IDs in the packet.

**P8B-M6 — The P8 delta test cannot detect the staleness in M5.** `MEDIUM` · hashed path (tests).
- Location: `tests/paper/test_p8_delta_manifest.py:22-24,40`.
- Observed: `candidate_sha = json.loads(committed)["candidate"]["sha"]`, then `assert payload["candidate"]["sha"] == candidate_sha` — tautological; nothing asserts candidate == `HEAD`.
- Remediation: `assert candidate_sha == git rev-parse HEAD`.

**P8B-M7 — The freeze guard validates an uncommitted file.** `MEDIUM` · hashed path (script).
- Location: `paper/scripts/generate_p6a_manifest.py:135`.
- Observed: `checklist = (repo / "docs/research/PAPER_P8_REVIEW_CHECKLIST.md").read_text(...)` while every inventory byte comes from `_canonical_bytes` (`git show HEAD:`). The checklist is not hashed into the manifest and not in the P6A `git diff --exit-code` list, so an unstaged local edit satisfies `Candidate SHA` / `Reviewer` / `Date` / `` Result: `PASS` ``.
- Why it matters: the machine-enforced link between "an independent PASS is on record" and "the freeze is permitted" can be satisfied by a file that no reviewer ever committed.
- Remediation: read the checklist through `_canonical_bytes`.

**P8B-M8 — Paper gates remain Linux-only, and one newly hashed input still has checkout-dependent bytes.** `MEDIUM` · docs/`.gitattributes` (non-hashed) + generator (hashed).
- Location: `.gitattributes`, `paper/scripts/generate_p5_figures.py:31` (`REQUIRED_INPUTS`) and `:285` (manifest write), `tests/paper/test_p5_figures.py:27-33`, `.github/workflows/regression.yml:21,40`, `docs/research/PAPER_EVIDENCE_MAP.md`, `paper/manuscript.md:94`, `paper/reproducibility/README.md:76`.
- Observed, measured on this host: `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` checks out with 119 CR bytes under `core.autocrlf=true` (`text: unspecified`), giving `sha256 902d06c2…` against the committed `7d6fe31c…`; `p5_figures_manifest.json` additionally records `"path": "paper\\figures\\…"` OS-native separators; PNG bytes differ with **0 pixel differences**; consequently the P5 zero-diff step exits 1. `test_generate_p5_writes_manifest_and_pngs` calls `generator.build(ROOT)` twice against the **real repository**, and `regression.yml` runs `pytest -q` on `windows-latest`, so the Windows regression job mutates committed figure artifacts — observed directly: after `git checkout -- paper/figures`, `pytest -q tests/paper` re-dirtied all six PNGs and the manifest.
- Note the candidate's own `.gitattributes` states "Submission-critical text must have checkout-independent bytes on every OS" and the same commit series broadened `text eol=lf` to `/reference/**` — the newly added `gpu_validation_results/**` input was left uncovered, so the fix is incomplete rather than wrong. (P8-R4's conclusion that the `reference/**` addition is a genuine fix, not a paper-over, is confirmed independently by my P2 zero-diff PASS.)
- Remediation: `/gpu_validation_results/**.json text eol=lf`; emit `/`-separated paths in the P5 manifest; either give the P5 test a `tmp_path` fixture root or restrict paper gates to Linux and say so in the README.

**P8B-M9 — Reproducibility README contains falsified and self-contradictory instructions.** `MEDIUM` · non-hashed (README) except where it changes regenerated outputs.
- `README.md:76` "P6A-1/P6A-2 inventory **59** committed paper evidence/source artifacts" — the committed manifest lists **60**; no test pins the count.
- `README.md:27` still advertises "Replay paired MATLAB oracle / M18C.2 | **yes** (GitHub Actions `matlab-actions`)" while `README.md:102` forbids dispatching it.
- Environment: `pip install -e '.[dev]' matplotlib` resolves unpinned `numpy>=2`/`matplotlib>=3.9`, but P5/P6A pin `numpy==2.3.3`/`matplotlib==3.10.9`, and `uv.lock` resolves neither (numpy 2.4.6/2.5.3, matplotlib 3.11.2) and is never referenced — so the byte-exact P5 path is unreachable from the README as written.
- `JAX_ENABLE_X64=1` / `JAX_PLATFORMS=cpu` appear only as prose (`README.md:88-96`) although `tools/run_p2a10_common_scope.py:282-283` hard-fails with `INVALID_RUN_DO_NOT_INTERPRET` without them.
- Positive: every path referenced by the README exists at this revision; a programmatic sweep of 148 Markdown files found no remaining instruction to run an absent script or workflow.

**P8B-M10 — The canonical journal artifact carries no figures and leaks internal planning metadata.** `MEDIUM` · hashed path.
- Observed by extracting the produced DOCX: `0` image parts, `0` `<w:drawing>` elements, `paper/dist/journal/…docx` contains no media; figure paths appear only as inline code (6 `.png` mentions, Figures 1–6 captions present). Header metadata survives `_strip_placeholder_reference_section`: target journal + "subscription track, no APC", `**Word count (main text, approximate):** 2,400`, `**Abstract:** <=250 words (this draft ~230)`, `**Figures:** 6  **Tables:** 6`.
- Why it matters: a referee opening the only produced artifact cannot see any figure, and neither `check_p7_submission.py` nor `docs/research/P7_JNM_PREFLIGHT.md` states how figures are delivered, so completeness is undecidable from the repository. Draft-facing notes do not belong in a submitted manuscript.
- Remediation: either embed `paper/figures/*.pdf` in the build or record explicitly in P7 that figures are separate submissions; move planning metadata out of the built document.

**P8B-M11 — Bibliography verification is shallower than its PASS suggests.** `MEDIUM` · hashed path (script).
- Location: `paper/scripts/build_journal_submission.py:18-21,72-79`, `.github/workflows/p7-paper-preflight.yml:41-49`.
- Observed: two hard-coded title substrings are checked for 12 references; PDF verification runs only `if shutil.which("pdftotext")`, so the DOCX/PDF PDF assertion is silently skipped on any host without poppler; `if: always()` + `if-no-files-found: error` means a build that raised during PDF generation still uploads a partial DOCX and adds a second, misleading red step.
- Verified adequate, to be fair: actual rendering is correct — I extracted both artifacts and found 12/12 entries with correct diacritics and DOIs, and `check_p7_submission.py --strict` reports `unresolved_bibliography_keys: []`.
- Remediation: assert the rendered entry count equals the number of cited keys and check every title case-insensitively on whitespace-normalised text; fail hard when a required engine is absent; gate the upload on success.

**P8B-M12 — `paper/tables/p3_horizon_summary.md` is declared generated but has no generator.** `MEDIUM` · hashed path.
- Observed: it is listed among P2-generated tables and is P6A-hashed, yet `generate_p2_tables.py` contains no horizon reference and my P2 regeneration neither wrote nor touched it; therefore P6A's `git diff --exit-code -- paper/tables/` gives false assurance for this file. Mitigation verified by the lead: all twelve rows recompute exactly from the committed aggregate (hgf_binary/128 conv 0.917, median r 0.148, median sRMSE 1.114; 512/1024 correctly rendered as gaps with `complete=False`), and its header preserves `INSUFFICIENT_REFERENCE_EVIDENCE` / `gate_pass=false`.
- Remediation: commit a generator, or relabel the file as manually curated evidence-derived text.

### LOW

- **P8B-L1** `paper/manuscript.md:7` declares `**Tables:** 6`; the body contains Tables 1–5. Figures 6 is correct.
- **P8B-L2** `paper/manuscript.md:8` self-reports the abstract as "~230" words; P7's own counter reports **245** (compliant with ≤250, but the declared value is wrong and leaves 5 words).
- **P8B-L3** "confirmed on two Tesla T4 devices" (`:22`, `:154`, `:161`): the measured cells ran on one device (`physical_gpu.device "cuda:0"`) in a hosted/shared environment; two T4s were visible. `PAPER_PROTOCOL.md:285` pre-authorises the 2×T4 scope, so this is imprecision, not a protocol breach.
- **P8B-L4** `:140` attributes "the earlier parameter-recovery failure" to Figure 2/Table 4, but both are generated from the paired S7 artifact; the earlier failure is `reference/validation/m18_scientific_validation.json` (`gate.pass=false`).
- **P8B-L5** `:171` "Typical use after `pip install hgfx==1.0.0` … including the official demo reproductions": `examples/matlab_demo_uhgf_ar1.py:22` needs a frozen-submodule demo input and errors without `git submodule update --init --recursive`; `examples/` is not installed by the wheel.
- **P8B-L6** `:183` "despite sharing the same predicted belief": the mapped quantity differs by 1.1102230246251565e-16 — say "to binary64 rounding scale".
- **P8B-L7** `:112` demo magnitudes `16.99162398501939` / `4.0927117005012175` have no committed machine-readable JSON (`reference/generated/` is gitignored); the claim audit's machine check greps a Markdown document.
- **P8B-L8** P3 provenance (`paper/reproducibility/p3_m18c2_provenance_35272347167.json`) preserves run `35272347167`, executed SHA `a051e747…`, artifact id/digest and aggregate hash `83ccbb7f…`, and I verified the workflow is discoverable from that commit (`a051e747:.github/workflows/pv1-01-m18c2-horizon.yml`). Not preserved: the workflow path itself, the MATLAB release (`release: latest` — the historical execution is therefore not version-reproducible even from the workflow), and that run's package versions; seeds live only in `PAPER_PROTOCOL.md` §4.4, uncited by the file. `a051e747` is reachable from `origin/paper/p3-m18c2-horizon-github-actions`, which is not an ancestor of the candidate; fresh-clone reachability of that ref is UNVERIFIED (external queries not permitted).

### INFO

- **P8B-I1** Remediation discipline was good: the six commits only (i) read committed evidence instead of hard-coding Figure 4 magnitudes, (ii) **tighten** the claim audit with two new value pins, (iii) broaden `text eol=lf`, (iv) replace a false instruction with a provenance pointer, (v) add a canonical builder and wire it into CI. No threshold, tolerance, seed, dataset, grid, optimiser setting or classification string was edited. Three of the six commits are `github-actions[bot]` syncs of regenerated artifacts, and `b66f294` itself removed the one-shot push step (`contents: write` → `read`) — i.e. the artifacts are CI-generated bytes rather than hand-edits.
- **P8B-I2** `README.md:43` "Use the exact locked submission candidate recorded in `docs/research/P8_REVIEW_PACKET.md`" now resolves, but only via lock commit `b03083c`; at `b66f294` itself the packet reads `PENDING LOCK`.
- **P8B-I3** `p6a_paper_evidence_manifest.json` `regeneration_commands` omits `build_journal_submission.py` even though the file is now a hashed generator.

### Panel claims refuted by the lead (recorded so they are not repeated)

- Claimed **CRITICAL**: that `build_journal_submission.py`'s two title constants are "mutually unsatisfiable" and abort the build. **Refuted by execution** — `pandoc 3.11` + `pdflatex` produced DOCX and PDF, exit 0, with 12/12 titles rendered; citeproc title-casing satisfies both constants.
- Claimed **HIGH**: that the committed P6A manifest is stale with three `sha256` mismatches and must fail its gate. **Refuted** — recomputing all 60 entries with the generator's own method (`git cat-file blob`) gives **0** mismatches; the ten apparent mismatches came from comparing this host's CRLF working copies, and my draft-mode regeneration was zero-diff.

## 5. Previous blocker re-check (candidate `c6ef9e5`, review result FAIL)

| Prior blocker | Status | Basis |
|---|---|---|
| 1. Figure 4 / GPU-backend evidence inconsistency (CRITICAL) | **RESOLVED** | `generate_p5_figures.py:229-258` now reads gap and criterion for each comparison from `gpu_validation_results/m18_s9_physical_gpu_revalidation.json`; the previously hard-coded `[1e-14, 1.42108547152e-14]` literals are gone; the file is declared **and actually opened** as a P5 input; plotted ratios are 0.0678371 and 1.42109e-07 against a single 1.0 boundary; label "Compatibility ↔ JAX CPU" verified against the producing script (`run_m18_s9_backend_robustness.py:233-256`: `compat_fit` vs `fit_hgf_binary_unitsq_fast(device=cpu)`); caption values pinned by the claim audit; regenerated PNG shows **0 pixel differences** against the committed figure. Residual concerns about this figure are new defects (P8B-M2), not the prior one. |
| 2. Candidate / provenance lock (HIGH) | **PARTIALLY RESOLVED** | Lock now exists and is coherent: `b03083c` names `b66f294` + tree + `LOCKED … NOT PASSED / NOT FROZEN` and records the six run IDs; provably docs-only (P8B section 1/3). Remaining: the in-candidate delta manifest still describes `82bbb0c`, no CI run has validated a delta manifest for `b66f294` (M5), the delta test remains self-referential (M6), and run IDs are unverifiable from the tree (and were not verified externally here). |
| 3. Obsolete workflow instruction in the reproducibility README (HIGH) | **RESOLVED** | `README.md:102` no longer asks anyone to dispatch a workflow absent from this revision; it points at the committed aggregate plus provenance, and I verified the pointer chain reaches `a051e747:.github/workflows/pv1-01-m18c2-horizon.yml`. Paper-facing artifacts regenerate from the committed aggregate (P3 figure: 0 pixel differences). Residuals: the README's own MATLAB table contradicts the new text and the environment is unpinned (M9), and the historical MATLAB release was `latest` (L8). |
| 4. Bibliography rendering in journal output (HIGH) | **RESOLVED** | Canonical `paper/scripts/build_journal_submission.py` runs pandoc `--citeproc` into DOCX **and** PDF, is hashed as a P6A generator, is executed by the P7 workflow with pandoc/latexmk/poppler installed, and is verified: 12/12 entries present in both artifacts, `Bibliography entries are in …` placeholder stripped and asserted absent, `unresolved_bibliography_keys: []`. The Markdown source legitimately keeps the placeholder because the canonical builder deterministically expands the bibliography. Residual: the self-check is shallow (M11) and the artifact has no figures (M10). |

The round-1 FAIL record is unchanged historical evidence: branch `p8-review/c6ef9e5`, commits `c5b48b2` (findings report) and `57560a6` (checklist dispositions and outcome). Nothing in this report renumbers, softens or reverses it.

## 6. Claim–evidence matrix (material claims)

Verdicts: SUPPORTED / PARTIALLY SUPPORTED / UNSUPPORTED. "Reproduced" = re-derived from the committed artifact during this review.

| # | Claim (location) | Evidence file → field | Reproduced | Verdict | Finding |
|---|---|---|---|---|---|
| 1 | 36/36 BIC winners agree (Abstract, §3.2:140, Fig. 3) | `reference/validation/m18_scientific_validation.json` / `model_selection.winner_matches = 36`, `selection_rule = minimum_BIC` | yes | SUPPORTED | |
| 2 | Max CPU-vs-GPU final-objective gap `1.4210854715202004e-14` vs frozen `1e-7`, 4/4 cells (Abstract:22, §3.4:154, Table 5:161, Fig. 4 caption) | `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` → `physical_gpu.cases[*].final_objective_gap`, `criteria.jax_cpu_vs_physical_gpu_final_objective_gap_max` | yes (values + claim-audit pins) | PARTIALLY SUPPORTED | M1 (run at `07b45a5`, undisclosed) |
| 3 | GPU evidence = applicability, not speed/scaling (§3.4:154, :173, :185) | protocol 1 activates no performance result; `P4 performance/scaling figure is not activated` | yes | SUPPORTED | |
| 4 | Compatibility-vs-JAX-CPU gap `0.0067837` vs criterion `0.10` (Fig. 4 caption) | same JSON → `acceptance_summary.fit_backend_max_objective_gap`, `criteria.compat_vs_jax_cpu_final_objective_gap_max` | yes; label verified against the producing script | PARTIALLY SUPPORTED | M2 (pre-release run; post-fix rerun not committed) |
| 5 | Two demo workflows reproduce the reference at frozen tolerances; uHGF→uHGF-AR(1) maxima 16.99162398501939 / 4.0927117005012175 (§2.5:110-112) | `docs/user/MATLAB_DEMOS.md:112-113`, `examples/matlab_demo_uhgf_ar1.py:54-55` (no committed JSON) | values consistent across committed prose | PARTIALLY SUPPORTED | L7 |
| 6 | D02/D08 are matched reference limitations, not recovery successes (§2.7, Table 3, :173) | `reference/validation/m18_{d02,d08}_reference_limitation/decision.json` = `REFERENCE_LIMITATION_MATCH` with `direct_gate_status = FAIL_PRESERVED` | yes (manifest pins) | SUPPORTED | |
| 7 | Historical M18 failure preserved (§3.2:140, Fig. 2, Table 4) | `reference/validation/m18_scientific_validation.json` `gate.pass = false`; manifest `historical_m18_scientific_validation = FAIL_PRESERVED` | yes | SUPPORTED | L4 (figure/table actually come from S7) |
| 8 | S7 paired recovery metrics (Table 4 rows 0.833/0.203/2.610, 0.917/0.462/2.359, 0.792/0.381/2.958) | `paper/tables/recovery_model_selection.md` ← `reference/validation/m18_s7_reference_limitation/decision.json` | yes (P2 zero-diff) | SUPPORTED | |
| 9 | Trial-horizon gate failed: 10 of 72 BIC winners disagreed, all classic binary HGF at 512/1024 (§2.6:102) | `paper/reproducibility/p3_m18c2_aggregate_35272347167.json` → `total_cases 72`, `winner_matches 62`, mismatch set | yes | SUPPORTED | |
| 10 | P3 evidence insufficient; 128/512 are trajectory diagnostics only (§2.6, §3.2:142, Fig. 6 caption) | `overall_classification = INSUFFICIENT_REFERENCE_EVIDENCE`, `gate_pass = false`, `coverage_pass = false`, `per_model_classification` | yes | PARTIALLY SUPPORTED | M4 (cause label undisclosed) |
| 11 | Twelve diagnostic rows (conv/median r/sRMSE; 512/1024 gaps) | recomputed from `parameter_recovery[*].horizons[*].matlab` | yes, 12/12 exact | SUPPORTED | M12 (file has no generator) |
| 12 | 11 mapped pyhgf quantities pass; 1.11e-16 … 1.55e-15 (§3.5:164) | `paper/reproducibility/p2a10_comparison_35268575414.json` | yes | SUPPORTED | |
| 13 | Response NLL not directly comparable; 13 boundary trials at `ze = 48`; HGFX total NLL 1808.855415351429; pyhgf +Inf (§3.5:166) | `p2a10_raw_numeric_result_35268575414.json`, `PYHGF_COMMON_SCOPE_NUMERICAL_RESULT.md`; manifest `pyhgf_participant_response_nll = NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` | yes | SUPPORTED | |
| 14 | Abstract: "no general faster/first/only claim" | every `faster/first/only/speed/scaling/throughput` occurrence is a disclaimer (`:22, :30, :32, :154, :173, :185`) or a benign restrictor/ordinal (`:63, :98, :110, :191, :207`) | yes | SUPPORTED | |
| 15 | `nvidia-smi` process residency (§3.4:154, S5:76) | artifact holds only `nvidia-smi -L` enumeration; residency = JAX `inf_states.devices()` | yes (negative) | UNSUPPORTED as worded | M3 |
| 16 | Frozen oracle = HGF Toolbox 8.2.0 @ `2437f4dc…` (Table 1:59, §2.2:73) | `reference/HGF_VERSION`, `reference/HGF_COMMIT`, submodule gitlink | yes | SUPPORTED | |
| 17 | HGFX 1.0.0 @ `4dd8fbd…`, MIT, PyPI `hgfx==1.0.0` (Table 1, :171) | tag `v1.0.0`, `LICENSE`, `reference/validation/v1_release/*` | ancestry + tag verified; PyPI publication not checked (no external query) | SUPPORTED (publication UNVERIFIED) | |
| 18 | Highlights (5 items ≤85 chars) each supported | `paper/highlights.txt` lengths 71/74/75/73/65 | yes | SUPPORTED | |
| 19 | "Tables: 6", abstract "~230 words" (header:7-8) | 5 numbered tables; P7 `abstract_word_count = 245` | yes | UNSUPPORTED as written | L1, L2 |
| 20 | Figure 4 caption ↔ figure ↔ artifact | see blocker re-check row 1 | yes (0 pixel diff) | SUPPORTED | |
| 21 | All 12 citations resolve and render | `paper/references.bib` (12 keys) ↔ 12 unique cited keys, multi-cite groups expanded; DOCX/PDF extraction | yes | SUPPORTED | M11 (verification depth) |

## 7. Scientific integrity checks (immutable classifications)

| Item | Committed value | Manuscript framing | Status |
|---|---|---|---|
| Historical M18 scientific validation | `gate.pass = false`; manifest `FAIL_PRESERVED` | §3.2:140 keeps the failure in the record; not reclassified | PRESERVED |
| D02 / D08 / S7 | `REFERENCE_LIMITATION_MATCH` with `direct_gate_status = FAIL_PRESERVED` | §2.7, Table 3, limitations (ii) | PRESERVED — not presented as scientific PASS |
| P3 trial horizon | `INSUFFICIENT_REFERENCE_EVIDENCE`, `gate_pass = false`, `coverage_pass = false` | §2.6 "did not pass"; §3.2 "not a positive identifiability result"; Fig. 6 caption | PRESERVED — no upgrade to identifiability PASS; per-model cause label undisclosed (M4) |
| pyhgf common scope | one authorized 128-trial cell; `PASS_EXACT` on 11 mapped quantities | §3.5, limitations (v) "one mapped cell, not package-wide equivalence" | PRESERVED — scope not widened |
| Response NLL | `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` | §3.5 remains NDC with the +Inf boundary explained | PRESERVED |
| GPU scope | applicability/correctness; `criteria` 1e-7 | §3.4:154, :173 (iv), :185, Fig. 4 caption "Not a speed claim" | PRESERVED — but the tested revision is undisclosed (M1) and residency wording overstates method (M3) |
| Parity vs identifiability | distinct classes kept distinct throughout | `:140` "Model-selection agreement is not used to imply strong parameter identifiability" | NOT conflated |

## 8. Reproducibility assessment

Sufficient for the claimed scope **on Linux, with named gaps**. A reader can: clone, verify the reference freeze, regenerate P2 tables (I confirmed byte-exact content on Windows), regenerate P5 figures and P6A outputs, and rebuild the journal DOCX/PDF. Every script and file the README names exists at this revision, the aggregate/raw hashes are consistent across all committed locations, and seeds are derivable from `PAPER_PROTOCOL.md` §4.4.

Insufficient or misleading in these respects: paper-gate byte-exactness is Linux-only and undocumented as such (M8); the README's artifact count is wrong and its MATLAB table contradicts its own prohibition (M9); the paper environment is unpinned relative to CI pins and the P2A10 hard requirement is prose-only (M9); P3's MATLAB release was `latest` so that historical execution is not version-reproducible (L8); `p3_horizon_summary.md` has no generator (M12).

## 9. Submission-output assessment

Built here by the canonical path: `paper/dist/journal/HGFX_JNM_submission.docx` and `.pdf` (12 pages).

- **DOCX bibliography: rendered.** `References` heading, 12/12 entries, Chicago author–date, DOIs present, diacritics intact (`Frässle`, en-dashes, curly quotes; no replacement characters), placeholder absent.
- **PDF bibliography: rendered.** 12/12 entries recoverable by text extraction; placeholder absent.
- In-text citations: `check_p7_submission.py --strict` reports `unresolved_bibliography_keys: []`; 12/12 bidirectional key coverage confirmed independently with multi-cite expansion.
- **Figures: absent from both artifacts** (M10).
- Declarations: author, affiliation, corresponding email (`m.ahmadkhanloo@ipm.ir`, matching the approved constant), funding, competing interests, CRediT sole authorship, acknowledgments, dual AI disclosures, code and data availability, MIT + GitHub + PyPI wording all present; no placeholder and no invented identifier found.
- **`FROZEN_FOR_SUBMISSION` was not attempted** (prohibited, and see P8B-H1). The draft manifest remains `DRAFT_NOT_FROZEN` with `submission_candidate_sha: null`, and `test_p6a_manifest.py` pins exactly that — so the P6A suite is green only while the manifest is unfrozen.

## 10. Final blocking status

Unresolved CRITICAL: none.

Unresolved HIGH: **P8B-H1** — the P6A freeze step that a P8 PASS authorises cannot pass the repository's own P6A integrity test.

Recommended-before-submission MEDIUM set: M1, M2, M3, M4 (referee-facing disclosure/wording), M10, M11 (submission artifact), M5–M9, M12 (provenance and reproducibility machinery). None of M1–M4 can be fixed inside the candidate: all four edit `paper/manuscript.md` or `paper/SUPPLEMENTARY_APPENDICES.md`, which are P6A-hashed.

## 11. Final P8 decision

**FAIL** for `b66f294f4799968404273127a9b06b4fc451ffb3` (tree `507c7568ac0c53ccd69c59e630e0f164cbe40284`).

This is a narrow FAIL. No previously filed blocker remains open in the form it was filed; no scientific claim in the manuscript is numerically wrong; every immutable classification is preserved; and the science of the remediated Figure 4 and of the bibliography build is now correct and locally reproducible. The obstruction is one verified HIGH process defect plus a referee-facing disclosure gap around the GPU evidence revision. Both have short, concrete fixes.

Minimum path to a passing candidate, in order:

1. Resolve P8B-H1 in `tests/paper/test_p6a_manifest.py` (rebuild in the committed manifest's mode), so the freeze can be CI-green.
2. Reword `paper/manuscript.md:94` and disclose in §3.4/S5 that the physical-GPU row is retained from `07b45a5` on a verified executable-path identity argument, and correct the residency wording (M1, M3).
3. Bind Figure 4's CPU number to a committed post-fix artifact, or state which run produced it (M2).
4. Disclose the P3 per-model cause label (M4).
5. Fix `.gitattributes` coverage, P5 path separators and the mutating P5 test; correct the README's count/MATLAB-table/environment/JAX-var gaps (M8, M9).
6. Make the journal build figure-complete and strip draft metadata (M10), and deepen its bibliography check (M11).
7. Land a docs-only lock commit naming the new SHA and tree; dispatch P2/P5/P6A/P7/P8-delta/regression on it; then request a fresh P8 review of that exact SHA (M5, M6, M7).

## 12. Independence, limits and handling

- The reviewer modified no implementation, manuscript, evidence, figure, threshold, seed, dataset, grid, optimiser setting or classification, and performed no remediation. Repository writes in this round are limited to `docs/research/P8_INDEPENDENT_PAPER_DELTA_REVIEW.md` and `docs/research/PAPER_P8_REVIEW_CHECKLIST.md`, in review-only commits on branch `p8-review/b66f294`.
- No push, PR comment, merge, tag, freeze, `workflow_dispatch` or external publication occurred. `gh` run-metadata verification was blocked by the local-only handling policy and was **not** worked around; the six claimed run IDs therefore remain documentary.
- Panel independence limits: four read-only agents and the lead share one underlying model family, so this is a multi-pass review, not four independent expert opinions. Two panel HIGH/CRITICAL claims were refuted by the lead's own execution (§4) and are excluded from the findings list. Agent findings quoted without independent re-derivation are marked by their locations; every CRITICAL/HIGH-grade item in §4 was verified by the lead directly.
- Not reviewed by design: the v1.0.0 implementation and release-integrity baseline (accepted prior review at `ad8f5cd6…` → `09c49031…`), unchanged golden-reference/M1–M17 parity surfaces, and MATLAB-side re-execution (no MATLAB available).
- Environment deviations recorded: Windows host with `core.autocrlf=true`; `pandoc 3.11` + MiKTeX instead of apt pandoc + texlive; no physical GPU, so no CPU-vs-GPU re-measurement was possible; PNG byte nondeterminism versus the committed figures with zero pixel differences.
