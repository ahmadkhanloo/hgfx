# P8 Independent Pre-Submission Review Checklist

Status: **OPEN / NOT STARTED**
Tracking: PV1-02 / GitHub issue #32
This is **not** M19 and is **not** an implementer self-review.

Use this checklist on the exact submission candidate after:

- [x] P3 aggregate is committed at `paper/reproducibility/p3_m18c2_aggregate_35272347167.json`, hash-verified as `83ccbb7f...31b4`, and classified under `m18c2-trial-horizon-identifiability-1` as `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`;
- [ ] the P3 diagnostic figure is generated from that committed aggregate if P3 is retained in the submission package;
- [ ] the paper evidence manifest is `FROZEN_FOR_SUBMISSION`.

Do not treat this file as a completed review. An independent reviewer must fill it.

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
- [ ] Paper evidence manifest is `FROZEN_FOR_SUBMISSION` and does not modify M19.

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
Candidate SHA:
Result: `PASS` / `FAIL` (unresolved CRITICAL/HIGH)
