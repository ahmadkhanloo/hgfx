# Paper Evidence Map

Last synchronized: 2026-09-17
Status: **ACTIVE / POST-M19 / v1.0.0 FROZEN / PAPER PROTOCOL FROZEN / PAPER EVIDENCE OPEN**
Tracking: PV1-02 / GitHub issue #32
Comparator tracking: PV1-02A / GitHub issue #33
Paper protocol: `paper/reproducibility/PAPER_PROTOCOL.md` / `hgfx-paper-protocol-1` / `FROZEN_FOR_EXECUTION`

This file maps paper-facing claims to the strongest currently committed evidence. Historical failures and scoped reference limitations remain visible. New paper-only recovery and comparator claims may be added only under the frozen paper protocol and after committed machine-readable results exist.

Historical M19 is the frozen v1.0.0 release-evidence gate. It is complete and is not the final paper-evidence freeze. The publication package will receive a separate `FROZEN_FOR_SUBMISSION` manifest after all paper-used evidence is generated and audited.

Paper protocol 1 deliberately does not activate general speedup or multi-GPU scaling as headline paper claims. Historical performance evidence therefore remains engineering context unless a later prospectively frozen protocol revision activates a paper performance benchmark.

## Claim-to-evidence map

| Candidate claim | Paper status | Evidence / restriction |
|---|---|---|
| HGFX v1.0.0 targets a Python replacement of frozen MATLAB HGF Toolbox 8.2.0 behavior | READY | v1 release definition; MATLAB oracle `2437f4dc241541072722a2695ddeca7b44d83dd3`; HGFX release `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| Users do not require a MATLAB runtime | READY | S10/release readiness; v1 user docs and release evidence |
| HGF/eHGF/uHGF forward behavior is reproduced in documented validated scopes | READY | M4–M6 evidence + frozen v1 evidence index |
| Observation/objective parity exists in documented validated scopes | READY | M7–M8 + later workflow evidence |
| MATLAB-compatible fitting/statistical surfaces are reproduced in accepted v1 scopes | READY WITH QUALIFICATION | M9–M10, D10/D11 and release evidence; D02/D08 direct failures remain scoped reference limitations |
| D02/D08 still need to be forced into direct PASS before paper submission | **REJECTED** | exact scopes are frozen `REFERENCE_LIMITATION_MATCH`; paper must disclose the direct failures and limitation interpretation rather than retune them |
| Exact D02/D08 limitations can be called scientific PASS | **REJECTED** | `REFERENCE_LIMITATION_MATCH` is product/reference-behavior accounting only |
| Hessian/covariance/correlation/AIC/BIC/LME compatibility exists in documented scopes | READY WITH QUALIFICATION | M10 + analysis-surface/release evidence; exact sensitive cases disclosed |
| Simulation/sample/analysis workflows are available and release-validated | READY | M11–M13 + D09/D10/D11/D12 + S10 |
| Model/source coverage is sufficient for v1.0 target | READY | M12 + release validation matrix |
| Public compatibility API is release-ready | READY | M13 + S10 + user docs/examples |
| Official classic-HGF/eHGF demo behavior is reproduced | READY | `PASS_MODEL_SELECTION_PARITY`; run `35028441041`; artifact `10420615907` |
| Official uHGF→AR(1) demo workflow is reproduced | READY | `PASS_UHGF_AR1_WORKFLOW_PARITY`; run `35028441038`; artifact `10420651501` |
| Paired model-selection behavior is preserved | READY | S7 `PASS_PAIRED_MODEL_SELECTION`; 36/36 BIC winners match |
| Parameter recovery is generally strong/complete | **NOT SUPPORTED** | historical M18 FAIL preserved; S7 exact-grid parameter recovery includes scoped reference limitation matches |
| Historical recovery failures are reproduced/retained transparently | READY | historical M18 + S7 evidence + v1 evidence index |
| Paper-only prospective settings were frozen before final execution | READY | `paper/reproducibility/PAPER_PROTOCOL.md`; protocol `hgfx-paper-protocol-1`; status `FROZEN_FOR_EXECUTION` |
| Trial horizon explains the recovery failures | OPEN / UNKNOWN | PV1-01 / issue #21 prospective 128/256/512/1024 analysis is frozen prospectively and in progress; do not infer before results |
| CPU compatibility and JAX CPU backend preserve tested outputs | READY | S9 `PASS_CPU_BACKEND_EQUIVALENCE`; post-review run `35080084517` |
| Physical NVIDIA GPU path preserves tested final objective values | READY / SCOPED | 2x Tesla T4; `PASS_PHYSICAL_GPU_APPLICABILITY`; max gap `1.4210854715202004e-14` vs `1e-7` |
| HGFX is faster than MATLAB/CPU in general | **OUT OF PROTOCOL-1 CLAIM SET** | no prospective performance benchmark is activated in `hgfx-paper-protocol-1`; historical measurements cannot support a general speed claim |
| Multi-GPU scaling is a general HGFX result | **OUT OF PROTOCOL-1 CLAIM SET** | historical H100 scaling remains limited to its original workload/environment; a future protocol revision is required for a headline scaling claim |
| Tiny binary64/runtime differences can be amplified by finite differences and optimization | READY AS SCOPED NUMERICAL CASE STUDY | D02 shared-state/source/self-sensitivity evidence; avoid generalizing to all fits |
| v1.0.0 evidence was frozen before final release | READY | historical M19 `PASS_FROZEN`; machine-readable v1 evidence manifest |
| The final paper evidence set is frozen | **NOT YET** | requires new paper manifest with status `FROZEN_FOR_SUBMISSION`; this is separate from M19 |
| Independent review portability blockers were resolved without retuning science | READY | independent review + remediation; H1/H2 resolved; post-review regression |
| Cross-platform regression passed after remediation | READY | run `35080084509`; Ubuntu + Windows; Windows `178 passed, 4 skipped, 0 failed` |
| Final v1.0.0 source/tag/release provenance is verified | READY | `docs/validation/V1_EVIDENCE_INDEX.md` and final release provenance |
| HGFX is the first/only Python or Python/JAX HGF implementation | **REJECTED** | pyhgf is an established Python/JAX HGF-related library with a 2026 PLOS Computational Biology paper |
| pyhgf is relevant related work and must be discussed | READY AS LITERATURE FACT | Legrand et al. 2026, PLOS Computational Biology 22(6):e1014340, DOI `10.1371/journal.pcbi.1014340` |
| `pyhgf==0.3.2` is the frozen paper comparator identity | READY AS PROTOCOL FACT | `hgfx-paper-protocol-1`; sdist SHA-256 `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d` |
| HGFX has a distinct frozen-MATLAB-8.2.0 compatibility/evidence objective | READY AS HGFX DESIGN CLAIM | v1 product definition, release evidence, MATLAB equivalence/reference-limitation policies; comparison must avoid implying this is pyhgf's objective |
| HGFX is generally more accurate/faster/better than pyhgf | **NOT SUPPORTED** | prohibited without direct prospectively frozen common-scope evidence; protocol 1 explicitly forbids a general superiority claim |
| A fair common-scope HGFX↔pyhgf comparison is complete | **OPEN / REQUIRED FOR POSITIONING** | PV1-02A / issue #33; comparator is pinned, but semantic overlap mapping and any valid common-scope result remain open; `NOT_DIRECTLY_COMPARABLE` is allowed |
| PyPI availability is required for scientific validity | **REJECTED** | distribution is separate from science; PV1-03 is useful reviewer-access evidence but not scientific validity evidence |

## Paper-facing interpretation of D02/D08

D02 and D08 remain narrow, explicit limitation cases. The frozen MATLAB oracle exhibits numerical/optimizer sensitivity in the relevant exact scopes, and HGFX reproduces the corresponding reference limitation. This supports reference-faithful product behavior, but it does not establish stable or scientifically correct parameter inference for those cases.

A paper sentence may state that the exact workflow is classified as `REFERENCE_LIMITATION_MATCH` and explain why. It must not relabel the result as direct fit parity or parameter-recovery success. The publication plan must not treat "make D02/D08 pass" as an acceptance task.

## Parameter recovery and model selection

The manuscript keeps two conclusions separate:

1. historical/paired parameter-recovery evidence contains failures and matched reference limitations;
2. paired model selection passes with 36/36 BIC winners matching under the recorded S7 protocol.

PV1-01 / issue #21 is a prospective trial-horizon/identifiability study. Its grid, deterministic generation, fitting contracts, thresholds, paired-integrity gate and 256→1024 interpretation rules are frozen before final execution in the paper protocol. Whatever its outcome, it does not rewrite historical M18 evidence.

## pyhgf comparison interpretation

pyhgf and HGFX overlap but have different design centers. pyhgf emphasizes generalized/nodalized predictive-coding networks, modular graph construction, differentiability and modern JAX/Rust integration. HGFX v1.0 emphasizes behavioral compatibility with one frozen MATLAB HGF Toolbox 8.2.0 oracle and explicit cross-language evidence/provenance.

Paper protocol 1 freezes `pyhgf==0.3.2` as the comparator identity. The manuscript must compare the project goals neutrally. The feature matrix may include non-overlapping capabilities, but empirical numerical comparison is permitted only after a committed semantic mapping passes the protocol gate for the intended scientific quantity. `NOT_DIRECTLY_COMPARABLE` is an acceptable and scientifically preferable result to a forced ranking.

## GPU and performance interpretation

The accepted physical GPU evidence is a correctness/applicability result on 2x Tesla T4. It supports the statement that the tested JAX/CUDA path executes on physical NVIDIA hardware and preserves the tested objective criterion.

It does not support a general speedup or scaling claim. Under `hgfx-paper-protocol-1`, general performance/scaling is not activated as a headline contribution. Archived H100/T4 measurements may be described only as historical engineering evidence unless a later protocol revision freezes a prospective performance benchmark before execution.

## Primary paper evidence sources

- `paper/reproducibility/PAPER_PROTOCOL.md`
- `docs/validation/V1_EVIDENCE_INDEX.md`
- `docs/planning/M19_GATE.md`
- `docs/planning/V1_RELEASE_GATE.md`
- `docs/user/MATLAB_DEMOS.md`
- `docs/validation/MATLAB_TOOLBOX_VALIDATION_MATRIX.md`
- `docs/validation/MATLAB_EQUIVALENCE_POLICY.md`
- `docs/validation/MATLAB_REFERENCE_LIMITATIONS_POLICY.md`
- `docs/validation/INDEPENDENT_REVIEW_REPORT.md`
- `docs/validation/INDEPENDENT_REVIEW_REMEDIATION.md`
- `reference/validation/v1_release/evidence_manifest.json`
- `docs/research/PAPER_REVIEW_GAP_ASSESSMENT.md`
- `docs/research/BENCHMARK_PLAN.md`

## Paper-only evidence still required

Before submission, add evidence entries for:

- immutable input/checksum manifests for prospective recovery/comparator runs before their result stage;
- generated manuscript table inputs/outputs and hashes;
- generated figure inputs/outputs and hashes;
- paper-specific reproducibility environment/commands;
- PV1-01 recovery-horizon analysis if used in the manuscript;
- PV1-02A pyhgf semantic mapping and any valid common-scope empirical outputs;
- a post-v1 performance benchmark only if a later protocol revision activates speed/scaling as a paper claim;
- final machine-readable paper evidence manifest marked `FROZEN_FOR_SUBMISSION`;
- independent pre-submission review of the exact manuscript candidate.
