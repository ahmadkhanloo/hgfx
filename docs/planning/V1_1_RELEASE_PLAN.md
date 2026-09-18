# HGFX v1.1.0 Release Plan

Recorded: 2026-09-18  
Status: **IMPLEMENTED ON MAIN / RELEASE GATE OPEN / NOT PUBLISHED**  
Package metadata: `1.1.0`  
Public PyPI: `hgfx==1.0.0`  
Frozen compatibility release: `v1.0.0` → `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`

## Objective

Release the additive HGFX 1.1.0 API already implemented on `main` without changing the immutable v1.0.0 MATLAB-compatibility contract, historical validation evidence, or paper-1 scientific claims.

The first 1.1.0 feature integration begins at `b74a3199077d0afc7af730d32b19cb3f158f9516`. The release is not complete until the gate below passes on one exact source SHA and that SHA is tagged and published.

## Implemented scope

### Opt-in MAP fitting

Public helpers:

- `hgfx.optim.fit_map`
- `hgfx.optim.minimize_map`
- `hgfx.optim.multi_start_map`
- `MapOptions`

SciPy `L-BFGS-B` is the production opt-in engine when SciPy is installed; the internal L-BFGS implementation remains available as fallback.

Invariant: `hgfx.fit_model` remains the frozen MATLAB-compatible quasi-Newton/Laplace path. The 1.1 MAP API is not allowed to silently replace it.

### Additional models

- `hgfx.models.dual_ar1_binary`
- `hgfx.models.vkf_binary`
- `hgfx.models.vkf_reward_social`

The dual-stream AR1 helper composes validated single-stream AR1 models. VKF is an additive model family and is not part of the frozen MATLAB HGF equivalence claim.

### Additional response models

- `hgfx.responses.softmax_binary_socialreward`
- `hgfx.responses.softmax_mab3_card_volatility`

These support social/reward and three-choice card-volatility workflows. Analysis-specific priors and study-specific parameter values stay outside the core package.

## Compatibility invariants

A 1.1.0 release must preserve all of the following:

1. Tag `v1.0.0` and its evidence remain immutable.
2. The default `fit_model` compatibility behavior does not change.
3. Frozen v1.0.0 reference tests and release guards remain green.
4. Historical M18 FAIL and all `REFERENCE_LIMITATION_MATCH` classifications remain unchanged.
5. New 1.1 APIs are not presented as evidence that recovery, LME, speed, identifiability, or pyhgf superiority improved.
6. Any scientific claim based on a new 1.1 API needs a separate prospective protocol and evidence.

## Release gate

### R1 — API and unit validation

- [ ] run all focused 1.1 unit tests;
- [ ] validate MAP backends, solver selection and fallback behavior;
- [ ] validate VKF and dual-stream model shape/parameter contracts;
- [ ] validate new response-model numerical and boundary behavior;
- [ ] verify public exports match `docs/user/API.md` and `docs/user/V1_1.md`.

### R2 — v1.0 compatibility regression

- [ ] run the complete CPU regression suite;
- [ ] run frozen-reference/source-classification guards;
- [ ] run official demo/model-selection compatibility checks required by the normal release gate;
- [ ] confirm no v1.0 acceptance threshold, seed, fixture, dataset, model family or optimizer was changed to accommodate 1.1.

### R3 — Packaging

- [ ] build wheel and sdist from the exact candidate SHA;
- [ ] run metadata/archive audit;
- [ ] clean-install the wheel in an isolated environment;
- [ ] smoke-test v1.0 public imports plus the new 1.1 public imports;
- [ ] confirm no MATLAB/reference validation payload is unintentionally shipped.

### R4 — Documentation and provenance

- [ ] freeze the exact release SHA;
- [ ] record Python/dependency compatibility;
- [ ] ensure README, API and v1.1 usage docs agree;
- [ ] create release notes separating frozen v1.0 compatibility from additive 1.1 features;
- [ ] record all workflow run IDs and artifact hashes used for promotion.

### R5 — Promotion

Only after R1–R4 pass:

- [ ] tag the exact validated SHA as `v1.1.0`;
- [ ] create the GitHub Release;
- [ ] publish `hgfx==1.1.0` through the established trusted-publishing path;
- [ ] independently verify `pip install hgfx==1.1.0` from public PyPI;
- [ ] update README and this file with final tag, source SHA, release ID, PyPI verification run and status **DONE / PASS / RELEASED**.

## Current blockers

No code blocker is declared by this document. The blocker to calling 1.1.0 released is simply that the dedicated release gate above has not yet been executed and recorded on one exact candidate SHA.

## Continuity

Use this file together with:

- `VERSION_POLICY.md`
- `V1_TODO.md`
- `../user/V1_1.md`
- `OPT_IN_MAP.md`
- frozen v1.0 release/evidence documents

Future agents must not infer that package metadata `1.1.0` means the public 1.1.0 release already exists.
