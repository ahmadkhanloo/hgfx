# REV-2.4 independent scientific review — complete **ONLY AFTER** verification

**This is an unfilled template, NOT a completed independent review, scientific PASS, or validation certificate.**

## Reviewer provenance

- Reviewer name / affiliation / GitHub handle:
- Date (UTC) and timezone:
- Reviewed code SHA (not merely branch name): `75a34897c84ee746feb96a874e0f2ac52789b93f` (or specify another precise SHA)
- Reviewer packet ZIP SHA-256:
- Reviewer packet verifier command and result:
- GitHub server-side push/commit chronology independently checked? YES / NO / PARTIAL. Supporting URL:
- Conflicts of interest / independence (how review differs from authorship):

## Original evidence checklist (mark VERIFIED / NOT VERIFIED / FAIL)

| Evidence category | Check | Result | How verified (command/artifact SHA) |
| --- | --- | --- | --- |
| Protocol chronology | Preregistration SHA `d1986311b8a5ff97f088ebac35c612e16cbe89db` in both original G/E run ancestry, before actual science | | |
| Panel G source identity | Exact released HGFX 1.0.0 Wheel/source and frozen MATLAB HGF 8.2.0 | | |
| Panel G integrity | Original synthetic artifact ZIP `faebd113e9ee050a2490d08e1d1fbc54ba589becd1015d41cab4e7879a785b1c` | | |
| Panel G original denominator | 200×3=600; 560 both-valid, 39 both-invalid, 1 asymmetric | | |
| Panel G HGF M8 | 164 both-valid within original HGF-only M8 gate, plus 36 both-invalid retained | | |
| Panel G eHGF `019` | Trial 11 (zero-based) first observed asymmetric likelihood, first *causal state* NOT_EXPORTED | | |
| Panel E provenance | 66 original D02/D08/64 cases; 132 slots; original D02 HGFX full endpoint missing | | |
| Panel E public artifact | ZIP `41e2aca61afb0d1961c653b87db3b36a1edd204f7b68ee0b362c958474fb96bb`, JSON `051aea43a11f7788b85d64a9cb8e82a59a274a70aa347f1927920d991a8ce86d` | | |
| Panel E original raw archives | D02 `10339454535`, D08 `10339403480`, 64 `13341288055` (not in packet; private/controlled audit) | | |
| Panel E HGF 128/128 | Same-vector original HGF endpoint pairs within original M8 gate, max `negLj` gap 2.842e-14 | | |
| Panel E family semantics | D02 `ehgf_binary+unitsq_sgm` obs prior 0.5; D08 continuous `uhgf+gaussian_obs` obs prior 0.1 | | |
| Posthoc bounds | Original old own-fit values / archived paired differences; not prospective numeric gate | | |
| Prior limits | M18 fitting FAIL, P3 FAIL, historical 63/64 NONPASS, PERF-01C BLOCK_FREEZE retained | | |
| Family gates | Original registered eHGF and uHGF objective gates found? Include exact dated source or mark not found | | |
| Privacy/reproducibility | Missing Panel E raw numerical artifacts, archive expiration, participant data control | | |

## Observations (reviewer-authored)

### 1. Scientific and numerical scope

[Reviewer to supply source-verified findings; distinguish same-vector objective from fitting/inference.]

### 2. One-sided invalid case `REV24-G-ehgf_binary-019`

[Reviewer to supply evidence-based hypothesis, or say NOT VERIFIED. Do not label scientific model limitation without frozen MATLAB latent-state evidence.]

### 3. Original D02 missing endpoint and D08 family/observation

[Reviewer to document limits and evidence.]

### 4. Provenance, preregistration, reproducibility and independence

[Reviewer to mark any checks that cannot be independently completed, especially private source archives and true GitHub push chronology.]

## Final scoped verdict

Choose only what actual evidence supports:

- `BLOCK_GLOBAL_PARITY`: YES / NO, rationale:
- `ALLOW_HGF_SAME_VECTOR_OBJECTIVE_CLAIM_ONLY`: VERIFIED / CONDITIONAL / NOT ALLOWED; exact population and denominator:
- `NEEDS_REFERENCE_EVIDENCE`: YES / NO, specify:
- `REV-2.4` scientific gate: BLOCKED / UNRESOLVED (do not assert PASS without all documented gates).
- D2/D3 submission or release: BLOCKED / EVIDENCE-BASED OTHER.
- Is this an **independent full review** or **limited review with unavailable primary data**?

## Suggested manuscript wording (EDIT ONLY AFTER VERIFICATION)

> For the 64 original HGF subjects, we evaluated both implementations at each of the two original fitted endpoints, yielding 128 same-vector objective comparisons. [If verified: all 128 comparisons met the previously established HGF M8 objective criterion; the maximum absolute negative-log-joint discrepancy was 2.842×10⁻¹⁴.] This does not establish fitted-parameter, optimizer-trajectory, Hessian, or scientific-inference equivalence. The original subject-7 fit-level failure, one one-sided invalid eHGF grid case, and one unavailable original D02 endpoint remain explicitly reported.

## Review completion and return

- Report file and canonical branch:
- Report commit SHA:
- Reviewer PR URL (if available):
- Comment on issue #108 (if available):
- Comment on PR #107 (if available):
- Exact known limitations or missing evidence still preventing sign-off:

**Signature / reviewer attribution:**
