# Reproducible Hierarchical Gaussian Filter workflows in Python/JAX: scoped validation against the MATLAB toolbox

**Article type:** Original Research

**Blinded review draft:** Author-identifying title page supplied as a separate document; the public software repository itself may reveal identity and journal confirmation is required.

**Keywords:** Hierarchical Gaussian Filter; Bayesian learning; computational neuroscience; software validation; reproducibility; Python

## Abstract

**Background:** The Hierarchical Gaussian Filter (HGF) is used to model learning under uncertainty and volatility. Reproducibility across software environments requires preservation of numerical as well as model-level behavior. **Objective:** To evaluate whether a Python/JAX implementation can reproduce documented scientific workflows of the frozen MATLAB HGF Toolbox 8.2.0 without requiring MATLAB for routine use. **Methods:** HGFX 1.0.0 was compared with a pinned MATLAB oracle using predeclared tolerances for trajectories, simulation, fitting, model-selection, and backend results. The validation record explicitly distinguishes direct agreement, matched reference limitations, preserved failures, and non-comparable quantities. **Results:** Two reference demonstration workflows were reproduced. In one paired grid, 36 of 36 Bayesian information criterion winners agreed. Parameter-recovery criteria were not fully met, while a subsequent trial-horizon study failed its paired-integrity gate (10 of 72 model-selection disagreements). Four GPU fitting cells executed on a physical Tesla T4 with a maximum CPU–GPU final-objective difference of 1.42 × 10⁻¹⁴ against a 10⁻⁷ criterion. A scoped comparison with pyhgf 0.3.2 showed agreement for 11 mapped inference quantities, but response likelihood was not directly comparable. **Conclusion:** HGFX supports reference-faithful computational neuroscience workflows in explicitly validated scopes. It does not establish improved parameter identifiability, general GPU speedups, or universal interchangeability between HGF packages.

## 1 Introduction

The Hierarchical Gaussian Filter (HGF) is a Bayesian framework for learning under uncertainty and volatility (Mathys et al., 2011; Mathys et al., 2014). Its established MATLAB implementation is part of TAPAS and supports computational-neuroscience and computational-psychiatry studies, including investigations of prediction errors and social inference (Frässle et al., 2021; Iglesias et al., 2013; Diaconescu et al., 2014). Reproducing an HGF analysis across programming environments requires more than translating equations: parameter conventions, optimization, observation likelihoods, numerical precision, and failure behavior affect fitted quantities and model decisions.

Modern Python approaches already exist. In particular, pyhgf emphasizes configurable predictive-coding networks and differentiable inference (Legrand et al., 2026). HGFX addresses a different objective: documented compatibility with the frozen MATLAB HGF Toolbox 8.2.0 and removal of MATLAB as a user-runtime dependency, without claiming superiority or priority as a Python HGF implementation.

We investigate the reproducibility of established HGF workflows across MATLAB and Python/JAX, using frozen protocols and traceable evidence. The work reports numerical and workflow agreement alongside limitations in fitting and parameter recovery; it does not introduce a new neuroimaging, behavioral, or clinical dataset.

## 2 Materials and methods

### 2.1 Software description and research context

HGFX is designed to reproduce established Bayesian-learning analyses relevant to computational neuroscience and computational psychiatry, including model fitting, simulation, and selection. This study evaluates numerical reproducibility rather than a new clinical cohort, neuroimaging dataset, or brain mechanism.

### 2.1.1 Implementation

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

HGFX was evaluated against the fixed MATLAB HGF Toolbox 8.2.0 reference at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`. The validation scope includes documented HGF/eHGF/uHGF configurations, parameter transforms, observation models, trajectories, fitting and simulation, summary statistics, and official demonstrations. Four evidence classes prevent overinterpretation (Figure 1): **direct parity** at predeclared tolerances; **matched reference limitation**, reproducing an oracle limitation without calling it scientific success; **preserved failure**, retaining unsuccessful experiments; and **not directly comparable**, applied where quantities lack matching semantics.

### 2.4 Validation hierarchy

Evidence proceeds from frozen reference identity to machine-readable MATLAB/HGFX outputs, CI provenance, and regenerated tables/figures. Numerical checks use binary64. Two official 320-trial demonstrations compare relevant trajectories at `rtol = 5e-11` and `atol = 5e-13`. Fitting checks include objectives, optimization, parameter estimates, predictions, and AIC/BIC/LME.

The earlier unsuccessful recovery study was preserved. A later three-model paired grid used truth scales 0.15 and 0.35 with predefined criteria (convergence >= 0.80; median correlation >= 0.50; median standardized RMSE <= 1.00; balanced model-recovery accuracy >= 0.50). Post-remediation CPU equivalence was remeasured; earlier physical Tesla T4 results were retained only as evidence of the unchanged GPU fitting path's applicability, not performance.

### 2.5 pyhgf common-scope protocol

`pyhgf==0.3.2` was pinned before execution. Direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. The authorized cell is a fixed-parameter, fully observed, three-level binary HGF (128 trials; standard/mean-field updates; unit coupling; zero drift; inverse temperature `ze = 48`). Trajectory quantities used `atol = 1e-10` and `rtol = 1e-8`; total response NLL used `atol = 1e-7` and `rtol = 1e-8`. Raw arrays were hashed before interpretation. A derived response-NLL boundary nonfinite was prospectively classified as NDC rather than triggering post-result clipping.

### 2.6 Prospective trial-horizon protocol

A frozen paired MATLAB/HGFX study examined 128, 256, 512, and 1024 trials using unchanged models, seeds, truth scales, and recovery criteria. All failed simulations/fits were retained. Execution completed in 24/24 shards (GitHub Actions `35272347167`), but the paired-integrity gate failed: 10/72 BIC winners disagreed, all in classic HGF at 512/1024 trials, where parameter metrics were undefined for invalid simulations. Per-model diagnostics identify possible implementation/optimizer mismatch; aggregate classification is `INSUFFICIENT_REFERENCE_EVIDENCE`, not proof of an identifiability mechanism.

## 3 Results

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

After `pip install hgfx==1.0.0`, fitting and simulation require no MATLAB runtime; reference-regeneration demos need the frozen MATLAB submodule and checkout. Validation is limited to HGF Toolbox 8.2.0 and tested configurations. Sensitive fitting cases and incomplete parameter recovery cannot support strong identifiability claims; longer-horizon paired integrity failed. The retained GPU test establishes objective agreement, not speed, and the pyhgf comparison covers only one mapped configuration.

## 4 Discussion

Cross-language reproduction of computational models requires preserving the practical scientific workflow, not simply implementing the equations. Numerically small differences may be amplified by finite-difference derivatives and non-convex quasi-Newton optimization, producing divergent endpoints. HGFX distinguishes reference faithfulness from scientific parameter identifiability: two sensitive fitting cases reproduce reference limitations, while parameter-recovery criteria remain unmet. Agreement among 36 paired model-selection winners does not negate these constraints.

The MATLAB-independent workflow may support the reanalysis of HGF studies within the documented validation scope. The comparison with pyhgf is complementary rather than competitive: 11 mapped perceptual quantities agree in one fixed case, while participant-response NLL remains non-comparable at the tested numerical boundary. The physical T4 result establishes objective agreement in four tested fitting cells; no general GPU speed or scaling conclusion follows.

The longer trial-horizon experiment did not pass paired integrity and cannot isolate an identifiability mechanism. The paper therefore supports a scoped computational reproducibility claim, not a new clinical or neuroscience effect. Future work should distinguish implementation and optimizer sources of mismatch prospectively before revisiting parameter-recovery conclusions.

## 5 Conclusions

Cross-language reproduction of established HGF workflows is achievable within the directly validated settings of this study. Agreement in model selection and selected trajectories coexists with preserved recovery failures and optimizer sensitivity; the results do not demonstrate parameter identifiability. GPU evidence is an applicability test rather than a performance benchmark, and comparisons with pyhgf remain restricted to semantically mapped quantities.

## 6 Data and code availability

HGFX 1.0.0 is MIT-licensed (HGFX developers, 2026). Source, tag, and package URLs are in Table 1. Paper tables regenerate with `python paper/scripts/generate_p2_tables.py`. Figures regenerate with `python paper/scripts/generate_p5_figures.py` (300 dpi PNG and PDF). The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence. Repository-facing case identifiers and claim-to-evidence traceability are intentionally confined to Supplementary Appendix S6.

## Declaration of competing interest

The author is the developer and maintainer of HGFX and declares no other competing financial interests or personal relationships that could have appeared to influence the work.

## CRediT authorship contribution statement

The author: Conceptualization, Software, Validation, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.

## Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## Acknowledgments

The frozen MATLAB HGF Toolbox 8.2.0 of Mathys and colleagues is the reference oracle for this work. GitHub Actions and MATLAB were used only to regenerate paired oracle evidence. No additional acknowledgments are recorded at draft time.

## Figure captions

**Figure 1.** Evidence classes used in this article: direct MATLAB parity, matched reference limitation, not-directly-comparable pyhgf quantities, and preserved historical failure. File: `paper/figures/fig_evidence_classes.png` (PDF: `.pdf`).

**Figure 2.** Paired parameter-recovery metrics for MATLAB 8.2.0 and HGFX 1.0.0 against the predeclared recovery thresholds. This panel does not constitute a scientific recovery success. File: `paper/figures/fig_recovery_metrics.png`.

**Figure 3.** Paired model-selection summary: MATLAB and HGFX balanced accuracy and 36/36 BIC winner agreement. File: `paper/figures/fig_model_selection.png`.

**Figure 4.** Backend agreement relative to each comparison's frozen criterion. The post-fix compatibility-versus-JAX-CPU remeasurement has a maximum final-objective gap of 0.006783711260709424 against a 0.10 criterion; JAX-CPU-versus-retained-physical-T4 has a maximum gap of 1.4210854715202004e-14 against a 1e-7 criterion. Bars show gap/criterion ratios, so the dashed line at 1.0 is the acceptance boundary for both comparisons. Not a speed claim. File: `paper/figures/fig_gpu_applicability.png`.

**Figure 5.** Frozen HGFX versus pyhgf 0.3.2 common-scope trajectories (predicted probability and level-2 posterior mean) for the authorized 128-trial binary HGF. Eleven mapped perceptual quantities pass; response NLL remains NDC. File: `paper/figures/fig_pyhgf_common_scope.png`.

**Figure 6.** Trial-horizon diagnostic parameter-recovery metrics at 128, 256, 512 and 1024 trials, generated directly from the hash-verified aggregate. Dotted lines are the predeclared thresholds. Incomplete classic-HGF cases at 512/1024 trials are retained as gaps. Individual diagnostic criteria do not establish identifiability; the paired-integrity gate failed, so the evidence remains insufficient for an identifiability conclusion. File: `paper/figures/fig_p3_horizon_diagnostics.png`.

## Declaration of generative AI and AI-assisted technologies

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
