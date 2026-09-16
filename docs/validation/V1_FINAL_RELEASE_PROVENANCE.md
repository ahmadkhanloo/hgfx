# HGFX v1.0.0 Final Release Provenance

Date: 2026-09-16
Status: **FINAL SOURCE VALIDATED / TAG AND GITHUB RELEASE OBJECT PENDING**

## Frozen reference

- MATLAB oracle: HGF Toolbox 8.2.0
- Frozen reference commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`

## Independent review closure

- Independent review report: `INDEPENDENT_REVIEW_REPORT.md`
- Release-blocking findings: H1/H2
- H1/H2 status: **RESOLVED**
- Remediation record: `INDEPENDENT_REVIEW_REMEDIATION.md`
- Frozen scientific thresholds/seeds/data/grids/model family/optimizer: unchanged

## Final metadata promotion

- Version: `1.0.0`
- Promotion PR: #30
- Promotion head: `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b`
- `pyproject.toml`: `1.0.0`
- `CITATION.cff`: `1.0.0`

Fresh PR-head validation:

| Workflow | Run | Result |
|---|---:|---|
| S10 v1 Release Readiness | `35089882319` | PASS |
| M19 M20 Release Preflight | `35089882608` | PASS |
| M18 D10 D11 Analysis Surfaces | `35089882668` | PASS |
| HGFX Regression | `35089882392` | PASS — Ubuntu + Windows |

## Final validated source target

- PR #30 merge commit on `main`: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- Main/push validation workflow: `HGFX Regression`
- Main validation run: `35090329868`
- Ubuntu result: PASS
- Windows result: PASS

**The `v1.0.0` tag/GitHub Release must target exactly `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.**

## Physical GPU evidence boundary

- Classification: `PASS_PHYSICAL_GPU_APPLICABILITY`
- Physical evidence source: `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`
- Hardware: 2x Tesla T4
- Maximum CPU/GPU objective gap: `1.4210854715202004e-14`
- Frozen acceptance criterion: `1e-7`
- Final promotion does not make a new H100/performance claim and does not replace physical GPU evidence with CPU evidence.

## Historical scientific evidence

Historical M18/D02/D08/S7 failures and `REFERENCE_LIMITATION_MATCH` classifications remain preserved. Final release validation does not convert those scientific failures into scientific PASS and does not modify their evidence.

## Remaining repository-hosting operation

- [ ] Create Git tag `v1.0.0` targeting `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- [ ] Create GitHub Release for `v1.0.0`.
- [ ] Record final tag/release URL or identifier below.

Tag: `v1.0.0` (pending creation)

GitHub Release URL/ID: **PENDING**

No substitute branch name should be treated as a tag, and the release gate must remain explicit until the hosting object exists.
