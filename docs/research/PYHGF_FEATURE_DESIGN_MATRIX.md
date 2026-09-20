# PV1-02A — HGFX vs pyhgf feature/design matrix

Status: **P2A STEP 1 COMPLETE — QUALITATIVE MATRIX**  
Paper protocol: `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`  
Tracking: issue #33  
Date: 2026-09-17

## Scope and integrity rule

This document is a neutral, primary-source-backed design comparison. It is **not** a ranking and it does not establish numerical equivalence, superiority, or performance ordering.

Direct HGFX↔pyhgf numerical comparison remains blocked until the separate semantic-mapping gate in `paper/reproducibility/PAPER_PROTOCOL.md` demonstrates matched model structure, update equations, inputs/masking, parameter semantics/transforms, initial states, observation/response quantity, and precision mode. `NOT_DIRECTLY_COMPARABLE` remains an acceptable outcome.

## Frozen identities

### HGFX

- product release: `hgfx==1.0.0`
- immutable source: `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- compatibility oracle: MATLAB HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

### pyhgf

- package: `pyhgf==0.3.2`
- release tag: `v0.3.2`
- release commit: `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`
- source distribution: `pyhgf-0.3.2.tar.gz`
- source-distribution SHA-256: `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d`
- PyPI release date: 2026-09-11

## Feature/design matrix

| Dimension | HGFX v1.0.0 | pyhgf v0.3.2 | Interpretation for the paper |
|---|---|---|---|
| Primary design objective | Reference-faithful Python/JAX reproduction of the frozen MATLAB HGF Toolbox 8.2.0 behavior in validated scopes, with MATLAB required only as a development/reference oracle. | A modular Python library for dynamic predictive-coding networks and generalized HGF/Bayesian filtering, with flexible network construction and integration with modern inference tooling. | **Different primary objectives.** Do not frame either objective as inherently superior. |
| Relation to MATLAB HGF Toolbox | MATLAB 8.2.0 is an explicit frozen compatibility target and release oracle. Cross-language parity and matched reference limitations are first-class validation outputs. | The project states that its HGF implementation was inspired by / follows the HGF lineage including the MATLAB toolbox, but its published objective is generalized/nodalized predictive-coding networks rather than behavioral replication of a frozen MATLAB release. | **Design-goal difference.** MATLAB behavioral compatibility is an HGFX-specific target, not a missing pyhgf feature. |
| Model/network construction | v1 exposes toolbox-oriented model/configuration and workflow compatibility surfaces, including HGF/eHGF/uHGF and specialized migrated models in documented validated scopes. | Networks are assembled from probabilistic nodes, edges, local update functions, and update schedules; the project explicitly supports arbitrarily sized generalized HGF networks. | **Different abstraction level.** A direct feature count would be misleading. |
| HGF coverage and extensibility | Emphasis is compatibility with the frozen toolbox model family and workflow surfaces; public availability does not imply equal validation strength for every arbitrary model/configuration combination. | Supports binary/continuous HGF constructions plus generalized filtering, arbitrary nodalized networks, custom coupling/update structures, and additional predictive-coding network types. | **Partial overlap plus non-overlap.** Additional generalized pyhgf surfaces are not HGFX defects; toolbox-specific HGFX surfaces are not pyhgf defects. |
| Forward filtering / belief trajectories | Provides Python/JAX implementations whose validated scopes are compared against MATLAB trajectories/inference states at frozen tolerances. | `Network.input_data(...)` performs belief propagation through the configured network and exposes node trajectories; standard binary/continuous HGF examples are documented. | **Candidate overlap.** Fixed-parameter forward trajectories are a possible common surface, pending semantic mapping. |
| Surprise / response quantity | Toolbox-compatible observation models and objective surfaces are part of the compatibility program; fitting/model-selection evidence is classified separately from forward parity. | Response functions return surprise; documented functions include first-level binary surprise and binary softmax variants, and surprise can be used as a differentiable log-probability component. | **Candidate overlap only after response semantics are matched.** Do not equate quantities by name alone. |
| Parameter fitting | MATLAB-style compatibility fitting is exposed through `fit_model`/`fitModel`; historical optimizer/inference mismatches remain preserved where applicable. | Differentiable HGF surprise/log-probability functions are integrated with PyMC/PyTensor/JAX workflows for Bayesian parameter inference, including NUTS examples. | **Workflow semantics differ.** Optimizer/posterior results must not be directly ranked without a separately frozen common fitting protocol. |
| Model comparison | HGFX exposes MATLAB-style statistical outputs such as BIC/LME and has paired model-selection evidence in its frozen validation record. | Documentation demonstrates posterior-based model comparison using modern Bayesian tooling such as ArviZ leave-one-out cross-validation when models are fitted to the same observations. | **Not the same default comparison workflow.** Compare capabilities descriptively unless an explicit common estimator/criterion is frozen. |
| Differentiability and JAX integration | JAX is used for validated CPU/GPU paths and numerical execution; 64-bit mode is exposed for workflows requiring the validated precision policy. | Core functions are described as differentiable and JIT-compiled where applicable; the framework is designed to integrate with JAX-based optimization/inference tooling. | **Shared JAX ecosystem, different product contracts.** JAX use alone does not establish algorithmic equivalence. |
| Accelerator/backend support | JAX CPU/GPU execution is part of the product; v1 contains frozen physical-NVIDIA applicability evidence and batch/multi-device infrastructure. | The v0.3.2 project supports JAX and Rust backends and provides GPU/JAX installation paths; JAX enables accelerator execution. | **Both support accelerated execution.** No speed/scaling comparison is authorized under paper protocol 1. |
| Parameter/model recovery evidence | HGFX preserves historical M18 failures, scoped `REFERENCE_LIMITATION_MATCH` cases, paired model-selection results, and an active prospective trial-horizon/identifiability study. | v0.3.2 documentation contains explicit parameter-recovery tutorials using simulated data and Bayesian inference; the tutorial records sampling diagnostics rather than claiming equivalence to MATLAB recovery gates. | **Evidence types differ.** Recovery examples/results should not be converted into a cross-tool score. |
| Reproducibility/provenance strategy | Frozen MATLAB oracle/source SHA, immutable v1 source, evidence manifests, workflow/run IDs, artifact hashes, generated tables, and explicit PASS/FAIL/reference-limitation classifications are central project artifacts. | Versioned source, tagged releases, public documentation/tutorials, PyPI distributions and the peer-reviewed methods paper provide software provenance; examples include environment watermarks. | **Both provide reproducibility mechanisms with different emphasis.** HGFX paper claims should describe its evidence freeze without implying pyhgf lacks reproducibility. |
| Packaging/documentation | Released as `hgfx==1.0.0` on PyPI with user/API/migration/demo documentation and MATLAB-style aliases for compatibility workflows. | Released as `pyhgf==0.3.2` on PyPI with API documentation, tutorials/examples, and a peer-reviewed PLOS Computational Biology methods paper. | **Both are public Python packages.** HGFX must not claim to be the first/only Python or Python/JAX HGF implementation. |

## Primary sources

### HGFX

- HGFX v1 source and release scope: `README.md` at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`
- Public API and precision policy: `docs/user/API.md`
- MATLAB demo parity and frozen tolerances: `docs/user/MATLAB_DEMOS.md`
- Paper fitting/model-selection classification: `paper/tables/fitting_statistics_classification.md`
- Paper protocol and pyhgf semantic gate: `paper/reproducibility/PAPER_PROTOCOL.md`
- Authoritative release evidence: `docs/validation/V1_EVIDENCE_INDEX.md`

### pyhgf

- Legrand N, Weber L, Waade PT, et al. (2026). *pyhgf: A neural network library for predictive coding*. PLOS Computational Biology 22(6):e1014340. DOI: `10.1371/journal.pcbi.1014340`
- Tagged source: `https://github.com/ComputationalPsychiatry/pyhgf/tree/v0.3.2`
- Tag identity: `v0.3.2` -> `ccd43db5ee5abe4a5a35077d098e53cce2c070c2`
- v0.3.2 README: `https://github.com/ComputationalPsychiatry/pyhgf/blob/v0.3.2/README.md`
- v0.3.2 documentation: `https://computationalpsychiatry.github.io/pyhgf/`
- Binary HGF tutorial: `https://computationalpsychiatry.github.io/pyhgf/notebooks/1.1-Binary_HGF.html`
- Parameter-recovery tutorial: `https://computationalpsychiatry.github.io/pyhgf/notebooks/4-Parameter_recovery.html`
- API reference: `https://computationalpsychiatry.github.io/pyhgf/api.html`
- PyPI release/source hash: `https://pypi.org/project/pyhgf/0.3.2/`

## Step-1 conclusion

The qualitative gate establishes that HGFX and pyhgf have a genuine common HGF lineage and overlapping forward-filtering concepts, but their primary design objectives, construction abstractions, fitting workflows, and evidence programs are not identical. Therefore **no direct numerical comparison is yet authorized**.

The next P2A step is a pre-execution semantic mapping of the candidate fixed-parameter three-level binary HGF forward trajectory / surprise surface. That mapping must either satisfy every protocol criterion or explicitly classify the surface as `NOT_DIRECTLY_COMPARABLE` before any empirical run.
