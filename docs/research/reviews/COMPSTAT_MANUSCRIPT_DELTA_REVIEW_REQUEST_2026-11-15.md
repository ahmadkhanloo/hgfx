# Computational Statistics manuscript-delta review request — 2026-11-15

**Status:** PREPARED FOR AN INDEPENDENT REVIEWER; **NO REVIEW SIGN-OFF RECEIVED**. This is a request/protocol, not an independent review. Prepared by the project agent from repository records. The original scientific experiments and negative outcomes are immutable.

## Exact candidate and review boundary

- Repository: [ahmadkhanloo/hgfx](https://github.com/ahmadkhanloo/hgfx).
- Working PR: [#107, DRAFT](https://github.com/ahmadkhanloo/hgfx/pull/107), target `main`, candidate branch `compstat-revision`.
- **Scientific manuscript candidate for review:** commit [`8de6a83cf985d687e72307bd26fed5de1d080672`](https://github.com/ahmadkhanloo/hgfx/commit/8de6a83cf985d687e72307bd26fed5de1d080672) (source files below; a later documentation-only commit does not change this candidate).
- The live target is *Computational Statistics*, software/package article, author's D1=A. The paper concerns **published HGFX v1.0.0** compared with **MATLAB HGF Toolbox 8.2.0**, not development HGFX 1.1, arbitrary models, or a speed claim.
- Actual-source **mechanical CI**: [run **43701976722**](https://github.com/ahmadkhanloo/hgfx/actions/runs/43701976722), job `132774881522`, **SUCCESS**. Claim audit: main **267/267**, ESM **232/232** numeric tokens covered, zero unmapped and zero evidence errors. Actual generic author-review PDFs: main **14/14** pages, supplement **7/10** pages; abstract **237** words.
- [Reviewer artifact **14156982013**](https://github.com/ahmadkhanloo/hgfx/actions/runs/43701976722/artifacts/14156982013) is the generated draft PDF/LaTeX/source/log bundle. Its manifest lists main PDF SHA-256 `4b57931fff300eb1ccd78e933f91eb76697f45a18fea99b1768a7073dca6f886` and supplement PDF SHA-256 `f7172985ba7466151bbeb2cbaac62bd13f3c015b0e50f8ebfc82979e4925c31e`. This is **not** the official Springer class and not a visual/independent scientific sign-off.

### Required reading (do not substitute old submitted PDFs)

1. [Current main source](../../../paper/computational_statistics/manuscript.md) and [current ESM](../../../paper/SUPPLEMENTARY_APPENDICES.md), both at the exact reviewed candidate SHA. Check the rendered PDFs from the linked CI artifact.
2. [Numeric-claim map](../../planning/COMPSTAT_CLAIM_MAP.json) and [checker](../../../tools/check_manuscript_claims.py); [precision data](../../../evidence/revision/rev26_precision_stability.json), [precommitted REV-2.6A protocol](../../../evidence/revision/protocols/REV-2.6_PROTOCOL.md). New Methods §2.9 / Results §3.6 / ESM §S8 must agree in model, data, success denominator, dtype and language of inference.
3. [Revision plan](../../planning/COMPSTAT_REVISION_PLAN.md), [C1–C8 and D2 decision packet](../../planning/COMPSTAT_D2_CLAIM_DECISION_PACKET_2026-11-13.md), [live readiness gate](../../planning/COMPSTAT_SUBMISSION_READINESS_2026-11-12.md), [journal/author preflight](../../planning/COMPSTAT_VENUE_PREFLIGHT_2026-11-15.md), [revision ledger](../../planning/COMPSTAT_REVISION_LEDGER.md).
4. [Original Panel G scoped report](../REV24_PANEL_G_ORIGINAL_RESULT_2026-11-10.md), [Panel E report](../REV24_PANEL_E_ORIGINAL_RESULT_2026-11-10.md), [independent-review issue #108](https://github.com/ahmadkhanloo/hgfx/issues/108), [eHGF-019 issue #109](https://github.com/ahmadkhanloo/hgfx/issues/109) and [D08 protocol-deviation issue #111](https://github.com/ahmadkhanloo/hgfx/issues/111). A past limited **AI** review exists; it is not an independent human counter-signature.
5. [Original published-input forward result](../../../paper/case_studies/REALDATA_FORWARD_PARITY_RESULT_2026-11-04.md), [publisher-used-data limitations in ESM §S7](../../../paper/SUPPLEMENTARY_APPENDICES.md), and [software release v1.0.0](https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0).

## Review tasks — read-only unless separately authorized

**Scientific validity (C1, C2, C3, C5)**

- Reconcile **600 Panel G cases**: 164 jointly-valid classic-HGF rows within its original objective criterion, 36 jointly invalid; 198 jointly-valid / 1 both-invalid / 1 one-sided-invalid eHGF; 198 jointly-valid / 2 jointly-invalid uHGF. No eHGF/uHGF predeclared family objective gate. Do not call 560 jointly-valid rows universal parity.
- Reconcile Panel E's original **132 planned endpoint slots**, **131** available/evaluable, **128/128 classic-HGF same-vector objective** within its existing scope; the original D02 HGFX full vector is missing. No broader optimizer, Hessian, fitted-trajectory or inference equivalence follows.
- Preserve original `eHGF-019` released v1.0.0 one-sided invalidity (latent finite-status divergence at zero-based trial 8; likelihood at trial 11); the distinct 1.1 maintenance patch is not retroactive scientific parity.
- Do not suppress historical **63/64** complete-fit nonpass, P3 scientific integrity failure, low parameter recovery, and **36/36** paired BIC winner agreement versus only **0.583** true generating-model balanced accuracy. The two quantities answer different questions.
- Confirm original D08 official `uhgf + gaussian_obs` with MATLAB-generated response data retains its **4/1228 and 3/1228** `traj.epsi` mismatches in two unintended concurrently started runs. The earlier holdout's sensitivity is **not** official-seed causal proof. A successful GitHub job is not an optimizer-parity result.
- Confirm **324** authentic published-input perceptual forward blocks came from **260** Suthaharan and **64** Reed blocks, sharing one frozen HGF-AR(1) vector. This is not original-study fitting, response-model or conclusion replication; **48** blocks have recorded warnings without established cause.
- Review new precision Results §3.6 against Methods §2.9 and ESM §S8. At each tested horizon, the frozen released-wheel **binary64** negative-precision failure counts are **54/200, 77/200, 96/200**. Median maximum posterior-mean errors are calculated **only** for **146, 123, 104** mutually valid draws, respectively. The failed draw identity set is unchanged between precision modes; binary32 may reclassify some failures as nonfinite. No MATLAB/optimizer/GPU or cross-family inference can be drawn from the precision-only CPU study.

**Manuscript quality and publication readiness (C4, C6, C7, C8)**

- Confirm Table **3** corresponds to original Panel G and Table **4** to fit/recovery classifications; check all table/figure cross-references, captions, model names and discussion in both rendered PDFs. Inspect every page of both current PDFs for overflow, font rendering, clipping, missing references, formula misrendering, and unsupported statements. This is a **new** PDF candidate, not the visually inspected November 14 preview.
- Evaluate the paper's computational-statistics contribution **without** asserting a new mathematical model, blanket parity, better runtime, superior parameter identifiability or new results from the unexecuted REV-2.5 recovery design. Judge clarity and novelty separately from numerical correctness.
- Trace important numeric claims to **actual original evidence**, not merely the coverage checker. The checker verifies registered phrases and pointers, **not** correctness of the experiment, completeness of scientific reporting, or independence of reviews.
- Identify any non-public participant data or restricted/unclear redistribution rights. Check source-study and referenced code licences, software version DOI versus preprint DOI, article/abstract/keywords/declarations and the still-unverified official submission template. Do not assert that a subscription no-APC option guarantees zero payable fees.
- Examine author-facing cover letter against final bounded claims. The explicit author placeholders, corresponding-author verification, exclusive submission, preprint overlap, and author funding/ethics declarations remain HUMAN ACTION.

## Reproducible minimum checks

From a clean checkout, pin the actual reviewed manuscript source before inspecting it:

```bash
git fetch origin compstat-revision
git checkout --detach 8de6a83cf985d687e72307bd26fed5de1d080672
git rev-parse HEAD
python tools/check_manuscript_claims.py \
  --source paper/computational_statistics/manuscript.md \
  --source paper/SUPPLEMENTARY_APPENDICES.md \
  --json-out compstat_reviewer_claim_audit.json
```

This check is **read-only** on the original experiments. If tools are available, review the actual PDF/artifact and source. Do **not** run a new MATLAB/HGFX fit, expand any frozen grid, alter thresholds or generate a supposedly corrective synthetic result under an exhausted run cap.

## Expected reviewer deliverable (reviewer-owned)

Write `docs/research/reviews/COMPSTAT_MANUSCRIPT_INDEPENDENT_REVIEW_2026-11-15.md` in **your own reviewer branch** from the exact reviewed commit. Include:

- Reviewer identity, whether **human** or **AI-assisted/AI-only**, conflicts/relationships, exact source commit and review date.
- Exact source files, artifact IDs, SHA-256 checks actually verified, commands and outputs, and unavailable/private evidence explicitly identified.
- For each C1–C8, classify `SUPPORTED_SCOPED`, `REQUIRES_TEXT_CORRECTION`, `BLOCKED_INSUFFICIENT_EVIDENCE`, or `NOT_REVIEWED`; cite exact main/ESM lines. List any factual contradiction, missing denominator, invented inference, legal/ethical uncertainty, or reviewer-identified risk.
- A bounded manuscript verdict: `READY_FOR_AUTHOR_D2_REVIEW`, `REQUIRES_MANUSCRIPT_REVISION`, or `BLOCK_UNSUPPORTED_CLAIM`. **This verdict does not grant scientific global parity, D2 or D3.**
- A signable summary of changes needed before author D2, separating editorial fixes from genuinely new scientific questions that require author-approved protocols.

Push your reviewer-only branch, open a PR targeting **`compstat-revision`** (not `main`), and comment with your branch, commit SHA and report/PR links on [PR #107](https://github.com/ahmadkhanloo/hgfx/pull/107). If GitHub access is unavailable, return the report plus a list of unverified sources; an owner repost of an AI review must remain labelled AI/limited, never human-approved.

**Current gate after preparation:** independent manuscript review **NOT RECEIVED**, REV-2.4 still **NOT_GLOBAL_PASS**, REV-2.5 still **NO FINAL RESULT**, D2 and D3 **BLOCKED**, PR #107 stays **DRAFT**. No journal submission is authorized by this request.
