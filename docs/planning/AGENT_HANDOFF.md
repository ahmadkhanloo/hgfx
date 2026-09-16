# Agent Handoff

Last synchronized: 2026-09-16
Branch: `main`
Release status: **HGFX v1.0.0 RELEASED / V1 GATE CLOSED**

Read [V1_TODO](V1_TODO.md), [V1_RELEASE_GATE](V1_RELEASE_GATE.md), [M20_GATE](M20_GATE.md), [FINAL_REVIEW_CHECKLIST](FINAL_REVIEW_CHECKLIST.md), [the evidence index](../validation/V1_EVIDENCE_INDEX.md), and [final release provenance](../validation/V1_FINAL_RELEASE_PROVENANCE.md) before any post-v1 work.

## Current state

- M0–M17 are complete in documented scopes.
- Historical M18 scientific FAIL remains preserved.
- D02/D08 and exact-grid S7 parameter recovery remain scoped `REFERENCE_LIMITATION_MATCH`, not scientific PASS.
- S9 physical NVIDIA GPU applicability is accepted on 2x Tesla T4 and is no longer blocked/deferred.
- M19 is PASS / FROZEN.
- M20 historical RC candidate gate is PASS (`PASS_M20_CANDIDATE`, run `34989737851`).
- Independent frontier review completed; H1/H2 were resolved without changing frozen scientific criteria.
- Final package/citation metadata are `1.0.0`.
- PR #30 head `85ea9c7be4ab5e5041ada0703d0cd3c9a7c1848b` passed S10 (`35089882319`), M19/M20 preflight (`35089882608`), D10/D11 (`35089882668`), and Regression (`35089882392`, Ubuntu + Windows).
- PR #30 merged to `main` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- Main Regression run `35090329868` passed on Ubuntu and Windows for that exact final source target.
- Git tag `v1.0.0` has been verified to resolve directly to `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.
- GitHub Release `v1.0.0` is published, non-draft and non-prerelease: https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0, Release ID `389966452`.

## v1 closure

The HGFX v1.0.0 product/release objective is complete. There is no remaining blocking v1 task.

Do not reopen frozen scientific validation, move the release tag, or rewrite historical evidence. Later commits on `main` are post-release documentation/maintenance and do not alter the immutable release source target.

## Future work policy

Any further work must begin with an explicit post-v1 objective and new milestone/release scope. Examples include:

- non-blocking independent-review maintenance findings M1/L1/L2;
- M18C.2/horizon-analysis research;
- methods-paper/publication work;
- PyPI publication;
- new performance claims/benchmarks;
- compatibility with a future upstream HGF Toolbox version;
- new models, APIs, or product features.

These items are not unfinished v1 release work and must not be used to revise the frozen v1 acceptance evidence.
