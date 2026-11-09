> **DORMANT GATE (2026-11-10):** superseding author D1 A decision resumed `Computational Statistics`. SWPUB gates are **PAUSED**, not accomplished or deleted. If alternative venue work resumes later, revalidate all costs, author criteria and policies afresh. Current science/submission authority: [COMPSTAT_REVISION_PLAN.md](../planning/COMPSTAT_REVISION_PLAN.md).

# SWPUB software-publication acceptance gate — prospective (2026-11-10)

**Current status: NOT READY FOR SUBMISSION.** Author D1 selected a new **venue category**, not a particular journal. Historical `COMPSTAT` revision and M18/v1.0.0 scientific acceptance criteria are **immutable**. Authority: [SOFTWARE_PUBLICATION_PLAN](../planning/SOFTWARE_PUBLICATION_PLAN.md).

## Required gates (all must PASS with directly verifiable evidence)

| Gate | Acceptance requirement | Current verification |
| --- | --- | --- |
| SWPUB-0 scope | Author D1 B recorded; prospective plan/ledger/readme/roadmap updated; no old REV task changed to PASS | IMPLEMENTED; repository consistency check needed |
| SWPUB-1 venue/fees | Chosen journal & article type explicitly approved; current author instructions and publisher price checked; **mandatory author fee exactly zero confirmed** for this author/route; preprint/duplicate-publication and license policies cleared | **BLOCKED**: SoftwareX conditional fee waiver not established; JOSS time gate not met; no named author choice |
| SWPUB-2 accurate draft | Distinct software-paper source, explicit version/source SHA and alternatives, journal-format compliance, labeled scoped evidence and limitations, legible figures | **OPEN** |
| SWPUB-3 computational audit | Every substantive quantitative scientific claim mapped to immutable source and SHA-256; audited outputs and code/params same frozen model; clean 1.0.0 install/example runs; claims limited to observed parity | **OPEN** |
| SWPUB-4 metadata/legal | Explicit author/affiliation/acknowledgment/AI disclosure signoff; verified program license (MIT `LICENSE` present), `CITATION.cff`, third-party and data sharing permissions, archived release DOI **if actually issued**, bioRxiv original version/crosslink, finances and submission forms | **OPEN** |
| SWPUB-5 final reviewer/author | Independently reviewed exact final candidate with zero unresolved CRITICAL/HIGH; clean build/figures/references; signed author final journal+claims+declarations+zero fees decision | **BLOCKED** |

### Frozen-release source identity (mandatory for SWPUB-3)

The current working branch's `pyproject.toml` is **`1.1.0b1`**, while the immutable `v1.0.0` tag's `pyproject.toml` is **`1.0.0`**. Any demonstration, DOI, comparison or claim about released HGFX 1.0.0 must be traced to the **v1.0.0 tag/wheel** at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, and document Python/JAX/NumPy runtime provenance. Development-branch successes cannot silently validate the released paper; an unverified clean environment keeps SWPUB-3 OPEN.

### Claims that may be included only when appropriately qualified

- v1.0.0 frozen compatibility tests, fixed-vector forward parity on original 324 blocks/25,920 trials (not study replication), evidence-linked frozen 36/36 BIC winner comparison with balanced accuracy about 0.583 (not reliable generating-model recovery), software usability/released package and observed GPU **applicability** in the original hardware's scope.
- Historical failures must be named and remain available: P3 scientific paired-integrity failure, 4 asymmetric HGFX pre-optimizer initial failures, Subject 7 `traj.mu/muhat` threshold exceedances (63/64 diagnostic agreement, not 64/64), warning types not archived, M18 scientific recovery FAIL, PERF-01C `BLOCK_FREEZE`.

### Forbidden unsupported claims

- Any overall MATLAB/HGFX speedup or resource superiority (PERF-01C is BLOCK_FREEZE).
- General full-fit equivalence, 64/64 fitting trajectory equality, unconditional numerical accuracy across every optimizer, inference or dataset.
- Successful reproduction of Pain/SPIRL/other empirical analyses, statistical identifiability or robust USD/CHF fit convergence, unless independently verified under a new protocol.
- JOSS submission eligibility before **more than six months** documented public activity and demonstrable research use; any APC waiver as a certainty without publisher confirmation.
- Scientific PASS inferred solely from source archive integrity, green unit tests, a previous publication manuscript, no participant data, or preprint DOI.

### Release-gate enforcement

**FAIL CLOSED** whenever a required journal condition, scientific evidence, source hash, reviewer statement, fee/waiver eligibility, licensing authorization or author signoff is absent. `NOT APPLICABLE` is allowed only if a documented journal-specific criterion demonstrably does not apply; it cannot waive scientific truthfulness. A future new software experiment must be preregistered before running and must not rewrite previous evidence.

No physical GPU validation can be asserted from simulated devices. No final journal submission or financial obligation without explicit author approval.
