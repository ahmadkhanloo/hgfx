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

## Required author D2 decision record (do not fill automatically)

Author must verify the exact final main manuscript and ESM against primary evidence, accept/reject the bounded claim envelope, classify any unresolved scientific contradiction as a limitation or narrow the claim, and explicitly approve scientific scope **before** final manuscript lock. Record the decision date and precise candidate commit in the REV ledger. This packet itself does **not** constitute D2 approval.

## Next mechanical work

Run actual-source preview on exact branch commit, archive run/job IDs, real PDF pages, source ZIP and manifest hashes; run strict `tools/check_manuscript_claims.py` (not only `--allow-unmapped`), reconcile unmapped scientific claims against source evidence while keeping non-result identifiers explicitly classified. Complete real rendered-PDF visual inspection and independent reviewer signoff. The updated workflow retains `claim_strict.json`, `claim_strict.log` and `claim_strict_exit_code.txt` even when strict coverage fails, without suppressing the PDF build. A nonzero strict check remains **NOT PASS**.
