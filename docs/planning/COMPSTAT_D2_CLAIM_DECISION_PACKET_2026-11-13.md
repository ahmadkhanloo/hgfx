# Computational Statistics — D2 scientific-claim decision packet (2026-11-13)

**Decision status:** D2 **BLOCKED / AUTHOR NOT YET APPROVED**. This packet is an evidence-led editorial disposition, not an independent scientific acceptance, new protocol, retrospective threshold, or journal submission.

**Target:** *Computational Statistics* software/package article (author D1=A). **Current candidate:** `paper/computational_statistics/manuscript.md` and `paper/SUPPLEMENTARY_APPENDICES.md` on `compstat-revision`. The immutable HGFX 1.0.0 wheel is the paper software baseline. See [publication objective](PUBLICATION_FIRST_OBJECTIVE_2026-11-13.md), [readiness](COMPSTAT_SUBMISSION_READINESS_2026-11-12.md), and [REV ledger](COMPSTAT_REVISION_LEDGER.md).

## C1–C8: reader-facing disposition, with remaining decision

| Criticism | Defensible statement or required correction | Current gate |
|---|---|---|
| C1 — fit agreement overstated | Separate same-vector classic-HGF objective comparisons (Panel G 164/200 jointly-valid within original criterion, 36 jointly invalid; Panel E 128/128 tested classic-HGF endpoint slots) from **fitted-parameter/optimizer** parity. Enhanced/unbounded families lack original family-wide gates. The original one-sided invalid eHGF case, missing D02 endpoint, and subject-7 63/64 complete-fit discrepancy persist. | **NOT GLOBAL PASS**; issue #108 independent-science scope remains relevant |
| C2 — weak recovery | Report 36/36 **paired MATLAB/HGFX BIC winner agreement** separately from *true generating-model recovery* (balanced accuracy 0.583) and failed/weak parameter recovery. No general identifiability success. Keep uncertainties and 10/72 prospective P3 winner discrepancies. | **SCOPED OBSERVATION; historical M18/P3 FAIL retained** |
| C3 — warnings | 48/324 warning-positive forward blocks, 86 events, associated with ignored-trial cases; archived aggregate does not establish warning categories or cause. A successful source comparison is not a warning safety certificate. | **MECHANISM UNRESOLVED; issue #110 design blocker** |
| C4 — speed/GPU claims | Exact physical GPU correctness applicability may be discussed only within its validated hardware/precision/model scope. No valid released-wheel same-workload MATLAB speed ratio has been established; REV-2.3 not run; PERF-01C BLOCK_FREEZE. | **NO TIMING CLAIM** |
| C5 — USD/CHF example | Descriptive 614-observation workflow; official released-wheel paired fitting reported 4/1228 and 3/1228 original `traj.epsi` gate failures in accidentally concurrent runs; first divergence trial 178 (zero-based). Historic other-seed Ridders/Armijo replay is not proof about the current released-wheel optimizer cause. Do not claim convergence or equivalent optima without matching evidence. | **UNRESOLVED_DISCREPANCY; issue #111** |
| C6 — journal contribution | Position contribution as a transparent, reusable statistical-computing **validation framework** that separates numerical evaluation, optimization endpoints, and scientific inference, plus an auditable MATLAB-to-Python software package. **Do not** call it a new HGF mathematical model, state-of-the-art optimizer, speedup, or original published-study replication. Journal fit and novelty remain editorial judgments. | **DRAFT / AUTHOR SCIENTIFIC REVIEW** |
| C7 — exposition | Use reader-facing model names and definitions before internal gate abbreviations; retain exact run IDs, SHA provenance and protocols in ESM/reproducibility annex. Align results, legends, denominators, captions and abstract with the same bounded claims. | **IN PROGRESS; actual-PDF visual QA pending** |
| C8 — submission/legal | Check software DOI and preprint DOI **as distinct identifiers**; editable source/real PDF, copyright/license and data permissions, authorship, AI use, journal declarations, portal article type, subscription fee terms and independent review. | **BLOCKED / AUTHOR AND VENUE PREFLIGHT** |

## D2 proposed narrow claim envelope (requires human approval)

**Permitted for author consideration, subject to exact sentence-by-sentence evidence audit:**
- HGFX is publicly distributed as `hgfx==1.0.0`, with a frozen MATLAB 8.2.0 reference and documented compatible workflows.
- The original archived fixed-parameter classic-HGF objective tests meet their original test-specific criteria **only for the tested valid rows**; invalid rows remain in the denominator.
- One fixed perceptual forward vector was compared on 324 blocks (260 Suthaharan; 64 Reed; 25,920 trials), not full source-study fitting or external scientific replication.
- Paired BIC winner agreement (36/36) does **not** imply that the generating model was identified; recovery results include failures.
- Specific physical GPU objective consistency is distinct from speed.

**Not authorized by current evidence:** general fitting/optimization parity, family-wide eHGF/uHGF objective parity, overall parameter-identifiability success, participant-study replication, evidence-free warning harmlessness, verified optimizer convergence on USD/CHF, MATLAB-versus-HGFX runtime superiority/inferiority, or any publication/approval statement.

## Exact stoplight at this handoff

- **DONE:** D1=A; preserved original published-input protocols and 324-status result; initial table/figure/source checks; document-only publication-priority alignment.
- **IMPLEMENTED BUT NOT VALIDATED:** active real-manuscript PDF builder and CI preview; exact-source synthetic smoke only.
- **IN PROGRESS:** provisional REV-3 manuscript/ESM; full strict numeric-claim audit; C1–C8 editorial reconciliation.
- **BLOCKED:** D2 author claim approval; final independent science and manuscript review; real PDF compilation evidence (no confirmed actual run ID at last connector query); D3 journal submission approval.
- **NOT RUN:** REV-2.3 MATLAB performance benchmark; no speed outcome can be reported.


## Status refresh 2026-11-14 (evidence states only; D2 remains BLOCKED)

The stoplight above is updated by the following verified states; no claim-envelope change is proposed and the required author decision record below is still empty.

- **Strict numeric-claim coverage is now COVERED**, locally and on CI. `tools/check_manuscript_claims.py` was extended (LF-normalized evidence hashing after a diagnosed Windows CRLF false-error; explicit non-claim `labels` registry with class + rationale) and `COMPSTAT_CLAIM_MAP.json` now maps 128 claims / 133 labels covering 254/254 main + 219/219 supplement numeric tokens with 0 evidence errors. CI run [`43520067948`](https://github.com/ahmadkhanloo/hgfx/actions/runs/43520067948) (push `568a585`) passed the fail-closed strict audit gate.
- **The real current-source build is CI-validated.** CI run [`43566466259`](https://github.com/ahmadkhanloo/hgfx/actions/runs/43566466259) (push `1a9d134`) compiled the active main + ESM from real sources on hosted runners with the repaired builder (`pdftotext -enc UTF-8`; code-span break points; microtype/emergencystretch/listings layout), passed the six-table/keyword/page gates (main 14/14, ESM 6/10, abstract 237 words), and the 20 rendered pages were inspected page-by-page with no clipping or unresolved markers. This supersedes the "exact-source synthetic smoke only" state; the build is still the generic author-review layout, not the official Springer class.
- **REV-2.6A (angle A) executed once** under the preregistered protocol (`87d5eb5`, amendment `c9c9755`, results `81431f7`): float32 misuse runs silently (JAX truncation warning, 1,233 warnings recorded), paired forward error grows with horizon (median max|mu diff| 2.8e-07 / 1.6e-06 / 5.6e-06; worst 3.4e-02 at the two longest horizons), and the negative-posterior-precision failure region is large (27%/38.5%/48% of draws) and precision-independent (identical failing draw sets in float32 and float64). MATLAB failure-region half NOT RUN (documented limitation). This gives C6 a concrete measured computational finding for the author to consider adding to the article at REV-3 (integration itself is not yet done and remains author-reviewed).
- **Two pre-existing test failures are now precisely diagnosed** (unchanged by this work): `test_p6a_manifest` and `test_p8_delta_manifest` fail because the P8 freeze at candidate `897aed80` predates the legitimate `paper/references.bib` revision; regenerating the FROZEN p6a manifest at a new candidate requires an independent P8 pass by the generator's own policy. Resolution belongs to the independent-review process.
- **Unchanged BLOCKED states:** D2/D3 author gates; REV-2.3 (protocol eligibility matrix DRAFT_NOT_FROZEN, all 44 cells pending independent review; requires MATLAB CI + GPU); REV-2.4 `NOT_GLOBAL_PASS`; REV-2.1 `BLOCKED_M12B_TRANSFORMED_BASELINE_UNDEFINED` (issue #110); PERF-01C `BLOCK_FREEZE`.

## Required author D2 decision record (do not fill automatically)

Author must verify the exact final main manuscript and ESM against primary evidence, accept/reject the bounded claim envelope, classify any unresolved scientific contradiction as a limitation or narrow the claim, and explicitly approve scientific scope **before** final manuscript lock. Record the decision date and precise candidate commit in the REV ledger. This packet itself does **not** constitute D2 approval.

## Next mechanical work

Run actual-source preview on exact branch commit, archive run/job IDs, real PDF pages, source ZIP and manifest hashes; run strict `tools/check_manuscript_claims.py` (not only `--allow-unmapped`), reconcile unmapped scientific claims against source evidence while keeping non-result identifiers explicitly classified. Complete real rendered-PDF visual inspection and independent reviewer signoff. The updated workflow retains `claim_strict.json`, `claim_strict.log` and `claim_strict_exit_code.txt` even when strict coverage fails, without suppressing the PDF build. A nonzero strict check remains **NOT PASS**.
