# SOFTWARE_PUBLICATION_PLAN — active post-D1 research-software article track

**Authority date:** 2026-11-10. **Author D1:** explicitly chose **B — change journal**. **Status:** ACTIVE PLANNING; SWPUB-1 venue/zero-cost gate OPEN; **not ready to submit**.

This is the *prospective* publication roadmap. It does **not** rename, delete, pass, retroactively waive or reinterpret historical `REV-0..REV-5` in [COMPSTAT_REVISION_PLAN.md](COMPSTAT_REVISION_PLAN.md), nor M0–M20/v1.0.0 validation. Old COMPSTAT `REV-2..REV-5` are **not authorized for this new journal article**, yet remain valid preserved history, including their unfulfilled tests. The old JOSS/SoftwareX names mentioned there were suggestions, not author venue approval.

## Current goal and article positioning

Prepare and independently validate one concise **research software / compatibility tooling** article about **HGFX 1.0.0**, comparing its bounded MATLAB HGF Toolbox 8.2.0 implementation, reproducible behavior and known limitations with established alternatives (including `pyhgf==0.3.2` only on genuinely common model/config workflows). Primary claim: a released, usable, well-evidenced Python/JAX HGF implementation with no *user runtime* MATLAB requirement, **not** a new statistical identification theory or an unconditional replacement of all TAPAS workflows.

**Candidate venue order (not yet journal-approved):** (1) *SoftwareX* if official zero-mandatory-fee eligibility and editorial fit are confirmed; (2) *Software: Practice and Experience* conventional subscription publication if a substantial original software-design contribution can be demonstrated; (3) *JOSS* only after public-development/history and actual research-impact eligibility are met (no earlier than March 2027 at the absolute earliest). JORS only if zero fees confirmed. Source and current constraints: [VENUE SCREEN](../submissions/2026-11-10_SOFTWARE_VENUE_SCREEN.md).

## Mandatory release-source separation

Current `compstat-revision` working tree contains `pyproject.toml` version **`1.1.0b1`**, whereas the **frozen tag `v1.0.0`** contains `pyproject.toml` version **`1.0.0`**. These were independently checked on GitHub (working blob `c792d06db3b8428d5d484377fad46b92654144a1`, tagged-release blob `d287d28e69d89f9f1a3cf8347922a25b9fb18b4c`). Every claim attributed to HGFX **1.0.0** must use the **tag's own artifact and scientifically frozen reference source**, not code run from this revision branch. This separation is a hard source identity condition for SWPUB-3 and SWPUB-5. The documentation revision is **not** a new software release.

## Historical evidence to reuse truthfully

- 1.0.0 release immutable SHA `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`; MATLAB 8.2.0 reference `2437f4dc241541072722a2695ddeca7b44d83dd3`.
- 324 real-data source blocks / 25,920 trials: **fixed-vector forward parity** only, not full study/model-fit replication; 48 Reed warning blocks / 86 warning events (type and mechanism unknown).
- S7 matched **36/36** paired BIC winner decisions, balanced accuracy 0.5833333333333334; HGF/uHGF weak scientific parameter recovery, original M18 scientific FAIL retained. Do not turn matching software-level model selection into accurate generative model identification.
- P3 horizon scientific gate **FAIL / INSUFFICIENT_REFERENCE_EVIDENCE**, four asymmetric initial HGFX recovery failures versus MATLAB outputs; 64 full-fit **63/64** with subject 7 outside existing trajectory tolerance, no demonstrated first causal intermediate.
- PERF-01C **BLOCK_FREEZE**; no untimed seven-task forward check may be converted into speedup/throughput/timing claim. Physical GPU *applicability* for original frozen release is distinct from this manuscript's *performance* evidence.
- Real USD/CHF example, Pain/SPIRL feasibility, model families and prior manuscripts must be described by their actual verified scopes; no asserted study replication, convergence certificate, dataset rights, codebase universality or new scientific discovery without evidence.

## Prospective milestones (separate identifiers, preserve frozen history)

| ID | Deliverable | Gate / state |
| --- | --- | --- |
| **SWPUB-0** | Record D1 author scope choice, venue dossier, plan, new gates, old/active entrypoint links | This document commit + consistency checks; **implemented**, verification pending |
| **SWPUB-1** | Confirm venue and no mandatory author fees, target format/preprint/rights/citation policies | **OPEN**; potential waivers do not count; author explicitly approves chosen journal |
| **SWPUB-2** | Write scoped software article plus version-specific code metadata and honest comparison, clean figures | **OPEN**; separate working article under `paper/software_publication/` and independently source-bound claims |
| **SWPUB-3** | Reproduce selected demonstrations in a clean HGFX 1.0.0 environment and audit **all scientific numerical claims** | **OPEN**; strict mapped claims, actual command/output/versions and original failure preservation |
| **SWPUB-4** | Complete release/archive version DOI or verified persistent repository identifier, license/third-party/data reuse/author declarations, true preprint identity | **OPEN**; human-controlled declarations and publisher compliance verified |
| **SWPUB-5** | Exact final artifact review, journal-specific build/preflight, author approval and submission handoff | **BLOCKED** until SWPUB-1..4 + independent review PASS. Actual external submission requires explicit author instruction. |

## Execution order and stop policy

1. SWPUB-0 document-only changes and static verification. Do **not** modify the 1.0.0 software implementation/frozen scientific results for this task.
2. SWPUB-1: screen publishers using their official current instructions; select one on actual price/eligibility and author decision. If a candidate is financially blocked, record it as such; do not wait indefinitely or send fee-acceptance request on behalf of author. JOSS six-month condition is a hard eligibility blocker for immediate submission.
3. SWPUB-2: use the software manuscript draft **only as a distinct working candidate**. Keep the original Computational Statistics manuscript, Figures, REV reports and previous submitted PDFs untouched. Structure according to the actually confirmed venue; include what the software does, need, software design/choice vs alternatives, evidence, install/example, limitations, data/code licenses.
4. SWPUB-3: run focused claims tests and clean-install release demonstration. `tools/check_manuscript_claims.py --allow-unmapped` is inventory only, **not** a final pass. Do not cherry-pick failures or invent performance results. If demonstration cannot run, report block.
5. SWPUB-4: check exact archive DOI (do not invent or assume Zenodo minted one), `LICENSE`, `CITATION.cff`, `THIRD_PARTY_NOTICES.md`, software distribution, data rights, official preprint policies, authorship/AI disclosures. Preserve existing `v1.0.0` archive.
6. SWPUB-5: independent review of **this specific new manuscript**, not v1 product release, no unresolved critical/high findings; numeric evidence map complete and official target package built; author explicitly approves statements, journal, zero cost, declarations and final submission. No direct submission before approval.

**Scientific integrity:** no changed tolerance, seed, grid, dataset, parameter ordering, historical status, or narrower implicit denominator to manufacture PASS. Scientific identifiability, optimizer semantics, model selection, and source provenance remain distinct validation categories. Full fitting benchmark is not required for a **speed-free software-article claim** but its documented failures must be disclosed wherever fit parity would otherwise be implied.

## Completion definition

The project achieves this objective only when a **specific chosen eligible** journal submission package exists, correctly formatted and reproducible, fees/rights/preprint cleared, all SWPUB gates verified and exact author approval obtained. **This plan itself is not publication readiness, journal acceptance, financial clearance, or a submitted article.**
