# HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox

**Preprint version for arXiv.** The scientific results and thresholds are identical to the frozen paper evidence; presentation is simplified for readers, while repository identifiers and exact provenance are kept in the supplementary traceability appendix.

**Authors and affiliations**

Mohammad Ahmadkhanloo  
Institute for Research in Fundamental Sciences (IPM), Tehran, Iran  
https://github.com/ahmadkhanloo

**Correspondence:** Mohammad Ahmadkhanloo, Institute for Research in Fundamental Sciences (IPM), Niavaran Square, Tehran, Iran. Email: m.ahmadkhanloo@ipm.ir. Software: https://github.com/ahmadkhanloo/hgfx.

**Keywords:** Hierarchical Gaussian Filter; computational neuroscience; Bayesian learning; Python; reproducibility; model validation

## Abstract

The Hierarchical Gaussian Filter (HGF) is a hierarchical Bayesian model of learning under uncertainty and volatility, with a widely used MATLAB implementation. We present HGFX 1.0.0, a Python/JAX toolbox whose primary objective is validated behavioral and numerical compatibility with a frozen HGF Toolbox 8.2.0 reference, while removing MATLAB as a user-runtime dependency. Reimplementation is treated as a validation problem rather than source translation: configuration semantics, parameter transforms, forward trajectories, observation likelihoods, objectives, fitting and statistical surfaces, simulation workflows, official demo behavior, model selection, and backend agreement are compared against the pinned oracle under predeclared tolerances. Two official MATLAB demo workflows reproduce the reference at frozen trajectory tolerances, including a regime in which classic HGF encounters negative posterior precision while eHGF completes successfully. In paired model-selection validation, all 36 BIC winners agree between MATLAB and HGFX. Physical NVIDIA GPU applicability was confirmed on two Tesla T4 devices, with a maximum CPU-versus-GPU final-objective difference of 1.42e-14 against a frozen 1e-7 criterion. Historical parameter-recovery results that did not meet predeclared criteria, together with exact MATLAB/HGFX limitation matches, are preserved and are not reclassified as scientific success. A prospectively gated comparison with pyhgf 0.3.2 shows binary64-scale agreement on mapped perceptual trajectories in one authorized three-level binary-HGF cell, while participant-response negative log-likelihood is retained as not directly comparable. HGFX therefore provides a MATLAB-independent Python implementation with an explicit evidence model that separates direct parity, matched reference limitations, backend applicability, and future performance claims.

## 1 Introduction

Computational models of learning under uncertainty must represent uncertainty about latent states and about the volatility of those states. The Hierarchical Gaussian Filter (HGF) was introduced as a generic hierarchical Bayesian framework for individual learning under uncertainty [@mathys2011] and later developed into a practical filtering framework for perception and learning [@mathys2014]. It has been used to recover hierarchical prediction errors in neuroimaging [@iglesias2013] and to model inference about others' intentions [@diaconescu2014]. The associated MATLAB toolbox is distributed as part of TAPAS, an open-source collection of translational neuromodeling tools [@fraessle2021tapas], and remains a reference implementation for fitting, simulation, model comparison, and analysis.

Reproducing such a toolbox in another language is not equivalent to translating published equations. Scientific behavior also depends on parameter ordering, transforms, prior conventions, fixed and free parameter semantics, placeholder values, numerical primitives, finite-difference behavior, optimizer trajectories, adverse numerical modes, and model-family selection. Small floating-point differences that are negligible at a shared state can be amplified by derivative estimation and non-convex optimization [@wilson2019ten; @peng2011reproducible]. A replacement implementation can therefore appear mathematically correct while producing materially different fitted inferences or model-selection outcomes.

Python/JAX toolboxes already exist in this space. pyhgf represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference [@legrand2026pyhgf]. HGFX does not claim to be the first Python or JAX HGF. Its v1.0 objective is narrower and complementary: behavioral compatibility with one frozen MATLAB HGF Toolbox 8.2.0 oracle, explicit cross-language evidence, and removal of MATLAB from the user runtime.

This paper asks whether a legacy scientific toolbox can be reproduced in an accelerator-compatible stack without silently changing the scientific contract. We report the released HGFX 1.0.0 evidence: workflow reproduction, paired model-selection agreement, CPU/backend and physical-GPU applicability, a scoped pyhgf comparison, and preserved historical negative results. General speedup and multi-GPU scaling are not headline claims.

For neuroscience methodology, the contribution is a reproducible route for re-running established HGF analyses outside the MATLAB runtime while retaining the validated reference behavior that underpins prior computational-neuroscience and computational-psychiatry applications. The study therefore evaluates software behavior, inferential workflows, and reproducibility rather than introducing a new behavioral or neuroimaging dataset.

## 2 Materials and methods

### 2.1 Software description

HGFX is a Python package (Python >= 3.11) built on NumPy and JAX [@jax2018github; @frostig2018]. The public surface exposes Python-first and MATLAB-style aliases (`fit_model`/`fitModel`, `sim_model`/`simModel`, `sample_model`/`sampleModel`). Compatibility-sensitive numerical paths are distinguished from JAX-backed execution. Compatibility repairs were introduced only when supported by an exact MATLAB oracle case and a regression that violated expected behavior.

OpenAI ChatGPT was used during software development for code drafting and review, repository maintenance, and consistency checks. AI-assisted changes were reviewed by the author and accepted only after the same regression, parity, and evidence gates as other changes; AI output was not treated as scientific evidence.

Software metadata and frozen validation identities are summarized in Table 1.

**Table 1.** HGFX 1.0.0 software metadata.

| Item | Value |
|---|---|
| Name | HGFX |
| Version | 1.0.0 |
| Source | https://github.com/ahmadkhanloo/hgfx |
| Release | https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0 |
| PyPI | `hgfx==1.0.0` |
| Validated CI platforms | Linux (Ubuntu) and Windows |
| Language | Python 3.11+ |
| License | MIT (no restriction on non-academic use) |
| Dependencies | NumPy, JAX |
| Frozen MATLAB oracle | HGF Toolbox 8.2.0 (exact source revision in Supplementary Appendix S6) |
| Frozen HGFX source | HGFX 1.0.0 (exact source revision in Supplementary Appendix S6) |

Users do not require MATLAB. MATLAB is used only when regenerating cross-language oracle evidence. The HGF Toolbox is cited via Mathys et al. [@mathys2011; @mathys2014] and TAPAS [@fraessle2021tapas]. Related probabilistic-modelling software includes the VBA toolbox [@daunizeau2014vba].

### 2.2 Covered HGF families

The HGF represents a hidden hierarchy of Gaussian states in which higher levels encode volatility of lower levels [@mathys2011; @mathys2014]. For binary observations, a unit-square sigmoid observation model maps the first hidden state to the probability of the observed outcome. HGFX v1.0 covers the classic HGF, the enhanced HGF (eHGF), and the unbounded HGF (uHGF) in the documented MATLAB-compatible configurations, plus specialized surfaces in the v1 migration matrix (sampling, analysis, Bayesian parameter averaging, and the official uHGF-AR(1) demo). Equations are those of the frozen MATLAB toolbox; this article does not introduce a new generative model.

The public fitting interface accepts perceptual and observation configurations, a default transformed start, and a Quasi-Newton optimizer with a frozen iteration budget in the paper protocols. Simulation exports inputs `u` and responses `y` that become immutable paired inputs when MATLAB is used as an oracle.

### 2.3 Frozen reference and evidence classes

HGFX v1.0 is validated against the frozen HGF Toolbox 8.2.0 reference. Exact source revisions are provided in Supplementary Appendix S6. The compatibility target includes the documented model/configuration inventory, parameter transforms and priors, HGF/eHGF/uHGF and specialized implementations, observation models, fitting and simulation surfaces, Hessian/covariance/correlation/statistical outputs, model selection, official workflow behavior, and public APIs.

We use four interpretation classes:

- **Direct numerical agreement:** MATLAB and HGFX agree under the frozen protocol and tolerance.
- **Matched reference limitation:** the MATLAB oracle exhibits the same numerical or workflow limitation in the same frozen scope; this is not a scientific recovery claim.
- **Preserved negative result:** a predeclared scientific criterion is not met and the result remains archived.
- **Not directly comparable (NDC):** a quantity lacks a defensible common semantic or numerical surface, most relevant to the pyhgf comparison.

Acceptance thresholds, seeds, datasets, starts, model families, optimizers, and grids are not changed after observing results. Results outside predeclared criteria remain archived. The numerical policy and the two most sensitive optimizer/basin cases are documented in Supplementary Appendices S1-S2.

### 2.4 Validation hierarchy

The evidence hierarchy is: frozen reference identity; machine-readable validation artifacts; paired MATLAB/HGFX raw outputs; continuous-integration provenance; and manuscript tables/figures generated from those artifacts. Numerical checks use IEEE-754 binary64. The project does not target arbitrary-precision solutions that differ from frozen MATLAB execution.

Two official MATLAB demo workflows (320 binary trials) are release-gated. Complete release-relevant trajectories and inference states are compared at `rtol = 5e-11` and `atol = 5e-13`.

Fitting validation covers objectives at fixed parameters, MATLAB-compatible optimizer behavior, fitted parameters where direct parity is expected, trajectories, predictions/residuals, Hessian-derived covariance/correlation, and AIC/BIC/LME.

An earlier frozen parameter-recovery experiment did not meet its scientific acceptance criteria and remains preserved. Subsequent paired validation distinguishes parameter recovery from model selection on a frozen three-model grid (three binary perceptual models; truth scales 0.15 and 0.35; Quasi-Newton; predeclared thresholds: convergence rate >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00, model-recovery balanced accuracy >= 0.50).

CPU/backend equivalence and physical NVIDIA GPU applicability were tested after an independent review of portability blockers (host C runtime `expm1`/`log` paths and Windows CRLF hash mismatches). Both blockers were remediated without changing scientific thresholds.

### 2.5 pyhgf common-scope protocol

`pyhgf==0.3.2` was pinned before execution. Direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. The authorized cell is a fixed-parameter, fully observed, three-level binary HGF (128 trials; standard/mean-field updates; unit coupling; zero drift; inverse temperature `ze = 48`). Trajectory quantities used `atol = 1e-10` and `rtol = 1e-8`; total response NLL used `atol = 1e-7` and `rtol = 1e-8`. Raw arrays were hashed before interpretation. A derived response-NLL boundary nonfinite was prospectively classified as NDC rather than triggering post-result clipping.

### 2.6 Prospective trial-horizon protocol

A prospectively frozen paired MATLAB/HGFX trial-horizon experiment examined 128, 256, 512 and 1024 trials using the same three perceptual models, truth scales, seeds, Quasi-Newton budget, and predeclared recovery thresholds. The preregistered scientific comparison was 256 versus 1024 after a paired-integrity gate; 128 and 512 were trajectory diagnostics. Invalid simulations and fits outside the preregistered criteria were retained rather than resampled. The experiment completed all 24 preregistered shards. The paired-integrity requirement was not satisfied: 10 of 72 model-recovery BIC winners disagreed, all for the classic binary HGF at 512 or 1024 trials, and parameter metrics for those horizons were undefined because invalid simulations were retained. The evidence was therefore judged insufficient to support a data-horizon or structural-identifiability conclusion.

## 3 Results

### 3.1 Workflow equivalence

HGFX 1.0.0 was used for all release-level comparisons. Official demo reproductions execute the MATLAB oracle and the Python reproduction on matched inputs, compare complete release-relevant outputs, and archive machine-readable artifacts (Table 2). Exact source identity is reported in Supplementary Appendix S6.

The first demo is a regime in which classic binary HGF encounters negative posterior precision while eHGF succeeds. HGFX reproduces this: `hgf_binary` reaches negative posterior precision in both implementations, `ehgf_binary` completes in both, and eHGF trajectories agree within the frozen tolerance (workflow parity).

The second demo reproduces the uHGF to uHGF-AR(1) transition. The maximum absolute third-level posterior mean is 16.99162398501939 for uHGF and 4.0927117005012175 for uHGF-AR(1) in both implementations (direct uHGF-AR(1) workflow parity).

**Table 2.** Official workflow and analysis-surface coverage. Machine-readable source data are available in the reproducibility package.

| Surface | Classification |
|---|---|
| Core model/API compatibility (documented scopes) | Agreement within documented compatibility scope |
| uHGF to AR(1) official workflow | Reference trajectory reproduced within frozen tolerance |
| sampleModel / prior-predictive workflow | Reference workflow reproduced |
| Correlation/residual analysis surfaces | Reference outputs reproduced within frozen tolerances |
| Bayesian parameter averaging | Reference outputs reproduced within frozen tolerances |

### 3.2 Fitting statistics and scoped limitations

Two fitting-validation cases expose reference limitations rather than direct fitting parity (Table 3). In an official fitting stress case, MATLAB and HGFX can terminate at different optimizer endpoints in a numerically sensitive basin. In a separate frozen Level-2 holdout case, the inference-equivalence criterion is not met for a specific seed. In both cases the frozen MATLAB oracle shows the corresponding instability or sensitivity, so these results are reported as matched reference limitations rather than as successful parameter recovery.

**Table 3.** Fitting and recovery classifications. Direct mismatches and negative results are retained.

| Surface | Direct result | Paper disposition |
|---|---|---|
| Earlier frozen parameter-recovery experiment | scientific criteria not met | preserved negative result |
| Official fitting stress case | optimizer endpoint mismatch in sensitive basin | MATLAB reference shows the same start sensitivity |
| Frozen Level-2 holdout fit | inference-equivalence criterion not met for a fixed seed | MATLAB reference shows the same start sensitivity |
| Paired parameter recovery | recovery criteria not fully met in either implementation | paired numerical behavior closely reproduced |
| Paired model selection | 36/36 BIC winners match | direct agreement |

### 3.3 Parameter recovery versus model selection

Paired parameter-recovery summaries are shown in Figure 1 and Table 4. MATLAB and HGFX closely reproduce the same recovery summaries, but the predeclared scientific recovery criteria are not fully met. Paired model selection is stronger: all 36/36 BIC winner decisions match between MATLAB and HGFX in the same frozen grid. Model-selection agreement is not used to imply strong parameter identifiability. Full grid dimensions, frozen thresholds, and the prospective trial-horizon extension are reported in Supplementary Appendix S3.

The trial-horizon study (section 2.6) is complete as an executed protocol, not as a positive identifiability result. Because its paired-integrity requirement was not satisfied, the available evidence is insufficient for a stronger recovery or identifiability conclusion. Diagnostic per-horizon values are shown in Figure 2; they do not replace the earlier recovery evidence.

**Table 4.** Paired parameter recovery on the frozen three-model grid (both truth scales). Thresholds: convergence >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00. Full-precision values are available in the reproducibility package.

| Model | MATLAB / HGFX convergence | MATLAB / HGFX median r | MATLAB / HGFX median sRMSE | Criteria outside target |
|---|---|---|---|---|
| hgf_binary | 0.833 / 0.833 | 0.203 / 0.203 | 2.610 / 2.610 | correlation, sRMSE |
| ehgf_binary | 0.917 / 0.917 | 0.462 / 0.462 | 2.359 / 2.359 | correlation, sRMSE |
| uhgf_binary | 0.792 / 0.792 | 0.381 / 0.381 | 2.958 / 2.958 | convergence, correlation, sRMSE |

### 3.4 Backend and physical-GPU applicability

Compatibility CPU and JAX-backed CPU outputs agree under the frozen backend-equivalence criterion. On two Tesla T4 GPUs (Python 3.12.13, JAX/JAXLIB 0.11.1, `nvidia-smi` process residency), all four required CPU-versus-GPU fitting cells remain below the predeclared final-objective difference criterion of 1e-7. The maximum gap is 1.4210854715202004e-14 (Table 5). This is applicability/correctness evidence, not a speed or scaling result. Exact hardware/runtime provenance, the four CPU-versus-GPU objective pairs, the execution command, and the raw-artifact checksum are reported in Supplementary Appendix S5.

**Table 5.** Backend and GPU applicability.

| Surface | Classification | Result |
|---|---|---|
| Compatibility vs JAX CPU | direct backend agreement | objective/backend agreement |
| Physical NVIDIA GPU (2x Tesla T4) | physical-GPU applicability confirmed | max abs objective gap = 1.42e-14; criterion 1e-7 |

### 3.5 Common-scope comparison with pyhgf

In the authorized 128-trial cell, all 11 mapped perceptual/inference quantities were within predeclared tolerances (Figure 3). Maximum absolute differences were at binary64 rounding scale (1.11e-16 to 1.55e-15). Observed-input integrity was exact.

Participant-response NLL was not directly comparable. With `ze = 48`, the pyhgf-side power-ratio transformation reached an exact probability boundary on 13 trials and unclipped surprise became +Inf; the HGFX log-domain `unitsq_sgm` evaluation remained finite (total NLL 1808.855415351429). No clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. Overall interpretation: mapped perceptual quantities agree in the authorized cell, while participant-response NLL remains not directly comparable. The semantic gate, exact comparator identity, and numerical-boundary details are given in Supplementary Appendix S4.

### 3.6 Examples of use and current limitations

Typical use after `pip install hgfx==1.0.0` is MATLAB-style fitting and simulation from Python, including the official demo reproductions. MATLAB is unnecessary for those user paths.

Current limitations: (i) compatibility is scoped to HGF Toolbox 8.2.0, not future upstream versions; (ii) two numerically sensitive fitting cases are matched reference limitations rather than scientific recovery successes; (iii) parameter identifiability is weaker than paired model selection, and the trial-horizon experiment did not satisfy its paired-integrity requirement, so it does not support a stronger recovery claim; (iv) GPU evidence is T4 applicability, not throughput; and (v) the pyhgf result is one mapped cell, not package-wide equivalence.

## 4 Discussion

Reproducing a scientific toolbox requires a broader notion of compatibility than implementing published equations. In numerically sensitive fitting problems, binary64-scale elementary differences can be amplified through finite-difference derivatives and quasi-Newton optimization, producing different endpoints even when shared-state objectives are extremely close.

This motivates separating scientific correctness from reference faithfulness. When the MATLAB oracle is itself unstable in a tested scope, forcing Python toward a preferred endpoint can be less faithful than preserving the oracle's limitation. A matched limitation is not evidence that the recovered parameter is identifiable. HGFX therefore preserves the original negative results and reports the narrow product-compatibility interpretation separately.

Workflow-level validation matters for the same reason. Reproducing the expected negative-posterior-precision behavior of classic HGF in a documented regime, while reproducing successful eHGF behavior, is part of compatibility. Treating every adverse or unstable outcome as an implementation bug would have encouraged divergence from the reference.

pyhgf and HGFX overlap but have different design centers. pyhgf emphasizes generalized network construction and differentiability [@legrand2026pyhgf]. HGFX v1.0 emphasizes frozen-MATLAB compatibility and provenance. Quantity-specific claims are more informative than ranking the packages. Mapped belief trajectories agree to rounding scale in the authorized cell; the response-NLL surface exposes a numerical-boundary difference despite sharing the same predicted belief.

JAX enables compiled CPU/GPU execution, batching, and multi-device workloads [@jax2018github; @frostig2018]. Accelerator-native code is scientifically useful only if the accelerated path preserves relevant outputs. The T4 result supports that claim for the tested objective. Throughput depends on workload size, compilation amortization, hardware, device count, and contention; protocol 1 therefore does not activate a headline performance or scaling result. Scalability of the JAX path is an engineering capability of the implementation, not a reported empirical law.

The strongest contribution is methodological: an explicit oracle, evidence classes, a numerical compatibility policy, preservation of negative results, and release provenance. That discipline reduces the risk that a modern implementation gains convenience by silently changing an established scientific contract.

## 5 Data and code availability

HGFX 1.0.0 is MIT-licensed [@hgfx100]. Source, tag, and package URLs are in Table 1. All tables and figures are generated from committed machine-readable evidence by scripts included with the source repository. MATLAB is required only to regenerate paired oracle evidence. Exact source revisions, repository-facing case identifiers, checksums, workflow provenance, and claim-to-evidence traceability are intentionally confined to Supplementary Appendix S6 and the reproducibility package.

## Supplementary material guide

The supplementary appendices are intentionally separated from the main narrative so that technical audit detail does not obscure the scientific results. They are organized as follows:

- **S1 — Numerical compatibility policy:** frozen tolerances, numerical rules, and acceptance logic.
- **S2 — Numerically sensitive fitting cases:** detailed evidence for the two optimizer/basin-sensitive workflows.
- **S3 — Recovery and model-selection protocol:** full grid design, thresholds, parameter-recovery results, paired model-selection results, and the prospective trial-horizon extension.
- **S4 — pyhgf common-scope comparison:** semantic mapping, numerical comparison, and the response-NLL non-comparability boundary.
- **S5 — Physical-GPU applicability:** hardware/runtime provenance, CPU-versus-GPU objective pairs, execution command, and limitations.
- **S6 — Reproducibility and traceability:** exact source revisions, internal case identifiers, workflow provenance, hashes, and links from reader-facing claims to repository evidence.

Each appendix is cited at the point where its detail becomes relevant; S6 is the audit trail rather than part of the scientific narrative.

## Declaration of competing interest

The author is the developer and maintainer of HGFX and declares no other competing financial interests or personal relationships that could have appeared to influence the work.

## CRediT authorship contribution statement

Mohammad Ahmadkhanloo: Conceptualization, Software, Validation, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.

## Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## Acknowledgments

The frozen MATLAB HGF Toolbox 8.2.0 of Mathys and colleagues is the reference oracle for this work. GitHub Actions and MATLAB were used only to regenerate paired oracle evidence.

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work, the author used OpenAI ChatGPT to assist with code drafting and review, repository/document consistency checks, manuscript organization, and language refinement. The author reviewed and edited the resulting material as needed, and all reported scientific results remained subject to the repository's frozen validation, evidence, and reproducibility gates. The author takes full responsibility for the content of the publication.

## Figure captions

**Figure 1.** Close paired agreement coexists with weak recovery. Original-scale summaries from the frozen 72-case parameter-recovery grid are shown for classic, enhanced, and unbounded HGF. Circles denote MATLAB 8.2.0 and crosses denote HGFX 1.0.0; small vertical offsets are used only for visibility. Dotted lines mark the unchanged recovery targets. The convergence panel includes descriptive Wilson 95% intervals for 24 cases per family. Correlation and standardized-RMSE panels show point summaries because replicate-level bootstrap inputs are not available in the archived aggregate. The median-correlation and standardized-RMSE criteria are outside target in all three families.

**Figure 2.** Trial-horizon diagnostics with incomplete cells retained. Columns separate classic, enhanced, and unbounded HGF; rows show median parameter correlation and median standardized RMSE at 128, 256, 512, and 1024 trials. Dotted lines mark the original recovery targets. Shaded regions denote incomplete classic-HGF summaries at 512 and 1024 trials and are not zeros or interpolated estimates. Lines connect point summaries only. Because the whole-study paired-integrity requirement was not satisfied, these trends do not establish identifiability.

**Figure 3.** Perceptual trajectories agree at binary64 rounding scale, with residuals shown separately. HGFX 1.0.0 and pyhgf 0.3.2 are compared on the frozen 128-trial, three-level binary-HGF cell. Panels show predicted input probability, level-2 posterior mean, and the signed HGFX-minus-pyhgf probability residual in units of 1e-16. Every stored trial is plotted without smoothing. Participant-response NLL is a separate quantity and remains not directly comparable in this cell.

## References

Bibliography entries are in `paper/references.bib`.
