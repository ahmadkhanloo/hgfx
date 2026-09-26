# P8 Independent Pre-Submission Review Checklist

Status: **REPLACEMENT CANDIDATE LOCKED / INDEPENDENT REVIEW PENDING**
Failed reviewed candidate: `c6ef9e5f4113e373a5d492cb73c9dbe0fe89fd28`  
Replacement candidate SHA: `b66f294f4799968404273127a9b06b4fc451ffb3`  
Candidate tree: `507c7568ac0c53ccd69c59e630e0f164cbe40284`
Review packet: `docs/research/P8_REVIEW_PACKET.md`
Delta manifest: `docs/research/P8_DELTA_MANIFEST.json`
Tracking: PV1-02 / GitHub issue #32
This is **not** M19 and is **not** an implementer self-review.

Use this checklist on the exact submission candidate after:

- [x] P3 aggregate is committed at `paper/reproducibility/p3_m18c2_aggregate_35272347167.json`, hash-verified as `83ccbb7f...31b4`, and classified under `m18c2-trial-horizon-identifiability-1` as `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`;
- [x] P3 diagnostic Figure 6 is generated from that committed aggregate, committed as `paper/figures/fig_p3_horizon_diagnostics.png`, and zero-diff gated by P5 CI;
- [x] the P6A draft evidence manifest and P6A-2 numerical claim audit are complete and reproducible;
- [x] replacement P7 submission-candidate SHA is locked; strict P7/P6A/P2/P5/regression gates pass on that exact SHA.

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

- [ ] Abstract claims only frozen, scoped results.
- [ ] No general HGFX-faster-than-MATLAB/pyhgf claim.
- [ ] No general multi-GPU scaling claim.
- [ ] No claim that HGFX is the first/only Python or JAX HGF.
- [ ] D02/D08 remain `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- [ ] Historical M18 remains FAIL / preserved.
- [ ] P3 classification matches the preregistered 256→1024 rules; 128/512 are not substituted.
- [ ] pyhgf comparison remains the single authorized common-scope cell; response NLL remains NDC if still nonfinite.

### Evidence traceability

- [ ] Every numerical sentence maps to a committed artifact in `docs/research/PAPER_EVIDENCE_MAP.md`.
- [ ] P2 tables regenerate with zero Markdown diff.
- [ ] P5 figures regenerate from committed inputs.
- [ ] P3 aggregate SHA-256 matches the frozen Actions artifacts.
- [ ] P6A draft manifest and P6A-2 claim audit reproduce with zero diff and do not modify M19.
- [ ] Candidate SHA in this review matches the exact P7 lock.
- [ ] If the review result is PASS, final P6A freeze is performed afterward for this exact candidate SHA.

### Reproducibility

- [ ] `paper/reproducibility/README.md` is sufficient without chat history.
- [ ] MATLAB-required vs MATLAB-free steps are explicit.
- [ ] Exact SHAs, tags, package versions, and seeds are recorded.
- [ ] Failed simulations/fits were retained, not dropped.

### Consistency

- [ ] Abstract, Results, tables, figures, and supplement agree.
- [ ] Figure captions match file contents.
- [ ] Bibliography keys resolve; pyhgf citation is present and fair.

### Metadata

- [ ] Authors, affiliations, corresponding author.
- [ ] Funding, conflicts, acknowledgments.
- [ ] Target-journal template applied.
- [ ] License/data/code availability wording matches MIT + GitHub + PyPI.

## Outcome

Reviewer:
Date:
Candidate SHA: `b66f294f4799968404273127a9b06b4fc451ffb3`
Result: `PENDING`
