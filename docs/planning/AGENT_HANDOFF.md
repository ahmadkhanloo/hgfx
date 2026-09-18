# Agent Handoff

Last synchronized: 2026-09-18
Branch: `main`
Release status: **HGFX v1.0.0 RELEASED / V1 GATE CLOSED**
Product-line policy: [VERSION_POLICY.md](VERSION_POLICY.md)

Read [VERSION_POLICY](VERSION_POLICY.md), [V1_TODO](V1_TODO.md), [V1_RELEASE_GATE](V1_RELEASE_GATE.md), [M20_GATE](M20_GATE.md), [FINAL_REVIEW_CHECKLIST](FINAL_REVIEW_CHECKLIST.md), [the evidence index](../validation/V1_EVIDENCE_INDEX.md), and [final release provenance](../validation/V1_FINAL_RELEASE_PROVENANCE.md) before any post-v1 work.

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
- Owner product decision recorded 2026-09-18: v1.0.0 remains the immutable MATLAB-compatibility release and paper-1 anchor; v1.1.x is the active additive development line.
- Current package metadata on `main` is `1.1.0`; the additive MAP/VKF/dual-stream/response APIs are implemented on `main` but 1.1.0 is not yet tagged, released, or published to PyPI.
- P3/M18C.2 execution is complete: official classification is `INSUFFICIENT_REFERENCE_EVIDENCE`, `gate_pass=false`; no horizon/structural-identifiability conclusion is promoted.
- Additive opt-in MAP helper lives at `hgfx.optim.minimize_map`. It is not the `fit_model` default. See [OPT_IN_MAP.md](OPT_IN_MAP.md).

## v1 closure

The HGFX v1.0.0 product/release objective is complete. There is no remaining blocking v1 task.

Do not reopen frozen scientific validation, move the release tag, or rewrite historical evidence. Later commits on `main` are post-release documentation/maintenance and do not alter the immutable release source target.

v1.0.x maintenance may only restore or document the frozen compatibility contract. v1.1.x may add opt-in models, response functions, fitting helpers and ergonomics, but it must preserve the v1.0.0 compatibility defaults and may not inflate tolerances or convert preserved FAIL / `REFERENCE_LIMITATION_MATCH` results into PASS.

## Paper 1

The active publication objective is the v1 methods paper as a validated MATLAB reproduction, not a generic HGF superiority claim or a pyhgf bake-off. GPU speedup and general recovery success are not paper-1 headlines. P3 is complete but inconclusive under its frozen gate and must not be rewritten as evidence for either horizon-limited or structural identifiability.

## v1.1.x

v1.1.x is the active additive product-development line. Current `main` includes opt-in MAP fitting, VKF helpers, dual-stream AR1 helpers, social-gaze softmax variants, and three-choice card-volatility softmax support. These APIs are additive and must not change `hgfx.fit_model` or the immutable v1.0.0 evidence set. User-facing details are in [../user/V1_1.md](../user/V1_1.md).

## Future work policy

Any further work must begin with an explicit post-v1 objective and new milestone/release scope. Examples include:

- non-blocking independent-review maintenance findings M1/L1/L2;
- completed M18C.2 evidence reporting and any non-selective follow-up diagnostics;
- methods-paper/publication work;
- v1.0.x compatibility maintenance;
- v1.1.x additive development and a dedicated 1.1.0 release gate;
- new performance claims/benchmarks (not paper 1);
- compatibility with a future upstream HGF Toolbox version.

These items are not unfinished v1 release work and must not be used to revise the frozen v1 acceptance evidence.
