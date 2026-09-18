# HGFX v1.1 Release Plan

Recorded: 2026-09-18  
Status: **1.1.0b1 BETA CANDIDATE / RELEASE GATE OPEN / NOT PUBLISHED**  
Candidate metadata: `1.1.0b1`  
Stable PyPI default: `hgfx==1.0.0`  
Tracking: GitHub issue #56  
Frozen compatibility release: `v1.0.0` → `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`

## Objective

Release the additive HGFX 1.1 API first as the PEP 440 beta `1.1.0b1`, without changing the immutable v1.0.0 MATLAB-compatibility contract, historical validation evidence, or paper-1 scientific claims.

The first 1.1.0 feature integration begins at `b74a3199077d0afc7af730d32b19cb3f158f9516`. Beta publication is not complete until the gate below passes on one exact source SHA and that SHA is tagged and published. Final `1.1.0` is a later promotion step, not the first public 1.1 release.

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

## Distribution behavior

The beta is intentionally opt-in.

After `hgfx==1.1.0b1` is published:

```bash
# Stable/default
python -m pip install hgfx
# Expected: 1.0.0

# Allow pre-releases
python -m pip install --pre hgfx
# Expected while b1 is the latest prerelease: 1.1.0b1

# Exact beta pin
python -m pip install hgfx==1.1.0b1
```

The public verification gate must test these behaviors in clean environments against `https://pypi.org/simple`.

## Compatibility invariants

A 1.1.0 release must preserve all of the following:

1. Tag `v1.0.0` and its evidence remain immutable.
2. The default `fit_model` compatibility behavior does not change.
3. Frozen v1.0.0 reference tests and release guards remain green.
4. Historical M18 FAIL and all `REFERENCE_LIMITATION_MATCH` classifications remain unchanged.
5. New 1.1 APIs are not presented as evidence that recovery, LME, speed, identifiability, or pyhgf superiority improved.
6. Any scientific claim based on a new 1.1 API needs a separate prospective protocol and evidence.

## Candidate validation order

Use this order so the tag always points at an already validated source:

1. merge beta-preparation changes to `main`;
2. run the release workflow with `source_ref=<exact main SHA>` and `publish=false`;
3. record the successful build/audit/smoke artifact for that exact SHA;
4. only then create tag `v1.1.0b1` pointing to the same validated SHA;
5. run the release workflow with `source_ref=v1.1.0b1` and `publish=true`;
6. run public-PyPI stable/default and `--pre` verification.

When `publish=false`, an exact tag is deliberately not required. When `publish=true`, the workflow must reject any source that is not exactly tagged `v<package-version>`.

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

### R4 — Stable/default versus beta resolver verification

Before beta promotion, prepare the post-publication verification commands and expected versions.

After publication:

- [ ] clean environment: `pip install hgfx` resolves to `1.0.0`;
- [ ] clean environment: `pip install --pre hgfx` resolves to `1.1.0b1` while it is the newest prerelease;
- [ ] clean environment: `pip install hgfx==1.1.0b1` succeeds;
- [ ] record pip/Python versions and the public index URL;
- [ ] record verification workflow run and logs.

### R5 — Documentation and provenance

- [ ] freeze the exact release SHA;
- [ ] record Python/dependency compatibility;
- [ ] ensure README, API and v1.1 usage docs agree;
- [ ] create release notes separating frozen v1.0 compatibility from additive 1.1 features;
- [ ] record all workflow run IDs and artifact hashes used for promotion.

### R6 — Beta promotion

Only after R1–R5 pass:

- [ ] tag the exact validated SHA as `v1.1.0b1`;
- [ ] create a GitHub **prerelease**;
- [ ] publish `hgfx==1.1.0b1` through the established trusted-publishing path;
- [ ] execute and record the R4 public resolver verification;
- [ ] update README and this file with beta tag, source SHA, release ID, publish run and verification run;
- [ ] mark beta status **DONE / PASS / BETA PUBLISHED** only when all checks are recorded.

### R7 — Final 1.1.0 promotion

Do not publish final `1.1.0` automatically after beta. First review beta feedback and any fixes under explicit validation. Then prepare a new exact candidate SHA, repeat the required regression/packaging gates, tag `v1.1.0`, create a normal GitHub Release, publish `hgfx==1.1.0`, and verify that ordinary `pip install hgfx` now resolves to final 1.1.0.

## Current blockers

No code blocker is declared by this document. The immediate blocker to beta publication is execution of the `1.1.0b1` gate on one exact candidate SHA. Final `1.1.0` additionally requires accepted beta feedback and a separate final promotion.

## Continuity

Use this file together with:

- `VERSION_POLICY.md`
- `V1_TODO.md`
- `../user/V1_1.md`
- `OPT_IN_MAP.md`
- frozen v1.0 release/evidence documents

Future agents must not infer that candidate metadata `1.1.0b1` means the beta is already public. Publication requires the recorded beta tag, GitHub prerelease, Trusted Publishing run, and public-index resolver verification.
