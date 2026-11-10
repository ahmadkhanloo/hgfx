# REV-2.4 / B08 — Human scientific review of eHGF-019 numerical correction

**Fill in personally. Leave unsupported fields as NOT VERIFIED. This blank form is NOT a signed review.**

## Reviewer identity and independence

- Full name:
- Affiliation and scientific expertise:
- Date (UTC):
- Relationship to authors / conflicts:
- Is this human-authored and personally checked? YES / NO:
- Reviewed HGFX source commit SHA:
- Source bundle ZIP SHA-256 and original archive SHA-256:
- Executed `python3 verify_evidence.py`? YES / NO; exact output:

## Evidence verification

| Audit question | VERIFIED / NOT VERIFIED / FAIL | Source, command or missing evidence |
|---|---|---|
| Original 600-case Panel G archive untouched; 39 both-invalid, 1 one-sided-invalid | | |
| Original D019 case SHA and original 128 trials/frozen transformed vector | | |
| MATLAB 8.2.0 reference commit and authentic `hgf_volatility_update.m` | | |
| Published v1.0.0 `np.maximum` code checked, published wheel not changed | | |
| Raw MATLAB+HGFX D019 traces verified, first latent disagreement trial 8, level 3 | | |
| Trial 11 observation likelihood failure retained | | |
| MATLAB scalar `max(0,NaN)` semantics checked with authoritative original runtime | | |
| `exp(1010.436...)` overflow chain: direct observation versus reconstruction distinguished | | |
| One-source-file `np.fmax` dev patch exact diff and HGF/uHGF effects reviewed | | |
| Golden prepatch FAIL and 22/22 targeted CPU PASS checked | | |
| Full Linux+Windows CI still NOT_PASS, 302/1/5 per OS historically | | |
| Single P6A Git history check 1/1 both OS (not full CI) | | |
| Original eHGF/uHGF family acceptance thresholds missing | | |
| No postpatch MATLAB/HGFX full trajectory or objective validation yet | | |

## Scientific findings

### Mechanism and alternatives

[Describe the exact line-level numerical mechanism, evidence strength, possible competing causes, and whether original vv/ww/rr/correction terms were independently instrumented.]

### Patch impact and generalizability

[Limit claims to the source and test actually checked. Explicitly address arbitrary eHGF parameters, optimization/Hessian and the distinction between the development implementation and released v1.0.0.]

### Proposed follow-up protocol review

Review [`REV-2.4_EHGF019_DEVELOPMENT_VALIDATION_PROPOSAL_2026-11-10.md`](../../evidence/revision/protocols/REV-2.4_EHGF019_DEVELOPMENT_VALIDATION_PROPOSAL_2026-11-10.md).

- Is one *in-sample* fixed-vector finite-status validation useful and sufficiently specified? YES / NO / REVISIONS:
- Is the exact tool/runtime/dataset/parameter/source freeze sufficient? YES / NO / REVISIONS:
- Is the proposed acceptance language appropriately limited? YES / NO / REVISIONS:
- Is prospective human approval granted to **this protocol only**? YES / NO:
- What evidence remains necessary for any broader parity claim?

## Required verdicts

- **Numerical source-level cause:** `NUMERICAL_CAUSE_SUPPORTED` / `NUMERICAL_CAUSE_UNRESOLVED`
- **Dev implementation for further tests:** `PATCH_APPROVED_FOR_DEV_TESTING` / `PATCH_REQUIRES_REVISION`
- **Separate one-case scientific protocol:** `MAINTENANCE_ORACLE_PROTOCOL_APPROVED` / `NOT_APPROVED`
- **Original released v1.0.0 Panel G/E global parity:** `BLOCK_GLOBAL_PARITY`
- **Full CPU regression:** `NOT_PASS` until a separate genuine full suite succeeds
- **D2/D3 manuscript/release decision:** `BLOCKED`
- Missing/limited evidence:

## Return and provenance

Save signed report as `docs/research/reviews/REV24_EHGF019_HUMAN_REVIEW_2026-11-10.md` on a new reviewer branch with a reviewer-owned commit/PR to `compstat-revision`. If unable to push, return this completed Markdown with exact SHA/commands and author identity to the paper author.

- Reviewer branch / report commit SHA:
- Reviewer PR link:
- Issue #109 / PR #107 review comment links:
- Signature / explicit personal attribution:

**No approval of manuscript, scientific family-wide parity, D2/D3 or future numerical execution is implied merely by returning this form. Any follow-up execution also requires the author's separate explicit authorization.**
