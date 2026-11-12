# Supplementary Appendices

These appendices accompany **HGFX: a Python package for reference-compatible Hierarchical Gaussian Filter workflows**. They provide the numerical-policy, sensitivity, provenance, and traceability details that are intentionally summarized in the main text. Repository identifiers are confined to the final traceability appendix so the scientific narrative remains reader-facing.

## Appendix S1. Numerical compatibility policy and frozen acceptance rules

HGFX treats MATLAB compatibility as a numerical validation problem rather than a source-translation exercise. The frozen reference is HGF Toolbox 8.2.0 at commit `2437f4dc241541072722a2695ddeca7b44d83dd3`; the released HGFX source is v1.0.0 at `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`.

All paper-facing acceptance thresholds, seeds, datasets, model families, starts, optimizers, and validation grids were fixed before interpretation of the corresponding final results. Negative, failed, and not-directly-comparable outcomes were retained. No failed replicate was silently dropped or regenerated, and no tolerance was widened after observing results.

Official release-relevant trajectory comparisons use IEEE-754 binary64 with `rtol = 5e-11` and `atol = 5e-13`. The prospective recovery criteria are unchanged from the frozen protocol:

- parameter convergence rate >= 0.80;
- median finite parameter correlation >= 0.50;
- median standardized RMSE <= 1.00;
- model-recovery balanced accuracy >= 0.50.

The physical-GPU applicability criterion is a CPU-versus-GPU final-objective absolute gap <= `1e-7`.

The paper distinguishes four reader-facing interpretations: direct parity, matched reference limitation, preserved failure, and not directly comparable. A matched reference limitation is never promoted to parameter-recovery success or direct fit parity.

## Appendix S2. Numerically sensitive fitting cases

### S2.1 Official enhanced-HGF fitting stress case

In one official enhanced-HGF fitting workflow, MATLAB and HGFX can terminate in different optimizer basins even though shared-state numerical agreement remains at binary64 scale.

In the **specific historical enhanced-HGF stress-case diagnostic**, the previously recorded shared-vector objective samples met that diagnostic's unchanged numerical comparison rule. This historical observation is **not** a newly established family-wide eHGF objective gate for the later 200-vector experiment. At the first localized off-centre sample, the objective absolute difference is `2.842170943040401e-14`, localized to the observation log-likelihood. The first-trial log-likelihood absolute difference is `2.220446049250313e-16`, the maximum per-trial log-likelihood absolute difference is `8.881784197001252e-16`, and the MATLAB vector-sum versus scalar-loop reduction difference is `1.1368683772161603e-13`. The inference-state maximum absolute difference at the localized source-likelihood probe is exactly zero.

A MATLAB self-sensitivity probe perturbed the official transformed start by one local floating-point spacing. All 6 independent +/- one-spacing perturbations produced materially different optimizer endpoints, despite preserving the same model, data, optimizer, and scientific tolerances. The largest observed free-parameter shift was approximately 1.508. This demonstrates that the residual endpoint mismatch is consistent with a numerical-basin sensitivity also present in the frozen MATLAB reference; it is therefore reported as a matched reference limitation, not as inferential parity.

### S2.2 Frozen uHGF Level-2 holdout case

A separate uHGF + Gaussian-observation holdout used a preselected seed and unchanged Level-2 tolerances `rtol = 3e-8` and `atol = 3e-10`. The frozen holdout fails inference equivalence for that seed, while exact shared-state objective/gradient checks and exact-state quasi-Newton/BFGS replay do not identify a material HGFX-only semantic defect.

The MATLAB reference is itself strongly start-sensitive in this exact workflow: 13 of 14 independent +/- one-local-spacing perturbations move the MATLAB optimizer endpoint outside the unchanged endpoint gate. The failed holdout therefore remains visible as a failure and is interpreted only as an exact-scope matched reference limitation. The result does not justify changing the seed, start, optimizer, data, or tolerance.

### S2.3 Original published-release objective evaluation at shared parameters

The original published-wheel REV-2.4 comparisons were performed against frozen MATLAB HGF Toolbox 8.2.0, not against the later development-only eHGF maintenance patch. The fixed-vector experiment contained **200 predeclared cases per family** at 128 trials and retained the complete valid/invalid denominator:

| Perceptual family (binary observation) | Paired valid | Paired invalid | One-sided invalid | Interpretation |
|---|---:|---:|---:|---|
| Classic HGF | 164 | 36 | 0 | All 164 paired-valid objectives satisfy the **pre-existing classic-HGF criterion**; the 36 invalid cases are not successes |
| Enhanced HGF | 198 | 1 | 1 | Numerical differences observed, **no preregistered enhanced-HGF objective gate** |
| Unbounded HGF | 198 | 2 | 0 | Numerical differences observed, **no preregistered unbounded-HGF objective gate** |
| **Total** | **560** | **39** | **1** | No global/parity verdict from this table |

The classic-HGF criterion was `rtol=2e-11, atol=2e-13` for the applicable original shared-vector objective checks. Classic-HGF maximum absolute objective difference among valid comparisons was `7.275957614183426e-12`. The original enhanced-HGF case with a one-sided-invalid likelihood at zero-based trial 11 remains a **released-1.0.0 failure**, not a successful reference match. Subsequent development-only source changes are maintained separately and have not been scientifically accepted as a released-wheel correction.

The original cross-evaluation experiment assessed **132 planned fitted-endpoint slots** from the two historical stress cases and 64 classic-HGF subjects: **128/128 classic-HGF slots** were paired-valid and within the original classic-HGF objective criterion (max negative-log-joint absolute difference `2.842170943040401e-14`), **2/2 unbounded-HGF slots** were paired-valid but had no registered family-specific objective threshold, and **1/2 enhanced-HGF slots** was evaluable because the archived HGFX endpoint vector was missing. The resulting **131/132 observable** endpoint slots do not establish global parity, fitted-endpoint equality, optimizer-path equivalence, trajectories, covariance or model-selection agreement. The historical **63/64** complete-fit discrepancy and subject-specific trajectory failure remain in force.

The original scientific outputs and frozen execution identities are preserved in `docs/research/REV24_PANEL_G_ORIGINAL_RESULT_2026-11-10.md` and `docs/research/REV24_PANEL_E_ORIGINAL_RESULT_2026-11-10.md`; their GitHub Actions and raw artifact hashes appear there. These are cross-language objective experiments, **not runtime benchmarks**.

### S2.4 Official USD/CHF full fitting: do not substitute holdout sensitivity for scientific parity

The source-only historical 614-observation `uhgf + gaussian_obs` holdout described in S2.2 has a **different seed and simulated responses** from the official published-wheel paired USD/CHF study. Its MATLAB 13-of-14 start perturbation endpoint sensitivity cannot be transferred to the official study. Indeed, the separate *official* MATLAB seed `123456789` historical ±one-ULP source check did **not** show an analogous out-of-gate endpoint shift in its 14 probes. This is a difference in scope, not a reason to disregard either historical result.

For the official published-wheel MATLAB/HGFX comparison, two independent concurrent one-shot workflows ran before either result was available, which was contrary to the planned single-invocation protocol. The two unchanged original-result records must be retained: against **1228** original own-fitted-endpoint `traj.epsi` entries, **4** were outside the original numerical gate in the first run and **3** were outside in the second, with zero-based first divergent trial **178** in both. Even though objectives evaluated at the *same* chosen parameter vectors were numerically close, the original complete HGFX optimizer traces were not archived, and the cause is not established. The official result is `UNRESOLVED_DISCREPANCY`, **not direct fit parity** and **not a proven model-identifiability limitation**. The runs were not a prospectively defined two-replicate design.

Unmodified original protocols, source hashes, all numerical outcomes and run-specific artifacts are documented in `docs/research/REV22_D08_ORACLE_ORIGINAL_RESULT_2026-11-11.md`. This appendix does not apply a retrospective family objective threshold or change the old D08 or M18 failure classification.

## Appendix S3. Recovery and model-selection protocol

The paired recovery program separates parameter recovery from model recovery.

For the frozen paired recovery grid used in the main paper, the perceptual models are classic binary HGF, enhanced binary HGF, and unbounded binary HGF, with the `unitsq_sgm` observation model. The grid contains 72 parameter-recovery cases and 36 model-recovery datasets; each model-recovery dataset is fit by all three candidate models. Trial counts are 128 and 256, truth perturbation scales are 0.15 and 0.35 prior standard deviations, parameter recovery uses 6 replicates per stratum, and model recovery uses 3 replicates per stratum.

The resulting parameter-recovery summary is intentionally not labeled a scientific PASS. MATLAB and HGFX agree closely on the frozen metrics:

| Model | Convergence MATLAB/HGFX | Median r MATLAB/HGFX | Median sRMSE MATLAB/HGFX |
|---|---:|---:|---:|
| classic binary HGF | 0.833 / 0.833 | 0.203 / 0.203 | 2.610 / 2.610 |
| enhanced binary HGF | 0.917 / 0.917 | 0.462 / 0.462 | 2.359 / 2.359 |
| unbounded binary HGF | 0.792 / 0.792 | 0.381 / 0.381 | 2.958 / 2.958 |

By contrast, paired model selection is stronger: all 36 of 36 BIC winners agree between MATLAB and HGFX, and balanced accuracy is 0.5833333333333334 in both implementations. This agreement is not used to imply strong parameter identifiability.

### S3.1 Prospective trial-horizon extension

A separately frozen prospective extension examined 128, 256, 512, and 1024 trials, with the same three perceptual models and truth scales. Parameter recovery used 6 replicates per model x horizon x truth-scale stratum. Model recovery used 3 replicates per generating-model x horizon x truth-scale stratum. The frozen workload was 360 fits per implementation.

The paired-integrity gate required complete paired shards, identical free-parameter indices, identical pass/fail outcomes for each frozen parameter criterion at each model x horizon, and agreement of every paired BIC winner before any identifiability interpretation.

That gate did not pass. Ten of 72 BIC winners disagreed, all in classic binary-HGF datasets at 512 or 1024 trials. Parameter-recovery summaries for classic HGF at those horizons are incomplete because invalid simulations were retained rather than resampled. The frozen per-model diagnostic classifier records `IMPLEMENTATION_OR_OPTIMIZER_MISMATCH`; this identifies paired implementation/optimization disagreement and is not itself an identifiability verdict. The aggregate scientific classification remains `INSUFFICIENT_REFERENCE_EVIDENCE` with `gate_pass=false`. Consequently, the study supports no data-horizon or structural-identifiability conclusion. This negative outcome is retained rather than repaired post hoc.

## Appendix S4. pyhgf common-scope semantic and numerical comparison

The external comparator was frozen as `pyhgf==0.3.2` before execution, with source-distribution SHA-256 `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d`.

Direct comparison was authorized only after mapping model structure, update equations, input/masking semantics, parameter meanings and transforms, initial states, observation/response quantities, precision mode, and numerical guards. The executed cell is a fully observed fixed-parameter three-level binary HGF with 128 trials and `ze = 48`.

All 11 mapped perceptual/inference quantities pass their prospectively frozen tolerances. Maximum absolute errors span approximately `1.11e-16` to `1.55e-15`, i.e. binary64 rounding scale. Observed inputs match exactly.

Participant-response negative log-likelihood is not directly comparable in this cell. The pyhgf-side power-ratio response transformation reaches an exact probability boundary on 13 trials, yielding nonfinite unclipped surprise, whereas the HGFX log-domain `unitsq_sgm` evaluation remains finite with total NLL `1808.855415351429`. No clipping, formula, precision, parameter, input, version, or tolerance was changed after observing the result.

This is a quantity-specific comparison, not a package ranking and not evidence of package-wide equivalence.

## Appendix S5. Physical-GPU applicability and environment provenance

Physical GPU validation was executed before release at source commit `07b45a569e04e8e71244c5310dd2cc53dbb2b0ec` in a hosted/shared Kaggle environment where two NVIDIA Tesla T4 devices were visible. The recorded runtime was Python 3.12.13, JAX 0.11.1, and JAXLIB 0.11.1. The required fitting cells executed on `cuda:0`; device residency was verified by the JAX device-placement check, while `nvidia-smi -L` provided hardware enumeration only.

The post-fix compatibility-versus-JAX-CPU leg was remeasured separately on Ubuntu with Python 3.12.14 and JAX/JAXLIB 0.11.1. The canonical execution is GitHub Actions run `36255732941`, source commit `0a40e7081421c0ad66ea45f852f11bd823cc9d51`, using the unchanged `0.1` criterion. Two repeated executions were byte-identical (raw-result SHA-256 `f5ad2c412a8ad9f6325e45e2398ec46f54bcb13bba64ebe12827033d8aeedfab`). Across the four fitting cells the maximum post-fix CPU gap is `0.006783711260709424`, so the CPU classification remains a PASS under the frozen criterion. The committed artifact is `gpu_validation_results/m18_s9_cpu_postfix_revalidation.json`.

Four required CPU-versus-GPU fitting cells were evaluated:

| Trials | Regime | CPU objective | GPU objective | Absolute gap |
|---:|---|---:|---:|---:|
| 128 | regular | 100.8431397034844 | 100.8431397034844 | 0 |
| 128 | ignored/missing | 99.10585723807621 | 99.10585723807620 | 1.4210854715202004e-14 |
| 256 | regular | 192.27807219103437 | 192.27807219103437 | 0 |
| 256 | ignored/missing | 190.1701167284927 | 190.1701167284927 | 0 |

All four are below the frozen `1e-7` final-objective criterion. The maximum observed gap is `1.4210854715202004e-14`.

This physical-GPU evidence is retained after release rather than represented as a new post-remediation GPU execution. Retention is based on source-path inspection: the S9 runner and JAX GPU fitting path used by these cells are unchanged across the release, whereas the later host-libm repair affected the NumPy compatibility path and therefore requires a separate post-fix CPU remeasurement. This evidence establishes physical-GPU applicability/correctness only. The environment was shared, and no claim of uncontended peak performance, general speedup, H100 performance, or multi-GPU scaling is made.

The exact recorded command was:

```text
/usr/bin/python3 /kaggle/working/hgfx/scripts/run_m18_s9_backend_robustness.py --output /kaggle/working/hgfx/gpu_validation_results/m18_s9_physical_gpu_revalidation.json --require-gpu
```

The preserved raw validation artifact SHA-256 is `6cd35c82be1e542830c06f6b7b7e444fda0ff4fe93773f080e6c13725212dfdf`.

## Appendix S6. Reproducibility and repository traceability

The main text deliberately avoids internal milestone/case identifiers. They are listed here only to provide an auditable bridge from reader-facing claims to repository evidence.

| Reader-facing item | Repository identifier / evidence |
|---|---|
| Official enhanced-HGF fitting stress case | D02; `reference/validation/m18_d02_reference_limitation/decision.json` |
| Frozen uHGF Level-2 holdout case | D08; `reference/validation/m18_d08_reference_limitation/decision.json` |
| Paired recovery/model-selection grid | S7; `reference/validation/m18_s7_reference_limitation/decision.json` |
| Physical GPU applicability | S9; `gpu_validation_results/m18_s9_physical_gpu_revalidation.json` |
| Prospective trial-horizon extension | M18C.2/P3; `paper/reproducibility/p3_m18c2_aggregate_35272347167.json` |
| pyhgf common-scope comparison | P2A.10; `paper/reproducibility/p2a10_comparison_35268575414.json` |

Primary reproducibility identities:

- HGFX release: `v1.0.0` / `4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27`;
- MATLAB oracle: HGF Toolbox 8.2.0 / `2437f4dc241541072722a2695ddeca7b44d83dd3`;
- paper protocol: `hgfx-paper-protocol-1`;
- trial-horizon Actions run: `35272347167`;
- trial-horizon aggregate SHA-256: `83ccbb7f5c4f0eed213d60330d0b318a37e74f03ba08a93a4e4d5d60841131b4`;
- pyhgf comparison raw-result SHA-256: `202007865c78ba0b138eeda5f105a73399d74076a802edd2c422ddcf98e4696b`.

Paper tables and figures are generated from committed machine-readable evidence by committed scripts. The reviewer entry point is `paper/reproducibility/README.md`. MATLAB is required only to regenerate paired oracle evidence; it is not required to install or use HGFX.

## Appendix S7. Published-input forward-filter compatibility: external-source data, not published-study replication

This is a separate **originally executed, predeclared fixed-parameter perceptual-filter comparison**, not a replication of the source papers or of their model-fitting workflows. Public stimulus and choice sequences were read from two source studies: Suthaharan et al. (2021), *Paranoia and belief updating during the COVID-19 crisis*, DOI `10.1038/s41562-021-01176-8`, and Reed et al. (2020), *Paranoia as a deficit in non-social belief updating*, DOI `10.7554/eLife.56345`. Original source file hashes are preserved in `paper/case_studies/REALDATA_FORWARD_PARITY_RESULT_2026-11-04.md`; participant-level input arrays and trajectories are not redistributed in this article.

### S7.1 Prospective denominator correction

The initial full-source inventory incorrectly counted an incidental MATLAB workspace variable `ans` as a Reed participant and specified 326 cases. Its source-integrity preflight [run 41809479255](https://github.com/ahmadkhanloo/hgfx/actions/runs/41809479255) stopped **before scientific model execution**. A source-only follow-up established the correct population: 130 Suthaharan people × two 80-trial blocks = 260 blocks; 32 Reed people × two 80-trial blocks = 64 blocks. Hence the amended complete source-defined workload was **324 blocks, 25,920 trials**, with no post-result deletion or model-based case exclusion. The [v2 corrected source protocol](../../paper/case_studies/PUBLISHED_REALDATA_FULLCOHORT_PROTOCOL_V2_2026-11-04.md) was recorded before the original full-grid science run. The original failed source gate and v1 plan remain intact.

### S7.2 Frozen mathematical and execution scope

- Reference: MATLAB HGF Toolbox 8.2.0 `hgf_ar1_binary_mab`, commit `2437f4dc241541072722a2695ddeca7b44d83dd3`, MATLAB R2025b Update 7.
- Test implementation: **published HGFX 1.0.0 wheel**, Python 3.11.18, JAX/JAXLIB 0.10.2, NumPy 2.2.6, CPU binary64. This is not a development-branch JAX-run simulation.
- One **native 17-element** parameter vector preselected from the earlier M12B source, shared across *all* 324 blocks: `[NaN,0,1,NaN,0.1,1,NaN,0,0.2,NaN,0,1,1,1,NaN,-2,-6]`. The NaN entries are native placeholder semantics, **not** failed numeric values.
- Locked criterion: `rtol=2e-9`, `atol=2e-11`; matched masks and nonfinite conventions; 12 perceptual/inference output quantities per block, including `infStates`. No model fits, optimizer restarts, parameter search, or response-model transformations were evaluated.

### S7.3 Original execution and scope of conclusions

The paired genuine MATLAB/wheel run [41809919116](https://github.com/ahmadkhanloo/hgfx/actions/runs/41809919116) had 324 MATLAB forward successes and 324 HGFX within-criterion results. Complete comparison coverage was **3,888 quantities (324 × 12)** and **2,540,160 compared numeric elements**, with zero outside the frozen tolerance. Maximum absolute difference was `3.1086244689504383e-15`; maximum relative difference `5.603239773513641e-11` is **descriptive**, not an additional pass criterion. **48 of 324 blocks** emitted Python warnings; all were Reed blocks with ignored trials, but the original archive records warning counts only, so causal warning type was **not established**. The later warning source audit documents an association with ignored trials, not the warning mechanism.

Machine-readable per-case **statuses, not participant-level array exports**, are retained byte-for-byte from the original repository in `paper/computational_statistics/evidence/published_input_41809919116.json`. The original final result `paper/case_studies/REALDATA_FORWARD_PARITY_RESULT_2026-11-04.md`, initial source protocol, failed 326-case source plan, and pre-execution corrected 324-case protocol are also preserved unchanged.

**Interpretation:** This establishes **one-parameter-vector, classic HGF-AR(1) binary perceptual forward numerical compatibility on authentic published input sequences**. It does **not** establish reproduction of either original paper's fitted priors/parameters, choice likelihoods, full model-selection analysis, participant exclusions, substantive effects or original software configuration. The published HGFX v1.0.0 compatibility fitting dispatcher does not provide end-to-end `hgf_ar1_binary_mab` plus softmax fitting; this is an explicit implementation-scope gap, not an observed fit mismatch. No rate of scientific recovery, model identifiability, runtime acceleration or speed comparison follows from this source-only forward result.

