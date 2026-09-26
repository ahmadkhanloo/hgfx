#!/usr/bin/env python3
"""Generate and validate the P6A-2 manuscript numerical-claim audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

CLAIMS = json.loads(r'''[{"id":"abstract_core_results","line_hint":22,"text":"The Hierarchical Gaussian Filter (HGF) is a hierarchical Bayesian model of learning under uncertainty and volatility, with a widely used MATLAB implementation. We present HGFX 1.0.0, a Python/JAX toolbox whose primary objective is validated behavioral and numerical compatibility with a frozen HGF Toolbox 8.2.0 reference in the documented scopes, while removing MATLAB as a user-runtime dependency. Reimplementation is treated as a validation problem rather than source translation: configuration semantics, parameter transforms, forward trajectories, observation likelihoods, objectives, fitting and statistical surfaces, simulation workflows, official demo behavior, model selection, and backend agreement are compared against the pinned oracle under predeclared tolerances. Two official MATLAB demo workflows reproduce the reference at frozen trajectory tolerances, including a documented regime in which classic HGF encounters negative posterior precision while eHGF completes successfully. In paired model-selection validation, all 36 BIC winners agree between MATLAB and HGFX. Physical NVIDIA GPU applicability was confirmed on two Tesla T4 devices, with a maximum CPU-versus-GPU final-objective difference of 1.42e-14 against a frozen 1e-7 criterion. Historical parameter-recovery failures and exact MATLAB/HGFX limitation matches are preserved and are not reclassified as scientific success. A prospectively gated comparison with pyhgf 0.3.2 shows binary64-scale agreement on mapped perceptual trajectories in one authorized three-level binary-HGF cell, while participant-response negative log-likelihood is retained as not directly comparable. HGFX therefore provides a MATLAB-independent Python implementation with an explicit evidence model that separates direct parity, matched reference limitations, backend applicability, and future performance claims.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","docs/user/MATLAB_DEMOS.md","reference/validation/m18_s7_reference_limitation/decision.json","gpu_validation_results/m18_s9_physical_gpu_revalidation.json","paper/reproducibility/p2a10_comparison_35268575414.json"]},{"id":"positioning_and_frozen_versions","line_hint":30,"text":"Python/JAX toolboxes already exist in this space. pyhgf represents predictive-coding systems as configurable node/edge networks and supports differentiable modern inference [@legrand2026pyhgf]. HGFX does not claim to be the first Python or JAX HGF. Its v1.0 objective is narrower and complementary: behavioral compatibility with one frozen MATLAB HGF Toolbox 8.2.0 oracle, explicit cross-language evidence, and removal of MATLAB from the user runtime.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","reference/validation/v1_release/evidence_manifest.json"]},{"id":"released_scope_summary","line_hint":32,"text":"This paper asks whether a legacy scientific toolbox can be reproduced in an accelerator-compatible stack without silently changing the scientific contract. We report the released HGFX 1.0.0 evidence: workflow reproduction, paired model-selection agreement, CPU/backend and physical-GPU applicability, a scoped pyhgf comparison, and preserved historical failures. General speedup and multi-GPU scaling are not headline claims.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","reference/validation/v1_release/evidence_manifest.json","gpu_validation_results/m18_s9_physical_gpu_revalidation.json","paper/reproducibility/p2a10_comparison_35268575414.json"]},{"id":"python_version_requirement","line_hint":38,"text":"HGFX is a Python package (Python >= 3.11) built on NumPy and JAX [@jax2018github; @frostig2018]. The public surface exposes Python-first and MATLAB-style aliases (`fit_model`/`fitModel`, `sim_model`/`simModel`, `sample_model`/`sampleModel`). Compatibility-sensitive numerical paths are distinguished from JAX-backed execution. Compatibility repairs were introduced only when supported by an exact MATLAB oracle case and a failing regression.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"release_version_metadata","line_hint":47,"text":"| Version | 1.0.0 |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","reference/validation/v1_release/evidence_manifest.json","docs/validation/V1_FINAL_RELEASE_PROVENANCE.md"]},{"id":"github_release_metadata","line_hint":49,"text":"| Release | https://github.com/ahmadkhanloo/hgfx/releases/tag/v1.0.0 |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["docs/validation/V1_FINAL_RELEASE_PROVENANCE.md","paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"pypi_release_metadata","line_hint":50,"text":"| PyPI | `hgfx==1.0.0` |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["docs/validation/V1_FINAL_RELEASE_PROVENANCE.md","paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"python_version_metadata","line_hint":52,"text":"| Language | Python 3.11+ |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"matlab_oracle_identity","line_hint":55,"text":"| Frozen MATLAB oracle | HGF Toolbox 8.2.0 @ `2437f4dc241541072722a2695ddeca7b44d83dd3` |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"hgfx_frozen_source_identity","line_hint":56,"text":"| Frozen HGFX source | `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27` |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","docs/validation/V1_FINAL_RELEASE_PROVENANCE.md"]},{"id":"paper_protocol_identity","line_hint":57,"text":"| Paper protocol | `hgfx-paper-protocol-1` |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"v1_model_coverage","line_hint":63,"text":"The HGF represents a hidden hierarchy of Gaussian states in which higher levels encode volatility of lower levels [@mathys2011; @mathys2014]. For binary observations, a unit-square sigmoid observation model maps the first hidden state to the probability of the observed outcome. HGFX v1.0 covers the classic HGF, the enhanced HGF (eHGF), and the unbounded HGF (uHGF) in the documented MATLAB-compatible configurations, plus specialized surfaces in the v1 migration matrix (sampling, analysis, Bayesian parameter averaging, and the official uHGF-AR(1) demo). Equations are those of the frozen MATLAB toolbox; this article does not introduce a new generative model.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/tables/model_workflow_coverage.md","docs/user/MATLAB_DEMOS.md","paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"frozen_reference_scope","line_hint":69,"text":"HGFX v1.0 is validated against HGF Toolbox 8.2.0 at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`. The compatibility target includes the documented model/configuration inventory, parameter transforms and priors, HGF/eHGF/uHGF and specialized implementations, observation models, fitting and simulation surfaces, Hessian/covariance/correlation/statistical outputs, model selection, official workflow behavior, and public APIs.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","reference/validation/v1_release/evidence_manifest.json"]},{"id":"binary64_numerical_policy","line_hint":82,"text":"The evidence hierarchy is: frozen reference identity; machine-readable validation artifacts; paired MATLAB/HGFX raw outputs; continuous-integration provenance; and manuscript tables/figures generated from those artifacts. Numerical checks use IEEE-754 binary64. The project does not target arbitrary-precision solutions that differ from frozen MATLAB execution.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"official_demo_trial_count_and_tolerances","line_hint":84,"text":"Two official MATLAB demo workflows (320 binary trials) are release-gated. Complete release-relevant trajectories and inference states are compared at `rtol = 5e-11` and `atol = 5e-13`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["docs/user/MATLAB_DEMOS.md"]},{"id":"s7_grid_and_thresholds","line_hint":88,"text":"The historical M18 scientific recovery experiment failed and is preserved. Subsequent paired product-level validation distinguishes parameter recovery from model selection on an exact S7 grid (three binary perceptual models; truth scales 0.15 and 0.35; Quasi-Newton; frozen M18 thresholds: convergence rate >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00, model-recovery balanced accuracy >= 0.50).","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json","paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"pyhgf_common_scope_protocol","line_hint":94,"text":"`pyhgf==0.3.2` was pinned before execution. Direct comparison was allowed only after model structure, update equations, parameters, initialization, input/masking semantics, reported quantities, precision mode, and numerical guards had been mapped. The authorized cell is a fixed-parameter, fully observed, three-level binary HGF (128 trials; standard/mean-field updates; unit coupling; zero drift; inverse temperature `ze = 48`). Trajectory quantities used `atol = 1e-10` and `rtol = 1e-8`; total response NLL used `atol = 1e-7` and `rtol = 1e-8`. Raw arrays were hashed before interpretation. A derived response-NLL boundary nonfinite was prospectively classified as NDC rather than triggering post-result clipping.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","paper/reproducibility/pyhgf_common_scope_case.json","paper/reproducibility/pyhgf_precision_numerical_policy.json"]},{"id":"p3_execution_and_integrity_failure","line_hint":98,"text":"Paper protocol 1 includes a prospectively frozen paired MATLAB/HGFX experiment (`m18c2-trial-horizon-identifiability-1`) at 128, 256, 512 and 1024 trials, using the S7 models, truth scales, seeds, Quasi-Newton budget, and M18 thresholds. The preregistered scientific comparison is 256 versus 1024 after a paired-integrity gate; 128 and 512 are trajectory diagnostics. Failed simulations and fits are retained. Historical M18 is not rewritten. The experiment completed on GitHub Actions (run `35272347167`; 24/24 shards). The frozen paired-integrity gate did not pass: 10 of 72 model-recovery BIC winners disagreed, all in `hgf_binary` at 512 or 1024 trials, and `hgf_binary` parameter metrics at those horizons are undefined because invalid simulations were retained rather than resampled. The official class is `INSUFFICIENT_REFERENCE_EVIDENCE`. No data-horizon or structural-identifiability conclusion is promoted.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/p3_m18c2_aggregate_35272347167.json","paper/reproducibility/p3_m18c2_provenance_35272347167.json","docs/research/P3_M18C2_RESULT.md"]},{"id":"v1_release_source","line_hint":104,"text":"HGFX 1.0.0 was released from commit `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`. Official demo reproductions execute the MATLAB oracle, execute the Python reproduction, compare complete release-relevant outputs, and archive machine-readable artifacts (Table 2).","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","docs/validation/V1_FINAL_RELEASE_PROVENANCE.md"]},{"id":"uhgf_ar1_demo_extrema","line_hint":108,"text":"The second demo reproduces the uHGF to uHGF-AR(1) transition. The maximum absolute third-level posterior mean is 16.99162398501939 for uHGF and 4.0927117005012175 for uHGF-AR(1) in both implementations (`PASS_UHGF_AR1_WORKFLOW_PARITY`).","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["docs/user/MATLAB_DEMOS.md"]},{"id":"d02_d08_reference_limitations","line_hint":122,"text":"D02 and D08 remain exact-scope reference limitations (Table 3). The MATLAB oracle exhibits endpoint/basin sensitivity in those scopes; HGFX matches the limitation. The release claims MATLAB-equivalent behavior in accepted product accounting, not universal optimizer endpoint identity.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_d02_reference_limitation/decision.json","reference/validation/m18_d08_reference_limitation/decision.json"]},{"id":"historical_m18_fail","line_hint":128,"text":"| Historical M18 scientific experiment | FAIL_PRESERVED | preserved historical failure |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/v1_release/evidence_manifest.json"]},{"id":"d02_classification","line_hint":129,"text":"| D02 fitting | optimizer mismatch | REFERENCE_LIMITATION_MATCH |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_d02_reference_limitation/decision.json"]},{"id":"d08_classification","line_hint":130,"text":"| D08 fitting holdout | inference-equivalence fail | REFERENCE_LIMITATION_MATCH |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_d08_reference_limitation/decision.json"]},{"id":"s7_recovery_classification","line_hint":131,"text":"| S7 parameter recovery | scientific_pass = false | REFERENCE_LIMITATION_MATCH |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json"]},{"id":"s7_model_selection_36_of_36","line_hint":132,"text":"| S7 paired model selection | 36/36 BIC winners match | PASS_PAIRED_MODEL_SELECTION |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json"]},{"id":"s7_model_selection_result","line_hint":136,"text":"Historical parameter-recovery failure remains part of the record (Figure 2; Table 4). Paired model selection is stronger: 36/36 BIC winners match (Figure 3). Model-selection agreement is not used to imply strong parameter identifiability.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json"]},{"id":"p3_classification_and_scope","line_hint":138,"text":"The trial-horizon study (section 2.6) is complete as an executed protocol, not as a positive identifiability result. Official classification: `INSUFFICIENT_REFERENCE_EVIDENCE`. This manuscript therefore still does not claim generally strong parameter recovery for HGFX or for the MATLAB reference. Diagnostic per-horizon numbers are archived with the paper materials and shown in Figure 6; they must not overwrite Table 4 or historical M18.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/p3_m18c2_aggregate_35272347167.json","docs/research/P3_M18C2_RESULT.md"]},{"id":"s7_thresholds","line_hint":140,"text":"**Table 4.** S7 paired parameter recovery (both truth scales). Thresholds: convergence >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00. Full precision: `paper/tables/recovery_model_selection.md`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json","paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"s7_hgf_rounded_metrics","line_hint":144,"text":"| hgf_binary | 0.833 / 0.833 | 0.203 / 0.203 | 2.610 / 2.610 | correlation, sRMSE |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json"]},{"id":"s7_ehgf_rounded_metrics","line_hint":145,"text":"| ehgf_binary | 0.917 / 0.917 | 0.462 / 0.462 | 2.359 / 2.359 | correlation, sRMSE |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json"]},{"id":"s7_uhgf_rounded_metrics","line_hint":146,"text":"| uhgf_binary | 0.792 / 0.792 | 0.381 / 0.381 | 2.958 / 2.958 | convergence, correlation, sRMSE |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json"]},{"id":"gpu_environment_and_objective_agreement","line_hint":150,"text":"Compatibility CPU and JAX-backed CPU outputs pass `PASS_CPU_BACKEND_EQUIVALENCE`. On two Tesla T4 GPUs (Python 3.12.13, JAX/JAXLIB 0.11.1, `nvidia-smi` process residency), all four required CPU-versus-GPU fitting cells pass the frozen final-objective criterion <= 1e-7. The maximum gap is 1.4210854715202004e-14 (Figure 4; Table 5). This is applicability/correctness evidence, not a speed or scaling result.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["gpu_validation_results/m18_s9_physical_gpu_revalidation.json","reference/validation/v1_release/evidence_manifest.json"]},{"id":"gpu_table_result","line_hint":157,"text":"| Physical NVIDIA GPU (2x Tesla T4) | PASS_PHYSICAL_GPU_APPLICABILITY | max abs objective gap = 1.42e-14; criterion 1e-7 |","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["gpu_validation_results/m18_s9_physical_gpu_revalidation.json"]},{"id":"pyhgf_mapped_quantity_result","line_hint":161,"text":"In the authorized 128-trial cell, all 11 mapped perceptual/inference quantities passed predeclared tolerances (Figure 5). Maximum absolute differences were at binary64 rounding scale (1.11e-16 to 1.55e-15). Observed-input integrity was exact.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/p2a10_comparison_35268575414.json"]},{"id":"pyhgf_response_nll_boundary_result","line_hint":163,"text":"Participant-response NLL was not directly comparable. With `ze = 48`, the pyhgf-side power-ratio transformation reached an exact probability boundary on 13 trials and unclipped surprise became +Inf; the HGFX log-domain `unitsq_sgm` evaluation remained finite (total NLL 1808.855415351429). No clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. Overall classification: `PARTIAL_MATCH_WITH_NOT_DIRECTLY_COMPARABLE_QUANTITIES`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/p2a10_raw_numeric_result_35268575414.json","paper/reproducibility/p2a10_comparison_35268575414.json","paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"stable_install_version","line_hint":167,"text":"Typical use after `pip install hgfx==1.0.0` is MATLAB-style fitting and simulation from Python, including the official demo reproductions. MATLAB is unnecessary for those user paths.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","docs/validation/V1_FINAL_RELEASE_PROVENANCE.md"]},{"id":"limitations_scope","line_hint":169,"text":"Current limitations: (i) compatibility is scoped to HGF Toolbox 8.2.0, not future upstream versions; (ii) D02/D08 are matched reference limitations, not scientific recovery success; (iii) parameter identifiability is weaker than paired model selection, and the trial-horizon experiment returned `INSUFFICIENT_REFERENCE_EVIDENCE` after a failed paired-integrity gate, so it does not support a stronger recovery claim; (iv) GPU evidence is T4 applicability, not throughput; (v) the pyhgf result is one mapped cell, not package-wide equivalence.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","reference/validation/m18_d02_reference_limitation/decision.json","reference/validation/m18_d08_reference_limitation/decision.json","paper/reproducibility/p3_m18c2_aggregate_35272347167.json","gpu_validation_results/m18_s9_physical_gpu_revalidation.json","paper/reproducibility/p2a10_comparison_35268575414.json"]},{"id":"binary64_discussion_scope","line_hint":173,"text":"Reproducing a scientific toolbox requires a broader notion of compatibility than implementing published equations. In numerically sensitive fitting problems, binary64-scale elementary differences can be amplified through finite-difference derivatives and quasi-Newton optimization, producing different endpoints even when shared-state objectives are extremely close.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","reference/validation/m18_d02_reference_limitation/decision.json"]},{"id":"pyhgf_discussion_scope","line_hint":179,"text":"pyhgf and HGFX overlap but have different design centers. pyhgf emphasizes generalized network construction and differentiability [@legrand2026pyhgf]. HGFX v1.0 emphasizes frozen-MATLAB compatibility and provenance. Quantity-specific claims are more informative than ranking the packages. Mapped belief trajectories agree to rounding scale in the authorized cell; the response-NLL surface exposes a numerical-boundary difference despite sharing the same predicted belief.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","paper/reproducibility/p2a10_comparison_35268575414.json"]},{"id":"gpu_discussion_scope","line_hint":181,"text":"JAX enables compiled CPU/GPU execution, batching, and multi-device workloads [@jax2018github; @frostig2018]. Accelerator-native code is scientifically useful only if the accelerated path preserves relevant outputs. The T4 result supports that claim for the tested objective. Throughput depends on workload size, compilation amortization, hardware, device count, and contention; protocol 1 therefore does not activate a headline performance or scaling result. Scalability of the JAX path is an engineering capability of the implementation, not a reported empirical law.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","gpu_validation_results/m18_s9_physical_gpu_revalidation.json"]},{"id":"release_and_regeneration_metadata","line_hint":187,"text":"HGFX 1.0.0 is MIT-licensed [@hgfx100]. Source, tag, and package URLs are in Table 1. Paper tables regenerate with `python paper/scripts/generate_p2_tables.py`. Figures regenerate with `python paper/scripts/generate_p5_figures.py` (300 dpi PNG and PDF). The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md","docs/validation/V1_FINAL_RELEASE_PROVENANCE.md","paper/scripts/generate_p2_tables.py","paper/scripts/generate_p5_figures.py"]},{"id":"oracle_acknowledgment_identity","line_hint":203,"text":"The frozen MATLAB HGF Toolbox 8.2.0 of Mathys and colleagues is the reference oracle for this work. GitHub Actions and MATLAB were used only to regenerate paired oracle evidence. No additional acknowledgments are recorded at draft time.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/PAPER_PROTOCOL.md"]},{"id":"figure2_recovery_caption","line_hint":209,"text":"**Figure 2.** Historical S7 paired parameter-recovery metrics for MATLAB 8.2.0 and HGFX 1.0.0 against frozen M18 thresholds. This panel is not a scientific PASS. File: `paper/figures/fig_recovery_metrics.png`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json","paper/figures/p5_figures_manifest.json"]},{"id":"figure3_model_selection_caption","line_hint":211,"text":"**Figure 3.** Paired model-selection summary: MATLAB and HGFX balanced accuracy and 36/36 BIC winner agreement. File: `paper/figures/fig_model_selection.png`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["reference/validation/m18_s7_reference_limitation/decision.json","paper/figures/p5_figures_manifest.json"]},{"id":"figure4_gpu_caption","line_hint":213,"text":"**Figure 4.** CPU-backend and physical Tesla T4 final-objective agreement on a log scale, against the frozen 1e-7 GPU criterion. Not a speed claim. File: `paper/figures/fig_gpu_applicability.png`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["gpu_validation_results/m18_s9_physical_gpu_revalidation.json","paper/figures/p5_figures_manifest.json"]},{"id":"figure5_pyhgf_caption","line_hint":215,"text":"**Figure 5.** Frozen HGFX versus pyhgf 0.3.2 common-scope trajectories (predicted probability and level-2 posterior mean) for the authorized 128-trial binary HGF. Eleven mapped perceptual quantities pass; response NLL remains NDC. File: `paper/figures/fig_pyhgf_common_scope.png`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/p2a10_comparison_35268575414.json","paper/figures/p5_figures_manifest.json"]},{"id":"figure6_p3_caption","line_hint":217,"text":"**Figure 6.** P3 trial-horizon diagnostic parameter-recovery metrics at 128, 256, 512 and 1024 trials, generated directly from the hash-verified M18C.2 aggregate. Dotted lines are the frozen thresholds. Incomplete HGF cases at 512/1024 trials are retained as gaps. Diagnostic PASS rows do not establish identifiability; the overall P3 classification remains `INSUFFICIENT_REFERENCE_EVIDENCE`. File: `paper/figures/fig_p3_horizon_diagnostics.png`.","category":"NUMERICAL_OR_VERSIONED_CLAIM","evidence":["paper/reproducibility/p3_m18c2_aggregate_35272347167.json","paper/figures/p5_figures_manifest.json"]}]''')
EXEMPTIONS = json.loads(r'''[{"line_hint":40,"text":"Software metadata and frozen validation identities are summarized in Table 1.","reason":"structural table cross-reference only"},{"line_hint":42,"text":"**Table 1.** HGFX 1.0.0 software metadata.","reason":"table caption/version label; values are audited in the table rows"},{"line_hint":71,"text":"We use four interpretation classes (Figure 1):","reason":"figure-number cross-reference; no quantitative result in the sentence"},{"line_hint":90,"text":"CPU/backend equivalence and physical NVIDIA GPU applicability were tested after an independent review of portability blockers (host C runtime `expm1`/`log` paths and Windows CRLF hash failures). Both blockers were remediated without changing scientific thresholds.","reason":"digit occurs only in the function identifier expm1; no numerical claim"},{"line_hint":115,"text":"| uHGF to AR(1) official workflow | PASS |","reason":"digit occurs only in the model identifier AR(1); classification is audited via the demo evidence"},{"line_hint":207,"text":"**Figure 1.** Evidence classes used in this article: direct MATLAB parity, matched reference limitation, not-directly-comparable pyhgf quantities, and preserved historical failure. File: `paper/figures/fig_evidence_classes.png` (PDF: `.pdf`).","reason":"figure-number caption label only; no quantitative value beyond the label"},{"line_hint":110,"text":"**Table 2.** Official workflow and analysis-surface coverage. Exact machine-readable rows are in `paper/tables/`.","reason":"table caption number only; substantive workflow claims are audited in the associated text/table rows"},{"line_hint":124,"text":"**Table 3.** Fitting and recovery classifications. Direct failures are retained.","reason":"table caption number only; D02/D08/S7 claims are audited in the associated rows"},{"line_hint":152,"text":"**Table 5.** Backend and GPU applicability.","reason":"table caption number only; backend/GPU numerical claims are audited in the associated paragraph and row"}]''')

# Reader-facing edits changed wording, not evidence. Keep each revised numerical
# sentence explicitly bound to the evidence set of its original audited claim.
CURRENT_TEXT_BY_ID = {
    "s7_grid_and_thresholds": "An earlier frozen parameter-recovery experiment failed its scientific acceptance criteria and remains preserved. Subsequent paired validation distinguishes parameter recovery from model selection on a frozen three-model grid (three binary perceptual models; truth scales 0.15 and 0.35; Quasi-Newton; predeclared thresholds: convergence rate >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00, model-recovery balanced accuracy >= 0.50).",
    "p3_execution_and_integrity_failure": "A prospectively frozen paired MATLAB/HGFX trial-horizon experiment examined 128, 256, 512 and 1024 trials using the same three perceptual models, truth scales, seeds, Quasi-Newton budget, and predeclared recovery thresholds. The preregistered scientific comparison was 256 versus 1024 after a paired-integrity gate; 128 and 512 were trajectory diagnostics. Failed simulations and fits were retained rather than resampled. The experiment completed on GitHub Actions (run `35272347167`; 24/24 shards). The paired-integrity gate did not pass: 10 of 72 model-recovery BIC winners disagreed, all for the classic binary HGF at 512 or 1024 trials, and parameter metrics for those horizons were undefined because invalid simulations were retained. The evidence was therefore judged insufficient to support a data-horizon or structural-identifiability conclusion.",
    "uhgf_ar1_demo_extrema": "The second demo reproduces the uHGF to uHGF-AR(1) transition. The maximum absolute third-level posterior mean is 16.99162398501939 for uHGF and 4.0927117005012175 for uHGF-AR(1) in both implementations (direct uHGF-AR(1) workflow parity).",
    "d02_d08_reference_limitations": "Two fitting-validation cases expose reference limitations rather than direct fitting parity (Table 3). In an official fitting stress case, MATLAB and HGFX can terminate at different optimizer endpoints in a numerically sensitive basin. In a separate frozen Level-2 holdout case, inference-equivalence fails for a specific seed. In both cases the frozen MATLAB oracle shows the corresponding instability or sensitivity, so these results are reported as matched reference limitations rather than as successful parameter recovery.",
    "d08_classification": "| Frozen Level-2 holdout fit | inference-equivalence failure for a fixed seed | matched reference limitation |",
    "s7_model_selection_36_of_36": "| Paired model selection | 36/36 BIC winners match | direct agreement |",
    "s7_model_selection_result": "The earlier parameter-recovery failure remains part of the record (Figure 2; Table 4). Paired model selection is stronger: 36/36 BIC winners match (Figure 3). Model-selection agreement is not used to imply strong parameter identifiability. Full grid dimensions, frozen thresholds, and the prospective trial-horizon extension are reported in Supplementary Appendix S3.",
    "p3_classification_and_scope": "The trial-horizon study (section 2.6) is complete as an executed protocol, not as a positive identifiability result. Because its paired-integrity gate failed, the available evidence is insufficient for a stronger recovery or identifiability conclusion. Diagnostic per-horizon numbers are archived with the paper materials and shown in Figure 6; they do not replace the earlier recovery evidence.",
    "s7_thresholds": "**Table 4.** Paired parameter recovery on the frozen three-model grid (both truth scales). Thresholds: convergence >= 0.80, median correlation >= 0.50, median standardized RMSE <= 1.00. Full precision: `paper/tables/recovery_model_selection.md`.",
    "gpu_environment_and_objective_agreement": "Compatibility CPU and JAX-backed CPU outputs agree under the frozen backend-equivalence criterion. On two Tesla T4 GPUs (Python 3.12.13, JAX/JAXLIB 0.11.1, `nvidia-smi` process residency), all four required CPU-versus-GPU fitting cells pass the frozen final-objective criterion <= 1e-7. The maximum gap is 1.4210854715202004e-14 (Figure 4; Table 5). This is applicability/correctness evidence, not a speed or scaling result. Exact hardware/runtime provenance, the four CPU-versus-GPU objective pairs, the execution command, and the raw-artifact checksum are reported in Supplementary Appendix S5.",
    "gpu_table_result": "| Physical NVIDIA GPU (2x Tesla T4) | physical-GPU applicability confirmed | max abs objective gap = 1.42e-14; criterion 1e-7 |",
    "pyhgf_response_nll_boundary_result": "Participant-response NLL was not directly comparable. With `ze = 48`, the pyhgf-side power-ratio transformation reached an exact probability boundary on 13 trials and unclipped surprise became +Inf; the HGFX log-domain `unitsq_sgm` evaluation remained finite (total NLL 1808.855415351429). No clipping, formula, precision, parameter, input, or tolerance was changed after observing the result. Overall interpretation: mapped perceptual quantities agree in the authorized cell, while participant-response NLL remains not directly comparable. The semantic gate, exact comparator identity, and numerical-boundary details are given in Supplementary Appendix S4.",
    "limitations_scope": "Current limitations: (i) compatibility is scoped to HGF Toolbox 8.2.0, not future upstream versions; (ii) two numerically sensitive fitting cases are matched reference limitations rather than scientific recovery successes; (iii) parameter identifiability is weaker than paired model selection, and the trial-horizon experiment failed its paired-integrity gate, so it does not support a stronger recovery claim; (iv) GPU evidence is T4 applicability, not throughput; and (v) the pyhgf result is one mapped cell, not package-wide equivalence.",
    "release_and_regeneration_metadata": "HGFX 1.0.0 is MIT-licensed [@hgfx100]. Source, tag, and package URLs are in Table 1. Paper tables regenerate with `python paper/scripts/generate_p2_tables.py`. Figures regenerate with `python paper/scripts/generate_p5_figures.py` (300 dpi PNG and PDF). The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence. Repository-facing case identifiers and claim-to-evidence traceability are intentionally confined to Supplementary Appendix S6.",
    "figure2_recovery_caption": "**Figure 2.** Paired parameter-recovery metrics for MATLAB 8.2.0 and HGFX 1.0.0 against the predeclared recovery thresholds. This panel does not constitute a scientific recovery success. File: `paper/figures/fig_recovery_metrics.png`.",
    "figure4_gpu_caption": "**Figure 4.** Backend agreement relative to each comparison\'s frozen criterion. Compatibility-versus-JAX-CPU has a maximum final-objective gap of 0.0067837 against a 0.10 criterion; JAX-CPU-versus-physical-GPU has a maximum gap of 1.421e-14 against a 1e-7 criterion. Bars show gap/criterion ratios, so the dashed line at 1.0 is the acceptance boundary for both comparisons. Not a speed claim. File: `paper/figures/fig_gpu_applicability.png`.",
    "figure6_p3_caption": "**Figure 6.** Trial-horizon diagnostic parameter-recovery metrics at 128, 256, 512 and 1024 trials, generated directly from the hash-verified aggregate. Dotted lines are the predeclared thresholds. Incomplete classic-HGF cases at 512/1024 trials are retained as gaps. Individual diagnostic criteria do not establish identifiability; the paired-integrity gate failed, so the evidence remains insufficient for an identifiability conclusion. File: `paper/figures/fig_p3_horizon_diagnostics.png`.",
}
REMOVED_NONNUMERIC_CLAIM_IDS = {"historical_m18_fail", "d02_classification", "s7_recovery_classification"}
CLAIMS = [item for item in CLAIMS if item["id"] not in REMOVED_NONNUMERIC_CLAIM_IDS]
for _claim in CLAIMS:
    if _claim["id"] in CURRENT_TEXT_BY_ID:
        _claim["text"] = CURRENT_TEXT_BY_ID[_claim["id"]]

# These are evidence-policy cross-references rather than reported results.
EXEMPTIONS.append({
    "line_hint": 78,
    "text": "Acceptance thresholds, seeds, datasets, starts, model families, optimizers, and grids are not changed after observing results. Failed experiments remain archived. The numerical policy and the two most sensitive optimizer/basin cases are documented in Supplementary Appendices S1-S2.",
    "reason": "policy statement and appendix-number cross-reference; no numerical result",
})

MANUSCRIPT = "paper/manuscript.md"
AUDIT_ID = "hgfx-paper-claim-audit-1"

FRONT_MATTER_PREFIXES = (
    "**Target journal:**",
    "**Article type:**",
    "**Highlights:**",
    "**Word count",
    "**Figures:**",
    "**Abstract:**",
    "**Authors and affiliations**",
    "**Correspondence:**",
    "**Keywords:**",
)


def _canonical_bytes(repo: Path, rel: str) -> bytes:
    path = repo / rel
    if not path.is_file():
        raise FileNotFoundError(rel)
    try:
        return subprocess.check_output(
            ["git", "show", f"HEAD:{rel}"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return path.read_bytes()


def _canonical_text(repo: Path, rel: str) -> str:
    return _canonical_bytes(repo, rel).decode("utf-8")


def _sha256(repo: Path, rel: str) -> str:
    return hashlib.sha256(_canonical_bytes(repo, rel)).hexdigest()


def _strip_citations(text: str) -> str:
    return re.sub(r"\[@[^\]]+\]", "", text)


def _auto_exemption(raw: str) -> str | None:
    stripped = _strip_citations(raw)
    if stripped.startswith("#"):
        return "section_number"
    if any(stripped.startswith(prefix) for prefix in FRONT_MATTER_PREFIXES):
        return "editorial_front_matter"
    return None


def _numeric_candidate_lines(manuscript: str) -> list[dict]:
    out = []
    for number, raw in enumerate(manuscript.splitlines(), start=1):
        stripped = _strip_citations(raw)
        if not re.search(r"\d", stripped):
            continue
        reason = _auto_exemption(raw)
        if reason is not None:
            continue
        out.append({"line_number": number, "text": raw})
    return out


def _find_line(lines: list[str], text: str) -> int:
    matches = [i + 1 for i, line in enumerate(lines) if line == text]
    if len(matches) != 1:
        raise RuntimeError(f"claim/exemption anchor must occur exactly once: {text!r}; matches={matches}")
    return matches[0]


def _verify_machine_sources(repo: Path) -> dict:
    demos = _canonical_text(repo, "docs/user/MATLAB_DEMOS.md")
    for token in (
        "input length: 320 trials",
        "rtol=5e-11",
        "atol=5e-13",
        "16.99162398501939",
        "4.0927117005012175",
        "PASS_MODEL_SELECTION_PARITY",
        "PASS_UHGF_AR1_WORKFLOW_PARITY",
    ):
        if token not in demos:
            raise RuntimeError(f"MATLAB demo evidence missing token: {token}")

    s7 = json.loads(_canonical_text(repo, "reference/validation/m18_s7_reference_limitation/decision.json"))
    assert s7["decision"] == "REFERENCE_LIMITATION_MATCH"
    assert s7["model_recovery"]["winner_matches"] == 36
    assert s7["model_recovery"]["total_cases"] == 36
    assert s7["coverage"]["truth_scales_prior_sd"] == [0.15, 0.35]
    assert s7["criteria_unchanged"] == {
        "convergence_rate_min": 0.8,
        "median_correlation_min": 0.5,
        "median_standardized_rmse_max": 1.0,
        "model_balanced_accuracy_min": 0.5,
    }

    gpu = json.loads(_canonical_text(repo, "gpu_validation_results/m18_s9_physical_gpu_revalidation.json"))
    assert gpu["environment"]["python"] == "3.12.13"
    assert gpu["environment"]["jax"] == "0.11.1"
    assert gpu["physical_gpu_evidence"]["jaxlib"] == "0.11.1"
    assert len(gpu["environment"]["devices"]) == 2
    assert "Tesla T4" in gpu["physical_gpu_evidence"]["nvidia_smi_list"]
    assert gpu["physical_gpu"]["classification"] == "PASS_PHYSICAL_GPU_APPLICABILITY"
    cases = gpu["physical_gpu"]["cases"]
    assert len(cases) == 4
    assert max(case["final_objective_gap"] for case in cases) == 1.4210854715202004e-14
    assert gpu["criteria"]["compat_vs_jax_cpu_final_objective_gap_max"] == 0.1
    assert gpu["acceptance_summary"]["fit_backend_max_objective_gap"] == 0.006783711271481252
    assert gpu["criteria"]["jax_cpu_vs_physical_gpu_final_objective_gap_max"] == 1e-7

    comp = json.loads(_canonical_text(repo, "paper/reproducibility/p2a10_comparison_35268575414.json"))
    passed = [
        value for value in comp["field_results"].values()
        if value["classification"] == "PASS_FOR_EXECUTED_QUANTITY"
    ]
    assert len(passed) == 11
    abs_errors = [value["max_abs_error"] for value in passed]
    assert min(abs_errors) == 1.1102230246251565e-16
    assert max(abs_errors) == 1.5543122344752192e-15
    ndc = comp["field_results"]["participant_response_nll_per_trial"]
    assert ndc["classification"] == "NOT_DIRECTLY_COMPARABLE_FOR_THAT_QUANTITY"
    assert len(ndc["nonfinite_coordinates"]) == 13

    raw = json.loads(_canonical_text(repo, "paper/reproducibility/p2a10_raw_numeric_result_35268575414.json"))
    assert raw["settings"]["response_contract"]["inverse_temperature_native_ze"] == 48
    assert raw["hgfx"]["fields"]["participant_response_nll_total"] == 1808.855415351429
    assert raw["pyhgf"]["fields"]["participant_response_nll_total"] == "+Inf"

    p3 = json.loads(_canonical_text(repo, "paper/reproducibility/p3_m18c2_aggregate_35272347167.json"))
    assert p3["coverage"]["shards"] == p3["coverage"]["expected_shards"] == 24
    assert p3["coverage"]["model_cases"] == p3["coverage"]["expected_model_cases"] == 72
    assert len(p3["model_recovery"]["mismatched_cases"]) == 10
    assert p3["model_recovery"]["winner_matches"] == 62
    assert p3["model_recovery"]["total_cases"] == 72
    assert all(
        ("hgf_binary" in case and ("T512" in case or "T1024" in case))
        for case in p3["model_recovery"]["mismatched_cases"]
    )
    assert p3["overall_classification"] == "INSUFFICIENT_REFERENCE_EVIDENCE"
    assert p3["gate_pass"] is False

    return {
        "matlab_demo_summary": "PASS",
        "s7_recovery_model_selection": "PASS",
        "physical_gpu": "PASS",
        "pyhgf_common_scope": "PASS",
        "p3_trial_horizon": "PASS",
    }


def build(repo: Path) -> dict:
    manuscript = _canonical_text(repo, MANUSCRIPT)
    lines = manuscript.splitlines()
    candidates = _numeric_candidate_lines(manuscript)

    mapped_texts = {item["text"] for item in CLAIMS}
    exempt_texts = {item["text"] for item in EXEMPTIONS}
    if mapped_texts & exempt_texts:
        raise RuntimeError("claim and exemption sets overlap")

    candidate_texts = {item["text"] for item in candidates}
    unmapped = sorted(candidate_texts - mapped_texts - exempt_texts)
    stale = sorted((mapped_texts | exempt_texts) - candidate_texts)
    if unmapped:
        raise RuntimeError("unmapped numerical manuscript lines: " + " | ".join(unmapped))
    if stale:
        raise RuntimeError("stale claim/exemption anchors: " + " | ".join(stale))

    evidence_paths = sorted({path for item in CLAIMS for path in item["evidence"]})
    evidence_hashes = {}
    for path in evidence_paths:
        if not (repo / path).is_file():
            raise FileNotFoundError(f"claim evidence missing: {path}")
        evidence_hashes[path] = _sha256(repo, path)

    resolved_claims = []
    for item in CLAIMS:
        resolved = dict(item)
        resolved["line_number"] = _find_line(lines, item["text"])
        resolved["evidence_sha256"] = {
            path: evidence_hashes[path] for path in item["evidence"]
        }
        resolved_claims.append(resolved)

    resolved_exemptions = []
    for item in EXEMPTIONS:
        resolved = dict(item)
        resolved["line_number"] = _find_line(lines, item["text"])
        resolved_exemptions.append(resolved)

    auto = []
    for number, raw in enumerate(lines, start=1):
        stripped = _strip_citations(raw)
        if not re.search(r"\d", stripped):
            continue
        reason = _auto_exemption(raw)
        if reason is not None:
            auto.append({"line_number": number, "text": raw, "reason": reason})

    checks = _verify_machine_sources(repo)

    return {
        "schema_version": 1,
        "audit_id": AUDIT_ID,
        "status": "COMPLETE_P6A_2_NOT_FROZEN",
        "protocol_id": "hgfx-paper-protocol-1",
        "manuscript_path": MANUSCRIPT,
        "manuscript_sha256": _sha256(repo, MANUSCRIPT),
        "claim_count": len(resolved_claims),
        "explicit_exemption_count": len(resolved_exemptions),
        "auto_exemption_count": len(auto),
        "unmapped_numeric_lines": [],
        "machine_checks": checks,
        "claims": resolved_claims,
        "explicit_exemptions": resolved_exemptions,
        "auto_exemptions": auto,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--output",
        default="paper/reproducibility/p6a_claim_audit.json",
    )
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    audit = build(repo)
    output = repo / args.output
    output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "audit_id": audit["audit_id"],
        "status": audit["status"],
        "claim_count": audit["claim_count"],
        "explicit_exemption_count": audit["explicit_exemption_count"],
        "auto_exemption_count": audit["auto_exemption_count"],
        "output": str(output.relative_to(repo)),
    }, indent=2))


if __name__ == "__main__":
    main()
