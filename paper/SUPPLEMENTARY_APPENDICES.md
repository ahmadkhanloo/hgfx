# Supplementary Appendices

These appendices accompany **HGFX: a validated Python/JAX reproduction of the Hierarchical Gaussian Filter toolbox**. They provide the numerical-policy, sensitivity, provenance, and traceability details that are intentionally summarized in the main text. Repository identifiers are confined to the final traceability appendix so the scientific narrative remains reader-facing.

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

The exact shared-vector objective checks pass under the unchanged numerical gate. At the first localized off-centre sample, the objective absolute difference is `2.842170943040401e-14`, localized to the observation log-likelihood. The first-trial log-likelihood absolute difference is `2.220446049250313e-16`, the maximum per-trial log-likelihood absolute difference is `8.881784197001252e-16`, and the MATLAB vector-sum versus scalar-loop reduction difference is `1.1368683772161603e-13`. The inference-state maximum absolute difference at the localized source-likelihood probe is exactly zero.

A MATLAB self-sensitivity probe perturbed the official transformed start by one local floating-point spacing. All 6 independent +/- one-spacing perturbations produced materially different optimizer endpoints, despite preserving the same model, data, optimizer, and scientific tolerances. The largest observed free-parameter shift was approximately 1.508. This demonstrates that the residual endpoint mismatch is consistent with a numerical-basin sensitivity also present in the frozen MATLAB reference; it is therefore reported as a matched reference limitation, not as inferential parity.

### S2.2 Frozen uHGF Level-2 holdout case

A separate uHGF + Gaussian-observation holdout used a preselected seed and unchanged Level-2 tolerances `rtol = 3e-8` and `atol = 3e-10`. The frozen holdout fails inference equivalence for that seed, while exact shared-state objective/gradient checks and exact-state quasi-Newton/BFGS replay do not identify a material HGFX-only semantic defect.

The MATLAB reference is itself strongly start-sensitive in this exact workflow: 13 of 14 independent +/- one-local-spacing perturbations move the MATLAB optimizer endpoint outside the unchanged endpoint gate. The failed holdout therefore remains visible as a failure and is interpreted only as an exact-scope matched reference limitation. The result does not justify changing the seed, start, optimizer, data, or tolerance.

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

That gate did not pass. Ten of 72 BIC winners disagreed, all in classic binary-HGF datasets at 512 or 1024 trials. Parameter-recovery summaries for classic HGF at those horizons are incomplete because invalid simulations were retained rather than resampled. Consequently, the study supports no data-horizon or structural-identifiability conclusion. This negative outcome is retained rather than repaired post hoc.

## Appendix S4. pyhgf common-scope semantic and numerical comparison

The external comparator was frozen as `pyhgf==0.3.2` before execution, with source-distribution SHA-256 `8289f6746668e3af9878c3b5638484c70cd44a596e796ec281986da47e9c723d`.

Direct comparison was authorized only after mapping model structure, update equations, input/masking semantics, parameter meanings and transforms, initial states, observation/response quantities, precision mode, and numerical guards. The executed cell is a fully observed fixed-parameter three-level binary HGF with 128 trials and `ze = 48`.

All 11 mapped perceptual/inference quantities pass their prospectively frozen tolerances. Maximum absolute errors span approximately `1.11e-16` to `1.55e-15`, i.e. binary64 rounding scale. Observed inputs match exactly.

Participant-response negative log-likelihood is not directly comparable in this cell. The pyhgf-side power-ratio response transformation reaches an exact probability boundary on 13 trials, yielding nonfinite unclipped surprise, whereas the HGFX log-domain `unitsq_sgm` evaluation remains finite with total NLL `1808.855415351429`. No clipping, formula, precision, parameter, input, version, or tolerance was changed after observing the result.

This is a quantity-specific comparison, not a package ranking and not evidence of package-wide equivalence.

## Appendix S5. Physical-GPU applicability and environment provenance

Physical GPU validation was executed in a hosted/shared Kaggle environment with two NVIDIA Tesla T4 devices. The recorded runtime was Python 3.12.13, JAX 0.11.1, and JAXLIB 0.11.1. Physical CUDA residency was verified through the runtime device list and `nvidia-smi` process evidence.

Four required CPU-versus-GPU fitting cells were evaluated:

| Trials | Regime | CPU objective | GPU objective | Absolute gap |
|---:|---|---:|---:|---:|
| 128 | regular | 100.8431397034844 | 100.8431397034844 | 0 |
| 128 | ignored/missing | 99.10585723807621 | 99.10585723807620 | 1.4210854715202004e-14 |
| 256 | regular | 192.27807219103437 | 192.27807219103437 | 0 |
| 256 | ignored/missing | 190.1701167284927 | 190.1701167284927 | 0 |

All four are below the frozen `1e-7` final-objective criterion. The maximum observed gap is `1.4210854715202004e-14`.

This evidence establishes physical-GPU applicability/correctness only. The environment was shared, and no claim of uncontended peak performance, general speedup, H100 performance, or multi-GPU scaling is made.

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
