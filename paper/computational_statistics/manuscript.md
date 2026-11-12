# HGFX: a Python package for reference-compatible Hierarchical Gaussian Filter workflows

**Status:** Working revision for author review; not submission-ready. Historical results are unchanged. The worked example, mathematical summary, figures, and submission package remain to be completed under the execution plan.
**Target journal:** *Computational Statistics*; subscription route, subject to confirmation of zero mandatory author charges.
**Contribution:** Research software / package paper; exact submission-system article type to be verified.
**Plan:** `docs/superpowers/plans/2026-11-03-publication-revision.md`

**Authors and affiliations**

Mohammad Ahmadkhanloo

Institute for Research in Fundamental Sciences (IPM), Tehran, Iran

https://github.com/ahmadkhanloo

**Correspondence:** Mohammad Ahmadkhanloo, Institute for Research in Fundamental Sciences (IPM), Niavaran Square, Tehran, Iran. Email: m.ahmadkhanloo@ipm.ir. Software: https://github.com/ahmadkhanloo/hgfx.

**Keywords:** Hierarchical Gaussian Filter; statistical software; Bayesian learning; Python; reproducibility; numerical compatibility

## Abstract

Porting hierarchical Bayesian learning models across computational environments requires more than reproducing their equations: parameter conventions, floating-point evaluation, and numerical optimization can affect fitted inference. HGFX 1.0.0 implements Hierarchical Gaussian Filter (HGF) workflows in Python/JAX, using a pinned MATLAB HGF Toolbox 8.2.0 reference. We distinguish fixed-parameter agreement, fitted-endpoint reproducibility, model-selection agreement, and statistical parameter recovery. In an original fixed-vector comparison, 164 of 200 classic binary-HGF cases produced valid results on both sides and met the existing objective-agreement criterion; 36 were jointly invalid. Two other HGF families lacked predeclared family-specific objective acceptance thresholds, and one enhanced-HGF case was valid only in MATLAB. Cross-evaluation at historical fitted vectors met the established classic-HGF objective criterion in 128 of 128 paired endpoint evaluations, but this does not establish independently optimized fit equivalence. Across a separate paired model-selection grid, all 36 Bayesian information criterion winners agreed between MATLAB and HGFX, whereas balanced accuracy for identifying the generating model was 0.583 and parameter-recovery criteria were not fully met. An official unbounded-HGF fitting comparison retained trajectory discrepancies at independently fitted endpoints. Recorded physical-GPU results support limited objective correctness, not a speedup. HGFX offers a reproducible, evidence-graded MATLAB-to-Python workflow migration with explicit boundaries between numerical compatibility and statistical inference.

## 1 Introduction

Computational models of learning under uncertainty must represent uncertainty about latent states and about the volatility of those states. The Hierarchical Gaussian Filter (HGF) was introduced as a generic hierarchical Bayesian framework for individual learning under uncertainty [@mathys2011] and later developed into a practical filtering framework for perception and learning [@mathys2014]. It has been used to recover hierarchical prediction errors in neuroimaging [@iglesias2013] and to model inference about others' intentions [@diaconescu2014]. The associated MATLAB toolbox is distributed as part of TAPAS, an open-source collection of translational neuromodeling tools [@fraessle2021tapas], and remains a reference implementation for fitting, simulation, model comparison, and analysis.

Reproducing such a toolbox in another language is not equivalent to translating published equations. Scientific behavior also depends on parameter ordering, transforms, prior conventions, fixed and free parameter semantics, placeholder values, numerical primitives, finite-difference behavior, optimizer trajectories, failure modes, and model-family selection. Small floating-point differences that are negligible at a shared state can be amplified by derivative estimation and non-convex optimization [@wilson2019ten; @peng2011reproducible]. A replacement implementation can therefore appear mathematically correct while producing materially different fitted inferences or model-selection outcomes.

Python/JAX toolboxes already exist in this space. pyhgf represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference [@legrand2026pyhgf]. HGFX does not claim to be the first Python or JAX HGF. Its v1.0 objective is narrower and complementary: behavioral compatibility with one frozen MATLAB HGF Toolbox 8.2.0 oracle, explicit cross-language evidence, and removal of MATLAB from the user runtime.

For researchers with established HGF workflows, the practical question is whether fitting and simulation can move into a Python environment while retaining the reference configuration and numerical behavior. We evaluate this question for the released HGFX 1.0.0 package using workflow reproduction, paired model-selection agreement, backend checks, and a scoped pyhgf comparison. These checks establish the scope of compatibility; they do not establish that a fitted parameter is identifiable or that a selected model is the data-generating model.

The contribution is a documented statistical software implementation and a reproducible method for examining when a MATLAB-to-Python migration preserves scientific quantities. We do not introduce a new HGF model or assert that faster execution follows from using JAX. Three contributions are distinguished: (i) reference-pinned reproduction of supported HGF workflows in Python without a MATLAB user-runtime dependency; (ii) separate numerical checks for fixed-parameter objectives, fitted endpoints, model selection, and inferential recovery, so agreement at one level cannot be mistaken for agreement at another; and (iii) machine-readable records of both passing comparisons and failures, including numerically sensitive fits. This layered distinction is relevant to statistical computing independently of whether future workload-specific benchmarking finds acceleration, parity, or a slowdown.

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
| Validated CI platforms | Linux (Ubuntu) and Windows |
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

### 2.7 Original fixed-vector objective comparisons

To separate numerical evaluation of the statistical objective from the behavior of an optimizer, a prospectively registered comparison evaluated identical transformed parameter vectors and identical inputs in the published HGFX 1.0.0 wheel and pinned MATLAB HGF Toolbox 8.2.0. One experiment contained 200 fixed vectors per binary perceptual family (classic HGF, enhanced HGF, and unbounded HGF), each with 128 trials; all valid, invalid, and one-sided-invalid outcomes were retained. The pre-existing objective acceptance criterion applied specifically to classic HGF. The other families' numerical gaps were recorded descriptively because no corresponding predeclared family-specific acceptance criterion had been established; they cannot inherit the classic-HGF threshold.

A separate cross-evaluation used original fitted parameter vectors from two stress cases and a 64-subject binary-HGF cohort. Each available historical MATLAB or HGFX fitted endpoint was evaluated as a *fixed* vector in both implementations, without new fitting, obtaining 132 planned endpoint evaluations. One historical HGFX endpoint vector was absent from the archive and remained missing. This design tests shared-state objective evaluation, not the equality of optimizer trajectories, convergence, Hessians, or independently fitted inference states. Source and trial data, provenance, the single original permitted execution, and unresolved discrepancies are documented in the associated machine-readable research record.

## 3 Results

### 3.1 Workflow equivalence

HGFX 1.0.0 was released from commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Official demo reproductions execute the MATLAB oracle, execute the Python reproduction, compare complete release-relevant outputs, and archive machine-readable artifacts (Table 2).

The first demo is a regime in which classic binary HGF encounters negative posterior precision while eHGF succeeds. HGFX reproduces this: `hgf_binary` fails in both implementations, `ehgf_binary` succeeds in both, and eHGF trajectories agree within the frozen tolerance (agreement in this documented workflow outcome, not a BIC model-selection experiment).

The second demo reproduces the uHGF to uHGF-AR(1) transition, including the recorded third-level trajectory behavior in both implementations (direct uHGF-AR(1) workflow parity).

**Table 2.** Documented release workflow and analysis-surface checks. Recorded passes apply **only to the listed reference cases and APIs**, not to general fitting or model-family parity. Exact machine-readable rows are in `paper/tables/`.

| Surface | Classification |
|---|---|
| Core model/API compatibility (documented scopes) | scoped release checks passed; not a general fitting-parity verdict |
| uHGF to AR(1) official workflow | PASS |
| sampleModel / prior-predictive workflow | PASS |
| Correlation/residual analysis surfaces | PASS |
| Bayesian parameter averaging | PASS |

### 3.2 Fixed-vector objective agreement and its limits

In the original 600-case fixed-vector comparison, classic binary HGF yielded 164 paired-valid objective evaluations within its previously established numerical criterion and 36 jointly invalid cases. Joint invalidity is recorded as a separate outcome, not counted as parity. Enhanced binary HGF yielded 198 paired-valid, one jointly invalid, and one one-sided-invalid case; unbounded binary HGF yielded 198 paired-valid and two jointly invalid cases. Objective differences for the 396 paired-valid enhanced/unbounded cases are observations, **not family-level parity verdicts**, because no independent family-specific objective acceptance policy had been frozen before examining these results. Table 4 preserves all original case outcomes.

**Table 3.** Original published-release shared-vector objective comparison, with 128 trials per case and 200 cases in each family. Joint invalidity and one-sided invalidity are not counted as parity.

| Binary-HGF family | Both valid | Both invalid | One-sided invalid | Evidence classification |
|---|---:|---:|---:|---|
| Classic | 164 | 36 | 0 | 164/164 paired-valid objectives meet existing HGF M8 criterion; 36 shared-invalid are not passes |
| Enhanced | 198 | 1 | 1 | Raw objective values only; no prospectively frozen eHGF-family objective criterion |
| Unbounded | 198 | 2 | 0 | Raw objective values only; no prospectively frozen uHGF-family objective criterion |
| **Total** | **560** | **39** | **1** | **No global fit, optimizer or model-family parity conclusion** |

 In the enhanced-HGF one-sided-invalid case, MATLAB reported finite likelihood while HGFX yielded a nonfinite result in the released 1.0.0 version. The observed likelihood disagreement began at zero-based trial 11; a later isolated diagnostic localized an earlier latent discrepancy, but its maintenance correction is development-only and was not retroactively assigned to the released software.

The second fixed-vector experiment cross-evaluated historical fitted endpoints without rerunning optimization. For the original 64-subject classic-HGF cohort, all 128 available endpoints were paired-valid and satisfied the original HGF same-vector objective criterion; the maximum absolute negative-log-joint difference was `2.842170943040401e-14`. This is a narrower finding than full-fit parity: an earlier subject-specific trajectory disagreement and the historical 63-of-64 complete-fit nonpass remain unchanged. Two further uHGF endpoint objectives were valid numerically but lacked a preregistered family-specific gate. For the enhanced-HGF stress case, the original HGFX fitted endpoint was not archived; its missing comparison was neither imputed nor excluded from the planned denominator. Thus 131 of 132 endpoint slots were evaluable, with only the 128 classic-HGF slots meeting a pre-existing family acceptance rule.

These objective results support selective reproducibility of *evaluation at the same parameter vector*, not general agreement of optimization paths, fitted parameters, Hessian-based statistics, or scientific identifiability.

### 3.3 Fitting statistics and scoped limitations

The historical enhanced-HGF fitting stress case and a separately frozen unbounded-HGF Level-2 *holdout* exhibited endpoint sensitivity in MATLAB as well as between implementations; those observations are documented as **reference limitations in those specific tested scopes**, not as evidence of general fit equivalence (Table 4). The holdout's sensitivity cannot be transferred to a distinct official USD/CHF experiment merely because both use unbounded HGF.

In the official 614-observation USD/CHF `uhgf + gaussian_obs` comparison with MATLAB-generated responses, two unintended concurrent runs used the same original reference inputs and published HGFX 1.0.0 wheel. At independently fitted endpoints, `traj.epsi` violated the unchanged paired gate at **4 of 1228** and **3 of 1228** entries, respectively. Both scientific results remain `UNRESOLVED_DISCREPANCY`. Although objective totals evaluated at shared parameter vectors were numerically close, the full optimizer path was not archived and the cause of fitted-endpoint differences has not been established. These two executions are retained as a documented protocol deviation, not presented as a designed replication.

**Table 4.** Fitting and recovery classifications. Direct failures are retained.

| Surface | Direct result | Paper disposition |
|---|---|---|
| Earlier frozen parameter-recovery experiment | scientific criterion not met | preserved failure |
| Historical enhanced-HGF fitting stress case | different fitted endpoints; MATLAB start sensitivity | reference limitation, **restricted to original scope** |
| Frozen unbounded-HGF Level-2 holdout fit | inference-equivalence failure; MATLAB start sensitivity | reference limitation, **restricted to holdout** |
| Official USD/CHF unbounded-HGF paired fit | original `traj.epsi` failures: 4/1228 and 3/1228 | **unresolved discrepancy; no fitting parity** |
| Paired parameter recovery | recovery criteria not fully met | matched reference limitation |
| Paired model selection | 36/36 BIC winners match | direct agreement |

### 3.4 Parameter recovery versus model selection

The earlier historical M18 parameter-recovery failure remains preserved separately. Figure 2 and Table 5 report the subsequent paired S7 recovery grid, whose recovery criteria are also not fully met. Paired S7 model selection is stronger: 36/36 BIC winners match (Figure 3). Model-selection agreement is not used to imply strong parameter identifiability. Full grid dimensions, frozen thresholds, and the prospective trial-horizon extension are reported in Supplementary Appendix S3.

The trial-horizon study (section 2.6) is complete as an executed protocol, not as a positive identifiability result. Because its paired-integrity gate failed, the available evidence is insufficient for a stronger recovery or identifiability conclusion. Diagnostic per-horizon numbers are archived with the paper materials and shown in Figure 6; they do not replace the earlier recovery evidence.

**Table 5.** Paired parameter recovery on the frozen three-model grid (both truth scales). Thresholds: convergence >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00. Full precision: `paper/tables/recovery_model_selection.md`.

| Model | MATLAB / HGFX convergence | MATLAB / HGFX median r | MATLAB / HGFX median sRMSE | Failed criteria |
|---|---|---|---|---|
| hgf_binary | 0.833 / 0.833 | 0.203 / 0.203 | 2.610 / 2.610 | correlation, sRMSE |
| ehgf_binary | 0.917 / 0.917 | 0.462 / 0.462 | 2.359 / 2.359 | correlation, sRMSE |
| uhgf_binary | 0.792 / 0.792 | 0.381 / 0.381 | 2.958 / 2.958 | convergence, correlation, sRMSE |

### 3.5 Backend and physical-GPU applicability

Compatibility CPU and JAX-backed CPU outputs agree under the frozen backend-equivalence criterion; the post-fix CPU value is remeasured from the released numerical path and is reported with Figure 4 provenance. Physical-GPU applicability is retained from source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec`: the hosted environment exposed two Tesla T4 devices (Python 3.12.13, JAX/JAXLIB 0.11.1), while the four required fitting cells executed on `cuda:0`. Residency was checked by JAX device placement, with `nvidia-smi -L` used only to enumerate the visible hardware. All four CPU-versus-GPU cells pass the frozen final-objective criterion <= 1e-7; the maximum gap is 1.4210854715202004e-14 (Figure 4; Table 6). The retained GPU result is applicability/correctness evidence, not a speed or scaling result. Exact hardware/runtime provenance, the retention basis, objective pairs, execution command, and raw-artifact checksum are reported in Supplementary Appendix S5.

**Table 6.** Backend and GPU applicability.

| Surface | Classification | Result |
|---|---|---|
| Compatibility vs JAX CPU | direct backend agreement | objective/backend agreement |
| Physical NVIDIA GPU (Tesla T4; 2 visible, tested device `cuda:0`) | retained physical-GPU applicability evidence | max abs objective gap = 1.42e-14; criterion 1e-7 |

### 3.6 Common-scope comparison with pyhgf

In the authorized 128-trial cell, all 11 mapped perceptual/inference quantities passed predeclared tolerances (Figure 5). Maximum absolute differences were at binary64 rounding scale (1.11e-16 to 1.55e-15). Observed-input integrity was exact.

Participant-response NLL was not directly comparable. With `ze = 48`, the pyhgf-side power-ratio transformation reached an exact probability boundary on 13 trials and unclipped surprise became +Inf; the HGFX log-domain `unitsq_sgm` evaluation remained finite (total NLL 1808.855415351429). No clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. Overall interpretation: mapped perceptual quantities agree in the authorized cell, while participant-response NLL remains not directly comparable. The semantic gate, exact comparator identity, and numerical-boundary details are given in Supplementary Appendix S4.

### 3.7 Examples of use and current limitations

Typical use after `pip install hgfx==1.0.0` is MATLAB-style fitting and simulation from Python. The official cross-language demo reproductions are repository workflows that additionally require a source checkout and the frozen MATLAB-reference submodule; they are not bundled as ordinary wheel examples. MATLAB is unnecessary for normal package use.

Current limitations: (i) compatibility is scoped to HGF Toolbox 8.2.0, not future upstream versions; (ii) classic-HGF fixed-vector objective agreement does not imply general fitting parity, and the released enhanced-HGF one-sided-invalid case and official USD/CHF fitted-trajectory discrepancies remain unresolved; (iii) the independently sensitive historical fitting stress cases support only narrow reference-limitation statements; (iv) parameter recovery and the trial-horizon integrity gate do not support strong identifiability conclusions; (v) GPU evidence is T4 objective applicability, not speed/throughput, and pyhgf agreement covers only an explicitly mapped perceptual cell.

## 4 Discussion

Reproducing a scientific toolbox requires a broader notion of compatibility than implementing published equations. The available evidence supports three distinct levels: a fixed-vector numerical comparison in a known valid domain; cross-evaluation of objective values at historical fitted endpoints; and end-to-end fit or statistical-inference agreement, which is not established globally here. In sensitive fitting problems, binary64-scale elementary differences may be amplified through finite-difference derivatives and quasi-Newton optimization, producing different endpoints even when shared-state objectives are extremely close. The observed discrepancy is consistent with such sensitivity, but a first causal optimizer decision has not been demonstrated for the official USD/CHF run.

This motivates separating scientific correctness from reference faithfulness. When the MATLAB oracle is itself unstable in a tested scope, forcing Python toward a preferred endpoint can be less faithful than preserving the oracle's limitation. A matched limitation is not evidence that the recovered parameter is identifiable. HGFX therefore preserves original failures and reports the narrow product-compatibility interpretation separately.

Workflow-level validation matters for the same reason. Reproducing the expected failure of classic HGF in a documented regime, while reproducing successful eHGF behavior, is part of compatibility. Treating every failure as an implementation bug would have encouraged divergence from the reference.

pyhgf and HGFX overlap but have different design centers. pyhgf emphasizes generalized network construction and differentiability [@legrand2026pyhgf]. HGFX v1.0 emphasizes frozen-MATLAB compatibility and provenance. Quantity-specific claims are more informative than ranking the packages. Mapped belief trajectories agree to rounding scale in the authorized cell; the response-NLL surface exposes a numerical-boundary difference even though the mapped belief values agree to binary64 rounding scale.

JAX enables compiled CPU/GPU execution, batching, and multi-device workloads [@jax2018github; @frostig2018]. Accelerator-native code is scientifically useful only if the accelerated path preserves relevant outputs. The T4 result supports that claim for the tested objective. Throughput depends on workload size, compilation amortization, hardware, device count, and contention; protocol 1 therefore does not activate a headline performance or scaling result. Scalability of the JAX path is an engineering capability of the implementation, not a reported empirical law.

For statistical practice, HGFX offers a way to reuse documented HGF workflows within Python while inspecting the evidence supporting each compatibility claim. The paired model-selection result illustrates why that evidence must be interpreted carefully: identical BIC winners across implementations can coexist with imperfect recovery of the generating model. Users should assess parameter recovery and model discrimination for their intended design before interpreting fitted quantities substantively. The package and its evidence record support that assessment but do not replace it. For this software article, the testable statistical-computing contribution is a documented separation of numerical evaluation, optimization outcomes, and recoverability under a fixed reference. A favorable speed ratio is neither necessary for this claim nor inferable from GPU availability. No new precision-stability or redesigned-recovery result is asserted until such a protocol is completed.

## 5 Data and code availability

HGFX 1.0.0 is MIT-licensed [@hgfx100]. Source, tag, and package URLs are in Table 1. Paper tables regenerate with `python paper/scripts/generate_p2_tables.py`. Figures regenerate with `python paper/scripts/generate_p5_figures.py` (300 dpi PNG and PDF). The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence. Repository-facing case identifiers and claim-to-evidence traceability are intentionally confined to Supplementary Appendix S6.

## Statements and Declarations

### Competing interests

The author is the developer and maintainer of HGFX and declares no other competing financial interests or personal relationships that could have appeared to influence the work.

### Author contributions

Mohammad Ahmadkhanloo: Conceptualization, Software, Validation, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.

### Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## Acknowledgments

The frozen MATLAB HGF Toolbox 8.2.0 of Mathys and colleagues is the reference oracle for this work. GitHub Actions and MATLAB were used only to regenerate paired oracle evidence. No additional acknowledgments are recorded at draft time.

## Figure captions

**Figure 1.** Evidence classes used in this article: direct MATLAB parity, matched reference limitation, not-directly-comparable pyhgf quantities, and preserved historical failure. File: `paper/figures/fig_evidence_classes.png` (PDF: `.pdf`).

**Figure 2.** Paired parameter-recovery metrics for MATLAB 8.2.0 and HGFX 1.0.0 against the predeclared recovery thresholds. This panel does not constitute a scientific recovery success. File: `paper/figures/fig_recovery_metrics.png`.

**Figure 3.** Two distinct model-selection summaries: MATLAB and HGFX agree on the BIC winner in 36/36 paired cases, whereas model-recovery balanced accuracy is 0.583333333333 for each implementation. Agreement measures reproducibility across implementations; balanced accuracy measures recovery of the generating model. The model-recovery threshold applies only to balanced accuracy. File: `paper/figures/fig_model_selection.png`.

**Figure 4.** Backend agreement relative to each comparison's frozen criterion. The post-fix compatibility-versus-JAX-CPU remeasurement has a maximum final-objective gap of 0.006783711260709424 against a 0.10 criterion; JAX-CPU-versus-retained-physical-T4 has a maximum gap of 1.4210854715202004e-14 against a 1e-7 criterion. Bars show gap/criterion ratios, so the dashed line at 1.0 is the acceptance boundary for both comparisons. Not a speed claim. File: `paper/figures/fig_gpu_applicability.png`.

**Figure 5.** Frozen HGFX versus pyhgf 0.3.2 common-scope trajectories (predicted probability and level-2 posterior mean) for the authorized 128-trial binary HGF. Eleven mapped perceptual quantities pass; response NLL remains NDC. File: `paper/figures/fig_pyhgf_common_scope.png`.

**Figure 6.** Trial-horizon diagnostic parameter-recovery metrics at 128, 256, 512 and 1024 trials, generated directly from the hash-verified aggregate. Dotted lines are the predeclared thresholds. Incomplete classic-HGF cases at 512/1024 trials are retained as gaps. Individual diagnostic criteria do not establish identifiability; the paired-integrity gate failed, so the evidence remains insufficient for an identifiability conclusion. File: `paper/figures/fig_p3_horizon_diagnostics.png`.

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work, the author used OpenAI ChatGPT to assist with code drafting and review, repository/document consistency checks, manuscript organization, and language refinement. The author reviewed and edited the resulting material as needed, and all reported scientific results remained subject to the repository's frozen validation, evidence, and reproducibility gates. The author takes full responsibility for the content of the publication.

## References

Bibliography entries are in `paper/references.bib`.

<!-- Working revision: no submission-candidate lock has been created for this version. -->
