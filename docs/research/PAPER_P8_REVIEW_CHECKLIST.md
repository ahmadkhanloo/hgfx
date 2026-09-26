# P8 Independent Pre-Submission Review Checklist

Status: **INDEPENDENT PAPER-DELTA REVIEW COMPLETED / RESULT FAIL / ONE UNRESOLVED HIGH**
Failed reviewed candidate: `c6ef9e5f4113e373a5d492cb73c9dbe0fe89fd28`  
Replacement candidate SHA: `b66f294f4799968404273127a9b06b4fc451ffb3`  
Candidate tree: `507c7568ac0c53ccd69c59e630e0f164cbe40284`
Review packet: `docs/research/P8_REVIEW_PACKET.md`
Delta manifest: `docs/research/P8_DELTA_MANIFEST.json`
Findings report: `docs/research/P8_INDEPENDENT_PAPER_DELTA_REVIEW.md`
Tracking: PV1-02 / GitHub issue #32
This is **not** M19 and is **not** an implementer self-review.

The Replacement candidate SHA above records the exact commit this reviewer examined. It is **not**
a lock: the lock is the documentation-only commit chain `b03083c` -> `d24b68e`, which the reviewer
did not author and which was verified to change nothing outside `docs/research/` and nothing among
the 60 P6A-hashed evidence paths.

Use this checklist on the exact submission candidate after:

- [x] P3 aggregate is committed at `paper/reproducibility/p3_m18c2_aggregate_35272347167.json`, hash-verified as `83ccbb7f...31b4`, and classified under `m18c2-trial-horizon-identifiability-1` as `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`; **VERIFIED** (blob hash matches; classification and `gate_pass=false` preserved; Figure 6 regenerates with zero pixel difference).
- [x] P3 diagnostic Figure 6 is generated from that committed aggregate, committed as `paper/figures/fig_p3_horizon_diagnostics.png`, and zero-diff gated by P5 CI; **VERIFIED on Linux; NOT reproducible byte-exact off-Linux** (see P8B-M8).
- [x] the P6A draft evidence manifest and P6A-2 numerical claim audit are complete and reproducible; **VERIFIED** (both regenerate zero-diff on this host; all 60 recorded `sha256` match `git cat-file`; 45 claims, 0 unmapped manuscript lines). (both regenerate zero-diff; all 60 recorded `sha256` match `git cat-file`; 45 claims, 0 unmapped lines).
- [x] replacement P7 submission-candidate SHA is locked; strict P7/P6A/P2/P5/regression gates pass on that exact SHA; **QUALIFIED**: the lock exists (`b03083c`/`d24b68e`, docs-only), and P2/P6A/P7/tests/claim-audit reproduce locally, but no CI run has ever validated a delta manifest describing this candidate (P8B-M5) and the six run IDs could not be verified externally under the local-only handling policy.

The final `FROZEN_FOR_SUBMISSION` manifest is intentionally **post-P8**: an independent P8 PASS for this exact candidate is a prerequisite for the final P6A freeze.

Do not treat this file as a completed review. An independent reviewer must fill it.

## Prior independent baseline

The repository already contains a completed independent frontier review at `docs/validation/INDEPENDENT_REVIEW_REPORT.md`, with remediation at `docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md`.

Accepted baseline:
- reviewed source: `ad8f5cd6fbea3bd1e5ac1cef8b51dbbb9a970a84`;
- H1/H2 were HIGH release blockers and are both RESOLVED;
- post-remediation status: no unresolved CRITICAL/HIGH findings;
- this baseline covers the v1 implementation/release integrity areas actually examined by that review.

Do **not** re-review unchanged baseline areas merely to satisfy P8 bookkeeping. Review only the paper/post-review delta and any changed evidence that could alter a manuscript claim.

## Scope

Review `paper/manuscript.md`, `paper/tables/`, `paper/figures/`, `paper/reproducibility/`, and the paper evidence map. Historical v1.0.0 gates remain closed.

## Required classifications

Every finding: `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `INFO`.

Submission is blocked by unresolved `CRITICAL` or `HIGH` findings.

## Checks

### Scientific overclaiming

- [x] Abstract claims only frozen, scoped results. **PASS** — every Abstract sentence traces to a committed artifact; the one qualification is that the physical-GPU row is a retained pre-release run (P8B-M1), not a misstated number.
- [x] No general HGFX-faster-than-MATLAB/pyhgf claim. **PASS** — all `speed/faster/throughput` occurrences are disclaimers (`manuscript.md:22, :154, :173, :185`).
- [x] No general multi-GPU scaling claim. **PASS** — `:32` and `:185` disclaim scaling; `:185`'s "engineering capability" phrasing is hedged and graded INFO, not a reported law.
- [x] No claim that HGFX is the first/only Python or JAX HGF. **PASS** — `:30` states the negation explicitly; all other `only/first` hits are restrictors or ordinals.
- [x] D02/D08 remain `REFERENCE_LIMITATION_MATCH`, not scientific PASS. **PASS** — decisions unchanged; `FAIL_PRESERVED` retained underneath.
- [x] Historical M18 remains FAIL / preserved. **PASS** — with a citation misattribution graded LOW (P8B-L4: Figure 2/Table 4 come from S7, not from the earlier M18 gate).
- [x] P3 classification matches the preregistered 256→1024 rules; 128/512 are not substituted. **PASS with finding** — `INSUFFICIENT_REFERENCE_EVIDENCE` / `gate_pass=false` intact and never framed as identifiability success, **but** the aggregate's per-model `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH` cause label appears in no paper file (P8B-M4).
- [x] pyhgf comparison remains the single authorized common-scope cell; response NLL remains NDC if still nonfinite. **PASS** — `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY` preserved; `+Inf` and 13 boundary trials reported honestly.

### Evidence traceability

- [ ] Every numerical sentence maps to a committed artifact in `docs/research/PAPER_EVIDENCE_MAP.md`. **FAIL** — the CPU-backend gap plotted in Figure 4 maps to the `07b45a5` artifact while the evidence map assigns the same claim to post-fix run `35080084517`, whose numbers are committed nowhere (P8B-M2); the demo magnitudes at `:112` have no machine-readable artifact (P8B-L7).
- [x] P2 tables regenerate with zero Markdown diff. **PASS** — reproduced on Windows; the new `/reference/**` `text eol=lf` rule resolved the previous CRLF hash drift.
- [ ] P5 figures regenerate from committed inputs. **FAIL** — content is correct and shows **zero pixel difference**, but the committed byte-exactness is Linux-only: a newly hashed input is still CRLF-converted on checkout, the manifest stores OS-native path separators, and a paper *test* mutates committed figures during the Windows regression job (P8B-M8).
- [x] P3 aggregate SHA-256 matches the frozen Actions artifacts. **PASS** — `83ccbb7f...31b4` consistent across the aggregate blob, provenance file, README, manifest anchor and test pin.
- [x] P6A draft manifest and P6A-2 claim audit reproduce with zero diff and do not modify M19. **PASS** — both zero-diff; `separate_from_m19: true`; draft mode untouched.
- [x] Candidate SHA in this review matches the exact P7 lock. **PASS via the lock chain** — `b03083c`/`d24b68e` name this SHA and tree; the manifest *inside* the candidate still describes `82bbb0c`, and no CI run has validated a delta manifest for `b66f294` (P8B-M5); the delta test cannot detect that (P8B-M6).
- [ ] If the review result is PASS, final P6A freeze is performed afterward for this exact candidate SHA. **NOT APPLICABLE — this review is FAIL**; and the step is currently blocked by P8B-H1, with the freeze guard satisfiable by an uncommitted checklist edit (P8B-M7).

### Reproducibility

- [ ] `paper/reproducibility/README.md` is sufficient without chat history. **FAIL** — sufficient for P2/P6A on Linux, but it miscounts the inventory (59 vs 60), contradicts itself on whether the M18C.2 Actions step exists, leaves the paper environment unpinned relative to CI pins, and states the P2A10 hard requirements only as prose (P8B-M9). All referenced paths exist; no instruction names an absent script or workflow any more (previous blocker RESOLVED).
- [x] MATLAB-required vs MATLAB-free steps are explicit. **PASS with finding** — the table exists and is now paired with a correct historical-provenance paragraph, but its M18C.2 row still advertises a workflow the same file forbids dispatching (P8B-M9).
- [ ] Exact SHAs, tags, package versions, and seeds are recorded. **FAIL** — the physical-GPU and compat artifacts record pre-release SHAs that the paper does not disclose (P8B-M1, P8B-M2), and the P3 historical run pinned `release: latest` with no environment sidecar (P8B-L8). Seeds and the v1.0.0/oracle SHAs themselves are correctly recorded.
- [x] Failed simulations/fits were retained, not dropped. **PASS** — `10 of 72` disagreements and the invalid 512/1024 trajectories are retained as gaps in the aggregate, Figure 6 and the summary table.

### Consistency

- [ ] Abstract, Results, tables, figures, and supplement agree. **FAIL** — one claim carries two provenances (P8B-M2); the residency method is described as `nvidia-smi` process evidence while only device placement is committed (P8B-M3); header metadata contradicts the body on table count and abstract length (P8B-L1, L2). No result carries two different *classifications*.
- [x] Figure captions match file contents. **PASS** — Figure 4 verified caption-vs-code-vs-artifact with zero pixel difference; Figure 6 verified against the hash-checked aggregate.
- [x] Bibliography keys resolve; pyhgf citation is present and fair. **PASS** — 12/12 bidirectional coverage with multi-cite expansion, `unresolved_bibliography_keys: []`, and pyhgf/TAPAS positioned accurately and non-disparagingly.

### Metadata

- [x] Authors, affiliations, corresponding author. **PASS** — sole author + CRediT statement; corresponding email matches the repository's approved constant. No ORCID is asserted, and none was invented here.
- [x] Funding, conflicts, acknowledgments. **PASS** — present, specific, no placeholder.
- [ ] Target-journal template applied. **FAIL** — the canonical journal DOCX/PDF render a complete bibliography but contain **no figures**, and they carry draft planning metadata including the venue and APC posture (P8B-M10).
- [x] License/data/code availability wording matches MIT + GitHub + PyPI. **PASS** — `LICENSE` is MIT; tag `v1.0.0` -> `4dd8fbd…`; PyPI publication itself was not externally verified under the local-only policy.

### Process

- [x] Documentation-only commits after the candidate lock do not silently modify the reviewed candidate. **PASS** — `b66f294..d24b68e` changes nothing outside `docs/research/` and none of the 60 hashed paths.
- [x] Reviewer performed no remediation and no freeze. **PASS** — writes limited to the two review documents in this branch.

## Outcome

Reviewer: Independent Frontier AI Review Agent (four read-only panel passes plus lead re-verification, via Qoder CLI). Accountable human: repository owner (sole author).
Date: 2026-09-26
Candidate SHA: `b66f294f4799968404273127a9b06b4fc451ffb3`
Result: `FAIL`

Blocking finding: **P8B-H1** — `tests/paper/test_p6a_manifest.py::test_committed_p6a_manifest_matches_generator`
rebuilds the manifest in default draft mode and asserts equality with the committed file, so a
`FROZEN_FOR_SUBMISSION` manifest can never pass the P6A workflow. The freeze is the step a P8 PASS
exists to authorise, so it cannot be handed over green.

Unresolved CRITICAL findings: none. All four `c6ef9e5` blockers were re-checked: Figure 4 **RESOLVED**
(every plotted value now derives from the committed S9 artifact with the correct criterion per
comparison, verified against the producing script, zero pixel difference on regeneration); the
obsolete workflow instruction **RESOLVED**; bibliography rendering **RESOLVED** (12/12 entries rendered
in both the canonical DOCX and PDF, placeholder asserted absent); the candidate/provenance lock
**PARTIALLY RESOLVED** (a provably docs-only lock chain exists and was verified not to touch the
candidate, but the in-candidate delta manifest still describes `82bbb0c` and no CI run has validated a
delta manifest for this SHA).

Twelve MEDIUM findings remain (P8B-M1…M12), of which five touch referee-facing text or the submission
artifact — most consequentially that the physical-GPU result is a retained pre-release run whose
executable-path identity argument the reviewer verified as sound but the manuscript never discloses
(P8B-M1), and that Figure 4's CPU-side number is attributed to a different run than the evidence map
(P8B-M2). Eight LOW and three INFO items are recorded in the findings report.

The previous FAIL against `c6ef9e5` is unchanged historical evidence (branch `p8-review/c6ef9e5`,
commits `c5b48b2`, `57560a6`) and is not rewritten, renumbered or softened by this review.

No scientific threshold, tolerance, seed, dataset, model grid, optimiser setting or frozen
classification was altered by the remediation or by this review. No merge, tag, pull-request,
`workflow_dispatch` or P6A freeze was performed. The owner subsequently authorised publishing this
record by pushing the review branch alone (`p8-review/b66f294`, review-only commits `4370342`,
`f390e23` and this document's outcome commit), leaving `main`,
the candidate branch and the lock chain untouched; no manuscript or review text was sent to any
third-party service.
