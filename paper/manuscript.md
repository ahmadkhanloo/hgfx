# HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox

**Target journal:** *Journal of Neuroscience Methods* (Elsevier; hybrid; **subscription track, no APC**)  
**Article type:** Research Article (methods)  
**Highlights:** `paper/highlights.txt`  
**Word count (main text, approximate):** 2,400  
**Figures:** 6  **Tables:** 6  
**Abstract:** <=250 words (this draft ~230)

**Authors and affiliations**

Mohammad Ahmadkhanloo  
Institute for Research in Fundamental Sciences (IPM), Tehran, Iran  
https://github.com/ahmadkhanloo

**Correspondence:** Mohammad Ahmadkhanloo, Institute for Research in Fundamental Sciences (IPM), Niavaran Square, Tehran, Iran. Email: m.ahmadkhanloo@ipm.ir. Software: https://github.com/ahmadkhanloo/hgfx.

**Keywords:** Hierarchical Gaussian Filter; computational neuroscience; Bayesian learning; Python; reproducibility; model validation

## Abstract

The Hierarchical Gaussian Filter (HGF) is a hierarchical Bayesian model of learning under uncertainty and volatility, with a widely used MATLAB implementation. We present HGFX 1.0.0, a Python/JAX toolbox whose primary objective is functional and scientific equivalence with a frozen HGF Toolbox 8.2.0 reference, while removing MATLAB as a user-runtime dependency. Reimplementation is treated as a validation problem rather than source translation: configuration semantics, parameter transforms, forward trajectories, observation likelihoods, objectives, fitting and statistical surfaces, simulation workflows, official demo behavior, model selection, and backend agreement are compared against the pinned oracle under predeclared tolerances. Two official MATLAB demo workflows reproduce the reference at frozen trajectory tolerances, including a model-family failure regime in which classic HGF fails and eHGF succeeds. In paired model-selection validation, all 36 BIC winners agree between MATLAB and HGFX. Physical NVIDIA GPU applicability was confirmed on two Tesla T4 devices, with a maximum CPU-versus-GPU final-objective difference of 1.42e-14 against a frozen 1e-7 criterion. Historical parameter-recovery failures and exact MATLAB/HGFX limitation matches are preserved and are not reclassified as scientific success. A prospectively gated comparison with pyhgf 0.3.2 shows binary64-scale agreement on mapped perceptual trajectories in one authorized three-level binary-HGF cell, while participant-response negative log-likelihood is retained as not directly comparable. HGFX therefore provides a MATLAB-independent Python implementation with an explicit evidence model that separates direct parity, matched reference limitations, backend applicability, and future performance claims.

## 1 Introduction

Computational models of learning under uncertainty must represent uncertainty about latent states and about the volatility of those states. The Hierarchical Gaussian Filter (HGF) was introduced as a generic hierarchical Bayesian framework for individual learning under uncertainty [@mathys2011] and later developed into a practical filtering framework for perception and learning [@mathys2014]. It has been used to recover hierarchical prediction errors in neuroimaging [@iglesias2013] and to model inference about others' intentions [@diaconescu2014]. The associated MATLAB toolbox is distributed as part of TAPAS, an open-source collection of translational neuromodeling tools [@fraessle2021tapas], and remains a reference implementation for fitting, simulation, model comparison, and analysis.

Reproducing such a toolbox in another language is not equivalent to translating published equations. Scientific behavior also depends on parameter ordering, transforms, prior conventions, fixed and free parameter semantics, placeholder values, numerical primitives, finite-difference behavior, optimizer trajectories, failure modes, and model-family selection. Small floating-point differences that are negligible at a shared state can be amplified by derivative estimation and non-convex optimization [@wilson2019ten; @peng2011reproducible]. A replacement implementation can therefore appear mathematically correct while producing materially different fitted inferences or model-selection outcomes.

Python/JAX toolboxes already exist in this space. pyhgf represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference [@legrand2026pyhgf]. HGFX does not claim to be the first Python or JAX HGF. Its v1.0 objective is narrower and complementary: behavioral compatibility with one frozen MATLAB HGF Toolbox 8.2.0 oracle, explicit cross-language evidence, and removal of MATLAB from the user runtime.

This paper asks whether a legacy scientific toolbox can be reproduced in an accelerator-compatible stack without silently changing the scientific contract. We report the released HGFX 1.0.0 evidence: workflow reproduction, paired model-selection agreement, CPU/backend and physical-GPU applicability, a scoped pyhgf comparison, and preserved historical failures. General speedup and multi-GPU scaling are not headline claims.

For neuroscience methodology, the contribution is a reproducible route for re-running established HGF analyses outside the MATLAB runtime while retaining the validated reference behavior that underpins prior computational-neuroscience and computational-psychiatry applications. The study therefore evaluates software behavior, inferential workflows, and reproducibility rather than introducing a new behavioral or neuroimaging dataset.

## 2 Materials and methods

### 2.1 Software description

HGFX is a Python package (Python >= 3.11) built on NumPy and JAX [@jax2018github; @frostig2018]. The public surface exposes Python-first and MATLAB-style aliases (`fit_model`/`fitModel`, `sim_model`/`simModel`, `sample_model`/`sampleModel`). Compatibility-sensitive numerical paths are distinguished from JAX-backed execution. Compatibility repairs were introduced only when supported by an exact MATLAB oracle case and a failing regression.

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
| Operating systems | Platform-independent (Linux, Windows, macOS) |
| Language | Python 3.11+ |
| License | MIT (no restriction on non-academic use) |
| Dependencies | NumPy, JAX |
| Frozen MATLAB oracle | HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3` |
| Frozen HGFX source | `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |
| Paper protocol | `hgfx-paper-protocol-1` |

Users do not require MATLAB. MATLAB is used only when regenerating cross-language oracle evidence. The HGF Toolbox is cited via Mathys et al. [@mathys2011; @mathys2014] and TAPAS [@fraessle2021tapas]. Related probabilistic-modelling software includes the VBA toolbox [@daunizeau2014vba].

### 2.2 Covered HGF families

The HGF represents a hidden hierarchy of Gaussian states in which higher levels encode volatility of lower levels [@mathys2011; @mathys2014]. For binary observations, a unit-square sigmoid observation model maps the first hidden state to the probability of the observed outcome. HGFX v1.0 covers the classic HGF, the enhanced HGF (eHGF), and the unbounded HGF (uHGF) in the documented MATLAB-compatible configurations, plus specialized surfaces in the v1 migration matrix (sampling, analysis, Bayesian parameter averaging, and the official uHGF-AR(1) demo). Equations are those of the frozen MATLAB toolbox; this article does not introduce a new generative model.

The public fitting interface accepts perceptual and observation configurations, a default transformed start, and a Quasi-Newton optimizer with a frozen iteration budget in the paper protocols. Simulation exports inputs `u` and responses `y` that become immutable paired inputs when MATLAB is used as an oracle.

### 2.3 Frozen reference and evidence classes

HGFX v1.0 is validated against HGF Toolbox 8.2.0 at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`. The compatibility target includes the documented model/configuration inventory, parameter transforms and priors, HGF/eHGF/uHGF and specialized implementations, observation models, fitting and simulation surfaces, Hessian/covariance/correlation/statistical outputs, model selection, official workflow behavior, and public APIs.

We use four interpretation classes (Figure 1):

- **PASS / direct parity:** MATLAB and HGFX agree under the frozen protocol and tolerance.
- **REFERENCE_LIMITATION_MATCH:** the MATLAB oracle exhibits the same limitation; HGFX reproduces that reference behavior. This is not a scientific success claim.
- **FAIL_PRESERVED:** an experiment failed its scientific criterion and remains archived.
- **NOT_DIRECTLY_COMPARABLE (NDC):** a quantity lacks a defensible common semantic or numerical surface, most relevant to the pyhgf comparison.

Acceptance thresholds, seeds, datasets, starts, model families, optimizers, and grids are not changed after observing results. Failed experiments remain archived.

### 2.4 Validation hierarchy

The evidence hierarchy is: frozen reference identity; machine-readable validation artifacts; paired MATLAB/HGFX raw outputs; continuous-integration provenance; and manuscript tables/figures generated from those artifacts. Numerical checks use IEEE-754 binary64. The project does not target arbitrary-precision solutions that differ from frozen MATLAB execution.

Two official MATLAB demo workflows (320 binary trials) are release-gated. Complete release-relevant trajectories and inference states are compared at `rtol = 5e-11` and `atol = 5e-13`.

Fitting validation covers objectives at fixed parameters, MATLAB-compatible optimizer behavior, fitted parameters where direct parity is expected, trajectories, predictions/residuals, Hessian-derived covariance/correlation, and AIC/BIC/LME.

The historical M18 scientific recovery experiment failed and is preserved. Subsequent paired product-level validation distinguishes parameter recovery from model selection on an exact S7 grid (three binary perceptual models; truth scales 0.15 and 0.35; Quasi-Newton; frozen M18 thresholds: convergence rate >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00, model-recovery balanced accuracy >= 0.50).

CPU/backend equivalence and physical NVIDIA GPU applicability were tested after an independent review of portability blockers (host C runtime `expm1`/`log` paths and Windows CRLF hash failures). Both blockers were remediated without changing scientific thresholds.

### 2.5 pyhgf common-scope protocol

`pyhgf==0.3.2` was pinned before execution. Direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. The authorized cell is a fixed-parameter, fully observed, three-level binary HGF (128 trials; standard/mean-field updates; unit coupling; zero drift; inverse temperature `ze = 48`). Trajectory quantities used `atol = 1e-10` and `rtol = 1e-8`; total response NLL used `atol = 1e-7` and `rtol = 1e-8`. Raw arrays were hashed before interpretation. A derived response-NLL boundary nonfinite was prospectively classified as NDC rather than triggering post-result clipping.

### 2.6 Prospective trial-horizon protocol

Paper protocol 1 includes a prospectively frozen paired MATLAB/HGFX experiment (`m18c2-trial-horizon-identifiability-1`) at 128, 256, 512 and 1024 trials, using the S7 models, truth scales, seeds, Quasi-Newton budget, and M18 thresholds. The preregistered scientific comparison is 256 versus 1024 after a paired-integrity gate; 128 and 512 are trajectory diagnostics. Failed simulations and fits are retained. Historical M18 is not rewritten. The experiment completed on GitHub Actions (run `35272347167`; 24/24 shards). The frozen paired-integrity gate did not pass: 10 of 72 model-recovery BIC winners disagreed, all in `hgf_binary` at 512 or 1024 trials, and `hgf_binary` parameter metrics at those horizons are undefined because invalid simulations were retained rather than resampled. The official class is `INSUFFICIENT_REFERENCE_EVIDENCE`. No data-horizon or structural-identifiability conclusion is promoted.

## 3 Results

### 3.1 Workflow equivalence

HGFX 1.0.0 was released from commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Official demo reproductions execute the MATLAB oracle, execute the Python reproduction, compare complete release-relevant outputs, and archive machine-readable artifacts (Table 2).

The first demo is a regime in which classic binary HGF encounters negative posterior precision while eHGF succeeds. HGFX reproduces this: `hgf_binary` fails in both implementations, `ehgf_binary` succeeds in both, and eHGF trajectories agree within the frozen tolerance (`PASS_MODEL_SELECTION_PARITY`).

The second demo reproduces the uHGF to uHGF-AR(1) transition. The maximum absolute third-level posterior mean is 16.99162398501939 for uHGF and 4.0927117005012175 for uHGF-AR(1) in both implementations (`PASS_UHGF_AR1_WORKFLOW_PARITY`).

**Table 2.** Official workflow and analysis-surface coverage. Exact machine-readable rows are in `paper/tables/`.

| Surface | Classification |
|---|---|
| Core model/API compatibility (documented scopes) | PASS |
| uHGF to AR(1) official workflow | PASS |
| sampleModel / prior-predictive workflow | PASS |
| Correlation/residual analysis surfaces | PASS |
| Bayesian parameter averaging | PASS |

### 3.2 Fitting statistics and scoped limitations

D02 and D08 remain exact-scope reference limitations (Table 3). The MATLAB oracle exhibits endpoint/basin sensitivity in those scopes; HGFX matches the limitation. The release claims MATLAB-equivalent behavior in accepted product accounting, not universal optimizer endpoint identity.

**Table 3.** Fitting and recovery classifications. Direct failures are retained.

| Surface | Direct result | Paper disposition |
|---|---|---|
| Historical M18 scientific experiment | FAIL_PRESERVED | preserved historical failure |
| D02 fitting | optimizer mismatch | REFERENCE_LIMITATION_MATCH |
| D08 fitting holdout | inference-equivalence fail | REFERENCE_LIMITATION_MATCH |
| S7 parameter recovery | scientific_pass = false | REFERENCE_LIMITATION_MATCH |
| S7 paired model selection | 36/36 BIC winners match | PASS_PAIRED_MODEL_SELECTION |

### 3.3 Parameter recovery versus model selection

Historical parameter-recovery failure remains part of the record (Figure 2; Table 4). Paired model selection is stronger: 36/36 BIC winners match (Figure 3). Model-selection agreement is not used to imply strong parameter identifiability.

The trial-horizon study (section 2.6) is complete as an executed protocol, not as a positive identifiability result. Official classification: `INSUFFICIENT_REFERENCE_EVIDENCE`. This manuscript therefore still does not claim generally strong parameter recovery for HGFX or for the MATLAB reference. Diagnostic per-horizon numbers are archived with the paper materials and shown in Figure 6; they must not overwrite Table 4 or historical M18.

**Table 4.** S7 paired parameter recovery (both truth scales). Thresholds: convergence >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00. Full precision: `paper/tables/recovery_model_selection.md`.

| Model | MATLAB / HGFX convergence | MATLAB / HGFX median r | MATLAB / HGFX median sRMSE | Failed criteria |
|---|---|---|---|---|
| hgf_binary | 0.833 / 0.833 | 0.203 / 0.203 | 2.610 / 2.610 | correlation, sRMSE |
| ehgf_binary | 0.917 / 0.917 | 0.462 / 0.462 | 2.359 / 2.359 | correlation, sRMSE |
| uhgf_binary | 0.792 / 0.792 | 0.381 / 0.381 | 2.958 / 2.958 | convergence, correlation, sRMSE |

### 3.4 Backend and physical-GPU applicability

Compatibility CPU and JAX-backed CPU outputs pass `PASS_CPU_BACKEND_EQUIVALENCE`. On two Tesla T4 GPUs (Python 3.12.13, JAX/JAXLIB 0.11.1, `nvidia-smi` process residency), all four required CPU-versus-GPU fitting cells pass the frozen final-objective criterion <= 1e-7. The maximum gap is 1.4210854715202004e-14 (Figure 4; Table 5). This is applicability/correctness evidence, not a speed or scaling result.

**Table 5.** Backend and GPU applicability.

| Surface | Classification | Result |
|---|---|---|
| Compatibility vs JAX CPU | PASS_CPU_BACKEND_EQUIVALENCE | objective/backend agreement |
| Physical NVIDIA GPU (2x Tesla T4) | PASS_PHYSICAL_GPU_APPLICABILITY | max abs objective gap = 1.42e-14; criterion 1e-7 |

### 3.5 Common-scope comparison with pyhgf

In the authorized 128-trial cell, all 11 mapped perceptual/inference quantities passed predeclared tolerances (Figure 5). Maximum absolute differences were at binary64 rounding scale (1.11e-16 to 1.55e-15). Observed-input integrity was exact.

Participant-response NLL was not directly comparable. With `ze = 48`, the pyhgf-side power-ratio transformation reached an exact probability boundary on 13 trials and unclipped surprise became +Inf; the HGFX log-domain `unitsq_sgm` evaluation remained finite (total NLL 1808.855415351429). No clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. Overall classification: `PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES`.

### 3.6 Examples of use and current limitations

Typical use after `pip install hgfx==1.0.0` is MATLAB-style fitting and simulation from Python, including the official demo reproductions. MATLAB is unnecessary for those user paths.

Current limitations: (i) compatibility is scoped to HGF Toolbox 8.2.0, not future upstream versions; (ii) D02/D08 are matched reference limitations, not scientific recovery success; (iii) parameter identifiability is weaker than paired model selection, and the trial-horizon experiment returned `INSUFFICIENT_REFERENCE_EVIDENCE` after a failed paired-integrity gate, so it does not support a stronger recovery claim; (iv) GPU evidence is T4 applicability, not throughput; (v) the pyhgf result is one mapped cell, not package-wide equivalence.

## 4 Discussion

Reproducing a scientific toolbox requires a broader notion of compatibility than implementing published equations. In numerically sensitive fitting problems, binary64-scale elementary differences can be amplified through finite-difference derivatives and quasi-Newton optimization, producing different endpoints even when shared-state objectives are extremely close.

This motivates separating scientific correctness from reference faithfulness. When the MATLAB oracle is itself unstable in a tested scope, forcing Python toward a preferred endpoint can be less faithful than preserving the oracle's limitation. A matched limitation is not evidence that the recovered parameter is identifiable. HGFX therefore preserves original failures and reports the narrow product-compatibility interpretation separately.

Workflow-level validation matters for the same reason. Reproducing the expected failure of classic HGF in a documented regime, while reproducing successful eHGF behavior, is part of compatibility. Treating every failure as an implementation bug would have encouraged divergence from the reference.

pyhgf and HGFX overlap but have different design centers. pyhgf emphasizes generalized network construction and differentiability [@legrand2026pyhgf]. HGFX v1.0 emphasizes frozen-MATLAB compatibility and provenance. Quantity-specific claims are more informative than ranking the packages. Mapped belief trajectories agree to rounding scale in the authorized cell; the response-NLL surface exposes a numerical-boundary difference despite sharing the same predicted belief.

JAX enables compiled CPU/GPU execution, batching, and multi-device workloads [@jax2018github; @frostig2018]. Accelerator-native code is scientifically useful only if the accelerated path preserves relevant outputs. The T4 result supports that claim for the tested objective. Throughput depends on workload size, compilation amortization, hardware, device count, and contention; protocol 1 therefore does not activate a headline performance or scaling result. Scalability of the JAX path is an engineering capability of the implementation, not a reported empirical law.

The strongest contribution is methodological: an explicit oracle, evidence classes, numerical compatibility policy, preserved failures, and release provenance. That discipline reduces the risk that a modern implementation gains convenience by silently changing an established scientific contract.

## 5 Data and code availability

HGFX 1.0.0 is MIT-licensed [@hgfx100]. Source, tag, and package URLs are in Table 1. Paper tables regenerate with `python paper/scripts/generate_p2_tables.py`. Figures regenerate with `python paper/scripts/generate_p5_figures.py` (300 dpi PNG and PDF). The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence.

## Declaration of competing interest

The author is the developer and maintainer of HGFX and declares no other competing financial interests or personal relationships that could have appeared to influence the work.

## CRediT authorship contribution statement

Mohammad Ahmadkhanloo: Conceptualization, Software, Validation, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.

## Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## Acknowledgments

The frozen MATLAB HGF Toolbox 8.2.0 of Mathys and colleagues is the reference oracle for this work. GitHub Actions and MATLAB were used only to regenerate paired oracle evidence. No additional acknowledgments are recorded at draft time.

## Figure captions

**Figure 1.** Evidence classes used in this article: direct MATLAB parity, matched reference limitation, not-directly-comparable pyhgf quantities, and preserved historical failure. File: `paper/figures/fig_evidence_classes.png` (PDF: `.pdf`).

**Figure 2.** Historical S7 paired parameter-recovery metrics for MATLAB 8.2.0 and HGFX 1.0.0 against frozen M18 thresholds. This panel is not a scientific PASS. File: `paper/figures/fig_recovery_metrics.png`.

**Figure 3.** Paired model-selection summary: MATLAB and HGFX balanced accuracy and 36/36 BIC winner agreement. File: `paper/figures/fig_model_selection.png`.

**Figure 4.** CPU-backend and physical Tesla T4 final-objective agreement on a log scale, against the frozen 1e-7 GPU criterion. Not a speed claim. File: `paper/figures/fig_gpu_applicability.png`.

**Figure 5.** Frozen HGFX versus pyhgf 0.3.2 common-scope trajectories (predicted probability and level-2 posterior mean) for the authorized 128-trial binary HGF. Eleven mapped perceptual quantities pass; response NLL remains NDC. File: `paper/figures/fig_pyhgf_common_scope.png`.

**Figure 6.** P3 trial-horizon diagnostic parameter-recovery metrics at 128, 256, 512 and 1024 trials, generated directly from the hash-verified M18C.2 aggregate. Dotted lines are the frozen thresholds. Incomplete HGF cases at 512/1024 trials are retained as gaps. Diagnostic PASS rows do not establish identifiability; the overall P3 classification remains `INSUFFICIENT_REFERENCE_EVIDENCE`. File: `paper/figures/fig_p3_horizon_diagnostics.png`.

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work, the author used OpenAI ChatGPT to assist with code drafting and review, repository/document consistency checks, manuscript organization, and language refinement. The author reviewed and edited the resulting material as needed, and all reported scientific results remained subject to the repository's frozen validation, evidence, and reproducibility gates. The author takes full responsibility for the content of the publication.

## References

Bibliography entries are in `paper/references.bib`.
