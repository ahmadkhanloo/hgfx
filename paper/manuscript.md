# HGFX: A Python/JAX Reproduction of the Hierarchical Gaussian Filter Toolbox with Validated MATLAB Equivalence and Accelerator-Compatible Execution

**Working manuscript — 2026-09-17**  
**Publication work:** PV1-02 / GitHub issue #32  
**Frozen product release:** HGFX `v1.0.0` @ `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`  
**Frozen reference oracle:** HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3`

**Authors and affiliations:** to be finalized before submission.

> Submission note: this draft is evidence-backed for the released v1.0.0 validation record, but it is not yet submission-ready. Final paper-specific generated tables/figures, the reproducibility bundle, target-journal formatting, and the independent manuscript audit remain open. New recovery-horizon or performance experiments must be prospectively frozen before they can be added as final results.

## Abstract

The Hierarchical Gaussian Filter (HGF) is a hierarchical Bayesian framework for learning under uncertainty and volatility, with a mature MATLAB toolbox that has been widely used in computational neuroscience and computational psychiatry [@mathys2011; @mathys2014]. We present HGFX, a Python/JAX reproduction and extension framework whose version 1.0 objective is functional and scientific equivalence with a frozen HGF Toolbox 8.2.0 reference while removing MATLAB as a user-runtime dependency. Rather than treating reimplementation as source translation alone, we validate configuration semantics, parameter transforms, forward trajectories, observation likelihoods, objectives, fitting/statistical outputs, simulation workflows, official demo behavior, model selection, backend agreement, and accelerator applicability against a pinned reference oracle using predeclared tolerances and preserved historical failures. Two official MATLAB demo workflows reproduce the reference behavior at frozen trajectory tolerances (`rtol=5e-11`, `atol=5e-13`), including a model-family failure regime in which classic HGF fails and eHGF succeeds, and an unbounded-HGF to AR(1) workflow. In paired model-selection validation, all 36 BIC winners agree between MATLAB and HGFX. Physical NVIDIA GPU applicability was validated on two Tesla T4 devices, with a maximum CPU-versus-GPU final-objective difference of `1.4210854715202004e-14` against a frozen `1e-7` criterion. Importantly, historical parameter-recovery failures and exact MATLAB/HGFX limitation matches are preserved and are not reclassified as scientific success. HGFX v1.0.0 therefore provides a MATLAB-independent Python/JAX implementation with an explicit evidence model separating direct parity, scoped reference limitations, backend applicability, and future performance claims.

## 1. Introduction

Computational models of learning under uncertainty must often represent multiple interacting sources of uncertainty, including uncertainty about latent states and uncertainty about the volatility of those states. The Hierarchical Gaussian Filter (HGF) was introduced as a generic hierarchical Bayesian framework for individual learning under uncertainty [@mathys2011] and later developed into a practical filtering framework for perception and learning [@mathys2014]. The associated MATLAB toolbox has become a useful reference implementation for fitting, simulation, model comparison, and analysis workflows.

Reproducing such a toolbox in another language is not equivalent to translating mathematical equations. Scientific behavior also depends on parameter ordering, transforms, prior conventions, fixed/free parameter semantics, placeholder values, numerical primitives, finite-difference behavior, optimizer trajectories, failure modes, and model-family selection. Small floating-point differences that are negligible at a shared state may be amplified by derivative estimation and non-convex optimization. A replacement implementation can therefore appear mathematically correct while producing materially different fitted inferences or model-selection outcomes.

HGFX was developed to address this problem with a reference-first validation strategy. The v1.0 target is not a generic HGF-like Python package; it is a validated Python/JAX reproduction of the scientific and workflow behavior of a frozen MATLAB HGF Toolbox 8.2.0 reference in explicitly documented scopes. The frozen MATLAB source is used as a development-time oracle, while users of the released package do not require a MATLAB runtime.

JAX provides array programming, automatic differentiation, compilation, and accelerator execution from Python [@jax2018github; @frostig2018]. HGFX uses these capabilities to support modern CPU/GPU execution and batching infrastructure, but accelerator support is treated as secondary to scientific compatibility. The project therefore separates four categories of evidence: direct MATLAB/HGFX parity, matched reference limitations, backend/applicability evidence, and performance/scaling evidence.

This paper asks whether a legacy scientific toolbox can be reproduced in a modern accelerator-compatible stack without silently changing the scientific contract. We report the released v1.0.0 evidence, including successful workflow reproduction, paired model-selection agreement, CPU/backend and physical-GPU applicability, preserved historical failures, and the numerical compatibility cases that motivated explicit reference-limitation semantics.

## 2. Design goals and software scope

### 2.1 Frozen reference target

HGFX v1.0.0 is validated against HGF Toolbox 8.2.0 at the frozen reference commit `2437f4dc241541072722a2695ddeca7b44d83dd3`. The immutable HGFX release source is commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`, tagged `v1.0.0`.

The compatibility target includes the documented v1 model/configuration inventory, parameter transforms and priors, HGF/eHGF/uHGF and specialized implementations in the migration matrix, observation models, fitting and simulation surfaces, Hessian/covariance/correlation/statistical outputs, model selection, official workflow behavior, and public compatibility APIs.

### 2.2 Python/JAX execution model

HGFX requires Python 3.11 or newer and depends on NumPy and JAX. The public surface exposes Python-first and MATLAB-style aliases for fitting, simulation, and sampling, including `fit_model`/`fitModel`, `sim_model`/`simModel`, and `sample_model`/`sampleModel`.

The implementation distinguishes compatibility-sensitive execution from fast JAX-backed execution. This distinction is important because a modernized numerical path can be mathematically close to MATLAB while differing in elementary floating-point behavior or optimizer trajectory. Compatibility repairs were therefore introduced only when supported by an exact reference case and regression evidence.

### 2.3 Evidence classifications

We use the following interpretation classes throughout the project and manuscript:

- **PASS / direct parity:** the tested MATLAB and HGFX surfaces agree under the frozen protocol and tolerance.
- **REFERENCE_LIMITATION_MATCH:** the exact tested MATLAB oracle exhibits the same limitation or failure regime, so HGFX reproduces reference behavior for that scope; this is not a scientific success claim.
- **FAIL_PRESERVED:** an experiment failed its scientific criterion and remains part of the record.
- **PASS_CPU_BACKEND_EQUIVALENCE:** validated backend outputs agree on the tested CPU surface.
- **PASS_PHYSICAL_GPU_APPLICABILITY:** a physical GPU executes the tested numerical path and agrees with the frozen CPU criterion; this does not imply a performance or scaling claim.

This classification scheme prevents product-compatibility acceptance from being confused with scientific identifiability or parameter-recovery success.

### 2.4 Relationship to pyhgf

pyhgf is an established Python/JAX HGF-related library that represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference workflows [@legrand2026pyhgf]. HGFX and pyhgf therefore overlap scientifically, but their design centers are not identical. HGFX v1.0 is organized around behavioral compatibility with a frozen MATLAB HGF Toolbox 8.2.0 oracle and explicit cross-language validation/provenance, whereas pyhgf emphasizes generalized network construction and extensibility. We treat these as design differences rather than a ranking.

For empirical positioning, `pyhgf==0.3.2` was pinned before execution and a direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. Quantities without a defensible common semantic/numerical surface are reported as not directly comparable rather than forced into a winner/loser comparison.

## 3. Validation methodology

### 3.1 Reference-first validation hierarchy

The evidence hierarchy is: frozen reference identity and manifests; milestone/gate documents and machine-readable validation artifacts; paired MATLAB/HGFX raw outputs; CI run/job/artifact provenance; and manuscript tables/figures generated from frozen data.

Acceptance thresholds, seeds, datasets, starts, model families, optimizers, and validation grids are not changed after observing results in order to manufacture agreement. Failed experiments remain archived when a later protocol or implementation repair is introduced.

### 3.2 Configuration and numerical equivalence

The migration program first established reference-source and configuration identity, followed by scalar numerical parity, HGF/eHGF/uHGF forward parity, observation-model parity, objective parity, compatibility fitting, Hessian and model-quality statistics, simulation parity, specialized model coverage, public compatibility APIs, GPU fitting, batching, and multi-device infrastructure.

Numerical validation is generally performed in IEEE-754 binary64 precision. The project does not target arbitrary-precision solutions that are mathematically different from the frozen MATLAB execution behavior. When an elementary runtime primitive materially affected compatibility, the protocol required an exact MATLAB oracle case, a failing regression, the smallest evidence-backed repair, and a rerun of unchanged scientific gates.

### 3.3 Official MATLAB workflow reproductions

Two official workflows from the frozen MATLAB demo are release-gated and reproduced as Python examples. Both use the official binary input of 320 trials. Complete release-relevant trajectories and inference states are compared at frozen `rtol=5e-11` and `atol=5e-13` tolerances.

The first workflow exercises a regime in which the classic binary HGF encounters negative posterior precision while the eHGF succeeds. HGFX reproduces this model-selection behavior: classic `hgf_binary` fails in both implementations, `ehgf_binary` succeeds in both implementations, and the eHGF trajectories/inference states agree within the frozen tolerance. The final classification is `PASS_MODEL_SELECTION_PARITY`.

The second workflow reproduces the transition from uHGF to uHGF-AR(1). For a descriptive reference quantity, the maximum absolute third-level posterior mean is `16.99162398501939` for uHGF and `4.0927117005012175` for uHGF-AR(1) in both the frozen MATLAB reference and the validated HGFX revision. The full checker compares more than these extrema and returns `PASS_UHGF_AR1_WORKFLOW_PARITY` with an empty mismatch list.

### 3.4 Fitting, model quality, and reference limitations

Fitting validation covers objective values at fixed parameters, MATLAB-compatible optimizer behavior, final fitted parameters where direct parity is expected, trajectories, predictions/residuals, Hessian-derived covariance/correlation, and information/model-quality statistics including AIC, BIC, and LME.

Two exact fitting cases, D02 and D08, are retained as scoped reference limitations in the v1 release accounting. Their direct failures are not hidden. The MATLAB reference itself exhibits endpoint/basin sensitivity in the validated scopes, and the final product accounting classifies the exact shared limitation as `REFERENCE_LIMITATION_MATCH`. This classification is deliberately narrower than claiming that the fitted scientific inference is correct.

### 3.5 Parameter recovery and model selection

The historical M18 scientific recovery experiment failed and is preserved. Subsequent paired product-level validation distinguishes parameter recovery from model selection. Exact-grid parameter-recovery limitations remain a scoped `REFERENCE_LIMITATION_MATCH`, while paired model selection passes: 36 of 36 BIC winners agree between MATLAB and HGFX under the recorded protocol.

This distinction is important. A toolbox can reproduce the reference model-selection decision even when parameters are weakly identified or the reference optimizer is unstable. We therefore do not use paired model-selection agreement to imply strong parameter identifiability.

### 3.6 CPU/backend and physical-GPU validation

The post-review CPU/backend gate returns `PASS_CPU_BACKEND_EQUIVALENCE`. Physical NVIDIA GPU applicability was independently recorded on two Tesla T4 devices in a hosted/shared environment. The run used Python 3.12.13 and JAX/JAXLIB 0.11.1 with the JAX `gpu` backend and physical process residency visible in `nvidia-smi`.

All four required CPU-versus-GPU fitting cells pass the unchanged final-objective criterion of `<=1e-7`. The maximum observed objective gap is `1.4210854715202004e-14`. This evidence supports numerical applicability of the tested NVIDIA/JAX/CUDA path. It does not establish peak speed, H100 performance, or general multi-GPU scaling.

### 3.7 Prospectively frozen pyhgf common-scope comparison

The external-comparator cell used `hgfx==1.0.0` and `pyhgf==0.3.2` in an Ubuntu 24.04 CPU environment with Python 3.12.14, NumPy 2.3.3, JAX/JAXLIB 0.6.2, JAX x64 enabled, and float64 mapped arrays. The test case was a fixed-parameter three-level binary HGF with standard volatility updates, mean-field updates, unit value/volatility coupling, zero drift, fully observed binary input, and unit time. The explicit 128-trial input and response arrays, package identities, inverse temperature, output fields, guards, and tolerances were committed before any cross-tool numerical output was inspected.

Trajectory and per-trial quantities used prospectively frozen `atol=1e-10` and `rtol=1e-8`; participant-response total NLL used `atol=1e-7` and `rtol=1e-8`. The raw per-implementation arrays and boundary diagnostics were written first, assigned a canonical SHA-256, reopened and verified, and only then interpreted. The protocol also prospectively specified that a derived surprise/response-NLL boundary nonfinite would be `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`, rather than triggering post-result clipping or tolerance changes.

### 3.8 Independent review and release freeze

Before the final release, an independent review identified two HIGH portability blockers: host CRT/libm dependence in compatibility-sensitive `expm1`/`log` paths and Windows CRLF behavior that could trigger false frozen-reference hash failures. Both were remediated without modifying frozen acceptance criteria.

Post-remediation regression passed on Ubuntu and Windows; the recorded Windows run reported 178 passed, 4 skipped, and 0 failed tests. Release-readiness, backend robustness, full demo composition, and M19/M20 preflight gates also passed. M19 then froze the release evidence manifest with status `FROZEN` and no failures, and M20 returned `PASS_M20_CANDIDATE` before the final 1.0.0 promotion.

## 4. Results

### 4.1 Release and workflow-equivalence result

HGFX v1.0.0 was released from the immutable source commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. The release requires no MATLAB runtime for users. MATLAB is needed only when regenerating cross-language oracle evidence.

The official demo reproductions establish concrete workflow equivalence for the tested model-family selection and uHGF-AR(1) workflows. These results are stronger than a code-path smoke test because the CI workflows execute the MATLAB oracle, execute the Python reproduction, compare complete release-relevant outputs under frozen tolerances, and archive machine-readable evidence artifacts.

### 4.2 Fitting and statistical outputs

The v1 validation matrix covers objective, fitting, Hessian/covariance/correlation, information criteria, and analysis surfaces in their documented scopes. D02 and D08 remain explicitly marked as exact-scope reference limitations rather than being silently relaxed into direct fit parity. The release therefore claims MATLAB-equivalent behavior in the accepted product accounting, not universal optimizer endpoint identity across all numerically sensitive cases.

### 4.3 Recovery and paired model selection

Historical parameter-recovery failure remains part of the scientific record. Paired model selection is stronger: all 36 BIC winners match between the MATLAB and HGFX runs under the frozen paired protocol. This supports preservation of the tested model-selection decision surface while leaving parameter identifiability as a separate scientific question.

A post-v1 trial-horizon study is planned to distinguish data-horizon limitation from weak or structural identifiability without changing the historical criterion. Until that prospective experiment is completed, the manuscript does not claim that HGFX or the MATLAB reference provides generally strong parameter recovery across the tested HGF families.

### 4.4 Backend and accelerator applicability

Compatibility CPU and JAX-backed CPU outputs pass the post-review backend-equivalence gate. On physical Tesla T4 hardware, the maximum final-objective difference between required CPU and GPU fitting cells is `1.4210854715202004e-14`, substantially below the pre-existing `1e-7` criterion.

This result demonstrates that the tested JAX GPU path can preserve the validated numerical objective surface on physical hardware. Performance is intentionally not inferred from this result. Historical H100/T4 scaling measurements are retained in the repository in their original scope, but a new prospectively frozen paper benchmark is required before speed or scaling becomes a headline claim.

### 4.5 Frozen common-scope comparison with pyhgf

In the prospectively frozen 128-trial comparator case, all 11 mapped perceptual/inference quantities passed their predeclared tolerances. Maximum absolute differences were at binary64 rounding scale: `1.1102230246251565e-16` for first-level predicted probability, `4.440892098500626e-16` for level-2 means, `6.661338147750939e-16` for level-2 precisions, and `1.5543122344752192e-15` for level-3 precisions. Derived first-level prediction error and input surprise also passed, with maximum absolute differences of `1.1102230246251565e-16` and `4.440892098500626e-16`, respectively. Observed-input integrity was exact.

The retained participant-response NLL surface was not directly comparable under the frozen numerical construction. With inverse temperature `ze=48`, the explicit power-ratio response transformation on the pyhgf side reached an exact probability boundary on 13 trials and the unclipped surprise became `+Inf`; the HGFX log-domain `unitsq_sgm` evaluation remained finite, with total NLL `1808.855415351429`. Because the pre-execution protocol had already classified response-NLL boundary nonfinites as `NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY`, no clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. The overall comparator classification is therefore `PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES`, not general tool equivalence.

### 4.6 Reproducibility and provenance

The release evidence index records the frozen MATLAB reference, final source revision, workflow classifications, physical-GPU evidence, independent review/remediation, release-gate runs, and final release provenance. M19 committed a machine-readable frozen evidence manifest rather than relying on a narrative statement that validation had completed.

The paper-specific reproducibility package will build on this foundation by generating manuscript tables and figures from committed evidence and recording the exact inputs and hashes used by each output.

## 5. Discussion

HGFX demonstrates that reproducing a scientific toolbox requires a broader notion of compatibility than implementing the published equations. The most difficult mismatches were not necessarily large forward-model errors. In numerically sensitive fitting problems, binary64-scale elementary differences can be amplified through finite-difference derivatives and quasi-Newton optimization, causing different endpoints or inferences even when shared-state objectives are extremely close.

This observation motivates the distinction between scientific correctness and reference faithfulness. When the MATLAB oracle itself is unstable to tiny changes in the tested scope, forcing the Python implementation toward a single preferred optimizer endpoint can be less faithful than preserving the oracle's limitation. Conversely, a matched reference limitation is not evidence that the recovered parameter is scientifically identifiable. HGFX therefore preserves the original failure and reports the narrow product-compatibility interpretation separately.

The official demo results also illustrate why workflow-level validation matters. Reproducing the expected failure of the classic HGF in a specific regime, while reproducing successful eHGF behavior, is part of compatibility. Treating every failure as an implementation bug would have encouraged divergence from the actual reference semantics.

JAX enables a modern path toward compiled CPU/GPU execution, batching, and multi-device workloads [@jax2018github; @frostig2018]. However, accelerator-native implementation is useful for scientific software only if the accelerated path preserves the relevant scientific outputs. The physical-GPU evidence in this paper is therefore framed as applicability/correctness evidence. A separate prospective benchmark is required for performance claims because throughput depends strongly on workload size, compilation amortization, hardware, device count, and host contention.

The external pyhgf comparison reinforces the value of quantity-specific compatibility claims. The mapped HGF belief trajectories agree to binary64 rounding scale in the single authorized common-scope case, while the response-NLL surface exposes a numerical-boundary difference despite sharing the same underlying predicted belief. Preserving the prospectively defined `NOT_DIRECTLY_COMPARABLE` outcome is more informative than changing clipping or reformulating the response computation after inspecting the result.

The strongest current contribution is thus methodological: a Python/JAX reproduction process that makes the reference oracle, evidence classifications, numerical compatibility policy, historical failures, and release provenance explicit. This reduces the risk that a modern implementation gains convenience or speed by silently changing the scientific contract.

## 6. Limitations

First, validation is scoped to the frozen HGF Toolbox 8.2.0 reference and the documented v1 model/workflow matrix. HGFX v1.0.0 should not be interpreted as an automatic compatibility claim for future upstream HGF versions.

Second, exact optimizer endpoint identity is not achieved or claimed for every numerically sensitive fitting case. D02 and D08 are retained as scoped reference-limitation matches, and their underlying scientific limitations remain visible.

Third, historical parameter-recovery results include failures. The current evidence supports paired model-selection agreement more strongly than general parameter identifiability. A prospective trial-horizon analysis is planned to characterize this distinction.

Fourth, the physical-GPU result establishes numerical applicability on the tested Tesla T4 environment. It does not establish general speedup, H100 performance, uncontended peak performance, or strong multi-GPU scaling. Those claims require a new frozen paper benchmark.

Fifth, the direct pyhgf evidence is intentionally narrow: one fixed-parameter, fully observed, three-level binary-HGF case under an explicitly mapped standard/mean-field configuration. It supports the reported common-scope trajectory result but not general equivalence across model families, fitting workflows, missing-data semantics, observation models, or package capabilities. The participant-response NLL surface is explicitly retained as not directly comparable under the frozen numerical construction.

Sixth, the current working manuscript still requires generated paper tables/figures, a complete paper-specific reproduction bundle, final author/affiliation metadata, target-journal formatting, and an independent pre-submission review.

## 7. Reproducibility and availability

HGFX v1.0.0 is released under the MIT license. The immutable source target is `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` and the Git tag is `v1.0.0`. The frozen MATLAB HGF Toolbox 8.2.0 oracle is pinned at `2437f4dc241541072722a2695ddeca7b44d83dd3` and is used for validation only; no MATLAB runtime is required by end users.

The repository records aggregate evidence in `docs/validation/V1_EVIDENCE_INDEX.md`, the M19 freeze in `docs/planning/M19_GATE.md`, official demo reproduction instructions in `docs/user/MATLAB_DEMOS.md`, and paper claim provenance in `docs/research/PAPER_EVIDENCE_MAP.md`.

`paper/reproducibility/` now includes the frozen paper protocol and the P2A external-comparator case, authorization gate, byte-for-byte raw numerical result, post-hash comparison artifact, exact resolved environment, and workflow/artifact provenance. Before submission, the remaining selected paper outputs must receive the same input-hash and regeneration treatment, followed by the final `FROZEN_FOR_SUBMISSION` evidence manifest.

## 8. Conclusion

HGFX v1.0.0 provides a Python/JAX implementation of the Hierarchical Gaussian Filter toolbox whose validation target is explicitly anchored to a frozen MATLAB HGF Toolbox 8.2.0 oracle. The release reproduces required workflows in documented scopes, preserves paired model-selection behavior, validates CPU/backend and physical-GPU numerical applicability, and removes MATLAB from the user runtime. Equally importantly, it preserves failed recovery experiments and distinguishes exact reference-limit matches from scientific success. This evidence discipline is central to using modern numerical and accelerator software without silently changing the behavior of an established scientific reference implementation.

## Declarations to complete for submission

- Author contributions.
- Affiliations and corresponding author.
- Funding statement.
- Conflict-of-interest statement.
- Acknowledgments.
- Target-journal-specific data/code availability wording.
- Target-journal formatting and supplementary-material structure.

## References

Bibliography entries are maintained in `paper/references.bib`.
