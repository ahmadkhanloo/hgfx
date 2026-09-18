# HGFX version policy

Recorded: 2026-09-18  
Status: **v1.0.0 FROZEN / v1.1.x ACTIVE ADDITIVE DEVELOPMENT**  
Authority: this file is the product-line decision record. It does not reopen the v1.0.0 scientific or release gate.

Immutable v1.0.0 source: `v1.0.0` → `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`  
Frozen MATLAB oracle: HGF Toolbox 8.2.0 → `2437f4dc241541072722a2695ddeca7b44d83dd3`  
Public PyPI release: `hgfx==1.0.0`  
Current beta-candidate metadata: `1.1.0b1`

## Product-line decision

HGFX keeps one continuous v1 product line.

- **v1.0.0 is immutable compatibility evidence.** It is the released Python/JAX reproduction of the frozen MATLAB HGF Toolbox 8.2.0 contract in the documented validated scopes.
- **v1.1.x is the active additive development line.** It may add analysis helpers, models and response functions while preserving the frozen v1.0.0 compatibility path and historical evidence.
- There is no separate major-version roadmap in the current project plan. New work must be classified either as v1.1.x-compatible additive work, v1.0.x compatibility maintenance, paper/research work, or a separately approved future scope.
- The first methods paper remains anchored to the immutable v1.0.0 evidence set. Later additive APIs do not retroactively enlarge the paper-1 equivalence claim.

## v1.0.0 — frozen MATLAB compatibility release

The following rules are immutable:

1. **Compatibility identity.** The v1.0.0 acceptance oracle is HGF Toolbox 8.2.0 at `2437f4dc241541072722a2695ddeca7b44d83dd3`.
2. **Frozen source.** Tag `v1.0.0` and commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` do not move.
3. **Historical evidence.** M18 scientific FAIL remains FAIL. D02/D08 and exact-grid S7 recovery remain scoped `REFERENCE_LIMITATION_MATCH` where recorded; they are not converted into scientific PASS.
4. **Default fitting contract.** `hgfx.fit_model` remains the frozen MATLAB-compatible quasi-Newton/Laplace path for reproducing v1.0.0 and paper-1 numbers.
5. **Paper-1 claim.** The methods paper may claim only the documented validated reproduction scopes, workflow/statistical-surface equivalence, official demo parity, paired model-selection agreement, backend/GPU applicability, and explicit reference-limit handling.
6. **pyhgf relation.** `pyhgf==0.3.2` is an external comparator with a different design center. The completed common-scope comparison does not imply global interchangeability, superiority, or response-likelihood equivalence.
7. **P3/M18C.2 result.** The completed trial-horizon study is classified `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`; no data-horizon or structural-identifiability conclusion is promoted, and historical M18 remains unchanged.

## v1.1.x — active additive line

The active 1.1 feature line is being prepared first as the PEP 440 prerelease `1.1.0b1`. The first 1.1.0 feature integration starts at commit `b74a3199077d0afc7af730d32b19cb3f158f9516`.

The current additive surface includes:

- **opt-in MAP fitting** through `hgfx.optim.fit_map`, `minimize_map`, and `multi_start_map`; SciPy `L-BFGS-B` is the production opt-in engine when available, with the internal solver retained as fallback;
- **binary and dual-stream Volatile Kalman Filter (VKF)** helpers;
- **dual-stream AR1 binary** helpers for reward/social analyses;
- **social-gaze softmax** response variants;
- **three-choice card-volatility softmax** support for the 3PLR-style workflow.

These additions are intentionally separate from the frozen compatibility default:

- `hgfx.fit_model` is not replaced by the opt-in MAP solver;
- v1.1.x additions do not rewrite v1.0.0 validation results or historical scientific classifications;
- project-specific priors, parameter numbers and analysis-specific wiring remain outside the core library unless explicitly generalized and validated;
- any new scientific claim using a v1.1.x API requires its own prospective protocol and evidence.

User-facing usage is documented in `docs/user/V1_1.md`.

## v1.1 release status and prerelease policy

As of 2026-09-18:

- package metadata for the beta candidate is `1.1.0b1`;
- the additive APIs are implemented on the 1.1 line;
- public PyPI stable remains `hgfx==1.0.0`;
- the intended first public 1.1 artifact is the prerelease `hgfx==1.1.0b1`;
- final `1.1.0` remains unreleased until beta validation and feedback are accepted.

PyPI/pip policy:

- ordinary `python -m pip install hgfx` must continue to resolve to stable 1.0.0 while only a 1.1 prerelease exists;
- beta users opt in with `python -m pip install --pre hgfx` or exact `python -m pip install hgfx==1.1.0b1`;
- the stable-default and `--pre` opt-in behavior must be independently verified against public PyPI after beta publication.

Publishing any 1.1 prerelease/final requires a dedicated release gate that at minimum verifies:

- full regression against the frozen v1.0.0 compatibility path;
- focused tests for every additive 1.1 API;
- clean wheel/sdist metadata and installation smoke tests;
- API/documentation consistency;
- exact source SHA, tag and release provenance;
- explicit confirmation that the release does not alter the immutable v1.0.0 evidence set.

## Change policy

Classify future work before implementation:

- **v1.0.x maintenance:** fixes required to restore the frozen v1.0.0 contract, packaging portability, documentation and citation corrections that do not alter scientific behavior.
- **v1.1.x additive development:** new opt-in models, response functions, fitting helpers and ergonomics that preserve the existing compatibility APIs and are covered by explicit tests.
- **paper/research work:** manuscript, reproducibility, prospective scientific analyses and comparison evidence; these do not silently change package acceptance criteria.
- **incompatible product changes:** require a new explicit owner decision and release policy before implementation. Do not infer such a roadmap from old planning documents.

No tolerance, seed, dataset, validation grid, model family, optimizer, or historical result may be changed post-hoc to manufacture a PASS.
