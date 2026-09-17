# External Paper-Readiness Critique Assessment

Last synchronized: 2026-09-17
Status: **ACTIVE / REVIEW INCORPORATED**
Tracking: PV1-02 / issue #32

## Purpose

This document reconciles external paper-readiness criticism with the current HGFX repository state. It prevents stale criticism from reopening completed v1 gates while preserving valid publication gaps as explicit work.

## Assessment

| Critique | Verdict | Repository interpretation / action |
|---|---|---|
| The manuscript is not written or is only an outline | **PARTLY STALE / PARTLY VALID** | `paper/manuscript.md` now contains a substantive working Abstract, Methods/validation, Results, Discussion, Limitations, Reproducibility and Conclusion. It is **not submission-ready** because generated tables/figures, final paper-only results, declarations, target-journal formatting and final review remain open. |
| M19/evidence freeze for the paper is incomplete | **WORDING STALE; UNDERLYING CONCERN VALID** | Historical **M19 is already PASS/FROZEN** for v1.0.0 and must not be reopened. Publication work instead requires a distinct paper-specific protocol freeze before new experiments and a final paper-evidence freeze after all included results are generated. |
| D02_fit and D08_fit remain unresolved equivalence blockers | **STALE AS A RELEASE/PASS REQUIREMENT** | Their direct failures remain visible, but the exact validated scopes are frozen as `REFERENCE_LIMITATION_MATCH` because the MATLAB oracle exhibits the relevant limitation/sensitivity. They must be explained clearly in the paper; they must **not** be chased until they become artificial PASS results. |
| Parameter recovery and model recovery are incomplete | **VALID WITH QUALIFICATION** | Historical parameter-recovery FAIL remains preserved. Paired model selection already has 36/36 matching BIC winners. PV1-01 / issue #21 is actively investigating trial horizon vs weak/structural identifiability. The manuscript must not infer strong parameter recovery from model-selection agreement. |
| Final performance benchmarks are missing | **VALID IF PERFORMANCE IS A PAPER CLAIM** | Existing H100/T4 evidence is scoped engineering evidence. A headline speed/scaling claim requires a prospectively frozen paper benchmark with fixed workload, hardware, software/runtime, warmup/compile/repeat policy and uncertainty summaries. Performance is not required to support the narrower MATLAB-equivalence software-methods claim. |
| Tables and figures must be generated from frozen data | **VALID / REQUIRED** | Core tables and figures remain open. Final numerical outputs must be script-generated from committed machine-readable evidence with input hashes and source SHA; manual transcription is prohibited. |
| Reproducibility package is incomplete | **VALID / REQUIRED** | The final package must contain exact commands, seeds/stochastic drivers, configs, dataset checksums, environment manifests, source/reference SHAs, artifact hashes and regeneration instructions. |
| Limitations and MATLAB differences need clearer disclosure | **VALID / PARTLY IMPLEMENTED** | Current manuscript and evidence map already distinguish PASS, `REFERENCE_LIMITATION_MATCH`, and `FAIL_PRESERVED`, but the final manuscript must retain this distinction in Abstract/Results/Discussion/tables and supplement. |
| A fair comparison with pyhgf is needed | **VALID / HIGH PRIORITY** | `pyhgf` is an established Python library published in PLOS Computational Biology in 2026. HGFX must not claim to be the first/only modern Python/JAX HGF. The paper needs a neutral related-work comparison and, where semantics overlap sufficiently, a prospectively defined common-scope empirical comparison. |
| PyPI publication would help | **VALID / OPTIONAL** | HGFX is currently installable from source/release but not formally published on PyPI. PV1-03 remains a separate distribution task. PyPI publication improves accessibility but is not a scientific submission gate unless required by the selected venue. |

## pyhgf positioning facts to preserve

External source checked 2026-09-17:

- Legrand et al., **"pyhgf: A neural network library for predictive coding"**, PLOS Computational Biology 22(6):e1014340, published 2026-06-22, DOI `10.1371/journal.pcbi.1014340`.
- The paper describes pyhgf as a Python package backed by JAX and Rust for dynamic predictive-coding networks, including generalized HGF functionality, differentiability, fitting/inference workflows and modular network construction.
- Current PyPI documentation exposes pyhgf as a public installable package; the comparison protocol should pin an exact version rather than benchmarking an unspecified moving target.

Paper consequence: HGFX should be positioned around **frozen MATLAB HGF Toolbox 8.2.0 behavioral compatibility, explicit cross-language evidence/provenance, and transparent reference-limitation accounting**, not around being the only Python/JAX HGF implementation.

## Required plan changes

The publication plan must therefore include:

1. completion of the substantive manuscript rather than creation from scratch;
2. a paper-specific protocol freeze distinct from historical M19;
3. scripted tables/figures from frozen machine-readable inputs;
4. completion of PV1-01 if a stronger recovery/identifiability claim is retained;
5. a new paper-grade performance protocol only if performance remains a headline claim;
6. a fair pyhgf related-work and common-scope comparison;
7. a complete reproducibility bundle;
8. a final paper-evidence freeze after all included evidence is generated;
9. independent pre-submission review;
10. optional PyPI publication tracked separately from the scientific submission gate.

## Integrity rule

Do not reinterpret this critique as permission to retune v1 or manufacture green results. Historical FAIL evidence, D02/D08 scoped limitation records, frozen thresholds, seeds, datasets, model families and validation history remain immutable. New paper-only work must be prospective and separately versioned.