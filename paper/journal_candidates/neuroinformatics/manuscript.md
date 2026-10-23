# HGFX: an open-source Python/JAX implementation for reproducible Hierarchical Gaussian Filter analyses

**Article type:** Software Original Article

**Author:** Mohammad Ahmadkhanloo

**Affiliation:** Institute for Research in Fundamental Sciences (IPM), Tehran, Iran

**Corresponding author:** m.ahmadkhanloo@ipm.ir

**Keywords:** Hierarchical Gaussian Filter; computational neuroscience; scientific software; numerical validation; reproducibility; JAX

## Abstract

**Background:** Computational neuroscience studies using the Hierarchical Gaussian Filter (HGF) depend on numerical and workflow conventions embedded in its MATLAB toolbox. Reimplementing the equations alone may not reproduce fitted inference or model-selection decisions. **Methods:** We developed HGFX 1.0.0, an MIT-licensed Python/JAX software package that targets documented behavioral and numerical compatibility with a frozen HGF Toolbox 8.2.0 reference. A predeclared validation protocol compares model configurations, forward trajectories, objectives, fitting statistics, simulation, official demonstrations, model selection, and execution backends; failed experiments and reference limitations remain archived. **Results:** Two official MATLAB demonstration workflows are reproduced within their frozen trajectory criteria. All 36 Bayesian information criterion model-selection winners agree in a paired validation grid. Parameter-recovery thresholds are not fully satisfied, and a prospective trial-horizon extension does not pass its paired-integrity gate; neither outcome is recast as identifiability success. A retained physical Tesla T4 test supports GPU objective agreement for the executed cells, without providing throughput evidence. Eleven mapped perceptual quantities agree with pyhgf 0.3.2 in one authorized common-scope case, whereas response negative log-likelihood is not directly comparable. **Conclusions:** HGFX provides a publicly installable MATLAB-independent HGF workflow and a traceable compatibility validation record. Its claims remain confined to the tested configurations and must not be interpreted as general recovery, acceleration, or package-wide cross-tool equivalence.

## 1 Introduction

Computational models of learning under uncertainty must represent uncertainty about latent states and about the volatility of those states. The Hierarchical Gaussian Filter (HGF) was introduced as a generic hierarchical Bayesian framework for individual learning under uncertainty (Mathys et al., 2011) and later developed into a practical filtering framework for perception and learning (Mathys et al., 2014). It has been used to recover hierarchical prediction errors in neuroimaging (Iglesias et al., 2013) and to model inference about others' intentions (Diaconescu et al., 2014). The associated MATLAB toolbox is distributed as part of TAPAS, an open-source collection of translational neuromodeling tools (Frässle et al., 2021), and remains a reference implementation for fitting, simulation, model comparison, and analysis.

Reproducing such a toolbox in another language is not equivalent to translating published equations. Scientific behavior also depends on parameter ordering, transforms, prior conventions, fixed and free parameter semantics, placeholder values, numerical primitives, finite-difference behavior, optimizer trajectories, failure modes, and model-family selection. Small floating-point differences that are negligible at a shared state can be amplified by derivative estimation and non-convex optimization (Wilson & Collins, 2019; Peng, 2011). A replacement implementation can therefore appear mathematically correct while producing materially different fitted inferences or model-selection outcomes.

Python/JAX toolboxes already exist in this space. pyhgf represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference (Legrand et al., 2026). HGFX does not claim to be the first Python or JAX HGF. Its v1.0 objective is narrower and complementary: behavioral compatibility with one frozen MATLAB HGF Toolbox 8.2.0 oracle, explicit cross-language evidence, and removal of MATLAB from the user runtime.

This paper asks whether a legacy scientific toolbox can be reproduced in an accelerator-compatible stack without silently changing the scientific contract. We report the released HGFX 1.0.0 evidence: workflow reproduction, paired model-selection agreement, CPU/backend and physical-GPU applicability, a scoped pyhgf comparison, and preserved historical failures. General speedup and multi-GPU scaling are not headline claims.

For neuroscience methodology, the contribution is a reproducible route for re-running established HGF analyses outside the MATLAB runtime while retaining the validated reference behavior that underpins prior computational-neuroscience and computational-psychiatry applications. The study therefore evaluates software behavior, inferential workflows, and reproducibility rather than introducing a new behavioral or neuroimaging dataset.

## 2 Software and validation methods

### 2.1 Software description and availability

The software is distributed as the MIT-licensed `hgfx==1.0.0` release on PyPI and can be installed with `python -m pip install hgfx==1.0.0`. The public documentation includes a getting-started guide, API descriptions, and runnable fitting and simulation examples. HGFX is designed for established HGF analysis workflows in computational neuroscience rather than to introduce a new model of neural or behavioral data.

### 2.1.1 Software implementation

HGFX is a Python package (Python >= 3.11) built on NumPy and JAX (Bradbury et al., 2018; Frostig et al., 2018). The public surface exposes Python-first and MATLAB-style aliases (`fit_model`/`fitModel`, `sim_model`/`simModel`, `sample_model`/`sampleModel`). Compatibility-sensitive numerical paths are distinguished from JAX-backed execution. Compatibility repairs were introduced only when supported by an exact MATLAB oracle case and a failing regression.

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
| Frozen MATLAB oracle | HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3` |
| Frozen HGFX source | `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| Paper protocol | `hgfx-paper-protocol-1` |

Users do not require MATLAB. MATLAB is used only when regenerating cross-language oracle evidence. The HGF Toolbox is cited via Mathys et al. (Mathys et al., 2011; Mathys et al., 2014) and TAPAS (Frässle et al., 2021). Related probabilistic-modelling software includes the VBA toolbox (Daunizeau et al., 2014).

### 2.2 Covered HGF families

The HGF represents a hidden hierarchy of Gaussian states in which higher levels encode volatility of lower levels (Mathys et al., 2011; Mathys et al., 2014). For binary observations, a unit-square sigmoid observation model maps the first hidden state to the probability of the observed outcome. HGFX v1.0 covers the classic HGF, the enhanced HGF (eHGF), and the unbounded HGF (uHGF) in the documented MATLAB-compatible configurations, plus specialized surfaces in the v1 migration matrix (sampling, analysis, Bayesian parameter averaging, and the official uHGF-AR(1) demo). Equations are those of the frozen MATLAB toolbox; this article does not introduce a new generative model.

The public fitting interface accepts perceptual and observation configurations, a default transformed start, and a Quasi-Newton optimizer with a frozen iteration budget in the paper protocols. Simulation exports inputs `u` and responses `y` that become immutable paired inputs when MATLAB is used as an oracle.

### 2.3 Frozen reference and evidence classes

HGFX v1.0 is validated against HGF Toolbox 8.2.0 at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`. The compatibility target includes the documented model/configuration inventory, parameter transforms and priors, HGF/eHGF/uHGF and specialized implementations, observation models, fitting and simulation surfaces, Hessian/covariance/correlation/statistical outputs, model selection, official workflow behavior, and public APIs.

We use four interpretation classes (Figure 1):

- **Direct parity:** MATLAB and HGFX agree under the frozen protocol and tolerance.
- **Matched reference limitation:** the MATLAB oracle exhibits the same limitation and HGFX reproduces the corresponding behavior; this is not a scientific success claim.
- **Preserved failure:** an experiment failed its scientific criterion and remains archived.
- **Not directly comparable (NDC):** a quantity lacks a defensible common semantic or numerical surface, most relevant to the pyhgf comparison.

Acceptance thresholds, seeds, datasets, starts, model families, optimizers, and grids are not changed after observing results. Failed experiments remain archived. The numerical policy and the two most sensitive optimizer/basin cases are documented in Supplementary Appendices S1-S2.

### 2.4 Validation hierarchy

The evidence hierarchy is: frozen reference identity; machine-readable validation artifacts; paired MATLAB/HGFX raw outputs; continuous-integration provenance; and manuscript tables/figures generated from those artifacts. Numerical checks use IEEE-754 binary64. The project does not target arbitrary-precision solutions that differ from frozen MATLAB execution.

Two official MATLAB demo workflows (320 binary trials) are release-gated. Complete release-relevant trajectories and inference states are compared at `rtol = 5e-11` and `atol = 5e-13`.

Fitting validation covers objectives at fixed parameters, MATLAB-compatible optimizer behavior, fitted parameters where direct parity is expected, trajectories, predictions/residuals, Hessian-derived covariance/correlation, and AIC/BIC/LME.

An earlier frozen parameter-recovery experiment failed its scientific acceptance criteria and remains preserved. Subsequent paired validation distinguishes parameter recovery from model selection on a frozen three-model grid (three binary perceptual models; truth scales 0.15 and 0.35; Quasi-Newton; predeclared thresholds: convergence rate >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00, model-recovery balanced accuracy >= 0.50).

CPU/backend equivalence was remeasured after remediation of the host-runtime numerical path, without changing the frozen criterion. Physical NVIDIA GPU applicability is retained from the recorded pre-release T4 run because the JAX GPU fitting path and its S9 runner are unchanged across the release; this retained GPU evidence is treated as applicability/correctness evidence only, not as a post-remediation performance measurement.

### 2.5 pyhgf common-scope protocol

`pyhgf==0.3.2` was pinned before execution. Direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. The authorized cell is a fixed-parameter, fully observed, three-level binary HGF (128 trials; standard/mean-field updates; unit coupling; zero drift; inverse temperature `ze = 48`). Trajectory quantities used `atol = 1e-10` and `rtol = 1e-8`; total response NLL used `atol = 1e-7` and `rtol = 1e-8`. Raw arrays were hashed before interpretation. A derived response-NLL boundary nonfinite was prospectively classified as NDC rather than triggering post-result clipping.

### 2.6 Prospective trial-horizon protocol

A prospectively frozen paired MATLAB/HGFX trial-horizon experiment examined 128, 256, 512 and 1024 trials using the same three perceptual models, truth scales, seeds, Quasi-Newton budget, and predeclared recovery thresholds. The preregistered scientific comparison was 256 versus 1024 after a paired-integrity gate; 128 and 512 were trajectory diagnostics. Failed simulations and fits were retained rather than resampled. The experiment completed on GitHub Actions (run `35272347167`; 24/24 shards). The paired-integrity gate did not pass: 10 of 72 model-recovery BIC winners disagreed, all for the classic binary HGF at 512 or 1024 trials, and parameter metrics for those horizons were undefined because invalid simulations were retained. The frozen per-model diagnostic classifier labels the affected model rows `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`; this cause label concerns paired implementation/optimization disagreement and does not supersede the aggregate scientific classification `INSUFFICIENT_REFERENCE_EVIDENCE`. The evidence was therefore judged insufficient to support a data-horizon or structural-identifiability conclusion.

## 3 Software validation results

### 3.1 Workflow equivalence

HGFX 1.0.0 was released from commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Official demo reproductions execute the MATLAB oracle, execute the Python reproduction, compare complete release-relevant outputs, and archive machine-readable artifacts (Table 2).

The first demo is a regime in which classic binary HGF encounters negative posterior precision while eHGF succeeds. HGFX reproduces this: `hgf_binary` fails in both implementations, `ehgf_binary` succeeds in both, and eHGF trajectories agree within the frozen tolerance (direct model-selection parity).

The second demo reproduces the uHGF to uHGF-AR(1) transition, including the recorded third-level trajectory behavior in both implementations (direct uHGF-AR(1) workflow parity).

**Table 2.** Official workflow and analysis-surface coverage. Exact machine-readable rows are in `paper/tables/`.

| Surface | Classification |
|---|---|
| Core model/API compatibility (documented scopes) | PASS |
| uHGF to AR(1) official workflow | PASS |
| sampleModel / prior-predictive workflow | PASS |
| Correlation/residual analysis surfaces | PASS |
| Bayesian parameter averaging | PASS |

### 3.2 Fitting statistics and scoped limitations

Two fitting-validation cases expose reference limitations rather than direct fitting parity (Table 3). In an official fitting stress case, MATLAB and HGFX can terminate at different optimizer endpoints in a numerically sensitive basin. In a separate frozen Level-2 holdout case, inference-equivalence fails for a specific seed. In both cases the frozen MATLAB oracle shows the corresponding instability or sensitivity, so these results are reported as matched reference limitations rather than as successful parameter recovery.

**Table 3.** Fitting and recovery classifications. Direct failures are retained.

| Surface | Direct result | Paper disposition |
|---|---|---|
| Earlier frozen parameter-recovery experiment | scientific criterion not met | preserved failure |
| Official fitting stress case | optimizer endpoint mismatch in sensitive basin | matched reference limitation |
| Frozen Level-2 holdout fit | inference-equivalence failure for a fixed seed | matched reference limitation |
| Paired parameter recovery | recovery criteria not fully met | matched reference limitation |
| Paired model selection | 36/36 BIC winners match | direct agreement |

### 3.3 Parameter recovery versus model selection

The earlier historical M18 parameter-recovery failure remains preserved separately. Figure 2 and Table 4 report the subsequent paired S7 recovery grid, whose recovery criteria are also not fully met. Paired S7 model selection is stronger: 36/36 BIC winners match (Figure 3). Model-selection agreement is not used to imply strong parameter identifiability. Full grid dimensions, frozen thresholds, and the prospective trial-horizon extension are reported in Supplementary Appendix S3.

The trial-horizon study (section 2.6) is complete as an executed protocol, not as a positive identifiability result. Because its paired-integrity gate failed, the available evidence is insufficient for a stronger recovery or identifiability conclusion. Diagnostic per-horizon numbers are archived with the paper materials and shown in Figure 6; they do not replace the earlier recovery evidence.

**Table 4.** Paired parameter recovery on the frozen three-model grid (both truth scales). Thresholds: convergence >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00. Full precision: `paper/tables/recovery_model_selection.md`.

| Model | MATLAB / HGFX convergence | MATLAB / HGFX median r | MATLAB / HGFX median sRMSE | Failed criteria |
|---|---|---|---|---|
| hgf_binary | 0.833 / 0.833 | 0.203 / 0.203 | 2.610 / 2.610 | correlation, sRMSE |
| ehgf_binary | 0.917 / 0.917 | 0.462 / 0.462 | 2.359 / 2.359 | correlation, sRMSE |
| uhgf_binary | 0.792 / 0.792 | 0.381 / 0.381 | 2.958 / 2.958 | convergence, correlation, sRMSE |

### 3.4 Backend and physical-GPU applicability

Compatibility CPU and JAX-backed CPU outputs agree under the frozen backend-equivalence criterion; the post-fix CPU value is remeasured from the released numerical path and is reported with Figure 4 provenance. Physical-GPU applicability is retained from source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`: the hosted environment exposed two Tesla T4 devices (Python 3.12.13, JAX/JAXLIB 0.11.1), while the four required fitting cells executed on `cuda:0`. Residency was checked by JAX device placement, with `nvidia-smi -L` used only to enumerate the visible hardware. All four CPU-versus-GPU cells pass the frozen final-objective criterion <= 1e-7; the maximum gap is 1.4210854715202004e-14 (Figure 4; Table 5). The retained GPU result is applicability/correctness evidence, not a speed or scaling result. Exact hardware/runtime provenance, the retention basis, objective pairs, execution command, and raw-artifact checksum are reported in Supplementary Appendix S5.

**Table 5.** Backend and GPU applicability.

| Surface | Classification | Result |
|---|---|---|
| Compatibility vs JAX CPU | direct backend agreement | objective/backend agreement |
| Physical NVIDIA GPU (Tesla T4; 2 visible, tested device `cuda:0`) | retained physical-GPU applicability evidence | max abs objective gap = 1.42e-14; criterion 1e-7 |

### 3.5 Common-scope comparison with pyhgf

In the authorized 128-trial cell, all 11 mapped perceptual/inference quantities passed predeclared tolerances (Figure 5). Maximum absolute differences were at binary64 rounding scale (1.11e-16 to 1.55e-15). Observed-input integrity was exact.

Participant-response NLL was not directly comparable. With `ze = 48`, the pyhgf-side power-ratio transformation reached an exact probability boundary on 13 trials and unclipped surprise became +Inf; the HGFX log-domain `unitsq_sgm` evaluation remained finite (total NLL 1808.855415351429). No clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. Overall interpretation: mapped perceptual quantities agree in the authorized cell, while participant-response NLL remains not directly comparable. The semantic gate, exact comparator identity, and numerical-boundary details are given in Supplementary Appendix S4.

### 3.6 Examples of use and current limitations

The package can be used by supplying trialwise responses and inputs to `hgfx.fit_model(y, u)`, inspecting `result.optim.BIC` and the returned parameter and trajectory structures. This example is a software-entry point and is not a new empirical validation case.

Typical use after `pip install hgfx==1.0.0` is MATLAB-style fitting and simulation from Python. The official cross-language demo reproductions are repository workflows that additionally require a source checkout and the frozen MATLAB-reference submodule; they are not bundled as ordinary wheel examples. MATLAB is unnecessary for normal package use.

Current limitations: (i) compatibility is scoped to HGF Toolbox 8.2.0, not future upstream versions; (ii) two numerically sensitive fitting cases are matched reference limitations rather than scientific recovery successes; (iii) parameter identifiability is weaker than paired model selection, and the trial-horizon experiment failed its paired-integrity gate, so it does not support a stronger recovery claim; (iv) GPU evidence is T4 applicability, not throughput; and (v) the pyhgf result is one mapped cell, not package-wide equivalence.

## 4 Discussion

Reproducing a scientific toolbox requires a broader notion of compatibility than implementing published equations. In numerically sensitive fitting problems, binary64-scale elementary differences can be amplified through finite-difference derivatives and quasi-Newton optimization, producing different endpoints even when shared-state objectives are extremely close.

This motivates separating scientific correctness from reference faithfulness. When the MATLAB oracle is itself unstable in a tested scope, forcing Python toward a preferred endpoint can be less faithful than preserving the oracle's limitation. A matched limitation is not evidence that the recovered parameter is identifiable. HGFX therefore preserves original failures and reports the narrow product-compatibility interpretation separately.

Workflow-level validation matters for the same reason. Reproducing the expected failure of classic HGF in a documented regime, while reproducing successful eHGF behavior, is part of compatibility. Treating every failure as an implementation bug would have encouraged divergence from the reference.

pyhgf and HGFX overlap but have different design centers. pyhgf emphasizes generalized network construction and differentiability (Legrand et al., 2026). HGFX v1.0 emphasizes frozen-MATLAB compatibility and provenance. Quantity-specific claims are more informative than ranking the packages. Mapped belief trajectories agree to rounding scale in the authorized cell; the response-NLL surface exposes a numerical-boundary difference even though the mapped belief values agree to binary64 rounding scale.

JAX enables compiled CPU/GPU execution, batching, and multi-device workloads (Bradbury et al., 2018; Frostig et al., 2018). Accelerator-native code is scientifically useful only if the accelerated path preserves relevant outputs. The T4 result supports that claim for the tested objective. Throughput depends on workload size, compilation amortization, hardware, device count, and contention; protocol 1 therefore does not activate a headline performance or scaling result. Scalability of the JAX path is an engineering capability of the implementation, not a reported empirical law.

The strongest contribution is methodological: an explicit oracle, evidence classes, numerical compatibility policy, preserved failures, and release provenance. That discipline reduces the risk that a modern implementation gains convenience by silently changing an established scientific contract.

## 5 Software availability and reproducibility

HGFX 1.0.0 is MIT-licensed (HGFX developers, 2026). Source, tag, and package URLs are in Table 1. Paper tables regenerate with `python paper/scripts/generate_p2_tables.py`. Figures regenerate with `python paper/scripts/generate_p5_figures.py` (300 dpi PNG and PDF). The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence. Repository-facing case identifiers and claim-to-evidence traceability are intentionally confined to Supplementary Appendix S6.

## Statements and Declarations

### Competing interests

The author is the developer and maintainer of HGFX and declares no other competing financial interests or personal relationships that could have appeared to influence the work.

### Author contributions

Mohammad Ahmadkhanloo: Conceptualization, Software, Validation, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.

### Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## Information Sharing Statement

HGFX source code, the MIT license, the pinned v1.0.0 release, installation instructions, documentation, and paper-generation scripts are publicly accessible at https://github.com/ahmadkhanloo/hgfx and https://pypi.org/project/hgfx/1.0.0/. Machine-readable validation evidence, frozen model/configuration protocols, reproducibility instructions, negative and non-comparable outcomes, and corresponding generated tables and figures are recorded in the repository under `docs/validation/` and `paper/`. MATLAB is required only when regenerating cross-language oracle evidence; it is not needed to run the released software. Access restrictions for the upstream MATLAB reference, where applicable, are governed by its own license.

## Acknowledgments

The frozen MATLAB HGF Toolbox 8.2.0 of Mathys and colleagues is the reference oracle for this work. GitHub Actions and MATLAB were used only to regenerate paired oracle evidence. No additional acknowledgments are recorded at draft time.

## Figure captions

**Figure 1.** Evidence classes used in this article: direct MATLAB parity, matched reference limitation, not-directly-comparable pyhgf quantities, and preserved historical failure. File: `paper/figures/fig_evidence_classes.png` (PDF: `.pdf`).

**Figure 2.** Paired parameter-recovery metrics for MATLAB 8.2.0 and HGFX 1.0.0 against the predeclared recovery thresholds. This panel does not constitute a scientific recovery success. File: `paper/figures/fig_recovery_metrics.png`.

**Figure 3.** Paired model-selection summary: MATLAB and HGFX balanced accuracy and 36/36 BIC winner agreement. File: `paper/figures/fig_model_selection.png`.

**Figure 4.** Backend agreement relative to each comparison's frozen criterion. The post-fix compatibility-versus-JAX-CPU remeasurement has a maximum final-objective gap of 0.006783711260709424 against a 0.10 criterion; JAX-CPU-versus-retained-physical-T4 has a maximum gap of 1.4210854715202004e-14 against a 1e-7 criterion. Bars show gap/criterion ratios, so the dashed line at 1.0 is the acceptance boundary for both comparisons. Not a speed claim. File: `paper/figures/fig_gpu_applicability.png`.

**Figure 5.** Frozen HGFX versus pyhgf 0.3.2 common-scope trajectories (predicted probability and level-2 posterior mean) for the authorized 128-trial binary HGF. Eleven mapped perceptual quantities pass; response NLL remains NDC. File: `paper/figures/fig_pyhgf_common_scope.png`.

**Figure 6.** Trial-horizon diagnostic parameter-recovery metrics at 128, 256, 512 and 1024 trials, generated directly from the hash-verified aggregate. Dotted lines are the predeclared thresholds. Incomplete classic-HGF cases at 512/1024 trials are retained as gaps. Individual diagnostic criteria do not establish identifiability; the paired-integrity gate failed, so the evidence remains insufficient for an identifiability conclusion. File: `paper/figures/fig_p3_horizon_diagnostics.png`.

## Use of AI-assisted technologies

During the preparation of this work, the author used OpenAI ChatGPT to assist with code drafting and review, repository/document consistency checks, manuscript organization, and language refinement. The author reviewed and edited the resulting material as needed, and all reported scientific results remained subject to the repository's frozen validation, evidence, and reproducibility gates. The author takes full responsibility for the content of the publication.



## References

- Bradbury, J., et al. (2018). JAX: composable transformations of Python+NumPy programs. https://github.com/jax-ml/jax
- Daunizeau, J., Adam, V., & Rigoux, L. (2014). VBA: A probabilistic treatment of nonlinear models for neurobiological and behavioural data. PLOS Computational Biology, 10(1), e1003441. https://doi.org/10.1371/journal.pcbi.1003441
- Diaconescu, A. O., et al. (2014). Inferring on the intentions of others by hierarchical Bayesian learning. PLOS Computational Biology, 10(9), e1003810. https://doi.org/10.1371/journal.pcbi.1003810
- Frässle, S., et al. (2021). TAPAS: An open-source software package for translational neuromodeling and computational psychiatry. Frontiers in Psychiatry, 12, 680811. https://doi.org/10.3389/fpsyt.2021.680811
- Frostig, R., Johnson, M. J., & Leary, C. (2018). Compiling machine learning programs via high-level tracing. Proceedings of SysML.
- HGFX developers. (2026). HGFX: A GPU-native Python toolbox for Hierarchical Gaussian Filters (Version 1.0.0) [Computer software]. https://github.com/ahmadkhanloo/hgfx (release source: 4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27)
- Iglesias, S., et al. (2013). Hierarchical prediction errors in midbrain and basal forebrain during sensory learning. Neuron, 80(2), 519–530. https://doi.org/10.1016/j.neuron.2013.09.009
- Legrand, N., et al. (2026). pyhgf: A neural network library for predictive coding. PLOS Computational Biology, 22(6), e1014340. https://doi.org/10.1371/journal.pcbi.1014340
- Mathys, C., Daunizeau, J., Friston, K. J., & Stephan, K. E. (2011). A Bayesian foundation for individual learning under uncertainty. Frontiers in Human Neuroscience, 5, 39. https://doi.org/10.3389/fnhum.2011.00039
- Mathys, C. D., et al. (2014). Uncertainty in perception and the Hierarchical Gaussian Filter. Frontiers in Human Neuroscience, 8, 825. https://doi.org/10.3389/fnhum.2014.00825
- Peng, R. D. (2011). Reproducible research in computational science. Science, 334(6060), 1226–1227. https://doi.org/10.1126/science.1213847
- Wilson, R. C., & Collins, A. G. E. (2019). Ten simple rules for the computational modeling of behavioral data. eLife, 8, e49547. https://doi.org/10.7554/eLife.49547
